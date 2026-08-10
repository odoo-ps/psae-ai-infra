"""Create a new Odoo instance: folder, conf file, IDE config patches, nginx
reverse-proxy config, and (with confirmation) DB.

The script is conservative: in default (dry-run) mode it prints the planned
actions and the createdb / odoo-bin / sudo commands, but does NOT run them.
Pass --write to actually create folder + conf + patch IDE configs + write +
symlink the nginx config. The DB is never created by this script and sudo
operations (/etc/hosts append + nginx reload) are also never run — the caller
(the agent) is responsible for showing the confirmation block to the user
and executing those commands.

Adaptive scaffolding:
  - First runs `_detect_environment.py` to find existing IDE configs and
    sibling instance conventions.
  - If a sibling convention exists, mirrors it (folder name = instance, conf
    filename, custom_addons dirname, dbfilter pattern).
  - If nothing exists, falls back to the canonical layout from SKILL.md
    Pre-Flight A and asks the user (via the agent) whether to proceed.

IDE patches (only when the relevant config is detected):
  - VS Code (`.vscode/launch.json`) and Cursor (`.cursor/launch.json`) get a
    new `configurations[]` entry pointing at the new conf, using a
    JSONC-tolerant in-place edit that preserves comments and surrounding
    formatting.
  - JetBrains (`.idea/`): NOT auto-patched (XML diffs risky); the script prints
    a suggested run-config snippet for the user to add.

Version routing:
  - `--version <major>` (e.g. 19) selects the on-disk stack under `v<major>/`
    (v19/, v20/, …). addons_path, odoo-bin, venv, instance folder, and the IDE
    launch config all route to that version. The version folder must already
    exist (validated against `_detect_environment.py`'s `versions` list).

nginx reverse-proxy (only when an nginx include dir is detected):
  - Writes `v<major>/instances/<name>/nginx.conf` (the source of truth, version-able).
  - Symlinks it into the platform nginx servers/conf.d dir as
    `odoo_<name>.conf` (Apple Silicon brew, Intel brew, RHEL conf.d, or
    Debian sites-enabled — first match wins).
  - The conf template sets `proxy_mode = True` and a `# Public URL` comment.
  - Prints the sudo follow-up commands (/etc/hosts append + nginx reload).
    These are never run automatically.
  - Pass `--no-nginx` to skip this entirely (e.g. server/headless setups).

Usage:
    python3 _create_instance.py --instance acme_dev --version 19 \\
        [--demo] [--write] [--no-nginx]
"""
import argparse
import json
import os
import re
import secrets
import shutil
import string
import subprocess
import sys
from configparser import ConfigParser
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers (shared with the rest of the skill)
# ---------------------------------------------------------------------------

# A version folder is `v<major>/` (v19, v20, …) with an `odoo/` source inside.
# Mirrors _detect_environment.VERSION_DIR_RE — kept as an independent copy
# because the two scripts are invoked separately.
_VERSION_DIR_RE = re.compile(r"^v(\d+)$")


def find_repo_root(start: Path) -> Path:
    cur = start.resolve()
    for _ in range(10):
        if (cur / "skills").is_dir() and any(
            _VERSION_DIR_RE.match(c.name) and (c / "odoo").is_dir()
            for c in cur.iterdir() if c.is_dir()
        ):
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    raise RuntimeError(f"Could not locate repo root above {start}")


def free_http_port(repo_root: Path, default_pool=(8069, *range(8019, 8200, 10))):
    used = set()
    # Ports bind to localhost regardless of Odoo version, so scan EVERY version
    # folder's instances — a v20 instance must not collide with a v19 one.
    for conf in repo_root.glob("v*/instances/*/odoo.conf"):
        cp = ConfigParser()
        try:
            cp.read(conf)
            for key in ("http_port", "xmlrpc_port"):
                if cp.has_option("options", key):
                    try:
                        used.add(int(cp.get("options", key)))
                    except ValueError:
                        pass
        except Exception:
            continue
    for p in default_pool:
        if p not in used:
            return p
    raise RuntimeError(f"All default ports {default_pool} are in use")


def hash_password(plain: str) -> str:
    """pbkdf2-sha512 hash compatible with Odoo's admin_passwd. stdlib fallback."""
    try:
        from passlib.hash import pbkdf2_sha512
        return pbkdf2_sha512.using(rounds=600000).hash(plain)
    except ImportError:
        pass
    try:
        from werkzeug.security import generate_password_hash
        return generate_password_hash(plain, method="pbkdf2:sha512:600000")
    except ImportError:
        pass
    import base64
    import hashlib
    rounds = 600000
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha512", plain.encode(), salt, rounds, dklen=64)
    def _b64(b: bytes) -> str:
        return base64.b64encode(b).decode().replace("+", ".").rstrip("=")
    return f"$pbkdf2-sha512${rounds}${_b64(salt)}${_b64(dk)}"


def random_password(length: int = 24) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def validate_instance_name(name: str) -> None:
    if not re.match(r"^[a-z][a-z0-9_]*$", name):
        raise SystemExit(
            f"Invalid instance name {name!r}: must be lowercase, start with a letter, "
            "contain only [a-z0-9_]."
        )


# ---------------------------------------------------------------------------
# Environment detection (delegated)
# ---------------------------------------------------------------------------

def detect_environment(repo_root: Path) -> dict:
    here = Path(__file__).parent
    detector = here / "_detect_environment.py"
    r = subprocess.run(
        [sys.executable, str(detector), "--repo-root", str(repo_root)],
        capture_output=True, text=True, timeout=30,
    )
    if r.returncode != 0:
        raise SystemExit(f"_detect_environment.py failed:\n{r.stderr}")
    return json.loads(r.stdout)


# ---------------------------------------------------------------------------
# Conf rendering — adapts to the detected convention
# ---------------------------------------------------------------------------

def render_conf(repo_root: Path, instance: str, version: str,
                http_port: int, hashed_pwd: str,
                custom_addons_dirname: str, dbfilter_pattern: str) -> str:
    # `version` is the Odoo major (e.g. "19"); the on-disk stack lives under the
    # matching version folder `v<major>/` (e.g. v19/). Path routing derives from
    # it so a v20 instance points its addons_path at v20/odoo, v20/enterprise, …
    version_folder = f"v{version}"
    # Version-qualified hostname == the DB name (<major>_<instance>).
    host = f"{version}_{instance}"
    dbfilter = dbfilter_pattern.replace("{version}", version).replace("{instance}", instance)
    return f"""[options]
; --- Public URL ---
; Reverse-proxied via nginx — see {version_folder}/instances/{instance}/nginx.conf
; Public URL: https://{host}.internal/
proxy_mode = True

; --- Security ---
admin_passwd = {hashed_pwd}

; --- Database Settings ---
db_host = localhost
db_port = 5432
db_user = odoo
dbfilter = {dbfilter}

; --- Network Settings ---
; Single-process dev (workers=0): Discuss WebSocket rides http_port; nginx proxies /websocket here.
http_port = {http_port}

; --- Addons Paths ---
; Order matters: Odoo looks for modules left-to-right.
addons_path =
    {repo_root}/{version_folder}/odoo/odoo/addons,
    {repo_root}/{version_folder}/odoo/addons,
    {repo_root}/{version_folder}/enterprise,
    {repo_root}/{version_folder}/instances/{instance}/{custom_addons_dirname}
"""


# ---------------------------------------------------------------------------
# nginx scaffolding — drop a per-instance reverse-proxy config and symlink it
# into the platform's nginx include dir.
# ---------------------------------------------------------------------------

# Candidate include dirs for various nginx layouts. First one that exists wins.
_NGINX_INCLUDE_CANDIDATES = (
    "/opt/homebrew/etc/nginx/servers",   # macOS Apple Silicon, brew
    "/usr/local/etc/nginx/servers",      # macOS Intel, brew
    "/etc/nginx/conf.d",                 # Linux (RHEL/CentOS) yum
    "/etc/nginx/sites-enabled",          # Linux (Debian/Ubuntu) apt
)


def detect_nginx() -> dict:
    """Return {'available': bool, 'include_dir': Path|None, 'log_dir': Path|None}.

    Best-effort detection — never raises. The caller decides whether to scaffold
    nginx based on `available`.
    """
    out = {"available": False, "include_dir": None, "log_dir": None}
    for cand in _NGINX_INCLUDE_CANDIDATES:
        p = Path(cand)
        if p.is_dir():
            out["available"] = True
            out["include_dir"] = p
            # Best-guess log dir for that prefix
            if "/opt/homebrew/" in cand:
                out["log_dir"] = Path("/opt/homebrew/var/log/nginx")
            elif "/usr/local/" in cand:
                out["log_dir"] = Path("/usr/local/var/log/nginx")
            else:
                out["log_dir"] = Path("/var/log/nginx")
            break
    return out


def render_nginx_conf(instance: str, host: str, http_port: int, websocket_port: int,
                      log_dir: Path | None, repo_root: Path) -> str:
    # `host` is the version-qualified id `<major>_<instance>` (== the DB name),
    # used for the routable hostname `<host>.internal`, the upstream block names,
    # the vhost symlink filename, and the log filenames — so the same instance
    # name under two version folders never collides in nginx. `instance` is kept
    # only as the human-readable label comment.
    log_prefix = (log_dir or Path("/var/log/nginx")).as_posix()
    cert = (repo_root / ".nginx" / "certs" / "instances.internal.pem").as_posix()
    key = (repo_root / ".nginx" / "certs" / "instances.internal-key.pem").as_posix()
    return f"""# Odoo instance: {instance}  (host {host}.internal)
# Generated by skills/odoo-plan-development/reference/scripts/_create_instance.py
# Public URL: https://{host}.internal/  (HTTP on :80 redirects to HTTPS on :443)
#
# Symlinked from the platform nginx servers/ dir back to this file. Edits
# made directly to the symlink target take effect immediately; reload nginx
# with `nginx -s reload` (or `sudo nginx -s reload` if it runs as root).
#
# HTTPS uses a mkcert-issued cert at .nginx/certs/. The mkcert root CA must be
# installed in the macOS keychain (`mkcert -install`, one-time). The cert
# covers every instance under v*/instances/; this script regenerates the cert
# each time a new instance is scaffolded — see regenerate_instances_cert().

upstream odoo_{host} {{
    server 127.0.0.1:{http_port};
}}
# Discuss WebSocket — single-process (workers=0) serves it on http_port.
upstream odoo_{host}_chat {{
    server 127.0.0.1:{websocket_port};
}}

# HTTP -> HTTPS redirect (port 80 -> 443)
server {{
    listen 80;
    server_name {host}.internal;
    return 301 https://$host$request_uri;
}}

server {{
    listen 443 ssl;
    ssl_certificate     {cert};
    ssl_certificate_key {key};
    ssl_protocols TLSv1.2 TLSv1.3;
    server_name {host}.internal;

    # Long timeouts for module install / heavy operations
    proxy_read_timeout 720s;
    proxy_connect_timeout 720s;
    proxy_send_timeout 720s;

    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Real-IP $remote_addr;

    gzip on;
    gzip_types text/css text/scss text/plain text/xml application/xml application/json application/javascript;

    # Bus / chatter websocket
    location /websocket {{
        proxy_pass http://odoo_{host}_chat;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Real-IP $remote_addr;
    }}

    # Legacy longpolling fallback
    location /longpolling {{
        proxy_pass http://odoo_{host}_chat;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }}

    location / {{
        proxy_pass http://odoo_{host};
        proxy_redirect off;
        # `proxy_http_version 1.1` + empty `Connection` header is the standard
        # Odoo nginx pattern (also in Odoo's official deployment docs). It
        # keeps the upstream connection alive long enough for Odoo to write
        # the full response — without it, nginx forwards `Connection: close`
        # and Odoo cuts the stream early, truncating downloads at ~216 bytes.
        # NOTE: do NOT add `proxy_buffering off` here. With buffering on,
        # nginx reads the full response, computes Content-Length, and forwards
        # it intact — which is what lets Chrome cleanly finalize `.crdownload`
        # temp files. Disabling buffering creates a Content-Length / chunked
        # framing mismatch and Chrome holds downloads in queue indefinitely.
        # See troubleshooting #48.
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }}

    # Static-asset caching
    location ~* /web/static/ {{
        proxy_cache_valid 200 60m;
        proxy_buffering on;
        expires 864000;
        proxy_pass http://odoo_{host};
    }}

    access_log {log_prefix}/odoo_{host}.access.log;
    error_log  {log_prefix}/odoo_{host}.error.log;
}}
"""


def instance_host(conf_path: Path) -> str | None:
    """Version-qualified host id for an instance — i.e. its DB name, which is
    also `<host>.internal` minus the suffix.

    The DB name is the single source of truth (host == DB name), read from the
    conf's `dbfilter` core (`^<db>(_.*)?$` → `<db>`). For a normal instance
    folder `<name>` under `v<major>/` that is `<major>_<name>`; for a legacy
    folder that already embeds its version (e.g. `19_keeper`, dbfilter
    `^19_keeper...`) it stays `19_keeper` — NOT `19_19_keeper` — so the existing
    URL is preserved. Falls back to `<major>_<name>` if the dbfilter is absent
    or unparseable. None if the path isn't under a `v<major>/instances/` tree."""
    name = conf_path.parent.name
    vfolder = conf_path.parents[2].name if len(conf_path.parents) >= 3 else ""
    vm = _VERSION_DIR_RE.match(vfolder)
    if not vm or name.startswith("_"):
        return None
    try:
        cp = ConfigParser()
        cp.read(conf_path)
        dbf = cp.get("options", "dbfilter", fallback="").strip()
    except Exception:
        dbf = ""
    core = re.match(r"\^?([A-Za-z0-9_]+)", dbf)
    return core.group(1) if core else f"{vm.group(1)}_{name}"


def regenerate_instances_cert(repo_root: Path) -> str:
    """Run mkcert against every instance's version-qualified `.internal` host.

    The cert at .nginx/certs/instances.internal.{pem,key.pem} is shared across
    ALL version folders. Hostnames are version-qualified (`<major>_<name>.internal`,
    matching the DB name), so the same instance name in v19 and v20 yields TWO
    distinct SANs and both coexist. The SAN list is the union across every
    `v*/instances/` tree. Idempotent: same set → identical cert.

    Requires mkcert on PATH and `mkcert -install` to have been run once
    (one-time, adds the local CA to the macOS keychain). If mkcert is
    missing, returns a warning string but doesn't fail the scaffold —
    the user can install mkcert and re-run separately.
    """
    if not shutil.which("mkcert"):
        return ("  mkcert not on PATH — skipping HTTPS cert regen. "
                "Install with `brew install mkcert && mkcert -install`, then "
                "re-run this script or regenerate manually.")
    cert_dir = repo_root / ".nginx" / "certs"
    cert_dir.mkdir(parents=True, exist_ok=True)
    hostnames = sorted({
        f"{h}.internal"
        for conf in repo_root.glob("v*/instances/*/odoo.conf")
        if (h := instance_host(conf))
    })
    if not hostnames:
        return "  No instances found under any v*/instances/ — skipping cert regen."
    cert_path = cert_dir / "instances.internal.pem"
    key_path = cert_dir / "instances.internal-key.pem"
    cmd = [
        "mkcert",
        "-cert-file", str(cert_path),
        "-key-file", str(key_path),
        *hostnames,
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        return f"  mkcert failed: {e.stderr.strip()}"
    return f"  Regenerated {cert_path.name} covering {len(hostnames)} instance(s)."


def write_nginx_config(instance_dir: Path, instance: str, host: str, http_port: int,
                        websocket_port: int, nginx_info: dict, dry_run: bool,
                        repo_root: Path) -> str:
    """Write <version>/instances/<instance>/nginx.conf and symlink into servers/.

    `host` is the version-qualified id `<major>_<instance>` — it names the vhost
    symlink (`odoo_<host>.conf`) and log files so the same instance name in two
    version folders never collides. Returns a one-line status string. Idempotent:
    an existing symlink with the right target is left alone.
    """
    nginx_path = instance_dir / "nginx.conf"
    if not nginx_info.get("available"):
        return "  No nginx include dir detected — skipping nginx scaffold."
    include_dir = nginx_info["include_dir"]
    link = include_dir / f"odoo_{host}.conf"
    log_dir = nginx_info.get("log_dir")
    text = render_nginx_conf(instance, host, http_port, websocket_port, log_dir, repo_root)
    if dry_run:
        return (f"  WOULD WRITE   {nginx_path}\n"
                f"  WOULD SYMLINK {link} -> {nginx_path}")
    nginx_path.write_text(text)
    # Symlink (overwrite if a different one exists)
    try:
        if link.is_symlink() or link.exists():
            link.unlink()
        link.symlink_to(nginx_path.resolve())
    except PermissionError as e:
        return f"  WROTE {nginx_path} — but could not symlink into {include_dir} ({e})"
    # Pre-touch access/error log files as the invoking user. Why: on the first
    # `sudo nginx -s reload` (or `sudo brew services restart nginx`) the master
    # runs as root and creates any missing log files as root:wheel. Subsequent
    # `nginx -t` invocations then simulate opening these files as the worker
    # user (`nobody`) and fail with EACCES because 644 + root-owned blocks the
    # write check — and `setup_nginx_sudo.sh` aborts at step 2 before reload.
    # Creating the files first as the user dodges the whole trap.
    touched = []
    if log_dir and log_dir.is_dir():
        for kind in ("access", "error"):
            f = log_dir / f"odoo_{host}.{kind}.log"
            if not f.exists():
                try:
                    f.touch()
                    touched.append(f.name)
                except (PermissionError, OSError):
                    pass
    extra = f"\n  TOUCHED {', '.join(touched)} in {log_dir}" if touched else ""
    return f"  WROTE  {nginx_path}\n  SYMLINK {link} -> {nginx_path}{extra}"


# ---------------------------------------------------------------------------
# launch.json patcher (JSONC-tolerant, preserves comments/formatting)
# ---------------------------------------------------------------------------

def _strip_jsonc(text: str) -> str:
    """Strip // line comments, /* */ block comments, and trailing commas — ONLY
    for parsing/validation. The actual patcher writes back the original text
    with a single targeted insertion."""
    out = []
    i, n = 0, len(text)
    in_str = False
    str_quote = ""
    escape = False
    while i < n:
        c = text[i]
        if in_str:
            out.append(c)
            if escape:
                escape = False
            elif c == "\\":
                escape = True
            elif c == str_quote:
                in_str = False
            i += 1
            continue
        if c == '"':
            in_str = True
            str_quote = c
            out.append(c)
            i += 1
            continue
        # Block comment
        if c == "/" and i + 1 < n and text[i + 1] == "*":
            j = text.find("*/", i + 2)
            i = (j + 2) if j != -1 else n
            continue
        # Line comment
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            j = text.find("\n", i + 2)
            i = j if j != -1 else n
            continue
        out.append(c)
        i += 1
    s = "".join(out)
    # Remove trailing commas
    s = re.sub(r",(\s*[}\]])", r"\1", s)
    return s


def _detect_indent(text: str) -> str:
    """Heuristic — look at the first inline-array entry's leading whitespace."""
    m = re.search(r"\n([ \t]+)\{", text)
    return m.group(1) if m else "  "


def patch_launch_json(launch_path: Path, instance: str, conf_relpath: str,
                      venv_relpath: str | None, version_folder: str,
                      dry_run: bool) -> str:
    """Add a new VS Code / Cursor debug configuration for this instance.

    Returns a description of what would change (or did change). Idempotent:
    if a configuration with the same `name` already exists, no change.
    """
    raw = launch_path.read_text()
    try:
        parsed = json.loads(_strip_jsonc(raw))
    except json.JSONDecodeError as e:
        return f"  SKIP: {launch_path} did not parse as JSONC: {e}"

    existing_names = []
    if isinstance(parsed, dict) and isinstance(parsed.get("configurations"), list):
        existing_names = [c.get("name") for c in parsed["configurations"] if isinstance(c, dict)]

    # Version-qualified name so the same instance name in two version folders
    # (v19/instances/acme and v20/instances/acme) yields distinct, non-colliding
    # run entries in the IDE's Run dropdown.
    cfg_name = f"Odoo {instance} ({version_folder})"
    if cfg_name in existing_names:
        return f"  SKIP: {launch_path} already has a configuration named {cfg_name!r}"

    # Build the new configuration.
    new_cfg = {
        "name": cfg_name,
        "type": "python",
        "request": "launch",
        "program": "${workspaceFolder}/" + version_folder + "/odoo/odoo-bin",
        "console": "integratedTerminal",
        "args": [
            "--config",
            "${workspaceFolder}/" + conf_relpath,
            "--limit-time-real", "9999",
            "--dev=all",
        ],
        "justMyCode": False,
        "cwd": "${workspaceFolder}",
        "env": {"PYTHONUNBUFFERED": "1"},
    }
    if venv_relpath:
        new_cfg["python"] = "${workspaceFolder}/" + venv_relpath

    # Find the closing `]` of the `configurations` array textually so we
    # preserve comments and formatting outside the array.
    m = re.search(r'"configurations"\s*:\s*\[', raw)
    if not m:
        return f"  SKIP: {launch_path} has no 'configurations' array"

    array_start = m.end()
    depth = 1
    i = array_start
    in_str = False
    str_quote = ""
    escape = False
    while i < len(raw) and depth > 0:
        c = raw[i]
        if in_str:
            if escape:
                escape = False
            elif c == "\\":
                escape = True
            elif c == str_quote:
                in_str = False
        else:
            if c == '"':
                in_str = True
                str_quote = c
            elif c == "[":
                depth += 1
            elif c == "]":
                depth -= 1
                if depth == 0:
                    break
        i += 1
    if depth != 0:
        return f"  SKIP: {launch_path} has unbalanced 'configurations' array"

    array_end = i  # position of the closing `]`
    indent = _detect_indent(raw[array_start:array_end])
    serialised = json.dumps(new_cfg, indent=2)
    serialised = "\n".join(indent + line for line in serialised.splitlines())

    # Find insertion point: right after the last non-whitespace char of the
    # existing array content. That way the comma sits next to the previous
    # entry's `}` instead of on its own indented line.
    array_body = raw[array_start:array_end]
    stripped = array_body.rstrip()
    insert_at = array_start + len(stripped)
    needs_comma = bool(stripped) and stripped[-1] in "}]"

    insertion = ("," if needs_comma else "") + "\n" + serialised + "\n" + indent[:-2]
    new_raw = raw[:insert_at] + insertion + raw[array_end:]

    # Validate the result still parses.
    try:
        json.loads(_strip_jsonc(new_raw))
    except json.JSONDecodeError as e:
        return f"  ERROR: patched output would be invalid JSONC ({e}); skipping"

    if not dry_run:
        launch_path.write_text(new_raw)
        return f"  PATCHED: {launch_path} (added configuration {cfg_name!r})"
    return f"  WOULD PATCH: {launch_path} (would add configuration {cfg_name!r})"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--instance", required=True)
    ap.add_argument("--version", required=True)
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--write", action="store_true",
                    help="Actually create the folder + conf + patch IDE configs.")
    ap.add_argument("--no-nginx", action="store_true",
                    help="Skip nginx reverse-proxy scaffolding (for headless/server setups).")
    args = ap.parse_args()

    validate_instance_name(args.instance)

    repo_root = find_repo_root(Path(__file__).parent)
    env = detect_environment(repo_root)

    # Resolve the target version folder from --version (the Odoo major, e.g. 19):
    # the on-disk stack lives under v<major>/. Validate it exists so a typo or an
    # unbuilt version fails loudly instead of scaffolding into a missing tree.
    version_folder = f"v{args.version}"
    available = {v["version"]: v for v in env.get("versions", [])}
    if version_folder not in available:
        avail = ", ".join(sorted(available)) or "none"
        print(f"ERROR: version folder {version_folder!r} not found under {repo_root}.")
        print(f"       Available version(s): {avail}.")
        print(f"       Create the {version_folder}/ stack (odoo/, enterprise/, instances/)")
        print(f"       first, or pass --version matching an existing version folder.")
        return 1
    version_info = available[version_folder]

    instance_dir = repo_root / version_folder / "instances" / args.instance
    if instance_dir.exists():
        print(f"Instance folder already exists: {instance_dir}")
        print("(idempotency rule — skipping scaffold)")
        return 0

    conv = env.get("convention") or {}
    conf_filename = conv.get("conf_filename", "odoo.conf")
    custom_addons_dirname = conv.get("custom_addons_dirname", "custom_addons")
    dbfilter_pattern = conv.get("dbfilter_pattern", "^{version}_{instance}(_.*)?$")
    based_on = conv.get("based_on")

    conf_path = instance_dir / conf_filename
    db_name = f"{args.version}_{args.instance}"
    # Version-qualified hostname == the DB name, so the instance is reached at
    # https://<major>_<instance>.internal/ and never collides with the same
    # instance name under another version folder.
    host = db_name
    http_port = free_http_port(repo_root)
    # Single-process dev instance: the WebSocket rides the main http port, so the
    # nginx /websocket upstream points here too (no separate longpolling/gevent
    # port is bound when workers = 0).
    websocket_port = http_port
    plain_pwd = random_password()
    hashed_pwd = hash_password(plain_pwd)
    conf_text = render_conf(repo_root, args.instance, args.version,
                            http_port, hashed_pwd,
                            custom_addons_dirname, dbfilter_pattern)
    demo_flag = "" if args.demo else " --without-demo=all"

    print("=" * 72)
    print("Detected environment")
    print("=" * 72)
    print(f"  repo_root           {env['repo_root']}")
    print(f"  Version folders     {sorted(available) or 'none'}")
    print(f"  Target version      {version_folder} "
          f"(Odoo {version_info.get('release_version') or args.version})")
    print(f"  IDEs                {sorted(env.get('ides', {}).keys()) or 'none'}")
    print(f"  Existing instances  "
          f"{[(i['instance'], i.get('version')) for i in env.get('instances', [])] or 'none'}")
    if based_on:
        print(f"  Convention          mirroring {based_on!r}: "
              f"conf={conf_filename}, addons_dir={custom_addons_dirname}, "
              f"dbfilter={dbfilter_pattern}")
    else:
        print("  Convention          NONE detected — using canonical defaults; "
              "the agent should confirm with the user before proceeding.")
    print(f"  venv ({version_folder})          {version_info.get('venv') or '(not found — falling back to default)'}")
    pg = env.get("postgres", {})
    print(f"  Postgres            reachable={pg.get('reachable')} "
          f"version={pg.get('server_version', 'unknown')}")
    print()

    nginx_info = detect_nginx() if not args.no_nginx else {"available": False}

    print("=" * 72)
    print("PLAN: New instance scaffold")
    print("=" * 72)
    print(f"  Folder              {instance_dir}/")
    print(f"  Conf                {conf_path}")
    print(f"  Custom addons dir   {instance_dir}/{custom_addons_dirname}/")
    print(f"  Ports               http={http_port} (WebSocket on same port; single-process)")
    print(f"  DB filter           {dbfilter_pattern.format(version=args.version, instance=args.instance)}")
    print(f"  DB to create        {db_name}")
    print(f"  Demo data           {'ON (--demo flag)' if args.demo else 'OFF (default)'}")
    print(f"  Admin pwd           {plain_pwd}")
    print(f"  Public URL          https://{host}.internal/  (proxy_mode = True)")
    if nginx_info.get("available"):
        print(f"  nginx servers dir   {nginx_info['include_dir']}")
    elif args.no_nginx:
        print(f"  nginx               SKIPPED (--no-nginx)")
    else:
        print(f"  nginx               not detected — set up later; conf already has proxy_mode")
    print()
    print("Privilege probe (run before createdb):")
    print(f"  psql -h localhost -p 5432 -U odoo -d postgres -tAc \\")
    print(f"    \"SELECT rolcreatedb FROM pg_roles WHERE rolname='odoo';\"")
    print("  Expected: 't'. If 'f' or empty, run as a Postgres superuser:")
    print("    ALTER ROLE odoo CREATEDB;")
    print()
    print("DB creation commands (run AFTER user confirmation):")
    print(f"  createdb -h localhost -p 5432 -U odoo {db_name}")
    print(f"  ./{version_folder}/odoo/.venv/bin/python ./{version_folder}/odoo/odoo-bin \\")
    print(f"    -c {conf_path} -d {db_name} --no-http --stop-after-init -i base{demo_flag}")
    print()
    print("Rollback on init failure:")
    print(f"  dropdb -h localhost -p 5432 -U odoo {db_name}")

    # IDE patch plan — use the TARGET version's venv (not the newest-default),
    # so a v20 instance debugs with v20/odoo/.venv.
    ides = env.get("ides", {})
    venv_rel = None
    venv = version_info.get("venv")
    if venv:
        # Don't .resolve() here — that follows symlinks (e.g. .venv/bin/python is
        # often a symlink to pyenv outside the repo), which would make
        # relative_to() throw ValueError. The detector already returns an
        # absolute path under the repo when the venv lives inside the repo.
        try:
            venv_rel = str(Path(venv).relative_to(repo_root))
        except ValueError:
            venv_rel = None

    print()
    print("=" * 72)
    print("IDE configuration")
    print("=" * 72)
    if not ides:
        print("  No IDE config detected — skipping (per skill design).")
    for ide_key in ("vscode", "cursor"):
        ide_info = ides.get(ide_key)
        if ide_info and "launch_json" in ide_info:
            launch = Path(ide_info["launch_json"])
            conf_rel = str(conf_path.resolve().relative_to(repo_root))
            msg = patch_launch_json(launch, args.instance, conf_rel, venv_rel,
                                    version_folder, dry_run=not args.write)
            print(msg)
    if "idea" in ides:
        print(f"  JetBrains config detected at {ides['idea']['path']} — NOT auto-patched.")
        print(f"  Suggested run config to add manually:")
        print(f"    Name:      Odoo {args.instance} ({version_folder})")
        print(f"    Script:    {version_folder}/odoo/odoo-bin")
        print(f"    Args:      --config {version_folder}/instances/{args.instance}/{conf_filename} --limit-time-real 9999 --dev=all")
        print(f"    Interpreter: {venv or '<your venv>'}")

    print()
    print("=" * 72)
    print("nginx reverse proxy")
    print("=" * 72)
    if not args.write:
        nginx_msg = write_nginx_config(instance_dir, args.instance, host, http_port,
                                        websocket_port, nginx_info,
                                        dry_run=True, repo_root=repo_root)
        print(nginx_msg)
    print()
    print("After --write, you still need to run a SUDO step once:")
    print(f"  # Preferred — auto-discovers every instance under ./v*/instances/, idempotent:")
    print(f"  sudo ./.nginx/setup_nginx_sudo.sh")
    print(f"  # Fallback (if .nginx/setup_nginx_sudo.sh is not in the repo):")
    print(f"  echo '127.0.0.1   {host}.internal' | sudo tee -a /etc/hosts")
    print(f"  sudo brew services restart nginx          # macOS/brew")
    print(f"  # OR for Linux:  sudo systemctl reload nginx")
    print("Verify:")
    print(f"  curl -kI https://{host}.internal/web/login")
    print("  (-k skips local-CA check from curl; in the browser the cert is")
    print("   trusted automatically once mkcert -install has been run once.)")

    if args.write:
        print()
        print("--write flag set — creating folder + conf now.")
        instance_dir.mkdir(parents=True, exist_ok=False)
        (instance_dir / custom_addons_dirname).mkdir()
        (instance_dir / custom_addons_dirname / ".gitkeep").touch()
        conf_path.write_text(conf_text)
        print(f"  WROTE {conf_path}")
        print(f"  WROTE {instance_dir}/{custom_addons_dirname}/.gitkeep")
        nginx_msg = write_nginx_config(instance_dir, args.instance, host, http_port,
                                        websocket_port, nginx_info,
                                        dry_run=False, repo_root=repo_root)
        print(nginx_msg)
        # Regenerate the shared mkcert SSL cert to include the new instance
        # hostname in its SAN list (idempotent — same set produces same cert).
        if nginx_info.get("available"):
            cert_msg = regenerate_instances_cert(repo_root)
            print(cert_msg)
        print()
        print("Next: run the privilege probe + DB creation, then the sudo steps above.")
    else:
        print()
        print("(Dry run — no files written, no IDE configs patched. Pass --write to apply.)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
