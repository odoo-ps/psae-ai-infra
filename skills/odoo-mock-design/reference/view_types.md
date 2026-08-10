# Odoo view types — anatomy & when to mock each

Runtime-read catalog. When mapping a workflow step to a screen, pick the view
type that matches what the user actually does at that step, then compose the
screen from `catalog/` fragments. **Read this and `style_guide.md` — do not
re-derive styling from Odoo source at generation time.** The catalog already
encodes it.

## Density — match the workflow, not a quota

A mock screen reads as "real Odoo" when its density matches what the
*workflow actually requires*. Padding to hit a row count or field count
turns the mock into bulk; under-populating turns it into a wireframe.
Aim for **the smallest faithful representation of what the user sees at
that step.**

| View type | Density anchor (aim for) |
|---|---|
| **form** | Carry the field groups + notebook tabs the **brief actually references** for this step, plus the standard fields that live where Odoo puts them (discovered from source per `field_placement.md`). Don't enumerate every field on the real model; don't strip the form to only the net-new ones. The chatter, statusbar, and smart-button box belong only when the step engages them. |
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

---

## form — a single record

**Use when** the step is "open / edit / act on one record" (a quotation, a
contract, an employee). The workhorse screen for most workflows.

- **Fragment:** `components/form_view.html`
- **Anatomy:** statusbar (left action buttons + right status pipeline) → sheet:
  title → two-column field groups → notebook tabs. **Smart buttons (the stat-button
  box) are NOT in the sheet** in Odoo 19 — they render in the **control panel's
  centered `.o_control_panel_actions` cell** (see `control_panel.html`); the sheet
  starts at the title. (Pre-17 put the box inside the sheet — don't.)
- **Button placement — don't duplicate.** A record's workflow buttons (Confirm,
  Create Invoice, Validate, …) live in the **form statusbar only**. On a form,
  the control panel above carries breadcrumbs (+ pager/switcher) — it does NOT
  repeat the workflow buttons. Putting the same buttons in both
  `o_control_panel_main_buttons` and `o_statusbar_buttons` renders them twice and
  reads as a bug. (List/kanban screens are the opposite: their action buttons DO
  live in the control panel, since those views have no statusbar.)
- **Add a chatter** (`components/chatter.html`) when the step involves
  messaging, logging, activities, or an audit trail — wrap the sheet + chatter
  in `.o_content_with_chatter`.
- **Status pipeline:** mark the active stage with `o_arrow_button_current`. This
  is the single most recognisable Odoo form cue — get it right.
- **Source:** `odoo/addons/web/static/src/views/form/`.

### Custom field widgets (solution-added OWL components)

When the spec adds a **bespoke OWL field widget** — a small display component
registered via `registry.category('fields').add(...)` and bundled in
`web.assets_backend` — it is **not a new screen**. It renders inside the same
`.o_field_widget` cell a standard field would, on whatever form already covers
that record. Treat it as a per-field fidelity detail of the form, not a
coverage-floor surface.

- **Fragment:** `components/custom_field_widget.html` — generic shapes a small
  display widget usually takes: a **status pill** (coloured `.badge`), an
  **icon+value pill** (`.o_cw_pill` + inline `<use>` glyph, e.g. a live FX rate),
  and a **meter/gauge** (`.o_cw_meter`, e.g. utilisation or score). Pick the
  closest shape and relabel.
- **Display only.** The widget shows a value; it never computes in a mock. Drive
  any state change with the screen's State axis, not live logic.
- **Flag it as custom.** Put the `o_field_help` "?" on the field's label (same as
  a custom standard field — see `interactions.md` § Custom-field help), so the
  reader sees it's solution-added.
- **Source:** `odoo/addons/web/static/src/views/fields/` (standard widgets) +
  `standardFieldProps`.

## list (tree) — many records, tabular

**Use when** the step is "find / scan / compare / pick from many records", or as
an editable sub-table inside a form notebook (order lines, invoice lines).

- **Fragment:** `components/list_view.html`
- **Anatomy:** sticky header row → selector column → data rows → optional
  grouped headers (`o_group_header`) → footer totals. Right-align numeric
  columns with `o_list_number`.
- **Keep** the pager + view switcher in the control panel for list screens.
- **Source:** `odoo/addons/web/static/src/views/list/`.

## kanban — cards in columns

**Use when** the step is about pipeline/stage progression, visual triage, or
drag-between-states (CRM pipeline, recruitment, project tasks).

- **Fragment:** `components/kanban.html`
- **Anatomy:** horizontal columns (`o_kanban_group`) each with a header +
  counter, holding cards (`o_kanban_record`). Use the ungrouped variant for a
  plain card grid.
- **Source:** `odoo/addons/web/static/src/views/kanban/`.

## dialog / wizard — a modal step

**Use when** the step is a transient action that pops a modal: a confirmation, a
`TransientModel` wizard (e.g. "Validate delivery", "Register payment").

- **Fragment:** `components/dialog.html` — rendered over the underlying screen so
  the backdrop dims it. Wire the footer button's `data-mock-goto` to the screen
  the wizard produces.

## search panel — left-hand filters

**Use when** a list/kanban step emphasises filtering by category/hierarchy.

- **Fragment:** `components/search_panel.html` — place to the left of the view
  body in a flex row.

---

## Chart / grid views — on-brand placeholders

`components/chart_views.html` ships static, recognizably-Odoo placeholders for
**graph** (bar), **pivot** (cross-tab grid), and **calendar** (month grid). Use
them only when a *reporting* step genuinely needs one — a mock should land its
decision points on form / list / kanban. **Never embed a charting library** —
that breaks self-containment; the placeholders are CSS + tokens only.

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
- **Accounting report** — `components/account_report.html` (enterprise
  `account_reports`). Filter bar (date / comparison / journals / export) +
  hierarchical foldable lines (`o_account_report_line`, indent/total/grandtotal).
  Render inside the backend shell.
- **Spreadsheet** — `components/spreadsheet.html` (`spreadsheet` / o-spreadsheet).
  Toolbar + formula bar + lettered grid + sheet tabs. Static — never wire a
  spreadsheet engine.
- **Spreadsheet Dashboard** — `components/dashboard.html`
  (`spreadsheet_dashboard`). KPI tiles + chart/pivot tiles (reuse the graph/pivot
  placeholders); section switcher on top.
- **Gantt** (enterprise `web_gantt`) — `components/gantt.html`. Row labels + date
  header + colored pills (`o_gantt_pill`); pill geometry is inline % only.
- **Activity** — `components/activity.html` (`mail`). Records × activity-types
  matrix with count cells coloured planned / today / overdue.
- **Cohort** (enterprise `web_cohort`) — `components/cohort.html`. Retention grid;
  cells heat-mapped in the brand color.
- **Map** (enterprise `web_map`) — `components/map.html`. Static placeholder map
  (**no tiles** — never load Leaflet) + numbered pins + pin-list sidebar.
- **Grid / timesheet** (enterprise `web_grid`) — `components/grid.html`. Rows ×
  day columns, hour cells, row/column totals.
- **Hierarchy / org chart** (`web_hierarchy`) — `components/hierarchy.html`.
  Parent node + connector lines to child nodes.
- **Settings** (`res.config.settings`) — `components/settings.html`. App nav +
  `o_setting_box` toggle rows.
- **Printed report (PDF)** — `components/report.html`. A4 paper document
  (header / lines / totals / footer); its OWN surface, no navbar.
- **Customer portal** — `components/portal.html` (`portal`). Logged-in customer
  frontend doc + action sidebar (Accept / Pay). Light frontend chrome.
- **Studio editor** — `components/studio.html` (enterprise `web_studio`). The form
  being edited + field-palette sidebar + dashed drop hooks.
- **Discuss** — `components/discuss.html` (`mail`). Channel/DM sidebar + thread +
  composer.

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
