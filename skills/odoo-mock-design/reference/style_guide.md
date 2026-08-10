# Odoo mock style guide — tokens, rules, source map

The fidelity bar is **"recognizably Odoo"**: a viewer should glance at a screen
and think "that's Odoo", without us chasing pixel-exact parity. Everything you
need is already in `catalog/odoo.css` as CSS custom properties. **Use the
tokens; never hard-code an off-palette color or font.**

## Design tokens (all in `:root` of `catalog/odoo.css`)

| Token | Value | Use |
|---|---|---|
| `--o-brand-primary` | `#714B67` | Enterprise purple — primary buttons, active states, markers |
| `--o-community-color` | `#71639e` | Community purple (navbar if mocking community) |
| `--o-enterprise-action-color` | `#017e84` | Teal — secondary accent, open marker |
| `--o-gray-100 … --o-gray-900` | `#f8f9fa … #212529` | Backgrounds, borders, muted text |
| `--o-success / warning / danger / info` | `#28a745 / #ffac00 / #dc3545 / #17a2b8` | Status badges |
| `--o-font-family` | system stack | Body text (no web font — keeps packages offline) |
| `--o-headings-font-family` | `"SF Pro Display", …` | Titles |
| `--o-font-size-base` | `0.875rem` (14px) | Base text |
| `--o-spacer` | `16px` | Default padding/margins |
| `--o-border-radius` | `4px` | Default corner radius |
| `--o-statusbar-height` | `33px` | Form statusbar |
| `--o-form-sheet-min-width` | `990px` | Form sheet max width |

## Rules (what makes a mock read as Odoo)

1. **Webclient background is gray-100, sheets/panels are white.** The form sheet
   is a white card centred on a gray background. Don't make the whole page white.
2. **Navbar is WHITE with dark text** in Odoo 19 **Enterprise**
   (`navbar.variables.scss`: `$o-navbar-background: $o-white`,
   `entry-color: $o-main-text-color`, `border-bottom: 0`) — the brand purple
   `#714B67` is an **accent** (buttons / active states), NOT the navbar. Full
   width, ~46px, app name + menus left, systray right. **Community** keeps the
   purple navbar (`#71639e`, white text) — `body.o-community` restores it. Use
   the SAME navbar markup on every screen (apps toggle + sections + systray +
   avatar) so the header doesn't change between steps.
3. **Control panel is white with a bottom border**, holding breadcrumbs (muted →
   bold current) on top and actions + search + pager + switcher below.
4. **Primary action = filled purple `btn btn-primary`.** Secondary/other actions
   = `o_btn_outline` or `btn-secondary`. One primary per cluster.
5. **Form statusbar:** left = workflow buttons, right = arrow-shaped status
   pipeline with exactly one `o_arrow_button_current`.
6. **Form fields are clean text in Odoo 19** — NO persistent dotted underline
   (that's the pre-15 look). Empty fields use `o_field_empty` (gray italic
   em-dash). A required *input* may carry a subtle solid bottom border via
   `o_required_modifier`, but don't put it on a filled value — especially not on
   a link.
7. **Icons come from the sprite, INLINED into `index.html`**, referenced with
   same-document `<use href="#o-id">`. Never link an external sprite
   (`<use href="assets/icons.svg#id">`) — external SVG `<use>` is blocked over
   `file://`, so the icons vanish when the package is opened as a file. Need a
   glyph that isn't there? Add it to `catalog/icons.svg` (the source) and it gets
   inlined. Never `<img>` an external icon or load FontAwesome from a CDN.
8. **No external anything.** No CDN CSS/JS/fonts/images, no `https://` asset, no
   tracking. `_lint_mock.py` enforces this and the lint is a release gate.
9. **Realistic placeholder data, not Lorem ipsum.** Use plausible Odoo-style
   names (Deco Addict, Mitchell Admin, SO0042). The linter rejects `Lorem ipsum`,
   `TODO`, `TBD`.
10. **Relational / URL values are teal links** (`--o-enterprise-action-color`,
    `#017e84`) — Customer, addresses, product names, and editable/linked numeric
    cells in lists. Use `<a class="o_form_link">` on a form and
    `class="o_list_link"` in a list. Plain dark text for non-relational values
    only. This is the single most recognizable Odoo color cue after the navbar.
11. **Statusbar buttons are compact and flat** — only the primary action is
    filled; the rest are flat text with a hover wash. **Inline tags use `o_tag`**
    (gray pill, e.g. a tax `15%`), distinct from a colored status `badge`. For
    sale/purchase/invoice, close the lines with an **`o_subtotal_footer`**
    (right-aligned Untaxed / Tax / **Total**, Total emphasized).
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
    | Inline tinted callout / disclosure | `.alert` (inline banner)         | `.s_website_form_note`                    | `.o_portal_note` + `_info/_success/_warning/_danger` | `.pos-callout` + same tone modifiers |
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

### Guard rendering — action-triggered Validation Error modals

When a State-axis value sets up a guard condition (line is partially
allocated; lot reserved by another transfer; etc.), the **happy state
is the default rendering**. The error modal opens **when the user
clicks the gated action**, not by default at the state.

This matches real Odoo: an Odoo form doesn't auto-open an error modal
when you load it — the modal fires only when you click the action
button (Confirm, Validate, Post, …) that would fail. The State value
shows the SETUP for the failure (the Unallocated badge, the partial-
allocation indicator, etc.); the user clicks the action button to see
the modal.

Use Odoo's standard modal anatomy:

- `.o_dialog.o_dialog_user_error` for **User Error** (no coloured
  header — title says "User Error" / "Validation Error"; matches real
  Odoo `error_dialog.scss` which has `border: none` on the header).
- Modal body carries the rule's message in user-facing Odoo voice
  (imperative + concrete, no spec citations).
- Modal footer has a Close button.

```html
<!-- Default-closed; opens on Confirm click at the guard state -->
<div class="o_dialog_backdrop" data-mock-modal="confirm-blocked"
     data-mock-variant="state=unallocated">
  <div class="o_dialog o_dialog_user_error">
    <div class="o_dialog_header"><span>Validation Error</span></div>
    <div class="o_dialog_body">
      <p>Allocate lots or serials on every tracked line before confirming this quotation.</p>
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
guard-banner element in place of the UserError modal.

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
load-bearing for the workflow.

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
  text, no value. Use for any input the user hasn't supplied yet.
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

These rules are LOAD-BEARING for "recognizably Odoo" fidelity. They were
extracted from a cross-surface drift audit (see REFRESH.md 2026-06-15 entry).
Each surface has a fragment in `catalog/components/` that demonstrates the
correct shape; if a screen needs something that fragment doesn't show,
extend the fragment — don't re-derive.

### Chatter (`o-mail-Chatter`)

- The chatter has THREE structural pieces: `.o-mail-Chatter-top` (sticky
  topbar + composer when open) + `.o-mail-Chatter-content` (scrollable
  thread + activities). Render BOTH wrappers even on minimal chatters —
  that's the recognizable Odoo skeleton.
- Topbar buttons use **real Odoo class names**:
  `.o-mail-Chatter-sendMessage`, `.o-mail-Chatter-logNote`,
  `.o-mail-Chatter-activity`, then `.o-mail-Chatter-topbarGrow` (spacer),
  then `.o-mail-Chatter-search` + `.o-mail-Followers` (followers button
  with icon + `<sup class="o-mail-Followers-counter">N</sup>`).
- **Composer** sits INSIDE `.o-mail-Chatter-top`, BELOW the topbar, **only
  when open**. Default state: `<div class="o-mail-Composer is-collapsed"
  data-mock-toggleable="composer-msg">`. Toggle via the topbar's Send
  message / Log note `data-mock-toggle`.
- **Messages are TWO-COLUMN**: `.o-mail-Message > .o-mail-Message-sidebar
  (48px) + .o-mail-Message-core`. The sidebar carries the avatar (inside
  `.o-mail-Message-avatarContainer` for rounded corners); the core carries
  `.o-mail-Message-header` (author + date + notification icons) +
  `.o-mail-Message-contentContainer > .o-mail-Message-body`.
- Tracking-value changes (Stage: A → B) render as a `<ul class="o_mail_tracking_value">`
  inside the message body, NOT inline text.

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

### Account Reports (`.account_report`)

- Wrap the whole report body in `<div class="account_report">` so the
  CSS variable scope applies. Inside, render `.o_account_reports_page`
  with the toolbar + table.
- The table is `<table class="table table-borderless table-hover">` with
  `<thead class="sticky">` (multi-row: period name on row 1, "Balance" /
  "Debit" / "Credit" on row 2).
- Row state classes are the **real** Odoo names:
  `line_level_0` (top section — gray bg + bold), `line_level_2..16`
  (progressive indent on `.line_name .wrapper`), `total` (bold sum row),
  `empty` (spacer between sections — no border), `unfolded` (parent is
  expanded).
- Cells: `<td class="line_name">` for the name (with
  `<button class="btn_foldable">` carrying a `<use href="#o-caret-down">`
  or `#o-caret-right` icon for fold/unfold), `<td class="line_cell numeric">`
  (or `.line_cell.o_list_number`) for right-aligned values.
- **Don't write** `<span class="o_pivot_expand_btn">[+]</span>` — the lint
  flags literal `[+]` / `[−]` markers. Use real `btn_foldable` with a
  caret icon.

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
  **Dialog popup OVER `.pos`** — use `.o_dialog_backdrop > .o_dialog`
  with `btn-lg` footer buttons. Body uses `.pos-popup-row` (label/value)
  and `.pos-popup-list`. Never drop backend `.o_field_row` /
  `.o_list_view` form chrome into `.rightpane`.
- Payment screen methods grid uses `.paymentmethods-container >
  .paymentmethods > .paymentmethod` (real Odoo names; the old
  `.pos-payment` / `.pos-paymentmethod` are kept as aliases).

### Wizards / Dialogs (`.o_dialog`)

- Pick a shape consistently across a package — don't mix:
  - **Simplified catalog shape** (default):
    `.o_dialog_backdrop > .o_dialog > .o_dialog_header / _body / _footer`
  - **Real Odoo Bootstrap shape** (for dev-facing mocks):
    `<div class="o_dialog"><div class="modal d-block"><div class="modal-dialog modal-dialog-centered modal-{size}"><div class="modal-content"><header class="modal-header"><main class="modal-body"><footer class="modal-footer">…`
  Both render identically.
- Size variants are Bootstrap modifier classes on `.o_dialog` or
  `.modal-dialog`: `.modal-sm` (360px), `.modal-md` (650px — default),
  `.modal-lg` (980px), `.modal-xl` (1140px).
- **Footer button DOM order is PRIMARY first, SECONDARY second**:
    `<button class="btn btn-primary">Save</button>`      ← FIRST
    `<button class="btn o_btn_outline">Discard</button>` ← SECOND
  On desktop the rightmost button reads as "final"; Odoo's
  `justify-content-md-start` arranges them left-to-right so the primary
  ends up rightmost. Do NOT reverse the DOM order.
- User Error / Validation Error dialog: `.o_dialog.o_dialog_user_error`
  modifier — borderless header, larger title, right-aligned footer with
  a single Close button.

## Sprite catalog (icons.svg + app-icons.svg)

Two sprites get inline-pasted into every mock's `index.html` (external
`<use href="file.svg#id">` dies on `file://`, see rule 7). Both live
under `reference/catalog/`:

- **icons.svg** — chrome glyphs (chevrons, cog, search, view-type
  switcher shapes, action affordances). Most are simplified FontAwesome
  4.7/5 paths; a few approximate Odoo's `oi-*` font (view-list,
  view-kanban, etc.) because the catalog can't ship the binary
  woff2/woff. The sprite's own header comment cites the source for each.
- **app-icons.svg** — Odoo app brand glyphs (Sales, CRM, Inventory,
  Helpdesk, …). Each `<symbol>` uses `fill="currentColor"`; the wrapper
  `.o_app` carries an inline `style="color:#xxx"` for the brand tint.
  Brand colors are documented in the sprite's header comment block.

### Available chrome glyphs (icons.svg)

Grouped by what they're for. Reference with `<use href="#o-name"/>`
inside a `<svg class="o_icon">`.

| Category            | Sprite ids                                                                                  |
|---------------------|---------------------------------------------------------------------------------------------|
| Navigation / chrome | `o-bars`, `o-chevron-left`, `o-chevron-right`, `o-caret-down`, `o-caret-right`, `o-arrow-left`, `o-arrow-right`, `o-ellipsis-v`, `o-times`, `o-times-circle`, `o-search`, `o-cog`, `o-bell`, `o-spinner` |
| View switcher       | `o-view-list`, `o-view-kanban`, `o-view-calendar`, `o-view-pivot`, `o-view-graph`, `o-view-map`, `o-view-activity`, `o-view-gantt`, `o-view-cohort`, `o-view-hierarchy`, `o-view-grid` (the older FA-shape `o-list` / `o-th-large` remain only as smart-button placeholders — do NOT use them for the switcher) |
| CRUD affordances    | `o-plus`, `o-pencil`, `o-trash`, `o-save`, `o-archive`, `o-unarchive`, `o-lock`, `o-key`    |
| Communication       | `o-envelope`, `o-paper-plane`, `o-comment`, `o-paperclip`, `o-microphone`, `o-phone`, `o-user`, `o-user-plus`, `o-star` |
| Status / help       | `o-check`, `o-info-circle`, `o-question-circle`, `o-warning`, `o-clock`                     |
| Files / IO          | `o-folder`, `o-download`, `o-cloud-upload`, `o-print`, `o-external-link`, `o-launch`        |
| Reporting toolbar   | `o-exchange` (flip axis), `o-filter`, `o-refresh`, `o-settings-adjust`, `o-tag`, `o-truck`, `o-sigma` (sum), `o-sort`, `o-sort-asc`, `o-sort-desc`, `o-chart-line`, `o-chart-pie`, `o-chart-stack` |
| Visibility          | `o-eye`, `o-eye-slash`                                                                      |
| E-commerce          | `o-cart`, `o-heart`                                                                         |
| Editor / spreadsheet| `o-undo`, `o-redo`, `o-paint-brush`, `o-borders`, `o-merge-cells`, `o-align-left`, `o-wrap-text`, `o-fill-bucket`, `o-link` |
| Brand               | `o-odoo-logo`                                                                               |

### Available app icons (app-icons.svg)

Each app's recommended brand color (apply via `.o_app`'s inline
`style="color:#xxx"`). The sprite header block carries the same table —
this duplicates it here so the style guide stays self-contained.

| App icon              | Brand color | App icon                | Brand color |
|-----------------------|-------------|-------------------------|-------------|
| `o-app-crm`           | `#1aa1cd`   | `o-app-helpdesk`        | `#ec6256`   |
| `o-app-sales`         | `#7c7bad`   | `o-app-mrp`             | `#009ba8`   |
| `o-app-accounting`    | `#f06050`   | `o-app-marketing`       | `#c1547a`   |
| `o-app-inventory`     | `#f4a460`   | `o-app-fsm`             | `#34a297`   |
| `o-app-purchase`      | `#5c8ed7`   | `o-app-subscriptions`   | `#1199b3`   |
| `o-app-project`       | `#27a978`   | `o-app-rental`          | `#ef7032`   |
| `o-app-hr`            | `#1d8348`   | `o-app-maintenance`     | `#5e7896`   |
| `o-app-discuss`       | `#e9b425`   | `o-app-recruitment`     | `#c084a6`   |
| `o-app-website`       | `#714B67`   | `o-app-survey`          | `#4f8d4f`   |
| `o-app-pos`           | `#017e84`   | `o-app-elearning`       | `#c84682`   |
| `o-app-settings`      | `#875a7b`   | `o-app-mass-mailing`    | `#4a6ed0`   |
| `o-app-studio`        | `#4a4a55`   | `o-app-quality`         | `#00a09b`   |
| `o-app-calendar`      | `#9d3c69`   | `o-app-apps`            | `#4a4a55`   |
| `o-app-contacts`      | `#1e74c5`   |                         |             |
| `o-app-documents`     | `#3c8dbc`   |                         |             |
| `o-app-dashboards`    | `#df7c2f`   |                         |             |
| `o-app-timesheets`    | `#287f59`   |                         |             |
| `o-app-fleet`         | `#666`      |                         |             |
| `o-app-sign`          | `#714b67`   |                         |             |

### Adding a new glyph

1. Append a new `<symbol id="o-name" viewBox="0 0 N N"><path d="…"/></symbol>`
   to `icons.svg` (or `app-icons.svg` for app brand icons). Use the FA 5/6
   `0 0 512 512` viewBox where possible — the existing paths assume it
   and the `.o_icon { fill: currentColor }` rule handles tinting.
2. Add a one-line HTML comment above the symbol explaining what it's for
   and citing the upstream (FA glyph name, or `oi-*` font entry).
3. If the glyph is for the view switcher or a place the catalog already
   has guidance, also add a row to the table above so authors find it
   without grepping the SVG.
4. Re-render the catalog (`reference/scripts/_render_catalog.py`) and
   eyeball that the glyph picks up `currentColor` in
   `assets/_gallery.html`.

`_lint_mock.py` enforces that every referenced `#o-…` resolves. New
glyphs land in the inlined sprite automatically (`_scaffold_mock.py`
copies the catalog sprite verbatim into each package); no further wiring
is required.

## Source map (for `REFRESH.md` / version bumps)

The catalog was hand-derived from Odoo 19 at these paths (all under
`odoo/addons/web/static/src/` unless noted):

- Tokens → `scss/primary_variables.scss`, `scss/secondary_variables.scss`
- Navbar → `webclient/navbar/navbar.scss`, `webclient/navbar/navbar.xml`
- Control panel → `search/control_panel/control_panel.{scss,xml}`
- Breadcrumbs → `search/breadcrumbs/breadcrumbs.xml`
- Form → `views/form/form_controller.scss`, `views/form/*.xml`
- List → `views/list/list_renderer.{scss,xml}`
- Kanban → `views/kanban/kanban_controller.scss`, `views/kanban/*.xml`
- Chatter → `../mail/static/src/chatter/web/chatter.xml`,
  `../mail/static/src/core/common/message.xml`,
  `../mail/static/src/core/common/composer.xml`
- Dialog → `core/dialog/dialog.{xml,scss}`,
  `core/errors/error_dialog.scss`
- Notification → `core/notifications/notification.{xml,scss}`,
  `core/notifications/notification.variables.scss`
- Autocomplete → `core/autocomplete/autocomplete.scss`
- Portal → `../portal/views/portal_templates.xml`,
  `../portal/static/src/scss/portal.scss`
- Account Report → `../../../enterprise/account_reports/static/src/
  components/account_report/account_report.{xml,scss}`
- Website Form → `../website/views/snippets/s_website_form.xml`,
  `../website/static/src/snippets/s_website_form/000.scss`
- POS → `../point_of_sale/static/src/app/components/navbar/navbar.{xml,scss}`,
  `../point_of_sale/static/src/app/components/orderline/orderline.{xml,scss}`,
  `../point_of_sale/static/src/app/screens/product_screen/`,
  `../point_of_sale/static/src/app/screens/payment_screen/`,
  `../point_of_sale/static/src/app/components/popups/`
- Chrome glyphs (icons.svg) → FontAwesome 4.7 free paths + selective
  `oi-*` font shapes from `lib/odoo_ui_icons/style.css` (Odoo's UI icon
  font; the catalog ships SVG surrogates because the woff2/woff binary
  can't be inlined). Per-glyph FA/OI source is cited in the symbol's
  HTML comment.
- App icons (app-icons.svg) → simplified FA-style shapes per app, with
  brand colors approximated from each app's
  `static/description/icon.png` (e.g. `odoo/addons/sale/static/description/icon.png`,
  `enterprise/helpdesk/static/description/icon.png`). For pixel-perfect
  fidelity, swap the `<use>` for an `<img class="o_app_icon o_app_icon_image" src="…">`
  and supply the real PNG.

Class names in the fragments are the real Odoo class names so a developer
reading the mock recognises them.
