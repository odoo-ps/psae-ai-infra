# Cover discipline — what the cover screen must carry

The cover screen carries the reader's onboarding. Order: chrome explainer
first, workflow narrative second. All reader-facing prose on the cover (and
on per-workflow overview screens, screen `data-title` / `data-desc`, and
annotation `data-note` text) follows the business-voice discipline in
[`style_guide.md`](style_guide.md) § Cover, overview, and meta-content voice
— **business, never technical** — no model dotnames, no class names, no
decorators, no `data-mock-*` vocabulary, no hand-waving filler.

## Required structural elements

### 1. Favicon

`<link rel="icon" href="assets/odoo-icon.svg"/>` in `<head>`. Uses the
icon-style Odoo logo (`odoo-icon.svg`, the circular "O" mark from
`odoo/addons/account/static/src/img/Odoo_logo_O.svg`).

### 2. Brand header

Sticky gradient banner with:
- The icon-style Odoo logo as a small kicker on the top-left
  (`.mock-cover-kicker` with `<img src="assets/odoo-icon.svg"/>` + the
  version label).
- The wordmark `assets/odoo-logo.png` as a watermark on the right
  (`.mock-cover-logo`).

The header uses `position: sticky` so it stays visible while the cover body
scrolls.

### 3. How to interact with this mock

Comes BEFORE the workflow list. Wrap the callout block in
`<div class="mock-cover-section">` (NOT `mock-cover-body` — a name with no
CSS rule that some older mocks used; it breaks the section's grid + spacing).
Each callout uses `<div class="mock-cover-callout">`.

**Canonical wording lives in [`templates/cover_callouts.html`](templates/cover_callouts.html)
— SINGLE SOURCE OF TRUTH.** Five callouts total in fixed reading order
(whole mock → workflows → screen-state pivots → element notes → field
help). Two are always emitted; three are conditional on package structure:

| Callout | Inclusion rule |
|---|---|
| Interactive mock | always |
| Multiple workflows | only when ≥ 2 `.mock-workflow` wrappers exist |
| Variant chips | only when ≥ 1 screen carries `data-mock-variant-axes` |
| Numbered markers | always |
| Field help | only when ≥ 1 screen carries `o_field_help` on a custom-field label |

**Author discipline:**
- Don't paraphrase the canonical wording — copy it verbatim from
  [`templates/cover_callouts.html`](templates/cover_callouts.html).
- Don't reorder; the order is the reading order.
- Don't add a sixth callout for module-specific affordances — those belong
  in a per-workflow overview's actor / narrative copy, not on the main
  cover.
- The **Variant chips** callout's example chip uses a GENERIC placeholder
  (`Axis: Value`) — NEVER a label drawn from the mock's own variant axes
  (no `State: Allocated`, no `Tracking: Lot`). The cover explains the
  chrome universally; citing this mock's specific values reads as a
  duplicated workflow legend.
- The **Numbered markers** callout's example marker uses both
  `mock-marker` AND `mock-marker-example` classes; its `data-note`
  describes what a marker IS, so clicking the cover example demonstrates
  the click behavior.

### 4. Workflow narrative — two-column table

Wrap the numbered list in `.mock-step-list-wrap` and emit TWO column
headers above it: `.mock-step-list-header-workflow` (label **WORKFLOW**)
spans cols 1-2, `.mock-step-list-header-variants` (label **VARIANTS**)
sits in col 3. The CSS draws a single full-height divider between them.

Each `<li>` is a sub-grid row with three cells:

- `.mock-step-num` (the numbered chip)
- the step description (one sentence)
- `.mock-step-axes` (the page-anchored axis chip)

**Axis-chip semantics:**

Render as a **three-cell pill**, with `data-mock-page-ref` on the outer
chip pointing at the host screen's `data-screen` ID:

```html
<span class="mock-step-axes" data-mock-page-ref="quote">
  <span class="mock-step-axes-page-num"><!-- filled by JS --></span>
  <span class="mock-step-axes-page">on Quote</span>
  <span class="mock-step-axes-axis">State
    <span class="mock-step-axes-value">= Confirmed</span>
  </span>
</span>
```

The chip is an `inline-grid` with `max-content` cells and `border-right`
separators between them. Cells are sized to their own content (not to
fixed pixel budgets), so chips with longer screen names or axis values
render cleanly. Cross-row internal alignment is intentionally NOT
preserved — each chip is self-contained.

- **Page-number cell** (`mock-step-axes-page-num`) — leave its inner text
  EMPTY in the markup. `walkthrough.js` resolves the `data-mock-page-ref`
  on the parent at init time and fills the cell with `Page N`, where `N`
  is the index of the referenced screen in the walkthrough order,
  **counting from the first non-cover screen** (so the cover is
  unnumbered; the first workflow screen is `Page 1`). The author NEVER
  hand-writes the number — it can't drift when screens are reordered.
- **Screen-name cell** (`mock-step-axes-page`) — reads
  `on <ScreenTitle>` (natural English). `<ScreenTitle>` matches the host
  screen's `data-title`.
- **Axis cell** (`mock-step-axes-axis`) — the axis name plus an optional
  `<span class="mock-step-axes-value">= Value</span>`.
- **For STATEFUL axes** (axes with a small set of discrete values like
  State, Stage, Status), every chip referencing that axis MUST show a
  value via `.mock-step-axes-value` — step 1 shows the default value
  (e.g. `= Unallocated`), step N shows the pivoted value
  (e.g. `= Confirmed`). Asymmetric chips (one bare "State", one
  "State = Confirmed") read as inconsistent. For NON-stateful axes
  (e.g. Tracking — a per-row property, not a single value at the screen
  level), omit `.mock-step-axes-value`.
- **NEVER write "via Axis on step N"** — cross-step references are
  illegible because the reader has to scroll back to decode them. The
  page-number cell already does the cross-reference job consistently.
- **A row with no axis pivot still emits a third cell** — an empty
  `<span></span>` AFTER the body text. The third cell is what carries
  the column divider (`border-left`); without it the row's subgrid
  collapses to two cells and the divider gaps out for that row.

### 5. Get Started — no standalone button in the cover body

The walkthrough bar's primary Next button is **relabeled by `walkthrough.js`**
based on context (single source of truth: `walkthrough.js::nextButtonLabel`):

- **Single-workflow mode on the cover** → `Get Started`
- **Multi-workflow mode on the main cover** → `Start: <first-workflow-title>`
  (names the destination workflow so the reader knows what they're
  committing to)
- **Per-workflow overview screen** → `Get Started`
- **Last screen of a non-final workflow** → bare `<next-workflow-title>`
  (the chevron icon in the button conveys the forward direction)
- **All other screens** → `Next`

`walkthrough.js` also **hides the Previous button on the cover and the
Next button on the final screen**, so each endpoint shows exactly one
CTA: cover → `[Get Started >]` (or `[Start: <name> >]` multi-workflow),
middle → `[< Previous] [Next >]`, last → `[< Previous]`. The author just
needs to put the label span inside the Next button in
`walkthrough_bar.html`; the JS handles label + visibility.

## Why this order

The reader needs to know HOW to read the mock (interactive surface +
markers + chips) BEFORE they start reading the workflow narrative. The
Get Started button at the bottom closes the onboarding with a clear next
action.

See [`samples/reference_pattern.md`](samples/reference_pattern.md) § Cover
for the worked-example markup.
