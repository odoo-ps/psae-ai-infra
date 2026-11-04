# Web assets: JavaScript, OWL templates, SCSS

*Calibrated against Odoo 19.0 and 20.0. Re-review on each major version bump — see [release cadence runbook](../release_cadence.md).*

For code under `static/src/` and `static/tests/`. Vendored libraries in `static/lib/`
and images in `static/description/` follow only the asset rules below. Frontend logic
stays thin: business rules live in guarded server methods (the QA and
solution-architect checklists, plan-dev Stage 3c).

## Files and assets

- Organise by **feature**, not by type: one folder per feature holding its component,
  template, styles and service (`library_return/return_dialog.js`, `.xml`, `.scss`), not
  `components/`, `services/`, `hooks/` folders.
- Every resource ships in the addon: copy images, fonts and libraries in; never link a
  CDN or an external URL. Third-party code goes in `static/lib/`, unminified, so it can
  be read and diffed.
- Files join bundles only through the manifest's `assets` key ([`manifest.md`](manifest.md)).

## JavaScript

- Prefer a plain function, or an OWL `computed` for derived state, over a getter: the call
  site shows that code runs, and a `computed` recomputes only when its inputs change.
- **Patching is allowed in a client addon.** Odoo discourages `patch()` inside its own
  code base; outside it, patching core components is the normal way to extend them. Keep
  each patch small, name what it patches, and re-check it when the target version moves
  (patched code drifts from its target).
- Escaping: render user text with `t-out`; build HTML only from literals
  (`markup` tagged templates). Sinks (`innerHTML`, `insertAdjacentHTML`, `markup(str)`)
  never receive user strings. See [`security.md`](../role_checklists/security.md).

## OWL templates

- `t-out` everywhere ([`views_and_data.md`](views_and_data.md) § QWeb output has the
  per-version table).
- **v20 ships OWL 3** with a compatibility layer for OWL 2 code. When moving code from
  v19, see `odoo-version-upgrade` catalog entry 19-20.15 (`owl3-migration`).
- **v20 icons are Material Symbols** (`<i class="oi" data-icon="check"/>`, button
  `icon="check_box"`); FontAwesome classes render empty (catalog 19-20.37).

## SCSS

- 4-space indent, about 80 columns, one declaration per line, brace on the selector line.
- Order properties outside-in: position and layout first, decoration (`font`, `filter`)
  last. Scoped variables at the top, then a blank line.
- Classes: `o_<module>_<element>`, flat (`o_library_entry`, not mirroring the DOM
  nesting); no `id` selectors. Classes use underscores; SCSS variables, mixins and
  functions use hyphens (`$o-library-entry-padding`, `@mixin o-library-card`).
- Global design through SCSS variables; CSS custom properties only for contextual
  adaptation, never on `:root`.
