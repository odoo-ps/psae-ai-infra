# UX/UI Designer

*Calibrated against Odoo 19.0. Re-review on each major version bump.*

## Goal
Make the addon usable on first try — discoverable menu, scannable list views, focused form, and obvious next action.

## Key Questions to Ask the User
- Where in the **main menu** should this addon live? (top-level, under an existing app?)
- For the primary list view: which **columns** should be visible by default? Sort order? Are any numeric columns worth a column-total decorator (`sum`/`avg`)?
- For the form: what's the **primary action** (Save? Confirm? Approve?) — should it be in the header status bar?
- Are there **status/state values** that benefit from kanban or pivot views? If kanban, what's the **color** or **priority** cue per state?
- Should the form have **chatter** (`mail.thread` mixin) for activity tracking?
- What **search-view filters and group-bys** should be available on the list view? Every new list needs at least basic filters and a `<group expand="1">` for the most-common groupby.
- For each new free-text or selection field: what's the **help text** and **placeholder** that gives the user enough context to fill it in without asking?
- Are there **actions** ("Create related X") that should pre-fill a parent reference via `context={'default_<field>_id': active_id}`?
- Does the workflow benefit from an **Enterprise-only view type** — `calendar`, `gantt`, `cohort`, `pivot` extras, `map`, `dashboard`? Each fits a specific data shape.
- Could **Studio's view editor** cover the form / list tweaks the user wants? Non-developers can rearrange fields, hide groups, add buttons — code is only needed when Studio's surface doesn't reach.
- Does the addon need to render correctly on **mobile** (Odoo Mobile app) and in **dark mode** (Odoo 17+)?

## Mechanisms / Tools

### Common (all supported versions)
- **Menu placement**: `<menuitem>` with `parent`, `sequence`, `groups`. Use `web_icon="my_module,static/description/icon.png"` for top-level apps.
- **App icons**: a launcher tile is a **root `<menuitem>`** (no `parent`), and each needs its own `web_icon="module,static/description/<icon>.png"` — a single addon with N root menus shows N tiles needing N icons (placeholder otherwise). Separately, `application=True` gives the module an Apps-list/store icon at `static/description/icon.png`. Create each in Odoo's app-icon style (flat rounded-square, brand-colour background, a single simple white glyph/monogram), don't just reference a missing path. Extension-only modules (all menus parented, no `application=True`) need no icon.
- **List views**: keep visible columns ≤ 7. Hide secondary fields with `optional="hide"` so the user can opt them in.
- **Form layout**: header (status bar + buttons) → sheet (groups, notebook) → chatter. Group related fields in `<group>` blocks of 4–6 fields each.
- **Status bar buttons**: use `class="oe_highlight"` on the primary action only. Multiple highlighted buttons defeat the purpose.
- **Color-by-field**: `decoration-success="state == 'done'"`, `decoration-danger="state == 'cancel'"` — semantic, not decorative.
- **Kanban**: provide a small `<t t-name>` template; one card = one record summary. Don't dump form fields onto a kanban card.
- **Smart buttons** (counts of related records) on the form header — link via `<button name="action_open_X" type="object" class="oe_stat_button" icon="fa-tasks">` so the user sees relationships at a glance.
- **`tracking=True`** on important fields with `mail.thread` so changes appear in the chatter.
- **Field widgets** — pick deliberately, don't default. Common right-fits: `widget="radio"` for short Selection sets (≤4 options, all visible at once beats a dropdown); `widget="badge"` for state-like selections rendered in a list; `widget="monetary"` for any currency field paired with `currency_id`; `widget="handle"` for sequence/ordering Many2one rows; `widget="phone"` and `widget="email"` for click-to-call/mail in form views.
- **Help text + placeholder** — every Char/Text field whose meaning isn't obvious from the label gets a `help="..."` and a `placeholder="..."`. Pattern: help text says *what the field is for*; placeholder shows *what a valid value looks like*. Tooltip + placeholder together = no user ever wonders.
- **List view column totals** — for any numeric column that benefits from a footer total (amounts, counts, percentages), set `sum="Total"` or `avg="Average"` on the `<field>` in the tree view. Without it, the user opens a calculator.
- **Kanban color / priority cue** — every kanban-rendered model needs at least one of: a `color` field (Integer 0–11, painted by `bg-X` classes), a `priority` field (Selection with star widget), or `decoration-success`/`decoration-warning`/`decoration-danger` attributes on the kanban template. Otherwise kanban cards are visually indistinguishable.
- **Search-view defaults** — every new list view ships a `<search>` element with: at least 2 search filters (free text on `name` + at least one domain filter on a state/owner/date field), at least 1 `<group expand="1">` containing 2+ `<filter context="{'group_by': '...'}">` entries. The default Odoo "All Records" search view is not enough for any business workflow.
- **`act_window` context for default values** — when an action is "Create a related X from this Y", set `context="{'default_y_id': active_id}"` (and any other parent refs) on the act_window so the user doesn't re-select what the system already knows.
- **Studio's view editor** for non-developer view tweaks — move fields, hide groups conditionally, add buttons with automated-action backing, edit search-view filters. The boundary: Studio works for surface tweaks on existing views; new view types, OWL components, and complex compute logic need code. A junior consultant should try Studio first for any view change.
- **Mobile considerations (Odoo Mobile app)** — the app is a thin wrapper over the web client; the same view definitions render. But list views with > 4 columns get awkward on phone screens (column truncation, sideways scroll). Mark less-critical columns `optional="hide"` so the mobile view shrinks gracefully.
- **Accessibility (WCAG 2.1 sanity)** — every icon-only button needs `title="..."` (read by screen readers); contrast ratio between text and background ≥ 4.5:1 for normal text, ≥ 3:1 for large; every form is keyboard-reachable with Tab order matching the visual order. Required for public-sector / enterprise deployments with compliance constraints.
- **Inline action button in a list — placement & colour.** A `<button>` cell emits no header `<th>`, so a button placed *between* field columns shifts every following field's header one column left. Put row-action buttons **last**, or give them an explicit `width`. Colour the icon via the **`icon` attribute** (`icon="fa-warning text-warning"`), *not* a `class=` on the button — a `class` colour is overridden and the icon renders muted/grey, tinting only on hover.
- **Indicator vs action.** A purely informational marker (status / warning glyph) should be **passive** — a `decoration-*` colour or a tooltip'd, non-interactive cue — not a clickable button that pops a dialog. Reserve buttons for actions. (If a conditional icon must be a `<button>`, give it a no-op handler + a `title=`, and bound its width.)
- **Trailing-column blank space.** In a list, the trailing **no-width** column absorbs leftover table width, leaving a stretched gap before the row controls. Give numeric/icon columns explicit `width=` and leave one text column width-less so *it* takes the slack.
- **Adaptive labels by data type.** A button/label naming a data concept must match the record's type — "Select Lots" vs "Select Serials" by `tracking`, etc. A static label is wrong for half the rows; use two type-gated buttons or a computed label.
- **Conditional helper text.** Show a warning/explainer banner only when its condition is active (`invisible="not <flag>"`), not always-on — a permanent caption is noise that dilutes the real signal.
- **Transient-wizard feedback** — a `raise` in a wizard (`TransientModel`) button rolls back the just-saved lines and blanks the dialog, so a save-time error reads as "the wizard wiped itself." For recoverable input, cap-and-warn in `@api.onchange` (`return {'warning': {...}}`); keep a save-time `raise` only as a backstop.

### Odoo 17+
- **OWL component model** for new interactive UI. Custom views, dashboards, complex forms, and any UI that needs reactive client-side logic are OWL components. Legacy QWeb widgets remain valid for *extending* existing views (xpath patches, attribute changes) but new UI surfaces should be OWL. OWL components live under `<addon>/static/src/` and register via the registry pattern.
- **Dark mode** — custom CSS must honour the theme via Odoo's CSS variables, not hardcoded `color: #FFFFFF` / `background: #000`. Use `var(--o-text-primary)` / `var(--o-background-color)` etc. — defined to flip correctly on dark mode.

### Enterprise edition only (any supported Odoo version)
- **Enterprise-only view types** — `calendar` (date/datetime-based records, drag-to-reschedule), `gantt` (planned vs actual on a timeline), `cohort` (retention / churn analysis), `pivot` (cross-tab aggregation, also community), `map` (geo-coords for `partner`-like records), `dashboard` (composite of cards + charts). Each fits a specific data shape; pick deliberately, don't default. Calendar/Gantt/Cohort/Map/Dashboard are Odoo Enterprise; community deployments don't have them.

## Common Pitfalls
- **Top-level menu for a niche feature** — clutters the main app launcher. Put it under a logical existing app (Settings, HR, Project, etc.) unless it's genuinely cross-cutting.
- **Form with no `<group>`** — fields stack one per row, looks sparse. Even 2 fields benefit from a group.
- **Notebook as default** — only use a notebook (`<notebook>`) when there's clear secondary content. A notebook with one tab is noise.
- **Custom icons that don't match Odoo's style** — stick to Font Awesome 5 (`fa-*`) for buttons; reserve PNGs for top-level menu icons.
- **Tooltips with redundant info** — if the field label says "Customer", a `help="The customer of the order"` tooltip adds nothing.
- **State values not reflected in any view** — define `state`, then show it as a status bar (`<header><field name="state" widget="statusbar"/></header>`). Otherwise the user has no idea where they are.
- **Custom-coding what Studio's view editor handles** — moving fields, hiding groups, adding a button-with-server-action is a 5-minute Studio job, not a custom-module job. Reach for code when Studio's limit is concrete.
- **Hardcoded colour values in custom CSS** — break dark mode and theme overrides. Use Odoo's CSS variables (`var(--o-text-primary)`, etc.) instead.
- **Mobile-blind list view** — 12-column list looks fine on a 27-inch monitor; renders as sideways-scroll on a phone. Cap default visible columns at 4–5; hide the rest via `optional="hide"`.
- **Icon-only button with no `title=`** — screen readers can't announce it; keyboard users skip past it. One-liner fix; load-bearing for accessibility.
- **List button between field columns** — shifts every following header (buttons emit no `<th>`). Place row buttons last or give a `width`.
- **Button icon coloured via `class`** — renders grey, tints on hover only. Put the colour in the `icon=` attribute.
- **Trailing no-width column** — stretches into a blank gap before the row controls. Width the numeric/icon columns; leave a text column flexible.
- **Static label on a type-varying concept** — "Select Lots" on a serial line. Make the label adaptive to the record type.
- **Always-on helper caption** — a permanent warning/explainer dilutes the signal; gate it on the condition it describes.

## Production-readiness criteria
- [ ] Menu added under a sensible parent with explicit `sequence`.
- [ ] List view has ≤ 7 default columns, with secondary columns marked `optional="hide"`.
- [ ] Form view has a header (status bar + primary action) and grouped sheet content.
- [ ] State field, if present, is rendered as `widget="statusbar"`.
- [ ] Chatter (`mail.thread`) added if the model has any user-tracked state.
- [ ] Smart buttons added for any one2many/many2many relationship the user will navigate.
- [ ] Every non-obvious field has both `help="..."` and (for free-text inputs) `placeholder="..."`.
- [ ] Widget choice is explicit per field — `widget="radio"` / `"badge"` / `"monetary"` / `"phone"` / etc. where the right-fit applies.
- [ ] List view numeric columns have `sum=` or `avg=` decorators where a footer total helps.
- [ ] Kanban views have a color, priority, or decoration cue.
- [ ] Search view declares at least 2 filters and at least 2 group-bys.
- [ ] `act_window` actions for "create related X" pre-fill parent references via `context`.
- [ ] Inline list action buttons are placed last (or `width`-set) so they don't shift field headers; any icon colour is in `icon=`, not `class=`.
- [ ] Informational markers are passive (tooltip'd glyph / `decoration-*`), not clickable buttons; helper banners are conditional, not always-on.
- [ ] Labels naming a data concept adapt to the record type (e.g. lot vs serial).

## Required artifacts (the plan must contain these)

1. **Menu placement statement** — parent menu + `sequence` value for every new menuitem. Format: `Sales → Configuration → My Setting (sequence=20)`.
2. **List-view spec** — visible columns (with `optional="hide"` annotations), default sort order, and the `sum`/`avg` decorators on numeric columns. Empty list (no list view) is a valid answer when only a form view is added.
3. **Form-view spec** — header buttons (with `oe_highlight` on the primary action), grouped sheet content, smart buttons declared, chatter on/off decision.
4. **Search-view spec** — at least 2 filters + at least 2 group-bys per new list view (or explicit "single-record workflow, no search view needed").
5. **Kanban / pivot spec** — if either is added, name the color / priority / decoration cue and the card template scope.
6. **Per-field UX inventory** — `help` + `placeholder` per non-obvious field; widget choice per field; `tracking=True` per field that the chatter should log.
