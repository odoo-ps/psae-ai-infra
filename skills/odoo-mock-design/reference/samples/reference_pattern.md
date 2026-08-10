# Reference Pattern — Annotated Mock-Package Walk-through

*Calibrated against Odoo 19.0. Re-review on each major version bump.*

The fidelity + density + discipline benchmark for `odoo-mock-design` output. Read this once before invoking the skill to calibrate what *good* looks like — never copy verbatim. The skill **curates**: the smallest faithful mock that carries the brief's story.

The reference package is a 5-screen mock of a Sales-Order lot/serial workflow on Odoo 19 Enterprise. Identifying details stripped; structural anatomy + fidelity cues preserved.

---

## At-a-glance

- **5 primary screens** carrying the workflow story.
- **Variant chip-row** on the Quote screen — `Tracking: [Lot | Serial]   State: [Unallocated | Partial | Allocated | Locked]` — folds 3 guard renderings (Unallocated / Partial / Locked) **into the same screen** as state-axis variants. Without the chip-row those would have been separate screens.
- **6 markers** total, package-wide — one per load-bearing solution element. Not one-per-field.
- **Catalog fragments used verbatim** — `navbar.html`, `control_panel.html`, `form_view.html`, `list_view.html`, `dialog.html`, `chatter.html`. No hand-coded chrome.
- **`mock-coverage-anchor` + `mock-fidelity-anchor` both passed.**

The polish target. A larger mock (multi-actor, multi-workflow) doesn't change the per-screen discipline — it just adds workflow chrome.

---

## Cover discipline — the worked example

The cover screen is the reader's onboarding. **Canonical wrapper class is
`mock-cover-section`** (NOT `mock-cover-body` — that name has no CSS rule;
older mocks shipped it and rendered the section as bare-default block
layout, hit as a `coverage:cover-section-wrapper` blocker).

The cover carries three required structural elements + a strictly-ordered
"How to interact" callout block + a workflow narrative table.

### 1. Brand header
```html
<div class="mock-cover">
  <div class="mock-cover-kicker">
    <img src="assets/odoo-icon.svg" alt=""/> Odoo 19 · Enterprise
  </div>
  <img class="mock-cover-logo" src="assets/odoo-logo.png" alt="Odoo"/>
  <h1>Lot / Serial Selection on Sales Order Lines</h1>
  <p>One-line workflow summary lifted from the brief.</p>
</div>
```
Two image assets are required and must live alongside other catalog
copies in the package's `assets/` folder: `odoo-icon.svg` (the circular
"O" mark) for the kicker + favicon, `odoo-logo.png` (the wordmark) for
the cover watermark. Don't substitute an inline SVG `<use href="#o-odoo-logo"/>`
— a sprite glyph won't carry the brand-quality raster the cover needs.

### 2. "How to interact with this mock" — the canonical FIVE callouts

Wrap the callout block in `<div class="mock-cover-section">`. Each callout
uses `<div class="mock-cover-callout">`.

**Canonical wording lives in [`../templates/cover_callouts.html`](../templates/cover_callouts.html)
— SINGLE SOURCE OF TRUTH.** Don't paraphrase, don't reorder, don't substitute.
The template carries all five callouts with inclusion-rule markers
(`ALWAYS` / `IF multi_workflows` / `IF variant_axes` / `IF field_help`); copy
the bodies verbatim and omit conditional callouts whose trigger doesn't fire.

Reading order (outside-in): whole mock → workflows → screen-state pivots →
element notes → field-label help. The template enforces this order — keep it.

The cover-callout example marker (the inline `i`) is reserved for the cover
only — workflow screens use NUMBERED markers (1, 2, 3 …) restarting per
screen.

### 3. Workflow narrative — three-cell axis chip
A numbered list with one row per primary state the user moves through.
The third cell on each row is the **axis chip** — a three-cell
`inline-grid` pill anchored to its host screen via `data-mock-page-ref`.
`walkthrough.js` resolves the page-ref at init time and fills the
`mock-step-axes-page-num` cell with `Page N`.

```html
<div class="mock-step-list-wrap">
  <div class="mock-step-list-header-workflow">WORKFLOW</div>
  <div class="mock-step-list-header-variants">VARIANTS</div>
  <ol class="mock-step-list">
    <li>
      <span class="mock-step-num">1</span>
      <span>Add a tracked product to a quote</span>
      <span class="mock-step-axes" data-mock-page-ref="quote">
        <span class="mock-step-axes-page-num"></span>
        <span class="mock-step-axes-page">on Quote</span>
        <span class="mock-step-axes-axis">State
          <span class="mock-step-axes-value">= Unallocated</span>
        </span>
      </span>
    </li>
    <li>
      <span class="mock-step-num">2</span>
      <span>Open Select Lots, pick lot/serial × quantity</span>
      <span class="mock-step-axes" data-mock-page-ref="lot-picker">
        <span class="mock-step-axes-page-num"></span>
        <span class="mock-step-axes-page">on Lot Picker</span>
        <span class="mock-step-axes-axis">Tracking</span>
      </span>
    </li>
    <li>
      <span class="mock-step-num">3</span>
      <span>Confirm order (guard refuses partial allocation)</span>
      <span class="mock-step-axes" data-mock-page-ref="quote">
        <span class="mock-step-axes-page-num"></span>
        <span class="mock-step-axes-page">on Quote</span>
        <span class="mock-step-axes-axis">State
          <span class="mock-step-axes-value">= Partial</span>
        </span>
      </span>
    </li>
  </ol>
</div>
```

Key rules (full set in `SKILL.md` § Cover discipline, item 4):

- The page-number cell (`mock-step-axes-page-num`) MUST be empty in
  markup — JS fills it. Authors NEVER hand-write the number.
- For STATEFUL axes (small discrete value set: State, Stage, Status),
  every chip referencing the axis MUST show `.mock-step-axes-value`.
  Non-stateful axes (e.g. Tracking — per-row property) omit the value.
- **NEVER write `via Axis on step N`** as the axis-chip body — that
  pattern was used in earlier drafts and is now anti-pattern. The
  page-number cell does the cross-reference job.
- A row with no axis pivot still emits a third cell — an empty
  `<span></span>` AFTER the body text — so the row's subgrid keeps
  three columns and the column divider doesn't gap out.

---

## Curation — how 10 candidate screens become 5

The brief named 5 workflow states (Quote draft → Allocate lots → Confirm order → Reserve on delivery → Pick) plus 3 guard rules (partial allocation refused; lot unavailable refused; locked after confirm). A naïve enumeration produces 8–10 screens. The chip-row + State axis collapse this:

| Naïve screen | Becomes |
|---|---|
| Quote draft (Unallocated) | Quote screen, `state=unallocated` |
| Quote draft (Partial) | Quote screen, `state=partial` (the guard rendering — "2 of 3 allocated; Confirm refused") |
| Quote draft (Allocated) | Quote screen, `state=allocated` |
| Confirmed SO (Locked) | Quote screen, `state=locked` (Confirm now disabled, ribbon visible) |
| Lot picker pre-input | Dialog screen, `state=empty` |
| Lot picker post-input | Dialog screen, `state=filled` |
| Confirm blocked — lot unavailable | Quote screen, with a toast variant on `state=allocated → Confirm` |
| Edit blocked — locked | Disabled button + tooltip on the Quote screen `state=locked` |
| Delivery | Standalone screen (different model/surface) |
| Pick committed lots | Same Delivery screen, `state=ready` |

Result: **2 primary screens** (Quote, Lot picker) carrying multi-axis variants, **2 supporting screens** (Delivery, Settings), **1 cover**. 5 screens total. Every guard rule is still visible — through the chrome, not extra screens.

A guard earns its own screen only when (a) it redirects to a different model's view, or (b) the brief narrates it as a standalone step. For this brief, neither applies.

---

## Package shape

```
<spec-folder>/mocks/                    ← whenever a spec folder is in the input
                                         path (embedded OR standalone pointed
                                         at a spec). <repo>/mocks/<kebab>/ is
                                         the orphan fallback for bare briefs
                                         with no spec-folder context.
├── index.html                          ← single file; sprite inlined; all screens
└── assets/
    ├── odoo.css                        ← verbatim copy of catalog odoo.css
    ├── annotations.css                 ← verbatim copy of catalog annotations.css
    └── walkthrough.js                  ← verbatim copy of catalog walkthrough.js
```

**Self-containment is a hard gate.** The `mock-fidelity-anchor` refuses any `http://`, `//cdn`, `../`, or skill-folder reference. Every asset is bundled or inlined.

---

## index.html structure (one screen with multi-axis chip row)

```html
<section class="mock-screen" data-screen="quote"
         data-title="Quote — lot-tracked line"
         data-desc="Sales Agent has added a lot-tracked product to a quotation"
         data-mock-variant-axes='[
           {"key":"tracking","label":"Tracking","default":"lot",
            "options":[["lot","Lot"],["serial","Serial"]]},
           {"key":"state","label":"State","default":"unallocated",
            "options":[["unallocated","Unallocated"],
                       ["partial","Partial"],
                       ["allocated","Allocated"],
                       ["locked","Confirmed (locked)"]]}
         ]'>

  <!-- Navbar + control panel composed VERBATIM from catalog/components/*.html
       — fill the SLOTs; never hand-code an alternative. -->

  <div class="o_form_view">
    <div class="o_form_statusbar">
      <!-- Confirm button: visibility depends on state axis -->
      <button class="btn btn-primary"
              data-mock-variant="state=allocated"
              data-mock-toast="Quotation confirmed."
              data-mock-toast-type="success">Confirm</button>
      <button class="btn btn-primary"
              data-mock-variant="state=partial"
              data-mock-toast="Line has 2 of 3 units allocated. Allocate the remaining units before confirming."
              data-mock-toast-type="danger">Confirm</button>
      <button class="btn btn-primary" data-mock-variant="state=locked" disabled>Confirm</button>
      ...
    </div>

    <!-- Sheet, product line with the Allocation badge that varies on state -->
    <td>
      <span data-mock-variant="state=unallocated" class="badge text-bg-danger">Unallocated</span>
      <span data-mock-variant="state=partial" class="badge text-bg-warning">Partial (2 of 3)</span>
      <span data-mock-variant="state=allocated" class="badge text-bg-success">Complete</span>
      <span data-mock-variant="state=locked" class="badge text-bg-success">Complete
        <svg class="o_icon o_icon_sm"><use href="#o-lock"/></svg>
      </span>
      <!-- Select Lots button: only on lot-tracked + actionable states -->
      <button class="btn btn-sm o_btn_outline"
              data-mock-variant="tracking=lot,state=unallocated"
              data-mock-goto="picker">Select Lots</button>
      <button class="btn btn-sm o_btn_outline"
              data-mock-variant="tracking=lot,state=partial"
              data-mock-goto="picker">Continue Allocation</button>
    </td>

    <!-- One marker, anchored to a load-bearing element -->
    <span class="mock-marker" data-note="The Select Lots button only appears on lot- or serial-tracked products (User Story #1).">1</span>
  </div>
</section>
```

The chip row appears automatically: `Tracking: [Lot ▾]   State: [Unallocated ▾]`. Reader changes `state` to Partial → an inline warning banner appears on the form sheet ("Confirm refused — line has 2 of 3 units allocated"), the badge flips to Partial, and Confirm fires the same warning as a toast on click. Reader changes `state` to Locked → Confirm becomes disabled and the locked ribbon appears.

Two-surface guard discipline: the **persistent banner** makes the rule legible in static review; the **toast** confirms what happens on click. State variants that represent a refused/blocked action MUST carry both.

### Data multiplicity vs variant axis

A real Sales Order with both lot-tracked AND serial-tracked products
carries **two order lines** (one per product) — not one line whose
rendering you pivot via a Tracking chip. The data model already
expresses the multiplicity; the mock shows both lines. The Tracking
variant axis applies on screens like the **Select Lots dialog**, where
the same dialog context renders differently depending on which line
the user opened it for — there's a single "context," and the pivot
shows what changes.

Test: *"is this one record/context viewed under a lens, or actually
multiple data items?"* If the data carries the variation naturally,
show the data. Variants are reserved for state/actor/version pivots
on the same record.

### When ≥ 3 axes — the dependent chip pattern

If a screen needs ≥ 3 axes (rare; usually a sign of over-loading),
the chrome auto-collapses to a two-chip pair: `Variant: [Type ▾]` +
`Value: [<current value> ▾]`. The Type chip picks WHICH axis to
pivot; the Value chip shows that axis's options. Switching Type
doesn't reset other axes' values — each axis still tracks its own
selection; the Value chip simply re-points. A screen author can
force the dependent chrome at 2 axes via
`data-mock-variant-mode="dependent"`.

---

## Per-package marker budget (4–7 total)

The reference uses **6 markers across the package**:

| # | Where | Anchored to |
|---|---|---|
| 1 | Quote screen, near Select Lots button | "Select Lots appears only on tracked products" (User Story #1) |
| 2 | Quote screen, near Allocation badge | "Allocation Status is computed from allocated vs ordered" (New Fields row 2) |
| 3 | Quote screen, on the warehouse field | "Picker filters lots to this warehouse's on-hand" (New Fields row 4) |
| 4 | Picker dialog, on the qty column | "Defaults to 1; fixed at 1 for serials" (New Fields row 5, Rule #4) |
| 5 | Delivery screen, on a locked move-line | "Pre-committed lots ship read-only to the warehouse" (User Story #5) |
| 6 | Settings screen, on the Lots & Serial toggle | "Precondition: this feature must be enabled" (impacted_apps row) |

Not one per field; not one per guard. Each marker points at a behavior the brief introduces; each has a citation in `data-note`. Anything past 7 should be questioned — could two markers fuse, or does the package have too many concerns?

---

## Marker text discipline

- `data-note` is the marker's content — appears in the floating tooltip on click.
- **Never duplicate `data-note` text as inline `<p>` body copy.** Body copy on a mock is for what the *user* sees in Odoo (placeholder text, empty-state copy, help strings the brief defines). Marker explanation lives only in `data-note`.

---

## Density discipline

The reference's lot picker dialog has **3 lots in the picker shown** (not 8) — three is enough to communicate "this is a tabular picker with on-hand counts." Adding 5 more lots makes the dialog read as a database dump.

The Quote form shows the standard sale.order fields the brief touches (Customer / Order Date / Pricelist / Payment Terms / Order Lines tab) plus the Other Info tab populated with the standard set Odoo puts there (Salesperson, Warehouse, etc.). Not every field on the real model; not just the net-new field.

Chatter shows two messages: the confirmation system-log + the activity scheduled for follow-up. Not a checklist of message-genre buckets.

---

## Catalog fragments used verbatim

```
navbar.html         → outer chrome on every screen
control_panel.html  → breadcrumbs + smart-button box on form screens; pager + switcher on list/kanban
form_view.html      → quotation + delivery
list_view.html      → picker dialog body; delivery operations table
dialog.html         → picker dialog backdrop + container
chatter.html        → chatter strip on the quote screen
settings.html       → Settings screen anatomy
walkthrough_bar.html → exactly one, outside the screens
```

If a fragment's markup looks wrong, **fix the fragment** — don't invent inline alternatives. The catalog is the source of truth; the package is downstream.

---

## What the anchors look for (post-reform)

### `mock-coverage-anchor`

- Every brief workflow step has a corresponding screen OR a State-axis variant on a primary screen.
- Brief-defined guard rules are visible somewhere (as State-axis values OR standalone guard screens — both valid).
- Data-driven options (lot/serial, B2C/B2B) have a registered axis; the mock doesn't silently drop one.
- Markers describe brief elements, not generic Odoo behavior.
- `data-note` text doesn't appear as inline body copy on the screen.
- Package marker count is in the 4–7 range; over ~10 triggers an over-annotation finding.

### `mock-fidelity-anchor`

- Self-containment hard gate: no external refs, no escapes.
- Catalog fragments used verbatim (no hand-coded navbar/settings/form chrome).
- No emoji glyphs where icon sprites exist (`🔒`, `⚙`, `⋮⋮`, `☐`, `✓` are all replaced by `<use href="#…"/>` or real `<input>` elements).
- Variant axes (`data-mock-variant-axes` JSON) are well-formed; defaults match options; child `data-mock-variant` references valid axis/value pairs.
- ≤ 4 axes per screen.
- Subtotal footer uses the catalog's `<table>` form with `o_subtotal_label`/`o_subtotal_amount`, not a flex-div alternative.
- Multi-workflow shell well-formed when present.

---

## Calibration cues at a glance

- **Curated, not enumerated.** 4–6 primary screens; variants and state-axis values absorb most secondary screens.
- **Catalog fragments verbatim** — the most common regression is hand-coding a navbar / settings / control panel that diverges from the fragment.
- **Markers point at brief deltas**, not interface decoration. 4–7 total per package.
- **Marker text stays in `data-note`** — never as inline body copy.
- **Density matches workflow weight** — enough rows/fields/chatter to read as real Odoo, not so many that the screen feels like a database dump.
- **Click-path connects every screen** via Next/Prev or `data-mock-goto`; every goto target resolves.
- **Self-containment** is mechanically enforced and is the hard gate.
