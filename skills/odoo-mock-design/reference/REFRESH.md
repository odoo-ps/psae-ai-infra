# Refreshing the catalog on an Odoo version bump

The `catalog/` (odoo.css + component fragments + icons) is **hand-authored** from
Odoo source, not generated — a mechanical SCSS→CSS conversion drags in the whole
Bootstrap layer and defeats the "small, readable, self-contained" goal. So
refreshing is a deliberate, traceable edit, not a script run.

## When to refresh

- The repo's `odoo/` checkout moves to a new major version.
- A view the catalog covers gets a visible redesign upstream.
- A mock needs a view type not yet in the catalog (promote it from the
  "NOT in the starter catalog" list in `view_types.md`).

## How to refresh

1. Re-read the source files listed in the **Source map** at the bottom of
   `style_guide.md`. Diff against what the catalog currently encodes.
2. Update **tokens first** (`catalog/odoo.css` `:root`) from
   `scss/primary_variables.scss` + `scss/secondary_variables.scss`. These cascade
   to everything else.
3. Update component styles/fragments only where the upstream DOM/class names or
   layout actually changed. Keep the real Odoo class names.
4. Add any new icons to `catalog/icons.svg` and document them in `style_guide.md`.
5. Re-run the verification before considering the refresh done: render the
   catalog gallery (`python3 reference/scripts/_render_catalog.py`) and eyeball
   every component against the previous baseline; then build a sample mock, run
   `_lint_mock.py`, and open it in a browser. The gallery catches render
   regressions (stray markers, z-index, broken layout) the lint is blind to.

## Catalog fix log

Rendering bugs found while generating mocks and fixed in the catalog source.
Both were latent in every mock until corrected — keep an eye out for the same
class of bug (CSS that styles a class but forgets a structural reset / stacking
order) on the next version bump.

- **`.o_breadcrumb` list-marker reset** — fixed 2026-06-12 (`odoo.css`).
  Breadcrumbs render as an `<ol>`/`<li>` list (`control_panel.html`) but the
  flex rule never reset the markers, so items showed stray "1."/"2." numbers.
  Added `list-style: none; margin: 0; padding: 0;` to `.o_breadcrumb`.

- **Walkthrough bar below the dialog backdrop** — fixed 2026-06-12
  (`annotations.css`). `.o_dialog_backdrop` (`z-index: 1000; position: fixed;
  inset: 0`) covered the whole viewport, so on any wizard/dialog screen it sat
  over the `.mock-walkthrough` bar (was `z-index: 900`) and swallowed its
  Prev/Next/Annotations clicks. Bumped the bar to `z-index: 1100` (above the
  dialog). The nav chrome must always sit above modals.

## Design refresh log

- **Odoo 19 fidelity pass** — 2026-06-12, calibrated against a real Odoo 19
  Sales Order form. Catalog changes that apply across all views:
  - Removed the persistent **dotted field underline** (`o_field_widget`) — Odoo
    15+ renders readonly fields as clean text. Required inputs keep a subtle
    solid cue only.
  - Added **teal link styling** (`o_form_link` / `o_list_link`,
    `--o-enterprise-action-color`) for relational/URL values — the look had them
    flat dark before.
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
  - **account_report.html** (enterprise `account_reports`) — filter bar +
    hierarchical foldable P&L/Balance-Sheet lines + grandtotal.
  - **spreadsheet.html** (`spreadsheet`/o-spreadsheet) — toolbar, formula bar,
    lettered grid, sheet tabs.
  - **gantt.html** (enterprise `web_gantt`), **activity.html** (`mail`),
    **dashboard.html** (`spreadsheet_dashboard`, KPI tiles + chart/pivot tiles).
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
  2026-06-12.
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
  Deliberately NOT changed (considered, kept): chatter width (kept ~360 for
  page-fit vs Odoo's 530 min), notebook active-tab brand underline + labels at
  normal weight (both match the user's real screenshots), minor kanban spacing
  and button padding (negligible, not load-bearing).

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
    or font-awesome class + bg + fg color). The catalog uses the
    class-based variant — inline `style="background:#xxx"` on
    `.o_app_icon` + a single-character glyph. App grid is 6 columns max,
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
- `--o-navbar-height` (46) — reference value; the rendered navbar stays at
  the documented 90%-scaled 42px via the global `html { font-size: 90% }`.
- `--o-main-link-color` (#6b4761 = `darken($o-brand-primary, 5%)`),
  `--o-main-headings-color`, `--o-main-code-color` (#d2317b),
  `--o-brand-secondary` (#8f8f8f), `--o-component-active-color`.
- `--o-opacity-disabled` (0.5), `--o-opacity-muted` (0.76) — used by
  modifier classes (and now wired into `.o_form_label_*`).
- `--o-easing-enter` (`cubic-bezier(0.05, 0.7, 0.1, 1.0)`),
  `--o-easing-exit` (`cubic-bezier(0.3, 0.0, 0.8, 0.15)`) — applied to
  notification and onboarding transitions; available for walkthrough.js.

### New surfaces (recognizable Odoo, source-cited)

Five surfaces were either missing entirely or rendered without their
distinctive Odoo decoration. Added CSS blocks in `odoo.css` and component
fragments where the surface stands alone:

- **No-content helper** (`o_view_nocontent` / `o_nocontent_help`) —
  `views/action_helper.{xml,js}`. Empty-state title + hint + optional
  illustration glyph. Fragment: `components/no_content.html`.
- **Tour pointer** (`o_tour_pointer`) — `web_tour/tour_pointer.{xml,scss}`.
  Brand-purple bubble with step number + directional caret (left / right /
  top / bottom). Fragment: `components/tour_pointer.html`.
- **Command palette** (`o_command_palette`, Ctrl+K) —
  `core/commands/command_palette.{xml,scss}`. Modal with search input,
  categorised result list, hotkey badges, footer hints. Fragment:
  `components/command_palette.html`.
- **Onboarding banner** (`o_onboarding_container`, `o_onboarding_step` +
  `_done` / `_just_done` modifiers) — `addons/onboarding/views/`.
  Horizontal progress strip on app dashboards. Fragment:
  `components/onboarding.html`.
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

- **Navbar rendered height 42px (vs source 46px).** Already an intentional
  10% scale-down via `html { font-size: 90% }` — the new
  `--o-navbar-height: 46px` token preserves the source value for math
  (toast positioning) without changing the rendered navbar.
- **Chatter width ~360-420px (vs source ~530px).** Documented in the
  earlier "Full source-audit pass" log entry as a deliberate
  page-fit trade-off.
- **Form-label weight = normal** (catalog) vs bold (`form_controller.scss:600`).
  The catalog matches the in-group case (`form_controller.scss:397`
  `.o_group .o_form_label { font-weight: normal }`) which is overwhelmingly
  what users see; only labels OUTSIDE a group are bold, and mocks rarely
  render those.
- **Form-sheet padding 24px/32px (no breakpoint shrink at xxl).** Catalog
  intentionally renders one density; the responsive shrink in source is
  marginal vs the readability cost of variable padding across mocks.

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

## Current baseline

- **Odoo version:** 19
- **Derived from:** `odoo/addons/web/static/src/` (see Source map in
  `style_guide.md` for exact files).
- Brand color in the catalog defaults to the **enterprise** palette (`#714B67`),
  the common deployment. Switch `--o-brand-primary`/`--o-action` to
  `--o-community-color` (`#71639e`) in `odoo.css` if mocking a community instance.
