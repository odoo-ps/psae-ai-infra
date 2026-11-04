#!/usr/bin/env python3
"""_render_mock_screens.py — per-screen visual review of a generated mock.

Drives walkthrough.js via its `#screen-ID` hash convention so each PNG
shows exactly one `.mock-screen` (the one the hash selected) plus the
walkthrough bar — i.e. the same composition the reader sees opening the
mock and pressing Next to that step.

Use this when the catalog has been edited (and you want to see whether
existing mocks still render correctly), or when the fidelity anchor is
clean but you suspect a visual gap the markup-level audit can't see
(stale assets, wrong grid template, drift between class names and the
CSS that styles them).

Catches things lint + anchors miss:
  - Layout / grid bugs (e.g. reversed `grid-template-columns`).
  - Stale `assets/odoo.css` that doesn't include classes the markup
    references (covered by `_lint_mock.py` STALE-ASSET now, but visual
    review confirms the fix actually rendered).
  - Cosmetic positioning (marker floats, button row alignment, sidebar
    width pressure) that lint is intentionally blind to.

Usage:
    python3 reference/scripts/_render_mock_screens.py <mocks | mocks/_reference | <name> - mock.html>
                                                      [<screen-id> ...] [--out DIR]
                                                      [--width N] [--height N]

    The mocks folder or its _reference/ renders the working package; a
    bundled `<name> - mock.html` renders the single-file deliverable.
    Default screen-ids: every `<section class="mock-screen">` declared in
    the page (cover + every workflow step).
    Default --out: /tmp/mock_renders/<mock-name>/ (package) or
    /tmp/mock_renders/<mock-name>-bundle/ (bundle), so both can be compared.
    Default --width / --height: 1440 / 900 (matches MBA / typical monitor)

Exit 0 on success, 2 if no Chrome/Chromium binary is found.
"""
import argparse
import os
import re
import subprocess
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _mock_paths  # noqa: E402

# Same lookup chain as `_render_catalog.py` — keep them in sync so a
# Chrome install that works for one works for the other.
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


def discover_screens(index_html):
    """Return list of `data-screen` IDs in document order."""
    text = open(index_html, encoding="utf-8", errors="replace").read()
    # Ignore inlined <script>/<style> and comments: a bundled single-file mock
    # carries walkthrough.js, whose comments contain example markup.
    text = re.sub(r"<(script|style)\b.*?</\1>|<!--.*?-->", "", text, flags=re.S | re.I)
    # Tolerant of extra classes on the section (`mock-screen mock-custom`).
    return re.findall(
        r'<section\b[^>]*\bclass="[^"]*\bmock-screen\b[^"]*"[^>]*\bdata-screen="([^"]+)"',
        text,
    )


def _mock_name(mock_dir):
    """Derive a short name for the output directory.

    For spec-driven mocks the structure is
    `<repo>/specifications/<TASK> - <CLIENT> - <slug>/mocks/`, and the
    interesting name is the spec folder. For specless mocks under
    `<repo>/mocks/<name>/` the name is the leaf directory.
    """
    mock_dir = _mock_paths.mocks_root(mock_dir).rstrip("/")
    parent = os.path.dirname(mock_dir)
    leaf = os.path.basename(mock_dir)
    if leaf == "mocks":
        # spec-driven: name is the parent (the spec folder)
        return os.path.basename(parent).split(" - ")[0] or "mock"
    return leaf


def render(mock_dir, screen_ids=None, out_dir=None, width=1440, height=900):
    is_bundle = os.path.isfile(mock_dir) and mock_dir.endswith(".html")
    if is_bundle:
        # A bundled single-file mock (<mocks>/<name> - mock.html).
        index, mock_dir = os.path.abspath(mock_dir), os.path.dirname(os.path.abspath(mock_dir))
    else:
        mock_dir = _mock_paths.package_dir(mock_dir)
        index = os.path.join(mock_dir, "index.html")
    if not os.path.isfile(index):
        sys.stderr.write(f"No index.html in {mock_dir}\n")
        return 2

    chrome = find_chrome()
    if not chrome:
        sys.stderr.write("No Chrome/Chromium found; install one or set PATH.\n")
        return 2

    ids = screen_ids if screen_ids else discover_screens(index)
    if not ids:
        sys.stderr.write(f"No `<section class=\"mock-screen\">` found in {index}\n")
        return 2

    if out_dir is None:
        out_dir = f"/tmp/mock_renders/{_mock_name(mock_dir)}" + ("-bundle" if is_bundle else "")
    os.makedirs(out_dir, exist_ok=True)

    base = "file://" + os.path.abspath(index)
    print(f"Rendering {len(ids)} screen(s) -> {out_dir}/")
    for sid in ids:
        url = f"{base}#{sid}"
        out_png = os.path.join(out_dir, f"{sid}.png")
        cmd = [chrome, "--headless", "--disable-gpu", "--no-sandbox",
               "--hide-scrollbars",
               f"--window-size={width},{height}",
               # Give walkthrough.js time to swap to the hash screen +
               # resolve variant axes + position markers AND let the
               # screen fade-in finish (2s often caught it washed-out).
               "--virtual-time-budget=6000",
               f"--screenshot={out_png}", url]
        subprocess.run(cmd, check=False,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.isfile(out_png):
            kb = os.path.getsize(out_png) // 1024
            print(f"  {sid:24s} -> {out_png}  ({kb} KB)")
        else:
            print(f"  {sid:24s} -> FAILED")

    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("mock_dir", help="the mocks folder, its _reference/ package, or a bundled '<name> - mock.html'")
    ap.add_argument("screen_ids", nargs="*", help="optional: render only these data-screen IDs")
    ap.add_argument("--out", default=None, help="output directory (default: /tmp/mock_renders/<mock-name>/, "
                    "or <mock-name>-bundle/ for a bundled file)")
    ap.add_argument("--width", type=int, default=1440)
    ap.add_argument("--height", type=int, default=900)
    args = ap.parse_args(argv)
    return render(
        args.mock_dir,
        screen_ids=args.screen_ids or None,
        out_dir=args.out,
        width=args.width,
        height=args.height,
    )


if __name__ == "__main__":
    sys.exit(main())
