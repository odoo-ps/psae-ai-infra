# Odoo view types — anatomy & when to mock each

Runtime-read catalog. When mapping a workflow step to a screen, pick the view
type that matches what the user actually does at that step, then compose the
screen from `catalog/` fragments. **Read this and `style_guide.md` — do not
re-derive styling from Odoo source at generation time.** The catalog already
encodes it, for the Odoo version stamped on the first line of
`catalog/odoo.css` (`calibrated to Odoo NN`); anatomy below describes that
version.

## Density — match the workflow, not a quota

A mock screen reads as "real Odoo" when its density matches what the
*workflow actually requires*. Padding to hit a row count or field count
turns the mock into bulk; under-populating turns it into a wireframe.
Aim for **the smallest faithful representation of what the user sees at
that step.**

| View type | Density anchor (aim for) |
|---|---|
| **form** | Carry the field groups + notebook tabs the **brief actually references** for this step, plus the standard fields that live where Odoo puts them (discovered from source per `field_placement.md`). Don't enumerate every field on the real model; don't strip the form to only the net-new ones. The chatter, statusbar, and smart buttons belong only when the step engages them. |
| **list** | Enough rows to communicate the shape — typically 3–6. More only when row count *is* the message (a picker showing "there are 8 lots to choose from"). Mix state values only when that diversity is load-bearing for the step. |
| **kanban** | Card ornaments that the brief uses — priority/tags/deadlines/avatar when the workflow names them. A bare card on an unstyled column is also valid when the brief doesn't mention ornaments. |
| **chatter** | Two or three entries that match the flow the brief describes (e.g. confirmation log + customer notification), not a checklist of message-genre buckets. The chatter exists to prove the audit tail is on; content follows the workflow. |
| **dialog / wizard** | Show the inputs the user supplies + the surrounding context (counters, running totals) the brief defines. Don't enumerate picker options beyond what's needed to read the picker shape. |
| **dashboard / chart** | Token-styled placeholder with one believable value + legend per tile. |

**Anti-pattern: padding for density.** Five extra list rows, an empty
notebook tab, a third chatter entry "to look populated" — all bulk. The
reader's question is *"what would I see here in production?"* — your
density answer should be **just enough** to make that question answer
itself.

**Anti-pattern: stripping for minimalism.** A sale-order form showing
only the net-new field reads as a wireframe. Standard fields surrounding
the solution provide the recognition that the mock *is* Odoo.

The calibration target is **the density of a screen at this step in a
real engagement** — not a maximum, not a minimum.

Every screen is the same outer shell:

```
<section class="mock-screen" data-screen="ID" data-title="..." data-desc="...">
  <div class="o_web_client">
    <div class="o_action_manager">
      <!-- navbar.html -->
      <!-- control_panel.html (trim to what the view needs) -->
      <!-- ONE view fragment: form_view | list_view | kanban | ... -->
    </div>
  </div>
  <!-- optional dialog.html overlay -->
</section>
```

The page is one gray canvas: navbar, control panel and search panel are
transparent on it; only the view surfaces (form sheet, list, kanban cards,
graph canvas) are white.

---

## form — a single record

**Use when** the step is "open / edit / act on one record" (a quotation, a
contract, an employee). The workhorse screen for most workflows.

- **Fragment:** `components/form_view.html`
- **Anatomy:** `.o_form_view > .o_form_sheet_bg > [.o_form_statusbar,
  .o_form_sheet]`. The statusbar (left action buttons + right status
  pipeline) is the FIRST child of `.o_form_sheet_bg`, on the gray page with
  no white strip; the sheet below it holds title → two-column field groups →
  notebook tabs. Never put the statusbar directly under `.o_form_view`.
  **Smart buttons are NOT in the sheet** — they render in the **control
  panel's centred `.o_control_panel_actions` cell** (see `control_panel.html`);
  the sheet starts at the title. (Older Odoo drew the box inside the sheet —
  don't.)
- **Button placement — don't duplicate.** A record's workflow buttons (Confirm,
  Create Invoice, Validate, …) live in the **form statusbar only**: every one
  `btn btn-secondary`, plus at most one `btn btn-primary` for the main next
  step. On a form, the control panel above carries the outlined New, the
  two-line breadcrumb + ⋮ and the pager (no view switcher on forms) — it does
  NOT repeat the workflow buttons. Putting the same buttons in both
  `o_control_panel_main_buttons` and `o_statusbar_buttons` renders them twice
  and reads as a bug. (List/kanban screens are the opposite: having no
  statusbar, their New and `display="always"` header buttons live in the
  control panel; other list header buttons appear only while records are
  selected.)
- **Add a chatter** (`components/chatter.html`) when the step involves
  messaging, logging, activities, or an audit trail — wrap `.o_form_sheet_bg`
  + `aside.o-mail-Chatter` in `.o_content_with_chatter`. The chatter is a
  column on the same gray page (no border) whose topbar lines up with the
  statusbar buttons.
- **Status pipeline:** one bordered group inside `.o_field_widget.o_field_statusbar`,
  stages left → right in workflow order; mark the active stage with
  `o_arrow_button_current` (teal tint, never a solid purple fill). This is the
  single most recognisable Odoo form cue — get it right.
- **Source:** `odoo/addons/web/static/src/views/form/` +
  `enterprise/web_enterprise/static/src/views/form/`.

### Custom field widgets (solution-added OWL components)

When the spec adds a **bespoke OWL field widget** — a small display component
registered via `registry.category('fields').add(...)` and bundled in
`web.assets_backend` — it is **not a new screen**. It renders inside the same
`.o_field_widget` cell a standard field would, on whatever form already covers
that record. Treat it as a per-field fidelity detail of the form, not a
coverage-floor surface.

- **Fragment:** `components/custom_field_widget.html` — generic shapes a small
  display widget usually takes: a **status pill** (`.badge.rounded-pill`), an
  **icon+value pill** (`.o_cw_pill` + inline `<use>` glyph, e.g. a live FX rate),
  and a **meter/gauge** (`.o_cw_meter`, e.g. utilisation or score). Pick the
  closest shape and relabel.
- **Display only.** The widget shows a value; it never computes in a mock. Drive
  any state change with the screen's State axis, not live logic.
- **Flag it as custom.** Put the `o_field_help` "?" on the field's label and
  `mock-custom` on its `.o_field_row` (same as a custom standard field — see
  `interactions.md` § Custom-field help and § Custom elements), so the reader
  sees it's solution-added.
- **Source:** `odoo/addons/web/static/src/views/fields/` (standard widgets) +
  `standardFieldProps`.

## list (tree) — many records, tabular

**Use when** the step is "find / scan / compare / pick from many records", or as
an editable sub-table inside a form notebook (order lines, invoice lines).

- **Fragment:** `components/list_view.html`
- **Anatomy:** sticky gray header row → selector column → data rows → optional
  grouped headers (`o_group_header`, "Name  N records") → footer aggregates
  under their numeric columns (no "Total" label). Right-align numeric columns
  with `o_list_number`. Cells are plain dark text, relational columns included;
  the reference column is `fw-bold`; statuses are `badge rounded-pill text-bg-*`
  (soft tint), many2many values `o_tag` pills.
- **Inline one2many** (order lines): the `.o_field_x2many_list` wrapper inside
  the notebook page, flush under the tabs, ending with its create row ("Add a
  line").
- **Keep** the pager + view switcher in the control panel for list screens.
- **Source:** `odoo/addons/web/static/src/views/list/` +
  `enterprise/web_enterprise/static/src/views/list/`.

## kanban — cards in columns

**Use when** the step is about pipeline/stage progression, visual triage, or
drag-between-states (CRM pipeline, recruitment, project tasks) — or when the
brief wants scannable summary cards (ungrouped layout).

- **Fragment:** `components/kanban.html`
- **Anatomy:** each record is an `<article class="o_card_record o_kanban_record">`
  (title, plain lines, tags, a `<footer>` with priority + activity left and
  avatar right). Pick one layout per view:
  - **grouped** — transparent columns (`o_kanban_group`) of STACKED cards; a
    two-row header (title + hover cog + circle quick-add, then the progress
    bar + aggregate when the view has one); done-type stages may render
    folded;
  - **ungrouped tiles** — a wrapping grid of cards (the summary-card layout);
  - **image cards** — photo aside + body (Employees);
  - **row-style** — `.o_kanban_list` full-width rows (Time Off, Surveys).
- **Source:** `odoo/addons/web/static/src/views/kanban/` +
  `web/static/src/views/card/card.scss` +
  `enterprise/web_enterprise/static/src/views/card/card.scss` +
  `enterprise/web_enterprise/static/src/views/kanban/{kanban_controller.scss,kanban_header.xml}`.

## card — not a view you can switch to

`card` is the reusable **record template** (`ir.ui.view` type `card`,
inlined into kanban via `card_id`), rendered as `<article class="o_card_record">`
in kanban and in calendar / gantt / map popovers. It has no view-switcher
entry and no fragment of its own. For summary tiles use `components/kanban.html`
layout 3 (ungrouped).

## dialog / wizard — a modal step

**Use when** the step is a transient action that pops a modal: a confirmation, a
`TransientModel` wizard (e.g. "Validate delivery", "Register payment").

- **Fragment:** `components/dialog.html` — rendered over the underlying screen so
  the backdrop dims it. Wire the footer button's `data-mock-goto` to the screen
  the wizard produces.
- **Size decides the design:** confirmations and every UserError /
  ValidationError → `modal-sm` (minimal, no rules); act_window wizards, form
  dialogs and the Search More picker → no size class (default lg, ruled
  header/footer). Footer: primary first (leftmost), then `btn-secondary`;
  left-aligned.

## search panel — left-hand filters

**Use only when** the real action's search view declares a `<searchpanel>`
(Employees, Time Off, Allocations, Chart of Accounts, product catalog …);
never on Sales Orders / Invoices / CRM.

- **Fragment:** `components/search_panel.html` — it replaces the view body
  under `.o_control_panel`: `<main class="o_content o_component_with_search_panel">`
  = `.o_search_panel` + `.o_search_panel_resize` + the view. A list or graph
  canvas beside it becomes a white rounded card; kanban cards sit on the gray.
  Never hand-roll an inline flex wrapper or inline panel styles.

---

## Chart / grid views — on-brand placeholders

`components/chart_views.html` ships static, recognizably-Odoo placeholders for
**graph** (bar), **pivot** (cross-tab grid), and the **calendar** month grid
(used inside `calendar_week.html`'s header + frame). Use them only when a
*reporting* step genuinely needs one — a mock should land its decision points on
form / list / kanban. Their toolbars (Measures, Spreadsheet, …) form a row
between the control panel and the view, on the gray page. **Never embed a
charting library** — that breaks self-containment; the placeholders are CSS +
tokens only.

## View types still NOT in the catalog

Coverage is now broad — every standard view type plus the major app surfaces have
fragments (see below). Only legacy/niche surfaces remain unbuilt, e.g. the
**board** legacy "My Dashboard". If a step needs one, build it from `odoo.css`
tokens (don't invent colors), keep it recognisably Odoo, and add a note to
`REFRESH.md` proposing promotion.

---

## App surfaces (beyond the backend webclient)

These are whole surfaces that don't share the backend chrome. Each has a catalog
fragment + token-based CSS; all are static and self-contained (no charting/grid
libraries, no images). Use the real class names so a dev recognises them.

- **Point of Sale** — `components/pos.html` (`point_of_sale`). Full-screen touch
  app: left order/cart + numpad + Payment, right category bar + product grid.
  **No backend navbar** — render `.pos` as the whole screen. Payment-screen
  variant in the fragment.
- **Website / eCommerce** — `components/website.html` (`website`,
  `website_sale`). Public frontend with its own light header; shop grid
  (`oe_website_sale` / `o_wsale_products_grid`) and a product-page variant. Light
  theme, not backend gray.
- **eCommerce checkout** — `components/checkout.html` (`website_sale`). The
  address / payment / confirmation checkout flow (`o_wsale_checkout*`); use for a
  "place order" / payment step rather than reusing the shop grid in `website.html`.
- **Accounting report** — `components/account_report.html` (enterprise
  `account_reports`). Standard control panel (Print + title/cog + filter
  buttons), info alert, centred white card table with hierarchical
  `tr.line_level_N` rows (level-0 gray bands, `.total` / `.unfolded` /
  `.fw-bold`), right-aligned `td.line_cell.numeric` amounts.
- **Spreadsheet** — `components/spreadsheet.html` (Enterprise
  `documents_spreadsheet` / `spreadsheet_edition`; o-spreadsheet). Full-screen
  action: its own navbar (Spreadsheet icon + brand, breadcrumb, file name,
  "Saved"), a File…Help menu row, one toolbar row with the formula composer to
  its right, a canvas-style grid, a bottom bar with sheet tabs. Static — never
  wire a spreadsheet engine; the grid is the mock-only `table.o-grid-mock`.
  Enterprise-only: never in a Community mock.
- **Spreadsheet Dashboard** — `components/dashboard_sidebar.html`
  (`spreadsheet_dashboard`). Left search-panel nav (uppercase sections, teal
  active item) + white shadowed figures with teal-dark titles; no tab switcher.
- **Gantt** (enterprise `web_gantt`) — `components/gantt.html`. Controls row +
  date header + pastel pills (`o_gantt_color_N`, dark text); pill geometry is
  inline % only. Framed only when it has a side panel.
- **Activity** — `components/activity_matrix.html` (`mail`). Records ×
  activity-types matrix: tinted summary cells (planned / today / overdue at 50%,
  dark text), progress-bar type headers. The global Activity Overview list is
  `activity_list.html`.
- **Cohort** (enterprise `web_cohort`) — `components/cohort.html`. Retention
  grid heat-mapped in TEAL (never brand-tinted); unreached periods are blank.
- **Map** (enterprise `web_map`) — `components/map.html`. Static placeholder map
  (**no tiles** — never load Leaflet), teal un-numbered pins, pin list on the
  RIGHT; "Maps" is a `btn-secondary` in the control panel.
- **Grid / timesheet** (enterprise `web_grid`) — `components/grid.html`. A
  borderless div grid with white gutters between day columns, "Nh Mm"
  durations, row/column totals.
- **Hierarchy / org chart** (`web_hierarchy`) — `components/hierarchy.html`.
  Colour-band cards with an overlapping avatar and a "N people" button, joined
  by a brace connector.
- **Settings** (`res.config.settings`) — `components/settings.html`. App rail +
  white card; `<h2>` section bands; `o_setting_box` checkbox rows, two per line.
- **Printed report (PDF)** — `components/report.html`. A4 paper document
  (header / lines / totals / footer); its OWN surface, no navbar.
- **Customer portal** — `components/portal.html` (`portal`). Logged-in customer
  frontend doc + action sidebar (Accept / Pay). Light frontend chrome. For the
  portal **home / "My Account" landing** (the card grid of document categories),
  use `components/portal_my.html` instead of the single-document `portal.html`.
- **Studio editor** — `components/studio.html` (enterprise `web_studio`). Dark
  Studio navbar + editor menu bar (breadcrumb, Undo/Redo/Saved, Studio tabs,
  view-type icons); a 300px dark sidebar on the LEFT (Add / View / Properties;
  white Components + New Fields tiles); the edited form on the gray page with
  no control panel — smart-button row, statusbar and sheet each with their
  "Add …" hooks, chatter below the sheet. Drop hooks show only on a dragging
  screen.
- **Discuss** — `components/discuss.html` (`mail`). Gray page; a vertical tab
  rail (Chats / Channels / Meetings) + white conversation-list card on the left;
  header card + white boxed actions, bubble thread and pill composer on the right
  (channels add the Members panel). No Inbox/Starred/History sidebar, no
  CHANNELS / DIRECT MESSAGES categories.
- **Empty / first-run state** — `components/no_content.html` (`web.ActionHelper`):
  an overlay helper centred over the view body — the list keeps its header on a
  white body, grouped kanban keeps its columns with faded 0 counters, pivot /
  graph / ungrouped kanban show only the helper. Sample-data variant
  (`.o_view_sample_data`) for `sample="1"` views. A list whose action has no help
  shows NO helper (4 blank rows). Never mock a strip of setup-step cards above a
  view: Odoo has no onboarding banner. The only setup checklist is
  `components/onboarding.html`, the in-card Accounting checklist inside a
  dashboard kanban card.

Only legacy/niche surfaces remain on-demand (board "My Dashboard"); build from
tokens and note in `REFRESH.md` if needed.

## Choosing the click-path

A mock is a sequence of screens wired with `data-mock-goto` / `data-mock-next`.
One screen per **meaningful workflow step** — the points where the user makes a
decision or the record changes state. Don't mock every keystroke; mock the
states. Each `.mock-screen` carries a `data-title` (the step name) and
`data-desc` (one line on what happens here), shown in the walkthrough bar.

**A button must only `goto` the state it actually causes — don't collapse two
workflow steps into one transition.** This is the most common click-path bug. If
the brief has distinct steps (e.g. *allocate lots* → *confirm order*), a wizard's
**Save** returns to the record (now in its updated, still-not-advanced state) — it
does NOT jump to the downstream confirmed/validated screen. That downstream state
is reached by its own action (the record's **Confirm**), so it needs its own
screen. Wiring "Save" straight to "Confirmed" reads as "saving the lots confirmed
the order," which is wrong. When two steps each change state, mock the
in-between state too, even if it costs an extra screen.
