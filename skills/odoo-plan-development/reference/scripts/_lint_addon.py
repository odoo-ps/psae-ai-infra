"""Stage-1 static linter for an Odoo addon.

Walks the addon directory and surfaces structural problems that would otherwise
fail at install-time (Stage 2) or render-time (Stage 3). No Odoo runtime needed.

Usage:
    python3 _lint_addon.py <addon_path> [--addons-path <p1,p2,...>]

Exits 0 on clean, 1 on any error.
"""
import argparse
import ast
import csv
import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET


issues = []


def err(category: str, where: str, msg: str) -> None:
    issues.append(("ERROR", category, where, msg))


def warn(category: str, where: str, msg: str) -> None:
    issues.append(("WARN", category, where, msg))


def parse_manifest(addon: Path) -> dict | None:
    mf = addon / "__manifest__.py"
    if not mf.exists():
        err("manifest", str(mf), "missing __manifest__.py")
        return None
    try:
        text = mf.read_text()
        tree = ast.parse(text, filename=str(mf))
        # The manifest is a single dict expression
        body = tree.body
        if not body or not isinstance(body[0], ast.Expr) or not isinstance(body[0].value, ast.Dict):
            err("manifest", str(mf), "manifest is not a single dict literal")
            return None
        return ast.literal_eval(body[0].value)
    except Exception as e:
        err("manifest", str(mf), f"parse failure: {e}")
        return None


def check_manifest_keys(addon: Path, m: dict) -> None:
    for k in ("name", "version", "depends"):
        if k not in m:
            err("manifest", "__manifest__.py", f"missing key '{k}'")
    if "data" not in m and "demo" not in m:
        warn("manifest", "__manifest__.py", "no 'data' or 'demo' entries — addon has no XML/CSV?")
    for entry in m.get("data", []) + m.get("demo", []):
        path = addon / entry
        if not path.exists():
            err("manifest", "__manifest__.py", f"data entry not found on disk: {entry}")


def check_security_csv(addon: Path, m: dict) -> set[str]:
    """Return set of model technical names declared in models/."""
    declared_models = set()
    abstract_models = set()
    for py in (addon / "models").glob("*.py") if (addon / "models").is_dir() else []:
        try:
            text = py.read_text()
        except Exception:
            continue
        for match in re.finditer(r"_name\s*=\s*['\"]([\w.]+)['\"]", text):
            declared_models.add(match.group(1))
        # AbstractModel has no DB table → no ir.model.access row is possible or
        # needed (e.g. account.report custom handlers). Exclude its _name from the
        # ACL requirement; TransientModel/Model still require a row.
        for cls in re.finditer(r"class\s+\w+\(([^)]*)\):(.*?)(?=\nclass\s|\Z)", text, re.S):
            if "AbstractModel" in cls.group(1):
                for nm in re.finditer(r"_name\s*=\s*['\"]([\w.]+)['\"]", cls.group(2)):
                    abstract_models.add(nm.group(1))
    declared_models -= abstract_models

    csv_path = addon / "security" / "ir.model.access.csv"
    if declared_models and not csv_path.exists():
        err("security", "security/ir.model.access.csv",
            f"missing — addon declares models {sorted(declared_models)}")
        return declared_models

    if csv_path.exists():
        try:
            with csv_path.open() as f:
                reader = csv.DictReader(f)
                required = {"id", "name", "model_id:id", "perm_read",
                            "perm_write", "perm_create", "perm_unlink"}
                if not required.issubset(set(reader.fieldnames or [])):
                    err("security", str(csv_path),
                        f"header missing columns: {required - set(reader.fieldnames or [])}")
                rows = list(reader)
                if not rows:
                    warn("security", str(csv_path), "file has no data rows")
                covered = {r["model_id:id"].removeprefix("model_") for r in rows
                           if r.get("model_id:id", "").startswith("model_")}
                # Convert from underscore form back to dotted: model_my_model -> my.model
                covered_dotted = {c.replace("_", ".") for c in covered}
                missing = declared_models - covered_dotted
                if missing:
                    warn("security", str(csv_path),
                         f"models without ACL row (best-effort match): {sorted(missing)}")
        except Exception as e:
            err("security", str(csv_path), f"parse failure: {e}")
    return declared_models


def check_xml_views(addon: Path, declared_models: set[str]) -> None:
    for xml in addon.rglob("*.xml"):
        try:
            tree = ET.parse(xml)
        except ET.ParseError as e:
            err("xml", str(xml), f"parse error: {e}")
            continue
        # Bracket balance is implicit in well-formed XML. Check that <field name="model"> values
        # for ir.ui.view records reference plausible model names.
        for rec in tree.iter("record"):
            if rec.get("model") == "ir.ui.view":
                model_field = rec.find("./field[@name='model']")
                if model_field is not None and model_field.text:
                    target = model_field.text.strip()
                    # We can only check declared_models; can't validate models from
                    # depended-on addons without full path resolution. Skip if unknown.
                    if "." not in target:
                        warn("xml", str(xml),
                             f"view targets model {target!r} which lacks a dot — likely typo")


def check_python_hygiene(addon: Path) -> None:
    for py in addon.rglob("*.py"):
        if "/migrations/" in str(py):
            continue
        text = py.read_text(errors="replace")
        if re.search(r"^\s*print\s*\(", text, re.MULTILINE):
            err("python", str(py), "contains print(...) — use _logger instead")
        # Mixed tabs/spaces
        if "\t" in text and re.search(r"^    ", text, re.MULTILINE):
            warn("python", str(py), "mixes tabs and spaces")
        try:
            ast.parse(text, filename=str(py))
        except SyntaxError as e:
            err("python", str(py), f"syntax error: {e}")


def check_inherits(addon: Path, addons_path: list[Path]) -> None:
    """Best-effort: every _inherit target should resolve to a known model
    in any addon under addons_path or in this addon's own models."""
    known_models = set()
    for ap in addons_path:
        for py in ap.rglob("models/*.py"):
            try:
                text = py.read_text(errors="replace")
            except Exception:
                continue
            for m in re.finditer(r"_name\s*=\s*['\"]([\w.]+)['\"]", text):
                known_models.add(m.group(1))
    for py in (addon / "models").glob("*.py") if (addon / "models").is_dir() else []:
        text = py.read_text(errors="replace")
        for inh in re.finditer(r"_inherit\s*=\s*['\"]([\w.]+)['\"]", text):
            target = inh.group(1)
            if target not in known_models:
                # Could also be a list-form _inherit
                warn("inherit", str(py),
                     f"_inherit target {target!r} not found in addons_path "
                     "(may still resolve via uninspected addon)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("addon", help="path to the addon directory")
    ap.add_argument("--addons-path", default="",
                    help="comma-separated list of additional addons-path roots to grep "
                         "for _inherit resolution")
    args = ap.parse_args()

    addon = Path(args.addon).resolve()
    if not addon.is_dir():
        print(f"FAIL: {addon} is not a directory")
        return 2

    extra_paths = [Path(p).resolve() for p in args.addons_path.split(",") if p.strip()]

    print(f"--- Linting addon: {addon}")
    m = parse_manifest(addon)
    if m is None:
        print(f"--- {len(issues)} issue(s); aborting before deeper checks")
        for sev, cat, where, msg in issues:
            print(f"  {sev:5s} [{cat}] {where}: {msg}")
        return 1

    check_manifest_keys(addon, m)
    declared_models = check_security_csv(addon, m)
    check_xml_views(addon, declared_models)
    check_python_hygiene(addon)
    check_inherits(addon, extra_paths or [addon.parent])

    errors = [i for i in issues if i[0] == "ERROR"]
    warns = [i for i in issues if i[0] == "WARN"]
    print(f"--- {len(errors)} error(s), {len(warns)} warning(s)")
    for sev, cat, where, msg in issues:
        print(f"  {sev:5s} [{cat}] {where}: {msg}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
