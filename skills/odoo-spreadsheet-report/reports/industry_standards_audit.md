# Industry Standards Audit — `odoo-spreadsheet-report` skill

**Date:** 2026-06-13
**Audit subject:** the `odoo-spreadsheet-report` skill as it stands after the Phase-1 calibration commit (`97fbda3`).
**Auditor:** Claude (Opus 4.7)
**Status:** Reference snapshot. Improvements deferred to future skill iterations, pending user prioritization. Not canonical structure — the canonical structure is [`../SKILL.md`](../SKILL.md) and the design system at [`../reference/design_system.md`](../reference/design_system.md).

## Purpose of this report

A point-in-time evaluation of the skill against external frameworks for dashboard design, data visualization, and BI report engineering. The report exists to:

- Inform future improvements to the skill (which gaps are worth closing, in what order).
- Justify deliberate exclusions, so future iterations don't accidentally re-introduce removed sections without first re-reading the rationale.
- Provide a baseline for re-audit when the skill structure changes materially or when the underlying frameworks evolve.

Re-run the audit (or update this report in place) when:

- A new `.osheet.json` shape ships in an Odoo release (Q1: register, Q2: globally).
- The design_system.md is materially restructured.
- A new external framework relevant to BI report engineering is published.
- The Odoo Spreadsheet runtime adds a significant new view type or feature.

---

## Frame of reference

Compared against four external reference points:

1. **Stephen Few's *Information Dashboard Design* (2nd ed., 2013)** — the canonical dashboard discipline: at-a-glance comprehension, cognitive-load minimization, no decoration, hierarchy by importance.
2. **Edward Tufte's *Visual Display of Quantitative Information*** — graphical excellence, data-ink ratio, chartjunk avoidance.
3. **Google's Material Design Data Tables / Cards spec** — modern UI grammar for tabular and card-based information.
4. **"Storytelling with Data" (Cole Nussbaumer Knaflic)** — slide-density and information-hierarchy discipline for business audiences.

These frameworks are widely-recognized by BI / analytics practitioners. They're connection points between the skill's Odoo-specific design system and the practitioner's existing knowledge.

---

## How the skill maps to each framework

### Stephen Few (Information Dashboard Design)

| Few's principle | Skill enforcement |
|---|---|
| Dashboard fits on a single screen, no scrolling | Single-screen rule in `design_system.md` § Layout discipline (1320 × 700 px viewport target). |
| Reduce non-data ink (decoration) | `areGridLinesVisible: false` on every visible sheet; no decorative borders / shading. |
| Use sparklines / small multiples for trends | `odoo_bar` / `odoo_line` / `odoo_pie` chart widgets supported; size-disciplined to 660×280 compact rows. |
| KPIs as scorecards, prominent placement | Scorecards (220 × 110) in the top tier, packed horizontally. Standard convention. |
| Avoid 3D effects, gradients, pie-chart abuse | Odoo's Spreadsheet runtime is flat by default; the skill reinforces by not introducing custom decorative CSS. |
| Color used semantically, not decoratively | One colour = one meaning: navy = chrome, red = issue, green = healthy, amber = warning. Documented in `design_system.md` § Colour palette. |
| Title bar clearly identifies the dashboard's purpose | Title bar at row 1, 50 px, navy + white, merged across full sheet width. |

**Gaps**: The skill could explicitly cite Few in `design_system.md` as the discipline's anchor for readers who already know the framework. Currently the discipline is correct but unsourced.

### Tufte (Visual Display)

| Tufte's principle | Skill enforcement |
|---|---|
| Maximize data-ink ratio | Default styling is minimal; decorative borders/fills are explicitly out-of-scope. |
| Avoid chartjunk | Charts ship with `axesDesign` (axis labels) only; no gridlines on presentation sheets; no 3D. |
| Small multiples | Side-by-side chart layout (660×280 each, anchored at col=0 and col=6 for a 12-col grid) supports small-multiple comparisons. |
| Labels integrated with data, not legends | `legendPosition: "none"` for single-series charts (label on the axis); legends only for multi-series. |
| Tabular data when numbers matter more than trends | List view with `sum=` / `avg=` decorators on numeric columns is the supported pattern. |

**Gaps**: The skill doesn't formally cite Tufte. The discipline is well-aligned but unsourced.

### Material Design (Data Tables, Cards)

| Material Design principle | Skill enforcement |
|---|---|
| Card has clear title + content + optional actions | Odoo's `figure` / scorecard model follows this — title bar + body + (optional) baseline. |
| Data table column-width fits content | Odoo's list view widths are content-fit by default. |
| Use elevation (shadow) sparingly | Odoo's design language is mostly flat; the skill doesn't introduce shadows. |
| Color-coded status indicators | Conditional formatting via CellIsRule + palette colors. |

**Gaps**: The skill's design system was Odoo-derived, not Material-derived. No deliberate Material citation; the alignment is incidental.

### Storytelling with Data (Knaflic)

| Knaflic's principle | Skill enforcement |
|---|---|
| Tier KPIs into one row each | Documented in `design_system.md` § Cognitive-load discipline: top KPIs (6–8 scorecards), trend (2 charts), distribution (2 charts). |
| Maximum 3 tiers per dashboard | Documented; "more than 3 tiers and the user is hunting." |
| Cognitive-load minimization | Documented; "one colour = one meaning"; "no floating annotations"; "same-tier widgets share dimensions." |
| Sheet ordering reflects narrative | `design_system.md` § Sheet ordering: headline → per-domain detail → hidden helpers. |

**Gaps**: Strongly aligned. No formal citation; would be cosmetic.

---

## What the skill does well (no industry-framework gap)

- **`cf_operators.md` as a hard reference card.** The Stage-1 verifier hashes against the operator registry — a CI-grade enforcement that's stricter than what Material / Few / Knaflic prescribe (they offer guidelines; this is rejection of an out-of-registry operator).
- **Pre-flight source sync (`_sync_o_spreadsheet_source.py`).** Reading the runtime's TypeScript source for ground truth rather than the minified bundle. No external framework requires this; it emerged from the skill's troubleshooting log (#12 / #14 / `cf_operators.md`).
- **`troubleshooting.md` in the shared 4-line format.** Refactored from the original mixed-content shape to match the shared discipline; the linter at `_shared/scripts/_lint_troubleshooting.py` enforces uniformly.
- **`design_system.md` as canonical source.** Layout / sizing / palette / styling lives in one file, not duplicated across SKILL.md. The skill's recent refactor reduced SKILL.md by ~130 lines.

---

## What the skill explicitly does NOT do (justified exclusions)

- **No formal D3 / ggplot grammar of graphics.** The Odoo Spreadsheet runtime is the constraint; supporting alternative grammars is bloat.
- **No machine-generated narrative layer.** Dashboards present data; the human reads context. Auto-generated "this metric is up 12% week-over-week" narrative is out of scope.
- **No CSS-in-JS, no custom theming framework.** Odoo Spreadsheet has its own CSS; layering a JS theming framework is incompatible with the runtime.
- **No CI test harness for the Stage-1 verifier.** The verifier exists per-instance (`<instance>/spreadsheet_reports/_verify_sheets.py`); a corpus-level CI test against the operator registry could be added but isn't yet.

---

## Tiered improvement backlog

### Tier 1 — low cost, immediate clarity

- Add a one-paragraph cross-reference to Stephen Few + Knaflic at the top of `design_system.md` for readers who already know those frameworks.
- Add a one-line note in `cf_operators.md` linking the Stage-1 verifier to the registry hash for traceability.

### Tier 2 — moderate

- Build a CI test that runs `_verify_sheets.py` against every `.osheet.json` sample under `reference/samples/`. Currently per-instance; could be corpus-level.
- Add a "dashboard storyline" question to `Fixed Questions` that asks the user to name the 1-line narrative the dashboard supports (Knaflic-aligned).

### Tier 3 — speculative

- Add per-region locale-aware number/date formatting documentation for cross-locale dashboards.
- Add an accessibility (WCAG 2.1) audit of generated dashboards — color contrast, screen-reader compatibility for scorecards.

---

## Re-audit triggers

- Odoo Spreadsheet runtime version bump (the `version` field in `.osheet.json` advances; verify `cf_operators.md` still matches).
- A new `widget=` for figures ships in Odoo Enterprise.
- The `_sync_o_spreadsheet_source.py` reference branch changes (currently tracks `19.0`).
