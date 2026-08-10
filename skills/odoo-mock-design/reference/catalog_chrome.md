# Catalog chrome — author discipline

This page collects the *per-fragment* discipline that previously lived
in `SKILL.md`. It covers the chrome surfaces (navbar, control panel,
home menu, settings tabs) and their compose-from-catalog rules. SKILL.md
points here so the orchestration entry-point stays focused on
*workflow*, not *component-by-component* rules.

When extending the catalog with a NEW chrome surface, document it
here — not in `SKILL.md`.

---

## Navbar (`components/navbar.html` + `.o_main_navbar` in `odoo.css`)

Source: `odoo/addons/web/static/src/webclient/navbar/navbar.{xml,scss,variables.scss}`
+ `enterprise/web_enterprise/static/src/webclient/navbar/navbar.{xml,scss,variables.scss}`

**Theme.** Enterprise navbar is **white background + dark text**,
46px tall, no border-bottom. The brand purple (`#714B67`) is an
**accent** (buttons / active state) — NOT the navbar background. The
older dark-purple navbar is the **community** variant; the catalog
ships it as `body.o-community` override only.

**Structure**, left to right:

| Cell | Class | Purpose |
|------|-------|---------|
| Apps launcher | `.o_menu_toggle` with inline 3×3 SVG | Tap → home menu |
| Brand icon (opt.) | `<img class="o_menu_brand_icon">` | Shown when an app is active |
| App name | `.o_menu_brand` | "Sales", "CRM", … |
| Menu sections | `.o_menu_sections` with `.o_nav_entry` + caret | Inline top-menu dropdowns |
| Systray (right) | `.o_menu_systray, margin-left:auto` | See below |

**Systray order (left to right) — DO NOT REORDER:**

1. **Liveness dot** — `.o_status_systray .o_status_dot` (red = connected).
2. **Chat with badge** — `.o_chat_systray` + `<span class="o_systray_badge">N</span>`
   (omit `<span>` when the count is 0).
3. **Activities clock** — `.o_systray_item` with `#o-clock` glyph.
4. **Close-all menus** — `.o_systray_item` with `#o-times` glyph.
5. **Company switcher** — `.o_company_switcher` (company name + caret).
6. **User avatar** — `.o_user_avatar` with initials.

Readers recognize this sequence from real Odoo; swapping it (e.g. avatar
before company name) reads as wrong even when each item is individually
correct.

**When to use which menu-sections variant:**

- App pages that surface their top-nav inline (Calendar, Sales, Settings,
  Project) → include all `.o_nav_entry` items with carets.
- App pages whose sub-nav lives in the breadcrumb area instead (Odoo 19
  CRM does this) → leave `.o_menu_sections` empty.

---

## Home menu / apps switcher (`components/apps_menu.html` + sprite)

Source: `enterprise/web_enterprise/static/src/webclient/home_menu/home_menu.{xml,scss,variables.scss}`
+ `home_menu_background.scss`

**Theme.** Light gray page (`$o-gray-200`), 850px max container, tiles are
**70px square white cards** with a soft inset shadow. The brand color
carries on the **icon glyph** (`currentColor` from `style="color:#xxx"`
on the `.o_app`), NOT on the tile background. The older brand-color-tile
look is wrong for Odoo 19.

**Sprite contract.** The catalog ships TWO inline sprites:

- `catalog/icons.svg` — UI icons (chevrons, plus, cog, view-switcher …)
- `catalog/app-icons.svg` — app brand icons (`#o-app-crm`, `#o-app-sales`, …)

Inline-paste **both** into a package's `index.html` — external `<use>`
breaks on `file://`. The sprites are forked so app icons can grow
without bloating the UI icon set.

**Authoring template (one tile):**

```html
<a class="o_app" role="option" style="color:#1aa1cd;" data-mock-goto="crm-kanban">
  <div class="o_app_icon"><svg class="o_app_icon_glyph"><use href="#o-app-crm"/></svg></div>
  <div class="o_caption">CRM</div>
</a>
```

The `style="color:#xxx"` is the app's brand color. The SVG uses
`currentColor` so a single sprite serves every app. For pixel-perfect
fidelity, swap the `<svg>` for `<img class="o_app_icon o_app_icon_image"
src="...">` pointing at the real per-app PNG from
`odoo/addons/<app>/static/description/icon.png`.

**Brand colors used in the catalog suite tour (close to real Odoo):**

| App | Color | App | Color |
|-----|-------|-----|-------|
| CRM | `#1aa1cd` | Sales | `#7c7bad` |
| Accounting | `#f06050` | Inventory | `#f4a460` |
| Purchase | `#5c8ed7` | Project | `#27a978` |
| Employees | `#1d8348` | Discuss | `#e9b425` |
| Website | `#714B67` | Point of Sale | `#017e84` |
| Settings | `#875a7b` | Studio | `#4a4a55` |
| Calendar | `#9d3c69` | Contacts | `#1e74c5` |
| Documents | `#3c8dbc` | Dashboards | `#df7c2f` |
| Timesheets | `#287f59` | Fleet | `#666` |

Real Odoo loads each app's color from its `web_icon` manifest entry;
these match well enough that the apps menu reads as native.

---

## Control panel (`components/control_panel.html`)

Source: `odoo/addons/web/static/src/search/control_panel/control_panel.scss`
+ `enterprise/web_enterprise/static/src/webclient/control_panel/`

**Smart buttons (button-box) sit in the control panel's CENTERED cell**
(`.o_control_panel_actions`), NOT in the form sheet. The catalog's
`form_view.html` deliberately omits a button-box for that reason —
put smart buttons in `control_panel.html` instead.

**The cog (`.o_cp_action_menus`) sits BETWEEN the breadcrumb and the
button-box on the same row.** With this order, the cog stays anchored
to the record identity on the left and the centered button-box flows
naturally in the remaining row width. Don't put the cog after the
button-box — it then floats to the far right and reads as wrong.

**View switcher (`.o_cp_switch_buttons`).** Odoo 19 enterprise apps
expose 5-7 view modes per record set. The catalog ships all seven
icons (kanban / list / calendar / pivot / graph / map / activity);
**authors DROP the ones not relevant to the model.** Default state =
none-active; mark the active one with `.active`.

---

## Settings page (`components/settings.html`)

Source: `odoo/addons/base/static/src/views/setting_view/setting_view.scss`

**Each tab in the left nav carries a small brand-colored app icon**
(sprite glyph from `app-icons.svg`, colored inline via `style="color:#xxx"`).
Drop the icon entirely on **General Settings** (which has no app
ownership).

**Section bands.** Real Odoo settings groups sit under
**full-width gray header bands** (Users, Languages, Companies, …),
not just bold-text titles. Use `.o_horizontal_separator` for the band.

**Save / Discard buttons** sit in the SAME ROW as the page title,
top of the right column — NOT in the control panel's
`.o_control_panel_main_buttons` slot.

---

## Activity views (`components/activity_list.html` + `activity_matrix.html`)

There are **two** activity surfaces, with different markup:

| Variant | When | Source |
|---------|------|--------|
| `activity_list.html` | Global activity action (`mail.mail_activity_action`) — a flat list of every pending activity | `odoo/addons/mail/static/src/views/web_activity/` |
| `activity_matrix.html` | Per-model activity tab — records × activity-types matrix with count cells | same module, matrix renderer |

`activity.html` stays as an alias for the matrix variant so legacy
mocks don't break.

---

## Kanban polish (`components/kanban.html`)

**Cards carry, top to bottom:**

1. **Top-bar** (`.o_kanban_record_topbar`): priority stars (left) + 3-dot
   menu (right). The priority widget is 3 stars; mark filled stars with
   `.o_priority_on`.
2. **Title** (`.o_kanban_record_title`).
3. **Subtitle** (`.o_kanban_record_subtitle`): amount + date or similar.
4. **Bottom row** (`.o_kanban_record_bottom`):
   - Tags on the left (`.o_tag`).
   - `.o_kanban_record_right` on the right with: activity status dot
     (`.o_activity_dot` + state class), days-old badge
     (`.o_kanban_age_badge`), salesperson avatar (`.o_user_avatar`).

**Lost / Won cards** get a diagonal corner ribbon via
`<div class="o_kanban_ribbon o_kanban_ribbon_lost">Lost</div>` (red) or
`.o_kanban_ribbon_won` (green). Position the ribbon as the FIRST child
of `.o_kanban_record`.

**Column header** carries an optional 1-3 segment progress bar
(`.o_kanban_progressbar`) above the title showing the breakdown of
records in that column (e.g. CRM: won-green / lost-red / in-progress-amber).
Header also carries a `.o_kanban_header_amount` next to the count.

---

## Pivot expand affordances (`components/chart_views.html`)

Row and column headers carry `[+]` / `[-]` glyphs (`.o_pivot_expand_btn`)
to signal drill-down. The catalog uses literal `[+]` text inside the
span — pure CSS, no JS toggle behavior needed for the mock. The visual
affordance is what matters.

---

## Layout variants vs base fragments

Some surfaces have multiple legitimate layouts depending on context.
The catalog ships both:

| Surface | Base | Variant |
|---------|------|---------|
| Login | `login.html` (card-only, backend installs) | `login_website.html` (embedded in website chrome) |
| Calendar | `chart_views.html` calendar block (month grid) | `calendar_week.html` (hour grid + sidebar) |
| Dashboard | `dashboard.html` (top-tab section switcher, INSIDE a category) | `dashboard_sidebar.html` (left category nav, landing page) |
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
[Workflow: Purchase ▾]   [< Previous]   [Next >]   [Step title + desc]   [● ● ●]   [counter]   [chips]   [Annotations]
 └ scope chip (left)     └ navigation              └ per-step context     └ dot row             └ variant filters
```

DOM order in `walkthrough_bar.html` is meaningful and reads left → right as
the user's mental hierarchy: `[Workflow scope] [Prev/Next] [Step context] [dots] [counter] [chips] [Annotations]`.
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
