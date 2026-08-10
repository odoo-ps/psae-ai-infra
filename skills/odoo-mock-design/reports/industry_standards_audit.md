# Industry Standards Audit — `odoo-mock-design` skill

> ⚠ **STALE SNAPSHOT (2026-06-13).** Authoritative current state is
> [`../SKILL.md`](../SKILL.md) and the reference docs under
> [`../reference/`](../reference/). Several descriptions below predate the
> Coverage-level gate, the 8-dimension coverage floor, the
> reference-material migration out of SKILL.md, and the templates
> single-source-of-truth pattern. Treat this file as a frame-of-reference
> baseline against external frameworks, not a current-state description.
> Re-run if the skill structure changes materially. The companion
> [`skill_audit.md`](skill_audit.md) carries the current structural audit.

**Date:** 2026-06-13
**Audit subject:** the `odoo-mock-design` skill after the
curation-and-restraint reform — density floors replaced with density
anchors; annotation density replaced with per-package marker budget;
single-axis pill switcher replaced with multi-axis filter-chip row;
guard-paths-as-separate-screens dissolved into State-axis variants;
supporting-surfaces sweep moved from default to opt-in; catalog-fragment
discipline tightened; pipeline collapsed for speed.
**Auditor:** Claude (Opus 4.7)
**Status:** Reference snapshot. Improvements deferred to future skill iterations, pending user prioritization. Not canonical structure — the canonical structure is [`../SKILL.md`](../SKILL.md), the style guide at [`../reference/style_guide.md`](../reference/style_guide.md), and the catalog at [`../reference/catalog/`](../reference/catalog/).

## Purpose of this report

A point-in-time evaluation of the skill against external frameworks for UI mockup design, design system fidelity, accessibility, and self-contained web artefacts. The report exists to:

- Inform future improvements (which gaps are worth closing, in what order).
- Justify deliberate exclusions, so future iterations don't accidentally re-introduce removed sections without first re-reading the rationale.
- Provide a baseline for re-audit when the skill structure changes materially.

Re-run the audit (or update this report in place) when:

- The Odoo Enterprise UI ships a significant new view type or class change.
- The catalog (`reference/catalog/`) gets refreshed for a new Odoo major.
- A new external framework relevant to mock-design / clickable prototypes is published.
- A structural depth/detail uplift (like the one this audit captures) lands.

---

## Frame of reference

Compared against six external reference points:

1. **WCAG 2.1 / 2.2** — Web Content Accessibility Guidelines; keyboard navigation, screen reader compatibility, contrast ratios.
2. **Material Design / Apple Human Interface Guidelines** — modern UI grammar for layout, typography, motion, interaction patterns.
3. **Atomic Design (Brad Frost)** — atoms / molecules / organisms / templates / pages hierarchy for design system composition.
4. **Brad Frost on design tokens** — color / spacing / typography token-based theming.
5. **Self-contained HTML demos as a practice** (e.g. CodePen-style single-file shareable artefacts) — the discipline of running anywhere with no external dependencies.
6. **Nielsen Norman Group on form state & affordance** — empty / filled / focus / disabled state distinctions, visible input affordances, "system status visibility" heuristic (Nielsen's #1 usability heuristic).

These frameworks are widely-recognized by designers + front-end engineers. They're connection points between the skill's Odoo-fidelity discipline and the practitioner's existing knowledge.

---

## How the skill maps to each framework

### WCAG 2.1 / 2.2

| WCAG criterion | Skill enforcement |
|---|---|
| 1.4.3 Contrast (minimum) | Odoo's catalog tokens (`--o-brand-primary`, `--o-gray-*`) meet 4.5:1 contrast for body text. The mock inherits the catalog; no custom colors injected. |
| 1.4.11 Non-text Contrast (UI components) | Catalog defines `--o-success-color`, `--o-danger-color`, `--o-warning-color` with adequate contrast for status indicators. |
| 2.1.1 Keyboard | Mock buttons render as native `<button>` elements; keyboard-focusable by default. Walkthrough nav uses native buttons; variant switcher pills are native `<button>` elements. |
| 2.4.4 Link Purpose (in Context) | Mock annotations (`mock-marker[data-note]`) describe each interactive element with context. Equivalent to ARIA label discipline. Annotation-density floors now require ≥ 1 marker per net-new field / gated action / record-rule-affected field — formalizes the "context" criterion. |
| 4.1.2 Name, Role, Value | Catalog's component classes (`o_main_navbar`, `o_form_view`, etc.) carry the right semantic roles inherited from Odoo's source. Variant-switcher pills carry `role="tablist"` on their container. |

**Gaps**: The skill doesn't formally cite WCAG. Mock annotations satisfy the Link-Purpose criterion implicitly but no explicit "accessibility checked" gate. Icon-only buttons in mocks would need `title=` (or `aria-label`) — the `ux-ui-anchor` flags this for the underlying spec, but `mock-fidelity-anchor` doesn't currently verify it on the rendered mock.

### Material Design / Apple HIG

| Principle | Skill enforcement |
|---|---|
| Hierarchy via typography scale | Catalog's font-size scale is inherited from Odoo SCSS; mock uses it verbatim. |
| Affordance — what's clickable looks clickable | `o_arrow_button_current` / `o_form_statusbar` / `oe_highlight` class system makes primary actions visually distinct. `o_input_pending` (dashed border + hover state) signals "click to fill"; `mock-fidelity-anchor` flags painted-but-dead affordances. |
| Consistency across views | Catalog enforces the same chrome (navbar + control panel + view container) on every screen. Multi-workflow chrome (workflow selector + variant switcher) lives in the walkthrough bar — one consistent control surface across the package. |
| Feedback — every action has visible response | Mock screens illustrate before / after states explicitly via the click-path. Variant switcher gives immediate in-place feedback (pill highlight + content swap). |
| Progressive disclosure | Variant switcher hides alternative options behind a single segmented control instead of rendering all variants flat — Material's "progressive disclosure" pattern. |

**Gaps**: The skill's design language is Odoo's, not Material's or HIG's. The alignment is incidental (both Material and Odoo favor flat design + clear hierarchy). The skill doesn't try to be Material/HIG-compliant; it tries to be Odoo-faithful.

### Atomic Design (Brad Frost)

| Atomic level | Skill correspondence |
|---|---|
| Atoms | Catalog tokens (CSS variables for color, spacing) + icons (`icons.svg` SVG sprite) + state classes (`o_input_pending`, `o_input_provided`). |
| Molecules | Catalog components (`o_arrow_button`, `mock-marker`, `o_breadcrumb`, variant-switcher pill). |
| Organisms | Catalog composites (`o_form_view`, `o_list_table`, `o_kanban_renderer`, walkthrough-bar). |
| Templates | Per-view-type composition (form layout, list layout, kanban layout) documented in `view_types.md`; density floors per view type now define minimum populated content. |
| Pages | Generated `mock-screen` instances (concrete data). Multi-workflow packages compose ≥ 2 page sequences in one document. |

**Gaps**: Strong alignment. The skill's catalog is essentially an atomic design system, sourced from Odoo Enterprise. The variant-switcher + multi-workflow uplift extends the page-tier composition without forking the atom/molecule tiers.

### Design tokens

| Token concern | Skill enforcement |
|---|---|
| Centralized definition | All tokens live in `catalog/odoo.css` as CSS variables. |
| Semantic naming | `--o-brand-primary`, `--o-success-color` (semantic, not "blue1") match Brad Frost's "use semantic names" discipline. |
| Theme adaptability | Dark mode (Odoo 17+) hot-swaps token values without changing component code. |
| No hardcoded values in components | The `mock-fidelity-anchor` flags hardcoded colors as a nit (breaks dark mode). Variant-switcher + workflow-selector CSS uses tokens throughout. |

**Gaps**: Aligned. The discipline matches; the framework citation is cosmetic.

### Self-contained HTML demos

| Self-containment criterion | Skill enforcement |
|---|---|
| Runs offline | `mock-fidelity-anchor` hard-gates external references (CDN fonts, remote images, external scripts) as blockers. |
| One-file portability | `index.html` + `assets/` folder, no symlinks to the skill folder. Multi-workflow packages still ship as a single folder — workflow selector chrome is JS-driven, not multi-file. |
| No build step | Mock package is plain HTML/CSS/JS; opens in any modern browser. Variant + workflow chrome are CSS class toggles, no framework. |
| Self-documenting | Annotation markers (`mock-marker`) + walkthrough bar + custom-field help "?" tooltips make the mock readable without external docs. Annotation-density floors keep self-documentation comprehensive. |

**Gaps**: Strongest alignment. The self-containment hard-gate is THE central discipline of the skill. The lint at `_lint_mock.py` + `mock-fidelity-anchor` both enforce it as defence-in-depth.

### Nielsen Norman Group — form state & affordance heuristics

| Heuristic | Skill enforcement |
|---|---|
| **#1 Visibility of system status** (Nielsen) | `o_input_pending` vs `o_input_provided` makes "is this field awaiting input or is the value system-supplied?" visually unambiguous. Pre-uplift, wizards rendered fully prefilled, which violates this heuristic. |
| **Affordance** (Norman) — "what can I do here?" | Variant switcher pills make "this screen has alternatives" discoverable in one consistent chrome location, not hidden in screen-by-screen variation. `o_input_pending` signals "click to fill"; wired through `data-mock-*` so the affordance is real. |
| **Recognition rather than recall** (Nielsen #6) | Workflow selector + step counter + dot row mean the viewer doesn't have to remember where they are in a multi-workflow / multi-step package. |
| **Match between system and the real world** (Nielsen #2) | Workflow titles + step descriptions use the brief's language, not abstract IDs. |
| **Help and documentation** (Nielsen #10) | Annotation markers + custom-field `?` tooltip. Annotation-density floors enforce minimum coverage. |

**Gaps**: The skill's form-state + affordance discipline now formally aligns with the established heuristics, but doesn't cite them in the skill prose. Citation would be cosmetic; the practice already matches.

---

## What the skill does well (no industry-framework gap)

- **Self-containment as a hard gate.** No external refs, no symlinks, no skill-folder dependencies. The mock package runs anywhere; this is rare in the design-mockup space (Figma mocks need Figma; HTML mocks usually need a build step).
- **Catalog refresh discipline + governance.** `REFRESH.md` documents catalog regeneration on Odoo version bumps. `SKILL.md` § Catalog governance adds the verbatim-use rule (use fragments as-is; fix the catalog when wrong, not the package) — the most leverage-y rule for keeping the visual cohort intact across mocks.
- **Two-anchor pre-finish gate** with mechanical lint behind it. `mock-coverage-anchor` + `mock-fidelity-anchor` enforce semantic correctness; `_lint_mock.py` enforces attribute hygiene. Most mockup tools have no equivalent.
- **Annotation markers grounded in source, scarce by design.** Markers are 4–7 per package, each tied to a load-bearing brief element. Prevents the documentation-sheet failure mode (one annotation per field) AND the wireframe failure mode (no annotations at all).
- **Multi-axis filter-chip variant chrome.** Same screen carries tracking × state × actor variations through a chip-row inspired by Odoo's search-view filter chips. Folds guard paths into state-axis values on primary screens, removing the screen-multiplication failure of the previous segmented-pill design.
- **Density calibrated to workflow weight, not floor-enforced.** Per-view density anchors in `view_types.md` aim for "what the user would see at this step in a real engagement" — explicit anti-patterns for both padding and stripping.
- **Input-state discrimination.** `o_input_pending` (with mandatory `data-mock-*` wiring) vs `o_input_provided` makes the before/after states visually + behaviorally distinct. NN/g's system-status-visibility heuristic, mechanically enforced.
- **Multi-workflow packaging.** ≥ 2 workflows ship in one package with workflow-selector chrome; navigation scopes per workflow; cross-workflow `data-mock-goto` works.
- **Curation over enumeration.** The skill aims for the smallest faithful mock (4–6 primary screens default). Supporting surfaces are opt-in; the P12 screen-list confirmation drops for small clear briefs. Pipeline collapsed for speed.

---

## What the skill explicitly does NOT do (justified exclusions)

- **No Figma / Sketch / Adobe XD export.** The skill's output is HTML; designers can recreate in their tool of choice if needed. Exporting to N proprietary formats is bloat.
- **No interactive prototyping framework integration (Framer, Origami, etc.).** Walkthroughs are linear via the built-in nav bar; complex state machines are out of scope. Data-driven variants give the most-needed "branching" affordance without a framework.
- **No actor-perspective variants.** Variants are scoped to data-driven options (lot/serial, B2C/B2B). Same-screen-different-actor is deferred — it depends on the brief naming each actor's visible scope, which most briefs don't, and the existing record-rule-affected-field marker (per annotation-density floor) covers most needs.
- **No formal accessibility audit (axe-core / lighthouse run).** WCAG alignment is implicit through the catalog; no automated WCAG audit is run on the generated mock.
- **No animation specification.** Odoo's UI is mostly motion-light; the mock doesn't try to specify animations.
- **No collaborative editing.** The mock is a snapshot artefact; iteration goes through the SKILL.md re-invocation, not in-place collaborative edit.

---

## Tiered improvement backlog

### Tier 1 — low cost, immediate clarity

- Add a one-paragraph cross-reference to WCAG + Atomic Design + Nielsen heuristics in `style_guide.md` for readers who already know those frameworks.
- Add an `aria-label` / `title=` check to `mock-fidelity-anchor` for icon-only buttons in the rendered mock.
- Add a "last refreshed against Odoo X.Y" line at the top of the catalog's `odoo.css` for traceability.
- Add `role="tab"` to variant-switcher pills (the container already has `role="tablist"`) so screen readers announce them correctly.

### Tier 2 — moderate

- Run `axe-core` (or `lighthouse`) on the generated mock as a pre-finish check; surface accessibility issues as nits.
- Add a `dark-mode preview` toggle to the walkthrough bar; let reviewers see the mock under dark theme.
- Build a CI test that opens every sample mock in headless Chrome and verifies zero console errors, zero failed asset loads, zero `o_input_pending` without `data-mock-*` wiring.
- Render the supporting-surfaces sweep as a Step-4 user-confirmable list (single `AskUserQuestion`, multi-select), so the user can opt surfaces in/out before assembly.

### Tier 3 — speculative

- Add animation specification for state transitions (slide-in dialog, fade for status changes).
- Add actor-perspective variants (a second variant axis per screen for "Sales rep view" vs "Manager view") when a brief surfaces with explicit per-actor visibility scoping.
- Add a Figma export step (only if customer demand surfaces).
- Render a "deep link" QR code on the cover screen pointing at the package's `index.html#screen-id` for the most-common entry points (e.g. "show me the lot picker").

---

## What changed since the last audit snapshot

The curation-and-restraint reform corrected several over-corrections from the depth-and-detail uplift:

- **Density floors → density anchors.** Hard minimums (≥ 8 rows, full field complement, ≥ 3 chatter entries) were producing bulk-for-bulk's-sake. Replaced with workflow-weight calibration in `view_types.md`. Both anti-patterns are now explicit: padding for density AND stripping for minimalism.
- **Annotation-density floors → per-package marker budget.** ≥ 1 marker per net-new field encouraged field-by-field annotation that read as documentation, not a mock. Replaced with **4–7 markers per package** anchored to load-bearing solution elements; explicit anti-pattern banning marker explanatory text as inline body copy.
- **Single-axis pill switcher → multi-axis filter-chip row.** Pills couldn't carry > 1 axis cleanly, forcing screen multiplication for state × tracking × actor combinations. New chrome (`data-mock-variant-axes` JSON + `data-mock-variant="axis=value,axis=value"`) supports up to 4 axes per screen, mirroring Odoo's search-view filter chips. Variant axes scoped to screens where the variation is meaningful (vs reused boilerplate).
- **Guard-paths-as-screens → State-axis variants.** "Every gated action gets its failure screen" produced 3 near-identical warning-dialog screens per workflow. Now guards typically render as State-axis values on the relevant primary screen (`state=partial`, `state=locked`); standalone guard screens reserved for redirect-to-different-surface or brief-narrates-as-step cases.
- **Supporting-surfaces sweep: default → opt-in.** Trigger table no longer runs automatically. Single `AskUserQuestion` ("Add supporting surfaces? — None / Settings only / All applicable") with default None. Most workflows don't need them.
- **Catalog-fragment discipline tightened.** New rule in `SKILL.md` § Catalog governance: use catalog fragments verbatim, fix the catalog when wrong (not the package). `mock-fidelity-anchor` flags hand-coded chrome as a blocker. Closes the most common regression — invented markup that the catalog CSS doesn't recognize.
- **Pipeline collapsed for speed.** 8 sequential steps + multi-cycle reconciliation reduced to 5: (1) Comprehension + screen list in one pass; (2) Curate to 4–6 screens; (3) Assemble; (4) Lint once + single anchor pass; (5) Finish. Stage-3 visual review moved to opt-in. The P12 screen-list confirmation drops for ≤ 6-screen packages with clear briefs.
- **Default screen count: 4–6 primary screens** per workflow. Above 6 requires brief justification.

The reform direction is **curation over enumeration**: the skill emits the smallest faithful mock, not the most complete one. Comprehensiveness comes from variant axes inside screens, not from screen multiplication.

---

## Re-audit triggers

- Odoo Enterprise UI redesign (the catalog needs full refresh).
- New view type ships in Odoo Enterprise (e.g. timeline, map).
- WCAG 2.2 → 2.3 transition (re-evaluate the contrast / keyboard / screen-reader criteria).
- A significant design-system framework adoption (e.g. if Odoo adopts a public token-system standard).
- Another structural uplift like the depth-and-detail one this audit captures.
