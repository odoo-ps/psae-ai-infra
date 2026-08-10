#!/usr/bin/env python3
"""_scaffold_mock.py — Emit a canonical-skeleton index.html from a spec.

What this DOES:
  - Read a spec folder's `_reference/_build_<task-code>.py` `SPEC_DATA` dict.
  - Emit a starter `index.html` with the structural pieces a mock requires:
      • <head> + inline icon sprite (copies catalog/icons.svg verbatim)
      • Cover screen — brand header, canonical FIVE callouts (with the
        conditional ones included/omitted per the spec's structure),
        workflow narrative table with three-cell axis chips.
      • One `<div class="mock-workflow">` shell per workflow (multi-
        workflow case) with a per-workflow overview screen.
      • One `<section class="mock-screen">` placeholder per `flow_strip`
        step, with a `<!-- SLOT: -->` comment for the generator to fill.
      • Walkthrough bar at the bottom (copies catalog walkthrough_bar.html).
  - Also copy the catalog's three assets (`annotations.css`,
    `walkthrough.js`, `odoo.css`) plus the two brand images
    (`odoo-icon.svg`, `odoo-logo.png`) into the package's `assets/`.

What this DOES NOT do:
  - Decide which screens are needed (the spec's flow_strip drives that,
    but curation/pruning is still the generator's job — see SKILL.md
    § Curate the screen list).
  - Fill in screen bodies. Each placeholder screen carries an empty
    body with a `<!-- SLOT: compose from components/<view-type>.html -->`
    comment. The generator picks the right view type and composes
    verbatim from `reference/catalog/components/`.
  - Author marker content. Markers are workflow-anchored explanations
    of solution elements; the spec's user-stories / business-rules /
    new-fields don't map 1:1 to markers. See `style_guide.md`
    § Annotations.

The skeleton passes Stage-1 lint by construction: no placeholder
strings (TODO/TBD/Lorem), all refs resolve inside the package, icon
sprite inlined, no external URLs.

Usage:
    python3 _scaffold_mock.py <spec-folder>

    # spec-folder is a path like
    # `specifications/TEST00X - INTERNAL - <slug>/`. The script writes
    # `<spec-folder>/mocks/` (creates `mocks/` and `assets/` if absent).

Exit code 0 = success, 1 = problem (e.g. SPEC_DATA missing required keys).

No third-party dependencies (stdlib only). Reads SPEC_DATA via
`importlib` so the build script's other imports (python-docx, etc.) are
NOT required — we only need the `SPEC_DATA` dict, not the docx builder.
"""
import argparse
import importlib.util
import os
import shutil
import sys
import textwrap
import types


# ---------------------------------------------------------------------------
# Path resolution

def _find_build_py(spec_folder):
    """Return the path to _build_<task-code>.py inside the spec folder, or None."""
    ref = os.path.join(spec_folder, "_reference")
    if not os.path.isdir(ref):
        return None
    for f in sorted(os.listdir(ref)):
        if f.startswith("_build_") and f.endswith(".py"):
            return os.path.join(ref, f)
    return None


def _catalog_dir():
    """Locate the catalog dir relative to this script."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "catalog"))


# ---------------------------------------------------------------------------
# SPEC_DATA loading — stdlib only

def load_spec_data(build_py_path):
    """Import _build_TEST00X.py and return its SPEC_DATA dict.

    Build scripts typically import python-docx for the docx builder. We
    don't want to require that — we only need the SPEC_DATA dict. So we
    install dummy modules for the heavy imports BEFORE loading.
    """
    # Stub out heavy imports the build script may pull in but we don't need.
    for name in ("docx", "docx.shared", "docx.enum.text", "docx.enum.table",
                 "docx.oxml", "docx.oxml.ns", "PIL", "PIL.Image"):
        if name not in sys.modules:
            stub = types.ModuleType(name)
            # Calling anything on the stub returns another stub — lets module
            # body execute past attribute access (e.g. `docx.shared.RGBColor`).
            def _attr(self, _attr_name): return _ChainableStub()
            class _ChainableStub:
                def __getattr__(self, _): return _ChainableStub()
                def __call__(self, *a, **kw): return _ChainableStub()
            stub.__getattr__ = lambda name: _ChainableStub()  # type: ignore
            sys.modules[name] = stub
    spec = importlib.util.spec_from_file_location("_spec_module", build_py_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {build_py_path} as a module")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "SPEC_DATA"):
        raise RuntimeError(f"{build_py_path} does not define SPEC_DATA")
    return mod.SPEC_DATA


# ---------------------------------------------------------------------------
# Template emitters — each returns a chunk of HTML.

def _escape(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def _flow_strip(wf):
    """Return the workflow's step list as plain strings.

    Specs vary: some carry an explicit `flow_strip` list, others encode
    the steps in `bpmn_diagram.nodes` (using `kind: "task"` + an `action`
    label). Try `flow_strip` first; fall back to BPMN tasks.
    """
    explicit = wf.get("flow_strip") or []
    if explicit:
        return [str(s) for s in explicit]
    nodes = (wf.get("bpmn_diagram") or {}).get("nodes") or []
    steps = []
    for n in nodes:
        if n.get("kind") == "task":
            steps.append(str(n.get("action") or n.get("label") or "Step"))
    return steps


def _short_workflow_title(name):
    """Reduce a long workflow name to ≤ 12 chars for the chip.

    Doesn't try to be smart — picks the first word if short, else
    truncates. Author should always review and replace with a hand-
    picked single business noun (style_guide.md § Workflow titles).

    Prints a WARN line to stderr when truncation occurs so the lint's
    "passes by construction" contract holds: the scaffolder never emits
    a `data-workflow-title` > 12 chars, but the author sees the
    truncated label and can replace it.
    """
    if len(name) <= 12:
        return name
    first = name.split()[0] if name else "Workflow"
    if len(first) <= 12:
        result = first
    else:
        result = first[:12]
    print(
        f'WARN: workflow "{name}" chip title set to "{result}" '
        f'(>{12} chars in source). Review and pick a single business '
        f'noun (e.g. "Purchase" / "Sales" / "Production") or a business '
        f'acronym (O2C, P2P) per style_guide.md § Workflow titles.',
        file=sys.stderr,
    )
    return result


def _slug(text):
    """kebab-case slug for data-workflow / data-screen IDs."""
    import re
    s = re.sub(r"[^a-zA-Z0-9]+", "-", (text or "").lower()).strip("-")
    return s or "wf"


def _read_catalog_file(rel_path):
    """Read a file from the catalog (sprite, walkthrough_bar.html, etc.)."""
    return open(os.path.join(_catalog_dir(), rel_path), encoding="utf-8").read()


def _templates_dir():
    """Locate reference/templates/ relative to this script."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "templates"))


def _parse_callout_template(text):
    """Parse `reference/templates/cover_callouts.html` into [(id, rule, body), ...].

    Marker format: `<!-- CALLOUT: <id> | <rule> -->`
    Rules: `ALWAYS`, `IF multi_workflows`, `IF variant_axes`, `IF field_help`.
    Markers appear in the canonical reading order; we preserve that order.
    """
    import re
    pattern = re.compile(
        r'<!--\s*CALLOUT:\s*(?P<id>[a-z_]+)\s*\|\s*(?P<rule>[A-Z][A-Z_ a-z]*?)\s*-->',
    )
    matches = list(pattern.finditer(text))
    out = []
    for i, m in enumerate(matches):
        body_start = m.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[body_start:body_end].strip("\n")
        out.append((m.group("id"), m.group("rule").strip(), body))
    return out


def _cover_callouts(has_multi_workflows, has_variant_axes_hint, has_new_fields):
    """Emit the canonical FIVE callouts, including only those whose
    conditional trigger fires.

    Canonical wording lives in `reference/templates/cover_callouts.html`
    (SINGLE SOURCE OF TRUTH). We parse that file at runtime and emit the
    callouts whose inclusion rule is satisfied by the runtime flags.
    Wording changes happen there, in one edit, not here.
    """
    template_path = os.path.join(_templates_dir(), "cover_callouts.html")
    with open(template_path, encoding="utf-8") as f:
        text = f.read()
    flags = {
        "multi_workflows": has_multi_workflows,
        "variant_axes": has_variant_axes_hint,
        "field_help": has_new_fields,
    }
    parts = []
    for cid, rule, body in _parse_callout_template(text):
        if rule == "ALWAYS":
            include = True
        elif rule.startswith("IF "):
            flag_name = rule[3:].strip()
            include = bool(flags.get(flag_name, False))
        else:
            # Unknown rule — fail loud rather than silently dropping the callout.
            raise RuntimeError(
                f"_cover_callouts: unknown inclusion rule {rule!r} for callout "
                f"{cid!r} in cover_callouts.html"
            )
        if include:
            parts.append(body)
    return "\n".join(parts)


def _emit_cover(title, summary, workflows):
    """Main cover: brand header + canonical callouts + workflow narrative table."""
    multi = len(workflows) >= 2
    has_axes_hint = True  # assume yes; generator can remove the callout if no screen ends up with axes
    has_new_fields = any(
        wf.get("subsections", {}).get("new_fields", {}).get("table")
        for wf in workflows
    )
    callouts = _cover_callouts(multi, has_axes_hint, has_new_fields)

    # Workflow narrative — one <li> per workflow when multi; one <li> per
    # flow_strip step when single.
    if multi:
        rows = []
        for i, wf in enumerate(workflows, start=1):
            short = _short_workflow_title(wf["name"])
            wf_slug = _slug(wf["name"])
            summary_text = wf.get("summary", "")
            rows.append(f'''        <li>
          <span class="mock-step-num">{i}</span>
          <span>{_escape(summary_text)}</span>
          <a class="mock-step-axes mock-step-axes-cta" data-mock-goto="wf{i}-overview">{_escape(wf["name"])}</a>
        </li>''')
        listing = "\n".join(rows)
    else:
        wf = workflows[0]
        rows = []
        for i, step in enumerate(_flow_strip(wf), start=1):
            rows.append(f'''        <li>
          <span class="mock-step-num">{i}</span>
          <span>{_escape(step)}</span>
          <span></span>
        </li>''')
        listing = "\n".join(rows) if rows else "        <!-- SLOT: workflow steps from spec's flow_strip -->"

    return f'''<!-- ===================== COVER ===================== -->
<section class="mock-screen" data-screen="cover" data-title="Overview"
         data-desc="What this mock demonstrates">
  <div class="mock-cover">
    <div class="mock-cover-kicker"><img src="assets/odoo-icon.svg" alt=""/> Odoo 19 · Enterprise</div>
    <img class="mock-cover-logo" src="assets/odoo-logo.png" alt="Odoo"/>
    <h1>{_escape(title)}</h1>
    <p>{_escape(summary)}</p>
  </div>
  <div class="mock-cover-section">
{callouts}

    <div class="mock-step-list-wrap">
      <div class="mock-step-list-header-workflow">WORKFLOW</div>
      <div class="mock-step-list-header-variants">{'GO TO' if multi else 'VARIANTS'}</div>
      <ol class="mock-step-list">
{listing}
      </ol>
    </div>
  </div>
</section>
'''


def _emit_workflow_overview(idx, total, wf):
    """Per-workflow overview screen — actors + narrative + step list.
    Only emitted when there are ≥ 2 workflows."""
    short = _short_workflow_title(wf["name"])
    actors_table = wf.get("subsections", {}).get("user_stories_and_steps", {}).get("table") or []
    actors = sorted({row[2] for row in actors_table[1:] if len(row) >= 3 and row[2]})  # column "Actor"

    actor_callouts = "\n".join(
        f'      <div class="mock-cover-callout"><strong>{_escape(a)}.</strong> <!-- SLOT: role description -->.</div>'
        for a in actors
    ) or '      <div class="mock-cover-callout"><strong>Actor.</strong> <!-- SLOT: role description --></div>'

    step_rows = []
    for i, step in enumerate(_flow_strip(wf), start=1):
        step_rows.append(f'''        <li><span class="mock-step-num">{i}</span>
          <span>{_escape(step)}</span>
          <span></span>
        </li>''')
    step_list = "\n".join(step_rows) if step_rows else "        <!-- SLOT: flow_strip steps -->"

    return f'''
  <section class="mock-screen" data-screen="wf{idx}-overview" data-screen-kind="workflow-overview"
           data-title="{_escape(wf['name'])} workflow"
           data-desc="{_escape(wf.get('summary', ''))}">
    <div class="mock-cover">
      <div class="mock-cover-kicker"><img src="assets/odoo-icon.svg" alt=""/> Workflow {idx} of {total} · {_escape(wf['name'])}</div>
      <h1>{_escape(wf['name'])}</h1>
      <p>{_escape(wf.get('summary', ''))}</p>
    </div>
    <div class="mock-cover-section">
{actor_callouts}
      <div class="mock-step-list-wrap">
        <div class="mock-step-list-header-workflow">WORKFLOW</div>
        <div class="mock-step-list-header-variants">VARIANTS</div>
        <ol class="mock-step-list">
{step_list}
        </ol>
      </div>
    </div>
  </section>
'''


def _emit_placeholder_screen(wf_idx, step_idx, step_text):
    """A placeholder screen for one flow_strip step. Generator fills in the
    body composing from `components/<view-type>.html` fragments."""
    sid = f"wf{wf_idx}-s{step_idx}" if wf_idx else f"s{step_idx}"
    title = step_text[:60] if step_text else f"Screen {step_idx}"
    return f'''
  <section class="mock-screen" data-screen="{sid}"
           data-title="{_escape(title)}"
           data-desc="{_escape(step_text)}">
    <!-- SLOT: compose this screen from reference/catalog/components/<view-type>.html
         Pick the right view per reference/view_types.md (form / list / kanban /
         report / settings / portal / website / chart_views / etc.). Wrap in the
         appropriate chrome (navbar + control_panel for backend, o_website + header
         for public website). Add `data-mock-variant-axes` if this step has ≥ 2
         renderings the spec encodes; add `mock-marker` annotations for
         solution-changing elements (numbered 1, 2, 3 ... per screen). -->
  </section>
'''


def _emit_workflow_shell(idx, total, wf):
    """One `mock-workflow` div containing the overview + per-step placeholders.
    Only emitted for multi-workflow packages."""
    overview = _emit_workflow_overview(idx, total, wf)
    placeholders = "".join(
        _emit_placeholder_screen(idx, i, step)
        for i, step in enumerate(_flow_strip(wf), start=1)
    )
    return f'''
<!-- ===================== WORKFLOW {idx}: {_escape(wf['name'])} ===================== -->
<div class="mock-workflow" data-workflow="wf{idx}-{_slug(wf['name'])}" data-workflow-title="{_escape(_short_workflow_title(wf['name']))}">
{overview}{placeholders}</div>
'''


# ---------------------------------------------------------------------------
# Asset copying

def _copy_assets(out_dir):
    """Copy the 3 catalog assets + 2 brand images into <out_dir>/assets/."""
    assets_out = os.path.join(out_dir, "assets")
    os.makedirs(assets_out, exist_ok=True)
    catalog = _catalog_dir()
    for fname in ("annotations.css", "walkthrough.js", "odoo.css",
                  "odoo-icon.svg", "odoo-logo.png"):
        src = os.path.join(catalog, fname)
        if not os.path.isfile(src):
            print(f"  WARN: catalog asset missing: {src}")
            continue
        shutil.copy2(src, os.path.join(assets_out, fname))


# ---------------------------------------------------------------------------
# Main emitter

def build_index_html(spec_data):
    """Compose a complete index.html string from a SPEC_DATA dict."""
    title = spec_data.get("title", "Mock")
    summary = spec_data.get("subtitle", "") or spec_data.get("summary", "")
    workflows = spec_data.get("workflows", []) or []

    sprite = _read_catalog_file("icons.svg")
    walkthrough_bar = _read_catalog_file("components/walkthrough_bar.html")

    cover = _emit_cover(title, summary, workflows)

    if len(workflows) >= 2:
        # Multi-workflow: cover lives inside an "Overview" workflow wrapper
        # so every .mock-screen has a workflow ancestor (catches lint
        # `[WORKFLOW] mock-screen outside any .mock-workflow wrapper`).
        cover = (
            '<div class="mock-workflow" data-workflow="overview" data-workflow-title="Overview">\n'
            + cover
            + "</div>\n"
        )
        body_screens = "".join(
            _emit_workflow_shell(i, len(workflows), wf)
            for i, wf in enumerate(workflows, start=1)
        )
    elif len(workflows) == 1:
        # Single-workflow: cover at top level (no wrapper needed — the
        # lint `[WORKFLOW]` rule fires only when ≥ 2 .mock-workflow exist).
        wf = workflows[0]
        body_screens = "".join(
            _emit_placeholder_screen(0, i, step)
            for i, step in enumerate(_flow_strip(wf), start=1)
        )
    else:
        body_screens = "  <!-- SLOT: no workflows in SPEC_DATA - author screens here -->\n"

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{_escape(title)} — Odoo Mock</title>
<link rel="icon" href="assets/odoo-icon.svg"/>
<link rel="stylesheet" href="assets/odoo.css"/>
<link rel="stylesheet" href="assets/annotations.css"/>
</head>
<body>

{sprite}

{cover}
{body_screens}
{walkthrough_bar}

<script src="assets/walkthrough.js"></script>
</body>
</html>
'''


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else "")
    parser.add_argument("spec_folder",
        help="Path to the spec folder (e.g. `specifications/TEST00X - ...`).")
    parser.add_argument("--force", action="store_true",
        help="Overwrite existing index.html. Default: refuse if a non-empty mocks/ already exists.")
    args = parser.parse_args(argv)

    if not os.path.isdir(args.spec_folder):
        print(f"ERROR: spec folder does not exist: {args.spec_folder}", file=sys.stderr)
        return 2

    build_py = _find_build_py(args.spec_folder)
    if not build_py:
        print(f"ERROR: no _reference/_build_*.py found under {args.spec_folder}", file=sys.stderr)
        return 2

    print(f"Reading SPEC_DATA from: {build_py}")
    try:
        spec_data = load_spec_data(build_py)
    except Exception as e:
        print(f"ERROR loading SPEC_DATA: {e}", file=sys.stderr)
        return 1

    out_dir = os.path.join(args.spec_folder, "mocks")
    index_path = os.path.join(out_dir, "index.html")
    if os.path.exists(index_path) and not args.force:
        print(f"REFUSE: {index_path} already exists. Re-run with --force to overwrite.",
              file=sys.stderr)
        return 1

    os.makedirs(out_dir, exist_ok=True)
    _copy_assets(out_dir)

    html = build_index_html(spec_data)
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Wrote skeleton: {index_path}")
    print(f"  {len(spec_data.get('workflows', []))} workflow(s)")
    print(f"  Next: fill in the SLOT placeholders by composing screens from")
    print(f"        reference/catalog/components/*.html. Then run the lint + the")
    print(f"        mock-coverage-anchor + mock-fidelity-anchor pair before delivery.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
