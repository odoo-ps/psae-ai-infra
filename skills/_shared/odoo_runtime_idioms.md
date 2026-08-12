# Odoo Runtime & Interaction Idioms

*Calibrated against Odoo 19.0. Re-review on each major version bump.*

The defects this file prevents share one trait: **they pass static lint, install, and the generic smoke, and only surface when a human drives the live UI.** Valid XML + a clean `-i` + a passing operational smoke does **not** mean the interaction is correct. Consult this list whenever the addon ships a wizard, an editable list, an inline action button, a status indicator, or a guard on a committed value.

This is a checklist of *gotcha → right pattern*, not a tutorial. The `solution_architect` and `ux_ui` role checklists reference it; the matching failure modes have entries in [`troubleshooting.md`](troubleshooting.md).

---

## Transient wizards (`TransientModel`)

- **A `raise` in a wizard button blanks the dialog.** The web client `web_save`s the transient record *before* calling the button method; if the method raises, the transaction rolls back — including the just-saved lines — and the dialog re-renders **empty**. So a save-time `UserError` for *recoverable* input (over-quantity, etc.) reads as "the wizard wiped itself," not as an error.
  → **Cap-and-warn in `@api.onchange` instead.** Correct the value in place and return `{'warning': {...}}`. Keep a save-time `raise` only as a backstop for genuinely-invalid states that the UI prevents reaching.
- **A wizard edits transient records; persist back explicitly.** `default_get` pre-fills from the real records; the save method writes back with `Command.clear()` + `Command.create(...)`. Don't assume the o2m auto-persists to the source model.

## `@api.onchange`

- **Don't naively sum sibling x2many rows in a per-row onchange.** Reading `self.<parent>.<line_ids>` from within a line's onchange double-counts: the current row appears both as `self` and in the parent set, and the editable list's blank "new" row (default values populated) is also present. Summing all rows produced false "over-allocated" warnings on the *first* entry.
  → **Filter to exclude self and lot-less/blank rows** — e.g. sum only rows with a different identifying key (`lot_id != self.lot_id`), which drops both the current-row duplicate and the not-yet-filled blank row.
- **`onchange` is UI-only.** It never fires from `create`/`write` via RPC, import, or automated actions. Invariants that must always hold go in `@api.constrains`; `onchange` is for in-client capping/warning/autofill.

## Editable lists & inline buttons

- **A `<button>` between field columns shifts every following header.** Button cells emit no header `<th>`, so each field column to its right inherits the *previous* column's header — the status badge ends up under the wrong label.
  → Place row-action buttons **last** in the list, or give the button an explicit `width=` (supported: `<button icon="fa-heart" width="25px"/>`). Then only one column (a width-less text field) flexes.
- **The trailing no-width column absorbs all slack** → a stretched blank gap before the row's delete control. Give numeric/icon columns explicit `width=`; leave one text column width-less to take the remainder.
- **`create`/`delete` on a `<list>` are static, not per-row.** You cannot conditionally allow add/delete per record via list attributes. To lock a *specific* record's operations, make the **o2m field `readonly`** (driven by a computed boolean on the parent) — a readonly o2m has no "Add a line" and no trash, for that record only.

## Icons, decorations & indicators

- **Colour a button's FontAwesome icon via the `icon` attribute, not `class`.** `icon="fa-warning text-warning"` renders coloured; `class="text-warning"` on the button is overridden by button styling → the icon shows grey and only tints on hover. (Core: `stock_orderpoint_views.xml`.)
- **Status vs action.** A purely informational marker (a warning/exception glyph) should be **passive** — a `decoration-*` colour on the cell, or a tooltip'd non-interactive cue — not a clickable button that pops a notification. Reserve buttons for actions. If a conditional icon must be a `<button>`, give it a no-op handler + a `title=`, and bound its `width`.
- **Helper/explainer text is conditional.** Show a warning banner only when its condition holds (`invisible="not <flag>"`), via a computed flag on the wizard/record — an always-on caption dilutes the real signal.
- **Labels adapt to the data type.** A button naming a concept ("Select Lots") is wrong for a record of a different type ("Select Serials" for `tracking == 'serial'`). Use two type-gated buttons (`invisible="lot_tracking != 'lot'"` / `'serial'`) or a computed label; the dialog title can branch in the action method.

## "Pick From" and non-obvious mutation paths

- **`stock.move.line.quant_id` ("Pick From") is a non-stored dummy field** whose onchange rewrites `lot_id`/location/quantity, and the picker can **create** a new move line rather than write the existing one. A guard that only blocks `write`/`unlink` of `lot_id` misses this entirely.
  → When locking a committed value, enumerate **every** mutation path — `write`, `create`, `unlink` — plus dummy/onchange-driven fields, barcode, and import. Guard at the model layer **and** remove the UI control (see editable-lists, above).

## Reservation & availability semantics (`stock`)

- **`stock.quant._get_available_quantity` = on-hand − reserved**, and *reserved* includes **this document's own** reservation. So a correctly-booked confirmed line reads as a *shortage* (available 0) if you compare its allocation against raw availability.
  → When asking "can my committed lot still be obtained," **add back this line's own reservation** (`move_ids.move_line_ids.quantity_product_uom` for that lot, non-done/cancel) and subtract only *other* documents' claims.
- **Reservation should honour the commitment, not the removal strategy.** If the addon pins specific lots, override `_action_assign` so a committed move re-reserves **its committed lots** (not FIFO). One reusable method, called from both the confirm hook and `_action_assign`, makes Unreserve → Check-Availability restore the correct lots — the release always has a restore.

## Guards vs system flows

- **A `write`/`create`/`unlink` guard protecting committed data also fires from the system's own flows** — cancel → `_do_unreserve` → `unlink`, validation writing done qty, backorder splits. A guard that doesn't exempt them blocks cancellation and shipping.
  → Exempt system-initiated operations via a trusted-operation context flag (e.g. override `_do_unreserve` to run `with_context(<flag>=True)`); block only the manual edit path. Validation writes `picked`/quantity (not `lot_id`), so a guard scoped to the *identifying* field leaves validation working.

## Cross-document contention (when a finite resource is claimed pre-confirmation)

- A quotation-time claim does not reserve stock (reservation is at confirmation), so two quotations can claim the same unit; the second fails late, at its confirm.
  → If contention matters, **gate availability by other open documents' claims** (a soft hold) and tie the hold to a **release valve** (the document's expiry / cancel) so a never-followed-up document can't hog the resource. Keep the soft hold as a UI booking gate; the hard reservation still happens at confirmation. Batch the cross-document lookup (`read_group`), never per-row.

## POS / OWL frontends (`point_of_sale`, `static/src`)

The whole surface is invisible to Stage 1/2/3 and `--test-tags` — only a human driving a live POS session exercises it. The defects here aren't caught by *any* automated stage; the discipline is to make the JS thin and prove the rest server-side. Calibrated against Odoo 19 source (`point_of_sale`, `pos_loyalty`).

- **Put zero business logic in the JS.** Every guard, state transition, and `sudo` escalation lives in a server method the popup *calls*; the OWL layer only collects input and renders the result. Unverifiable JS logic is also bypassable.
- **JS→server call convention.** `this.pos.data.call(model, method, args, kwargs)` maps to `env[model].browse(ids).method(*rest)`:
  - **Non-`@api.model`** method (operates on a record): pass a **leading ids list** — `pos.data.call("tradein.appraisal", "accept_device", [[id], finalValue, managerId])` → `browse([id]).accept_device(finalValue, managerId)`. A method that `self.search(...)`es works on an empty recordset: pass `[[], ref]`.
  - **`@api.model`** method: pass args directly with **no** leading ids — `pos.data.call("loyalty.card", "get_gift_card_status", [code, configId])`.
  - Don't change a core method's decorator just to call it from POS; pick the matching arg shape instead.
- **Frontend extension points (no control-button registry in v19).** Add a control button by `patch(ControlButtons.prototype, {...})` + a `t-inherit="point_of_sale.ControlButtons"` XPath template. Open a popup with `makeAwaitable(this.dialog, MyPopup, {...})` (from `@point_of_sale/app/utils/make_awaitable_dialog`); the popup is an OWL `Component` with `static components = { Dialog }` and `setup(){ this.pos = usePos(); }` (`usePos` from `@point_of_sale/app/hooks/pos_hook`). Order helpers: `order.setPartner(partner)`, `this.pos.models["res.partner"].get(id)`, `this.pos.data.read(model, ids)`.
- **Assets bundle.** Register JS/XML/SCSS under `point_of_sale._assets_pos` (a `tradein_management_pos/static/src/**/*` glob is fine). Style with theme vars (`var(--o-...)`) + logical properties (`inline-size`, `margin-block`) so the popup is dark-mode / RTL safe.
- **Reuse the standard mechanism, don't reinvent.** eWallet credit redeems through `pos_loyalty`'s existing reward flow once the partner is set on the order — mint the `loyalty.card` server-side, set the partner, and let standard POS apply it. Same for gift cards, coupons, promotions.

## Financial reports (`account.report` custom handler — Enterprise `account_reports`)

A custom financial report is **data + a Python handler**, not a normal model. The engine lives in `enterprise/account_reports`, so the feature is **Enterprise-only** — confirm edition before building. Calibrated against Odoo 19. Reference handlers: `account_cash_flow_report.py` (dynamic lines), `account_aged_partner_balance.py` (dynamic columns + period bucketing). Matching troubleshooting: #60 (AbstractModel/ACL) and #61 (dynamic columns).

- **The handler is an `AbstractModel`** (`_inherit = ['account.report.custom.handler']`): no DB table, **no `ir.model.access.csv` row** (real enterprise handlers ship none), and it must **not be searched** — `search([])` on it raises `relation "..." does not exist`. Static lint and operational smoke must skip `_abstract` models; for any custom probe, gate on `env[model]._abstract`. Don't add a bogus ACL to silence a linter.
- **The report is an `account.report` data record** with `custom_handler_model_id` → the handler. A pure-handler report has **no `line_ids`** in XML — every line comes from `_dynamic_lines_generator`. Define only `column_ids`.
- **Dynamic lines:** `_dynamic_lines_generator(self, report, options, all_column_groups_expression_totals, warnings=None)` returns `[(sequence, line_dict), …]`. Build each `line_dict['columns']` by iterating `options['columns']` and calling `report._build_column_dict(value, col, options=options, currency=...)`; the line id is `report._get_generic_line_id(None, None, markup='my_marker')`. Key shape: `{id, name, level, columns, unfoldable, unfolded}`.
- **Variable column count (N period/date buckets):** the engine reads columns from the static `column_ids`. For a runtime-variable count, declare the **MAX** columns in XML (e.g. `opening` + `b1..b13`, each with `expression_label` + `figure_type="monetary"`), then in `_custom_options_initializer` **rename** the headers and **filter** `options['columns']` down to the active count. Don't try to mint columns from scratch at runtime.
- **Bucketing by date — dodge the locale week-start trap.** Bucket by **rolling windows from today** (`today + i*step`), not SQL `date_trunc('week')` (which forces ISO Monday regardless of locale). Render every bucket/period header with locale-aware `format_date(self.env, d)`, never a raw `strftime`. Wrap handler-built line/warning strings in `_()`.
- **Performance at scale** (open AR/AP can be 10k–100k lines): bucket with **one grouped query** (a `CASE`-over-date-ranges or a period-CTE like aged-partner-balance), never per-record Python loops; compute the opening position as one aggregated query over the configured cash accounts. A two-column `COALESCE(expected_date, date_maturity)` bucket key is **not sargable** on a single-column index — add an expression index or split the predicate.
- **Surface it** with `ir.actions.client tag='account_report'`, `context={'report_id': ref('my_report')}`, and a `menuitem` under `account.account_reports_legal_statements_menu` (or `…_partners_reports_menu`), `groups="account.group_account_readonly,account.group_account_basic"`.
