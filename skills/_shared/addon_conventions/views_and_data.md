# Views, data records and QWeb

*Calibrated against Odoo 19.0 and 20.0. Re-review on each major version bump — see [release cadence runbook](../release_cadence.md).*

UI behaviour that passes install but breaks in use (wizards, editable lists, icons,
indicators) is in plan-dev's [`odoo_runtime_idioms.md`](../../odoo-plan-development/reference/odoo_runtime_idioms.md);
search-view and view-type gotchas are in its troubleshooting file.

## Records

- `id` before `model`. Inside a `<field>`: `name` first, then the value (body or `eval`),
  then the other attributes. Group records by model.
- Prefer the sugar tags `<menuitem>`, `<template>` and `<asset>` over raw `<record>`.
- **An `active` attribute on `<template>` or `<asset>` applies at creation only.** On
  `-u` the arch updates but `active` does not change (`tools/convert.py`, v19 `:517,574`,
  v20 `:539-546, 596-603`), so an update can never deactivate an already-installed
  template. Deactivate through a `migrations/` script, or a `<field name="active">`
  inside the record.
- `noupdate="1"` only for data the user may edit afterwards (sequences, default
  parameters, mail templates meant to be customised). When the whole file is
  non-updatable, put `noupdate="1"` on `<odoo>` and drop `<data>`.
- External-id patterns: [`module_structure.md`](module_structure.md) § Naming.
- CSS classes in views and templates start with `o_<module>_` (`o_` alone belongs to the
  web client); never style through ids.

## Inherit views by name, never by position

Anchor an inheritance on a **stable, identifying attribute** (an element's `name`),
never on document position.

```xml
<!-- good: shorthand, matches the field by name -->
<field name="partner_id" position="after">
    <field name="return_date"/>
</field>

<!-- good: xpath when the shorthand can't express it -->
<xpath expr="//page[@name='other_info']//field[@name='user_id']" position="attributes">
    <attribute name="readonly">1</attribute>
</xpath>

<!-- bad: lands on the wrong element the day the parent view changes -->
<xpath expr="//group[2]/field[3]" position="after">
    <field name="return_date"/>
</xpath>
```

- The shorthand `<field name="x" position="…">` matches the **first** field named `x`
  at any depth, embedded subviews included. Use an xpath when the name recurs, for
  example in a one2many's inline list.
- Any other shorthand tag matches the first node with that tag carrying all the given
  attributes with equal values.
- An inheriting view reuses the parent's id in its own module and takes the name
  `<parent name>.inherit.<module>`. A variant (not an extension) sets `mode="primary"`.
  Don't re-add fields the parent already shows.
- Check the anchor exists **in the target version's** parent view before writing it.
  `odoo-version-upgrade`'s scanner flags anchors missing from the target.

## QWeb output

| Directive | v19 server QWeb | v20 server QWeb | v19 OWL 2 (static/) | v20 OWL 3 (static/) |
|---|---|---|---|---|
| `t-out` | escapes; renders `Markup` raw | escapes; renders `Markup` raw | escapes; renders `markup()` raw | escapes; renders `markup()` raw |
| `t-esc` | deprecated alias, escapes | **not compiled: renders nothing** | deprecated alias, escapes | deprecated alias, escapes |
| `t-raw` | raw HTML (XSS risk) | **not compiled: renders nothing** | deprecated alias of `t-out` (warns) | **removed** |

Write `t-out` on every version: it is the only directive that works everywhere. Raw HTML
is a `Markup` value built from trusted literals, never a directive (security rules in
[`security.md`](../role_checklists/security.md)). The v20 directive list
(`ir_qweb.py` `_compile_directive_*`) has no `esc` and no `raw`; v19's has both. OWL:
v19's `web/static/lib/owl/owl.js:5284-5292` maps `t-raw` onto `t-out` with a warning;
v20's OWL 3 has no `t-raw`.

## QWeb PDF reports

- A custom `_get_report_values` must return `docs` / `doc_ids` / `doc_model` itself when
  the template uses them; they are not added for you.
- Translate a report with `t-lang`, which is only valid on a node that also carries
  `t-call` (elsewhere it raises `SyntaxError` at compile, `ir_qweb.py` v19 `:2649`, v20
  `:2738`). To translate part of a report, move that part into its own template and
  `t-call` it with `t-lang`.
- Layout and PDF-rendering gotchas (wkhtmltopdf, paper formats, fonts) are in plan-dev's
  troubleshooting file.
