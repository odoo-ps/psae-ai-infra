# Catalog chrome — author discipline

This page collects the *per-fragment* discipline that previously lived
in `SKILL.md`. It covers the chrome surfaces (navbar, control panel,
home menu, settings tabs) and their compose-from-catalog rules. SKILL.md
points here so the orchestration entry-point stays focused on
*workflow*, not *component-by-component* rules.

When extending the catalog with a NEW chrome surface, document it
here — not in `SKILL.md`.

**One calibrated version.** The catalog tracks ONE Odoo version — the
one named in the `calibrated to Odoo NN` stamp on the first line of
`catalog/odoo.css` (sources: `style_guide.md` § Source map). Every rule
below describes that version. All px values are real Odoo px against a
16px `html` root and a 14px body — never rescale `html`. Desktop layouts
only: the mobile Material-3 form styles (`form_controller_m3.scss`,
below 768px) are not modelled, so desktop mocks must not imitate them.

---

## Navbar (`components/navbar.html` + `.o_main_navbar` in `odoo.css`)

Source: `odoo/addons/web/static/src/webclient/navbar/navbar.{xml,scss,variables.scss}`
+ `enterprise/web_enterprise/static/src/webclient/navbar/navbar.{xml,scss,variables.scss}`

**Theme.** The Enterprise navbar is **transparent over the gray-100
(`#f8f9fa`) page** — no white bar, no bottom border, dark text. It is 46px
tall and every entry is a 26px pill with a 6px radius (hover `#e7ebed`).
The brand plum (`#714B67`) is an accent, never the navbar background.
Variants share the same markup:

- `body.o-community` — purple `#71639e` bar, white entries, green badges;
  the grid glyph always shows and the app icon is hidden.
- `studio.html` — dark `#262c34` Studio bar (`.o_studio_navbar`), no systray.

**Structure**, left to right, inside `<header class="o_navbar"><nav class="o_main_navbar">`:

| Cell | Markup | Purpose |
|------|--------|---------|
| Apps toggle + brand | `a.o_menu_toggle.hasImage` = 3×3 grid svg + `svg.o_menu_brand_icon` (`<use href="#o-app-<app>"/>`, 26px, real colours) + `span.o_menu_brand` | Current app icon + name; the grid shows on hover only. Drop the icon AND `hasImage` only on screens with no app context. |
| Menu sections | `.o_menu_sections` > `a.o_nav_entry` | The app's REAL top-level menus as plain 14px text — **no carets** |
| Systray (right) | `.o_menu_systray` > `button.o_systray_item` | See below |

**Menu sections.** Always render the app's real top-level menus (CRM shows
Sales / Reporting / Configuration inline). To draw one open, add `show` to
its entry (teal outline on `#e6f2f3`) and put an
`.o-dropdown--menu.dropdown-menu` (with `left` set inline) as a direct
child of the nav — snippet in `navbar.html`.

**Systray order (left to right, registry sequence) — DO NOT REORDER:**

1. *[Timesheets only]* **Timer** — `#o-play-circle` in `text-danger`
   (with only Attendances: `#o-circle` in `text-success` / `text-danger`).
2. *[ai module only]* **Ask AI** — `#o-app-ai` at 18px (`.o_icon_ai`).
3. **Messages** — `#o-forum` + `<span class="badge">N</span>`.
4. **Activities** — `#o-clock` + `<span class="badge">N</span>`.
5. **Toggle Studio** — `#o-studio` (crossed tools — not a "close" X).
6. **Company** — `button.o_switch_company_menu > span.oe_topbar_name`
   (plain text, regular weight, no caret).
7. **User** — `button.o_user_menu > span.o_user_avatar`: a 26px rounded
   square with ONE initial (optional `o_avatar_c0..c7`); the green online
   dot is CSS.

Badges are red pills after the glyph; omit the `<span>` when the count is
0. There is no liveness dot and no close-all X. Readers recognize this
sequence from real Odoo; swapping it reads as wrong even when each item is
individually correct.

**Retired** (no CSS — lint reports CLASS-UNKNOWN): `o_status_systray`,
`o_status_dot`, `o_chat_systray`, `o_systray_badge`, `o_company_switcher`,
`o_app_icon_image`, and the `#o-caret-down` caret after nav entries.

---

## Home menu / apps switcher (`components/apps_menu.html` + sprites)

Source: `enterprise/web_enterprise/static/src/webclient/home_menu/home_menu.{xml,scss,variables.scss}`
+ `home_menu_background.scss`

**Compose** as `<div class="o_web_client o_home_menu_background">` +
`navbar.html` + `apps_menu.html`. On the home menu only the systray
shows — `.o_home_menu_background` hides the toggle, brand and sections.
The background is the light dotted pattern (gray-100, 12px dot grid, soft
central shade), not a wallpaper. Never draw the trial "This database will
expire" banner. (Opened from inside an app, real Odoo turns the toggle
into a back arrow; the catalog models the landing state only.)

**Tiles.** Each tile is the app's REAL multi-colour artwork (each module's
`static/description/icon.svg`): 50px inside a 70px white card (10px
padding, 8px radius), caption 14px / 500, hover changes only the shadow.
**Never tint** — no `style="color:…"` on `.o_app`.

```html
<a class="o_app" role="option" data-mock-goto="crm-kanban">
  <div class="o_app_icon"><svg class="o_app_icon_glyph"><use href="#o-app-crm"/></svg></div>
  <div class="o_caption">CRM</div>
</a>
```

**Order** = the database's menu sequence (`apps_menu.html` lists them in
order: Discuss, Calendar, To-do, Contacts, CRM, Sales, Dashboards, …,
Apps, Settings last). Keep only the apps the solution's database has.
Without the Accountant app the Accounting slot is **Invoicing**
(`#o-app-invoicing`). Studio and Field Service have no home tile.

**Available app ids** (`catalog/app-icons.svg`): `o-app-` + `discuss`,
`calendar`, `todo`, `contacts`, `crm`, `sales`, `dashboards`,
`accounting`, `invoicing`, `project`, `timesheets`, `hr` (Employees),
`timeoff`, `payroll`, `inventory`, `purchase`, `documents`, `pos`,
`website`, `ai`, `fleet`, `sign`, `helpdesk`, `mrp`, `marketing`,
`mass-mailing`, `planning`, `subscriptions`, `rental`, `maintenance`,
`recruitment`, `survey`, `elearning`, `quality`, `spreadsheet`, `apps`,
`settings` (+ `studio`, `fsm` — not home tiles). To add an app, copy its
`icon.svg` into a `<symbol id="o-app-<name>" viewBox="0 0 50 50">`.

**Sprite contract.** The catalog ships TWO inline sprites:

- `catalog/icons.svg` — UI glyphs: the calibrated version's real icon
  outlines (Material Symbols Outlined + Odoo `oi_*` icons), same ids
  across refreshes. Id map: `style_guide.md`.
- `catalog/app-icons.svg` — app artwork (`#o-app-crm`, `#o-app-sales`, …).

Inline-paste **both** into a package's `index.html` (the scaffolder does
this) — external `<use>` breaks on `file://`. Paste them verbatim; never
restyle `icons.svg`'s zero-size root (`width="0" height="0"
style="position:absolute;…"`) to `display:none` — its empty-state
illustrations' gradients and masks would stop painting.

---

## Control panel (`components/control_panel.html`)

Source: `odoo/addons/web/static/src/search/control_panel/control_panel.{xml,scss}`
+ `enterprise/web_enterprise/static/src/search/control_panel/`

**Look.** The Enterprise control panel has **no bar of its own** — same
gray as the page, no bottom border, padding 8px 16px 16px
(`body.o-community`: white bar with a 1px rule). It is ONE desktop row:

```
[main buttons][title ⋮]  |  page-centred search  |  [pager][switcher]
 .o_control_panel_breadcrumbs  .o_control_panel_actions  .o_control_panel_navigation
```

The side cells are equal `flex:1`, so the search (min(600px, 33%)) sits
exactly centred. An empty main-buttons / actions cell must be LITERALLY
empty (CSS `:empty`). The fragment ships two shells (LIST / KANBAN /
REPORTING, then FORM) plus commented optional states.

**Main buttons — by view type:**

| View | `.o_control_panel_main_buttons` |
|---|---|
| list / kanban | filled `btn btn-primary` New |
| form | outlined `btn btn-outline-primary o_form_button_create` New |
| reporting (pivot / graph) | empty — the toolbar sits in the content below |
| settings | Save (`btn-primary o_form_button_save`) + Discard (`btn-secondary o_form_button_cancel`) |
| read-only model | empty |

Extra layout buttons (e.g. CRM "Generate ▾") follow New as
`btn-secondary`. Add the `New ▾` caret (`<svg class="o_icon o_caret"><use
href="#o-caret-down"/></svg>` inside the button) only where the real app
has it. List header buttons without `display="always"` appear only while
records are selected; only `display="always"` ones sit next to New.
Workflow buttons (Confirm, Validate, Post…) never go here on a form —
they live in the form statusbar.

**Title.** A single-level title (list / kanban / reporting / settings) is
16.8px REGULAR, never bold. A form or drill-down shows TWO stacked lines:
a 13px teal link to the IMMEDIATE parent only, then the 14px record name.
Older ancestors collapse into a ⋯ button (`#o-ellipsis-h`) before the
parent. Never an inline "Parent / Record" path.

**⋮ action menu.** `.o_cp_action_menus` holds a ⋮ (`#o-ellipsis-v`) in a
`btn o_btn_circle btn-light`, placed right after the title or record name
INSIDE `.o_breadcrumb` (in `.o_control_panel_breadcrumbs_actions`). It is
never a cog, there is no favorite star, and it is not rendered while list
records are selected (nor inside dialogs). Open state: add `show` to the
button; the menu is an `.o-dropdown--menu.dropdown-menu` in a
`.mock-anchor` — Print (▸ when several reports), Edit Properties,
Duplicate, Archive, Delete (`.text-danger`) with icons, then a divider
and the model's server actions without icons.

**Search bar** (list / kanban / reporting). A white pill input-group
(`.o_cp_searchview.input-group.rounded-pill`), 1px `#ced4da` border, no
visible caret (the end-cap toggler is empty). The catalog draws the
blurred gray border; it turns teal on focus or while the menu is open
(real screenshots show teal because Odoo autofocuses the search).
**Facets** are light-gray chips with a tinted icon square — filter
`#o-filter` (plum), group-by `.o_facet_groupby` + `#o-stacks` (teal),
favorite `.o_facet_favorite` + `#o-star`, field search = the bold field
name instead of an icon — with 13px values and a `#o-close-small` remove
(`.o_facet_remove`). Never solid purple pills. **The search menu** is one
popover under the search with three columns (Filters / Group By /
Favorites, coloured filled title icons); a `selected` item gets weight 500
and a CSS teal check; it ends with Custom Filter... / Custom Group / Save
search.

**Pager** — "1-80 / 132" (form: "27 / 81") + a JOINED 2-button group
(`#o-chevron-left` / `#o-chevron-right`). On a single page both buttons
carry `disabled`. Omitted on reporting views and grouped kanban; a
grouped list pager counts groups.

**View switcher** (`nav.o_cp_switch_buttons.btn-group.o_switcher`) — a
white segmented control of icon buttons (`#o-view-<type>`). Buttons follow
the ACTION's view order; **exactly one** carries `.active` (a gray tile,
never teal). Drop the views the action doesn't expose; omit the whole nav
on forms and when the action has a single view.

**Smart buttons** render ONLY on forms, in the CENTRED cell
(`.o_control_panel_actions > .o-form-buttonbox`), never in the form sheet
(`form_view.html` deliberately has no button box). They form one joined
group of white bordered buttons: a 21px plum outline icon (the button's
own glyph — ids in `control_panel.html`), then a label stacked over a
plum value. No smart buttons → leave the cell literally empty.

**Optional states** (commented snippets in the fragment): with list /
kanban records selected, the search bar is REPLACED by `[N selected ×]`,
the header buttons and `Print` / `⚙ Actions` `btn-secondary` dropdowns
(the ⋮ disappears; pager and switcher stay). An unsaved form adds save /
discard icon buttons after the ⋮ — omit them on a clean record. Embedded
actions and date facets have snippets too.

Pivot / graph toolbars (Measures etc.) sit in the content under the
control panel, on the same gray — never in the control panel.

---

## Settings page (`components/settings.html`)

Source: `web/static/src/webclient/settings_form_view/` (+ `settings/`),
`web/static/src/views/form/setting/`, and the `web_enterprise`
`settings_form_view.scss` override.

**DOM.** `.o_form_view.o_base_settings_view.o_field_highlight` holds the
control panel, then `.o_setting_container` = `.settings_tab` (the app
RAIL) + `.settings` (the white card, 12px rounded top corners) >
`.app_settings_block`. Copy the fragment; never re-derive it.

**Control panel** — the standard ONE-ROW shell: Save + Discard in
`.o_control_panel_main_buttons`, the "Settings" title (followed by an
EMPTY `.o_control_panel_breadcrumbs_actions` — no ⋮), and a PLAIN
6px-radius search box (`.o_cp_searchview > .o_searchview.form-control`,
no pill, no menu) centred in `.o_control_panel_actions`.
`.o_control_panel_navigation` stays empty. The search never goes inside
`.o_setting_container`. Show `<span class="text-muted o_dirty_warning">Unsaved
changes</span>` after the breadcrumb only on a screen that represents an
edited, not-yet-saved form.

**Rail.** One `a.tab` per installed app (`a.tab.selected` = current app),
each with its full-colour app icon (`svg.icon` + `#o-app-*`, 23px, never
tinted) and a 13px name. General Settings comes first and uses
`#o-app-settings`. The selected tab is a teal 10% tint with a 2px teal
left bar — never brand plum.

**Card.** No app title. Each section is an `<h2>` gray band spanning the
card; a block with no title is just another `.o_settings_container`.
Settings sit TWO per row (`o_setting_box col-12 col-lg-6`), never split
into a label column and a control column:

- `.o_setting_left_pane` — the checkbox of a boolean setting (teal when
  checked; never a toggle switch), else empty.
- `.o_setting_right_pane` — `.o_form_label`, optional `a.o_doc_link`
  (`#o-question-circle`) or company icon (`#o-business`), the `.text-muted`
  help, then `<div class="mt16">` with the control. Keep the `.mt16` div
  even when empty.

Selections are a vertical radio list (`o_field_radio`) or an underlined
select; numbers sit inline ("Warn me [7] days…"); action links are
`button.btn.btn-link` with `#o-east` in a `div.mt8` — never a text "→".
Solution-added settings keep the mock-only `.o_field_help` "?" after the
label.

---

## Activity views (`components/activity_matrix.html` + `activity_list.html`)

There are **two** activity surfaces, with different markup:

| Variant | When | Source |
|---------|------|--------|
| `activity_matrix.html` | Per-model Activity view (view switcher) — records × activity-types matrix | `mail/static/src/views/web/activity/` |
| `activity_list.html` | Global "Activity Overview" action (`mail.mail_activity_action`) — a plain list of every pending activity | `mail/views/mail_activity_views.xml` |

**Matrix.** Summary cells are tinted 50% green / amber / red (planned /
today / overdue) with DARK text, a date and an assignee avatar; empty
cells stay white. Type headers carry a progress bar and "n/N". There is
no legend row and no count bubble.

**List.** Summary · Document (plain text) · Assigned to · Role · Due Date,
then a dark Reschedule `btn-link` and a teal Done `btn-link`. No Cancel
button, no Activity Type column. It is a standalone action: the navbar
shows no app brand or menus, and there is no view switcher.

---

## Kanban (`components/kanban.html`)

Source: `web/static/src/views/kanban/` + `web/static/src/views/card/card.scss`
+ `web_enterprise/static/src/views/{card/card.scss,kanban/kanban_controller.scss,kanban/kanban_header.xml}`.
The record look lives in the `card` and `web_enterprise` overrides — diff
those and confirm with a live probe, not just `kanban_record.scss`.

**Record** = `<article class="o_card_record o_kanban_record">`, never a
div (only the trailing `.o_kanban_ghost` placeholders are divs). Top to
bottom:

1. **Title** — `<span class="fw-bold fs-5">` (project tiles: `fs-4`).
2. **Lines** — plain 13px divs (partner = small avatar + name); meta lines
   muted with a leading 13px icon.
3. **Tags** — `.o_tag.o_tag_color_N` bordered pills.
4. **`<footer>`** — LEFT: priority stars (`#o-star` set / `#o-star-o`
   unset) + the activity button; RIGHT (`.ms-auto`): badges, 24px
   rounded-square avatar, optional state circle.
5. **⋮ menu** — `.o_dropdown_kanban` (`#o-ellipsis-v`), last child,
   visible on hover only.

Never draw a top bar. The **activity** indicator is the next activity's
TYPE glyph, filled, coloured by state (`text-success` planned /
`text-warning` today / `text-danger` overdue), or an outline `#o-clock`
when none is planned — never a dot. A colour tag
(`o_kanban_record_colored o_kanban_color_N`) is a 3px band on the LEFT
edge. **Lost / Won** reuses the form's ribbon widget as the article's
first child: `<div class="o_widget o_widget_web_ribbon"><div class="ribbon
ribbon-top-right"><span class="text-bg-danger">Lost</span></div></div>`.

**Grouped (stages).** Transparent columns, no gray box. Cards in a column
are STACKED (shared 1px borders, no gaps, no shadows; only the stack's
outer corners rounded). The header has two rows: `.o_column_title` +
hover-only cog (`#o-cog`) + circle quick-add (`#o-add-2`); then, only when
the view has a progressbar, `.o_kanban_counter` = progress bar +
right-aligned aggregate. No counter pill — without a progressbar write
"(N)" after the title. Add `.o_kanban_small_column` where the real view
has it (CRM pipeline, Project tasks). Done/Cancelled-type stages can
render as folded strips.

**Other layouts** (one per `.o_kanban_view`): ungrouped tiles (16px gap,
cards grow from 320px, end with 2-3 ghosts — the layout for any "summary
cards" need); image cards (`article.flex-row > aside.o_card_aside_full`);
row-style lists (`.o_kanban_view.o_kanban_list` — Time Off, Surveys,
mailing lists; never draw those as tile grids).

**Retired** (no CSS): `o_kanban_record_topbar` / `_menu` / `_subtitle` /
`_bottom` / `_right`, `o_kanban_age_badge`, `o_kanban_progressbar`,
`o_kanban_header_amount`, `o_kanban_ribbon*`, `.o_activity_dot` on cards,
`o_card_grid` / `o_card_line` / `o_card_key`.

---

## Pay run, opened (hr_payroll — no pay-run form in v20)

Source: `enterprise/hr_payroll/static/src/search/payrun_control_panel.xml`,
`components/payrun_card/button_box/payrun_button_box.xml`,
`views/hr_payslip_run_views.xml` (kanban `payrun_menu` template).

Opening a pay run (the kanban card in `payrun-kanban.html`) shows the run's
**payslip list** (`action_open_payslips`), not a form:

- Control panel: `New ▾` (PayrunNewDropdown) in `.o_control_panel_main_buttons`,
  then the run's buttons in a SIBLING box (`div.d-flex.gap-1.pe-1`), then the
  two-line breadcrumb `Pay Runs / <run>` + ⋮.
- The button box shows **one** inline action (two when a priority button such
  as Pay / Mark as Paid applies) and folds the rest into a
  `btn-outline-secondary` **More ▾** dropdown (Test Print, Re-compute Payslips,
  Work times, Payroll Journal, Add Employees, Delete …). Validate carries
  `confirm="Are you sure you want to proceed?"`.
- Navigation: pager, `[List | Activity]` switcher, then the Chatter toggle.
- List columns (`view_hr_payslip_tree`): Employee, Worked Days, Total Cost,
  Basic Wage, Net Wage (bold), Status badge, Warnings; Period and Pay Run
  are hidden inside a run.

The payslip form's posted entry is a **Journal Entry (Posted)** smart button
(`hr_payroll_account`, attach_money), and with `hr_payroll_account` the
payslip Validate also asks "Are you sure you want to proceed?". A refund is
**Correct** (paid payslips) → Payslip Correction wizard (`modal-md`:
Correct / Revert only / Discard); there is no Refund button.

---

## Pivot expand affordances (`components/chart_views.html`)

Row and column headers that can drill down are
`th.o_pivot_header_cell_closed` with `#o-add-box`; expanded ones are
`th.o_pivot_header_cell_opened` with `#o-minus-box`. Indent rows with
inline `padding-left` (5px + 30px per level); totals get `fw-bold`. Never
write literal `[+]` / `[−]` text or bordered squares. The pivot toolbar
(Measures `btn-primary`, Spreadsheet `btn-secondary`, then flip-axis /
expand-all / download) is a free-standing row between the control panel
and the table.

---

## Layout variants vs base fragments

Some surfaces have multiple legitimate layouts depending on context.
The catalog ships both:

| Surface | Base | Variant |
|---------|------|---------|
| Login | `login.html` (card-only, backend installs) | `login_website.html` (embedded in website chrome) |
| Calendar | `calendar_week.html` (header + frame + side panel, week grid) | month scale: swap in the `chart_views.html` month grid (`.o_calendar_grid`) |
| Dashboard | `dashboard_sidebar.html` (search-panel nav) | — none: there is no section switcher |
| Activity | `activity_matrix.html` (per-model, record × type) | `activity_list.html` (global activity action) |

Choose the variant that matches the action the mock is showing — same
catalog, different render based on which Odoo route the user is on.

---

## Multi-workflow chrome (`components/walkthrough_bar.html` + `annotations.css`)

A multi-workflow package (≥ 2 `.mock-workflow` wrappers, not counting the
`overview` pseudo-wrapper around the cover) is **NOT** the single-workflow
pattern with an extra dropdown. It has its own cover topology, walkthrough-bar
order, and Next-button relabel rules. Single-workflow packages stay as today.

### Reading flow (multi-workflow)

```
Main cover (table of contents — universal, always reachable)
  ↓ Next = "Start: <first-workflow-title>"
Per-workflow overview (chapter intro — actors, narrative, step list)
  ↓ Next = "Get Started"
Workflow content screens (the real chrome)
  ↓ on last screen of non-final WF, Next = "<next-workflow-title>"
Per-workflow overview (next workflow)
  ↓ … repeat …
Last workflow's last screen → Next hides (terminal)
```

The reader experiences the package as one continuous narrative even though
it's structurally N workflows. Previous works symmetrically and can cross
workflow boundaries (the first screen of WF2 goes back to the last screen of
WF1).

### Walkthrough-bar layout

```
[Workflow: Purchase ▾]   [< Previous]   [Next >]   [Step title + desc]   [● ● ●]   [counter]   [chips]   [Annotations | Custom]
 └ scope chip (left)     └ navigation              └ per-step context     └ dot row             └ variant filters └ overlay toggles
```

DOM order in `walkthrough_bar.html` is meaningful and reads left → right as
the user's mental hierarchy: `[Workflow scope] [Prev/Next] [Step context] [dots] [counter] [chips] [Annotations | Custom]`.
Don't reorder. The workflow scope chip sits **leftmost** — workflow is the
outer mental scope, stepping is inner. Single-workflow packages keep the chip
hidden (no DOM change required; `walkthrough.js` shows it only when ≥ 2
`.mock-workflow` wrappers exist).

### Per-workflow overview screen

The first `.mock-screen` inside each `.mock-workflow` wrapper (excluding the
`overview` pseudo-wrapper) must be a workflow overview screen:

```html
<section class="mock-screen" data-screen="<slug>-overview"
         data-screen-kind="workflow-overview"
         data-title="<Workflow name> workflow"
         data-desc="<one-line summary of the workflow's arc>">
  ...
</section>
```

`data-screen-kind="workflow-overview"` is the JS anchor (Get Started relabel +
no-content-marker rule). The `-overview` suffix on `data-screen` is the lint
anchor (mock-coverage-anchor's structural check). The two evolve independently.

Content shape:
- **Mock-cover kicker** with "Workflow N of M · &lt;Name&gt;" so the reader
  knows where they are in the package.
- **Title + 2-3 sentence narrative** explaining why this workflow exists.
- **Actors section** — one `.mock-cover-callout` per actor with the role's
  name in bold + one sentence of what they do. Avoid generic personas; use
  the actors the workflow's screens actually engage.
- **Step list** — same `.mock-step-list-wrap` markup as the main cover. The
  `data-mock-page-ref` chips resolve workflow-scoped (the page numbers match
  the walkthrough counter the reader sees on that screen).
- **No How-To callouts** — those stay on the main cover, universal.
- **No numbered `mock-marker` annotations** — workflow overviews are framing
  screens, not content screens; markers belong on the screens that
  demonstrate the workflow's solution elements. Inline illustrative markers
  (`mock-marker-example`) are still allowed.

**Voice**: every piece of reader-facing prose on a per-workflow overview —
title, subtitle, narrative paragraph, actor descriptions, step descriptions
— follows the business-voice rules in
[`style_guide.md`](style_guide.md) § Cover, overview, and meta-content voice.

### Main cover (multi-workflow)

The main cover stays as the package's table of contents and lives inside its
own `<div class="mock-workflow" data-workflow="overview" data-workflow-title="Overview">`
pseudo-wrapper. This makes "Overview" the first entry in the walkthrough's
workflow dropdown, so the reader can always return mid-walkthrough.

Multi-workflow specific changes vs single-workflow cover:

1. **Add the "Multiple workflows" how-to callout** — automatic when ≥ 2
   `.mock-workflow` wrappers exist, per the inclusion rule in
   [`templates/cover_callouts.html`](templates/cover_callouts.html).
2. **Replace the workflow-index page-ref chips with CTA chips.** Each row's
   chip becomes
   `<a class="mock-step-axes mock-step-axes-cta" data-mock-goto="<slug>-overview">`
   — clicking jumps to that workflow's overview. The old
   `data-mock-page-ref` mechanic doesn't work in multi-workflow mode because
   page numbers are workflow-scoped (a global "Page N" is meaningless).
3. **Trim the per-row description.** The longer narrative now lives in the
   per-workflow overview; the cover row stays at one sentence summarising
   the workflow's arc.

### walkthrough.js mechanics (reference)

> **Single source of truth:** [`catalog/walkthrough.js`](catalog/walkthrough.js)
> `nextButtonLabel()`. This table mirrors that function; if it ever differs,
> the JS wins — fix the table.

| Trigger | Behavior |
|---|---|
| ≥ 2 `.mock-workflow` wrappers | Show the workflow selector chip (leftmost in bar) |
| `data-screen="cover"`, single-workflow mode | Next button label → `Get Started` |
| `data-screen="cover"`, multi-workflow mode | Next button label → `Start: <first-workflow-title>` |
| `data-screen-kind="workflow-overview"` | Next button label → `Get Started` |
| Last `.mock-screen` of its workflow, AND the workflow is NOT the last DOM-order workflow | Next button label → bare `<next-workflow-title>` (the chevron icon conveys forward direction) |
| All other screens | Next button label → `Next` |
| First screen of the first workflow (the main cover) | Previous button hidden |
| Last screen of the last workflow | Next button hidden (terminal) |
| ≥ 1 `.mock-custom` in the package | Custom chip beside Annotations (the bottom row splits in two) |
| Active `.mock-screen` carries `mock-custom` | Corner Custom banner (`mock-screen-custom` on `<body>`) |
| Workflow selector chip changed | Jump to selected workflow's first screen (its overview) |
| `data-mock-page-ref` chip | Resolves "Page N" within the chip's containing `.mock-workflow` (scope-local), falling back to global non-cover screens if outside any wrapper |

### Discipline

- Main cover row description and per-workflow overview narrative **don't
  overlap content**. Cover = one sentence per workflow; overview = the
  paragraph. Drift is visible because the audiences are explicitly separated.
- **Workflow order = DOM order** of `.mock-workflow` wrappers (the "overview"
  pseudo-wrapper is always first by convention). No alphabetization, no
  override.
- **Marker budget** unchanged — 4–7 across the package. The main cover and
  per-workflow overviews are exempt from the count.

### Scope chip styling

The scope chip's styling lives at `.mock-wt-workflow` in `annotations.css` —
pale-plum background, brand-plum dropdown text, right-divider separating it
from the Prev/Next controls. Don't put a chip-style on other walkthrough
elements without thinking about hierarchy: the chip says "outer scope," and
proliferating chips reads as "everything is scope."

---

## When something is missing from the catalog

Per `SKILL.md` § Iteration Etiquette: source-first. Read the matching
Odoo source, port the markup + scss into the catalog, cite the path
in this file (or in `REFRESH.md`), then use it from the mock. Do NOT
invent new chrome from `odoo.css` tokens alone — that's the leading
cause of catalog drift across iterations.

Source alone is not proof either: read the `web_enterprise` overrides,
then compare against a REAL screen of the calibrated version with the
calibration kit (`scripts/calibrate/`: `capture.js` screenshots the live
screens listed in `screens.json`, `probe.js` dumps computed styles from a
live screen or a catalog page, `render.js` renders a catalog page; the
per-screen comparison pages live in `calibration/screens/<name>.html`).
A class name that still exists in the new version says nothing about how
it looks.
