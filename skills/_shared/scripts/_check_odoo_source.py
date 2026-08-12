#!/usr/bin/env python3
"""Verify standard-Odoo model claims against on-disk source.

Modes:
  --probe                    Addons-path availability check; canonical
                             warning + exit 1 if unreachable.

Roots are the fixed Odoo.sh paths (/home/odoo/src/{odoo,enterprise}) plus the
Project Repo named by --cwd, which is the custom-addons root on a branch.
  --models m1,m2,m3          Batch resolve each model to {exists, module,
                             edition, path}.
  --plan <file>              Regex-extract _inherit / Many2one / Many2many /
                             One2many comodel / env[...] claims from a plan
                             file, then resolve each (skipping models the
                             plan itself declares via _name).

Output: JSON to stdout. Status / warnings to stderr.
Exit codes: 0 all resolved, 1 source unavailable, 2 some claims missing.

Speed: one ripgrep invocation per addons-root with an alternation pattern
covering ALL models — total wall-clock ~0.5–1s regardless of model count.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Absolute addons roots on an Odoo.sh container. These are fixed by the
# platform (principle #13) — there is no version folder and no `instances/`
# tree, so nothing here is relative to the caller's cwd. `--cwd` still names
# the Project Repo, which is itself the custom-addons root on Odoo.sh.
ADDONS_ROOTS = [
    ("/home/odoo/src/odoo/addons", "community"),
    ("/home/odoo/src/odoo/odoo/addons", "community"),
    ("/home/odoo/src/enterprise", "enterprise"),
]

GREP_TOOL = "rg" if shutil.which("rg") else "grep"


def _edition(rel):
    """Edition tag for a relative addons root — independent of the glob branch
    it resolves through (a `v*` prefix makes every root a glob, so this can't
    key off `*`-ness)."""
    if "enterprise" in rel:
        return "enterprise"
    if "custom_addons" in rel:
        return "custom"
    return "community"


def resolve_roots(cwd, root_prefix=None):
    """Absolute platform roots, plus the Project Repo as the custom-addons root.

    `root_prefix` is accepted and ignored — it existed for a multi-version
    workstation layout that no longer exists. Kept so an old call site does not
    crash; it has no effect.
    """
    found = [(Path(r), ed) for r, ed in ADDONS_ROOTS if Path(r).is_dir()]
    repo = Path(cwd)
    if repo.is_dir():
        found.append((repo, "custom"))
    return found


def probe(cwd, root_prefix=None):
    roots = resolve_roots(cwd, root_prefix)
    if not roots:
        sys.stderr.write(
            "WARNING: Odoo source not found under "
            + ", ".join(r for r, _ in ADDONS_ROOTS)
            + ". Standard-Odoo claims cannot be verified — surface this on the deliverable.\n"
        )
        print(json.dumps({"available": False, "roots": []}))
        return 1
    print(json.dumps({
        "available": True,
        "roots": [{"path": str(p), "edition": e} for p, e in roots],
    }))
    return 0


def _score(model, path, module):
    """Lower = more canonical. Prefers <model.split('.')[0]>/models/<model_underscored>.py."""
    expected_file = model.replace(".", "_") + ".py"
    expected_module = model.split(".")[0]
    score = 0
    if Path(path).name != expected_file:
        score += 2
    if "/models/" not in path:
        score += 4
    if "/tests/" in path or "/static/" in path:
        score += 8
    if module != expected_module:
        score += 1
    return score


def grep_models(models, roots):
    results = {
        m: {"exists": False, "module": None, "edition": None, "path": None}
        for m in models
    }
    candidates = {m: [] for m in models}
    alt = "|".join(re.escape(m) for m in models)
    pattern = r"_name\s*=\s*['\"](" + alt + r")['\"]"
    for path, edition in roots:
        if GREP_TOOL == "rg":
            cmd = ["rg", "--no-heading", "-n", "-g", "*.py", pattern, str(path)]
        else:
            cmd = ["grep", "-rnE", "--include=*.py", pattern, str(path)]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        except subprocess.TimeoutExpired:
            continue
        if r.returncode not in (0, 1):
            continue
        for line in r.stdout.splitlines():
            parts = line.split(":", 2)
            if len(parts) < 3:
                continue
            file_path, _, content = parts
            m = re.search(pattern, content)
            if not m:
                continue
            model = m.group(1)
            try:
                rel = Path(file_path).relative_to(path)
                module = rel.parts[0]
                candidates[model].append({
                    "module": module,
                    "edition": edition,
                    "path": file_path,
                    "_score": _score(model, file_path, module),
                })
            except ValueError:
                continue
    for model, cands in candidates.items():
        if not cands:
            continue
        cands.sort(key=lambda c: c["_score"])
        best = cands[0]
        results[model] = {
            "exists": True,
            "module": best["module"],
            "edition": best["edition"],
            "path": best["path"],
        }
    return results


def check_models(models, cwd, root_prefix=None):
    roots = resolve_roots(cwd, root_prefix)
    if not roots:
        sys.stderr.write("Source unavailable — cannot verify claims.\n")
        print(json.dumps({"available": False}))
        return 1
    results = grep_models(models, roots)
    missing = [m for m, r in results.items() if not r["exists"]]
    print(json.dumps(results, indent=2))
    if missing:
        sys.stderr.write("Unresolved: " + ", ".join(missing) + "\n")
        return 2
    return 0


CLAIM_PATTERNS = [
    re.compile(r"_inherit\s*=\s*['\"]([^'\"]+)['\"]"),
    re.compile(r"Many2one\(\s*['\"]([^'\"]+)['\"]"),
    re.compile(r"Many2many\(\s*['\"]([^'\"]+)['\"]"),
    re.compile(r"One2many\(\s*['\"][^'\"]+['\"]\s*,\s*['\"]([^'\"]+)['\"]"),
    re.compile(r"env\[\s*['\"]([^'\"]+)['\"]"),
]


def extract_claims(plan_path):
    text = Path(plan_path).read_text()
    new_models = set(re.findall(r"_name\s*=\s*['\"]([^'\"]+)['\"]", text))
    claims = set()
    for pat in CLAIM_PATTERNS:
        claims.update(pat.findall(text))
    return sorted(claims - new_models)


def check_plan(plan_path, cwd, root_prefix=None):
    claims = extract_claims(plan_path)
    if not claims:
        print(json.dumps({"claims": [], "results": {}}))
        return 0
    return check_models(claims, cwd, root_prefix)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--probe", action="store_true")
    p.add_argument("--models", help="Comma-separated model names")
    p.add_argument("--plan", help="Plan file to extract claims from")
    p.add_argument("--cwd", default=os.getcwd(), help="Project root (default: cwd)")
    p.add_argument("--root-prefix", default=None,
                   help=argparse.SUPPRESS)  # deprecated no-op; roots are fixed
    args = p.parse_args()

    if args.probe:
        return probe(args.cwd, args.root_prefix)
    if args.models:
        return check_models(
            [m.strip() for m in args.models.split(",") if m.strip()],
            args.cwd, args.root_prefix,
        )
    if args.plan:
        return check_plan(args.plan, args.cwd, args.root_prefix)
    p.error("Specify one of --probe / --models / --plan")


if __name__ == "__main__":
    sys.exit(main())
