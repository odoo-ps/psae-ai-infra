#!/usr/bin/env python3
"""_render_catalog.py — visual-regression harness for the catalog.

Renders reference/catalog/_gallery.html (every component, interactive states
force-shown) to a PNG so you can EYEBALL the catalog — and diff against a saved
baseline — after editing odoo.css / a fragment, or on an Odoo version bump. The
Stage-1 lint checks references/placeholders; it is blind to *rendering* (stray
markers, z-index, broken layout). This catches those.

It stages a real package layout (assets/ + index.html) in a temp dir so the
gallery's `assets/...` paths resolve exactly as they do in a generated mock,
then drives headless Chrome.

Usage:
    python3 reference/scripts/_render_catalog.py [--out PATH] [--baseline]

    (no args)     render to /tmp/catalog_gallery/_gallery.png and print the path
    --out PATH    write the screenshot there instead
    --baseline    also copy the screenshot to reference/catalog/_gallery.png
                  (the committed baseline to diff future renders against)

Exit 0 on success, 2 if no Chrome/Chromium binary is found.
"""
import argparse
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CATALOG = os.path.normpath(os.path.join(HERE, "..", "catalog"))
ASSETS = ("odoo.css", "annotations.css", "walkthrough.js", "icons.svg")

CHROME_CANDIDATES = [
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]


def find_chrome():
    for c in CHROME_CANDIDATES:
        if os.path.isfile(c) and os.access(c, os.X_OK):
            return c
        which = shutil.which(c)
        if which:
            return which
    return None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/tmp/catalog_gallery/_gallery.png")
    ap.add_argument("--baseline", action="store_true",
                    help="also copy to reference/catalog/_gallery.png (the baseline)")
    args = ap.parse_args(argv)

    chrome = find_chrome()
    if not chrome:
        sys.stderr.write("No Chrome/Chromium found; install one or set PATH.\n")
        return 2

    # Stage a package layout so assets/... paths resolve like a real mock.
    stage = "/tmp/catalog_gallery"
    os.makedirs(os.path.join(stage, "assets"), exist_ok=True)
    for a in ASSETS:
        shutil.copyfile(os.path.join(CATALOG, a), os.path.join(stage, "assets", a))
    shutil.copyfile(os.path.join(CATALOG, "_gallery.html"),
                    os.path.join(stage, "index.html"))

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    url = "file://" + os.path.join(stage, "index.html")
    cmd = [chrome, "--headless", "--disable-gpu", "--no-sandbox",
           "--hide-scrollbars", "--window-size=1280,2400",
           "--virtual-time-budget=3000", "--screenshot=" + args.out, url]
    subprocess.run(cmd, check=False,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if not os.path.isfile(args.out):
        sys.stderr.write("Render failed — no screenshot produced.\n")
        return 2
    print("Rendered catalog gallery -> " + args.out)

    if args.baseline:
        baseline = os.path.join(CATALOG, "_gallery.png")
        shutil.copyfile(args.out, baseline)
        print("Updated baseline -> " + baseline)
    return 0


if __name__ == "__main__":
    sys.exit(main())
