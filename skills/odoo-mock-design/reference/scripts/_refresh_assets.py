#!/usr/bin/env python3
"""_refresh_assets.py — idempotent re-copy of catalog assets into a mock package.

The catalog (`reference/catalog/`) is the source of truth for `odoo.css`,
`annotations.css`, `walkthrough.js`, and the two brand images
(`odoo-icon.svg`, `odoo-logo.png`). When the catalog is updated, every
existing mock's `assets/` copies go stale — `_lint_mock.py`'s STALE-ASSET
rule catches the drift via SHA-256 diff.

This script is the documented fix path. It overwrites the asset files only;
it never touches `index.html`. Safe to run repeatedly; safe to run on any
mock package regardless of how it was built (`_scaffold_mock.py` or by hand).

Usage:
    python3 _refresh_assets.py <package_dir>

    # Example:
    python3 skills/odoo-mock-design/reference/scripts/_refresh_assets.py \
        "specifications/TEST001 - INTERNAL - my-feature/mocks/"

Exit 0 on success (or no-op when assets are already fresh).
Exit 2 if the package dir or expected `assets/` subfolder is missing.

No third-party dependencies (stdlib only).
"""
import argparse
import hashlib
import os
import shutil
import sys

CATALOG_ASSETS = (
    "odoo.css",
    "annotations.css",
    "walkthrough.js",
    "odoo-icon.svg",
    "odoo-logo.png",
)


def _catalog_dir():
    """Locate the catalog dir relative to this script."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "catalog"))


def _sha256(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def refresh(package_dir):
    if not os.path.isdir(package_dir):
        print(f"ERROR: package dir does not exist: {package_dir}", file=sys.stderr)
        return 2

    assets_dir = os.path.join(package_dir, "assets")
    if not os.path.isdir(assets_dir):
        print(f"ERROR: no `assets/` subfolder in {package_dir}", file=sys.stderr)
        return 2

    catalog = _catalog_dir()
    refreshed, fresh = [], []
    for name in CATALOG_ASSETS:
        src = os.path.join(catalog, name)
        dst = os.path.join(assets_dir, name)
        if not os.path.isfile(src):
            print(f"WARN: catalog asset missing: {src}", file=sys.stderr)
            continue
        if os.path.isfile(dst) and _sha256(src) == _sha256(dst):
            fresh.append(name)
            continue
        shutil.copy2(src, dst)
        refreshed.append(name)

    if refreshed:
        print(f"Refreshed {len(refreshed)} asset(s) in {assets_dir}/:")
        for name in refreshed:
            print(f"  - {name}")
    if fresh:
        print(f"Already fresh: {', '.join(fresh)}")
    if not refreshed and not fresh:
        print("No catalog assets present in the package; nothing to refresh.")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else "")
    ap.add_argument("package_dir", help="path to the mock package (the dir containing index.html + assets/)")
    args = ap.parse_args(argv)
    return refresh(args.package_dir)


if __name__ == "__main__":
    sys.exit(main())
