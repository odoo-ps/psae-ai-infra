# Interactive elements — the `data-mock-*` API (walkthrough.js v2)

`walkthrough.js` wires a small, dependency-free interaction layer so a mock
behaves like a clickable prototype, not a slideshow. **It never fakes a working
app** — no computation, validation, or persistence. These hooks reveal/switch
UI and feed back; they don't "save". Keep that line (see the honesty rule in the
skill's framing).

All hooks are plain HTML attributes; no JS authoring per mock.

## Navigation (v1, still current)
- `data-mock-goto="SCREEN_ID"` — go to that `.mock-screen`.
- `data-mock-next` / `data-mock-prev` — step the walkthrough.
- Arrow keys ←/→ navigate; a `#screen-id` hash opens that screen on load.

## Tabs — switch notebook pages in place
Pair a header with a panel; mark the open pair `active` / `is-active-tab`:
```
<span class="nav-link active" data-mock-tab="lines">Order Lines</span>
<span class="nav-link"        data-mock-tab="other">Other Info</span>
...
<div data-mock-tabpanel="lines" class="is-active-tab"> … </div>
<div data-mock-tabpanel="other"> … </div>
```
Scope is the containing `.o_notebook` (or `.mock-screen`), so multiple screens
can each have their own tab set with the same keys.

## In-place modal — open/close a dialog on the current screen
```
<button data-mock-modal-open="alloc">Allocate Lots</button>
<div class="o_dialog_backdrop" data-mock-modal="alloc">
  … <button data-mock-modal-close data-mock-goto="next">Save</button> …
</div>
```
Hidden until opened; closes on `data-mock-modal-close`, Esc, or a screen change.
`data-mock-modal-close` + `data-mock-goto` on one button = close then navigate.

## Toggle — dropdown / expander reveal
```
<span class="o-autocomplete-input" data-mock-toggle="lotsel">Select a lot…</span>
<div class="o-autocomplete-dropdown" data-mock-toggleable="lotsel"> … </div>
```
Click flips `.is-open`; only one toggle open at a time; Esc / screen change close it.
The id resolves inside the clicked element's screen first, so fragment ids (e.g.
the chatter's `composer-msg` / `composer-note`) may repeat on several screens.
To render a toggleable OPEN statically, add `is-open` and drop
`data-mock-toggleable` (a screen change closes every toggleable) — e.g.
`.o-mail-Chatter-composer.is-open`. Never hand-add `.active` to the chatter's
topbar buttons; CSS derives it from the open composer.

Every Odoo dropdown (⋮ action menu, Print ▸, `New ▾`, navbar section menus, the
search bar menu) is an `.o-dropdown--menu.dropdown-menu` with `.dropdown-item` /
`.dropdown-divider` / `.dropdown-header`, placed in a `.mock-anchor` next to its
toggle and wired with this pair. Never hand-roll a menu.

## Screen variants — multi-axis filter-chip chrome

When the same step has more than one meaningful rendering — different
tracking modes (Lot vs Serial), different state values (Quotation /
Partial-allocated / Confirmed-locked), different actor perspectives
(Sales rep / Manager / Customer portal), different currency modes — do
NOT duplicate the screen per combination. Register the **axes of
variation** on the screen, and the walkthrough bar renders a row of
**filter chips** — one chip per axis, each chip a labelled dropdown of
that axis's values.

Author each axis with three attributes on a `data-mock-variant-axes`
container. The recommended pattern is a single multi-axis declaration
JSON-encoded on the `.mock-screen` itself:

```
<section class="mock-screen" data-screen="quote-lot-line"
         data-title="Quote — lot-tracked line"
         data-desc="Sales Agent adds a tracked product to a quotation"
         data-mock-variant-axes='[
           {"key":"tracking","label":"Tracking","default":"lot",
            "options":[["lot","Lot"],["serial","Serial"]]},
           {"key":"state","label":"State","default":"unallocated",
            "options":[["unallocated","Unallocated"],
                       ["partial","Partial"],
                       ["allocated","Allocated"],
                       ["locked","Confirmed (locked)"]]}
         ]'>

  <!-- Elements that swap on the TRACKING axis -->
  <span data-mock-variant="tracking=lot">Conference Table — Black (lot-tracked)</span>
  <span data-mock-variant="tracking=serial">Laptop M3 Pro (serial-tracked)</span>

  <!-- Elements that swap on the STATE axis -->
  <span data-mock-variant="state=unallocated" class="badge rounded-pill text-bg-danger">Unallocated</span>
  <span data-mock-variant="state=partial" class="badge rounded-pill text-bg-warning">Partial (2 of 3)</span>
  <span data-mock-variant="state=allocated" class="badge rounded-pill text-bg-success">Complete</span>
  <span data-mock-variant="state=locked" class="badge rounded-pill text-bg-success">Complete <svg class="o_icon o_icon_sm"><use href="#o-lock"/></svg></span>

  <!-- Elements that combine multiple axes (only visible when ALL match) -->
  <button class="btn btn-secondary" data-mock-variant="tracking=lot,state=unallocated"
          data-mock-toggle="lot-picker">Select Lots</button>
  <button class="btn btn-secondary" data-mock-variant="tracking=lot,state=locked" disabled>View Lots (locked)</button>

  <!-- Elements without data-mock-variant stay visible across all combinations -->
  <div class="o_form_sheet_bg"> ... shared statusbar + sheet chrome ... </div>
</section>
```

### Attribute reference

- **`data-mock-variant-axes`** on `.mock-screen` — a JSON array of axes,
  each with `key`, `label`, `default`, and `options` (an array of
  `[key, label]` pairs). One axis: the chrome shows one chip. Three
  axes: three chips. Up to 4 axes per screen is reasonable; more →
  reconsider whether the screen is doing too much.
- **`data-mock-variant="<axis>=<value>"`** on any child element — that
  child is visible only when the named axis is set to the named value.
- **`data-mock-variant="<axisA>=<valueA>,<axisB>=<valueB>"`** —
  AND-condition across DIFFERENT axes: the child is visible only when
  EVERY listed axis-value pair matches. Use sparingly; most elements
  should pivot on a single axis.
- **`data-mock-variant="<axis>=<a>|<b>|<c>"`** — same-axis OR (a, b, OR
  c — pipe-separated values). Mirrors real Odoo's view-attrs convention
  (`('state','in',[...])`). Use for statusbar segments that highlight on
  multiple states, or shared chrome that shows across several lifecycle
  phases. Combines with cross-axis AND, e.g.
  `data-mock-variant="state=draft|sent,tracking=lot"`.
- **DO NOT use same-axis comma** (`<axis>=<a>,<axis>=<b>`) — that
  evaluates as `axis==a AND axis==b`, which is always false, so the
  element is permanently HIDDEN. `_lint_mock.py` flags this as
  `KNOWN-BAD`. Use the pipe form instead.
- **Children without `data-mock-variant`** stay visible across all
  combinations — the form chrome, the statusbar, the unchanged half of
  the layout. Tag only the elements that genuinely change.

### When to use which axis

- **`tracking`-style data-driven axes** — lot vs serial, B2C vs B2B,
  invoiced vs not-yet-invoiced. The brief explicitly says "X or Y."
- **`state`** — the workflow's stages **as a variation of the same
  screen**. This is how guard-paths fold in: instead of a "Confirm
  blocked — partial allocation" screen, the `state=partial` value on
  the primary screen renders that block-state inline (the badge says
  Partial, the Confirm button shows the warning toast or the inline
  guard message).
- **`actor`** — Sales rep / Manager / Customer portal renderings, when
  record rules + ACLs change which fields/buttons are visible. Only add
  this axis if the brief names per-actor visibility.

### Anti-patterns

- **Don't model micro-variation as an axis.** "Customer name shown vs
  hidden" isn't worth a chip; collapse it.
- **Don't model > 4 axes per screen.** That's a sign the screen is
  carrying too many concerns — split into 2 screens.
- **Don't require every element to live under some axis.** Most chrome
  is invariant; tag only the variable parts.
- **Don't repeat the same axis across many unrelated screens just
  because it's available.** If the variation doesn't change what's on
  *this* screen, omit the axis here.

### Chrome scales: parallel chips (1–2 axes) vs dependent chip pair (≥ 3 axes)

The walkthrough bar auto-renders different chrome based on how many
axes a screen declares:

- **1 axis** → one chip: `Tracking: [Lot ▾]`
- **2 axes** → two parallel chips: `Tracking: [Lot ▾]  State: [Unallocated ▾]`
- **≥ 3 axes** → **dependent Type + Value chip pair**:
  `Variant: [Tracking ▾]  Value: [Lot ▾]`

The dependent pattern picks one axis to "look at" via the Type chip,
and the Value chip exposes that axis's options. Switching Type doesn't
reset other axes' values — each axis still has a current selection;
the Type chip just decides which one the Value chip controls. This
keeps the chrome compact regardless of axis count.

Why this design: stacking 4 parallel chips makes the bar crowded and
forces the reviewer to scan a row of labels. The Type/Value pair holds
one mental concept at a time ("right now I'm pivoting the State"),
which matches how a reader walks the variants — one axis change per
click.

When authoring screens, you don't choose the chrome shape — declare
your axes in `data-mock-variant-axes`, and the chrome picks
automatically based on count. A screen can opt into the dependent
pattern explicitly by adding `data-mock-variant-mode="dependent"` if
the author wants the compact chrome even at 2 axes.

### Why this replaces the old segmented-pill chrome

The previous single-axis pill design (one segmented control per screen)
couldn't carry > 1 axis at a time, so the workflow had to spawn N
screens for the cross-product. The chip-row lets one screen carry
multiple independent axes, dramatically reducing the screen count
while keeping the brief's variation visible.

### Why guard-paths-as-screens are gone by default

State-axis variants absorb most guard paths: the `state=partial` value
renders the partial-allocation guard *on the same screen* as the happy
state. A guard earns its own screen only when:

- The guard surfaces a brand-new piece of chrome (a redirect to a
  different model's view), OR
- The brief explicitly walks through the guard as its own narrative
  step (rare).

For everything else, the State axis is the right home.

## Toast — transient action feedback (`o_notification`)
```
<button data-mock-toast="Quotation confirmed."
        data-mock-toast-type="success"   <!-- success|warning|danger|info -->
        data-mock-goto="so-confirmed">Confirm</button>
```
Side-effect attributes (`data-mock-toast`, `data-mock-modal-close`) co-occur with
a `goto` on the same element — they fire, then navigation runs.

## Annotations (numbered markers)
- `.mock-marker[data-note]` — a numbered pin; click toggles its note. The
  **Annotations** chip in the walkthrough bar hides all markers for a clean
  screenshot (it shares its row with the **Custom** chip — § Custom elements).
- The note renders in **one body-level floating layer** (`position:fixed`, top
  z-index), so NO ancestor `overflow` (form sheet, list, notebook) can clip it —
  it's always fully visible. walkthrough.js clamps it to the viewport, flips it
  above the marker when there's no room below, and re-positions it on scroll.

## Multi-workflow packaging — workflow selector chrome

When the input spec contains ≥ 2 workflows, wrap each workflow's screens
in a `mock-workflow` container so the chrome can scope navigation per
workflow and offer a top-level selector:

```
<div class="mock-workflow" data-workflow="quote-to-cash" data-workflow-title="O2C">
  <section class="mock-screen" data-screen="quote-draft" ...> ... </section>
  <section class="mock-screen" data-screen="quote-confirm" ...> ... </section>
  ...
</div>

<div class="mock-workflow" data-workflow="returns" data-workflow-title="Returns">
  <section class="mock-screen" data-screen="rma-create" ...> ... </section>
  ...
</div>
```

- `data-workflow` — kebab slug, unique per package.
- `data-workflow-title` — short human label for the chrome chip. **≤ 12 characters** (chip cell + cross-workflow Next button label are space-constrained — see `style_guide.md` § Workflow titles). Prefer a single business noun (`Purchase`, `Sales`) or a business-friendly acronym (`O2C`, `P2P`).
- Each screen still carries `data-screen`/`data-title`/`data-desc` as
  today; `data-screen` IDs must remain globally unique across workflows.

`walkthrough.js` auto-detects the wrappers:
- ≥ 2 `mock-workflow` → renders a workflow dropdown in the walkthrough bar
  and constrains Next/Prev + the dot row to the **current** workflow's
  screens only.
- Exactly 1 (or zero) → selector chrome stays hidden; behaves as today.

Switching workflows resets the step counter, jumps to the new workflow's
first screen, and updates the URL fragment to `#<screen-id>` (so deep
links still work).

## Cross-screen variant mutation — `data-mock-set-variant`

A click on an in-screen action (Save in the picker, Confirm on the
quote, Validate on the delivery) must be able to **advance the
workflow's state on the target screen**, not just navigate to it. The
default `data-mock-goto` only changes which screen is active; without
state mutation, the target screen stays at whatever variant value it
was last left at (`unallocated` even though the user just saved a full
allocation).

Use `data-mock-set-variant` to flip a target screen's variant value
BEFORE navigating to it:

```html
<!-- Picker → Save: advance the quote to state=allocated, then navigate -->
<button class="btn btn-primary"
        data-mock-set-variant="quote:state=allocated"
        data-mock-goto="quote">Save</button>

<!-- Quote → Confirm (at state=allocated): advance to locked, navigate to delivery -->
<button class="btn btn-primary"
        data-mock-variant="state=allocated"
        data-mock-set-variant="quote:state=locked"
        data-mock-goto="delivery">Confirm</button>
```

### Attribute syntax

- **`data-mock-set-variant="<screen-id>:<axis>=<value>"`** — single mutation.
- **`data-mock-set-variant="A:axis=val;B:other=val2"`** — multiple
  mutations separated by `;`. All apply before any subsequent navigation.

### Combines with

- `data-mock-goto` — runs `set-variant` first, then navigates.
- `data-mock-toast` — toast still fires; the set-variant also applies.
- `data-mock-modal-close` — close fires, then set-variant.

### Anti-pattern: leaving navigation without state mutation

A "Save" button that opens the picker but only does
`data-mock-goto="quote"` forces the reviewer to manually pivot the
State chip on the chrome to see the post-save state. That's the
broken-interactive-path failure mode. Every action that *changes
state* on a downstream screen needs a `data-mock-set-variant` for
that screen's State (or other relevant axis).

The chip-row chrome stays available for the reviewer to walk
edge-state variants directly (partial, lot-unavailable, etc.); the
interactive path covers the happy + main alternates.

## UserError / ValidationError dialog — Odoo's blocking-error convention

When a guard rule refuses an action (Confirm with partial allocation,
Validate with shortages, Post with imbalanced journal), real Odoo
shows a **blocking error dialog**: a small (460px) minimal modal — no
coloured header bar — whose title comes from the exception, the rule's
message, the thin X and ONE left-aligned primary **Close**. This is the
standard Odoo blocking convention.

| Exception | Dialog title |
|---|---|
| `UserError` | **Invalid Operation** (never "User Error") |
| `ValidationError` | **Validation Error** |
| `AccessError` / `MissingError` / other warnings | Access Error / Missing Record / Odoo Warning |

The mock uses the `dialog.html` markup with the `o_dialog_user_error`
modifier (`o_dialog_validation_error` for a ValidationError — same
minimal `modal-sm` look). **When it opens depends on what the variant
value means** (single source of truth for this rule):

- **Setup value** — the precondition for a refusal (`state=partial`,
  Block posting, a shared journal entry, a user without rights). The
  screen renders its normal state; the dialog is closed and opens when
  the reader clicks the gated action (`data-mock-modal-open="<id>"` on
  the button). Setup values are often reached by click-through from
  another screen (a list row's `data-mock-set-variant`), and an error
  already open on arrival reads as if the reader did something wrong.
- **Attempt value** — the variant names the action itself ("Change a
  locked timesheet", "Set to Draft", "Delete"). The dialog is open by
  default (`mock-blocking-modal is-open` + the variant), so static
  review sees the refusal without a click.
- **Never** open an error dialog by default on a state the reader lands
  on: an axis default, a value another screen sets by click-through, or
  the value an Ok / Save sets after a successful action (the Canceled
  state a Cancel → Ok produces). `_lint_mock.py` fails this as
  `GUARD-LANDING`.

Modal ids resolve document-wide (`data-mock-modal-open` takes the first
match in the page), so every dialog id must be unique across the package.

```html
<!-- Setup value: the gated action opens the guard dialog. -->
<button class="btn btn-primary" data-mock-variant="state=partial"
        data-mock-modal-open="partial-guard">Confirm</button>

<!-- Closed until Confirm is clicked; the X / Close dismiss it.
     (An ATTEMPT value would instead add `mock-blocking-modal is-open` and
     its own data-mock-variant, e.g. data-mock-variant="action=edit".) -->
<div class="o_dialog_backdrop" data-mock-modal="partial-guard">
  <div class="o_dialog o_dialog_user_error">
    <div class="o_dialog_header">
      <h4 class="modal-title">Invalid Operation</h4>
      <button class="btn-close" type="button" title="Close" aria-label="Close" data-mock-modal-close></button>
    </div>
    <div class="o_dialog_body">
      <div role="alert"><p>Line "Conference Table — Black" has 2 of 3 units allocated to lots. Allocate the remaining units before confirming.</p></div>
    </div>
    <div class="o_dialog_footer">
      <button class="btn btn-primary o-default-button" data-mock-modal-close>Close</button>
    </div>
  </div>
</div>
```

The Close button dismisses the modal but does NOT change the State —
the underlying form (with the partial badge, the Select Lots link) is
still visible. The user advances the workflow by clicking the in-screen
affordances (Select Lots → picker → Save with `data-mock-set-variant`).

### Replaces the previous `.mock-guard-banner`

The earlier persistent inline banner approach is retired. Reasons:
- Real Odoo shows blocking errors as modals, not inline alerts. The
  banner read as an invented design convention.
- The modal AND the underlying form are both visible (modal on top),
  so the reviewer still sees the form context — same legibility as a
  banner, but with the right chrome.

`.alert` banners are for persistent context only (a duplicate warning,
outstanding credits), never for a refused action. When extending the
catalog with a new dialog flavor, follow `dialog.html` (size class,
`h4.modal-title`, `btn-close`, left-aligned footer: primary first, then
`btn-secondary`) and update the catalog rather than inventing inline
markup.

## Custom-field help "?" (`.o_field_help`)
Flag **every field the solution adds or modifies** with an Odoo-style help `?`
that reveals its attributes on hover (and click, for touch). "Adds" covers the
full field surface, not just net-new stored primitives:

- **Stored** fields — `Char`, `Date`, `Boolean`, `Selection`, `Integer`,
  `Float`, `Monetary`, …
- **Computed** fields — stored or non-stored, with or without `depends`.
- **Related** fields — `fields.X(related='foo_id.bar')`. The value lives on
  another model, but the *exposure* on this view is the solution's delta and
  earns the `?`.
- **Relational** fields — `Many2one`, `One2many`, `Many2many`, including
  reverse relations and `inverse_name` companions on the related model.
- **Standard fields the solution overrides** — new `compute=` / `default=` /
  `readonly` / `required` / `domain` / `depends=` on an otherwise-standard
  field also count as solution deltas and get a `?`.

A standard field the solution merely *uses unchanged* gets no `?`. The rule
of thumb: if the field's existence, value, or behavior on this screen is
something the addon manifest introduces, mark it; if it would render
identically without the addon, leave it alone.

Carry the attributes as `data-*`, and glue the `?` to the label text — NO
whitespace before it, so it wraps with the last word like Odoo's `<sup>`:
```
<label class="o_form_label">Lot Allocations<span class="o_field_help"
        data-help="Records which lot covers how much of the line."
        data-label="Lot Allocations" data-field="lot_allocation_ids"
        data-model="sale.order.line" data-type="one2many"
        data-readonly="state in ['done','cancel']">?</span></label>
```
It renders as Odoo's small blue superscript `?` (no circle). The tooltip shows
the highlighted help text + a `Label / Field / Model / Type / Readonly` list —
the same shape as Odoo's developer field tooltip. Use it to make the
solution's new fields self-describing for the developer audience. (Standard
fields don't get one — only the deltas.)

**Apply it to EVERY solution-added field — stored, computed, related, or
relational — including those in wizards / editable-list column headers** —
e.g. a Lot Allocations dialog's `Lot / Serial` (Many2one), `Available Qty`
(related, exposed from the lot), `Allocated Qty` (stored) headers each carry
their own `?`, not just the form-level field. Don't stop at the main form,
and don't skip a column because its `data-type` is `many2one` or its value
is fetched via `related=` — both are still solution-added exposures.

## Custom elements (`.mock-custom`)
Mark **everything the solution adds or changes** with `mock-custom`, so a
stakeholder sees at a glance what is custom and what is standard Odoo. This is
as non-negotiable as the "?": the test is the same — if it would render
identically without the addon, it is standard and stays unmarked; otherwise it
is custom. That covers fields (as listed for the "?" above), actions (buttons,
smart buttons, menu entries, dropdown items, search filters and group-bys),
containers (form groups, notebook tabs, settings, wizards) and whole screens.

The class renders two ways, depending on where it sits:

- **On the `.mock-screen`** — the screen is custom from end to end (a view of
  a custom model, a custom report, a new page). It shows a small pink
  **Custom** banner across the top-right corner — partly see-through, so
  the chrome under it still shows — and nothing inside the screen is marked
  again.
- **On an element** — that part of a standard screen is custom. It gets a
  light-pink highlight, laid over the element like a highlighter pen: white or
  see-through elements turn light pink, coloured ones (a primary button, a
  status badge) keep their colour, and text stays legible.

Put the class on the **outermost element that is entirely custom** — never on
one that also holds standard content (that would paint the standard part as
custom), and never on an element inside another custom element:

| Custom thing | Mark |
|---|---|
| Field on a form | its `.o_field_row` |
| Group the solution adds (separator + its fields) | the `.o_inner_group` — not each row |
| List column | its `<th>` and every `<td>` of that column — cells, never the `<tr>` |
| Notebook tab | the tab's `.nav-link` AND its `data-mock-tabpanel` panel |
| Setting | its `.o_setting_box` |
| Status widget in the statusbar | its `.o_field_widget` wrapper (badge + "?") |
| Button, smart button, menu entry, dropdown item, search filter or facet | the element itself |
| Wizard of a custom model over a standard screen | its `.o_dialog` |
| Error the solution raises (its guard's UserError dialog) | the dialog's `.o_dialog_body` — the title and Close are Odoo's |
| Line the solution adds to a standard dialog or confirmation | that line (`<p>` / `<div>`) |
| Notification or chatter note the solution posts | the `.o_notification` / the message's `.o-mail-Message-body` — the author and date are Odoo's |
| Standard button the solution disables or gates in a new state | that button, in that variant |
| Values the solution writes into a standard field on some rows | those cells only — the column header stays standard, with no "?" |
| View of a custom model, custom report, new page | the `.mock-screen` |

```
<section class="mock-screen mock-custom" data-screen="report" …>     ← whole screen
<div class="o_field_row mock-custom"><label class="o_form_label">Lot Allocations<span class="o_field_help" …>?</span></label> …</div>
```

A custom field carries both: the "?" documents the field for developers, the
mark shows its scope. Add `mock-custom` to the element's existing `class`
attribute — a second `class` attribute on the same tag is dropped by the
browser. The cover and workflow overviews are never marked; the cover's Custom
callout uses `mock-custom-example` / `mock-custom-banner-example`, which stay
visible whatever the chip says.

The **Custom** chip (Show / Hide) sits beside **Annotations** in the
walkthrough bar, the two splitting that row like two variant chips; it renders
only when the package marks something custom. Hide adds `mock-custom-off` to
`<body>`. Highlights and the banner never change layout, so toggling them
reflows nothing.

`_lint_mock.py` gates it like the "?": `CUSTOM-UNMARKED` fails any "?" field
outside a custom element or screen, and `CUSTOM-PLACEMENT` fails marks on the
cover / overviews, inside a custom screen, nested, or on a `<tr>` / `<table>` /
void element (the highlight is an overlay `walkthrough.js` places inside the
marked element). Which other elements the solution adds is judged by both
anchors against the spec.

## Motion
- Screens fade in (CSS `mock-screen-in`); respects `prefers-reduced-motion`.

## Weight discipline
All of the above is CSS + the single `walkthrough.js`. No libraries, fonts, or
images — the self-containment lint stays green. Keep added interactions in this
vocabulary; don't reach for a framework.
