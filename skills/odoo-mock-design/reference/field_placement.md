# Field placement — discover it at runtime, don't cache it

**There is no per-model cache.** Where a standard Odoo field lives (which group,
which notebook tab, the statusbar stages) is discovered **at generation time from
the actual Odoo source** in the repo's `odoo/` (Community) and `enterprise/`
checkouts. This guarantees the mock matches the *real* code present — including
module inheritance — instead of a stale, hand-maintained snapshot.

The reason placement must come from source and not memory: an Odoo form is not
one file. The effective layout is assembled by **view inheritance** — e.g.
`sale_stock` injects Warehouse into `sale.order`'s *Other Info ▸ Shipping* group,
`sale_management` adds the Quotation Template field, etc. Only the source (merged
across installed modules) is authoritative.

## "Discover from source" applies to CHROME layout too, not just field positions

The same rule governs **where structural chrome renders**, not only which group a
field sits in. Component placement drifts between major versions, and memory of
"how Odoo looks" lags the code — so verify chrome layout against source the same
way you verify a field's group. The canonical miss: **smart buttons (the
stat-button box) moved out of the form sheet into the control panel's centered
`.o_control_panel_actions` cell in Odoo 19** (`views/form/form_controller.xml`
renders `ButtonBox` into the `layout-actions` slot) — re-deriving it from memory
lands them in the sheet (the pre-17 look). When a screen's structure hinges on
*where a component lives* (button box, statusbar, pager, breadcrumb actions,
chatter side-vs-bottom), grep the relevant `web` / view template and trust the
code, not the recollection. Treat a placement you "just know" as a hypothesis to
confirm against source before composing the screen.

## Don't invent composite fields

Odoo forms render **discrete fields**, not composite labels invented by
the mock. If `stock.picking` has `location_id` and `location_dest_id`
as two separate Many2one fields, the mock shows them as two separate
`<div class="o_field_row">` entries — **not** as a fused `From → To`
label with both values mashed into one cell. The composite reads as
"the consultant designed a new chrome convention that doesn't exist in
Odoo," which it didn't.

Same rule for any field pair you're tempted to fuse for visual economy
(`partner_id` + `partner_shipping_id` are two rows, not one
"Customer + Shipping" composite; `date_order` + `commitment_date` are
two rows, not "Order → Delivery"). When in doubt, grep the model's
form view in `odoo/addons/<app>/views/` — every `<field name="...">`
is its own row.

The single exception: small Odoo helpers that wrap two fields in a
single `<div class="o_row">` (e.g. percentage + unit, or qty + UoM).
Those are explicit patterns in source, not invented.

## Step 0 — source-availability check + WARNING

Before deriving any standard screen, check what's present:

- `odoo/` (Community source) — required for faithful base screens.
- `enterprise/` — required for enterprise-only models/fields (accounting
  extensions, subscriptions, field service, etc.).

Then:

- **Both present** → derive from source (below). Note in the plan which trees
  were read.
- **Community only** → derive from `odoo/`, and **warn**: enterprise-only fields
  / pages won't appear, so enterprise screens may differ from reality.
- **Neither present** → **STOP and warn the user explicitly**, e.g.:

  > ⚠ Odoo source (Community/Enterprise) was not found at `odoo/` / `enterprise/`.
  > Field placement and screen structure are **best-effort and may not match real
  > Odoo**. Provide the checkout for faithful screens, or treat these mocks as
  > approximate.

  Then proceed with a generic, view_types-based layout from the brief — but the
  caveat stands and should also be surfaced on the mock's cover screen so anyone
  who opens it knows the screens are approximate.

## Discovery recipe (per standard model)

For each screen that represents a standard model:

1. **Find the primary form view.** Grep the source for the model's form record,
   e.g. the `<field name="model">sale.order</field>` form arch, or the known
   `*_views.xml` under the owning module
   (`grep -rl 'view_order_form\|model">sale.order' odoo/addons enterprise`).
2. **Resolve inheritance.** Grep for views that inherit it — `inherit_id` on the
   model plus `position="…"` / `xpath` snippets across `odoo/addons/*/views/` and
   `enterprise/*/views/`. Merge them mentally into the effective arch (this is
   what adds module-specific fields like Warehouse).
3. **Extract the structure** the catalog needs:
   - Statusbar stages (`<field name="state" widget="statusbar" statusbar_visible="…">`)
     and their label↔state mapping.
   - Header workflow buttons; corner `web_ribbon` states.
   - Smart buttons (`oe_button_box`) — defined inside the form arch, but in
     Odoo 19 they RENDER in the control panel's centered `.o_control_panel_actions`
     cell (the OWL `layout-actions` slot), not in the sheet. Mock them there.
   - Main `<sheet>` groups — left / right, field label ↔ field name, in order.
   - `<notebook>` pages in order and which fields/groups sit on each.
   - Chatter presence (`<chatter/>` / mail mixin).
4. **Place accordingly.** Standard fields the brief doesn't change go exactly
   where source puts them (e.g. `sale.order` Warehouse & Salesperson on *Other
   Info*, never the main sheet — the most common fidelity bug). Use
   `view_types.md` + `style_guide.md` for *styling*; use source for *placement*.

## Custom fields and custom models

- **Solution-added fields on a standard model** — any field the addon adds,
  including stored / computed / **related** (`related='foo_id.bar'`) /
  **relational** (`Many2one` / `One2many` / `Many2many`, plus reverse
  relations), as well as standard fields the addon overrides with a new
  compute / default / domain / readonly / required — are placed by judgment
  into the group/tab their meaning fits and earn annotation markers (they're
  the solution's delta). Flag each with a custom-field help **"?"**
  (`.o_field_help`) carrying its attributes (`data-field` / `data-model` /
  `data-type` / `data-help`) so the developer audience sees what's new — see
  `reference/interactions.md` § Custom-field help. Do not skip the `?` because
  the field's `data-type` is `many2one` / `one2many` / `many2many` or because
  the value comes via `related=`: the *exposure* on this view is what the
  solution adds, and that's what the `?` documents.
- **Entirely custom models** have no source ground truth; compose from
  `view_types.md` anatomy + the brief. Placement is sensible-Odoo-shaped by
  design, not a fidelity claim.
