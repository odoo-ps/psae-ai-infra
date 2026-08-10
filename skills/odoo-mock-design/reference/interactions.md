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
  <span data-mock-variant="state=unallocated" class="badge text-bg-danger">Unallocated</span>
  <span data-mock-variant="state=partial" class="badge text-bg-warning">Partial (2 of 3)</span>
  <span data-mock-variant="state=allocated" class="badge text-bg-success">Complete</span>
  <span data-mock-variant="state=locked" class="badge text-bg-success">Complete <svg class="o_icon o_icon_sm"><use href="#o-lock"/></svg></span>

  <!-- Elements that combine multiple axes (only visible when ALL match) -->
  <button data-mock-variant="tracking=lot,state=unallocated"
          data-mock-toggle="lot-picker">Select Lots</button>
  <button data-mock-variant="tracking=lot,state=locked" disabled>View Lots (locked)</button>

  <!-- Elements without data-mock-variant stay visible across all combinations -->
  <div class="o_form_statusbar"> ... shared chrome ... </div>
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
  walkthrough-bar checkbox hides all markers for a clean screenshot.
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
shows a **UserError dialog** — a Bootstrap-style modal with a
**red header** titled "User Error" (or yellow for "Validation Error"),
the rule's message body, and a Close button. This is the standard
Odoo blocking convention.

The mock follows the same pattern. Use the existing dialog markup
with the `o_dialog_user_error` (red) or `o_dialog_validation_error`
(yellow) modifier class. For a guard State variant, the dialog is
**open by default** (persistent rendering for static review) AND
re-opens when the user clicks the gated action.

```html
<!-- Modal opens by default when state=partial; close button dismisses. -->
<div class="o_dialog_backdrop is-open" data-mock-variant="state=partial">
  <div class="o_dialog o_dialog_user_error">
    <div class="o_dialog_header">
      <span>User Error</span>
      <svg class="o_icon" style="cursor:pointer;" data-mock-modal-close><use href="#o-times"/></svg>
    </div>
    <div class="o_dialog_body">
      <p>Line "Conference Table — Black" has 2 of 3 units allocated to lots. Allocate the remaining units before confirming.</p>
    </div>
    <div class="o_dialog_footer">
      <button class="btn btn-primary" data-mock-modal-close>Close</button>
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

When extending the catalog with a new dialog flavor (e.g. AccessError
modal with a different colour header), follow the same pattern and
update the catalog rather than inventing inline markup.

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

Carry the attributes as `data-*`:
```
<label class="o_form_label">Lot Allocations
  <span class="o_field_help"
        data-help="Records which lot covers how much of the line."
        data-label="Lot Allocations" data-field="lot_allocation_ids"
        data-model="sale.order.line" data-type="one2many"
        data-readonly="state in ['done','cancel']">?</span></label>
```
The tooltip shows the highlighted help text + a `Field / Model / Type / Readonly`
list — the same shape as Odoo's developer field tooltip. Use it to make the
solution's new fields self-describing for the developer audience. (Standard
fields don't get one — only the deltas.)

**Apply it to EVERY solution-added field — stored, computed, related, or
relational — including those in wizards / editable-list column headers** —
e.g. a Lot Allocations dialog's `Lot / Serial` (Many2one), `Available Qty`
(related, exposed from the lot), `Allocated Qty` (stored) headers each carry
their own `?`, not just the form-level field. Don't stop at the main form,
and don't skip a column because its `data-type` is `many2one` or its value
is fetched via `related=` — both are still solution-added exposures.

## Motion
- Screens fade in (CSS `mock-screen-in`); respects `prefers-reduced-motion`.

## Weight discipline
All of the above is CSS + the single `walkthrough.js`. No libraries, fonts, or
images — the self-containment lint stays green. Keep added interactions in this
vocabulary; don't reach for a framework.
