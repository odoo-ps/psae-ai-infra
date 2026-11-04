# Refreshing the catalog on an Odoo version bump

The `catalog/` (odoo.css + component fragments + sprites) is **hand-authored**
from Odoo source, not generated — a mechanical SCSS→CSS conversion drags in the
whole Bootstrap layer and defeats the "small, readable, self-contained" goal.
So refreshing is a deliberate, traceable edit, not a script run. (The one
exception is icon artwork, which is extracted from Odoo's real icon fonts.)

The catalog tracks ONE Odoo version — the latest, stamped on the first line of
`catalog/odoo.css` ("calibrated to Odoo NN Enterprise"). Mocks built for an
older version keep the assets they copied; they are not migrated.

## When to refresh

- A new `versions/v<major>/` stack (Odoo + Enterprise) lands in the repo.
- A view the catalog covers gets a visible redesign upstream.
- A mock needs a view type not yet in the catalog (promote it from the
  "NOT in the starter catalog" list in `view_types.md`).

## How to refresh

Mandatory and in order — a refresh is calibrated against the REAL product, not
against class names. The kit lives in `reference/scripts/calibrate/` (Node,
maintainer-only: `npm install` there once; drives the system Chrome via
puppeteer-core; configure with `ODOO_URL`, `ODOO_LOGIN`, `ODOO_PASSWORD`,
`CHROME_PATH`). The `node` commands below run from that folder; the `python`
ones from the skill root.

1. **Stand up the target version and capture real screens.** Create a fresh
   `--with-demo` database of the target major **with Enterprise** on the
   addons path (`versions/v<major>/enterprise`) and the modules listed in
   `screens.json` `_note`, served on its own port. Then
   `ODOO_URL=http://127.0.0.1:<port> node capture.js <outdir> [screen …]` saves
   one 1440×900 @2x PNG per `screens.json` entry. These captures are the ground
   truth. A covered surface with no entry gets one (url + optional `click` /
   `clickText` / `press` steps).
2. **Diff SCSS VALUES and DOM, old vs new major — not class existence.** For
   `web` AND `web_enterprise` (plus `mail` and the app addon of any app
   surface): diff the variables files (`primary_variables.scss`,
   `secondary_variables.scss`, `bootstrap_overridden.scss`,
   `*.variables.scss`), each component's SCSS, and its OWL/QWeb templates
   (`*.xml`). `web_enterprise/static/src/` mirrors web's paths and carries most
   of the visual design. Update **tokens first** (`:root` in `odoo.css`), then
   components, keeping the real class names; bump the stamp and the
   `Catalog version` header in `odoo.css` — line 1 is the **authoritative**,
   machine-read stamp (`_scaffold_mock.py` + `_lint_mock.py` parse it); keep the
   human `Catalog version` header identical. Paths: `style_guide.md` § Source map.
3. **Probe computed styles, real vs catalog, for every component.**
   `node probe.js real <odoo-path> '["<css>", …]' [--steps '<json>']` and
   `node probe.js file <page.html> '["<css>", …]' [--hash <screen-id>]` print
   rect, font, color, border, radius, padding and gap per selector. Fix the CSS
   until the numbers agree (sub-pixel noise aside).
4. **Rebuild icons from the real icon fonts.** Odoo draws UI icons from
   Material Symbols (`web/static/src/libs/materialsymbols/`, names in
   `web/icons.py`) and `odoo_ui_icons` (`web/static/lib/odoo_ui_icons/`). For
   each glyph the new version renders:
   `python reference/scripts/_extract_icons.py <name>[=id] [--filled]`
   (needs `fonttools` + `brotli`; `--list` lists names; `--web` points at
   another version's `web` addon). Paste the printed `<symbol>` into
   `catalog/icons.svg` under the EXISTING id — ids are the contract mocks use:
   swap the artwork, never add an alias. App icons: copy each module's
   `static/description/icon.svg` into `catalog/app-icons.svg`.
5. **Match the calibration screens.** The key captures have a twin page,
   `reference/calibration/screens/<name>.html`, built only from catalog markup
   and `odoo.css` (not every `screens.json` capture has a twin — some are
   covered by a sibling twin of the same view type). Render a twin with
   `node render.js ../../calibration/screens/<name>.html <out>.png` and compare
   it pairwise with its capture. **A refresh is not done until every twin
   matches its capture at a glance** — same chrome, colors, density and icons
   (data and photos may differ). When you touch a view type whose twin is
   missing, add the twin.
6. **Resync + render the gallery.** `_gallery.html` is a **hand-inlined copy**
   of the component markup — `_render_catalog.py` only screenshots it, nothing
   regenerates or diffs it against `components/*.html`. So after editing any
   fragment, paste the change into `_gallery.html` too, or it silently goes
   stale. Then `python3 reference/scripts/_render_catalog.py` and eyeball every
   component — it catches stray markers, z-index and broken layout the lint is
   blind to (`--baseline` saves the new baseline). Then build a sample mock, run
   `_lint_mock.py`, and open it in a browser.

> **Why class existence is not enough.** The first 19→20 pass (2026-09-30)
> compared `o_*` class indexes of the old and new cores, found "0 real drift"
> and stopped. Odoo 20 kept almost every class name yet redesigned the look —
> transparent navbar, borderless gray control panel, 16px root, teal active
> states, white bordered secondary buttons, tinted badges, boxed notebook,
> Material Symbols icons — almost entirely through SCSS values and
> `web_enterprise` overrides that a class-name diff cannot see. A passing lint,
> class or icon-ref check proves internal consistency only, never fidelity.
> (A class index is still handy for one thing: telling coined mock helpers —
> `.o_login_card`, `.o_portal_kv` … — from real classes that disappeared.)

## Catalog fix log

Rendering bugs found while generating mocks and fixed in the catalog source.
Both were latent in every mock until corrected — keep an eye out for the same
class of bug (CSS that styles a class but forgets a structural reset / stacking
order) on the next version bump.

- **`.o_breadcrumb` list-marker reset** — fixed 2026-06-12 (`odoo.css`).
  Breadcrumbs render as an `<ol>`/`<li>` list (`control_panel.html`) but the
  flex rule never reset the markers, so items showed stray "1."/"2." numbers.
  Added `list-style: none; margin: 0; padding: 0;` to `.o_breadcrumb`.
  *Obsolete since 2026-10-07: the breadcrumb is now `div.o_breadcrumb`
  (multi-level: `ol.breadcrumb > li.breadcrumb-item`) — the lesson stands.*

- **Walkthrough bar below the dialog backdrop** — fixed 2026-06-12
  (`annotations.css`). `.o_dialog_backdrop` (`z-index: 1000; position: fixed;
  inset: 0`) covered the whole viewport, so on any wizard/dialog screen it sat
  over the `.mock-walkthrough` bar (was `z-index: 900`) and swallowed its
  Prev/Next/Annotations clicks. Bumped the bar to `z-index: 1100` (above the
  dialog). The nav chrome must always sit above modals.

## Design refresh log

Entries are chronological. Those before 2026-10-07 describe the Odoo 19
calibration; where they conflict with the 2026-10-07 entry, that entry wins.

- **Odoo 19 fidelity pass** — 2026-06-12, calibrated against a real Odoo 19
  Sales Order form. Catalog changes that apply across all views:
  - Removed the persistent **dotted field underline** (`o_field_widget`) — Odoo
    15+ renders readonly fields as clean text. Required inputs keep a subtle
    solid cue only.
  - Added **teal link styling** (`o_form_link` / `o_list_link`,
    `--o-enterprise-action-color`) for relational/URL values — the look had them
    flat dark before. *(Lists: superseded 2026-10-07 — list cells are plain
    text; teal only for readonly `a.o_form_uri` links.)*
  - Field **labels** dropped to normal weight (were medium/bold).
  - **Statusbar buttons** made compact + flat (only primary filled); were full
    bordered Bootstrap buttons.
  - **Form sheet** softened: hairline `gray-200` border + subtle shadow (was a
    hard 1px border).
  - **List** rows tightened; added `o_list_handle` (drag), `o_optional_columns_toggle`,
    and steered inline tags to `o_tag` (gray pill) vs colored status `badge`.
  - Added **`o_subtotal_footer`** (right-aligned Untaxed / Tax / Total) — a
    near-universal sale/purchase/invoice element that was previously faked with a
    `tfoot`.
  - **Chatter topbar** flattened to tab-like actions with a divider.

- **Accuracy + interactivity pass (P1+P2)** — 2026-06-12. Two tracks:
  - **P1 — field-placement accuracy.** Added `reference/odoo_screens/` (per-model
    field placement transcribed from real Odoo 19 view XML; `sale_order.md`,
    `stock_picking.md`, README). Generation now consults it (SKILL.md step 3 +
    checklist) so standard fields land in their real group/tab. Fixed the
    flagship mock: `sale.order` Warehouse & Salesperson moved off the main form
    to *Other Info ▸ Shipping/Sales*.
  - **P2 — interaction layer.** `walkthrough.js` v2 adds `data-mock-tab`
    (switching notebook tabs), `data-mock-modal-open/-close` (in-place modals),
    `data-mock-toggle` (dropdown reveal), `data-mock-toast` (o_notification),
    Esc-to-close, and a CSS screen fade (`prefers-reduced-motion` aware). New
    catalog CSS/components: corner ribbon (`o_widget_web_ribbon`), toast
    (`o_notification`), `o-autocomplete` dropdown, `o_horizontal_separator` group
    titles, tab-panel show/hide. Documented in `reference/interactions.md`. All
    vanilla — self-containment lint stays green.

- **Catalog breadth + hardening (P3)** — 2026-06-12.
  - **Field-placement breadth**: `reference/odoo_screens/` grew to 7 models —
    added `account.move`, `purchase.order`, `res.partner`, `product.template`,
    `crm.lead` (transcribed from real Odoo 19 view XML; partner/product forms are
    version-stable).
  - **Component breadth**: chatter v2 (followers, composer, scheduled activity),
    control-panel favorite ★ + actions cog, `o_horizontal_separator` group
    titles, and `components/chart_views.html` — on-brand **graph / pivot /
    calendar** placeholders (CSS only, no charting lib). `view_types.md` updated:
    those three are now in-catalog.
  - **Theming**: `body.o-community` one-line switch flips the brand to the
    Community palette.
  - **Visual-regression harness**: `reference/catalog/_gallery.html` +
    `reference/scripts/_render_catalog.py` render every component (interactive
    states force-shown) to a PNG for eyeballing / baseline diff after edits or a
    version bump. Run with `--baseline` to save `_gallery.png` as the reference.

- **Field placement → runtime discovery (cache removed)** — 2026-06-12.
  Superseded the P1/P3 `reference/odoo_screens/` cache: a hand-maintained
  per-model snapshot was limiting and drifts on version bumps. **Deleted
  `reference/odoo_screens/` entirely.** Field placement is now discovered **at
  generation time from the live `odoo/`/`enterprise/` source** (base view +
  inheriting modules), documented as a procedure in `reference/field_placement.md`.
  When that source isn't present, the skill **warns the user** (and notes it on
  the mock cover) that screens are best-effort, then falls back to a generic
  view_types layout. Net: every model is covered and stays true to the actual
  code, with no static set to maintain.

- **App surfaces beyond the backend webclient** — 2026-06-12. Added 7 catalog
  fragments + token-based CSS (all static, self-contained — no charting/grid
  libs, no images), with authentic Odoo class names grounded in source:
  - **pos.html** (`point_of_sale`) — full-screen order screen (cart + numpad +
    Payment, category bar + product grid); payment-screen variant noted.
  - **website.html** (`website`/`website_sale`) — public frontend header + shop
    grid (`oe_website_sale`); product-page variant noted.
  - **account_report.html** (enterprise `account_reports`) — hierarchical
    foldable P&L / Balance-Sheet lines (rebuilt 2026-10-07 as a client action
    with its own control panel).
  - **spreadsheet.html** (`spreadsheet`/o-spreadsheet) — navbar
    (SpreadsheetNavbar), menu row, toolbar + inline composer, canvas-style grid,
    bottom bar with sheet tabs and statistic.
  - **gantt.html** (enterprise `web_gantt`).
  Documented in `view_types.md` § App surfaces; all added to `_gallery.html` and
  validated via the render harness. Still on-demand (not yet fragments): map,
  cohort, hierarchy/org-chart, timesheet/planning grid.

- **Annotation / help / sizing polish** — 2026-06-12. Three fixes from a review:
  1. **Annotations no longer clipped.** Marker notes were `position:absolute`
     inside the marker, so `.o_form_sheet { overflow:hidden }` (added for the
     ribbon) clipped them. walkthrough.js now renders ONE body-level floating
     tooltip (`.mock-float`, `position:fixed`, z-index 1300) for both markers and
     field-help — always top-layer and fully visible; clamped to the viewport,
     flips above when needed, re-positions on scroll.
  2. **Custom-field "?"** (`.o_field_help`) — an Odoo-style help marker on
     solution-added fields that reveals attributes (help text + Field/Model/Type/
     Readonly) on hover/click. Documented in `interactions.md`; demonstrated on
     the sale-lot mock's `lot_allocation_ids` column.
  3. **Sizing / chatter fit** — `.o-mail-Chatter` now `flex:0 1 360px;
     min-width:300px; overflow:auto` and the sheet area gets `min-width:0`, so
     sheet + chatter fit common widths cleanly (fixes the partial-chatter
     output). Verified at 1280/1440 via the render harness.

- **Statusbar modernized to Odoo 19** — 2026-06-12. The earlier fidelity pass
  modernized fields/links/buttons/sheet but left `.o_arrow_button` as the
  pre-15 look (white bordered chevrons, solid brand-purple current). Corrected
  against `statusbar_field.scss` + `primary_variables.scss`: the bar is
  **borderless**, inactive stages are flat muted-gray text, and the current stage
  is `color-mix(var(--o-enterprise-action-color) 20%, var(--o-gray-100))` with
  dark text (= `mix($o-action,$o-gray-100,20%)`), not a purple fill. Lesson:
  when matching a version, audit EVERY component — a single un-updated one makes
  the whole screen read as the old version. (Also: the regenerated sale-lot mock
  now carries a chatter on each SO/delivery form, which real Odoo forms have.)

- **Icons inlined (file:// fix)** — 2026-06-12. Icons were referenced from an
  external sprite (`<use href="assets/icons.svg#id">`). Browsers **block external
  SVG `<use>` over `file://`** (opaque origin), so every icon silently vanished
  when a mock was opened as a local file — which is the mock's whole point. Fix:
  the sprite is now **inlined** into `index.html` (hidden `<svg>` at top of body)
  and all fragment refs use same-document `<use href="#o-id">`; `icons.svg` is no
  longer copied as an asset. Added a `SVG-USE` lint check that flags any external
  `.svg#` ref so this can't regress. (Catalog `icons.svg` stays as the source
  that gets inlined.)

- **Navbar = white (Enterprise) + dropdown overlay + navbar consistency** —
  2026-06-12. *(Navbar color superseded 2026-10-07: the Enterprise navbar is
  transparent over the page gray.)*
  - **Navbar color** was the long-standing "header colors off" miss. Odoo 18/19
    **Enterprise** redesigned the top navbar to **white with dark text**
    (`web_enterprise/.../navbar.variables.scss`: `$o-navbar-background: $o-white`);
    `#714B67` is accent-only. Catalog navbar is now white/dark by default with a
    `body.o-community` override restoring the community purple (`#71639e`). Verify
    against source which edition's value you mean — don't assume the brand color
    paints the navbar.
  - **Toggled dropdown** was clipped + scrolled by `.o_list_view { overflow:auto }`
    inside a dialog. Added `.o_dialog .o_list_view` / `.o_dialog_body { overflow:
    visible }` and bumped the menu z-index so it **overlays** instead of forcing a
    scrollbar (same "overlays render on top" principle as the floating tooltip).
  - **Navbar consistency**: every screen must use the *same* navbar markup —
    condensed navbars on the dialog screens made the header change between steps.

- **Smart buttons (stat buttons) redesigned to Odoo 19** — 2026-06-12. Were a
  tall box (gray icon, bold value on top). Per `button_box/button_box.scss` they
  are now: a **joined, light-bordered group**, each compact (~btn height) with a
  **brand-purple icon left** + a left-aligned stack of **label on top** (small,
  muted, `o_stat_text`) and **value below** (bold, brand-purple, `o_stat_value`),
  wrapped in `o_stat_info`. Markup order is label-then-value (Odoo flips it via
  flex `order`; we author it directly). Also applied the `?` field-help to
  **wizard** custom-field columns (not just the main form).
- **CORRECTION — smart-button PLACEMENT** — 2026-06-13. The box is **not in the
  form sheet at all** in Odoo 19. Per `views/form/form_controller.xml` the
  `ButtonBox` renders into the control panel's `layout-actions` slot —
  `.o_control_panel_actions` — **centered** between the breadcrumb (left) and the
  pager/actions (right); the sheet starts at the title. (The "sheet top-right" note
  above, and an interim "sheet top-left" attempt, were both wrong — verified
  against `form_controller.xml`.) Catalog now: `control_panel.html` owns the box,
  `form_view.html` no longer has it, `odoo.css` `.o_control_panel_actions` centers
  it.

- **Full source-audit pass** — 2026-06-12. Audited the whole catalog against Odoo
  19 SCSS (4 parallel cluster audits). Foundation confirmed correct: tokens
  (font sizes, brand/action/semantic colors, grays, radii, fonts), buttons,
  dialog, autocomplete dropdown, tags/badges, list links, kanban structure,
  chatter topbar/composer/activity. Fixed the genuine drifts found:
  - **Form sheet**: `max-width` 990 → **1400px** (`$o-form-view-sheet-max-width`);
    **removed the box-shadow** (Odoo sheet is flat); border → `$border-color`.
  - **`o_horizontal_separator`**: added the **bottom rule** (`box-shadow:0 1px 0`)
    Odoo draws under group titles (was bold text only).
  - **Toast** (`o_notification`): **light bg + dark text** + colored left bar
    (was inverted dark — Odoo notifications are light).
  - Dialog backdrop opacity 0.4 → **0.5**; ribbon gained Odoo's `text-shadow`.
  Deliberately NOT changed at the time: chatter width, notebook tab style,
  label weight, kanban spacing, button padding — all recalibrated to the real
  values on 2026-10-07.

- **View-type & surface completeness pass** — 2026-06-12. Audited the catalog
  against Odoo's full view-type set (`ir.ui.view` type selection + view registry
  + module presence). Added 9 fragments so every standard + specialised view type
  and the major surfaces are covered: `cohort` (web_cohort), `map` (web_map —
  **static placeholder, never loads Leaflet tiles**), `grid` timesheet (web_grid),
  `hierarchy`/org-chart (web_hierarchy), `settings` (res.config.settings),
  `report` (printed QWeb PDF — A4 paper, its own surface), `portal` (customer
  frontend), `studio` (web_studio editor + field palette), `discuss` (mail).
  All real class names, token-based, self-contained; added to `view_types.md`,
  the gallery, and validated via render. Only `board` (legacy "My Dashboard")
  remains intentionally on-demand.

- **Login + Apps menu** — 2026-06-13. Added the two unauthenticated /
  entry surfaces that were missing from the catalog:
  - `components/login.html` — ported from `odoo/addons/web/views/
    webclient_templates.xml` (templates `web.login_layout` @ line 110
    and `web.login` @ line 136). Real Odoo composes the form from
    bootstrap (`.card / .form-control / .btn-primary / .alert`); the
    catalog ships a minimal Odoo-flavoured surrogate of those classes
    in `odoo.css` under the "Login screen" block.
  - `components/apps_menu.html` — ported from
    `enterprise/web_enterprise/static/src/webclient/home_menu/{home_menu.xml,
    home_menu.scss, home_menu.variables.scss}` and `home_menu_background.scss`.
    Real Odoo loads each app's icon via `web_icon` (either webIconData PNG
    or font-awesome class + bg + fg color). The catalog used the
    class-based variant — inline `style="background:#xxx"` on
    `.o_app_icon` + a single-character glyph. *(Superseded 2026-10-07: real
    multi-color `#o-app-*` artwork, never tinted; dotted background.)* App grid is 6 columns max,
    container max-width 850px (matches `$o-home-menu-container-size`),
    icon tiles 70px square (matches `$o-home-menu-app-icon-max-width`),
    page background `var(--o-gray-200)` (matches the SCSS default).
  Both were authored via the source-first iteration etiquette path —
  cited paths above; no token-only invention. Promoted alongside
  catalog-suite-tour, which now uses them as screens 1 + 2.

## 2026-06-14 — Coverage-floor reconciliation + website_form fragment

A quality-review run found the mock omitted spec-indicated surfaces (the
customer website form, the CRM lead, the inventory receipt, the eWallet card)
because the screen list was derived from the per-workflow `Screens &
Interactions` subsection plus a tight operator-journey curation — none of the
spec's stronger surface indicators (§3 Apps Impacted, the BPMN swimlane
*lanes*, the Automated-Behaviours triggers) were used as discovery inputs.

- **Coverage-level gate must show CONCRETE per-task choices (follow-up 3).**
  Generic tier labels ("Standard — full workflow") tell the user a category,
  not what their package contains. Because the gate is asked AFTER the step-1
  inventory is built, each `AskUserQuestion` option must be populated from that
  inventory — a screen count + the actual surfaces as a delta over the lower
  tier (use `preview` for long lists). Skip the gate when the inventory can't
  differentiate the tiers. Recompute per run; never show example figures
  verbatim.
- **Coverage floor → 8 dimensions + an explicit coverage-level gate
  (follow-up 2).** Two more gaps surfaced: (a) the floor still listed only
  *surface* dimensions, so behaviour coverage (lifecycle states, guard rules)
  and notification surfaces (emails/PDFs) had no home — the un-gated "Agree"
  was a guard-dimension miss; (b) there was no explicit user control over how
  much to render, so scope drifted between "too thin" and "too much" across
  prompts. Fixes: the floor is now EIGHT dimensions in two classes — SURFACE
  (actors, apps, new models+views, menus, reports, notifications) and
  BEHAVIOUR (lifecycle states, guard rules / negative paths); `New Fields`
  stays a per-screen fidelity item, not a floor dimension. And a single
  **coverage-level gate** (Core / Standard=default / Comprehensive) is asked
  once before assembly — each dimension is reconciled at the chosen tier, with
  out-of-tier items recorded as explicit exclusions. § Verify now hands the
  anchor all eight dimensions + the chosen level. (This spec's own mock sits at
  the Comprehensive level — config + reports + all states.)
- **Coverage floor BROADENED (follow-up).** The first cut of the floor
  reconciled only **actors + apps**, so a re-run still missed a new config
  model (`tradein.criterion`), a Configuration menu, and two named reports —
  all sitting *inside an already-covered app*, which an actor/app check can't
  catch. The floor is now FIVE dimensions — actors, apps, **new models (+
  their Views Required), menus, reports** — each mapped to a screen or an
  explicit exclusion; § Verify tells the coverage anchor to audit all five.
  Lesson: a partial coverage floor (or an anchor briefed on a partial
  inventory) reproduces the very under-coverage it was meant to prevent.
- **SKILL.md § Comprehension** gained a *coverage floor*: build the actor (BPMN
  lanes + user-story actors) + app (§3 Apps Impacted + Automated-Behaviours
  triggers) inventory FIRST; every actor and impacted app must map to ≥1 screen
  or be explicitly excluded. § Curate gained "never prune below the coverage
  floor"; the "supporting surfaces — opt-in" rule was clarified so a primary
  actor/workflow surface (website entry, CRM lead, inventory receipt, eWallet)
  is never misclassified as opt-in. § Verify now tells the coverage anchor to
  audit against the actor/app inventory, not the (circular) cover step list.
- **`components/website_form.html`** added — the public website intake form
  (s_website_form snippet), derived from
  `website/views/snippets/s_website_form.xml`; CSS block `.s_website_form*` added
  to `odoo.css`. A website intake is a PRIMARY surface when the spec says the
  journey "starts online", not an opt-in supporting page.

## 2026-06-14 — POS fragment reconciliation + ribbon/chatter fixes

Triggered by a quality-review run whose POS screens rendered "bleak" and whose
form ribbon/chatter were mislaid. Root causes + fixes (all source-cited):

- **`components/pos.html` rewritten to the current `odoo.css` vocabulary.** The
  fragment had drifted to dropped class names (`.pos-topbar-title`,
  `.order-summary`) that the refreshed `.pos` block no longer styles, so POS
  screens rendered unstyled. Re-derived from
  `point_of_sale/static/src/app/components/navbar/navbar.{xml,scss}`,
  `.../components/orderline/orderline.xml`, `.../screens/product_screen/**`.
  Now uses `.pos-topbar-tabs`/`.pos-tab`, `.orderline-num`/`.orderline-body`,
  `.order-totals`/`.order-total-row`, `.pos-actions-row`/`.pos-action-btn`.
  Re-verify these class names against the POS app templates on the next bump.
- **Custom POS UI = a Dialog popup over `.pos`.** Added a worked example + the
  `.pos-popup-row` / `.pos-popup-list` / `.o_dialog_alert_warn` helpers in
  `odoo.css`, modelled on `.../components/popups/select_lot_popup` (POS popups
  are standard web `Dialog` modals with `btn-lg`). Stops authors dropping
  backend `.o_field_row` / `.o_list_view` chrome into `.rightpane`.
- **`components/form_view.html` ribbon example fixed** to `data-text="…"` on an
  empty element — the band is drawn by `o_widget_web_ribbon::after {
  content: attr(data-text) }` (mirrors `web/.../widgets/ribbon/ribbon.scss`).
  Child text rendered unstyled. `_lint_mock.py` now flags a ribbon missing
  `data-text` or carrying child text (RIBBON rule).
- Chatter placement: no code change needed (`.o_content_with_chatter` was
  already correct); the failure was a package not using the wrapper. The
  `chatter.html` header already documents it.

## 2026-06-15 — Custom on-form OWL field-widget fragment

Triggered by the Quote Desk run (a small bespoke "live FX rate" OWL field widget),
which had no catalog pattern and had to be hand-built from tokens — the same
new-surface gap previously hit for POS popups and account.report.

- **`components/custom_field_widget.html`** added — a generic small DISPLAY field
  widget rendered inside the standard `.o_field_widget` cell (a custom widget is a
  per-field fidelity detail of a form, NOT a new screen / coverage-floor surface).
  Three shapes: status pill (`.badge`), icon+value pill (`.o_cw_pill` + inline
  `<use>` glyph), meter/gauge (`.o_cw_meter`). Carries the `o_field_help` "?" so
  it reads as solution-added. Modelled on `web/static/src/views/fields/` +
  `standardFieldProps`.
- **`odoo.css`** — added `.o_cw_pill` / `.o_cw_meter` (+ `is-warning`/`is-danger`
  tints) under the badges block; reuses existing tokens otherwise.
- **`_gallery.html`** — new "Custom on-form field widgets" section so the render
  harness covers the shapes.
- **`view_types.md`** — new "Custom field widgets" subsection under `form` telling
  authors to treat a bespoke widget as form fidelity, not a screen.

## 2026-06-15 — Source-audit reconciliation + missing surfaces

A five-lane audit of `odoo.css` and the component fragments against the real
Odoo 19 source surfaced verifiable drift and a handful of recognizable
surfaces that had no catalog representation at all. All findings cited a
specific source file:line so the fixes trace back; nothing is invented.

### Drift fixes (cited)

- **`o-autocomplete--dropdown-menu` z-index 100 → 1051.** Real source
  (`core/autocomplete/autocomplete.scss:5`) sets `z-index: $zindex-modal + 1`
  precisely because dropdowns rendered from inside an `.o_dialog` would
  otherwise sit BEHIND the modal. The catalog's `z-index: 100` reproduced that
  bug on every autocomplete-inside-dialog mock.
- **`o_notification_manager` positioning + bar width.** Catalog had
  `top: 12px` (over the navbar) and a 4px coloured left-border bar. Real
  source (`core/notifications/notification.scss:7` + `notification.variables.scss`)
  positions the manager via `inset: ($o-navbar-height * 1.15) $o-notification-margin auto $o-notification-margin`
  (≈ 53px down + 16px sides) with a media-breakpoint switch to a 400px
  right-anchored column on >= sm, and the bar is `$o-notification-bar-width: 0.5rem`
  (8px). The catalog now exposes a `.o_notification_bar` child element matching
  the real notification.xml structure, with a fallback `border-left: 8px` when
  the bar element is absent so existing mocks don't regress.
- **`o_form_sheet` horizontal alignment.** Catalog had `margin: 0 auto`
  (centered on ultra-wide). Real source comments
  (`views/form/form_controller.scss:240`) read literally "Always align to le left"
  via `margin-right: auto`. Sheet now pins to the left edge under the
  breadcrumb.
- **`o_form_label` conditional modifiers.** Real source applies
  `opacity: 0.66; font-weight: normal` on `.o_form_label_empty`,
  `.o_form_label_false`, `.o_form_label_readonly`
  (`form_controller.scss:606-609`). The catalog never rendered the muted
  state on labels whose field was empty/readonly; added.

### Missing tokens added

Pulled forward from `primary_variables.scss` / `secondary_variables.scss`
into `:root` so component blocks can reference them without recourse to
magic numbers:

- `--o-modal-lg` (980), `--o-modal-md` (650) — Dialog `size` prop variants.
- `--o-dropdown-hpadding` (20), `--o-dropdown-vpadding` (3),
  `--o-dropdown-max-height` (70vh).
- `--o-statbutton-spacing` (6) — gap between stat-buttons in the box.
- `--o-navbar-height` (46).
- `--o-main-link-color` (#6b4761 = `darken($o-brand-primary, 5%)`),
  `--o-main-headings-color`, `--o-main-code-color` (#d2317b),
  `--o-brand-secondary` (#8f8f8f), `--o-component-active-color`.
- `--o-opacity-disabled` (0.5), `--o-opacity-muted` (0.76) — used by
  modifier classes (and now wired into `.o_form_label_*`).
- `--o-easing-enter` (`cubic-bezier(0.05, 0.7, 0.1, 1.0)`),
  `--o-easing-exit` (`cubic-bezier(0.3, 0.0, 0.8, 0.15)`) — applied to
  notification transitions; available for walkthrough.js.

### New surfaces (recognizable Odoo, source-cited)

Five surfaces were either missing entirely or rendered without their
distinctive Odoo decoration. Added CSS blocks in `odoo.css` and component
fragments where the surface stands alone:

- **No-content helper** (`o_view_nocontent` / `o_nocontent_help`) —
  `views/action_helper.xml`, `views/view.scss:7-59`, `scss/utils.scss:290-333`.
  Odoo 20: absolute overlay centred over the whole view body; 800px text block
  (sale `services_and_material.scss`); bold black 20px first `<p>`, 16px hint.
  Illustration chosen by the title `<p>` class (`o_view_nocontent_smiling_face`
  / `_neutral_face` / `_empty_folder`) and inlined from `#o-nocontent-*` sprite
  symbols. Sample-data state `o_view_sample_data` (opacity .06). Fragment:
  `components/no_content.html`.
- **Tour pointer** (`o_tour_pointer`) — `web_tour/tour_pointer.{xml,scss}`.
  Brand-purple bubble with step number + directional caret (left / right /
  top / bottom). Fragment: `components/tour_pointer.html`.
- **Command palette** (`o_command_palette`, Ctrl+K) —
  `core/commands/command_palette.{xml,scss}`. Modal with search input,
  categorised result list, hotkey badges, footer hints. Fragment:
  `components/command_palette.html`.
- **In-card onboarding checklist** (`o_widget_account_onboarding` >
  `.col-auto.my-1` steps; `#o-circle .text-300` = not done, `#o-check-circle
  .text-success` = done; description only as the link's title tooltip) —
  `account/static/src/components/onboarding/onboarding.xml`, placed in the
  Accounting dashboard Tax Returns card (enterprise `account_reports`
  `account_journal_dashboard_view.xml:52-57`). Odoo 19/20 mount NO horizontal
  onboarding banner (`onboarding.onboarding_panel` is never rendered; no
  `banner_route`). Fragment: `components/onboarding.html`.
- **Grouped-list controls** (`o_group_buttons`, `o_group_pager` inside
  `o_group_header`) — `views/list/list_renderer.scss`. Hover-revealed
  per-group action buttons + record pager. No new fragment — extend
  `components/list_view.html`'s group-header rows when needed.

### Kanban decoration (recognizable Odoo, was missing)

- **`o_kanban_color_1` … `o_kanban_color_11` colour stripe** — derived from
  `kanban_record.scss:146-156` ($o-colors palette in `secondary_variables.scss`).
  3px right-edge stripe with a 1px inner 50%-alpha rule, matching the
  outer/inner border pattern Odoo uses.
- **`o_kanban_hover` drag-target highlight** — `kanban_controller.scss:228-238`.
  Brand-tinted column bg + inset left/right rules while a card is being
  dragged over.
- **`o_kanban_ghost` placeholder card** — invisible-but-space-occupying
  card used by the kanban renderer to keep grid shape during drag.
- **`o_kanban_quick_create` compact form** — top-of-column "+ Add" card
  used by quick-create flows.
- **`o_column_progress` segmented counter bar** — kanban column progress
  segments by status (success / warning / danger / info / muted).

### Deliberately NOT changed (documented intent vs apparent drift)

*(Superseded 2026-10-07: navbar height, chatter width, label weight and sheet
padding all use the real values now — 46px navbar at a 16px root, 530px
chatter, 500-weight labels, 24px sheet padding.)*

## 2026-06-15 — Cross-surface drift audit + reconciliation (Chatter / Portal / Account Reports / Website Forms / POS / Wizards)

A six-lane audit (one per surface) against the real Odoo 19 source, anchored
against four real mock packages (TEST001-TEST004) that exhibited the drift.
Each fix cites a specific source file:line; no class was invented.

### Pattern observed across all six surfaces

**Surface-native class names had drifted.** The catalog had its own
simplified vocabulary (`.o-mail-Chatter-topbar`-with-flat-tabs,
`.pos-topbar` / `.pos-topbar-info`, `.o_account_report_line_section`,
`.o_dialog_*` only, flat website-form fields) that visually approximated
Odoo but missed structural shapes that make the real Odoo recognisable:
- Two-column message layout (sidebar + content) in chatter
- Sticky topbar region (`.o-mail-Chatter-top`) above scrollable thread
- `.pos-topheader > .pos-leftheader / .pos-centerheader / .pos-rightheader`
  in POS
- Multi-row `<thead class="sticky">` + `line_level_N` indent + `btn_foldable`
  caret button in account reports
- 3-level nested Bootstrap grid (`col-12 > row > col-sm-auto label +
  col-sm input`) in website forms
- Bootstrap modal class aliases (`.modal-dialog`, `.modal-content`,
  `.modal-header`, `.modal-body`, `.modal-footer`) on dialogs

Authors faced with shapes the catalog didn't surface invented their own
classes (TEST002's `.pos-topbar-info`, TEST004's `o_portal_table`,
TEST003's `<span class="o_pivot_expand_btn">[+]</span>`). The systemic
fix is to **surface the real Odoo classes as catalog citizens**, keep the
old class names working as aliases for back-compat, and document each
surface's structural rules in `style_guide.md` so future generations
follow the canonical shape.

### Chatter — `o-mail-Chatter`

*(Superseded 2026-10-07: the `is-collapsed` composer, the
`<ul class="o_mail_tracking_value">` tracking list and the sidebar-beside-core
message nesting were replaced — see `chatter.html` and the 2026-10-07 entry.)*

- Rewrote the fragment to use the real Odoo three-piece structure:
  `.o-mail-Chatter-top` (sticky topbar + composer) + `.o-mail-Chatter-content`
  (scrollable thread + activities).
- Renamed topbar buttons to real Odoo names: `.o-mail-Chatter-sendMessage`,
  `.o-mail-Chatter-logNote`, `.o-mail-Chatter-activity`, `.o-mail-Chatter-topbarGrow`,
  `.o-mail-Chatter-search`.
- Followers cluster is now a single button (`.o-mail-Followers-button`) with
  a user icon + `<sup class="o-mail-Followers-counter">N</sup>` superscript
  — NOT the prior overlapping-avatars + "N Followers" text label.
- Messages are now **two-column**: `.o-mail-Message-sidebar` (48px) with
  `.o-mail-Message-avatarContainer` + `.o-mail-Message-core` with
  `.o-mail-Message-header` and `.o-mail-Message-contentContainer`.
- Composer hidden by default (`.is-collapsed`); toggle via topbar buttons
  carrying `data-mock-toggle="composer-msg" / "composer-note"`.
- Added activity list collapsible header (`.o-mail-ActivityList-header`)
  and activity card sidebar/core split (`.o-mail-Activity-sidebar` /
  `.o-mail-Activity-core`).
- Added tracking-value rendering (`<ul class="o_mail_tracking_value">` with
  field name, old (struck through), arrow, new value).

### Portal — `.o_portal`

The catalog's portal fragment was already correct (navbar, sidebar amount
lead, `o_portal_kv` / `o_portal_note` / `o_portal_actions`). The drift in
TEST004 (missing navbar, ad-hoc `o_portal_table` / `o_portal_title`) is a
mock-level deviation, not a catalog gap. Added explicit "Portal structural
rules" to `style_guide.md` so future generations follow the catalog.

### Account Reports — `.account_report`

*(Superseded 2026-10-07: `.o_account_reports_page`, the `.wrapper` / `.content`
cells and every `o_account_report_*` alias below are retired — the report is a
client action with its own control panel.)*

- Rewrote the fragment to use real Odoo class vocabulary:
  `<div class="account_report"><table class="table table-borderless table-hover"><thead class="sticky">…`.
- Replaced custom catalog classes with real Odoo state classes:
  `line_level_0` (top-level section, gray bg + bold), `line_level_2..16`
  (progressive indent on `.line_name .wrapper`), `total` (bold), `unfolded`,
  `empty` (spacer row, no border-bottom).
- Replaced literal `[+]` / `[−]` foldable markers with
  `<button class="btn_foldable">` + `<svg class="o_icon"><use href="#o-caret-down"/></svg>` /
  `#o-caret-right`. Added `o-caret-right` to the icon sprite.
- Added `.line_cell.numeric > .wrapper { justify-content: flex-end }` for
  right-aligned values per Odoo source (account_report.scss:217).
- Kept the older `.o_account_report_line_section` / `_total` / `_grandtotal`
  classes as ALIASES so existing TEST003 still renders correctly.

### Website Forms — `.s_website_form`

- Rewrote the fragment to use the real **3-level nested Bootstrap grid**:
  `.s_website_form_field.col-12.mb-3 > .row > label.col-sm-auto + .col-sm > input.form-control`.
- Added `form-control`, `form-select`, `form-check-input`, `is-invalid`,
  `invalid-feedback` CSS so Bootstrap-vocabulary inputs render correctly.
- Added the real submit-row structure: `.col-12.s_website_form_submit.text-end.s_website_form_no_submit_label`
  with a 200px label spacer div + `#s_website_form_result` slot + the button.
- Added `@media (max-width: 575.98px)` rule so labels stack above inputs
  on mobile — matching Odoo's real responsive behaviour (which the flat
  flex layout broke).
- Kept the catalog's simplified flex-row `.s_website_form_field`
  (`display: flex; gap: 16px`) working for existing TEST002/TEST004 mocks.

### POS — `.pos`

- Added the real Odoo class hierarchy alongside the existing aliases:
  `.pos-topheader > .pos-leftheader (Register/Orders + .navbar-separator
  + tabs) + .pos-centerheader (logo when idle) + .pos-rightheader >
  .status-buttons`.
- Added `.btn-light` + `.btn-lg` + `.lh-lg` styles for the real POS
  topheader buttons (per `navbar.xml:9`).
- Added the real payment-methods classes: `.paymentmethods-container >
  .paymentmethods > .paymentmethod` (kept `.pos-payment` / `.pos-paymentmethod`
  as aliases).
- Rewrote the POS fragment to use real Odoo names. Removed encouragement
  of the ad-hoc `.pos-topbar-info` / `.pos-cashier` / `.pos-session` panel
  pattern (TEST002 used it, but Odoo doesn't ship that block — cashier
  name is a single `<CashierName>` on the right, hidden on mobile).

### Wizards / Dialogs — `.o_dialog`

- Added Bootstrap modal CSS aliases so the real Odoo Dialog structure works:
  `.modal.d-block`, `.modal-dialog`, `.modal-dialog-centered`, `.modal-content`,
  `.modal-header`, `.modal-title`, `.modal-body`, `.modal-footer`, `.btn-close`.
- Added size variants on both `.o_dialog` and `.modal-dialog`:
  `.modal-sm` (360px), `.modal-md` (650px = default), `.modal-lg` (980px),
  `.modal-xl` (1140px).
- Added responsive footer alignment per real Odoo (`justify-content-around` on
  mobile, `justify-content-md-start` on desktop) when the footer carries
  Bootstrap utility classes.
- Documented the **footer button DOM order rule** in both the fragment and
  `style_guide.md`: PRIMARY first, SECONDARY second. CSS flex arranges them
  visually on desktop without DOM reordering.
- Documented the catalog's two valid shapes (simplified `.o_dialog_*` vs.
  real Bootstrap `.modal-*` nest); both render identically — author should
  pick one consistently across a package, not mix.

### Style guide updates

- Added a new "Surface-specific structural rules" section to
  `style_guide.md` capturing the rules for each surface (chatter, portal,
  account report, website form, POS, dialog). This gives future
  generations explicit canonical shapes to follow rather than re-deriving
  from source.
- Expanded the Source map to cover the additional surfaces (chatter,
  dialog, notification, autocomplete, portal, account report, website
  form, POS).

### Lessons learnt

- **Drift compounds when the catalog "approximates" instead of mirroring.**
  A simplified topbar layout in the catalog teaches authors to invent
  their own simplified extensions; the next quarter's drift is a custom
  `.pos-topbar-info` block. Mirror Odoo's class names verbatim so authors
  can't easily invent on top.
- **Surface boundaries are load-bearing.** Portal forms must use
  `s_website_form_*`, not backend `o_field_row`; POS popups must use
  Dialog over `.pos`, not backend chrome in `.rightpane`; chatter messages
  must use two-column sidebar+content. Each boundary the catalog enforces
  is one class of fidelity bug authors can't make.
- **Real Odoo uses Bootstrap.** Catalog has been gradually adding real
  Bootstrap class support (`form-control`, `modal-*`, `col-12`, `col-sm-auto`).
  This pass made the alignment explicit: where Odoo uses Bootstrap, the
  catalog now does too, and the catalog's own classes alias to the same
  visual.

## 2026-06-17 — Sprite catalog gap-fill (view switcher · pivot/graph toolbar · chrome glyphs · app icons · discuss rebuild)

*(Superseded 2026-10-07: the FontAwesome-shape glyphs and tinted app icons were
replaced by the real Odoo 20 artwork under the same ids, and `discuss.html` was
rebuilt for Odoo 20 — no Inbox / Starred / History sidebar.)*

Two-commit pass on the icon catalog. Triggered by a mock author noting
the control panel didn't carry the right glyphs in the view switcher
and that the pivot view's Measures / Insert in Spreadsheet / Flip Axis
buttons were rendered in the wrong control-panel slot.

### Pattern observed

The catalog's sprite was a FontAwesome-shape proxy for what real Odoo 19
renders. Three failure modes followed:
- **Wrong shape for the right slot** — view-switcher cells used FA
  `o-list` / `o-th-large`. Real Odoo uses `oi-view-list` / `oi-view-kanban`
  with column-bar / dot-row glyphs that read differently.
- **No glyph for a high-frequency Odoo action** — `o-pencil`, `o-trash`,
  `o-envelope`, `o-paper-plane`, `o-info-circle`, `o-lock`, `o-archive`,
  `o-truck`, `o-tag` etc. were absent. Mocks that needed them either
  invented markup or reached for the wrong placeholder (e.g. `o-list`
  next to a database picker, `o-th-large` next to "Use a Passkey").
- **Catalog comment contradicted source** — `chart_views.html` had a NOTE
  telling generators to put the pivot toolbar in `.o_control_panel_main_buttons`.
  The real `pivot_renderer.xml:6` renders the toolbar OUTSIDE the control
  panel via `<t t-call="{{ props.buttonTemplate }}"/>` above the table.
  The generator followed the wrong NOTE.

### Commit 1 — `808fb64` view-switcher icons + pivot/graph toolbar slot

- **Six Odoo-shape view glyphs** added to `icons.svg`:
  `o-view-list`, `o-view-kanban`, `o-view-gantt`, `o-view-cohort`,
  `o-view-hierarchy`, `o-view-grid`. Each approximates the matching
  `oi-view-*` font shape (column-bar kanban, dot-row list, stepped
  cohort, etc.).
- **control_panel.html** view-switcher block repointed at the new
  glyphs; commented enterprise-only entries added for gantt / cohort /
  hierarchy / grid. The control-panel matrix row for reporting now
  reads "empty (toolbar lives in `.o_pivot_buttons` / `.o_graph_buttons`)".
- **chart_views.html** rewritten: the contradictory NOTE removed,
  worked `.o_pivot_buttons` and `.o_graph_buttons` examples added with
  source citations (pivot_controller.xml, pivot_renderer.xml,
  graph_controller.xml, graph_renderer.xml). The fragment now
  demonstrates the correct shape.
- **odoo.css** `.o_pivot_buttons` rules extended to also cover
  `.o_graph_buttons` (same flex shape, padding, gap).
- `_gallery.html` synced.

### Commit 2 — `82e33e5` chrome + app icon gap-fill, discuss rebuild

- **22 chrome glyphs** added to `icons.svg`. Tallied from real Odoo's
  `fa fa-…` and `oi oi-…` usage across `web/static/src/views`,
  `web/webclient`, `mail/static/src`, `pos`, `portal`, `website`:
  `o-pencil`, `o-trash`, `o-paper-plane`, `o-info-circle`,
  `o-question-circle`, `o-envelope`, `o-archive`, `o-unarchive`,
  `o-lock`, `o-launch`, `o-external-link`, `o-cloud-upload`,
  `o-arrow-left`, `o-arrow-right`, `o-tag`, `o-truck`, `o-microphone`,
  `o-phone`, `o-settings-adjust`, `o-spinner`, `o-key`, `o-bell`.
- **12 enterprise app icons** added to `app-icons.svg`:
  `o-app-helpdesk`, `o-app-mrp`, `o-app-marketing`, `o-app-fsm`,
  `o-app-subscriptions`, `o-app-rental`, `o-app-maintenance`,
  `o-app-recruitment`, `o-app-survey`, `o-app-elearning`,
  `o-app-mass-mailing`, `o-app-quality`. Recommended brand colors
  documented as a sprite-header comment block + the new "Sprite
  catalog" section in `style_guide.md`.
- **Three nonsensical icon uses corrected**:
  - `login.html` database picker: `o-list` → `o-caret-down`.
  - `login_website.html` "Use a Passkey": `o-th-large` → `o-key`.
  - `command_palette.html` Apps results: `o-list` / `o-th-large` →
    `o-app-sales` / `o-app-inventory` (real Odoo's command palette
    renders each app's own brand icon per result).
- **apps_menu.html extended** with all 12 new apps so the catalog
  gallery doubles as a brand-color crib.
- **discuss.html rebuilt** from a near-empty skeleton. The CSS already
  supported the richer shape; the fragment now exercises it:
  Inbox/Starred/History top section, Channels/DMs categories with `+`
  add buttons, channel header with search/phone/bell/cog actions, Today
  thread divider, message reactions, composer with toolbar (paperclip,
  microphone, comment) and a primary Send (`o-paper-plane`).

### Style guide updates

- New **"Sprite catalog (icons.svg + app-icons.svg)"** section in
  `style_guide.md` enumerating every chrome glyph (grouped by category)
  and every app icon with its brand color. Previously the only
  documentation was per-symbol inline comments in the SVG; authors had
  to grep. Now there's a table.
- Source map extended with two entries citing where the chrome glyphs
  and app icons were derived from (FA 4.7 free + `lib/odoo_ui_icons`
  for chrome; per-app `static/description/icon.png` for apps).

### Lessons learnt

- **A catalog comment that contradicts the source is worse than no
  comment.** `chart_views.html` had a NOTE explicitly telling the
  generator to put the toolbar in the wrong slot; that's how the bug
  was born. When a comment cites where it came from, it can be
  re-validated; an unsourced opinion ages into drift.
- **Missing assets compound into wrong assets.** Mocks that needed
  pencil/trash/envelope/key fell back on the closest-looking sprite
  id, which produced semantically wrong icons (`o-th-large` on a
  Passkey button, `o-list` on a username field). Filling the gaps
  removes the temptation.
- **Cite per-glyph provenance in the sprite.** Each new chrome glyph
  carries a one-line HTML comment naming the FA / OI source. On a
  version bump the per-symbol citation is what tells you whether a
  shape needs to track Odoo's evolution or stays parked at FA 4.7.

## 2026-10-07 — Recalibrated to real Odoo 20 Enterprise

The 2026-09-30 "19→20 refresh" checked class existence only (see the warning in
§ How to refresh) and missed the whole v20 redesign. This pass captured real v20
Enterprise screens on a demo DB, diffed `web` + `web_enterprise` SCSS values
and DOM, probed computed styles and rebuilt the catalog group by group; the
calibration kit (`scripts/calibrate/`, `calibration/screens/`) and
`_extract_icons.py` came out of it. `odoo.css` now opens with the stamp
"calibrated to Odoo 20 Enterprise". It supersedes every older entry it
contradicts.

- **Tokens / typography** — root 16px (the `html { font-size: 90% }` scaling and
  its 42px navbar are gone), body 14px / 21px; backend "bold" = 500, h1 33.6px.
  Teal `--o-action` #017e84 now drives links, checked, active / selected and
  focus (`--o-component-active-bg` #e6f2f3); plum only for `btn-primary`,
  `btn-outline-primary` and the notebook tab bar. Gray-200 #e7ebed, semantic
  #00a945 / #f59e0b / #ef4444, radius 6 / 4 / 8 / 12px; `body.o-community`
  switches the whole palette.
- **Buttons, badges, tags, inputs** — 33px buttons; `btn-secondary` = white with
  a #ced4da border (`o_btn_outline` a deprecated alias), `btn-light` icon
  buttons, teal `btn-link`. Status = `badge rounded-pill text-bg-*` 15% tints;
  tags = `o_tag o_badge badge rounded-pill o_tag_color_N` on the new OKLCH
  palette (the old palette was NOT "unchanged"). Real Bootstrap checkboxes /
  radios / switches; rounded-square one-initial avatars (`o_avatar_c0..7`); no
  resting input underline.
- **Icons** — `icons.svg` rebuilt from the real Material Symbols Outlined +
  `odoo_ui_icons` outlines under the same ids (filled vs outline in the id);
  `app-icons.svg` = the real multi-color `icon.svg` artwork, never tinted; the
  scaffolder inlines both sprites.
- **Navbar / home menu** — transparent over the page gray, no border, 46px;
  `o_menu_toggle.hasImage` with the current app's icon; sections without
  carets; systray timer / Ask AI / Messages / Activities / Studio / company /
  avatar. Dotted home background, tiles in menu-sequence order.
- **Control panel** — no bar of its own; one row: buttons + title + ⋮ action
  menu (the cog is gone) | centred pill search (tinted-icon facets, 3-column
  search menu) | pager button group + segmented view switcher. Two-line
  drill-down breadcrumb; a selection state that replaces the search.
- **Search panel** — transparent panel, icon section headers, teal active pill,
  fold toggle + collapsed strip; the view beside it becomes a white card.
- **List** — plain dark cells (relational included), 40px rows, `N records`
  group rows, label-less footer aggregates, `o_handle_cell` /
  `o_list_actions_header`, edge-to-edge inline one2many.
- **Form / chatter** — statusbar inside `.o_form_sheet_bg` on the gray
  (`btn-secondary` buttons, one bordered pipeline with a teal current stage);
  sheet 8px radius / 24px padding; boxed notebook; empty readonly fields render
  nothing; superscript `?`; real ribbon markup; smart buttons as one joined
  group. Chatter: 530px on the gray with its buttons on the statusbar row;
  topbar / composer / activity / thread markup rebuilt (bubbles, DateSection,
  one-line tracking, Done / Edit only).
- **Kanban / card** — `article.o_card_record` records, transparent stacked
  columns with 2-row headers, activity type glyphs, left color stripe,
  ungrouped tiles and row-style `.o_kanban_list`. **Card view removed**: v20
  `card` is the record template, not a switchable view (`card.html` deleted).
- **Settings** — app rail (`settings_tab > a.tab`, real icons, teal selection)
  + white card with `<h2>` bands and two-per-row checkbox boxes; Save /
  Discard + search in the one-row control panel.
- **Dialogs & overlays** — size decides design (sm 460 / md 620 minimal; lg 980
  / xl 1140 ruled), `h4.modal-title` + `.btn-close`, left-aligned footer with
  the primary first; UserError title **"Invalid Operation"** (never "User
  Error"); 25% + grayscale backdrop; shared `.o-dropdown--menu`; v20 toast,
  tooltip, command palette and tour pointer.
- **Reporting** — global-size toolbars between control panel and view; pivot
  add / minus boxes; graph palette + switches; calendar / gantt / map frames
  with pastel events; teal cohort; `activity_matrix.html` (activity.html
  removed); borderless timesheet grid; hierarchy cards;
  `dashboard_sidebar.html` (dashboard.html removed).
- **Other surfaces** — Discuss rebuilt (tab rail + list card, header card,
  bubbles, pill composer; no Inbox / Starred sidebar; rules scoped under
  `.o-mail-DiscussContent`); spreadsheet as a full-screen editor (own navbar,
  toolbar + composer row, canvas grid); Studio editor (left sidebar, editor
  menu bar, invisible hooks); account report as a client action with its own
  control panel (all `o_account_report_*` aliases and `o_account_reports_page`
  retired); empty state = overlay helper with the real illustrations +
  sample-data fade; `.alert` with a 3px left accent.
- **Onboarding retired** — Odoo 19/20 mount no horizontal onboarding banner;
  `onboarding.html` is now the in-card Accounting checklist.
- **Tooling** — the scaffolder reads the cover's Odoo version from SPEC_DATA
  `odoo_version` (fallback: the stamp) and inlines `icons.svg` +
  `app-icons.svg`; `_lint_mock.py` finds Enterprise under
  `versions/v*/enterprise` and prints a non-failing NOTE when a mock's cover
  version differs from the stamp. One catalog tracks the latest version;
  older-version mocks keep their copied assets.
- **Scope — NOT recalibrated in this pass (carried over from v19, treated as
  version-stable).** This pass redesigned the backend webclient. The public /
  frontend fragments were left as-is and have no v20 calibration-screen twin:
  `login.html`, `login_website.html`, `website.html`, `website_form.html`,
  `portal.html`, `portal_my.html`, `pos.html`, `checkout.html`, `report.html`.
  The single "Odoo 20" stamp does **not** assert these were re-verified against
  v20 source — it means the catalog's baseline is v20. Re-verify them (capture +
  twin + probe) on the next pass, or when a mock leans on one of these surfaces.

## 2026-10-30 — Custom-element identification

Mock-layer chrome (`annotations.css` + `walkthrough.js`, like the markers), not
Odoo chrome, so there is no Odoo screen to calibrate against; it reuses Odoo's
own pink (tag colour 9 in `odoo.css`: `#fec5d9` / `#671d3f`) and the
`web_ribbon` geometry (`odoo.css` § `.ribbon`) so it still reads as Odoo.

- **`mock-custom`** marks what the solution adds or changes. On an element:
  a light-pink highlight (`#ffe2ec`, the tag pink at 50% on white) —
  `walkthrough.js` appends a `.mock-custom-overlay` multiplied over the
  element and everything inside it (so a tab panel's list header and alert
  tint too), with a 3px ring of the same pink except on table cells. A
  ResizeObserver sizes it to what the element paints, so a list pulled up to
  the tabs and out to the sheet edges by negative margins is covered edge to
  edge. White and see-through areas turn pink, coloured ones keep their
  colour. A child element, not `::before` / `::after`, which the active tab
  bar, kanban colour stripes and selected-item checks already use. On a
  `.mock-screen`: a small corner **Custom** banner (`.mock-custom-banner`,
  one body-level fixed element shown while that screen is active): a 60%
  opaque band that reads as tag 9's fill `#fec5d9` over white, so the company
  name, avatar and view switcher under it still show, softened. `_gallery.html` shows
  the highlight on a field row, a list column and both button kinds.
- **Walkthrough bar:** a **Custom** chip (Show / Hide → `mock-custom-off` on
  `<body>`) beside Annotations; the bottom row splits in two like two variant
  chips, rendered only when the package marks something custom. The control
  cluster widened 290 → 340px so both halves read untruncated.
- **Gated like the field "?":** `interactions.md` § Custom elements (placement
  table), a sixth cover callout (`IF custom`, `_scaffold_mock.py` flag),
  `_lint_mock.py` `CUSTOM-UNMARKED` (a "?" field outside any custom mark) and
  `CUSTOM-PLACEMENT` (cover / overview, nested, inside a custom screen), plus
  rules in both mock anchors. Mocks built before this fail `CUSTOM-UNMARKED`
  until their custom elements are marked.
- Fixed in passing: `MARKER-TEXT` (and the absolute-marker `KNOWN-BAD` rule)
  stopped excluding the cover's `mock-marker-example` after 29f93ef widened the
  class match, so every canonical cover failed the lint; and
  `_render_mock_screens.py` only found sections whose class was exactly
  `mock-screen`, so it skipped any screen with a second class.

## Current baseline

- **Odoo version:** the one stamped on the first line of `catalog/odoo.css`
  (Odoo 20 Enterprise as of the 2026-10-07 entry). One catalog tracks the
  latest version; mocks for an older version keep their copied assets.
- **Derived from:** `versions/v<NN>/odoo/addons/` + `versions/v<NN>/enterprise/`
  (see Source map in `style_guide.md` for exact files), verified against the
  calibration screens.
- The palette defaults to **Enterprise**; `body.o-community` switches the whole
  palette (brand, links, radius, semantic colors, badges, tags, navbar) for a
  Community instance.
