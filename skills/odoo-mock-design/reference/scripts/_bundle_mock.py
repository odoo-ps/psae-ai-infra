#!/usr/bin/env python3
"""_bundle_mock.py — consolidate a mock's working package into ONE html file.

The skill builds and checks a mock as a multi-file package in
`<mocks>/_reference/` (index.html + assets/). Once the final checks pass, this
script inlines everything into the deliverable `<mocks>/<name> - mock.html`:

  * linked stylesheets (assets/*.css)   → <style data-asset="assets/…">
  * script files       (assets/*.js)    → <script data-asset="assets/…">
  * local images (img/src, favicon href, CSS url()) → data: URIs

Refs may be written `assets/…` or `./assets/…`. It first runs the Stage-1 lint
on the package and refuses to bundle a package that fails it (bundling is the
LAST step — fix the package, then re-bundle). After inlining it re-scans the
result with the lint's reference rules (HTML src/href/… attributes, CSS url()
and @import) and refuses to write the file if ANY reference is left that is not
data:, a #fragment, mailto:, tel: or javascript: — so the bundle references
nothing outside itself (a link to README.md or another local page fails).

A legacy flat package (index.html + assets/ directly in <mocks>/, no
_reference/) is refused: move index.html, assets/ and README.md into
<mocks>/_reference/ first, then bundle.

Usage:
    python3 reference/scripts/_bundle_mock.py <mocks-dir | _reference-dir> [--out FILE]
                                                [--steps "Screen title" ...]

    --steps   forwarded to the lint (same meaning as _lint_mock.py --steps)
    --out     override the output path (default: see _mock_paths.bundle_path)

Exit 0 = bundle written; 1 = legacy layout, lint failed, or the bundle would
not be self-contained (nothing is written). Stdlib only.
"""
import argparse
import base64
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lint_mock  # noqa: E402
import _mock_paths  # noqa: E402

MIME = {".png": "image/png", ".svg": "image/svg+xml", ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg", ".webp": "image/webp", ".gif": "image/gif",
        ".ico": "image/x-icon"}

# Comments and <script>/<style> elements are opaque to the markup rewrites.
_SEG_RE = re.compile(r"<!--.*?-->|<script\b[^>]*>.*?</script\s*>|<style\b[^>]*>.*?</style\s*>",
                     re.S | re.I)
# Reference attributes on markup. `data` matches only `data=` (e.g. <object>),
# never `data-*` (which has `-`, not `=`/space, after "data"); the lookbehind
# also blocks `metadata=`. Kept in sync with _lint_mock.py `_URL_ATTRS`.
_ATTR_RE = re.compile(r"""(?<![\w:-])((?:xlink:)?href|src|poster|data)\s*=\s*(["'])(.*?)\2""", re.S | re.I)
_STYLE_ATTR_RE = re.compile(r"""(?<![\w:-])(style\s*=\s*)(["'])(.*?)\2""", re.S | re.I)
_CSS_URL_SUB_RE = re.compile(r"""url\(\s*(['"]?)([^'")]+)\1\s*\)""", re.I)


def _segments(html):
    """[(kind, text)] in document order; kind: markup | comment | script | style."""
    out, pos = [], 0
    for m in _SEG_RE.finditer(html):
        if m.start() > pos:
            out.append(("markup", html[pos:m.start()]))
        t = m.group(0)
        kind = "comment" if t.startswith("<!--") else "script" if t[1:7].lower() == "script" else "style"
        out.append((kind, t))
        pos = m.end()
    if pos < len(html):
        out.append(("markup", html[pos:]))
    return out


def _attr(tag, name):
    m = re.search(r"""(?<![\w:-])%s\s*=\s*(["'])(.*?)\1""" % re.escape(name), tag, re.S | re.I)
    return m.group(2) if m else None


def _rel(ref):
    """Package-relative spelling of a ref, without a leading './'."""
    ref = ref.strip()
    return ref[2:] if ref.startswith("./") else ref


def _local(ref, base):
    """Absolute path a package-local ref points at; None for inline/external refs."""
    ref = ref.strip()
    if _lint_mock._is_inline_ok(ref) or _lint_mock._is_external(ref):
        return None
    path = re.split(r"[?#]", ref, 1)[0]
    return os.path.normpath(os.path.join(base, path)) if path else None


def leftover_refs(html):
    """Every reference in `html` that would load something from outside the file."""
    left = []
    collector = _lint_mock._RefCollector()
    collector.feed(html)
    collector.close()
    left += [ref for _attr_name, ref in collector.refs if not _lint_mock._is_inline_ok(ref)]
    css = []
    for kind, text in _segments(html):
        if kind == "style":
            css.append(text)
        elif kind == "markup":
            css += [m.group(3) for m in _STYLE_ATTR_RE.finditer(text)]
    for text in css:
        for ref in _lint_mock._CSS_URL_RE.findall(text) + _lint_mock._CSS_IMPORT_RE.findall(text):
            if not _lint_mock._is_inline_ok(ref):
                left.append(ref.strip())
    return sorted(set(left))


def bundle(pkg, out):
    with open(os.path.join(pkg, "index.html"), encoding="utf-8") as fh:
        html = fh.read()
    cache = {}

    def data_uri(path):
        """data: URI for a local image; None if it is missing or not an image
        (the final check then reports the ref)."""
        if path not in cache:
            mime = MIME.get(os.path.splitext(path)[1].lower())
            if not mime or not os.path.isfile(path):
                cache[path] = None
            else:
                with open(path, "rb") as fh:
                    cache[path] = f"data:{mime};base64," + base64.b64encode(fh.read()).decode()
        return cache[path]

    def css_urls(css, base, q='"'):
        def sub(m):
            p = _local(m.group(2), base)
            uri = p and data_uri(p)
            return f"url({q}{uri}{q})" if uri else m.group(0)
        return _CSS_URL_SUB_RE.sub(sub, css)

    def style_attr_sub(m):
        # url() inside style="…": quote the data: URI with the other quote char.
        q = "'" if m.group(2) == '"' else '"'
        return f"{m.group(1)}{m.group(2)}{css_urls(m.group(3), pkg, q)}{m.group(2)}"

    def read_asset(ref, what):
        p = _local(ref, pkg)
        if not p or not os.path.isfile(p):
            raise SystemExit(f"FAIL — missing {what}: {ref}")
        with open(p, encoding="utf-8") as fh:
            return p, fh.read()

    def attr_sub(m):
        p = _local(m.group(3), pkg)
        uri = p and data_uri(p)
        return f"{m.group(1)}={m.group(2)}{uri}{m.group(2)}" if uri else m.group(0)

    def link_sub(m):
        tag = m.group(0)
        href = _attr(tag, "href") or ""
        if "stylesheet" not in (_attr(tag, "rel") or "").lower().split() or not _local(href, pkg):
            return tag
        p, css = read_asset(href, "stylesheet")
        if "</style" in css.lower():
            raise SystemExit(f"FAIL — {_rel(href)} contains '</style'; cannot inline safely")
        return f'<style data-asset="{_rel(href)}">\n{css_urls(css, os.path.dirname(p))}\n</style>'

    parts = []
    for kind, text in _segments(html):
        if kind == "markup":
            text = _ATTR_RE.sub(attr_sub, text)          # images → data: URIs
            text = _STYLE_ATTR_RE.sub(style_attr_sub, text)
            text = re.sub(r"<link\b[^>]*>", link_sub, text, flags=re.I)  # stylesheets → <style>
        elif kind == "script":
            m = re.match(r"<script\b([^>]*)>\s*</script\s*>\Z", text, re.I)
            src = _attr(m.group(1), "src") if m else None
            if src and _local(src, pkg):
                _p, js = read_asset(src, "script")
                js = js.replace("</script", "<\\/script")
                text = f'<script data-asset="{_rel(src)}">\n{js}\n</script>'
        elif kind == "style":
            text = css_urls(text, pkg)
        parts.append(text)
    html = "".join(parts)

    left = leftover_refs(html)
    if left:
        raise SystemExit("FAIL — bundle would not be self-contained; these references would "
                         f"load from outside the single file: {left[:10]}. Keep images inside the "
                         "package (they are inlined as data: URIs), move other content into "
                         "index.html, or drop the reference; then re-bundle.")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(html)
    return len(html.encode())


def main(argv=None):
    ap = argparse.ArgumentParser(description="Bundle a mock's _reference/ package into one html file.")
    ap.add_argument("path", help="the mocks folder or its _reference/ working package")
    ap.add_argument("--out", default=None)
    ap.add_argument("--steps", nargs="*", default=None)
    a = ap.parse_args(argv)

    pkg = _mock_paths.package_dir(a.path)
    if not os.path.isfile(os.path.join(pkg, "index.html")):
        print(f"FAIL — no index.html in {pkg}", file=sys.stderr)
        return 1
    if os.path.basename(pkg) != _mock_paths.REF:
        print(f"FAIL — {pkg} is a legacy flat package (no {_mock_paths.REF}/). Migrate it first: "
              f"move index.html, assets/ and README.md into {os.path.join(pkg, _mock_paths.REF)}/, "
              f"then re-run on {pkg}.", file=sys.stderr)
        return 1
    findings = _lint_mock.lint(pkg, steps=a.steps)
    if findings:
        print(f"FAIL — lint reports {len(findings)} finding(s) in {pkg}; fix them, then bundle:")
        for kind, where, msg in findings[:20]:
            print(f"  [{kind}] {where}: {msg}")
        return 1
    out = a.out or _mock_paths.bundle_path(pkg)
    size = bundle(pkg, out)
    print(f"PASS — bundled {pkg}/ → {out} ({size // 1024} KB, self-contained)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
