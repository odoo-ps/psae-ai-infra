#!/usr/bin/env python3
"""_lint_mock.py — Stage-1 lint for an odoo-mock-design package.

Mechanically enforces the two promises the skill makes:
  1. SELF-CONTAINED: no external network references, and every local reference
     resolves to a file *inside the package root* (nothing escapes into the
     skill folder, an absolute path, or a parent dir).
  2. COMPLETE: no placeholder strings, and (optionally) every workflow step from
     the source brief has a screen.

Usage:
    python3 _lint_mock.py <mocks-dir | _reference-dir> [--steps "Step A" "Step B" ...]

    Either path resolves (via _mock_paths.py) to the working package
    `<mocks>/_reference/` — or to `<mocks>/` itself for a legacy flat package.
    The lint checks the package, never the bundled `<name> - mock.html`.

Advisory `NOTE:` lines never fail the run: the cover's "Odoo NN" differs from
the assets/odoo.css stamp, or the single-file bundle is missing / older than
the package's index.html + assets/ (re-bundle with _bundle_mock.py).

Exit code 0 = pass, 1 = findings (printed), 2 = bad invocation.
No third-party dependencies (stdlib regex/html parsing only).
"""
import argparse
import html
import json
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _mock_paths  # noqa: E402
from html.parser import HTMLParser

# Reference-bearing attributes we check across the package's HTML/CSS.
_URL_ATTRS = ("src", "href", "data", "poster")
_EXTERNAL_RE = re.compile(r"""^\s*(?:https?:)?//|^\s*https?:|^\s*ftp:""", re.I)
_DATA_OR_FRAGMENT_RE = re.compile(r"""^\s*(?:data:|mailto:|tel:|#|javascript:)""", re.I)
_CSS_URL_RE = re.compile(r"""url\(\s*['"]?([^'")]+)['"]?\s*\)""", re.I)
_CSS_IMPORT_RE = re.compile(r"""@import\s+(?:url\()?\s*['"]?([^'")\s;]+)""", re.I)
_PLACEHOLDERS = ("lorem ipsum", "todo", "tbd", "fixme", "xxx", "placeholder text")


class _RefCollector(HTMLParser):
    """Collects (attr, value) reference pairs from an HTML file."""

    def __init__(self):
        super().__init__()
        self.refs = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if value is None:
                continue
            # SVG <use href="..."> and xlink:href both matter.
            if name in _URL_ATTRS or name.endswith(":href"):
                self.refs.append((name, value.strip()))


class _CustomScan(HTMLParser):
    """Walks index.html with an element stack to check custom marking.

    `.mock-custom` flags what the solution adds or changes (interactions.md
    § Custom elements): on a `.mock-screen` the whole screen is custom (the
    corner banner), on an element that element is (the pink highlight). A
    field carrying the "?" is solution-added by the same definition, so it
    must sit inside a custom element or on a custom screen.
    """

    _VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
             "link", "meta", "param", "source", "track", "wbr"}
    _TABLE_PARTS = {"table", "thead", "tbody", "tfoot", "tr", "colgroup"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []       # [(tag, is_custom_element)]
        self.screen = None    # (sid, framing, custom) of the open .mock-screen
        self.findings = []
        self.unmarked = {}    # sid -> [labels of "?" fields outside any custom mark]

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = (a.get("class") or "").split()
        if tag == "section" and "mock-screen" in classes:
            sid = a.get("data-screen", "(unnamed)")
            framing = sid == "cover" or a.get("data-screen-kind") == "workflow-overview"
            custom = "mock-custom" in classes
            self.screen = (sid, framing, custom)
            if framing and custom:
                self._add("CUSTOM-PLACEMENT", "the cover and workflow overviews explain the mock — "
                          "they are never solution scope; drop `mock-custom` from the screen")
            if tag not in self._VOID:
                self.stack.append((tag, False))
            return
        custom_el = "mock-custom" in classes and "mock-custom-example" not in classes
        if self.screen:
            sid, framing, screen_custom = self.screen
            inside_custom = any(c for _t, c in self.stack)
            if custom_el:
                if framing:
                    self._add("CUSTOM-PLACEMENT", "`mock-custom` on the cover / a workflow overview — those "
                              "screens explain the mock; only the callout examples (`mock-custom-example`) belong there")
                elif screen_custom:
                    self._add("CUSTOM-PLACEMENT", "element marked `mock-custom` on a screen that is already "
                              "custom as a whole (the corner banner says it) — drop the element mark")
                elif inside_custom:
                    self._add("CUSTOM-PLACEMENT", "`mock-custom` inside another `mock-custom` element — mark "
                              "only the outermost element that is entirely custom")
                if tag in self._TABLE_PARTS or tag in self._VOID:
                    self._add("CUSTOM-PLACEMENT", f"`mock-custom` on a <{tag}> — the highlight overlay cannot "
                              f"sit inside it; mark the cells (`<th>` / `<td>`) or the element's container")
            if "o_field_help" in classes and not framing and not screen_custom and not inside_custom \
                    and not custom_el:
                label = a.get("data-label") or a.get("data-field") or "?"
                self.unmarked.setdefault(sid, []).append(label)
        if tag not in self._VOID:
            self.stack.append((tag, custom_el))

    def handle_endtag(self, tag):
        for k in range(len(self.stack) - 1, -1, -1):
            if self.stack[k][0] == tag:
                del self.stack[k:]
                break
        if tag == "section" and not any(t == "section" for t, _c in self.stack):
            self.screen = None

    def _add(self, code, msg):
        self.findings.append((code, f"index.html#{self.screen[0] if self.screen else '?'}", msg))

    def results(self):
        out = list(self.findings)
        for sid, labels in self.unmarked.items():
            names = list(dict.fromkeys(labels))
            out.append(("CUSTOM-UNMARKED", f"index.html#{sid}",
                        f'{len(names)} field(s) carry the "?" (solution-added) but are not marked custom: '
                        f'{", ".join(names)}. Add `mock-custom` to each field\'s row / column cells / '
                        f'settings box, or to the `.mock-screen` when the whole screen is custom '
                        f'(interactions.md § Custom elements).'))
        return out


def _is_external(ref):
    return bool(_EXTERNAL_RE.match(ref))


def _is_inline_ok(ref):
    """data:/mailto:/tel:/#fragment/javascript: are not file references."""
    return bool(_DATA_OR_FRAGMENT_RE.match(ref)) or ref == ""


def _resolves_inside(package_dir, source_file, ref):
    """True if a local ref resolves to an existing file inside package_dir."""
    # Strip any #fragment / ?query.
    path = re.split(r"[?#]", ref, 1)[0]
    if not path:
        return True
    if os.path.isabs(path):
        return False  # absolute paths escape portability
    base = os.path.dirname(source_file)
    target = os.path.normpath(os.path.join(base, path))
    pkg = os.path.normpath(package_dir)
    # Must stay within the package root AND exist.
    inside = target == pkg or target.startswith(pkg + os.sep)
    return inside and os.path.exists(target)


def _iter_files(package_dir, exts):
    for root, _dirs, files in os.walk(package_dir):
        for fn in files:
            if os.path.splitext(fn)[1].lower() in exts:
                yield os.path.join(root, fn)


def _blank_comments(s):
    """Return `s` with every HTML comment replaced by equal-length spaces.

    Length is preserved so byte offsets stay valid — the `<div>`/`</div>`
    depth balancers search this copy (a `<div` inside a comment must not
    count toward nesting depth) while still slicing bodies by offset from
    the original text.
    """
    return re.sub(r"<!--.*?-->", lambda m: " " * len(m.group(0)), s, flags=re.DOTALL)


def _screen_segments(index_text):
    """Yield (sid, open_tag, body) for each `.mock-screen` <section>.

    Segments at screen OPENERS (opener -> next opener), never at `</section>`,
    so a nested <section> inside a screen (website_form, portal, dashboard
    sidebar, search_panel, login_website, …) does not truncate the body. Class
    matching is tolerant of extra classes on the section (`mock-screen o_cover`).
    """
    opens = list(re.finditer(
        r'<section[^>]*\bclass="[^"]*\bmock-screen\b[^"]*"[^>]*>',
        index_text, re.I))
    segs = []
    for k, m in enumerate(opens):
        end = opens[k + 1].start() if k + 1 < len(opens) else len(index_text)
        open_tag = m.group(0)
        sid_m = re.search(r'data-screen="([^"]*)"', open_tag)
        sid = sid_m.group(1) if sid_m else "(unnamed)"
        segs.append((sid, open_tag, index_text[m.end():end]))
    return segs


def _catalog_class_tokens():
    """Every class token used in the catalog component fragments.

    CLASS-UNKNOWN credits these in addition to CSS-defined classes: a class
    that appears in a shipped `components/*.html` fragment IS, by definition,
    legitimate catalog vocabulary even when the catalog styles it only via a
    child/descendant selector (e.g. the `o-mail-ActivityList` container whose
    CSS lives under `.o-mail-ActivityList-header`). This is what keeps the rule
    from false-failing a mock composed verbatim from the catalog, while still
    catching genuinely invented classes (absent from both CSS and fragments).
    """
    tokens = set()
    components = os.path.normpath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "catalog", "components"))
    if not os.path.isdir(components):
        return tokens
    for f in _iter_files(components, {".html", ".htm"}):
        try:
            with open(f, encoding="utf-8", errors="replace") as fh:
                frag = fh.read()
        except OSError:
            continue
        for m in re.finditer(r'\bclass=(["\'])([^"\']*)\1', frag):
            tokens.update(m.group(2).split())
    return tokens


def lint(package_dir, steps=None):
    package_dir = _mock_paths.package_dir(package_dir)
    findings = []
    if not os.path.isdir(package_dir):
        return [("FATAL", package_dir, "package directory does not exist")]
    # Normalize to an absolute path so the inside-the-package check works
    # regardless of how the dir was passed (e.g. "." from inside the package
    # used to mis-resolve every ./assets ref as an ESCAPE).
    package_dir = os.path.abspath(package_dir)

    index = os.path.join(package_dir, "index.html")
    if not os.path.isfile(index):
        findings.append(("STRUCTURE", package_dir, "no index.html at package root"))

    all_text = []  # (file, text) for placeholder + coverage scan

    # ---- HTML files: reference checks -----------------------------------
    for f in _iter_files(package_dir, {".html", ".htm"}):
        rel = os.path.relpath(f, package_dir)
        with open(f, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        all_text.append((rel, text))
        parser = _RefCollector()
        parser.feed(text)
        for attr, ref in parser.refs:
            if _is_inline_ok(ref):
                continue
            if _is_external(ref):
                findings.append(("EXTERNAL", rel, f'{attr}="{ref}" is an external/network reference'))
            elif re.search(r"\.svg#", ref, re.I):
                # External SVG <use href="file.svg#id"> is blocked over file://
                # (opaque origin) — icons silently vanish. Inline the sprite and
                # use same-document #id refs instead.
                findings.append(("SVG-USE", rel,
                    f'{attr}="{ref}" links an external SVG sprite — inline the sprite '
                    f'and use same-document "#id" refs (external <use> fails over file://)'))
            elif not _resolves_inside(package_dir, f, ref):
                findings.append(("ESCAPE", rel, f'{attr}="{ref}" does not resolve to a file inside the package'))
        # Same-document icon refs: every <use href="#x"> must resolve to an
        # id="x" in this page (the inlined icons.svg + app-icons.svg sprites).
        # An unresolved ref renders as a blank icon with no error anywhere.
        # Comments are ignored on both sides (fragment comments carry examples).
        live = re.sub(r"<!--[\s\S]*?-->", "", text)
        ids = set(re.findall(r'\bid=["\']([^"\']+)["\']', live))
        missing = []
        for m in re.finditer(r'<use\b[^>]*?\b(?:xlink:)?href=["\']#([^"\']+)["\']', live):
            if m.group(1) not in ids and m.group(1) not in missing:
                missing.append(m.group(1))
        for sym in missing:
            findings.append(("UNRESOLVED-USE", rel,
                f'<use href="#{sym}"> has no matching id="{sym}" in the page — the icon '
                f'renders blank. Inline BOTH catalog sprites (icons.svg + app-icons.svg) '
                f'and use an id that exists there (catalog `_gallery.html` § Icons lists them).'))

    # ---- Asset freshness — every `assets/<x>` must match catalog ----------
    # FINDINGS#26: stale catalog assets. When the catalog (`reference/catalog/`
    # odoo.css / annotations.css / walkthrough.js / icons.svg etc.) is updated
    # but the mock's `assets/` copies aren't re-copied, the mock renders with
    # the OLD chrome — silently. Lint catches the drift by SHA-256 diffing
    # each asset against its catalog source; mismatches are blockers because
    # the rendered mock no longer matches what `_render_mock_screens.py` or
    # a stakeholder would see if they opened the file.
    #
    # The catalog source lives at `<this-file>/../../catalog/<asset>`. Only
    # files the catalog actually ships are checked — mocks may carry extra
    # assets (e.g. project-specific images) that aren't in the catalog, and
    # those are NOT flagged.
    import hashlib
    catalog_dir = os.path.normpath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "catalog"))
    assets_dir = os.path.join(package_dir, "assets")
    if os.path.isdir(assets_dir):
        for asset_name in os.listdir(assets_dir):
            catalog_src = os.path.join(catalog_dir, asset_name)
            mock_copy = os.path.join(assets_dir, asset_name)
            if not os.path.isfile(catalog_src) or not os.path.isfile(mock_copy):
                continue
            def _sha(path):
                with open(path, "rb") as fh:
                    return hashlib.sha256(fh.read()).hexdigest()
            if _sha(catalog_src) != _sha(mock_copy):
                findings.append(("STALE-ASSET", f"assets/{asset_name}",
                    f'differs from `reference/catalog/{asset_name}` — the '
                    f'catalog was updated after this mock was generated. '
                    f'Run `python3 skills/odoo-mock-design/reference/scripts/'
                    f'_refresh_assets.py <package-dir>` to refresh '
                    f'(idempotent; never touches `index.html`).'))

    # ---- CSS files: url() and @import checks ----------------------------
    for f in _iter_files(package_dir, {".css"}):
        rel = os.path.relpath(f, package_dir)
        with open(f, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        all_text.append((rel, text))
        for ref in _CSS_URL_RE.findall(text) + _CSS_IMPORT_RE.findall(text):
            if _is_inline_ok(ref):
                continue
            if _is_external(ref):
                findings.append(("EXTERNAL", rel, f"url()/@import to external resource: {ref}"))
            elif not _resolves_inside(package_dir, f, ref):
                findings.append(("ESCAPE", rel, f"url()/@import does not resolve inside the package: {ref}"))

    # JS files contribute to placeholder scan only.
    for f in _iter_files(package_dir, {".js"}):
        rel = os.path.relpath(f, package_dir)
        with open(f, encoding="utf-8", errors="replace") as fh:
            all_text.append((rel, fh.read()))

    # ---- Placeholder strings --------------------------------------------
    for rel, text in all_text:
        if rel.lower().endswith((".html", ".htm")):
            # Inlined sprites are catalog artwork, not author copy (the real
            # `o-app-todo` app icon would read as "todo"): skip each <symbol>,
            # the glyph comment right before it, and same-document #id refs.
            text = re.sub(r"<!--(?:(?!-->)[\s\S])*-->(?=\s*<symbol\b)", "", text)
            text = re.sub(r"<symbol\b[\s\S]*?</symbol>", "", text)
            text = re.sub(r'\bhref=["\']#[^"\']*["\']', "", text)
        low = text.lower()
        for ph in _PLACEHOLDERS:
            # Word-ish boundary so "todol" / CSS classes don't false-positive.
            if re.search(r"(?<![a-z])" + re.escape(ph) + r"(?![a-z])", low):
                findings.append(("PLACEHOLDER", rel, f'contains placeholder string "{ph}"'))

    # ---- Workflow-step coverage (optional) ------------------------------
    if steps:
        index_text = ""
        for rel, text in all_text:
            if rel == "index.html":
                index_text = text
                break
        # FINDINGS#1: HTML-decode data-title before string-compare so a screen
        # title like `data-title="P&amp;L Report"` matches `--steps "P&L Report"`.
        # Without unescape() the lint would falsely flag the screen as missing.
        titles_raw = re.findall(r'data-title="([^"]*)"', index_text)
        titles = [html.unescape(t) for t in titles_raw]
        titles_low = [t.strip().lower() for t in titles]
        for step in steps:
            s = html.unescape(step).strip().lower()
            if not any(s in t or t in s for t in titles_low if t):
                findings.append(("COVERAGE", "index.html", f'no screen found for workflow step: "{step}"'))

    # ---- Variant chip-row hygiene + multi-workflow hygiene --------------
    # Mechanical attribute checks (anchors do the semantic pass).
    index_text = ""
    for rel, text in all_text:
        if rel == "index.html":
            index_text = text
            break
    # Comment-blanked copy (length-preserved) for the <div>-depth balancers —
    # a `<div` inside an HTML comment must not count toward nesting depth.
    index_text_nc = _blank_comments(index_text)

    if index_text:
        # Variant axes — every screen with data-mock-variant-axes JSON must:
        #   (a) parse as valid JSON array
        #   (b) each axis has key + options of >= 2 entries
        #   (c) each axis's default is in its options list
        #   (d) every data-mock-variant on a child references a declared axis
        #       and (warn-level) a value in that axis's options
        import json
        for sid, section_open, section_body in _screen_segments(index_text):
            axes_m = re.search(
                r"""data-mock-variant-axes=(?P<q>['"])(?P<body>.*?)(?P=q)""",
                section_open, re.DOTALL,
            )
            if not axes_m:
                continue
            raw = axes_m.group("body")
            # Tolerate single quotes around JSON since HTML attributes accept either.
            try:
                axes = json.loads(raw)
            except Exception:
                findings.append(("VARIANT", f"index.html#{sid}",
                    "data-mock-variant-axes is not valid JSON"))
                continue
            if not isinstance(axes, list) or not axes:
                findings.append(("VARIANT", f"index.html#{sid}",
                    "data-mock-variant-axes is empty or not an array"))
                continue
            axis_keys = set()
            axis_options = {}
            for axis in axes:
                if not isinstance(axis, dict) or "key" not in axis:
                    findings.append(("VARIANT", f"index.html#{sid}",
                        "an axis entry has no 'key'"))
                    continue
                key = axis["key"]
                opts = axis.get("options", [])
                opt_keys = [pair[0] for pair in opts if isinstance(pair, (list, tuple)) and len(pair) == 2]
                axis_keys.add(key)
                axis_options[key] = opt_keys
                if len(opt_keys) < 2:
                    findings.append(("VARIANT", f"index.html#{sid}",
                        f"axis '{key}' has < 2 options"))
                if "default" in axis and axis["default"] not in opt_keys:
                    findings.append(("VARIANT", f"index.html#{sid}",
                        f"axis '{key}' default '{axis['default']}' is not in its options"))
            if len(axes) > 4:
                findings.append(("VARIANT", f"index.html#{sid}",
                    f"{len(axes)} axes on one screen (> 4) — consider splitting"))
            # Children carrying data-mock-variant
            child_variants = re.findall(r'data-mock-variant="([^"]+)"', section_body)
            if not child_variants:
                findings.append(("VARIANT", f"index.html#{sid}",
                    "axes declared but no child carries data-mock-variant"))
            for spec in child_variants:
                for pair in spec.split(","):
                    bits = pair.strip().split("=")
                    if len(bits) != 2:
                        findings.append(("VARIANT", f"index.html#{sid}",
                            f"malformed data-mock-variant='{spec}' (expected axis=value)"))
                        continue
                    axis_k = bits[0].strip()
                    # Same-axis OR via `|`: validate each value separately.
                    value_ks = [v.strip() for v in bits[1].split("|") if v.strip()]
                    if axis_k not in axis_keys:
                        findings.append(("VARIANT", f"index.html#{sid}",
                            f"data-mock-variant='{spec}' references axis '{axis_k}' not declared on the screen"))
                        continue
                    options = axis_options.get(axis_k, [])
                    for value_k in value_ks:
                        if value_k not in options:
                            findings.append(("VARIANT", f"index.html#{sid}",
                                f"data-mock-variant='{spec}' references value '{value_k}' not in axis '{axis_k}'"))

        # Multi-workflow shell — when >= 2 .mock-workflow wrappers exist:
        #   (a) every wrapper must have data-workflow + data-workflow-title
        #   (b) data-screen IDs must be globally unique across the document
        #   (c) no .mock-screen may sit outside a .mock-workflow wrapper
        wf_wraps = re.findall(
            r'<div[^>]*\bclass="[^"]*\bmock-workflow\b[^"]*"[^>]*>',
            index_text, re.I,
        )
        if len(wf_wraps) >= 2:
            for w in wf_wraps:
                if 'data-workflow=' not in w:
                    findings.append(("WORKFLOW", "index.html",
                        ".mock-workflow wrapper missing data-workflow slug"))
                if 'data-workflow-title=' not in w:
                    findings.append(("WORKFLOW", "index.html",
                        ".mock-workflow wrapper missing data-workflow-title label"))
            # Duplicate screen IDs.
            sids = re.findall(r'data-screen="([^"]*)"', index_text)
            seen = set()
            for sid in sids:
                if sid in seen:
                    findings.append(("WORKFLOW", "index.html",
                        f'duplicate data-screen="{sid}" across workflows'))
                seen.add(sid)
            # Orphan screens — any .mock-screen outside any .mock-workflow.
            # Heuristic: count screens vs sum across wrappers.
            total_screens = len(re.findall(r'<section[^>]*\bmock-screen\b', index_text))
            inside = 0
            for m in re.finditer(
                r'<div[^>]*\bmock-workflow\b[^>]*>(.*?)(?=<div[^>]*\bmock-workflow\b|</body>)',
                index_text, re.DOTALL | re.I,
            ):
                inside += len(re.findall(r'<section[^>]*\bmock-screen\b', m.group(1)))
            if total_screens > inside:
                findings.append(("WORKFLOW", "index.html",
                    f'{total_screens - inside} .mock-screen(s) outside any .mock-workflow wrapper (orphan)'))

        # Input-pending must be wired — class="...o_input_pending..." element
        # MUST also carry one of data-mock-toggle / data-mock-modal-open /
        # data-mock-goto. Painted-but-dead affordances are blockers.
        for tag_m in re.finditer(
            r'<[a-zA-Z][a-zA-Z0-9]*\b[^>]*\bclass="[^"]*\bo_input_pending\b[^"]*"[^>]*>',
            index_text,
        ):
            tag = tag_m.group(0)
            if not re.search(r'data-mock-(toggle|modal-open|goto)\b', tag):
                # Snip a short slug for location-friendly output.
                slug = re.search(r'(?:data-screen|class)="([^"]{0,40})"', tag)
                where = slug.group(1) if slug else "(near o_input_pending)"
                findings.append(("INPUT-PENDING", f"index.html#{where}",
                    "o_input_pending element has no data-mock-toggle / -modal-open / -goto wiring"))

        # FINDINGS#13: cover step-axes chips reference a screen by id via
        # data-mock-page-ref="<screen-id>". A typo silently degrades to
        # "Page ?" — catch the dangling ref at lint time.
        all_screen_ids = set(re.findall(r'data-screen="([^"]*)"', index_text))
        for m in re.finditer(r'data-mock-page-ref="([^"]+)"', index_text):
            ref = m.group(1)
            if ref not in all_screen_ids:
                findings.append(("PAGE-REF", "index.html",
                    f'data-mock-page-ref="{ref}" does not match any data-screen on the page'))

        # FINDINGS#14: the cover's workflow narrative uses
        # .mock-step-list-wrap (CSS subgrid container) around the
        # <ol class="mock-step-list">. Without the wrap, subgrid resolves to
        # a single column and the chip alignment collapses. Flag bare
        # .mock-step-list that sits outside .mock-step-list-wrap.
        wrap_blocks = re.findall(
            r'<[^>]*\bclass="[^"]*\bmock-step-list-wrap\b[^"]*"[^>]*>([\s\S]*?)</',
            index_text,
        )
        wrapped_listings = sum(len(re.findall(r'\bmock-step-list\b', w)) for w in wrap_blocks)
        total_listings = len(re.findall(
            r'<ol[^>]*\bclass="[^"]*\bmock-step-list\b[^"]*"', index_text,
        ))
        if total_listings > wrapped_listings:
            findings.append(("COVER-SUBGRID", "index.html",
                f'{total_listings - wrapped_listings} .mock-step-list(s) outside .mock-step-list-wrap '
                '(subgrid alignment will collapse — wrap them in a <div class="mock-step-list-wrap">)'))

        # FINDINGS#15: known-bad string patterns observed in prior generation
        # runs. These match documented anti-patterns (reference/cover_discipline.md
        # / reference/catalog_chrome.md § Settings / reference/templates/
        # cover_callouts.html) and are cheap to catch at lint time so the
        # anchor pass fires on substantive findings.
        # Each entry: (regex, code, hint). Add new known-bad patterns here
        # ONLY after observing them in a generated mock (or retiring them from
        # the catalog in a recalibration) and confirming the canonical
        # replacement. A pattern must not match any current catalog fragment.
        _KNOWN_BAD = [
            (r'\bmock-cover-body\b', "KNOWN-BAD",
             '`mock-cover-body` has no CSS rule — rename to `mock-cover-section` '
             '(reference/cover_discipline.md § 3 How to interact with this mock)'),
            (r'\bo_setting_searchbar\b', "KNOWN-BAD",
             '`o_setting_searchbar` is invented — use `o_cp_searchview` inside '
             '`.o_control_panel` (reference/catalog_chrome.md § Settings; catalog '
             '`components/settings.html`)'),
            (r'<table[^>]*\bclass="[^"]*\bo_list_view\b[^"]*"', "KNOWN-BAD",
             '`o_list_view` is the WRAPPER div class — put it on a `<div>`, then '
             'the table inside uses `class="o_list_table o_list_table_ungrouped"` '
             '(catalog `components/list_view.html`)'),
            # FINDINGS#23: website-form class drift. `o_website_form` is the
            # invented variant — the catalog snippet class is `s_website_form_rows`
            # (with the `s_` snippet prefix). `o_website_page` / `o_website_container`
            # are invented wrappers; `.s_website_form` already centres + caps width.
            (r'<form[^>]*\bclass="[^"]*\bo_website_form\b', "KNOWN-BAD",
             '`o_website_form` is invented (missing the `s_` snippet prefix) — use '
             '`<form class="s_website_form_rows">` per catalog `components/website_form.html`'),
            (r'\bclass="[^"]*\b(?:o_website_page|o_website_container)\b', "KNOWN-BAD",
             '`o_website_page` / `o_website_container` are invented wrappers — '
             '`.s_website_form` already centres + caps the width; drop the wrapper '
             'and place `<section class="s_website_form">` directly inside `.o_website`'),
            # Cover callout wording drift. Canonical is "Interactive mock."
            # (reference/templates/cover_callouts.html). The pre-template
            # wording was "Interactive walkthrough." — flag the old string so
            # legacy mocks get caught at lint time.
            (r'>\s*Interactive walkthrough\.?\s*<', "KNOWN-BAD",
             '`Interactive walkthrough` is the pre-template cover-callout wording — '
             'canonical is `Interactive mock.` Copy verbatim from '
             '`reference/templates/cover_callouts.html` (SINGLE SOURCE OF TRUTH).'),
            # Visual-audit pass (2026-06-15) found these classes invented in
            # 4 mocks with 0 odoo.css rules each — they render unstyled.
            # Authors reach for these intuitive names instead of the catalog
            # equivalents. Each row maps the invented class to the catalog's
            # actual class name verbatim from `catalog/components/<file>.html`.
            (r'\bclass="[^"]*\b(?:o_website_brand|o_website_nav|o_website_action|o_website_actions|o_website_header[^_]|o_website_link)\b',
             "KNOWN-BAD",
             '`o_website_brand` / `o_website_nav` / `o_website_action(s)` / `o_website_header` / '
             '`o_website_link` are invented or unstyled — catalog `components/website.html` uses '
             '`<header class="o_header_standard">` as the header wrapper, with `o_website_logo` '
             '(brand wordmark), `o_website_menu` (nav links container), `nav-link` (each link), '
             '`o_website_header_right` (action row), `o_website_iconbtn` (icon button).'),
            (r'\bclass="[^"]*\b(?:o_portal_header|o_portal_brand|o_portal_user)\b',
             "KNOWN-BAD",
             '`o_portal_header` / `o_portal_brand` / `o_portal_user` are invented — '
             'catalog `components/portal.html` has NO header: the portal opens '
             'directly with `<div class="o_portal_wrap">` → `o_portal_breadcrumb` → '
             '`o_portal_doc`. Drop the header wrapper.'),
            (r'\bclass="[^"]*\b(?:pos-leftpane|pos-rightpane|pos-body|pos-section|pos-final-value|pos-order-table|pos-payment-methods|orderline-credit|order-total-grand)\b',
             "KNOWN-BAD",
             'POS class drift — these names are invented: `pos-leftpane`/`pos-rightpane` → '
             '`leftpane`/`rightpane` (no pos- prefix); `pos-body` → `pos-content`; '
             '`pos-section`/`pos-final-value`/`pos-order-table`/`pos-payment-methods`/'
             '`orderline-credit`/`order-total-grand` are not in odoo.css. Catalog '
             '`components/pos.html` is the source of truth. Custom POS UI lives as '
             'a Dialog popup INSIDE `.pos`, not as inline panels.'),
            (r'\bclass="[^"]*\b(?:o_settings_sidebar|o_settings_pane|o_settings_tab|o_setting_left|o_setting_right)\b',
             "KNOWN-BAD",
             'Settings class drift — `o_settings_sidebar`/`o_settings_pane`/'
             '`o_settings_tab`/`o_setting_left`/`o_setting_right` are invented. '
             'Catalog `components/settings.html` uses `o_base_settings_view` > '
             '`o_setting_container` > `settings_tab` (rail, `a.tab`) + `settings` '
             '(card) > `app_settings_block` > `<h2>` bands + `o_settings_container` > '
             '`o_setting_box col-12 col-lg-6`.'),
            # Account report: the invented helpers AND the pre-recalibration
            # catalog vocabulary (all CSS-less now). Real report-action classes
            # (o_account_report_scroll_*, _chatter*, _name_ellipsis,
            # _column_value, plural o_account_reports_table) must NOT match.
            (r'\bclass="[^"]*\b(?:o_account_report_(?:filter_chip|body|amount|toolbar|title|filters|banner|card|period|subhead|line\w*|caret|group\w*|pos|neg)|o_report_filters?|o_report_pdf|o_account_reports_page)\b',
             "KNOWN-BAD",
             'Account report class drift — `o_account_reports_page`, '
             '`o_account_report_toolbar`/`_title`/`_filters`/`_card`/`_line*`/`_neg` …, '
             '`o_report_filter(s)` and `o_report_pdf` are not report-action classes. '
             'Rebuild from catalog `components/account_report.html`: '
             '`div.o_action.account_report` with its own `.o_control_panel` '
             '(Print btn-primary, title + #o-cog, filters as '
             '`div#filter_<x> > button.btn.btn-secondary`), the `#warnings` '
             '`.alert-info`, then `.o_account_report_scroll_container` > table rows '
             '`tr.line_level_N` with `td.line_cell.numeric` amounts.'),
            (r'\bclass="[^"]*\b(?:o-mail-Chatter-tab|o-mail-Chatter-divider|o-mail-Chatter-action)\b',
             "KNOWN-BAD",
             'Chatter class drift — `o-mail-Chatter-tab` / `-divider` / `-action` '
             'are invented and have no CSS rules. Catalog '
             '`components/chatter.html`: Send message / Log note / Activity '
             'buttons inside `.o-mail-Chatter-topbarButtons`, then '
             '`.o-mail-Chatter-search`, `.o-mail-Chatter-attachFiles` and '
             '`.o-mail-Followers > .o-mail-Followers-button`. Never hand-add '
             '`.active` to the topbar buttons.'),
            # Kanban wrapper drift: real Odoo renders columns horizontally
            # because the renderer carries `o_kanban_renderer.o_kanban_grouped`
            # which sets flex-direction. A `<div class="o_kanban_view">` whose
            # immediate child is `<div class="o_kanban_group">` lacks that
            # wrapper and renders as stacked rows (catalog/components/kanban.html
            # line 7-8).
            (r'<div\s+class="o_kanban_view"\s*>\s*<div\s+class="o_kanban_group"',
             "KNOWN-BAD",
             'Kanban renders as STACKED ROWS instead of horizontal columns — '
             '`<div class="o_kanban_view">` needs an inner '
             '`<div class="o_kanban_renderer o_kanban_grouped">` wrapper before the '
             '`o_kanban_group` columns (catalog `components/kanban.html` lines 7-8). '
             'Without it, the catalog\'s horizontal flex CSS does not trigger.'),
            # Marker absolute-positioning drift. Every visual audit showed
            # markers with hardcoded inline `style="position:absolute;top:Npx;
            # right:N%;"` landing in dead space or over column headers / table
            # data. The catalog supports markers either INLINE adjacent to
            # their referent (preferred) or absolute INSIDE a `.mock-anchor`
            # parent that scopes the positioning. A bare absolute marker
            # outside a positioned ancestor anchors to the viewport / nearest
            # positioned ancestor — usually the wrong one.
            (r'<span class="(?![^"]*\bmock-marker-example\b)[^"]*\bmock-marker\b[^"]*"[^>]*style="[^"]*position\s*:\s*absolute',
             "KNOWN-BAD",
             'mock-marker carries inline `position:absolute` — markers are placed '
             'INLINE next to their referent by default. Absolute positioning is only '
             'valid when wrapped in a `.mock-anchor` (position:relative) parent that '
             'scopes the anchor. Bare absolute markers float over data cells or land '
             'in dead space (style_guide.md § Annotations).'),
            # ---- Retired by the 2026-10 catalog recalibration (the version
            # in the odoo.css stamp; REFRESH.md). Earlier catalog fragments
            # shipped this markup, so mocks that copied them still carry it;
            # the CSS is gone, so it renders unstyled or as the old chrome.
            (r'\bclass="[^"]*\bo_cp_cog\b', "KNOWN-BAD",
             '`o_cp_cog` (gear action menu) is retired — the control-panel action '
             'menu is ⋮: `<div class="o_control_panel_breadcrumbs_actions"><div '
             'class="o_cp_action_menus"><button class="btn o_btn_circle btn-light">'
             '` + `#o-ellipsis-v` INSIDE `.o_breadcrumb` (catalog '
             '`components/control_panel.html`). No favorite star.'),
            (r'\bclass="[^"]*\bbreadcrumb_(?:item|sep)\b', "KNOWN-BAD",
             '`breadcrumb_item` / `breadcrumb_sep` are retired — a multi-level title is '
             '`<ol class="breadcrumb"><li class="breadcrumb-item o_back_button"><a>Parent</a>'
             '</li></ol>` (direct parent only; deeper levels collapse into `#o-ellipsis-h`) '
             'over `.o_last_breadcrumb_item.active` (catalog `components/control_panel.html`).'),
            (r'\bclass="[^"]*\b(?:o_searchview_caret|o_searchview_facet_remove|o_pager_arrows?|o_setting_bookmark)\b',
             "KNOWN-BAD",
             'Retired control-panel markup — no search caret (`o_searchview_caret`; the '
             'toggler is an empty `button.o_searchview_dropdown_toggler`); facet remove is '
             '`button.o_facet_remove` + `#o-close-small`; the pager is `nav.o_pager > '
             'span.btn-group > button.btn.btn-secondary.o_pager_previous / o_pager_next`; '
             'settings have no bookmark (catalog `components/control_panel.html`).'),
            (r'\bclass="[^"]*\b(?:o_base_settings|o_setting_search_panel|o_settings_title|o_setting_band|o_setting_section|o_setting_box_split|o_setting_left_col|o_setting_right_col|o_settings_tab_icon|o_switch)\b',
             "KNOWN-BAD",
             'Retired settings markup — copy catalog `components/settings.html`: '
             '`.o_base_settings_view` root, rail `.settings_tab > a.tab[.selected]`, '
             'card `.settings > .app_settings_block`, `<h2>` bands, two-per-row '
             '`.o_setting_box.col-12.col-lg-6` with a checkbox in `.o_setting_left_pane`; '
             'no toggle switches, no label|control split rows.'),
            (r'<span[^>]*\bclass="settings_tab\b', "KNOWN-BAD",
             '`settings_tab` is the RAIL container (a `<div>`); each entry is '
             '`<a class="tab [selected]">` with an `svg.icon` app icon + `span.app_name` '
             '(catalog `components/settings.html`).'),
            (r'\bclass="[^"]*\bo_kanban_(?:record_topbar|record_menu|record_right|record_bottom|record_subtitle|age_badge|progressbar(?:_seg)?|header_amount|ribbon(?:_lost|_won)?)\b',
             "KNOWN-BAD",
             'Retired kanban helper (topbar / menu / bottom / age badge / progressbar / '
             'header amount / ribbon) — rebuild the card from catalog '
             '`components/kanban.html` (title, lines, `<footer>`, hover-only '
             '`.o_dropdown_kanban`; Lost/Won = the `o_widget_web_ribbon` widget; '
             'column progress = `.o_kanban_counter > .o_column_progress`).'),
            (r'<div\s[^>]*\bclass="(?![^"]*\bo_kanban_ghost\b)[^"]*\bo_kanban_record\b[^"]*"',
             "KNOWN-BAD",
             'Kanban records must be `<article class="o_card_record o_kanban_record">` — '
             'a `<div>` record loses all card styling; only the trailing '
             '`o_kanban_ghost` fillers are divs (catalog `components/kanban.html`).'),
            (r'\bclass="[^"]*\bo_card_(?:grid|line|key)\b', "KNOWN-BAD",
             'There is no standalone card view — `card` is the kanban record template. '
             'For summary tiles use the ungrouped kanban (catalog `components/kanban.html` '
             'layout 3).'),
            (r'\bclass="[^"]*\bo-mail-Composer\b[^"]*\bis-collapsed\b', "KNOWN-BAD",
             '`o-mail-Composer is-collapsed` is retired — wrap the composer in '
             '`<div class="o-mail-Chatter-composer" data-mock-toggleable="composer-msg|'
             'composer-note">` (or `.o-mail-Chatter-composer.is-open` without the '
             'toggleable to show it open), per catalog `components/chatter.html`.'),
            (r'\bclass="[^"]*\bo-mail-Chatter-activity\b[^"]*"[^>]*>\s*(?:<span[^>]*>\s*)?Activities\s*<',
             "KNOWN-BAD",
             'The chatter topbar button reads "Activity", never "Activities" — '
             '`<button class="btn btn-secondary o-mail-Chatter-activity"><span>Activity</span></button>`.'),
            # (A "Mark Done" <h6> popover title is real; only a button/link is not.)
            (r'\bclass="[^"]*\bo-mail-Activity(?=[\s"])(?:(?!</aside>)[\s\S]){0,2000}?<(?:button|a)\b[^>]*>(?:\s*<(?:svg|i)\b[\s\S]{0,300}?</(?:svg|i)>)?\s*Mark Done\s*<',
             "KNOWN-BAD",
             'A planned activity has no "Mark Done" / "Cancel" buttons — its tools are '
             '`button.o-mail-Activity-markDone` (#o-check) "Done" + '
             '`button.o-mail-Activity-edit` (#o-pencil) "Edit" (catalog `components/chatter.html`).'),
            (r'\bclass="[^"]*\b(?:o_mail_tracking_value|o-mail-Message-note|o_avatar_csys)\b',
             "KNOWN-BAD",
             'Retired chatter message markup — tracking is '
             '`.o-mail-Message-body.o-note.o_track` with one "Old → <b>New</b> <i>(Field)</i>" '
             'line per change; notes use `.o-mail-Message-body.o-note`; OdooBot is '
             '`<span class="o-mail-Message-avatar o_avatar_odoobot"></span>` (catalog '
             '`components/chatter.html`).'),
            (r'\bclass="[^"]*\b(?:o_dialog_header|modal-header|modal-title)\b[^"]*"[^>]*>(?:\s*<(?!/)[^>]*>)*\s*User Error\s*<',
             "KNOWN-BAD",
             'No Odoo dialog is titled "User Error" — the title comes from the exception: '
             'UserError → "Invalid Operation", ValidationError → "Validation Error", '
             'AccessError → "Access Error". Use `<h4 class="modal-title">` (catalog '
             '`components/dialog.html`).'),
            (r'\bclass="[^"]*\b(?:o_dialog_footer|modal-footer)\b[^"]*"[^>]*>(?:(?!</(?:div|footer)>)[\s\S])*?\bo_btn_outline\b',
             "KNOWN-BAD",
             'Dialog footer secondary uses `o_btn_outline` — write `btn btn-secondary`, '
             'after the leftmost `btn btn-primary` (catalog `components/dialog.html`).'),
            (r'\bclass="[^"]*\bo_tour_step\b', "KNOWN-BAD",
             '`o_tour_step` (numbered tour bubble) is retired — the tour pointer is '
             '`.o_tour_pointer > .o_tour_pointer_tip.o_<direction>` with a popover; '
             'number things with `.mock-marker` (catalog `components/tour_pointer.html`).'),
        ]
        # Variant-attribute same-axis-comma misuse. The walkthrough.js matcher
        # uses `pairs.every()` across comma-separated axis=value pairs, so
        # `data-mock-variant="state=a,state=b"` evaluates as
        # `state==a AND state==b` — impossible — and the element is HIDDEN
        # for every variant. Visual audits found 16+ such constructs that
        # silently broke statusbar pipelines, multi-state fields, and entire
        # POS panes. The correct form is `state=a|b` (pipe-separated OR on
        # the same axis; interactions.md § Attribute reference).
        for m in re.finditer(r'data-mock-variant="([^"]+)"', index_text):
            v = m.group(1)
            axes = [p.split("=")[0].strip() for p in v.split(",") if "=" in p]
            if len(axes) != len(set(axes)):
                findings.append(("KNOWN-BAD", "index.html",
                    f'data-mock-variant="{v}" repeats an axis across commas — '
                    f'commas mean cross-axis AND, so same-axis comma evaluates '
                    f'to false and the element is permanently hidden. Use the '
                    f'pipe form: <axis>=<a>|<b>|<c> for same-axis OR '
                    f'(walkthrough.js + interactions.md § Attribute reference).'))
        for pattern, code, hint in _KNOWN_BAD:
            for m in re.finditer(pattern, index_text):
                findings.append((code, "index.html", hint))
                break  # one finding per pattern is enough; the hint is global

        # Confirmation prompts are `modal-sm` (ConfirmationDialog size="sm").
        # A dialog with NO size class renders as the 980px ruled wizard. Keyed
        # on Odoo's canonical confirmation copy (title "Confirmation" /
        # "Bye-bye, record!", or an "Are you sure…" body) so text-only wizards
        # are not caught. A size class anywhere between the dialog opener and
        # its title (real shape: on the inner .modal-dialog) satisfies it.
        for m in re.finditer(
            r'<div\b[^>]*\bclass="(?![^"]*\bo_dialog_(?:user|validation)_error\b)'
            r'[^"]*\b(?:o_dialog|modal-dialog)(?=[\s"])[^"]*"[^>]*>', index_text):
            window = index_text[m.start():m.start() + 1500]
            head_m = re.search(
                r'class="[^"]*\bmodal-title\b[^"]*"[^>]*>\s*([^<]*?)\s*<', window)
            if not head_m or re.search(r'\bmodal-(?:sm|md|lg|xl)\b', window[:head_m.start()]):
                continue
            title = head_m.group(1)
            body_m = re.search(r'<p\b[^>]*>\s*([^<]{0,40})', window[head_m.end():head_m.end() + 600])
            body = body_m.group(1) if body_m else ""
            if title in ("Confirmation", "Bye-bye, record!") or body.startswith("Are you sure"):
                findings.append(("KNOWN-BAD", "index.html",
                    f'confirmation dialog "{title}" has no size class — it renders as the '
                    f'980px ruled wizard. Confirmation / delete / archive prompts are '
                    f'`<div class="o_dialog modal-sm">` (catalog `components/dialog.html`).'))
                break

        # FINDINGS#24: backend form chrome inside a non-backend surface
        # (`.o_website`, `.o_portal`, `.pos`). The recurring drift is authors
        # smuggle `o_field_row` / `o_form_label` / `o_field_widget` / `o_input` /
        # `o_group` / `o_inner_group` into these surfaces because the backend
        # equivalents are the visible default. Each surface has its own
        # vocabulary (see style_guide.md rule 14 + catalog `portal.html` /
        # `website_form.html` / `pos.html`). Scope the check to within each
        # surface wrapper by extracting the wrapper's tag-balanced content.
        _SURFACE_PATTERNS = [
            (r'<div class="o_website"', '.o_website', 'website_form.html'),
            (r'<div class="o_portal"', '.o_portal', 'portal.html'),
            (r'<div class="pos"', '.pos', 'pos.html'),
        ]
        _BACKEND_CLASSES = [
            ('o_field_row', '.o_field_row'),
            ('o_form_label', '.o_form_label'),
            ('o_field_widget', '.o_field_widget'),
            ('o_input', '.o_input'),
            ('o_group', '.o_group'),
            ('o_inner_group', '.o_inner_group'),
        ]
        for opener_re, surface_name, ref_file in _SURFACE_PATTERNS:
            for opener in re.finditer(opener_re, index_text):
                # Find the matching closing </div> by counting depth. The
                # surface wrapper is the outermost <div class="<surface>">;
                # we scan forward and balance open/close <div> tags.
                start = opener.start()
                depth = 0
                i = start
                end = -1
                while i < len(index_text):
                    open_m = re.search(r'<div\b', index_text_nc[i:])
                    close_m = re.search(r'</div>', index_text_nc[i:])
                    if not close_m:
                        break
                    if open_m and open_m.start() < close_m.start():
                        depth += 1
                        i += open_m.end()
                    else:
                        depth -= 1
                        i += close_m.end()
                        if depth == 0:
                            end = i
                            break
                if end < 0:
                    continue
                block = index_text[start:end]
                for cls, display in _BACKEND_CLASSES:
                    if re.search(rf'\bclass="[^"]*\b{cls}\b', block):
                        findings.append(("SURFACE-LEAK", "index.html",
                            f'backend class `{display}` used inside {surface_name} '
                            f'— surfaces have their own vocabulary (see style_guide.md '
                            f'rule 14 + catalog `components/{ref_file}`); '
                            f'don\'t smuggle backend form chrome onto public surfaces'))
                        # Don't break — multiple distinct leaks per surface
                        # should each fire so the author sees the full list.

                # FINDINGS#25: inline-styled tinted callout boxes inside
                # non-backend surfaces. Pattern: `<div style="...background:...;
                # border:...;">` (the hand-rolled "I needed a colored box and
                # there's no class for it" failure). Each surface ships a
                # `.*-callout` / `.*-note` class with tone variants. Match any
                # explicit background colour (hex / color-mix / catalog token)
                # paired with a border — the combination is what makes it a
                # tinted box.
                callout_re = re.compile(
                    r'<div\s+style="[^"]*'
                    r'background:\s*(?:color-mix|#[0-9a-fA-F]|var\(--o-)'
                    r'[^"]*;[^"]*border\s*:',
                    re.IGNORECASE,
                )
                if callout_re.search(block):
                    findings.append(("INLINE-CALLOUT", "index.html",
                        f'inline-styled tinted callout inside {surface_name} — '
                        f'each surface ships a callout class with tone modifiers '
                        f'(`.o_portal_note_*`, `.s_website_form_note`, `.pos-callout-*`); '
                        f'see catalog `components/{ref_file}`'))

        # Workflow-title chip overflow: data-workflow-title > 12 chars overflows
        # the workflow chip select and the cross-workflow Next button label.
        for m in re.finditer(r'data-workflow-title="([^"]+)"', index_text):
            title = m.group(1)
            if len(title) > 12:
                findings.append(("WORKFLOW-TITLE", "index.html",
                    f'data-workflow-title="{title}" is {len(title)} chars '
                    f'(max 12) — overflows the workflow chip; shorten to a single '
                    f'business noun (e.g. "Purchase" / "Sales" / "Production")'))

        # EDITION gate (SKILL.md § Comprehension → "Edition gate (ENFORCED)").
        # If Odoo ENTERPRISE source is present in the workspace, the mock MUST
        # use Enterprise chrome: a bare <body> (no o-community class) and a
        # "· Enterprise" cover kicker. Inferring "Community" from where core
        # models resolve (they ALWAYS live under odoo/addons, even on an
        # Enterprise install) is the known regression this guards. The
        # "absent ⇒ ask the user" half of the gate is interactive and stays in
        # SKILL.md; the lint enforces the two halves it can mechanically see:
        #   (a) enterprise-present ⇒ chrome must NOT be Community, and
        #   (b) the <body> class and the cover kicker must agree.
        _dir = package_dir
        enterprise_present = False
        while True:
            # Flat layout (<root>/enterprise) or the versioned layout
            # (<root>/versions/v<major>/enterprise) used by this workspace.
            if os.path.isdir(os.path.join(_dir, "enterprise")) or glob.glob(
                    os.path.join(_dir, "versions", "v*", "enterprise")):
                enterprise_present = True
                break
            parent = os.path.dirname(_dir)
            if parent == _dir:
                break
            _dir = parent
        body_is_community = bool(
            re.search(r'<body\b[^>]*\bclass="[^"]*\bo-community\b', index_text))
        km = re.search(r'mock-cover-kicker.*?·\s*(Enterprise|Community)',
                       index_text, re.IGNORECASE | re.DOTALL)
        kicker_edition = km.group(1).capitalize() if km else None
        if body_is_community and kicker_edition == "Enterprise":
            findings.append(("EDITION", "index.html",
                'chrome edition mismatch — <body> carries o-community (Community) '
                'but the cover kicker says "· Enterprise". Pick one edition and '
                'make both agree (SKILL.md § Edition gate).'))
        if (not body_is_community) and kicker_edition == "Community":
            findings.append(("EDITION", "index.html",
                'chrome edition mismatch — the cover kicker says "· Community" but '
                '<body> has no o-community class (renders Enterprise). Add '
                'o-community for Community, or set the kicker to "· Enterprise".'))
        if enterprise_present and (body_is_community or kicker_edition == "Community"):
            findings.append(("EDITION", "index.html",
                'Odoo Enterprise source (enterprise/) is present in the workspace, '
                'but this mock uses Community chrome (o-community body class / kicker '
                '"· Community"). Enterprise source present ⇒ Enterprise is the ENFORCED '
                'default (SKILL.md § Edition gate): remove the o-community body class '
                'and set the cover kicker to "· Enterprise". Do NOT infer Community '
                'from where standard models resolve — core models always live under '
                'odoo/addons even on an Enterprise install.'))

        # Workflow-screen markers with non-digit text — `>i<` is the cover
        # `mock-marker-example` pattern; workflow markers must be numbered
        # sequentially per screen (style_guide.md § Number markers per screen).
        # Match `<span class="mock-marker"` (NOT `mock-marker-example`) whose
        # text content is not a digit string.
        for m in re.finditer(
            r'<span class="(?![^"]*\bmock-marker-example\b)[^"]*\bmock-marker\b[^"]*"[^>]*>([^<]+)</span>',
            index_text,
        ):
            txt = m.group(1).strip()
            if not txt.isdigit():
                findings.append(("MARKER-TEXT", "index.html",
                    f'mock-marker text "{txt}" is not a digit — workflow-screen markers '
                    f'must be numbered sequentially per screen (style_guide.md § Number markers '
                    f'per screen). The `i` glyph is reserved for the cover `mock-marker-example`.'))
                # Don't break — let the lint surface each occurrence so the
                # author can spot which screen needs renumbering.

        # Corner ribbon (o_widget_web_ribbon). Two valid shapes: the real widget
        # markup (an inner `.ribbon` element holding a `span.text-bg-*` label),
        # or the legacy EMPTY element whose band text comes from data-text via
        # CSS ::after. Bare child text without the inner `.ribbon` renders
        # unstyled (the blank/capped-ribbon bug).
        _RIBBON_HINT = ('use `<div class="o_widget o_widget_web_ribbon"><div class="ribbon '
                        'ribbon-top-right"><span class="text-bg-success|danger">Label</span>'
                        '</div></div>` (catalog `components/form_view.html`)')
        for m in re.finditer(
            r'<([a-zA-Z][\w-]*)\b([^>]*\bclass="[^"]*\bo_widget_web_ribbon\b[^"]*"[^>]*)>([\s\S]*?)</\1>',
            index_text,
        ):
            attrs = m.group(2)
            if re.search(r'\bclass="[^"]*\bribbon\b', m.group(3)):
                continue  # real widget markup
            inner = re.sub(r'<[^>]*>', '', m.group(3)).strip()
            if 'data-text=' not in attrs:
                findings.append(("RIBBON", "index.html",
                    f"o_widget_web_ribbon has no band label — {_RIBBON_HINT}"))
            elif inner:
                findings.append(("RIBBON", "index.html",
                    f'o_widget_web_ribbon has child text "{inner[:24]}" next to data-text '
                    f"(renders unstyled) — leave the data-text element empty, or {_RIBBON_HINT}"))

        # Backend guard banners use the UserError modal, not a Bootstrap
        # `alert alert-danger` inline banner. Scope the check to backend form
        # chrome (`.o_form_view`); inline alerts inside `.o_website` /
        # `.o_portal` / `.pos` use those surfaces' own callout vocabulary
        # (already flagged by INLINE-CALLOUT + SURFACE-LEAK above).
        for m in re.finditer(
            r'<div[^>]*\bclass="[^"]*\bo_form_view\b[^"]*"',
            index_text,
        ):
            # Find the form view's tag-balanced body — same depth-counting
            # technique used for surface wrappers above. Reuse a small inline
            # walker rather than refactoring (kept short).
            start = m.start()
            depth = 0
            i = start
            end = -1
            while i < len(index_text):
                open_m = re.search(r'<div\b', index_text_nc[i:])
                close_m = re.search(r'</div>', index_text_nc[i:])
                if not close_m:
                    break
                if open_m and open_m.start() < close_m.start():
                    depth += 1
                    i += open_m.end()
                else:
                    depth -= 1
                    i += close_m.end()
                    if depth == 0:
                        end = i
                        break
            if end < 0:
                continue
            block = index_text[start:end]
            if re.search(r'\bclass="[^"]*\balert\s+alert-danger\b', block):
                findings.append(("GUARD-BANNER", "index.html",
                    'Bootstrap `alert alert-danger` used inside `.o_form_view` — '
                    'real Odoo guards a blocking action via a UserError modal, '
                    'not an inline alert. Use `.o_dialog.o_dialog_user_error` '
                    'instead (see `reference/interactions.md` § UserError / '
                    'ValidationError dialog).'))

        # ---- GUARD-LANDING: an error dialog open by default must not sit on a
        # state the reader LANDS on. Setup values (Block posting, a shared
        # entry…) render the normal screen and open the dialog on the gated
        # click; only an "attempt" value (the variant names the action itself)
        # may show it open by default (interactions.md § UserError dialog).
        # Landing values = each axis default + every value another screen sets
        # by click-through + every value an Ok/Save (data-mock-modal-close)
        # sets after completing an action.
        landing = {}
        defaults = {}
        sections = _screen_segments(index_text)
        for sid, tag, _body in sections:
            am = re.search(r"""data-mock-variant-axes=(['"])(.*?)\1""", tag, re.DOTALL)
            if am:
                try:
                    for ax in json.loads(html.unescape(am.group(2))):
                        defaults.setdefault(sid, {})[ax.get("key")] = ax.get("default")
                except ValueError:
                    pass
        for sid, _tag, body in sections:
            for el in re.finditer(r'<[a-z][^>]*\bdata-mock-set-variant="([^"]+)"[^>]*>', body):
                closes = "data-mock-modal-close" in el.group(0)
                for one in el.group(1).split(";"):
                    if ":" not in one or "=" not in one:
                        continue
                    target, pair = one.split(":", 1)
                    axis_key, value = pair.split("=", 1)
                    target = target.strip()
                    if target != sid or closes:
                        landing.setdefault(target, {}).setdefault(axis_key.strip(), set()).add(value.strip())
        for sid, _tag, body in sections:
            for dm in re.finditer(r'<div[^>]*\bclass="[^"]*\bo_dialog_backdrop\b[^"]*\bis-open\b[^"]*"[^>]*>', body):
                if not re.match(r'\s*<div[^>]*\bclass="[^"]*\bo_dialog_(user|validation)_error\b', body[dm.end():dm.end() + 200]):
                    continue
                vm = re.search(r'\bdata-mock-variant="([^"]*)"', dm.group(0))
                spec = vm.group(1) if vm else ""
                pairs = [p.split("=", 1) for p in spec.split(",") if "=" in p]
                hit = True
                for axis_key, values in pairs:
                    axis_key = axis_key.strip()
                    can_land = set(landing.get(sid, {}).get(axis_key, set()))
                    if defaults.get(sid, {}).get(axis_key) is not None:
                        can_land.add(defaults[sid][axis_key])
                    if not can_land & {v.strip() for v in values.split("|")}:
                        hit = False
                        break
                if hit:
                    findings.append(("GUARD-LANDING", f"screen {sid}",
                        f'error dialog open by default at `{spec or "every state"}`, a state the reader lands on '
                        '(axis default, a click-through from another screen, or an Ok that completes an action). '
                        'Make it click-only (drop `mock-blocking-modal is-open`; open it from the gated button with '
                        '`data-mock-modal-open`), or keep it open by default only on a variant value that names the '
                        'attempted action itself (interactions.md § UserError / ValidationError dialog).'))

        # ---- CLASS-UNKNOWN: every o_*/s_*/oe_* class in index.html must have a
        # CSS rule in one of the package's bundled stylesheets.
        # Closes the "invented vocabulary" bug class — markup pattern looks
        # right, anchor passes, but the screens render as flat unstyled HTML
        # because the class names have no backing CSS (observed at scale on
        # TEST007's web/portal surfaces — 17 invented o_wsale_* tokens).
        # Only catalog-prefixed namespaces are checked (o_, s_website_, oe_)
        # to keep Bootstrap / Tailwind / utility classes out of scope.
        known_classes = set()
        for css_file in _iter_files(package_dir, {".css"}):
            with open(css_file, encoding="utf-8", errors="replace") as fh:
                css_text = fh.read()
            # Capture every class token appearing anywhere in a selector,
            # including compound (.foo.bar), descendant (.foo .bar), pseudo
            # (.foo:hover, .foo:not(.bar)), and attribute-modifier selectors.
            # A class that's only mentioned as :not(.x) is still defined as
            # far as the lint cares — the catalog acknowledges it exists.
            for m in re.finditer(r'\.([_a-zA-Z][\w-]*)', css_text):
                known_classes.add(m.group(1))
        # mock-design's own framework classes — added to keep the lint focused
        # on Odoo vocabulary (mock-marker / mock-cover-* etc. live in
        # annotations.css; the iteration above already picks them up, but the
        # explicit allowlist documents intent for future-readers).
        known_classes.update({
            "mock-screen", "mock-workflow", "mock-marker", "mock-cover",
            "mock-walkthrough",
        })
        # Credit every class the catalog's own component fragments use. A class
        # shipped by a `components/*.html` fragment is legitimate vocabulary even
        # when the catalog styles it only via a child selector (container classes
        # like `o-mail-ActivityList`, `o_web_studio_*`). Without this the rule
        # false-fails a mock composed verbatim from the catalog; WITH it, only
        # genuinely invented classes (in neither CSS nor any fragment) are flagged.
        known_classes.update(_catalog_class_tokens())
        for tag_m in re.finditer(r'\bclass=(["\'])([^"\']*)\1', index_text):
            tokens = tag_m.group(2).split()
            for tok in tokens:
                # Only check catalog-prefixed namespaces. Other tokens (btn,
                # text-muted, badge, modal, table, …) belong to Bootstrap or
                # framework utilities outside the catalog's surface — out of
                # scope here.
                if not (tok.startswith("o_")
                        or tok.startswith("s_website_")
                        or tok.startswith("oe_")
                        or tok.startswith("o-mail-")):
                    continue
                if tok in known_classes:
                    continue
                # Carry a small slug for the operator to locate the offender.
                # `data-screen` first; class= attribute as a fallback.
                slug_m = re.search(
                    r'data-screen="([^"]+)"',
                    index_text[max(0, tag_m.start() - 600):tag_m.start()],
                )
                where = (
                    f"index.html#{slug_m.group(1)}"
                    if slug_m else "index.html"
                )
                findings.append(("CLASS-UNKNOWN", where,
                    f'class `{tok}` has no CSS rule in any `assets/*.css` — '
                    f'either an invented class name (renders unstyled) or the '
                    f'catalog component shipping it isn\'t in this mock\'s '
                    f'`assets/odoo.css`. Add the rule to the catalog and '
                    f'refresh assets, or fix the class name.'))

        # ---- SURFACE-LEAK: known backend classes inside .o_website / .o_portal.
        # Closes the "backend chrome bleeds into customer-facing surface"
        # bug class (observed on wf3-s3 portal Payment Methods which used
        # `o_list_table` + `o_data_row`; same family as the wf3-s4 alert
        # leak previously caught by mock-fidelity-anchor). The check
        # complements the anchor's pattern audit with a mechanical grep so
        # the regression can't ship past lint a second time.
        # The class list is the high-confidence backend vocabulary; expand
        # cautiously — false positives erode trust in the rule fast.
        _BACKEND_CLASSES = (
            "o_form_view", "o_form_sheet", "o_form_sheet_bg", "o_form_statusbar",
            "o_field_row", "o_form_label", "o_field_widget",
            "o_group", "o_inner_group",
            "o_list_view", "o_list_table", "o_list_table_ungrouped", "o_data_row",
            "o_kanban_view", "o_kanban_record",
            "o_control_panel", "o_control_panel_main", "o_breadcrumb",
            "o_navbar", "o_main_navbar", "o_menu_brand", "o_menu_sections",
        )
        for surface in ("o_website", "o_portal"):
            # Depth-balanced extraction of each surface's body (same technique
            # used by GUARD-BANNER above for `.o_form_view`).
            for surf_m in re.finditer(
                rf'<div[^>]*\bclass="[^"]*\b{surface}\b[^"]*"[^>]*>',
                index_text, re.I,
            ):
                start = surf_m.start()
                depth = 0
                i = start
                end = -1
                while i < len(index_text):
                    open_m = re.search(r'<div\b', index_text_nc[i:])
                    close_m = re.search(r'</div>', index_text_nc[i:])
                    if not close_m:
                        break
                    if open_m and open_m.start() < close_m.start():
                        depth += 1
                        i += open_m.end()
                    else:
                        depth -= 1
                        i += close_m.end()
                        if depth == 0:
                            end = i
                            break
                if end < 0:
                    continue
                body = index_text[start:end]
                slug_m = re.search(r'data-screen="([^"]+)"',
                                   index_text[max(0, start - 600):start])
                where = (
                    f"index.html#{slug_m.group(1)}"
                    if slug_m else f"index.html (inside .{surface})"
                )
                # Find each backend class as a class-attribute token (not just
                # any string match) so unrelated comments / data attributes
                # don't false-positive.
                for cls in _BACKEND_CLASSES:
                    if re.search(rf'\bclass="[^"]*\b{re.escape(cls)}\b', body):
                        findings.append(("SURFACE-LEAK", where,
                            f'backend class `{cls}` used inside `.{surface}` — '
                            f'each public surface has its own catalog vocabulary '
                            f'(see `catalog/components/{surface[2:]}.html` and '
                            f'related). Using backend form / list chrome here '
                            f'leaks the back-office look-and-feel into a '
                            f'customer-facing page.'))

        # ---- NESTING: components with required-parent doctrine.
        # Closes the "structurally-wrong nesting that lint can't see because
        # it's syntactically fine" bug class. Observed on WF4 chatter
        # (`<aside class="o-mail-Chatter">` nested inside `.o_form_sheet_bg`
        # instead of as its sibling, so the catalog's
        # `.o_content_with_chatter` flex container had only one child and
        # the chatter stacked below the sheet instead of as a right rail).
        # The doctrine table below is the seed; extend as new
        # required-parent rules surface from the catalog component
        # references.
        _REQUIRED_PARENT = {
            # tag-and-class signature : (required-parent-class, where-the-doctrine-lives)
            ("aside", "o-mail-Chatter"):
                ("o_content_with_chatter",
                 "catalog/components/chatter.html § Wrap with `.o_content_with_chatter`"),
        }
        for (tag, child_class), (required_parent, doctrine) in _REQUIRED_PARENT.items():
            for m in re.finditer(
                rf'<{tag}[^>]*\bclass="[^"]*\b{re.escape(child_class)}\b[^"]*"[^>]*>',
                index_text,
            ):
                # Walk backwards from the child's open tag, depth-counting
                # `<div>` opens vs closes, to find the innermost open div
                # (the direct parent).
                prefix = index_text[:m.start()]
                opens = list(re.finditer(r'<div\b[^>]*>', prefix))
                closes = list(re.finditer(r'</div>', prefix))
                # Each close cancels the most-recent unclosed open.
                stack = []
                # Merge opens and closes in document order.
                merged = sorted(opens + closes, key=lambda x: x.start())
                for ev in merged:
                    if ev.re.pattern.startswith("</div"):
                        if stack:
                            stack.pop()
                    else:
                        stack.append(ev)
                if not stack:
                    continue
                direct_parent = stack[-1].group(0)
                if re.search(rf'\bclass="[^"]*\b{re.escape(required_parent)}\b',
                             direct_parent):
                    continue
                slug_m = re.search(r'data-screen="([^"]+)"',
                                   index_text[max(0, m.start() - 600):m.start()])
                where = (
                    f"index.html#{slug_m.group(1)}"
                    if slug_m else "index.html"
                )
                findings.append(("NESTING", where,
                    f'<{tag} class="{child_class}"> must be a direct child of '
                    f'`.{required_parent}` (see {doctrine}). It is currently '
                    f'nested one level deeper, which breaks the catalog\'s '
                    f'flex / grid layout — the catalog CSS keys off the '
                    f'direct-child relationship.'))

        # ---- FIELD-HELP-INCOMPLETE: every `o_field_help` "?" must carry
        # data-help, data-field, data-model, data-type — all present and
        # non-empty, data-model dotted-lowercase, data-field a Python
        # identifier. Closes the "malformed ? widget" class: tooltip pops
        # visually but the developer-facing Field/Model/Type panel is blank
        # because the emitting author forgot half the attrs.
        field_re = re.compile(r'^[a-z_][a-z0-9_]*$')
        model_re = re.compile(r'^[a-z_]+(\.[a-z0-9_]+)+$')
        help_pattern = re.compile(
            r'<span\s+([^>]*?class=(["\'])[^"\']*\bo_field_help\b[^"\']*\2[^>]*)>'
            r'\s*\?\s*</span>',
            re.DOTALL,
        )
        for m in help_pattern.finditer(index_text):
            attrs_chunk = m.group(1)
            attr_map = {}
            for am in re.finditer(
                r'(data-[a-z-]+)\s*=\s*(["\'])(.*?)\2', attrs_chunk, re.DOTALL
            ):
                attr_map[am.group(1)] = am.group(3)
            problems = []
            for key in ("data-help", "data-field", "data-model", "data-type"):
                v = attr_map.get(key, "").strip()
                if not v:
                    problems.append(f"missing/empty {key}")
            f_val = attr_map.get("data-field", "").strip()
            if f_val and not field_re.match(f_val):
                problems.append(f"data-field={f_val!r} is not a valid Odoo field name")
            m_val = attr_map.get("data-model", "").strip()
            if m_val and not model_re.match(m_val):
                problems.append(f"data-model={m_val!r} is not a dotted lowercase model name")
            if problems:
                cite = attr_map.get("data-field") or attr_map.get("data-label") or "<no data-field>"
                findings.append((
                    "FIELD-HELP-INCOMPLETE", "index.html",
                    f'o_field_help "?" for `{cite}` — {"; ".join(problems)}. '
                    f'Every solution-added field\'s "?" must carry all four attrs '
                    f'(data-help, data-field, data-model, data-type) so the tooltip '
                    f'renders the full developer-facing Field / Model / Type panel; '
                    f'missing attrs render as a bare "?" with a blank technical reference.'
                ))

        # ---- CUSTOM-UNMARKED / CUSTOM-PLACEMENT: custom marking is gated like
        # the "?" (interactions.md § Custom elements). Every "?" field sits in
        # a `mock-custom` element or on a `mock-custom` screen; marks never sit
        # on the cover / workflow overviews, never inside a custom screen, and
        # never nest. Which non-field elements the solution adds is judged by
        # the anchors against the spec — the lint cannot see that.
        scan = _CustomScan()
        scan.feed(index_text)
        scan.close()
        findings.extend(scan.results())

    return findings


def bundle_notes(path):
    """Advisory (non-failing): state of the single-file deliverable built by
    _bundle_mock.py from the _reference/ working package."""
    pkg = _mock_paths.package_dir(path)
    if os.path.basename(pkg) != _mock_paths.REF:
        return []  # legacy flat package — no bundle convention
    out = _mock_paths.bundle_path(pkg)
    if not os.path.isfile(out):
        return [f'no single-file deliverable yet — after the final checks run '
                f'`_bundle_mock.py "{_mock_paths.mocks_root(pkg)}"`.']
    # Only what the bundle is built from: index.html + assets/** (dotfiles such
    # as a Finder .DS_Store, and README.md, are not bundled).
    sources = [os.path.join(pkg, "index.html")]
    for d, dirs, fs in os.walk(os.path.join(pkg, "assets")):
        dirs[:] = [x for x in dirs if not x.startswith(".")]
        sources += [os.path.join(d, f) for f in fs if not f.startswith(".")]
    newest = max((os.path.getmtime(f) for f in sources if os.path.isfile(f)), default=0)
    if newest > os.path.getmtime(out):
        return [f'"{os.path.basename(out)}" is older than the _reference/ package — '
                f're-bundle after the final checks.']
    return []


def version_notes(package_dir):
    """Advisory (non-failing): the cover kicker's "Odoo NN" vs the version the
    package's assets/odoo.css is calibrated to (its `calibrated to Odoo NN`
    header stamp). The catalog tracks ONE Odoo version; a mock for another
    version renders that version's chrome — say so instead of failing."""
    notes = []
    try:
        with open(os.path.join(package_dir, "index.html"), encoding="utf-8") as fh:
            index_text = fh.read()
        with open(os.path.join(package_dir, "assets", "odoo.css"), encoding="utf-8") as fh:
            css_head = fh.read(600)
    except OSError:
        return notes
    km = re.search(r'mock-cover-kicker.*?Odoo\s+(\d+)', index_text, re.DOTALL)
    cm = re.search(r'calibrated to Odoo (\d+)', css_head)
    if km and cm and km.group(1) != cm.group(1):
        notes.append(
            f'the cover says Odoo {km.group(1)} but assets/odoo.css is calibrated to '
            f'Odoo {cm.group(1)} — screens render Odoo {cm.group(1)} chrome. Expected '
            f'when the spec targets an older version (the catalog tracks one version).')
    return notes


def main(argv=None):
    ap = argparse.ArgumentParser(description="Lint an odoo-mock-design package.")
    ap.add_argument("package_dir", help="the mocks folder or its _reference/ working package "
                    "(a legacy flat package resolves too)")
    ap.add_argument("--steps", nargs="*", default=None,
                    help="workflow step names that must each have a screen")
    args = ap.parse_args(argv)

    findings = lint(args.package_dir, steps=args.steps)
    if findings and findings[0][0] == "FATAL":
        print(f"FATAL: {findings[0][2]}", file=sys.stderr)
        return 2

    for note in version_notes(_mock_paths.package_dir(args.package_dir)) + bundle_notes(args.package_dir):
        print(f"NOTE: {note}")

    if not findings:
        print(f"PASS — {args.package_dir} is self-contained and complete.")
        return 0

    print(f"FAIL — {len(findings)} finding(s) in {args.package_dir}:\n")
    for kind, where, msg in findings:
        print(f"  [{kind}] {where}: {msg}")
    print("\nFix all findings; a mock package must be self-contained and placeholder-free.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
