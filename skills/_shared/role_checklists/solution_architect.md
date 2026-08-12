# Solution Architect — Technical Spec

*Calibrated against Odoo 19.0. Re-review on each major version bump.*

## Goal
Decide how each user story maps to Odoo primitives — models, fields, views, methods — minimising new code and maximising reuse of standard Odoo.

## Key Questions to Ask the User
- For each new piece of data: **extend an existing model** (`_inherit`) or **introduce a new model**?
- For each new screen: **inherit and xpath** an existing view or **define a fresh one**?
- Does the workflow need a **state machine** (`fields.Selection` + transition methods) or is it stateless?
- Are computed fields **stored** (queryable, indexable) or **on-the-fly** (no DB column, no search)?
- What's the **manifest version** strategy — major bump or patch?
- Could **Studio** cover this surface? Custom code is the fallback when Studio's limits bite (per-line conditions on approval rules, complex compute logic, server-side validation across records); for view tweaks + automated actions + simple approvals, Studio is often the right answer.
- For new UI: **OWL component** or extend a legacy widget? OWL is the default for Odoo 17+; legacy widgets remain for surface tweaks on existing views.
- Does the change introduce a **state, lock, reservation, or commitment**? If so: what **releases** it, what **restores** it, and what does **cancel / expire / done** do to it? (principle #15)
- To make a field/record **immutable to a role**: which mutation paths exist — `write`, `create`, `unlink`, plus dummy/onchange-driven fields (e.g. `stock.move.line.quant_id` "Pick From")? A view `readonly` is *not* enforcement.
- For any **"available / remaining / free"** figure: whose reservations does it include vs exclude (this document's own vs other documents')?

## Dependency & configuration discipline (mandatory for every addon)

Before declaring the technical spec done, produce two lists in the plan file
(see SKILL.md Section B):

1. **Module dependencies** — every model the addon touches resolved to its
   owning module. Don't lean on transitive deps from a high-level "umbrella"
   module (`sale_stock` pulling `sale`); list each module the addon *directly*
   uses, with a one-line "why" so the user can spot gaps at `ExitPlanMode`.
2. **Required configuration / feature groups** — every `res.config.settings`
   toggle or `res.groups` flag the addon's workflow depends on. The test:
   *"if I install this addon in a freshly-created DB with only `base` and the
   `depends` modules loaded, does every field, view, button, and computed
   actually function?"* If the answer requires the operator to flip a toggle
   in Settings, that toggle goes in the **Required configuration** list with
   the group's `xml_id` and the UI path. Either bake the toggle into a
   `post_init_hook` (preferred when the addon is non-functional without it) or
   document it in the manuals.

The yoa_test failure mode is the canonical miss here: an addon depending on
`sale_stock` but using lot/serial fields needs `stock.group_production_lot`
enabled, otherwise the addon installs but its core field is invisible.

## Lifecycle, locks & contention discipline (when the change commits / locks / reserves)

Per principle #15. If the addon introduces a state, lock, reservation, or
commitment on a resource, the plan answers each of these — folded into the
relevant design sections, or explicitly `N/A` when the change introduces no such
resource:

1. **Inverse paths.** Every commit / lock / reserve has a defined **release**
   (free it) and **restore** (re-apply it). A reservation pinned at confirmation
   must survive Unreserve → Check-Availability (re-pin to the committed value),
   and Cancel must free it. A release with no restore is incomplete.
2. **Terminal-state cleanup.** Cancel / expire / done releases what was held —
   frees the stock reservation *and* clears the commitment record where the order
   ships nothing.
3. **Mutation-path lockdown.** To stop a role altering a committed value, guard
   **every** write path at the model layer — `write`, `create`, *and* `unlink` —
   not just `readonly` in one view; and **remove the UI control** (make the
   list/o2m non-editable) rather than leaving a control that only errors on save.
   Enumerate non-obvious paths: dummy fields (`quant_id` "Pick From"),
   onchange-driven writes, barcode, import.
4. **Guard ≠ break the system.** A guard protecting a committed value must exempt
   the legitimate system flows that traverse the same code (cancel → unreserve →
   `unlink`; validation writing done qty). Block the *manual* path; pass a
   trusted-operation context flag through the system path.
5. **Contention.** If a finite resource can be claimed by more than one document
   *before* confirmation, decide whether claims gate each other (soft-hold) and
   what **releases a stale hold** (expiry / cancel) so it can't be hogged
   indefinitely.

## Mechanisms / Tools
- Default rule: prefer `_inherit` over a parallel model when the relationship is "is a kind of".
- Default rule: prefer `_inherits` (delegation) over `_inherit` when the new model has its own lifecycle but reuses fields.
- For view changes: write the smallest `<xpath expr="..." position="...">` that achieves the goal. Avoid `replace` unless absolutely necessary; prefer `after`/`before`/`inside`/`attributes`.
- Resolve every model reference to its owning module before adding to manifest `depends`. Run `../scripts/_check_odoo_source.py --models <list>`.
- For each new model, decide `_log_access`, `_order`, `_rec_name` deliberately — defaults are usually right but worth one sentence each.
- **`Command.create` / `Command.update` / `Command.link` for x2many writes** (Odoo 17+ idiom; replaces legacy `(0, 0, {...})` / `(1, id, {...})` / `(4, id)` tuples):
  ```python
  order.write({"order_line": [
      Command.create({"product_id": product.id, "product_uom_qty": 5}),
      Command.update(existing_line.id, {"product_uom_qty": 10}),
      Command.link(another_line.id),
      Command.unlink(stale_line.id),
  ]})
  ```
  Mixing the tuple form and the `Command` form in the same call works but reads as legacy code. Pick one — `Command` for new code.
- **`@api.constrains` (server-side) vs `@api.onchange` (UI-only)**: `@api.constrains` runs on every write/create at the ORM layer — fires from any code path (ORM, RPC, imports, UI). `@api.onchange` runs ONLY in the web client when a user edits the form — does NOT fire from imports, automated actions, or RPC. Use `constrains` for invariants that must always hold; `onchange` for UX hints / autofill that only matter when the user is typing.
- **`_check_company` decorator** for multi-company integrity: applied to `Many2one` fields that reference another model with `company_id`, validates that the target record's `company_id` matches the source record's. Example: a sales order's pricelist must belong to the same company as the order; a `_check_company`-decorated `Many2one("product.pricelist", check_company=True)` enforces it.
- **OWL component model** (Odoo 17+ default) for new interactive UI. OWL components live under `<addon>/static/src/` and register via the registry pattern. Legacy QWeb widgets still work for extending existing views, but new UI surfaces (custom views, dashboards, complex forms) should be OWL.
- **POS / OWL frontends: keep the frontend thin, the server methods fat and guarded.** A POS control button, popup, or any `static/src` OWL component is INVISIBLE to lint, install, and operational smoke — only a human in a live session exercises it. So every guard, state transition, and `sudo` escalation must live in a server method the OWL layer merely *calls* (`this.pos.data.call(model, method, [[ids], ...args], {kwargs})` → `browse(ids).method(*args)`), never in the JS. That keeps the business logic provable by module tests + a server-method shell smoke even though the UI itself is manually checked. See [`../odoo_runtime_idioms.md`](../odoo_runtime_idioms.md) § POS / OWL frontends.
- **Custom financial reports are `account.report` (data) + an `AbstractModel` handler — Enterprise only.** A custom report extends the `account_reports` engine (Enterprise; confirm edition before designing). The handler subclasses `account.report.custom.handler` as an `AbstractModel` — no table, **no ACL row**, never searched. Define columns in the `account.report` XML (no `line_ids`); emit lines from `_dynamic_lines_generator`; build dynamic period/bucket columns by declaring a static MAX and renaming/filtering in `_custom_options_initializer`. See [`../odoo_runtime_idioms.md`](../odoo_runtime_idioms.md) § Financial reports.
- **A workflow that touches POS gets its own `*_pos` module, depending on core; core never depends on `point_of_sale`.** Put ALL `point_of_sale` / `pos.order` references and the POS-cashier ACL in the satellite module (extend the core model via `_inherit`). One-directional pos→core keeps the core addon installable and fully testable standalone, and avoids the dependency cycle a shared `pos.order` Many2one in core would create.
- **`pre_init_hook` vs `post_init_hook` vs migration scripts boundary**:
  - `pre_init_hook` — raw `cr` only, ORM NOT loaded. Use for schema work that must happen before models load (rare).
  - `post_init_hook` — ORM available. Use for one-time setup on FRESH install (gate with idempotency check: "only run if X doesn't exist yet"). Fires on every `-i` AND every `-u` — without a gate, it re-runs on every upgrade.
  - `<addon>/migrations/<version>/post-...py` — fires on `-u` when the manifest version increments past `<version>`. Use for *version-bumping* data changes; `post_init_hook` is for *install-time* setup.
  Picking the wrong one: a `post_init_hook` for what should be a migration runs unconditionally on upgrades and re-applies. A migration script for what should be a `post_init_hook` doesn't run on fresh install.
- **Studio-vs-code boundary**: Studio handles view tweaks, simple computed fields, automated actions, approval rules, and most "add a field, hide it conditionally, send mail" flows. Custom code is the right tool when: (a) the compute is non-trivial Python; (b) the approval needs per-line gates Studio can't express; (c) the workflow has cross-record state transitions; (d) the addon needs to ship as a deployable artifact to multiple tenants. Default to Studio; reach for code when the Studio limit is real.
- **Reservation / lock primitives are reusable, not confirm-only.** Put "(re)apply the commitment" in ONE method called from BOTH the confirm hook AND `_action_assign` (Check Availability), so a release always has a restore. A confirm-time-only re-pin leaves no way back after a manual unreserve.
- **Availability reference frame.** `stock.quant._get_available_quantity` = on-hand − reserved, and *reserved* includes this document's own reservation. To answer "can my committed lot still be obtained," **add back this line's own reservation** and subtract only *other* documents' claims — otherwise a correctly-booked confirmed line reads as a shortage.

## Common Pitfalls
- **Reaching into other addons' private methods** (`_compute_*`, `_*_implementation`). They're private for a reason; wrap a public helper if needed.
- **Cross-module circular deps** — if module A's manifest depends on B and B's view xpath references A's field, you have a cycle. Refactor.
- **Storing what should be computed** (e.g. `total = unit_price * qty`). Storing duplicates state and rots silently.
- **Computing what should be stored** when the field is searched/grouped/sorted often. Compute-on-the-fly is fine for display, terrible for `search([("total", ">", 100)])`.
- **`@api.depends` on a relational field** without the chain — `@api.depends("partner_id")` does NOT re-trigger when `partner_id.name` changes. Use `@api.depends("partner_id.name")`.
- **Renaming an existing field** in an `_inherit` — breaks any external reference (reports, automated actions, exports).
- **Mixing legacy x2many tuples with `Command` form** — both work but the codebase reads as half-migrated. Pick the `Command` form for new code; refactor adjacent tuples in the same edit.
- **`@api.onchange` for an invariant that must always hold** — onchange only fires in the web client; imports and RPC writes skip it. Use `@api.constrains` for invariants.
- **`Many2one` to a company-scoped target without `_check_company`** — cross-company data leaks silently. The check_company decorator is one line and prevents the failure mode entirely.
- **`post_init_hook` without an idempotency gate** — re-runs on every `-u`, re-applies whatever it does. Always guard: `if not env['my.model'].search([], limit=1):` (or equivalent state check).
- **Building custom what Studio handles** — wasted dev cycles on view tweaks Studio does in 5 minutes. Try Studio FIRST; reach for code when Studio's limit is concrete.
- **A commit / lock / reserve with no inverse** — reserves but never frees, locks but never unlocks, or a terminal state (cancel/expire) that strands the held resource. Incomplete per principle #15.
- **`readonly` mistaken for enforcement** — a view-only readonly leaves `create` / import / RPC paths open and still shows Add/Delete controls that merely error on save. Lock at the model (write+create+unlink) AND remove the control.
- **A guard that blocks its own release path** — e.g. an `unlink` guard that also blocks cancel → unreserve. Exempt system flows via a trusted context; block only manual edits.
- **Business logic in the OWL / JS layer** — a guard or state change implemented in a POS popup's JS is unverifiable (no automated stage drives it) and bypassable. Push it to a guarded server method the frontend calls.
- **Availability that counts your own reservation as unavailable** — `on-hand − reserved` flags a correctly-booked confirmed line as short. Add back the line's own reservation.

## Production-readiness criteria
- [ ] Every new model has `_name`, `_description`, `_order`, `_rec_name` decided.
- [ ] Every model used in code is declared in manifest `depends` (via its owning module).
- [ ] No `_inherit` of a model whose owning module isn't a declared dep.
- [ ] **Each declared `depends` entry is verified installed in the validation DB before Stage 2** (per SKILL.md Section B.1).
- [ ] **Required feature groups / `res.config.settings` toggles are listed under a `Required configuration` heading and either enabled via `post_init_hook` or documented in the manuals.**
- [ ] No computed field with `store=True` lacks a tested `@api.depends`.
- [ ] State machine has at least one transition method per transition (no setting `state` directly from views).
- [ ] View inheritance uses minimal xpath — no `position="replace"` of a stable upstream view without a comment explaining why.
- [ ] Every state / commit / lock / reservation the change introduces has a defined release **and** restore; terminal states (cancel/expire/done) free what they held — or the lifecycle section is `N/A` (no such resource). (principle #15)
- [ ] To make a value immutable to a role: `write` + `create` + `unlink` all guarded at the model layer AND the UI control removed; system flows (cancel / unreserve / validate) exempted via a trusted context.
- [ ] Any "available / remaining / free" computation states whose reservations it includes; the self-vs-others boundary is correct.
