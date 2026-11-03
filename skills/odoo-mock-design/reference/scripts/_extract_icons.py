#!/usr/bin/env python3
"""_extract_icons.py — real Odoo icon glyphs as SVG <symbol>s for catalog/icons.svg.

Odoo (v20+) draws UI icons from two fonts, both shipped in the source tree:
  * Material Symbols Outlined — `<i class="oi" data-icon="NAME">` (ligatures);
    the backend WOFF carries the codepoints listed in `web/icons.py`.
    `.oi-filled` switches the FILL axis → use --filled for those glyphs.
  * odoo_ui_icons — `data-icon="oi_NAME"` (view switchers, Odoo logo, brands);
    outlines live in `web/tooling/icons/odoo_ui_icons_config.json`.

Use this when refreshing the catalog for a new Odoo version (see REFRESH.md):
find the data-icon name the real template uses, then paste the printed symbol
into catalog/icons.svg under the catalog's existing id (ids are the contract
mocks use — keep them stable, swap only the artwork).

Usage:
    python _extract_icons.py --list
    python _extract_icons.py NAME[=symbol-id] [NAME[=id] ...] [--filled]
    python _extract_icons.py oi_view-kanban=o-view-kanban
    python _extract_icons.py star=o-star-filled --filled
Options:
    --web PATH   Odoo `web` addon dir (default: newest versions/v*/odoo/addons/web)
Requires fonttools + brotli in the running Python (`pip install fonttools brotli`;
a throwaway venv is fine — this is a maintainer tool, not used when building mocks).
"""
import argparse
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _default_web():
    # skills/odoo-mock-design/reference/scripts → repo root is 4 levels up.
    root = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
    cands = sorted(glob.glob(os.path.join(root, "versions", "v*", "odoo", "addons", "web")),
                   key=lambda p: int(re.search(r"/v(\d+)/", p).group(1)))
    return cands[-1] if cands else None


def _ms_codepoints(web):
    src = open(os.path.join(web, "icons.py"), encoding="utf-8").read()
    return {m.group(1): int(m.group(2), 16) for m in re.finditer(
        r"'([a-z0-9_]+)': \{'has_fill': (?:True|False), 'codepoint': 0x([0-9A-Fa-f]+)", src)}


def _oi_glyphs(web):
    cfg = os.path.join(web, "tooling", "icons", "odoo_ui_icons_config.json")
    return {g["css"]: g for g in json.load(open(cfg, encoding="utf-8"))["glyphs"]}


def _fill_map(font):
    """FILL=1 alternates: GSUB FeatureVariations single substitutions."""
    gsub = font["GSUB"].table
    mapping = {}
    if getattr(gsub, "FeatureVariations", None):
        for rec in gsub.FeatureVariations.FeatureVariationRecord:
            for sub in rec.FeatureTableSubstitution.SubstitutionRecord:
                for li in sub.Feature.LookupListIndex:
                    for st in gsub.LookupList.Lookup[li].SubTable:
                        if hasattr(st, "mapping"):
                            mapping.update(st.mapping)
    return mapping


def _norm(d):
    """Trim float noise (655.0 → 655) so symbols diff cleanly against the catalog."""
    return re.sub(r"(\d)\.0(?!\d)", r"\1", d)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("names", nargs="*")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--filled", action="store_true")
    ap.add_argument("--web", default=_default_web())
    a = ap.parse_args(argv)
    if not a.web or not os.path.isdir(a.web):
        sys.exit("Odoo web addon not found; pass --web <path>/odoo/addons/web")
    cps, oi = _ms_codepoints(a.web), _oi_glyphs(a.web)
    if a.list:
        print("MS:", " ".join(sorted(cps)))
        print("OI:", " ".join("oi_" + n for n in sorted(oi)))
        return 0
    try:
        from fontTools.pens.svgPathPen import SVGPathPen
        from fontTools.pens.transformPen import TransformPen
        from fontTools.ttLib import TTFont
    except ImportError:
        sys.exit("needs fonttools + brotli: pip install fonttools brotli")
    font = TTFont(os.path.join(a.web, "static", "src", "libs", "materialsymbols", "material_symbols_backend.woff"))
    glyphs, cmap = font.getGlyphSet(), font.getBestCmap()
    asc, upm = font["hhea"].ascent, font["head"].unitsPerEm
    fill = _fill_map(font) if a.filled else {}
    missing = []
    for arg in a.names:
        name, _, sid = arg.partition("=")
        if name.startswith("oi_"):
            g = oi.get(name[3:])
            if not g:
                missing.append(name)
                continue
            print(f'<symbol id="{sid or "o-" + name[3:]}" viewBox="0 0 {g["svg"]["width"]} 1000">'
                  f'<path d="{g["svg"]["path"]}"/></symbol>')
            continue
        if name not in cps:
            missing.append(name)
            continue
        gname = cmap[cps[name]]
        gname = fill.get(gname, gname)
        pen = SVGPathPen(glyphs)
        glyphs[gname].draw(TransformPen(pen, (1, 0, 0, -1, 0, asc)))  # font y-up → SVG y-down
        # overflow="visible": some Material glyphs overshoot their box (e.g. settings at x=-2).
        print(f'<symbol id="{sid or "o-" + name}" viewBox="0 0 {glyphs[gname].width} {upm}" overflow="visible">'
              f'<path d="{_norm(pen.getCommands())}"/></symbol>')
    if missing:
        print("MISSING: " + " ".join(missing), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
