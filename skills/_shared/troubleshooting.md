# Odoo addon implementation — Troubleshooting

Lookup index of known failure modes — symptom-first, four lines each. Read before generating; consult when a new error appears (grep the literal error string here first). See [`troubleshooting-archive.md`](troubleshooting-archive.md) for fixed/obsolete entries.

**Migration note (2026-05-20):** This file was reformatted from a 528-line append-only log to a sectioned lookup. ID numbers do NOT match the legacy numbering — old plans referencing "troubleshooting #N" by number need rewiring against this file's IDs or against the archive.

**Write gate (per principle #6):** A new entry only lands if the skills tree is git-cloned AND the user has push access, OR if the skills tree is not git-cloned at all. Otherwise surface the proposed entry to the user without writing. The full check + rationale lives in [`principles.md` § 6](principles.md).

**Update protocol (per principle #6, after the write gate has passed):**
1. Before appending: grep this file for the literal error string. If an entry exists, update its `Last confirmed` date and refine `Cause`/`Fix` if the new occurrence taught something — don't duplicate.
2. New entries take the next free integer in the global ID space (highest active or archived ID + 1). IDs are never reused, even after archive.
3. When the file exceeds 250 lines or 35 active entries, prune (move fixed-for-90+-days entries to archive, retire whole version-specific sections when a major version is no longer supported, promote recurring patterns to principles/role checklists).
4. Run `scripts/_lint_troubleshooting.py` after editing — it validates entry shape, flags duplicate IDs, and reports archive candidates.

---

## Install (Stage 2)

### 1. Manifest declares `data: ["views/x.xml"]` but the file is missing
Applies: all versions. Status: active. Last confirmed: 2026-05-20.
Cause: Typo in manifest, or the file was deleted without updating `data`.
Fix: Remove the entry from `data` or restore the file. Stage 1 lint walks every `data`/`demo` entry and `os.path.exists`-es it — runs first.

### 2. New model installs but is invisible to all non-admin users
Applies: all versions. Status: active. Last confirmed: 2026-05-20.
Cause: No row in `security/ir.model.access.csv` for the new model — only `__system__` (uid 1) can read it.
Fix: Add an `access_<model>_user` row at minimum: `access_my_model_user,my.model.user,model_my_model,base.group_user,1,1,1,0`. Stage 1 lint collects every `_name = "..."` and warns when no ACL row exists.

### 3. `_inherit` of a model whose owning module isn't in manifest `depends`
Applies: all versions. Status: active. Last confirmed: 2026-05-20.
Cause: Forgot to add the dep when extending an existing model — install passes (extending class registers) but at runtime inherited fields may appear missing.
Fix: Add the owning module to `depends`. Stage 1 lint flags `_inherit` targets it can't find anywhere on the addons-path.

### 4. View xpath references a field that doesn't exist
Applies: all versions. Status: active. Last confirmed: 2026-05-20.
Cause: Typo, field removed in a newer Odoo version, or the addon adding the field isn't in `depends`.
Fix: `grep -rn "name=\"<field>\"" odoo/addons/<owner>/views/` to confirm the real name. Update xpath; add the addon's owner to `depends` if missing. Stage 1 only validates XML syntax — field existence surfaces at Stage 2.

### 5. `<menuitem parent="X">` where X doesn't resolve
Applies: all versions. Status: active. Last confirmed: 2026-05-20.
Cause: Parent menu's external ID is wrong, or its owning module isn't in `depends`.
Fix: `grep -rEn "<menuitem id=\"<menu>\"" odoo/addons/<owner>/` to find the real xml-id. Update `parent=`; add owner to `depends` if needed.

### 6. Adding a `required=True` field to an existing populated model fails install
Applies: all versions. Status: active. Last confirmed: 2026-05-20.
Cause: Existing rows have NULL for the new column; `NOT NULL` constraint blows up.
Fix: Ship `required=False` first with a backfill in `migrations/<version>/pre-fill.py`, then bump version and set `required=True`. Or provide `default=` callable for a sensible value. Or backfill via `post_init_hook`.

### 7. Demo data references an external ID that's not yet loaded
Applies: all versions. Status: active. Last confirmed: 2026-05-20.
Cause: Manifest `data:` list order matters — referenced records must load first.
Fix: Reorder `data` in the manifest so producers come before consumers. Split large files into smaller ones with clear dependencies if untangling order is hard.

### 8. Addon "installs" but a core field/menu is invisible — required feature group never enabled
Applies: all versions. Status: active. Last confirmed: 2026-05-20.
Cause: Odoo gates many "advanced" features (lots, variants, multi-currency, multi-step routes, pricelists, discounts, analytic, subtasks) behind `res.groups` flags toggled via Settings — `__manifest__.py:depends` doesn't surface them.
Fix: List required feature groups in the plan's `Required configuration` heading with xmlid + UI path, then either add a `post_init_hook` that flips them on or document the operator pre-step. Stage 3 smoke asserts `env.ref('<xmlid>') in env.user.groups_id` for each.

### 9. The install stage flags `ERROR ... Importing test framework` even though install succeeds
Applies: Odoo 19. Status: active. Last confirmed: 2026-05-20.
Cause: Addon's top-level `__init__.py` does `from . import tests`, which transitively imports `odoo.tests.common`. Odoo 19's `common.py` logs `_logger.error("Importing test framework ...")` whenever imported outside `--test-enable`. The harness's "flag any ERROR" rule then fails Stage 2 even though install completed and exit code was 0.
Fix: Drop `from . import tests` from the addon's top-level `__init__.py`. Odoo's test loader discovers the `tests` subpackage on its own when `--test-enable` is active.

---

## Static lint (Stage 1)

### 10. The install stage reports `<string>:38: (ERROR/3) Unexpected indentation.`
Applies: all versions. Status: active. Last confirmed: 2026-05-20.
Cause: Odoo parses each module's `__manifest__.py:description` as reStructuredText. RST-tricky shapes (numbered lists with continuation indents, mixed inline markup) produce `docutils` warnings printed at module-load time, which the installer's regex catches as ERROR.
Fix: Keep `description` as a plain prose paragraph — no headings, no numbered lists, no continuation indents. Anything richer belongs in `<addon>/doc/user_manual.md`.

### 11. The install stage reports `FAIL ... did not complete cleanly` after a successful install
Applies: Odoo 19. Status: active. Last confirmed: 2026-05-20.
Cause: Installer's suspicious-line regex matches Odoo's framework-level warnings that aren't actually failures — chiefly entries #9 (test framework import) and #10 (RST description).
Fix: Verify via `psql -tAc "SELECT state FROM ir_module_module WHERE name='<module>';"` — if `installed`, treat the FAIL as false positive. Long-term: tighten the installer's regex to downgrade the two known patterns to warnings.

---

### 49. `odoo-bin --i18n-export` rejected with "no such option" when exporting a .pot
Applies: tooling. Status: active. Last confirmed: 2026-06-13.
Cause: The CLI translation-export option is not exposed in this build's `odoo-bin` (the option parser rejects `--i18n-export=` outright with exit 2), so the documented one-liner to generate `i18n/<module>.pot` fails.
Fix: Export via the `base.language.export` wizard in `odoo-bin shell` instead: create one with `format='po'`, `modules=[(6,0,[mod.id])]`, call `act_getfile()`, then `base64.b64decode(exp.data)` and write to the addon's `i18n/<module>.pot`. Leave `lang` blank for a POT template.
---

## Operational smoke (Stage 3)

### 12. Tour test fails because the menu xml-id changed
Applies: all versions. Status: active. Last confirmed: 2026-05-20.
Cause: Tour selector `[data-menu-xmlid="my_module.menu_root"]` doesn't match the actual rendered menu.
Fix: `grep -n "menu_root" odoo/addons/<addon>/views/` and pin tours to xml-ids, never to UI labels (which translate).

### 14. `set_approval` / `_set_approval` tests fail with `AccessError: You are not allowed to modify 'Contact'`
Applies: Odoo 19, web_studio. Status: active. Last confirmed: 2026-05-20.
Cause: `web_studio._set_approval` does `record.check_access('write')` on the underlying record. Test users created with `mail_new_test_user(..., groups="base.group_user")` don't have partner-write — which requires `contacts.group_partner_manager` or `sales_team.group_sale_salesman`.
Fix: In test `setUpClass`, give each user that will call `set_approval` membership in a partner-writable group: `groups="base.group_user,contacts.group_partner_manager"`. Apply to `approver`, `outsider`, `parent_approver`, `static_approver`.

### 15. Subclassed `_set_approval` UserError silently swallowed by `check_approval` try/except
Applies: Odoo 19, web_studio. Status: active. Last confirmed: 2026-05-20.
Cause: Upstream `studio_approval.check_approval` wraps `_set_approval` in a `try/except UserError` and falls back to `_create_request` on any `UserError`, including domain-specific errors the subclass meant the user to see. The UI shows the generic "An approval is missing" notification.
Fix: Also override `check_approval` and raise the domain-specific `UserError` *before* calling super (so it propagates out before the upstream try/except catches it). Keep the `_set_approval` override too — it covers direct "Approve" clicks on the activity which don't go through `check_approval`.

---

## Demo data / Data files

### 21. Demo data with `noupdate="1"` doesn't update on `-u`
Applies: all versions. Status: active. Last confirmed: 2026-05-20.
Cause: By design — `noupdate="1"` means "load on first install only" so customer edits aren't clobbered.
Fix: For one-time updates, change to `noupdate="0"` for that release then change back. Or write a migration script in `migrations/<version>/post-update.py`.

### 22. `%(xmlid)d` substitution in plain-text `<field>` content stays unresolved
Applies: all versions. Status: active. Last confirmed: 2026-05-20.
Cause: Printf-style xmlid substitution (`%(module.xmlid)d`) only fires inside `<field eval="...">` attributes. Used as plain-text content of `<field name="domain">` or `<field name="context">`, the literal string lands in the DB and the JS evaluator throws `EvalError: Token cannot be parsed` when the menu opens.
Fix: Switch to `eval` with `ref()`: `<field name="domain" eval="[('project_id', '=', ref('mod.xmlid'))]"/>`. Re-run `-u <addon>` to reload the action. Stage 1 lint can grep `<field name="(domain|context)">[^<]*%\([^)]+\)[ds]` for the bad pattern.

---

## Compute / API

### 23. `@api.depends` doesn't re-trigger when a related field's child changes
Applies: all versions. Status: active. Last confirmed: 2026-05-20.
Cause: `@api.depends("partner_id")` doesn't trigger when `partner_id.name` changes — the depend chain only watches one hop.
Fix: List the full read path: `@api.depends("partner_id.name")`. List every dotted path the compute method dereferences.

### 24. Removing a `post_init_hook` in code does not undo what it already did
Applies: all versions. Status: active. Last confirmed: 2026-05-20.
Cause: `post_init_hook` runs once on initial install. If the hook mutated DB state (e.g. `view.active = False`), removing the hook from `__init__.py` and re-upgrading leaves the DB still reflecting the deactivation.
Fix: When refactoring away from a state-mutating hook, add a one-shot `data` XML record (or migration script) that explicitly restores the affected fields. Or restore manually via `odoo-bin shell` once.

### 50. `@api.onchange` summing sibling x2many rows double-counts (false "over-allocated")
Applies: all versions. Status: active. Last confirmed: 2026-06-13.
Cause: Reading `self.<parent>.<line_ids>` inside a per-row onchange counts the current row twice (as `self` and in the parent set) and includes the editable list's blank "new" row with its default values — so a sum-vs-limit check fires on the very first entry.
Fix: Sum only rows with a different identifying key (`l.lot_id != self.lot_id`), excluding the current-row duplicate and the lot-less blank row. See odoo_runtime_idioms.md § `@api.onchange`.

### 51. `_get_available_quantity` flags a correctly-booked confirmed line as a shortage
Applies: all versions, `stock`. Status: active. Last confirmed: 2026-06-13.
Cause: Available = on-hand − reserved, and *reserved* includes THIS document's own reservation. Once a confirmed order reserves its committed lot, that lot's available drops to 0, so "is my committed lot still available?" reads as a shortage/exception.
Fix: Add back this line's own reservation (`move_ids.move_line_ids.quantity_product_uom` for the lot, non-done/cancel) before comparing; subtract only OTHER documents' claims. See odoo_runtime_idioms.md § Reservation & availability semantics.

### 52. A lot/lock guard on `stock.move.line` blocks order/delivery cancellation
Applies: all versions, `stock`. Status: active. Last confirmed: 2026-06-13.
Cause: Cancel → `stock.move._action_cancel` → `_do_unreserve()` → `move_line.unlink()`. A `write`/`unlink` guard meant to stop manual lot tampering also fires on this system unreserve, so the order can't be cancelled.
Fix: Exempt system unreserve by overriding `_do_unreserve` to run `with_context(<bypass>=True)` and checking that flag in the guard; manual deletes call `unlink()` directly and stay blocked. See odoo_runtime_idioms.md § Guards vs system flows.

### 58. Receiving a serial: a second move line doubles demand and blocks validation
Applies: all versions, `stock`. Status: active. Last confirmed: 2026-06-14.
Cause: `picking.action_confirm()` already reserves one `stock.move.line` for the move's demand. Code that then *adds* a line via `move.move_line_ids = [Command.create({'lot_id': ..., 'quantity': 1})]` ends up with two lines (demand doubles to 2), and the auto-created first line has no lot — so `_action_done()` raises `UserError: You need to supply a Lot/Serial Number for product`.
Fix: Stamp the lot onto the EXISTING line instead of creating a new one: `if move.move_line_ids: move.move_line_ids[0].lot_id = lot.id; move.move_line_ids[0].quantity = 1.0`. Only `Command.create` a line when none was auto-reserved.

### 59. `cr.commit()` inside a method called from a test raises "Cannot commit or rollback a cursor"
Applies: all versions. Status: active. Last confirmed: 2026-06-14.
Cause: A cron/batch method that commits between records (to avoid one late failure undoing a whole nightly batch) is correct in production, but the test cursor forbids commit/rollback — the assertion `Cannot commit or rollback a cursor from inside a test` fails the test even though the logic is right.
Fix: Guard the commit with the core idiom: `from odoo import modules` then `if not modules.module.current_test: self.env.cr.commit()`. Mirrors `mail.mail` (`auto_commit = not modules.module.current_test`). There is no `registry.in_test_mode()` in v19 — `modules.module.current_test` is the flag.

---

## Views / UI

### 25. Two website header templates can't both replace `//header//nav`
Applies: all versions, `website`. Status: active. Last confirmed: 2026-05-20.
Cause: `website` ships multiple `template_header_*` views that all `<xpath expr="//header//nav" position="replace">` against `website.layout`. Only ONE may be `active=True` at a time — they're mutually exclusive.
Fix: Don't inherit `website.layout`. Inherit `website.template_header_default` (or whichever is active) and replace `<div id="o_main_nav">` rather than the outer `<nav>`. Keeps all website-layer placeholders wired and avoids the mutual-exclusion conflict.

### 26. Deactivating `template_header_default` reverts to the portal navbar, not a usable website header
Applies: all versions, `website`. Status: active. Last confirmed: 2026-05-20.
Cause: Layout chain is `web.frontend_layout` → `portal.frontend_layout` (basic nav, sign-in only) → `website.template_header_default` (website-aware navbar with search/lang/brand/CTA). Deactivating the default falls back to the portal's basic navbar.
Fix: Inherit `website.template_header_default` directly and modify its content (see #25). Don't toggle headers via `post_init_hook` unless you genuinely want the portal navbar.

### 27. `kanban_image()` and `activity_image()` are NOT available inside `<kanban>` templates
Applies: Odoo 19. Status: active. Last confirmed: 2026-05-20.
Cause: Odoo 19 removed/renamed these helpers. Only a regex check for the string `kanban_image` survives in the kanban parser (for cache-busting field-fetch); no runtime function. Calling either from a `<kanban>` template fails with `TypeError: ctx.<name> is not a function` at render — install does NOT catch this.
Fix: Use `<field name="image_128" widget="image" options="{'size':[200,200]}"/>` or `widget="background_image"`. Alternatively `<img t-attf-src="/web/image/my.model/#{record.id.raw_value}/image_128"/>`. The model needs `image.mixin` (or `fields.Image`) for `widget="image"` to work.

### 53. A `raise` in a transient-wizard button blanks the dialog instead of showing the error
Applies: all versions. Status: active. Last confirmed: 2026-06-13.
Cause: The web client `web_save`s the wizard before calling the button; if the method raises, the transaction (including the just-saved lines) rolls back and the dialog re-renders empty — the user sees the wizard wipe itself, not the error.
Fix: For recoverable input, cap-and-warn in `@api.onchange` (`return {'warning': {...}}`) so the value is corrected before save; keep a save-time `raise` only as a backstop. See odoo_runtime_idioms.md § Transient wizards.

### 54. A `<button>` between list field columns shifts every following column's header
Applies: all versions. Status: active. Last confirmed: 2026-06-13.
Cause: Button cells emit no header `<th>`, so each field to the button's right inherits the previous column's header — e.g. a status badge renders under the wrong label.
Fix: Place row-action buttons LAST in the `<list>`, or give the button an explicit `width=`. See odoo_runtime_idioms.md § Editable lists & inline buttons.

### 55. List/action button icon renders grey (colours only on hover)
Applies: all versions. Status: active. Last confirmed: 2026-06-13.
Cause: `class="text-warning"` on a `<button>` is overridden by button styling, so the FontAwesome icon shows muted and tints only on hover.
Fix: Put the colour in the `icon` attribute — `icon="fa-warning text-warning"` (core pattern, `stock_orderpoint_views.xml`). See odoo_runtime_idioms.md § Icons, decorations & indicators.

### 56. A list column stretches into a big blank gap before the row controls
Applies: all versions. Status: active. Last confirmed: 2026-06-13.
Cause: The trailing no-width column absorbs all leftover table width; if it's a narrow icon/button column, the slack shows as dead space before the delete control.
Fix: Give numeric/icon columns explicit `width=` and leave one text column width-less so it (not the icon column) takes the remainder. See odoo_runtime_idioms.md § Editable lists & inline buttons.

### 62. `t-field` of a Monetary/Date field inside a `<td>` raises "QWeb widgets do not work correctly on 'td' elements"
Applies: Odoo 19, QWeb (report PDF + portal/website templates). Status: active. Last confirmed: 2026-06-15.
Cause: `t-field` renders via the field's widget (monetary, date, …); the widget injects markup the table-cell layout can't host, so QWeb asserts at RENDER time. Install/lint pass — it only fails when the template renders (a portal page 500s; a report falls back to an HTML error doc, so `_render_qweb_pdf` returns ctype `html` not `pdf`). A redirect into the broken portal page also 500s a controller test that looked unrelated.
Fix: In table cells use `t-out` for the plain value and add the currency name separately — `<td><span t-out="o.amount"/> <span t-out="o.currency_id.name"/></td>` — instead of `<td><span t-field="o.amount"/></td>`. `t-field` with a widget is fine outside `<td>`/`<th>` (in a `<div>`/`<span>`/`<p>`).

---

## Version-specific — Odoo 19

*This whole section graduates to archive when the user migrates off Odoo 19.*

### 35. `res.groups.category_id` removed — use `privilege_id` referencing `res.groups.privilege`
Applies: Odoo 19. Status: active. Last confirmed: 2026-05-20.
Cause: Odoo 19 removed the `category_id` Many2one on `res.groups`. It was replaced by `privilege_id` → new model `res.groups.privilege`. Install fails: `ValueError: Invalid field 'category_id' in 'res.groups'`.
Fix: Define a `res.groups.privilege` record (its own `category_id` still points at `ir.module.category` if needed), then reference it from the group: `<field name="privilege_id" ref="res_groups_privilege_<name>"/>` instead of `<field name="category_id" ref="..."/>`. Stage 1 lint can grep `<field name="category_id"` inside `<record … model="res.groups">` blocks.

### 36. `res.users.groups_id` (and `ir.ui.menu.groups_id`) renamed to `group_ids`
Applies: Odoo 19. Status: active. Last confirmed: 2026-05-20.
Cause: Standard naming sweep — every Many2many to `res.groups` renamed `_id` → `_ids`. Code writing `{'groups_id': [...]}` to users or menus fails with `Invalid field 'groups_id' in 'res.users'`.
Fix: Replace every `groups_id` with `group_ids` in Python (`user.write({'group_ids': [(4, group.id)]})`), demo XML, and test setUp. The implied-groups field is now `all_group_ids`. `<menuitem groups="...">` attribute still parses but `menu.group_ids` is the direct ORM access.

### 38. `product.product_category_all` is gone — root split into goods/services/expenses
Applies: Odoo 19. Status: active. Last confirmed: 2026-05-20.
Cause: The single root product category was split into three: `product.product_category_goods` / `_services` / `_expenses`. Demo/data XML referencing `product.product_category_all` fails "External ID not found".
Fix: Map each child category to the semantic root. Services (consultations, procedures) → `_services`. Physical (cosmetics, pharma, consumables) → `_goods`. Reimbursable → `_expenses`.

### 39. `ir.cron` no longer has `numbercall`/`doall`/`state`/`code`/`model_id` — needs a paired `ir.actions.server`
Applies: Odoo 19. Status: active. Last confirmed: 2026-05-20.
Cause: Odoo 19 simplified `ir.cron` — the "run this Python code / call this method" concerns moved into `ir.actions.server`. The cron just schedules an existing server action via `ir_actions_server_id`.
Fix: Split into two records — one `ir.actions.server` with `state="code"` and `code="model._my_method()"`, and one `ir.cron` referencing it via `ir_actions_server_id`. Drop `numbercall`/`doall`/`state`/`code`/`model_id`/`name` from the cron; `name` is now computed from the server action.

### 40. Partner list view xpath fails because `name` is `column_invisible`
Applies: Odoo 19. Status: active. Last confirmed: 2026-05-20.
Cause: In Odoo 19's `base.view_partner_tree`, the visible name column is `<field name="display_name" string="Name"/>`. `name` is also present but `column_invisible="true"` — xpath against it inserts content that doesn't render where expected.
Fix: Use `<xpath expr="//field[@name='display_name']" position="after">` for partner list inheritance. Same lesson for any model where the human label is rendered via `display_name` (kanban cards, list views generally).

### 41. `<search>` view RELAXNG strict — filters can't follow `<group>`, no `<group string="…">`
Applies: Odoo 19. Status: active. Last confirmed: 2026-05-21.
Cause: Two rules in Odoo 19's search-view schema: (1) element order must be `<field>` → `<separator>/<filter>` → `<group>`; once `<group name="group_by">` appears, no bare `<filter>` siblings after it; (2) `<group>` inside `<search>` doesn't accept `string=`, `expand=`, or any other attribute except `name=`.
Fix: Use bare `<group>` for group-by clusters (no `name=`, no `string=`, no `expand=`). Inside, use `<filter ... context="{'group_by': 'X'}"/>`. For inheritance: add new filters with `<xpath expr="//filter[@name='inactive']" position="after">`; merge new group-bys with `<xpath expr="//group" position="inside">` (anchor on the bare group). Stage 1 lint can warn on `<group string="...">`, `<group expand="...">`, and `<group name="group_by">` inside `<search>`.

### 46. `ir.actions.act_window.target="inline"` rejected by v19 Selection field
Applies: Odoo 19. Status: active. Last confirmed: 2026-05-21.
Cause: `target` on `ir.actions.act_window` is a Selection field in v19; `inline` is not in the allowed values list. Older `res.config.settings` actions used `target="inline"` to render the settings form embedded in the configuration panel — that value is no longer accepted. Install fails with `convert_to_column_insert` → `convert_to_column` traceback on `fields_selection.py:225`.
Fix: Omit the `target` field entirely (defaults to `current`), OR use a known-valid value: `current`, `new`, `main`, `fullscreen`. For settings actions, the standard v19 pattern is `target=current` with `context="{'module': 'your_module', 'bin_size': False}"` — matches `action_account_config` in `odoo/addons/account/views/res_config_settings_views.xml`.

### 47. Menu loaded before its referenced action — "External ID not found"
Applies: all versions. Status: active. Last confirmed: 2026-05-21.
Cause: Manifest `data` order matters. `<menuitem action="action_X"/>` records resolve `action_X` at load time. If the file defining `action_X` appears AFTER the menu file in `data`, the menu load raises ParseError on the unresolved external ID.
Fix: In `__manifest__.py`, list every action-defining file (views, wizards, reports) BEFORE `views/menus.xml`. Menus are always last in the data array. Stage 1 lint can warn when a `menuitem`'s `action=` ref isn't defined in an earlier data file.

### 57. `stock.move` has no `name` field in v19 — passing `name` in move vals fails
Applies: Odoo 19. Status: active. Last confirmed: 2026-06-14.
Cause: The `name` field was removed from `stock.move`; the human-readable line label is now the computed `description_picking`. Code creating a move with `{'name': product.display_name, ...}` (the pre-19 idiom) raises `ValueError: Invalid field 'name' on model 'stock.move'`.
Fix: Drop `name` from the move vals entirely — `description_picking` auto-computes from the product/picking type; set it only for a custom label. `grep -n "name\s*=\s*fields\." odoo/addons/stock/models/stock_move.py` returns nothing in v19, confirming the field is gone.

### 60. Custom `account.report` handler is an `AbstractModel` — needs no ACL, isn't searchable
Applies: Odoo 19 Enterprise (`account_reports`). Status: active. Last confirmed: 2026-06-15.
Cause: A custom financial report's handler subclasses `account.report.custom.handler` as `models.AbstractModel` (no DB table). It has a `_name`, so naive tooling treats it like a stored model: Stage-1 lint demands an `ir.model.access.csv` row (false error), and Stage-3 smoke `search([])`es it → `relation "<table>" does not exist` → aborts the transaction. Real enterprise handlers ship NO ACL row.
Fix: AbstractModel handlers need NO ACL and must NOT be searched. Static lint and operational smoke should skip `_name`s whose class extends `AbstractModel` (smoke also runs each probe in a savepoint). For your own checks, gate on `env[model]._abstract`. Don't add a bogus ACL row to silence a linter.

### 61. Custom `account.report` with a variable number of period/bucket columns
Applies: Odoo 19 Enterprise (`account_reports`). Status: active. Last confirmed: 2026-06-15.
Cause: The `account.report` engine builds columns from the report's static `column_ids` (XML). A report needing a runtime-variable column count (N date buckets from a configurable horizon) can't express that purely in XML, and lines built by hand miss the per-column plumbing (`column_group_key`, `figure_type`).
Fix: Declare the MAX columns statically in XML (e.g. `opening` + `b1..b13`, each with `expression_label` + `figure_type="monetary"`, NO `line_ids`). In the handler's `_custom_options_initializer`, rename `options['columns']` headers (locale-aware `format_date`) and filter to the active horizon. In `_dynamic_lines_generator`, build each line's `columns` by iterating `options['columns']` and calling `report._build_column_dict(value, col, options=options, currency=...)`; line id via `report._get_generic_line_id(None, None, markup=...)`. Bucket by rolling windows from today (not `date_trunc('week')`, which forces ISO Monday regardless of locale). Pattern: `enterprise/account_reports/models/account_cash_flow_report.py` (handler) + `account_aged_partner_balance.py` (column manipulation).

---

## Planning process / cross-addon refactor

### 42. Refactor plan based on subagent summaries over-states inconsistencies
Applies: planning. Status: active. Last confirmed: 2026-05-20.
Cause: Subagent `Explore` runs that summarise rather than emit verbatim code can drift from the live tree (line numbers off, locations inferred from comments). Cross-addon refactor plans built from those summaries inherit drift — several "inconsistencies" are already-resolved, overstated, or infeasible due to invisible dep cycles.
Fix: Before committing any cross-addon move, run live `grep -rln <symbol>` for every model/field/method the move touches. Verify the symbol's actual declaration, every consumer's `__manifest__.py:depends`, and that the move direction doesn't create a cycle. Surface mid-execution corrections in a `## Plan corrections discovered at execution time` block in the plan.

### 43. Moving a field/model across addons requires bidirectional dependency audit
Applies: planning. Status: active. Last confirmed: 2026-05-20.
Cause: A "cohesion fix" that moves a field from addon A to addon B looks clean from B's perspective, but every consumer that read it via A's dep graph now needs B in their depends. If those consumers are *upstream* of B, the move creates a cycle.
Fix: For every planned move, build the consumer set via `grep -rln <symbol>`, then read each consumer's manifest `depends` and confirm the destination is already transitively reachable. If any consumer is upstream of the destination, the move is infeasible without restructuring — default outcome is keep the symbol and address cohesion via comments instead.

### 44. "Forward declaration" critique misapplied to decoupled-extension pattern
Applies: planning. Status: active. Last confirmed: 2026-05-20.
Cause: A field declared in addon A and *written* (not computed) by a cron in addon B can look like a forward-declaration anti-pattern but isn't. A's declaration provides the column + default + view-visibility for A-scope consumers; B owns the update logic. Standard loose-coupling Odoo pattern — B can be uninstalled without breaking A's view filters.
Fix: Re-read the field declaration carefully. If it's `fields.X(default=...)` (stored with default) and another addon writes via `record.write({...})`, it's a legitimate seam — not a forward declaration. The misleading signal is usually a "# Placeholder" comment from the original author; correct the comment to "stored field; addon B writes via cron" and move on.

### 64. `res.groups.users` renamed to `user_ids` (the reverse side of the #36 sweep)
Applies: Odoo 19. Status: active. Last confirmed: 2026-06-25.
Cause: The same `res.groups` rename sweep as #36 also hit the group→users side. `group.users` raises `AttributeError: 'res.groups' object has no attribute 'users'` at runtime (passes lint/install — only fails when the code path runs, e.g. an approval-notify helper iterating a group's members).
Fix: Use `group.user_ids` (members explicitly in the group) or `group.all_user_ids` (incl. implied). Membership tests on a user are `group in user.all_group_ids` (not `user.groups_id`). Grep new code for `\.users\b` on a `res.groups` recordset before shipping.

### 65. `_sql_constraints` is no longer supported — use `models.Constraint`
Applies: Odoo 19. Status: active. Last confirmed: 2026-06-25.
Cause: Odoo 19 deprecated the `_sql_constraints = [(...)]` class attribute. It logs `WARNING: Model attribute '_sql_constraints' is no longer supported, please define models.Constraint on the model` and the SQL constraint is NOT created — so the uniqueness/check silently does nothing (install still "succeeds").
Fix: Replace each tuple with a class attribute: `_code_uniq = models.Constraint('unique(code)', "The code must be unique.")`. The first arg is the SQL definition, the second the error message. Confirm with the same warning gone from the install log.

### 66. Full-copy override of an enterprise raw-SQL matcher method drifts silently on upgrade
Applies: Odoo 19. Status: active. Last confirmed: 2026-07-01.
Cause: To add a criterion to the reconcile-model engine (`account_accountant`'s `get_available_reconcile_model_per_statement_line` / `_apply_reconcile_models`), there is no partial hook — the WHERE logic is one monolithic `SQL(""" ... """)` string. Extending it means copying the whole method verbatim and injecting one AND-block. On an Odoo point-release that edits the upstream SQL (new column, changed `match_label` block), the override keeps running the stale copy: install/lint/smoke stay green while matching silently diverges from core.
Fix: Isolate the copied method in one file with a header comment naming the exact upstream file + method + line range copied. On every upgrade, `diff` the upstream method against your copy and re-sync the non-injected parts; re-run the addon's `--test-tags`. Mirror the upstream idioms exactly when injecting — e.g. `jsonb` columns (`transaction_details`, `move.narration`) MUST be cast `::TEXT` before `ILIKE`/`~*`, and compare against the stored `reco_model.<param>` column (never a Python-interpolated string) to avoid injection.

### 67. Raw-SQL matcher reads a field the caller hasn't flushed (e.g. `move.narration`)
Applies: Odoo 19. Status: active. Last confirmed: 2026-07-01.
Cause: `_apply_reconcile_models` matches statement lines with a raw `cr.execute(SQL(...))` that reads `move.narration`, but its preamble only `flush_recordset`s statement-line fields — not `narration`. In production narration arrives already-persisted from the bank import, so it works; in a test (or any code) that sets `move.narration` in the ORM cache and immediately calls the matcher, the query reads stale DB and the model silently fails to match. Passes as "test asserts model didn't apply" — looks like a matching bug, is actually a flush bug.
Fix: Before calling a method that matches via raw SQL on a field you just wrote, flush it: `self.env.flush_all()` (or `record.flush_recordset(['narration'])`). General rule: any ORM write consumed by a subsequent raw-SQL read in the same transaction must be flushed first.
