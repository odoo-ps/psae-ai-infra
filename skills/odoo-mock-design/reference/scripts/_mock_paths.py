"""Shared path rules for an odoo-mock-design output folder.

Layout:

    <mocks>/                        <spec-folder>/mocks/  or  <repo>/mocks/<kebab>/
    ├── <name> - mock.html          DELIVERABLE — one self-contained file, built by
    │                               _bundle_mock.py after the final checks pass
    └── _reference/                 WORKING PACKAGE the bundle is built from
        ├── index.html              (edit here; lint / anchors / renders run here)
        ├── assets/                 odoo.css, annotations.css, walkthrough.js, icons
        └── README.md               optional notes (mappings, deferred findings)

<name> is the spec folder's name when <mocks> is `<spec-folder>/mocks/`, else the
mocks folder's own name. Legacy packages (index.html + assets/ directly inside
<mocks>/) still resolve, so older mocks keep linting / rendering.
"""
import os

REF = "_reference"
BUNDLE_SUFFIX = " - mock.html"


def package_dir(path):
    """The working package (dir holding index.html + assets/) for `path`, which
    may be the mocks folder, its _reference/ folder, or a legacy flat package."""
    p = os.path.abspath(path)
    if os.path.isfile(os.path.join(p, REF, "index.html")):
        return os.path.join(p, REF)
    return p


def mocks_root(path):
    """The mocks folder that holds the deliverable (parent of _reference/)."""
    pkg = package_dir(path)
    return os.path.dirname(pkg) if os.path.basename(pkg) == REF else pkg


def bundle_path(path):
    """Where the single-file deliverable lives for this mock."""
    root = mocks_root(path)
    parent = os.path.dirname(root)
    name = os.path.basename(parent) if os.path.basename(root) == "mocks" else os.path.basename(root)
    return os.path.join(root, name + BUNDLE_SUFFIX)
