# Odoo mock style guide — tokens, rules, source map

The fidelity bar is **"recognizably Odoo"**: a viewer should glance at a screen
and think "that's Odoo", without us chasing pixel-exact parity. Everything you
need is already in `catalog/odoo.css` as CSS custom properties. **Use the
tokens; never hard-code an off-palette color or font.**

The catalog tracks ONE Odoo version — the **calibrated version** stamped on the
first line of `catalog/odoo.css` ("calibrated to Odoo NN Enterprise"; history in
`REFRESH.md`, sources in § Source map). Every value and rule below describes
that version. The default edition is **Enterprise**.

## Design tokens (all in `:root` of `catalog/odoo.css`)

| Token | Value | Use |
|---|---|---|
| `--o-brand-primary` | `#714B67` | Enterprise plum — ONLY `btn-primary`, `btn-outline-primary` (form "New") and the notebook active-tab bar |
| `--o-action` (= `--o-enterprise-action-color`) | `#017e84` | Teal — links, relational values, checked checkboxes/radios, active / selected / focus states |
| `--o-component-active-bg` | `#e6f2f3` | Teal tint behind active / selected items (search-panel row, settings tab, current stage) |
| `--o-main-link-color` | `#017e84` (hover `#01585c`) | Links — never underlined, not even on hover |
| `--o-community-color` | `#71639e` | Community brand (`body.o-community`) |
| `--o-gray-100 … --o-gray-900` | `#f8f9fa … #212529` (200 = `#e7ebed`) | Page background, borders, muted text |
| `--o-success / warning / danger / info` | `#00a945 / #f59e0b / #ef4444 / #17a2b8` | Badge tints, alerts, activity states |
| `--o-text-success / info / warning / danger` | `#008818 / #0180a5 / #9a6b01 / #d23f3a` | Text-on-white variants (`.text-*`) |
| `--o-favorite` | `#f3cc00` | Priority / favorite stars |
| `--o-font-family` | system stack | Body text (no web font — keeps packages offline) |
| `--o-font-size-base` | `0.875rem` = 14px (root 16px) | Body, buttons, labels; `-sm` 13px (small text, `.btn-sm`), `-smaller` 12px (badges, tags) |
| `--o-font-weight-bold` / `-bolder` | `500` / `700` | Backend "bold" is 500 (headings, `.fw-bold`, buttons, labels, badges); 700 only for `.fw-bolder`. Frontend (`.o_website` / `.o_portal` / `.pos`) keeps 700 |
| `--o-font-size-h1 … h5` | 33.6 / 21 / 18.2 / 16.8 / 15.4px | h1 = record title (weight 500, black) |
| `--o-spacer` | `16px` | Default padding/margins |
| `--o-border-radius` (`-sm` / `-lg` / `-xl` / `-pill`) | `6px` (4 / 8 / 12px / 50rem) | default (buttons, inputs, badges) / btn-sm / sheet, modal, chatter avatar / list & kanban containers / badges, tags, search bar |
| `--o-statusbar-height` | `33px` | Statusbar = button height |
| `--o-form-sheet-max-width` | `1400px` | Form sheet area max width |
| `--o-navbar-height` | `46px` | Navbar |

**Edition.** `body.o-community` switches the whole palette, not just the brand:
radius 4/3/6px, semantic colors `#28a745 / #ffac00 / #dc3545`, link `#66598f`,
gray-300 secondary-button fill, solid badges, borderless tags, a `#ccc` input
underline, h1 28px, no button sheen, purple navbar. Never scale the root font
(`html` stays 16px) — the catalog's px values are the calibrated version's px.

## Rules (what makes a mock read as Odoo)

1. **One gray canvas; only view surfaces are white.** The page is gray-100.
   Navbar, control panel, search panel, statusbar, chatter and report toolbars
   sit transparent on it. White = form sheet, list renderer, kanban cards, graph
   canvas, settings card, report table. Never make the whole page white, never
   paint a white or colored bar behind the chrome.
2. **Navbar is transparent over the page gray** (Enterprise): no bottom border,
   46px, every entry a 26px pill (6px radius, gray-200 hover). Left:
   `a.o_menu_toggle.hasImage` = the current app's real icon (`#o-app-<id>`,
   26px) + app name (16.8px, regular); the 3×3 grid appears only on hover (drop
   icon + `hasImage` only on screens with no app context). Menu sections are
   plain 14px text with **no carets**; an open one is `.o_nav_entry.show` + an
   `.o-dropdown--menu`. Systray, left → right, never reordered: [timesheet
   timer] [Ask AI] Messages · Activities (red count badges) · Studio · company
   name (no caret) · user avatar (one initial). There is no liveness dot and no
   close-all ×. Use the SAME navbar markup on every screen
   (`components/navbar.html`). `body.o-community` restores the purple bar.
3. **Control panel has no bar of its own** — page gray, no border, ONE row:
   [New / main buttons][title + ⋮] | centred pill search | [pager][view
   switcher]. A single-level title is 16.8px **regular**; a drill-down is two
   lines (13px teal link to the immediate parent over the record name). The
   action menu is **⋮** (`#o-ellipsis-v` in `o_btn_circle btn-light`) inside
   `.o_breadcrumb` — never a cog, no favorite star. Details: § Control panel &
   search panel; markup: `components/control_panel.html`.
4. **One filled plum `btn btn-primary` per cluster; every other action is
   `btn btn-secondary`** — white, `#ced4da` border, 6px radius, 33px tall
   (statusbar, dialog footer, chatter Log note / Activity, pager). Icon-only
   toolbar buttons are `btn btn-light`; inline actions ("Add a line") are teal
   `btn-link`, never underlined; join pairs in `.btn-group`. Never shrink or
   recolor buttons per view. `o_btn_outline` is a deprecated alias — write
   `btn-secondary`.
5. **Form statusbar** is the first child of `.o_form_sheet_bg`, on the gray (no
   white strip, no border). Left: workflow buttons (rule 4 — at most one
   primary). Right: ONE white, bordered, rounded `.o_statusbar_status` group
   inside `.o_field_widget.o_field_statusbar`, stages left → right, exactly one
   `o_arrow_button_current` (teal tint, black text). Readonly `state` pipeline:
   every stage `disabled`, the others muted; clickable `stage_id` pipeline: only
   the current stage disabled. Never a solid purple fill.
6. **Form fields are clean text — no resting underline, even when required**
   (it shows only on hover / focus). Empty readonly value → renders NOTHING
   (`o_field_empty` + `o_form_label_empty` on the label), never an em-dash;
   empty editable value → its pale placeholder (`o_input_placeholder`).
   Readonly labels add `o_form_label_readonly` (muted); invalid fields get
   `o_field_invalid` on label AND widget. Booleans, radios and selection badges
   are real inputs (`o-checkbox form-check`, `form-check o_radio_item`;
   `form-switch` only for `boolean_toggle`) — never ☐ / ● / ○ glyphs. Form dates
   are non-numeric ("Oct 6, 12:29 PM", "Sep 1 → Oct 1"). The mock-only "please
   fill this" cue is `.o_input_pending` (§ Input affordances).
7. **Icons are the real ones, from the sprite, INLINED into `index.html`**,
   referenced with same-document `<use href="#o-id">` inside
   `<svg class="o_icon">`. Never link an external sprite
   (`<use href="assets/icons.svg#id">`) — external SVG `<use>` is blocked over
   `file://`, so the icons vanish when the package is opened as a file. Never
   hand-draw a glyph, never load FontAwesome / a CDN, never `<img>` an external
   icon, never type a Unicode stand-in (→ ⋮ + − ▾ ● ✓ ×) where Odoo renders an
   icon. Missing glyph? Extract it (§ Sprite catalog › Adding a glyph).
8. **No external anything.** No CDN CSS/JS/fonts/images, no `https://` asset, no
   tracking. `_lint_mock.py` enforces this and the lint is a release gate.
9. **Realistic placeholder data, not Lorem ipsum.** Use plausible Odoo-style
   names (Deco Addict, Mitchell Admin, SO0042). The linter rejects `Lorem ipsum`,
   `TODO`, `TBD`.
10. **Teal marks links and state; plum marks the primary action.** On a form,
    relational / URL values are teal links (`<a class="o_form_link">`). **List
    cells are plain dark text — relational columns included**; teal in a list
    is only a many2one the view renders readonly as a link (`a.o_form_uri`) and
    `btn-link` buttons. Active / selected / checked / focus states are teal
    (`--o-action`, `--o-component-active-bg`) — never brand plum.
11. **Status badge ≠ tag; avatars are squares.** A state / status is
    `<span class="badge rounded-pill text-bg-{success|info|warning|danger|primary|secondary|300}">`
    — a 15% tint with dark text, never solid (`300` = neutral gray). A many2many
    value is `<span class="o_tag o_badge badge rounded-pill o_tag_color_N"><div class="o_tag_badge_text">…</div></span>`
    — a bordered pastel pill from the 12-colour palette (0 = gray, e.g. taxes);
    several go in `<div class="d-flex flex-wrap gap-1">`. Avatars are rounded
    squares with ONE initial on a palette color (`.o_user_avatar.o_avatar_c0..c7`,
    no inline style; 24px in m2o / list / kanban, 32px in chatter); keep one
    color per person across the mock. For sale / purchase / invoice, close the
    lines with an **`o_subtotal_footer`** (right-aligned Untaxed / Tax / Total).
12. **Place standard fields where Odoo does — discovered at runtime** from the
    live `odoo/`/`enterprise/` source (`reference/field_placement.md`), not a
    cache. Standard fields the brief doesn't change stay in their real group/tab
    (e.g. `sale.order` Warehouse & Salesperson on *Other Info*, never the main
    sheet). Only **solution-added fields** (stored / computed / related /
    relational, plus standard fields the solution overrides — see
    `interactions.md` § Custom-field help) are placed by judgment + carry the
    `?`. If the Odoo source isn't available, **warn** that screens are
    best-effort.
13. **Make it behave like a prototype, not a slideshow** — use the
    `reference/interactions.md` hooks (tabs switch, modals open in place,
    dropdowns reveal, toasts confirm). But never fake computation/validation/
    persistence — a mock shows states and the path between them.
14. **Surface-native vocabulary — backend classes never cross the surface
    boundary.** Backend chrome (`o_field_row`, `o_form_label`, `o_field_widget`,
    `o_input`, `o_group`, `o_inner_group`, `o_list_view`) is for the **backend
    form / list views ONLY**. Inside `.o_website`, `.o_portal`, or `.pos` reach
    for the surface-native equivalent below — NEVER smuggle backend rows in,
    and NEVER hand-roll an inline `style="background:color-mix(...);border:...;"`
    callout box. Both drifts are flagged by mock-fidelity-anchor as
    `fidelity:surface-backend-leak` / `fidelity:inline-callout`.

    | Need                              | Backend (form view)               | Website (`.o_website`)                    | Portal (`.o_portal`)                          | POS (`.pos`)                           |
    |-----------------------------------|-----------------------------------|-------------------------------------------|-----------------------------------------------|----------------------------------------|
    | Field row (label + input)         | `.o_field_row` + `_label` + `_widget` | `.s_website_form_field` + `_label` + `_input` | (use `.s_website_form_*` inside `.o_portal_doc_main`) | `.pos-popup-row` (inside `.o_dialog`)  |
    | Read-only label / value pair      | `.o_field_row`                    | `.s_website_form_field` (static value)    | `.o_portal_kv` + `.o_portal_kv_label/_value`  | `.pos-popup-row`                       |
    | Required-field mark               | `.o_required_modifier` on input   | `.s_website_form_mark` "*" inside label   | (same as website)                             | n/a (POS popups don't mark required)   |
    | Help text under a field           | `<span class="o_field_help">?` ↗ help | `.s_website_form_help`                | (use `.s_website_form_help`)                  | (use `.s_website_form_help`)           |
    | Inline tinted callout / disclosure | `.alert.alert-{info\|success\|warning\|danger}[role=alert]` (§ Form) | `.s_website_form_note`   | `.o_portal_note` + `_info/_success/_warning/_danger` | `.pos-callout` + same tone modifiers |
    | Section divider inside a form     | `.o_horizontal_separator`         | `.s_website_form_section`                 | (use `.s_website_form_section`)               | n/a                                    |
    | Action row (submit / accept)      | statusbar buttons                 | `.s_website_form_submit` row              | `.o_portal_actions`                           | `.o_dialog_footer` (POS popups)        |
    | Submit / primary CTA              | `.btn.btn-primary`                | `.btn.btn-primary.s_website_form_send`    | `.btn.btn-primary`                            | `.btn.btn-primary.btn-lg`              |
    | Small print / caveat              | `text-muted` paragraph            | `.s_website_form_help`                    | `.o_portal_sidebar_note`                      | (inside a `.pos-callout`)              |

    Catalog component files (`portal.html`, `website_form.html`, `pos.html`)
    carry the worked markup for each row of this table. When a need genuinely
    has no surface-native class, **extend the catalog** (propose promotion in
    `REFRESH.md`) — do not inline-style and hope.

## Annotations

- Numbered/`i` markers: `<span class="mock-marker" data-note="...">N</span>`.
- **Default placement is INLINE adjacent to the referent.** Drop the marker
  as a sibling immediately after the element it explains — a button, a field
  label, a badge, a column header. The marker sits on the same baseline as
  its referent so the reader's eye connects them with no guess.
- **Do NOT use inline `style="position:absolute;top:Npx;right:N%;"` on a
  marker.** Visual audits across the corpus have repeatedly found
  absolute-positioned markers floating over data cells, on column headers,
  or in dead space — the `top`/`right` coordinates are guesses against an
  unknown ancestor's coordinate system. A bare absolute marker anchors to
  the nearest positioned ancestor, which is usually NOT the screen container
  the author had in mind. `_lint_mock.py` flags this as a KNOWN-BAD pattern.
- **Absolute positioning is only valid when wrapped in a `.mock-anchor`
  (`position: relative`) parent.** When a marker must sit absolutely over a
  specific element (an icon, a badge, a corner of a card), wrap the referent
  in `<span class="mock-anchor">…<span class="mock-pin">N</span></span>`.
  The `.mock-anchor` scopes the absolute positioning to the referent itself.
- Keep notes to one or two sentences, grounded in the brief — a marker
  explains *why this element matters to the solution*, not what a generic
  Odoo field is.
- The annotations toggle in the walkthrough bar hides all markers for a
  clean "screenshot" view.
- **Custom elements** are marked with `mock-custom`, not with markers: on
  what the solution adds or changes (a light-pink highlight), or on the
  `.mock-screen` of a screen that is new from end to end (a small Custom
  banner across the top-right corner). Placement table: `interactions.md`
  § Custom elements. The **Custom** chip beside Annotations hides them.
  Never hand-roll a custom indicator — an inline pink style, a "Custom" /
  "New" badge, an `o_widget_web_ribbon` — the class is the only one.

### Variants vs data multiplicity (load-bearing)

A variant axis applies when **one record / one context** renders
differently under a lens (state, actor, version). It does NOT apply
when the data model itself carries multiplicity (multiple lines,
multiple records, multiple cards).

| Situation | Right model |
|---|---|
| One Sales Order, viewed at Draft vs Sent vs Confirmed | `state` variant axis (same record, different lens) |
| One product, viewed by Sales rep vs Customer portal | `actor` variant axis (same record, different lens) |
| One workflow's UoM rendering: Each vs Box vs Kg | `uom` variant axis (same record, different lens) |
| One order that has **both** a lot-tracked line AND a serial-tracked line | **NOT** a variant axis — show both lines as data. The order's lines table simply has 2+ tracked rows. |
| A picker dialog whose shape differs by product (lot vs serial) | **Variant axis is correct** — same dialog context, different rendering per product type the user opened it for. |
| Multi-warehouse customer with one quote per warehouse | **NOT** a variant axis — separate records; if both matter, show both in a list or as separate screens. |

The test: *"is this the same record / same context being rendered
differently, or is this actually multiple data items?"* If the data
model carries the variation naturally (an order with many lines, a
customer with many addresses, a kanban with many cards), surface it as
**data** and skip the axis. Variants are for cases where, looking at
the same record at a moment in time, there's a meaningful "but what if
I changed this lens?" question.

**Anti-pattern.** Tracking-type as a variant axis on a Sales Order
where the order can carry both lot-tracked AND serial-tracked lines.
That collapses two distinct lines into one alternated rendering and
forces the reader to pivot a chip to see what's literally on the
record.

### Guard rendering — action-triggered error dialogs

When a State-axis value sets up a guard condition (line is partially
allocated; lot reserved by another transfer; etc.), the **happy state
is the default rendering**. The error modal opens **when the user
clicks the gated action**, not by default at the state.

This matches real Odoo: an Odoo form doesn't auto-open an error modal
when you load it — the modal fires only when you click the action
button (Confirm, Validate, Post, …) that would fail. The State value
shows the SETUP for the failure (the Unallocated badge, the partial-
allocation indicator, etc.); the user clicks the action button to see
the modal. The one exception is an **attempt** value — a variant that
names the action itself ("Change a locked timesheet", "Set to Draft"):
there the dialog is open by default. Full rule, and the `GUARD-LANDING`
lint that enforces it: `interactions.md` § UserError / ValidationError
dialog.

Use Odoo's standard error-dialog anatomy (§ Wizards / Dialogs):

- `.o_dialog.o_dialog_user_error` (`.o_dialog_validation_error` for a
  constraint) — a small, minimal dialog: no colored header bar, an
  `<h4 class="modal-title">` plus the `.btn-close` X.
- The title comes from the exception: a blocked action (UserError) reads
  **Invalid Operation**; a constraint (ValidationError) reads
  **Validation Error**. Never "User Error".
- The body carries the rule's message in user-facing Odoo voice
  (imperative + concrete, no spec citations) inside `<div role="alert"><p>`.
- The footer has ONE left-aligned `btn btn-primary` Close.

```html
<!-- Default-closed; opens on Confirm click at the guard state -->
<div class="o_dialog_backdrop" data-mock-modal="confirm-blocked"
     data-mock-variant="state=unallocated">
  <div class="o_dialog o_dialog_user_error">
    <div class="o_dialog_header">
      <h4 class="modal-title">Invalid Operation</h4>
      <button class="btn-close" type="button" title="Close" aria-label="Close" data-mock-modal-close></button>
    </div>
    <div class="o_dialog_body">
      <div role="alert"><p>Allocate lots or serials on every tracked line before confirming this quotation.</p></div>
    </div>
    <div class="o_dialog_footer">
      <button class="btn btn-primary" data-mock-modal-close>Close</button>
    </div>
  </div>
</div>

<!-- Confirm fires the modal when clicked -->
<button class="btn btn-primary"
        data-mock-variant="state=unallocated"
        data-mock-modal-open="confirm-blocked">Confirm</button>
```

The `data-mock-variant` on the backdrop scopes WHICH modal opens for
which State (the right error for the right setup). When the State
value changes (e.g. user picks lots, state advances to Allocated),
the backdrop's variant no longer matches → modal won't open even if
the action button is clicked.

**Anti-pattern**: opening the modal by default at the guard State
variant. That treats the error as the primary rendering of the
screen, which makes the happy path feel like the exception. The
correct rendering is: happy state visible, error only when the user
attempts the gated action.

`mock-fidelity-anchor` flags an invented inline `.alert` / custom
guard-banner element in place of the UserError modal. (`.alert` is only for
persistent context on a form — § Form.)

### Interactive-path completeness

The mock isn't just a slideshow — clicking through the in-screen
actions must advance the workflow naturally. Specifically: **every
in-screen action that changes a downstream screen's state must carry
both `data-mock-set-variant` AND `data-mock-goto`**.

The pattern:

```html
<!-- Picker Save → set the Quote to state=allocated, then navigate to Quote -->
<button data-mock-set-variant="quote:state=allocated" data-mock-goto="quote">Save</button>

<!-- Quote Confirm (at state=allocated) → set state=locked, navigate to Delivery -->
<button data-mock-variant="state=allocated"
        data-mock-set-variant="quote:state=locked"
        data-mock-goto="delivery">Confirm</button>
```

Without `set-variant`, the target screen retains whatever variant it
was last left at — clicking Save from the picker would return to a
Quote still showing `state=unallocated`, breaking the click-through
illusion. The reviewer is forced to manually pivot the State chip on
the chrome to see the post-save state.

**Anti-pattern**: an action button with only `data-mock-goto` that
navigates to a screen whose variant should have advanced.
`mock-coverage-anchor` flags this as `coverage:no-state-mutation`.

The chip-row chrome stays available for **direct walk** of edge-state
variants (partial allocation, lot-unavailable race condition) that
don't have a natural click path. The interactive set-variant covers
the **happy path + main alternates**.

### Body copy reads as Odoo — no brief citations

Banner text, toast text, error messages, system-log entries, activity
descriptions, help strings — anything rendered as **user-facing copy
inside Odoo** — must read like what the user would actually see in
production. Specifically:

- **No "(Rule #N)" or "(Spec § X)" citations** in body copy. The user
  doesn't see rule numbers in real Odoo; the rule reference is
  internal-to-the-spec metadata. Cite it in the marker's `data-note`
  if it matters for the reviewer — never in the visible text.
- **No "(per the spec)" or "as designed" footnotes.** Same reason.
- **No documentation voice** in the body. Real Odoo error text is
  imperative + concrete: *"Allocate the remaining units before
  confirming."* — not *"As per Rule #1, you need to allocate every
  unit (see User Story #4)."*

If a guard's rationale matters for the reviewer, attach a marker next
to the banner whose `data-note` carries the citation. The banner
itself stays user-facing.

`mock-coverage-anchor` flags banners/toasts/messages with citation
suffixes as a `coverage:body-cites-spec` finding.

### Body copy comes from the spec, not invented

Chatter messages, activities, system-log entries, log notes,
toast text — every piece of body copy must trace to a spec element
(the brief's automated behaviors, user stories, rules, or example
language). **Don't invent content** the spec doesn't define.

Common temptations that produce invented content:

- Adding an "Activity scheduled" entry to chatter when the spec
  doesn't define any scheduled activity on the workflow.
- Writing customer-conversation log notes ("Sara mentioned LOT-CT-006
  in the call yesterday") to make the chatter feel realistic — when
  no such conversation exists.
- Drafting a richer error message than the spec specifies.

If the spec is silent on what the chatter should carry, render the
chatter with **only the system-derived entries** the workflow
genuinely produces — state transitions ("Stage changed from Quotation
to Sales Order"), references created ("Delivery WH/OUT/00148
created"). Those are derived from the data model, not invented.

For activities specifically: only render an activity if the spec's
*Automated Actions* table explicitly defines one. Otherwise leave the
activities tab empty (just the topbar button).

### Tracking-aware affordance labels

When an affordance's behavior is driven by data (e.g. Select Lots
opens a lot picker on a lot-tracked product, but the same affordance
would open a serial picker on a serial-tracked product), the
**affordance label must match the data** — "Select Serials" on the
serial-tracked line, "Select Lots" on the lot-tracked line.

This is **data-driven labeling**, NOT a variant axis on the affordance
itself. Each row in the data has its own label derived from its
own tracking attribute.

```html
<!-- LOT-tracked row -->
<a class="o_form_link" data-mock-goto="picker">Select Lots</a>

<!-- SERIAL-tracked row (same affordance kind, different label) -->
<a class="o_form_link" data-mock-goto="picker">Select Serials</a>
```

The picker screen *itself* uses a Tracking variant axis because it's
the same dialog context rendering differently — but the calling
affordance on each line is just a label that reflects its row's data.

### Disabled affordance — drop, don't paint a ghost

When a workflow state disables an affordance (e.g. Select Lots locked
after order confirmation), **don't render the affordance as grayed-out
italic text**. That reads as a half-disabled button and looks like a
mock weakness.

Two acceptable patterns:

1. **Drop the affordance entirely** when its disabled state is
   communicated by other cues (e.g. the lock icon on the badge already
   shows "this is locked"). The reader's question *"can I edit these
   lots?"* is already answered by the lock; no need to also paint
   "Select Lots" in gray.
2. **Render a real disabled button** with `<button disabled>` or
   `<a class="o_form_link is-disabled">`, plus a tooltip explaining
   why it's disabled. This is for cases where the affordance's
   absence would be confusing.

Avoid the third pattern (grayed italic text without interactivity) —
it occupies space without communicating anything beyond what other
cues already say.

### Annotation discipline — load-bearing, not field-by-field

A marker is an overlay that points at a **solution element worth
stopping to read**. It is not a label, not a tooltip, not a footnote on
every input. Treat markers as scarce.

**Aim for 4–7 markers per package**, not per screen. The reader's job
is to walk the workflow and absorb the deltas; a screen with 5 markers
becomes a slide rack, not a screen. Concentrate markers where the
solution **changes Odoo's default behavior** — typically:

**Number markers per screen, not globally across the package.** Each
screen restarts at 1. A continuous package-wide numbering (1 on the
quote, 5 on the delivery) forces the reader to scroll back to find
"what was marker 3 again?" — and is inconsistent with how readers
mentally chunk the walkthrough (one screen = one mental unit). The
cover screen uses an inline `i` example (not a number) since the
cover's marker is illustrative, not workflow-anchored.



- The button or affordance that triggers the new capability.
- The new field whose meaning isn't self-evident from the label.
- The guard / rule that blocks an action the user would otherwise expect.
- The visibility / readonly transition tied to a workflow state.
- The downstream consequence (what the choice on this screen produces).

That's usually 4–7 distinct things for a mid-sized engagement. Going
above that is a signal the workflow has been over-narrated.

**Anti-pattern: one marker per net-new field.** Field-by-field
annotation turns the mock into a documentation sheet and floods the
reader with low-information callouts. If two related fields share one
rationale, **one marker carries the explanation**.

**Anti-pattern: marker text bleeding outside `data-note`.** The
`data-note` attribute is the marker's content; it shows in a floating
tooltip on click. **Do NOT also paste that sentence as a `<p>`
paragraph, footer caption, legend ("🔒 = lot pre-committed…"), or
"what this means" sidebar next to the affected element.** Body copy
in a mock is reserved for what the *user* sees in Odoo: empty-state
text the brief defines, help strings on form fields, the literal
warning Odoo would render for a guard. Explanatory text *about the
mock itself* — what an icon represents, why a button is disabled, what
a variant axis controls — belongs only inside `data-note` or on the
cover screen.

The leak shapes to watch for:
- Footer legend (`🔒 = …`, `* = …`).
- "What you're seeing" paragraph above or below a table.
- "Note:" callouts inside the form sheet.
- Inline parentheticals explaining the chrome to the reader.

If the icon's meaning isn't self-evident, the right fix is **a marker
next to it** carrying the explanation in `data-note`, not a legend
caption.

**Custom-field `?` is its own thing.** The `.o_field_help` "?" tooltip
(see `interactions.md` § Custom-field help) is a developer-facing
attribute panel — it documents a solution-added field's
`field`/`model`/`type` without taking a marker slot. **Every field the
solution adds or modifies earns the `?`** — that includes net-new
stored fields, computed fields, **related** fields (`related='foo_id.bar'`),
**relational** fields (`Many2one` / `One2many` / `Many2many`, including
reverse relations), and standard fields the solution overrides (new
compute, default, domain, readonly, required, or `depends`). A standard
field used unchanged carries neither `?` nor marker. Solution-added
fields can carry both a `?` AND a numbered marker when their behavior is
load-bearing for the workflow. Its row (column cells, settings box) also
carries `mock-custom`: the `?` documents the field, the mark shows its scope.

### Cover, overview, and meta-content voice — business, never technical

The mock's reader is a **business stakeholder or functional consultant
reviewing a proposed workflow** — not a developer reading code. Every
piece of reader-facing prose in the mock's chrome and overview screens
must read in **business voice**, not technical voice.

**What this covers:**
- Cover callouts (How-to-interact section + workflow-narrative descriptions)
- Per-workflow overview screens (title, subtitle, narrative paragraph,
  actor descriptions, step-list descriptions)
- Screen `data-title` and `data-desc` attributes (visible in the
  walkthrough bar)
- Annotation marker `data-note` text
- Workflow names (`data-workflow-title`)
- Any other reader-facing prose introduced by the package

**Distinct from in-screen body copy.** In-screen text — toasts, error
messages, system-log entries, chatter messages, help strings — reads
like real Odoo (see § Body copy reads as Odoo, § Body copy comes from
the spec). The meta-content rules below cover the prose that EXPLAINS
the workflow and the mock chrome, not the prose Odoo would render.

**Rules:**

1. **Name business concepts, not implementation.**
   - ✅ "Sales Order", "delivery transfer", "approval gate", "vendor bill"
   - ❌ "sale.order", "stock.picking outgoing", "Studio approval rule", "account.move type in_invoice"

2. **Name roles, not technical user types.**
   - ✅ "Salesperson", "Warehouse user", "Accountant", "Production Planner"
   - ❌ "user with sales.group_sale", "the session user", "the res.users record"

3. **Describe what the user sees / does, not how the system works.**
   - ✅ "Confirm turns the quotation into a Sales Order; the delivery is generated automatically."
   - ❌ "Click triggers `_compute_state` which sets `state = 'sale'`, then `_create_picking()` runs as a post-save hook."

4. **Active verbs, present tense, concrete subjects.**
   - ✅ "The salesperson confirms the quote." "Stock moves out of the warehouse."
   - ❌ "The quote can be confirmed by the user." "Stock might be moved out in due course."

5. **No skill / catalog / framework vocabulary in reader-facing prose.**
   - ❌ "mock", "screen catalog", "fragment", "view type", "OWL component", `data-mock-*` attributes, "interaction hook", "wired", "registered", "hooked"
   - **Exception:** the cover's "How to interact" callouts and per-workflow overviews must name visible chrome affordances — "walkthrough bar", "Workflow chip", "Annotations toggle", "marker", "variant chip" — because the reader has to learn what they're called to use them. Naming an affordance is allowed; describing it in implementation terms is not.
     - ✅ "Click numbered markers to read what each element does."
     - ❌ "Numbered `mock-marker` elements carry `data-note` attributes that render in a `position:fixed` overlay."

6. **To the point. No filler, no hand-waving, no minimizing.**
   - ❌ "The screens are wired together — use the bar to move forward and back. Get Started takes you in; the rest is just stepping." *(vague + dismissive; teaches nothing)*
   - ✅ "Step through screens using the walkthrough bar at the bottom or the arrow keys. The screens themselves respond to clicks — buttons open modals, tabs switch panels."

7. **Concrete examples beat abstractions.** When teaching a mock mechanic, anchor it in something the reader sees on a specific screen, not a generic statement.
   - ✅ "The Purchase Order screen pivots between RFQ and confirmed PO without leaving the form."
   - ❌ "Screens can render variant states via filter-chip mechanisms."

8. **Screen `data-title` shows the kind of screen, not the specific record.**
   - ✅ `data-title="Purchase Order"`, `data-title="Vendor Bills & Payments"`, `data-title="Quality Check"`
   - ❌ `data-title="Purchase Order P00027"`, `data-title="Vendor Bills & Payments — BILL/2026/06/0042"`, `data-title="Quality Check QC-00088"`
   - The specific record reference (`P00027`, `BILL/2026/06/0042`) belongs **inside the screen's body** as the form's `<h1 class="o_form_title">` text. The `data-title` appears in the walkthrough bar, the dot tooltips, and page-ref chips — all places where a record number is noise, not signal.

9. **`data-workflow-title` ≤ 12 characters — short chip name, not the workflow's full identity.**
   The `data-workflow-title` attribute on a `.mock-workflow` wrapper renders in two space-constrained places: the workflow scope chip's value cell (a custom `buildChip` dropdown in the nav cluster — historically a native `<select>`, now styled to match the variant + annotations chips), and the cross-workflow Next button label on the last screen of a non-final workflow. Both have limited horizontal room. A long name overflows the chip; a tight limit forces a discipline of short, scannable workflow names.
   - **Hard limit: ≤ 12 characters.** Names ≤ 8 chars are ideal; 9-12 acceptable. > 12 is flagged.
   - **Prefer a short single-word business noun** that names the workflow's CONCEPT: `Purchase`, `Sales`, `Inventory`, `Payroll`, `Production`, `Overview`.
   - **Use a business-friendly acronym** when no short single word captures the workflow's scope: `P2P` (Procure-to-Pay), `O2C` (Order-to-Cash), `R2R` (Record-to-Report), `H2R` (Hire-to-Retire), `MtO` (Make-to-Order). Acronyms are 3-5 chars and read as one chunk.
   - **The workflow's "full" descriptive name** can live ANYWHERE the chip's name doesn't reach — the per-workflow overview screen's `mock-cover-title` and `data-title`, the kicker (`Workflow N of M · <name>`), the cover row's narrative text, the body prose. These places aren't space-constrained, so they can carry "Manufacturing" or "Order Fulfillment" or whatever name reads best in context.
   - **Example pairing in a real mock:** the chip says `Production`; the per-workflow overview screen kicker says `Workflow 2 of 3 · Manufacturing`; the cover row narrative says `Manufacturing — define the recipe, plan production, run the orders…`. Reader maps "Production" (chip) ↔ "Manufacturing" (full) by context. Don't fight this — pick the chip name for compactness and the full name for narrative.
   - **Anti-patterns:**
     - ❌ `data-workflow-title="Manufacturing Operations"` (24 chars — overflows the chip)
     - ❌ `data-workflow-title="Order to Cash Flow"` (18 chars — use `O2C` instead)
     - ❌ `data-workflow-title="Workflow 1"` (positional name with no semantic content — reader can't pick from a dropdown of `Workflow 1 / Workflow 2 / Workflow 3`)

**Voice anti-patterns to grep for:**

| Anti-pattern | Replace with |
|---|---|
| `Lorem ipsum`, `TBD`, `TODO` in cover/overview text | concrete business statement |
| "wired together", "hooked up", "the rest is just stepping" | concrete description of what moves between screens |
| Model dotnames in prose (`sale.order`, `stock.picking`, `account.move`) | "Sales Order", "delivery", "vendor bill" |
| Class names in prose (`o_form_view`, `o_kanban_record`) | "form view", "kanban card" (and only when the catalog name is the right teaching term) |
| Decorator / method names (`_compute_*`, `@api.depends`, `_inherit`) | drop entirely; describe outcome, not mechanism |
| Passive multi-clause: "X can be done by the user when Y is also true" | active: "The user does X once Y holds." |
| Apologetic / minimizing closers: "the rest is just stepping", "you'll figure it out" | confident statement of what the reader does next |

`mock-coverage-anchor` flags reader-facing prose that uses skill/catalog
vocabulary outside the chrome-naming exception (rule 5), names technical
models/fields in cover or overview text, or hand-waves with vague
metaphors instead of teaching.

## Input affordances (before-user-input state)

When the screen represents the state **before** the user has acted —
opened wizard, awaiting-input form — render inputs in their pending
state. Prefilling everything hides what the mock is showing: *the user
supplies these values.*

### Visual classes

- **`o_input_pending`** — dashed border, lighter italic placeholder
  text, no value. Use for any input the user hasn't supplied yet. It is a
  MOCK-ONLY cue: real Odoo shows no field border at rest (rule 6), so
  never imitate it with underlines or `o_required_modifier`.
  Placeholder copy hints at the input type (`"Select a lot…"`,
  `"YYYY-MM-DD"`, `"Customer name"`).
- **`o_input_provided`** — solid value, no border. Standard rendering
  for any value already supplied (default, prior input, prefilled).

### Wire pending inputs to their interaction

A pending input that *looks* clickable but does nothing reads as broken.
For every `o_input_pending`, attach the matching `data-mock-*` (per
`interactions.md`):

- **Many2one / autocomplete** → `data-mock-toggle` + a single shared
  `data-mock-toggleable` dropdown panel listing options.
- **Pop-up picker** → `data-mock-modal-open` + the dialog markup.
- **Multi-step navigation** → `data-mock-goto` to the post-state.

If a needed interactive isn't yet supported by the catalog, extend the
catalog (same tokens, recognizable Odoo markup) and propose promotion
in `REFRESH.md`. **Never paint a clickable affordance that does
nothing.** `mock-fidelity-anchor` flags `o_input_pending` without
wiring.

**Pickers share their dropdown panels.** Don't render N parallel
`data-mock-toggleable` panels — one shared panel per axis (e.g.
`lot-picker`, `sn-picker`), referenced by every row's
`data-mock-toggle`. The panel demonstrates the picker shape; per-row
state doesn't need to persist (mock honesty).

## Surface-specific structural rules

These rules are LOAD-BEARING for "recognizably Odoo" fidelity. They come from
the cross-surface drift audit and the calibration against real screens (see
REFRESH.md 2026-06-15 and 2026-10-07 entries). Each surface has a fragment in
`catalog/components/` that demonstrates the correct shape; if a screen needs
something that fragment doesn't show, extend the fragment — don't re-derive.

### Navbar, home menu, control panel, settings, kanban

Their per-fragment rules (structure tables, systray order, title / ⋮ / search /
facets / pager / switcher, optional control-panel states, the settings rail and
card, kanban records / columns / layouts, pivot expanders) live in
`catalog_chrome.md`; rules 2–4 and 11 above are the summary. Copy the fragment
rather than re-deriving.

### Search panel (`search_panel.html`)

- Only where the real action's search view declares a `<searchpanel>` (see
  `view_types.md` § search panel for the composition). Never hand-roll an
  inline flex wrapper or inline panel styles.
- Sections: an icon + UPPERCASE `<b>` header (write natural case). Category =
  select-one: "All" first (`fw-bold`, no counter), exactly one `.active` row (a
  teal-tint pill). Filter (`select=multi`) = checkbox rows. Counters are
  right-aligned 13px, muted unless their row is active.
- Hierarchy: every title is preceded by `.o_toggle_fold`; parents add
  `.o_toggle_fold_with_children` (`#o-caret-right` / `#o-caret-down`); children
  are `li.o_treeEntry` in a nested `ul.list-group`.
- The fold toggle (`#o-left-panel-close`) is always shown; the collapsed state
  is a 31px vertical strip (`#o-left-panel-open` + the current selection).

### Form (`.o_form_view`)

- Layout: `.o_form_view > [.o_content_with_chatter >] .o_form_sheet_bg >
  [.o_form_statusbar, .o_form_sheet]` (+ `aside.o-mail-Chatter`). Never put the
  statusbar directly under `.o_form_view`.
- Sheet: white, 1px `#dee2e6` border, 8px radius, 24px padding, no shadow,
  left-aligned. Title = `h1` 33.6px / 500, black.
- Groups: the `.o_inner_group` label column is as wide as the longest label
  (max 150px); labels 14px / 500. Annotation markers go INSIDE the widget or the
  label, never as a third direct child of `.o_field_row`.
- Group titles: `.o_horizontal_separator` as the first row of an
  `.o_inner_group`, written in natural case (CSS uppercases it: 13px / 700,
  gray-700, hairline below).
- Notebook = boxed Enterprise tabs: inactive gray-100, active white with plum
  text and a 3px plum top bar; the strip bleeds to the sheet edges. An x2many
  list as a page's first content attaches to the tabs, edge to edge. A tab
  holding an invalid field gets `o_page_invalid`.
- Smart buttons render ONLY in the control panel's centre cell: one joined
  group of white bordered 33px buttons, each a 21px plum icon + 12px label over
  a 12px / 500 plum value.
- Ribbon: `<div class="o_widget o_widget_web_ribbon"><div class="ribbon ribbon-top-right"><span class="text-bg-success">Paid</span></div></div>`
  as the first child of `.o_form_sheet` (text renders uppercase; `text-bg-danger`
  for Cancelled / Archived). The legacy empty `data-text` element still renders.
- Custom-field `?`: `<span class="o_field_help" …>?</span>` glued to the label
  text with NO space (it wraps with the last word like Odoo's `<sup>`); a
  plain blue superscript, never `#o-question-circle` / `#o-info-circle`.
- Image header (employee / partner / product): a `d-flex align-items-center
  gap-3` row with the 128px photo left of `.oe_title`. Photos are packaged
  local files; without one, an initials `.o_user_avatar` sized to the photo.
- Alerts (persistent context only — duplicate warning, outstanding credits,
  settings notice): `<div class="alert alert-info|success|warning|danger" role="alert">`
  as a direct child of `.o_form_sheet_bg` between statusbar and sheet. The 3px
  left accent and padding come from CSS — no inline borders, shadows or tints;
  optional `#o-warning` / `#o-info-circle` icon with `.me-1`. A blocked action is
  a dialog, not an alert (§ Guard rendering).
- `form_controller_m3.scss` (Material-3 outlined field boxes) applies below
  768px only — desktop mocks never imitate it.

### List (`.o_list_view`)

- 40px header and rows; the header row is the page-gray gradient with
  regular-weight `#495057` labels; one rule per row. Rows are single-line —
  keep text short or mark long-text cells `td.o_list_text`.
- Cells are plain dark text (rule 10). Reference / number column `td.fw-bold`.
  Row decorations go on the `<tr>` (`text-muted` / `-danger` / `-warning` /
  `-info`, `fw-bold`), column decorations on the `<td>`. Status columns are
  badges (rule 11). Person columns shown with `many2one_avatar*` carry the 24px
  avatar before the name.
- Grouped (`o_list_table_grouped`): white group rows reading `Name  N records`
  (muted count, "1 record"), never `Name (N)`; `#o-caret-right` folded,
  `#o-caret-down` + `o_group_open` open; per-column sums as
  `<span class="fw-bold">` in their numeric column.
- Footer: aggregate values only, under their numeric columns — no "Total"
  label, no top rule.
- Chrome: `th.o_list_actions_header` (`#o-settings-adjust`) with an empty `<td>`
  closing every row; handle `td.o_handle_cell` (`#o-drag`); at most one sorted
  column (`th.table-active` + arrow), unsorted columns show nothing.
- Inline one2many: `.o_field_x2many_list > .o_list_renderer > table` (never
  `.o_list_view` on the wrapper), a trailing `td.o_list_record_remove`
  (`#o-trash`) and a last row `td.o_field_x2many_list_row_add` with btn-link
  "Add a line" (sale order lines: Add Line · Add Section · Add Note · Catalog);
  `o_subtotal_footer` below.
- Without a search panel the list is full-bleed white; beside one it is a white
  card with 12px top corners.

### Chatter (`o-mail-Chatter`)

- Placement: `.o_form_view > .o_content_with_chatter > [.o_form_sheet_bg >
  .o_form_statusbar + .o_form_sheet] + aside.o-mail-Chatter` — a 530px column
  on the page gray, no border, its topbar on the statusbar row; below 1400px it
  stacks under the sheet.
- Two wrappers: `.o-mail-Chatter-top` (sticky topbar + composer when open) +
  `.o-mail-Chatter-content` (planned activities + thread). Render both even on
  minimal chatters.
- Topbar: `.o-mail-Chatter-topbarButtons` = Send message (`btn-primary`), Log
  note and **Activity** (`btn-secondary`; never "Activities"), then
  `.o-mail-Chatter-topbarGrow`, `.o-mail-Chatter-search`,
  `.o-mail-Chatter-attachFiles`, `.o-mail-Followers > .o-mail-Followers-button`
  (`active` + `#o-user` only when the current user follows; else `#o-user-o`).
- Composer: `.o-mail-Chatter-composer[data-mock-toggleable="composer-msg|composer-note"]`,
  toggled by the topbar buttons' matching `data-mock-toggle` (ids may repeat
  across screens). Never hand-add `.active` to the topbar buttons. To show it
  open statically, use `.o-mail-Chatter-composer.is-open` WITHOUT
  `data-mock-toggleable`. Send message = To (recipient tag pills) + Cc [+
  Subject only on Sales Orders / CRM leads] + "Send a message to all followers
  and selected contacts…" + Send; Log note = `.o-mail-Composer-note`, "Log an
  internal note…", "Log".
- Planned activities: assignee avatar + state badge holding the type icon; due
  label colored by state ("Due in N days:" / "Today:" / "N days overdue:");
  summary or type name in bold ("To-Do"); "for <user>"; info icon. Tools are
  ✓ Done and ✎ Edit only — no "Mark Done", no "Cancel".
- Thread: `.o-mail-Thread`, each day opened by `.o-mail-DateSection` ("Today",
  "Oct 5, 2026"), no separator lines. Message =
  `.o-mail-Message > .o-mail-Message-core > .o-mail-Message-sidebar + <div>`
  (header + contentContainer). Log notes, notifications and tracking are a
  plain `.o-mail-Message-body.o-note` (no tint); messages posted with Send
  message are bubbles (`.o-mail-Message-bubble.o-blue` others / `.o-green` you).
- Tracking: one line per change in `.o-mail-Message-body.o-note.o_track` —
  `Old → <b>New</b> <i>(Field)</i>`, several joined by `<br>`. Never a `<ul>`,
  strike-through or "Field:" prefix. OdooBot = `o_avatar_odoobot` (no text).

### Wizards / Dialogs (`.o_dialog`)

- Pick a shape consistently across a package — don't mix:
  - **Simplified catalog shape** (default):
    `.o_dialog_backdrop > .o_dialog > .o_dialog_header / _body / _footer`
  - **Real Odoo shape** (for dev-facing mocks):
    `<div class="o_dialog"><div class="modal d-block"><div class="modal-dialog modal-dialog-centered modal-{size}"><div class="modal-content"><header class="modal-header"><main class="modal-body"><footer class="modal-footer">…`
  Both render identically. Copy `components/dialog.html`.
- **Size decides the design.** `.modal-sm` (460px) and `.modal-md` (620px) are
  MINIMAL (no header / footer rules, 24px padding); no size class (= lg, 980px)
  and `.modal-xl` (1140px) are DEFAULT (ruled header and footer). Confirmation
  prompts, alerts and every error dialog → `modal-sm`; act_window wizards, form
  dialogs and the "Search more…" picker → no class; `modal-md` only for
  `dialog_size='medium'`, the command palette and POS popups; `modal-xl` only
  for `dialog_size='extra-large'`. A prompt without `modal-sm` renders as a
  980px ruled wizard.
- Title = `<h4 class="modal-title">`; every dialog carries
  `<button class="btn-close" type="button" title="Close" aria-label="Close" data-mock-modal-close></button>`
  — never a "×" glyph or `#o-times` svg.
- **Footer: LEFT-aligned, PRIMARY first, then `btn btn-secondary`** (Discard /
  Cancel / "No, keep it"). Never right-aligned, never reversed, never
  `o_btn_outline`.
- Error titles come from the exception: UserError → **Invalid Operation**,
  ValidationError → Validation Error, AccessError → Access Error, MissingError
  → Missing Record, other warnings → Odoo Warning. Never "User Error", never a
  red or yellow header bar.
- Canonical copy: Archive = "Confirmation" / "Are you sure that you want to
  archive this record?" / [Archive][Discard]; generic = [Ok][Discard]; Delete =
  "Bye-bye, record!" / "Are you sure you want to delete this record?" /
  `btn-danger` [Delete] + [No, keep it].
- Backdrop = 25% black + grayscale(50%) — the page behind stays readable; never
  darken or blur it further.

### Dropdowns, autocomplete, toasts, tooltips

- Every dropdown (⋮ actions, Print ▸, selection Print / ⚙ Actions, navbar
  sections, New ▾, search menu) is `.o-dropdown--menu.dropdown-menu` with
  `.dropdown-item` / `.dropdown-divider` / `.dropdown-header`, placed in a
  `.mock-anchor` next to its toggle and wired with `data-mock-toggle` /
  `data-mock-toggleable`. Never hand-roll a menu.
- Many2one dropdown: a light gray-100 menu under the input; the highlighted
  row is light gray with black text (never a purple fill); the typed term is
  purple bold; `Create "x"` / "Create and edit..." / "Search more..." are teal,
  with no separator line.
- Toast (`o_notification`): white card, 8px colored left bar, 1px border, 14px
  text, × close, top-right below the navbar; one short Odoo-voice sentence
  ("Quotation confirmed."), optional teal bold action ("Undo").
- Tooltips are black pills (13px light text, small arrow). Custom-field help
  shows the debug layout: a help line, then a monospace Label / Field / Model /
  Type list.
- Command palette: `modal-md`, search icon on the RIGHT of the input, text-only
  rows with CONTROL + key `kbd` chips, `<hr>` between groups, footer "TIP —
  search for /menus and @conversations".
- Tour pointer: a plum teardrop pointing at the target (direction class on
  `.o_tour_pointer_tip`) + a white popover with "Stop Tour". No step numbers —
  number with `.mock-marker`.

### Reporting views

- Toolbars sit between the control panel and the view body (flex row, 4px
  gap) and use the GLOBAL `.btn` — never shrink or recolor per view; join
  related buttons in `.btn-group`. Measures is always `btn-primary` (the graph
  shows the measure's name; pivot / cohort read "Measures"). Enterprise pivot /
  graph add a `btn-secondary` "Spreadsheet" right after it.
- Scale pickers are `.btn-group.o_view_scale_selector > .btn.btn-secondary.dropdown-toggle`
  (never a pill span); prev / next is a joined `btn-group`.
- Pivot expanders: `catalog_chrome.md` § Pivot expand affordances — never
  literal `[+]` / `[−]` or bordered squares.
- Graph: one group-by = one color, no legend; 2+ = `--o-graph-1..6` with a
  bottom-centred legend (keep ≤ 6 series); horizontal gridlines only. Mode and
  sort are `.btn-group.o_switcher` groups; Stacked / Cumulative are
  `form-switch` toggles.
- Calendar / gantt / map frames are white with rounded top corners on the
  gray. Events and gantt pills are pastel with DARK text
  (`o_calendar_color_N`, `o_gantt_color_N`) — never solid purple with white
  text; the calendar's today is marked only by the red day circle.
- Cohort heat map is TEAL (white text only above 50%). Activity matrix
  (`activity_matrix.html`): 50% tinted summary cells with dark text. Timesheet
  grid: borderless with gutters, "2h 30m", zero as "0h" at 25%. Map: pin list on
  the RIGHT, teal un-numbered pins, a "Maps" `btn-secondary` in the control
  panel. Hierarchy: color-band cards with a "▸ N people" `btn-secondary`.
  Dashboards: `dashboard_sidebar.html` (search-panel nav, white figures, no tab
  switcher).

### Account Reports (`.account_report`)

- The report is a client action with its OWN standard control panel:
  `div.o_action.account_report > .o_control_panel + .o_content > div`. Never a
  separate filter toolbar or chip row, never a PDF + XLSX pair — Print is the
  first (`btn-primary`) bar button, other always-shown buttons follow as
  `btn-secondary`, XLSX lives in the report's cog menu.
- Title (16.8px regular) + the report's own cog (`#o-cog`) in
  `.o_control_panel_breadcrumbs_actions` — the one screen where a cog sits next
  to the title; no ⋮.
- Filters: `div#filter_<name> > button.btn.btn-secondary.o-dropdown.dropdown-toggle`
  (no caret) in `.o_control_panel_actions`; icons date `#o-calendar-fill`,
  options `#o-settings-adjust`, variant / journals `#o-book`, budget
  `#o-bar-chart`.
- Warnings: `#warnings.warnings > .alert.alert-info.alert-dismissible.fade.show.text-center`
  with an empty `.btn-close`.
- Table: a centred white card — `table.table.table-borderless.table-hover`
  (+ `.striped` when several value columns) inside
  `.o_account_report_scroll_container > .o_account_report_scroll_content`;
  `thead#table_header.sticky` keeps the empty `tr[data-id=column_companies_row]`;
  period header boxes only with a comparison or several periods.
- Rows: `tr.line_level_N` (+ `.unfolded` / `.total` / `.fw-bold`), with an
  empty `<tr class="empty"></tr>` before every `line_level_0`. `line_level_0` =
  gray band, bold; a childless level-0 line is the grand total; computed
  sub-results are `line_level_1.fw-bold`. No `tfoot`, no `.wrapper` / `.content`
  divs.
- Cells: `td.line_name.text[.unfoldable]` starting with
  `i.btn.btn_foldable` (`#o-caret-right` / `#o-caret-down`); amounts
  `td.line_cell.numeric.auditable > a`, `.muted` for zero, `.text-danger` for
  negatives. Never literal `[+]` / `[−]` / ▾.
- Never write `o_account_reports_page` or `o_account_report_toolbar / _title /
  _filters / _banner / _card / _period / _line*`, `o_report_filter`,
  `o_report_pdf` — the real `o_account_report_*` classes are only
  `_scroll_container`, `_scroll_content` and `_chatter*`.

### Empty state & first-run (`no_content.html`, `onboarding.html`)

- `.o_view_nocontent` is an OVERLAY centred over the whole view body — never in
  the flow between control panel and view. Place it as the first child of
  `.o_list_view` (the list header stays), after the last group in a grouped
  `.o_kanban_renderer`, in `main.o_content` for pivot / graph, as the last
  child of `.o_grid_view` for grid.
- Copy: the first `<p>` is the title (bold, 20px) carrying the illustration
  class + `<svg class="o_nocontent_img">` — `#o-nocontent-smiling-face` (model
  helpers), `-neutral-face` ("nothing matches"), `-empty-folder` (default
  helper only); later `<p>`s are the 16px hint. Use the model's real help text;
  no CTA button unless the real helper has one (New is the CTA).
- A list whose action has no help shows its header + 4 blank rows and no
  helper; the default "No data to display" helper is for kanban / pivot / graph
  / grid / cohort. Empty grouped-kanban columns keep their headers
  (`o_kanban_no_records`, faded counter).
- Sample data (`sample="1"` views): add `o_view_sample_data` to the view body
  and render believable records — the CSS fades them under the helper.
- There is no horizontal onboarding banner. First-run guidance is the
  empty-state helper, or the in-card Accounting checklist (`onboarding.html`)
  inside its dashboard card. Never mock a strip of setup-step cards above a
  view.

### Discuss, Spreadsheet, Studio

Anatomy in `view_types.md` § App surfaces; the never-rules:

- **Discuss** — no mailbox sidebar (no Inbox / Starred / History rows, no
  CHANNELS / DIRECT MESSAGES headings, no colored DM dots); header actions are
  white boxed `btn-secondary` buttons, no cog, never "# name · N members";
  bubbles are blue (others) / green (you), both left-aligned; "Today" in
  sentence case; the composer is a pill with GIF / emoji / send icons — no
  "Send" text button, no microphone. Discuss CSS for shared mail classes stays
  scoped under `.o-mail-DiscussContent`.
- **Spreadsheet** — Enterprise only; a full screen with its own navbar (never
  `navbar.html` above it). No formula-bar row (toolbar + composer share one
  row); only the real toolbar tools (no $, font picker, print, Σ, "Insert
  chart"); Share is plain text, never `btn-primary`; selection is BLUE, not
  plum; `table.o-grid-mock` is a mock-only class kept inside the real
  `.o-grid-container > .o-group-grid > .o-grid > .os-canvas-background` chain;
  editor icons are `svg.o-icon` (18px).
- **Studio** — no control panel; the 300px dark sidebar is on the LEFT;
  palette tiles are WHITE chips with the exact field-type labels (never "New
  Structure", "Separator", "Smart Button"); editor tabs exactly Views · Reports
  · Automations · Actions · Webhooks · Security · Filter Rules; selection = 2px
  plum outline, no pencils or tint; drop hooks only on a "dragging" screen;
  add affordances only "Add button", an `add_box` tab and "Add Picture"; the
  chatter goes BELOW the sheet.

### Portal (`.o_portal`)

- Every portal screen MUST start with `<header class="o_header_standard
  o_portal_navbar">…</header>` inside `.o_portal`, then `<div
  class="o_portal_wrap">` containing the breadcrumb + `.o_portal_doc`
  (two-column grid: main left + sidebar right).
- Sidebar LEADS with `.o_portal_sidebar_amount` (large centered total),
  THEN action buttons (`.o_portal_actions`), THEN `.o_portal_kv` metadata
  rows, THEN `.o_portal_sidebar_note` small print.
- Line tables use `<table class="o_list_table o_list_table_ungrouped">`
  with `<thead><tr><th>` headers. **Don't invent** `o_portal_table` /
  `o_portal_title` — they have no catalog backing.
- Forms inside the portal use the website-form vocabulary
  (`.s_website_form_*`) — NOT backend `.o_field_row` / `.o_form_label`.

### Website Forms (`.s_website_form`)

- Use the **3-level nested Bootstrap grid** so the form reflows on mobile:
    `.s_website_form_field.col-12.mb-3`
      `> .row`
        `> label.col-form-label.col-sm-auto.s_website_form_label[style="width:200px"]`
        `+ .col-sm > input.form-control.s_website_form_input`
  A flat flex layout works on desktop but won't reflow below the `sm`
  breakpoint — labels need to stack above inputs there.
- Inputs ALWAYS carry both classes: `form-control s_website_form_input`
  (or `form-select` for `<select>`).
- Required asterisk is `<span class="s_website_form_mark"> *</span>`
  INSIDE the `<label>`, not a sibling.
- Help text is a **sibling** of `.s_website_form_field`
  (`<p class="s_website_form_help">`), not a child — CSS shifts it under
  the input column.
- Submit row is `.col-12.s_website_form_submit.text-end.s_website_form_no_submit_label`
  with NO nested `.row` — a 200px label spacer div + result message span +
  the submit button.

### POS (`.pos`)

- Topheader uses the **real Odoo class hierarchy**:
  `.pos-topheader > .pos-leftheader (Register/Orders btns +
  .navbar-separator + tabs) + .pos-centerheader (logo when no order open)
  + .pos-rightheader > .status-buttons`.
- Buttons in the topheader are `btn btn-light btn-lg lh-lg` — the
  large, light Bootstrap variant. The catalog also keeps the older
  `.pos-topbar` / `.pos-topbar-tabs` / `.pos-topbar-search` /
  `.pos-topbar-actions` names working as aliases.
- **Do NOT invent** a `.pos-topbar-info`, `.pos-cashier`, `.pos-session`,
  or any "session info" block in the topheader — real Odoo doesn't have
  one. The cashier name is `<CashierName>` (hidden on mobile via `ui.isSmall`),
  not a custom panel.
- Custom POS UI (trade-in panel, lot picker, approval prompt) is a
  **Dialog popup OVER `.pos`** — `.o_dialog_backdrop > .o_dialog.modal-md`
  with the `.btn-close` X and `btn-lg` footer buttons. Body uses
  `.pos-popup-row` (label/value) and `.pos-popup-list`. Never drop backend
  `.o_field_row` / `.o_list_view` form chrome into `.rightpane`.
- Payment screen methods grid uses `.paymentmethods-container >
  .paymentmethods > .paymentmethod` (real Odoo names; the old
  `.pos-payment` / `.pos-paymentmethod` are kept as aliases).

## Sprite catalog (icons.svg + app-icons.svg)

Both sprites are inlined into every mock's `index.html` by `_scaffold_mock.py`
(external `<use href="file.svg#id">` dies on `file://`, see rule 7). Both live
under `reference/catalog/`:

- **icons.svg** — the REAL glyphs of the calibrated version: Material Symbols
  Outlined (weight 400) + `odoo_ui_icons` (`oi_*`), extracted from the backend
  fonts. `viewBox="0 0 960 960" overflow="visible"`, so `<svg class="o_icon">`
  at 1em renders like `<i class="oi">` at the same size. Each symbol's comment
  names its `data-icon`. Exceptions: the spreadsheet ids are the o-spreadsheet
  18×18 SVGs, the `o-studio-field-*` ids approximate Studio's raster sprite, and
  `o-nocontent-*` are multi-color empty-state illustrations (never tint). The
  root is `width="0" height="0" style="position:absolute;…"` — never
  `display:none`, or the illustrations' gradients and masks stop painting.
- **app-icons.svg** — each app's real multi-color artwork
  (`<module>/static/description/icon.svg`). **Never tint**: no
  `style="color:…"` on `.o_app`, settings tabs or the navbar brand. Sizes:
  home tile 50px in a 70px card, navbar brand 26px, settings rail 23px, Ask AI
  18px.

### Size, fill and carets

- Chrome icons render at 1em (14px). `.o_icon_lg` (1.25em = `.oi-lg`: priority
  stars, kanban / list activity, dialog back / expand), `.o_icon_sm` (0.8em =
  `.oi-sm`: activity badges), `.o_icon_fw` (1.2857em = `.oi-fw`); smart-button
  icons 21px; facet icons 13px. Never shrink chrome icons to 8–12px, never
  `.o_icon_xs` in backend chrome.
- Filled vs outline is part of the id: `o-star` filled (priority on, Favorites)
  / `o-star-o` outline (priority off, opacity .25); `o-user` (following) /
  `o-user-o`; a `-fill` suffix marks the filled twin of an outline id
  (`o-calendar-fill`, `o-warning-fill`, `o-trash-fill`, `o-dock-left-fill`).
  `o-cog`, `o-filter`, `o-stacks`, `o-folder`, `o-group`, `o-envelope`,
  `o-phone`, `o-pencil`, `o-info-circle`, `o-times-circle`, `o-add-box`,
  `o-task`, `o-work` are filled; the rest are outline.
- A dropdown caret after a label (New ▾, Generate ▾) is
  `<svg class="o_icon o_caret"><use href="#o-caret-down"/></svg>`. Navbar
  sections, the company name and the search bar carry NO caret.

### Element → sprite id

Reference with `<use href="#o-name"/>` inside a `<svg class="o_icon">`.

| Where | Sprite ids |
|---|---|
| Control panel | actions menu `o-ellipsis-v` (never `o-cog`), collapsed breadcrumb `o-ellipsis-h`, pager `o-chevron-left` / `o-chevron-right`, search `o-search`, facets `o-filter` / `o-stacks` / `o-star` (sort facets `o-arrow-upward` / `o-arrow-downward`) + remove `o-close-small`, date-facet arrows `o-chevron-backward` / `o-chevron-forward`, unsaved form `o-save` + `o-times`, embedded actions `o-settings-adjust` |
| Search menu titles | `o-filter` (text-primary), `o-stacks` (text-action), `o-star` (text-favourite) |
| Search panel | categories `o-folder`, filters `o-filter` (a view's `icon=` overrides, e.g. `o-business`, `o-group`), fold `o-left-panel-close` / `o-left-panel-open`, tree `o-caret-right` / `o-caret-down` |
| View switcher | `o-view-list`, `o-view-kanban`, `o-view-calendar`, `o-view-pivot`, `o-view-graph`, `o-view-map`, `o-view-activity`, `o-view-gantt`, `o-view-cohort`, `o-view-hierarchy`, `o-view-grid` |
| Navbar systray | timer `o-play-circle` (Attendances only: `o-circle`), Ask AI `o-app-ai` (app-icons.svg), Messages `o-forum`, Activities `o-clock`, Studio `o-studio` |
| ⋮ actions menu | `o-print`, `o-settings-applications` (Edit Properties), `o-content-copy` (Duplicate), `o-archive` / `o-unarchive`, `o-trash` |
| List | optional columns `o-settings-adjust`, handle `o-drag`, row delete `o-trash`, sortable `o-sort` (hover only), sorted `o-arrow-upward` / `o-arrow-downward`, group fold `o-caret-right` / `o-caret-down` |
| Kanban | quick add `o-add-2`, column config `o-cog`, card menu `o-ellipsis-v`, add column `o-double-arrow-right`, unfold `o-caret-left` + `o-caret-right`, quick-create discard `o-trash-fill`; activity `o-clock` (none) or `o-phone` / `o-envelope` / `o-check` / `o-calendar-fill` / `o-upload` / `o-warning-fill` / `o-checklist`; meta lines `o-calendar-clock`, `o-timer`, `o-task`, `o-work`, `o-user` |
| Form / smart buttons | Delivery `o-truck`, Invoices `o-edit-square`, Payments `o-payments`, Payslips `o-attach-money`, Time Off / Timesheets `o-view-calendar`, people `o-group-o`, products `o-package`, generic `o-bars`; alerts `o-warning` / `o-info-circle` |
| Chatter | `o-search`, `o-paperclip`, `o-user` / `o-user-o`; composer `o-emoji`, `o-article`, `o-paperclip`, `o-expand`; activities `o-check` (Done), `o-pencil` (Edit), `o-info-circle` |
| Pivot / graph | `o-flip-axis`, `o-expand-all`, `o-download`, headers `o-add-box` / `o-minus-box`; modes `o-view-graph` / `o-chart-line` / `o-chart-pie`, sort `o-sort-desc` / `o-sort-asc` |
| Calendar / gantt / grid / map | calendar `o-arrow-left` / `o-arrow-right`, mini month `o-chevron-backward` / `o-chevron-forward`, side panel `o-dock-left` / `o-dock-left-fill`; gantt / grid `o-west` / `o-east`, grid add `o-add-circle`, gantt sparse `o-expand`; map `o-my-location`, `o-explore` |
| Settings | action links `o-east`, doc links `o-question-circle`, company-specific `o-business` |
| Account report | cog `o-cog`, filters `o-calendar-fill` / `o-settings-adjust` / `o-book` / `o-bar-chart` / `o-folder-open` / `o-description` / `o-user`, fold `o-caret-right` / `o-caret-down`, journal-item menu `o-ellipsis-v`, sortable `o-sort` |
| Discuss | `o-hashtag` (Channels — not `o-tag`), `o-videocam`, `o-group`, `o-add-circle`, `o-gif-box`, `o-emoji`, `o-paper-plane`, `o-push-pin`, `o-reply`, `o-travel`, `o-user-plus`, `o-bell`, `o-phone` |
| Spreadsheet (`svg.o-icon`, 18px) | `o-undo`, `o-redo`, `o-paint-brush`, `o-clear-format`, `o-number-formats`, `o-bold`, `o-italic`, `o-strikethrough`, `o-text-color`, `o-fill-bucket`, `o-borders`, `o-merge-cells`, `o-align-left`, `o-align-bottom`, `o-wrap-overflow`, `o-wrap-text`, `o-rotate-text`, `o-table-paint`, `o-filter`, `o-fx`, `o-sheet-add`, `o-sheet-list`, `o-column-stats`, `o-global-filters`, `o-family-history` |
| Studio | `o-tv`, `o-dns`, `o-ms-undo`, `o-ms-redo`, `o-contact-mail`, `o-view-list-alt`, `o-area-chart`, `o-studio-field-*` |
| Empty state | `o-nocontent-smiling-face`, `o-nocontent-neutral-face`, `o-nocontent-empty-folder` |
| Other | `o-plus`, `o-times`, `o-check-circle`, `o-circle`, `o-lock`, `o-key`, `o-cloud-upload`, `o-external-link`, `o-launch`, `o-refresh`, `o-tag`, `o-cart`, `o-heart`, `o-eye` / `o-eye-slash`, `o-link`, `o-question-circle`, `o-microphone`, `o-comment`, `o-spinner`, `o-odoo-logo` (mock cover only) |

Legacy ids that still resolve but have no place in current chrome: `o-chart-stack`
(Stacked is a switch), `o-exchange`, `o-list`, `o-th-large`, `o-sigma`.

### App icons (app-icons.svg)

Available `o-app-*` ids and tile order: `catalog_chrome.md` § Home menu.
`o-app-hr` = Employees, `o-app-settings` also serves the General Settings tab,
`o-app-ai` is the systray Ask AI mark, and `o-app-fsm` / `o-app-studio` exist
but are not home tiles.

### Adding a glyph

1. Find the `data-icon` name the real template uses, and grep the icons.svg
   comments for it — if a symbol exists, use its id (never add an alias id).
2. Extract the real outline:
   `python reference/scripts/_extract_icons.py <name>[=o-id] [--filled]`
   (`--list` lists names; needs `fonttools` + `brotli`). The name must exist in
   the version's Material Symbols set (`web/icons.py`) or be an `oi_*` glyph.
   Paste the printed `<symbol>` before the sprite's FINAL `</svg>`, keeping
   `viewBox="0 0 960 960" overflow="visible"` and a comment naming the
   `data-icon` and where Odoo uses it.
3. New app: copy `<module>/static/description/icon.svg` into
   `<symbol id="o-app-<name>" viewBox="0 0 50 50">` in `app-icons.svg`,
   renaming any internal id.
4. If the glyph has a fixed use, add it to the Element → sprite id table above.
   A `<use href="#o-…">` with no matching `<symbol>` renders blank — re-render
   the gallery (`_render_catalog.py`) to check.

## Source map (for `REFRESH.md` / version bumps)

The calibrated version's source lives under `versions/v<NN>/odoo/addons/`
(Community) and `versions/v<NN>/enterprise/` (Enterprise). Below, `web/…` =
`odoo/addons/web/static/src/…`, `web_enterprise/…` =
`enterprise/web_enterprise/static/src/…`, `../<addon>/…` = another addon under
`odoo/addons/`, and `enterprise/<addon>/…` = an Enterprise addon. The
Enterprise overrides mirror web's paths and carry most of the visual design —
**read both for every component**, and confirm with a live probe
(`REFRESH.md` § How to refresh).

- Tokens → `web/scss/{primary,secondary}_variables.scss`;
  `web_enterprise/scss/{primary_variables,secondary_variables,bootstrap_overridden}.scss`
- Buttons, badges, tags, dropdowns, notebook, switcher →
  `web_enterprise/core/{btn,badge,tags_list,dropdown,notebook,switcher}/` (+ `web/core/…`)
- Navbar / home menu → `web/webclient/navbar/navbar.{scss,xml}`;
  `web_enterprise/webclient/navbar/navbar.{variables.scss,scss}`,
  `web_enterprise/webclient/home_menu/`
- Control panel / search → `web/search/{control_panel,search_bar,breadcrumbs}/`,
  `web/core/pager/`; `web_enterprise/search/control_panel/control_panel.scss`
- Search panel → `web/search/search_panel/`;
  `web_enterprise/search/search_panel/search_panel.scss`
- Form → `web/views/form/` (`form_controller.scss`; `form_controller_m3.scss` =
  mobile only; `button_box/`), `web/views/fields/statusbar/`,
  `web/views/widgets/ribbon/`; `web_enterprise/views/form/form_controller.scss`,
  `web_enterprise/views/fields/statusbar/`, `web_enterprise/views/widgets/ribbon/`
- List → `web/views/list/list_renderer.{scss,xml}`;
  `web_enterprise/views/list/list_renderer.scss`
- Kanban / card shell → `web/views/kanban/`, `web/views/card/card.scss`;
  `web_enterprise/views/kanban/{kanban_controller.scss,kanban_header.xml,kanban_header.scss}`,
  `web_enterprise/views/card/card.scss`
- Reporting views → `web/views/{pivot,graph,calendar}/`,
  `web_enterprise/views/{pivot,graph,calendar,gantt}/`; Enterprise `web_gantt`,
  `web_grid` / `timesheet_grid`, `web_cohort`, `web_map`; Community
  `web_hierarchy`, `spreadsheet_dashboard`
- Settings → `web/webclient/settings_form_view/`;
  `web_enterprise/webclient/settings_form_view/settings_form_view.scss`
- Empty state → `web/views/action_helper.xml`, `web/views/view.scss`
- Dialog / errors → `web/core/dialog/dialog.{xml,scss}`,
  `web/core/confirmation_dialog/`, `web/core/errors/error_dialogs.xml`
- Notification, autocomplete, tooltip, command palette →
  `web/core/{notifications,autocomplete,tooltip,commands}/`; tour pointer →
  `../web_tour/static/src/tour_pointer/`
- Chatter → `../mail/static/src/chatter/web/chatter.xml`,
  `../mail/static/src/core/common/{message,composer,date_section}.xml`,
  `../mail/static/src/core/web/activity.xml`
- Discuss → `../mail/static/src/core/public_web/` (`discuss_app/`,
  `discuss_content.*`, `messaging_menu/`, `notification_item.*`)
- Account Report → `enterprise/account_reports/static/src/components/account_report/`
  (`account_report.{xml,scss}`, `header/`, `line/`, `filters/`, `cog_menu/`)
- Onboarding checklist → `../account/static/src/components/onboarding/`
- Spreadsheet → `../spreadsheet/static/src/o_spreadsheet/`; Enterprise
  `spreadsheet_edition`, `documents_spreadsheet`, `spreadsheet_dashboard_edition`
- Studio → `enterprise/web_studio/static/src/client_action/`
- Portal → `../portal/views/portal_templates.xml`,
  `../portal/static/src/scss/portal.scss`
- Website Form → `../website/views/snippets/s_website_form.xml`,
  `../website/static/src/snippets/s_website_form/000.scss`
- POS → `../point_of_sale/static/src/app/components/navbar/navbar.{xml,scss}`,
  `../point_of_sale/static/src/app/components/orderline/orderline.{xml,scss}`,
  `../point_of_sale/static/src/app/screens/product_screen/`,
  `../point_of_sale/static/src/app/screens/payment_screen/`,
  `../point_of_sale/static/src/app/components/popups/`
- Chrome glyphs (icons.svg) → Material Symbols
  `web/libs/materialsymbols/material_symbols_backend.woff` (names + codepoints
  in `odoo/addons/web/icons.py`) and `odoo_ui_icons`
  `odoo/addons/web/static/lib/odoo_ui_icons/fonts/odoo_ui_icons_backend.woff`
  (glyph list in `odoo/addons/web/tooling/icons/odoo_ui_icons_config.json`),
  extracted with `reference/scripts/_extract_icons.py`.
- App icons (app-icons.svg) → each module's `static/description/icon.svg`.
- Calibration kit → `reference/scripts/calibrate/` (`screens.json`,
  `capture.js`, `probe.js`, `render.js`) + one page per real screen in
  `reference/calibration/screens/<name>.html`.

Class names in the fragments are the real Odoo class names so a developer
reading the mock recognises them; mock-only helpers are named as such in each
fragment's header.
