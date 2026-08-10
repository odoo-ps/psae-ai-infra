"""Detect the development environment to inform adaptive scaffolding.

What this script answers, in one structured report:
  1. What IDE / runtime config files exist? (.vscode/, .cursor/, .idea/, systemd, docker-compose)
  2. Which Odoo version folders exist? (`v19/`, `v20/`, … — each a self-contained
     stack with its own odoo source, venv, enterprise, and instances tree)
  3. What instances exist and which version does each belong to? (conf paths,
     custom_addons paths, ports — every instance tagged with its `version`)
  4. Is there a Python venv to use, per version and as a default?
  4. Is Postgres reachable for the next pre-flight steps?
  5. Is an nginx include dir present (so Pre-Flight A.11 reverse-proxy scaffold can be planned)?

The report is JSON on stdout. Decision-making (which layout to use, whether to patch
launch.json) lives in `_create_instance.py` and the agent — this script is detection only.

Usage:
    python3 _detect_environment.py [--repo-root <path>]
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from configparser import ConfigParser
from pathlib import Path


# Architecture labels — single source of truth for the JSON report's
# `architecture` field. Mirrored in skills/_shared/principles.md (P13)
# and each SKILL.md's routing table.
ARCH_LOCAL = "local"
ARCH_ODOO_SH = "odoo.sh"
ARCH_DOCKER = "docker"
ARCH_BARE_METAL = "bare_metal"
ARCH_UNKNOWN = "unknown"


# A version folder is `v<major>/` (e.g. v19, v20) holding a self-contained Odoo
# stack: `<version>/odoo/` source (+ its `.venv`), `<version>/enterprise/`, and
# `<version>/instances/`. The repo root is version-agnostic — it holds `skills/`
# plus one-or-more version folders — so adding v20 alongside v19 needs no path
# edits, only a new `v20/` tree.
VERSION_DIR_RE = re.compile(r"^v(\d+)$")


def _read_release_version(odoo_src: Path) -> str | None:
    """Best-effort read of the real Odoo series (e.g. '19.0') from release.py."""
    rel = odoo_src / "odoo" / "release.py"
    try:
        text = rel.read_text()
    except OSError:
        return None
    m = re.search(r"version_info\s*=\s*\(\s*(\d+)\s*,\s*(\d+)", text)
    if m:
        return f"{m.group(1)}.{m.group(2)}"
    m = re.search(r"""series\s*=\s*['"]([\d.]+)['"]""", text)
    return m.group(1) if m else None


def detect_versions(repo_root: Path) -> list[dict]:
    """Every `v<major>/` folder containing an `odoo/` source tree is a version.

    Returned sorted by major ascending, so the LAST entry is the newest. Each
    entry carries the per-version paths callers need to route correctly:
    odoo_bin, venv, enterprise, and the real Odoo series from release.py.
    """
    out = []
    if not repo_root.is_dir():
        return out
    for child in sorted(repo_root.iterdir()):
        m = VERSION_DIR_RE.match(child.name)
        if not m or not child.is_dir() or not (child / "odoo").is_dir():
            continue
        venv = child / "odoo" / ".venv" / "bin" / "python"
        odoo_bin = child / "odoo" / "odoo-bin"
        enterprise = child / "enterprise"
        out.append({
            "version": child.name,                       # "v19"
            "major": int(m.group(1)),                    # 19
            "path": str(child),
            "odoo_bin": str(odoo_bin) if odoo_bin.is_file() else None,
            "venv": str(venv) if venv.is_file() else None,
            "enterprise": str(enterprise) if enterprise.is_dir() else None,
            "release_version": _read_release_version(child / "odoo"),
        })
    out.sort(key=lambda e: e["major"])
    return out


def find_repo_root(start: Path) -> Path:
    cur = start.resolve()
    for _ in range(10):
        if (cur / "skills").is_dir() and detect_versions(cur):
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    raise RuntimeError(f"Could not locate repo root above {start}")


def detect_ides(repo_root: Path) -> dict:
    found = {}
    for ide_dir, marker_file in [
        (".vscode", "launch.json"),
        (".cursor", "launch.json"),
        (".idea", None),
    ]:
        d = repo_root / ide_dir
        if d.is_dir():
            entry = {"path": str(d), "files": sorted(p.name for p in d.iterdir() if p.is_file())}
            if marker_file and (d / marker_file).exists():
                entry["launch_json"] = str(d / marker_file)
            found[ide_dir.lstrip(".")] = entry

    # Workspace-file form
    ws = list(repo_root.glob("*.code-workspace"))
    if ws:
        found["code_workspace"] = [str(p) for p in ws]

    # systemd / docker — readable inventory only, never written by this skill
    systemd_units = []
    for d in ("/etc/systemd/system", "/usr/lib/systemd/system"):
        if Path(d).is_dir():
            try:
                systemd_units += sorted(str(p) for p in Path(d).glob("odoo*.service"))
            except PermissionError:
                pass
    if systemd_units:
        found["systemd"] = systemd_units

    docker = []
    for fn in ("docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"):
        p = repo_root / fn
        if p.is_file():
            docker.append(str(p))
    if docker:
        found["docker_compose"] = docker

    return found


def parse_conf(conf_path: Path) -> dict:
    cp = ConfigParser()
    try:
        cp.read(conf_path)
    except Exception as e:
        return {"path": str(conf_path), "error": str(e)}
    if not cp.has_section("options"):
        return {"path": str(conf_path), "error": "no [options] section"}
    info = {"path": str(conf_path)}
    for k in ("dbfilter", "db_name", "db_host", "db_port", "db_user",
              "http_port", "xmlrpc_port", "longpolling_port", "addons_path"):
        if cp.has_option("options", k):
            info[k] = cp.get("options", k).strip()
    return info


def detect_instances(repo_root: Path, versions: list[dict] | None = None) -> list[dict]:
    """Find every instance under `<repo_root>/<version>/instances/<name>/`.

    Layout convention (post-2026-07-08, version-aware): each Odoo instance
    lives at `<repo_root>/v<major>/instances/<name>/` (e.g. `v19/instances/`,
    `v20/instances/`). Every returned instance is tagged with its `version`
    folder so callers route odoo-bin / venv / conf paths to the matching
    version. Earlier flat layouts (instances at the repo root or a top-level
    `instances/`) are no longer auto-discovered — move them under a version
    folder to bring them back into the skill's purview.
    """
    versions = versions if versions is not None else detect_versions(repo_root)
    out = []
    for v in versions:
        instances_root = Path(v["path"]) / "instances"
        if not instances_root.is_dir():
            continue
        for child in sorted(instances_root.iterdir()):
            if not child.is_dir() or child.name.startswith("."):
                continue
            conf = child / "odoo.conf"
            if conf.is_file():
                inst = parse_conf(conf)
                inst["instance"] = child.name
                inst["version"] = v["version"]
                inst["custom_addons_dir"] = str(child / "custom_addons") if (child / "custom_addons").is_dir() else None
                out.append(inst)
    return out


def detect_venv(repo_root: Path, versions: list[dict] | None = None) -> str | None:
    """Default venv for LOCAL-arch classification — the newest version's venv.

    Per-version work must use that version's own venv (see `detect_versions`);
    this is only the sensible default when no specific version is in play.
    Falls back to a repo-root `.venv` for non-versioned legacy layouts.
    """
    versions = versions if versions is not None else detect_versions(repo_root)
    for v in reversed(versions):  # newest first
        if v.get("venv"):
            return v["venv"]
    fallback = repo_root / ".venv" / "bin" / "python"
    return str(fallback) if fallback.is_file() else None


def detect_odoo_sh(repo_root: Path) -> dict:
    """Return a dict of Odoo.sh signals that fired. Empty dict if none."""
    signals = {}
    yaml_path = repo_root / ".odoo.sh.yaml"
    if yaml_path.is_file():
        signals["yaml"] = str(yaml_path)
    odoo_sh_dir = repo_root / "odoo.sh"
    if odoo_sh_dir.is_dir():
        signals["dir"] = str(odoo_sh_dir)
    if os.environ.get("ODOO_SH"):
        signals["env_var"] = "ODOO_SH"
    if signals:
        return signals  # cheap signals settled it; skip the git subprocess
    try:
        r = subprocess.run(
            ["git", "-C", str(repo_root), "remote", "get-url", "origin"],
            capture_output=True, text=True, timeout=3,
        )
        if r.returncode == 0:
            url = r.stdout.strip()
            if "odoo.sh" in url or "runbot.odoo.com" in url:
                signals["remote"] = url
    except Exception:
        pass
    return signals


def detect_bare_metal() -> dict:
    """Return a dict of bare-metal signals that fired. Empty dict if none.

    Systemd units are collected by `detect_ides()` into `report["ides"]["systemd"]`
    (loose naming, kept for backwards compatibility with existing report consumers).
    `classify_architecture()` combines that with the signals returned here.
    """
    signals = {}
    if Path("/etc/init.d/odoo").is_file():
        signals["initd"] = "/etc/init.d/odoo"
    sys_bin = shutil.which("odoo-bin")
    if sys_bin and sys_bin.startswith(("/usr/", "/opt/")):
        signals["system_odoo_bin"] = sys_bin
    return signals


def classify_architecture(report: dict) -> dict:
    """Build the `{architecture, signals, alternatives}` block for the report.

    Precedence: odoo.sh > local > docker > bare_metal > unknown. Architectures
    that fire below the primary land in `alternatives` so the agent's Q0 step
    can surface multi-signal cases as ties per shared principle #12.
    `alternatives` is an empty list when no other signals fired.
    """
    candidates = []

    if report.get("odoo_sh"):
        candidates.append((ARCH_ODOO_SH, report["odoo_sh"]))
    if report.get("instances") and report.get("venv"):
        candidates.append((ARCH_LOCAL, {
            "instances": [i["instance"] for i in report["instances"]],
            "venv": report["venv"],
        }))
    docker = report.get("ides", {}).get("docker_compose")
    if docker:
        candidates.append((ARCH_DOCKER, {"compose": docker}))
    bare = dict(report.get("bare_metal") or {})
    ides_systemd = report.get("ides", {}).get("systemd")
    if ides_systemd:
        bare["systemd"] = ides_systemd
    if bare:
        candidates.append((ARCH_BARE_METAL, bare))

    if not candidates:
        return {"architecture": ARCH_UNKNOWN, "signals": {}, "alternatives": []}

    primary_name, primary_signals = candidates[0]
    alternatives = [{"architecture": n, "signals": s} for n, s in candidates[1:]]
    return {
        "architecture": primary_name,
        "signals": primary_signals,
        "alternatives": alternatives,
    }


def detect_postgres() -> dict:
    out = {"createdb_in_path": bool(shutil.which("createdb")),
           "psql_in_path": bool(shutil.which("psql"))}
    if out["psql_in_path"]:
        try:
            r = subprocess.run(
                ["psql", "-h", "localhost", "-p", "5432", "-U", "odoo", "-d", "postgres",
                 "-tAc", "SELECT version();"],
                capture_output=True, text=True, timeout=5,
            )
            out["reachable"] = r.returncode == 0
            if r.returncode == 0:
                out["server_version"] = r.stdout.strip().split(",")[0]
        except Exception as e:
            out["reachable"] = False
            out["error"] = str(e)
    return out


# Candidate nginx include dirs (first existing match wins). Mirrors the list
# in _create_instance.py:_NGINX_INCLUDE_CANDIDATES — single source of truth
# for the candidate set, but each script keeps its own copy because they're
# invoked independently.
_NGINX_INCLUDE_CANDIDATES = (
    "/opt/homebrew/etc/nginx/servers",   # macOS Apple Silicon, brew
    "/usr/local/etc/nginx/servers",      # macOS Intel, brew
    "/etc/nginx/conf.d",                 # Linux (RHEL/CentOS) yum
    "/etc/nginx/sites-enabled",          # Linux (Debian/Ubuntu) apt
)


def detect_nginx() -> dict:
    """Return {'available', 'include_dir', 'log_dir', 'binary_in_path'}.

    Best-effort detection — never raises. Pre-Flight A.11 (in pre_flight.md)
    consumes this to decide whether to scaffold the reverse-proxy and to
    surface the planned target in the user-facing confirmation block.
    The actual scaffold logic still lives in _create_instance.py, which
    re-probes for safety; this script's job is visibility.
    """
    out = {
        "available": False,
        "include_dir": None,
        "log_dir": None,
        "binary_in_path": bool(shutil.which("nginx")),
    }
    for cand in _NGINX_INCLUDE_CANDIDATES:
        p = Path(cand)
        if p.is_dir():
            out["available"] = True
            out["include_dir"] = str(p)
            if "/opt/homebrew/" in cand:
                out["log_dir"] = "/opt/homebrew/var/log/nginx"
            elif "/usr/local/" in cand:
                out["log_dir"] = "/usr/local/var/log/nginx"
            else:
                out["log_dir"] = "/var/log/nginx"
            break
    return out


def infer_convention(instances: list[dict], repo_root: Path) -> dict:
    """Best-effort inference of the existing scaffolding convention.

    Returns a dict with keys describing what to mirror, or `{}` if no
    sibling instance exists.
    """
    if not instances:
        return {}

    # Take the most recent (by mtime) instance as the canonical example.
    latest = max(instances, key=lambda i: Path(i["path"]).stat().st_mtime)

    conv = {"based_on": latest["instance"]}
    # Conf at <instance>/odoo.conf — that's our baseline.
    conf_dir = Path(latest["path"]).parent
    conv["conf_filename"] = Path(latest["path"]).name  # usually "odoo.conf"

    # Custom addons dir name
    addons_path = latest.get("addons_path", "")
    cust = None
    for line in addons_path.splitlines():
        line = line.strip().rstrip(",")
        if line.startswith(str(conf_dir)) and line != str(conf_dir):
            rel = Path(line).relative_to(conf_dir)
            if rel.parts:
                cust = rel.parts[0]
                break
    conv["custom_addons_dirname"] = cust or "custom_addons"

    # dbfilter shape — extract version prefix if present
    dbf = latest.get("dbfilter", "")
    m = re.match(r"\^(\d+)_(.*?)(\(.*\))?\$?$", dbf)
    if m:
        conv["dbfilter_pattern"] = "^{version}_{instance}(_.*)?$"
    else:
        conv["dbfilter_pattern"] = dbf or "^{version}_{instance}(_.*)?$"

    # Port pattern — pick first free assuming offsets like the latest.
    # (xmlrpc_port fallback kept only to read legacy confs; new confs drop it.
    # No longpolling/gevent port is tracked — the WebSocket rides http_port.)
    conv["http_port_seen"] = latest.get("http_port") or latest.get("xmlrpc_port")

    return conv


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=None)
    args = ap.parse_args()

    start = Path(args.repo_root or Path(__file__).parent).resolve()
    repo_root = find_repo_root(start)

    versions = detect_versions(repo_root)
    report = {
        "repo_root": str(repo_root),
        "versions": versions,
        "ides": detect_ides(repo_root),
        "instances": detect_instances(repo_root, versions),
        "venv": detect_venv(repo_root, versions),
        "odoo_sh": detect_odoo_sh(repo_root),
        "bare_metal": detect_bare_metal(),
        "postgres": detect_postgres(),
        "nginx": detect_nginx(),
    }
    report["convention"] = infer_convention(report["instances"], repo_root)
    classification = classify_architecture(report)
    report["architecture"] = classification["architecture"]
    report["architecture_signals"] = classification["signals"]
    report["architecture_alternatives"] = classification["alternatives"]

    json.dump(report, sys.stdout, indent=2, default=str)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
