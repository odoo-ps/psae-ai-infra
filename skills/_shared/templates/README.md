# Skill template

[`skill.md`](skill.md) is the canonical `SKILL.md` skeleton. A new skill starts by
copying it; an existing skill can be compared against it section by section. This
file explains the skeleton. It is not copied.

## How to use it

1. `mkdir skills/<skill-slug>` and copy `skill.md` to `skills/<skill-slug>/SKILL.md`.
2. Fill the frontmatter. `name` equals the folder name. `description` plus
   `when_to_use` stay at or under 1,536 characters. `allowed-tools` lists only what
   the skill calls: plan-mode skills need `EnterPlanMode, ExitPlanMode, ToolSearch`,
   and skills with an anchor pass need `Agent`.
3. Fill every section in the order given. A section that does not apply either keeps
   its heading with a one-line `N/A — <reason>`, or is removed with a carve-out
   recorded under § Entry (see § Carve-outs below).
4. Delete every `<!-- TEMPLATE: … -->` comment.
5. Create the rest of the footprint (§ Skill folder footprint) and register the skill
   (§ Registering a new skill).
6. Keep `SKILL.md` at or under 500 lines. A procedure longer than a screen moves to
   `reference/` and is linked.

## Section order and where each section came from

The order follows the order things happen in a run. Each section was extracted from
what the existing skills had already converged on.

| # | Section | What it holds | Extracted from |
|---|---|---|---|
| 1 | Frontmatter | `name`, `description`, `when_to_use`, `allowed-tools` | all four skills; README § Adding a new skill |
| 2 | `# Title` + purpose | the request, the reader, the defining rule; link to principles | all four |
| 3 | `## Scope` *(optional)* | the hard boundary another skill owns | spreadsheet-report § Scope |
| 4 | `## Entry: …` | P13 architecture detection (or exemption) and P11 plan mode (or exemption) | plan-dev, spreadsheet-report (detection + plan mode); write-specs, mock-design (exemptions) |
| 5 | `## When To Use` | trigger, lifecycle position, nearest other skill | plan-dev, spreadsheet-report, mock-design |
| 6 | `## Output Contract` | ordered deliverables + what does NOT satisfy the contract | all four |
| 7 | `## Reference Material` | what to read before building, in authority order | all four |
| 8 | `## Pre-Flight` | read-only probes (in plan mode) vs destructive steps (after approval) | plan-dev, write-specs, spreadsheet-report |
| 9 | `## Fixed Questions` | interview discipline, necessity filter, the questions | plan-dev, spreadsheet-report, write-specs |
| 10 | `## Role-Based Questions` | which role checklists the skill walks, and when | plan-dev, write-specs, spreadsheet-report |
| 11 | `## Anchor Pass` | parallel drift detection before the gate | plan-dev (pre-ExitPlanMode), write-specs (post-interview), mock-design (pre-finish) |
| 12 | skill-specific execution | the skill's own procedure, as many `##` sections as needed | each skill |
| 13 | `## Validation` | three stages (principle #2) | all four |
| 14 | `## Documentation (Always Last)` | the reader-facing docs | plan-dev, spreadsheet-report, write-specs |
| 15 | `## Production-readiness checklist` | the done-gate as checkboxes | all four |
| 16 | `## Iteration Etiquette` | where fixes go; what to tell the user | all four |

## Carve-outs

A skill may deviate from the skeleton only with an explicit, justified note in its own
`SKILL.md`. The recognised carve-outs are:

- **Plan-mode exemption (P11).** Allowed when every write stays inside the skill's own
  output folder, nothing touches a DB or installs a module, and the artifact is not
  deployable code. The skill names the gate that replaces `ExitPlanMode` (write-specs:
  post-interview anchor pass; mock-design: lint + two anchors before bundling).
- **Architecture-detection exemption (P13).** Allowed for documentation-only artifacts
  whose shape does not depend on the host.
- **No interview.** A skill that consumes an existing artifact (mock-design) drops
  § Fixed Questions and § Role-Based Questions and says where its input comes from.
- **No anchor pass.** Allowed when the walkthrough is short enough not to drift; say so
  in one line under § Anchor Pass.
- **Free-text questions.** Each standing free-text question is listed with its reason
  under § Fixed Questions → Interview discipline (write-specs Q1, Q2, Q5).

A carve-out is never an edit to `_shared/principles.md` for one skill's benefit.

## Skill folder footprint

```
skills/<skill-slug>/
├── SKILL.md                         ← from _shared/templates/skill.md
├── agents/<skill-slug>.yaml         ← Claude.ai web/desktop Agent export (version, display_name,
│                                      short_description, default_prompt — a thin shell that says
│                                      "read SKILL.md first")
├── reference/
│   ├── troubleshooting.md           ← principle #6: header with write gate + update protocol,
│   │                                  sections by failure surface, 4-line entries
│   ├── troubleshooting-archive.md   ← same ID space, never loaded at run time
│   ├── samples/reference_pattern.md ← annotated walk-through of good output
│   ├── architecture_branches.md     ← only when § Entry runs Q0
│   └── scripts/                     ← Stage-1 lint, builders, validators (stdlib Python)
└── reports/
    └── industry_standards_audit.md  ← snapshot audit; stale-tolerant; re-run, don't edit in place
```

Exemplars to mirror: [`odoo-plan-development/reference/troubleshooting.md`](../../odoo-plan-development/reference/troubleshooting.md)
(header and sections), [`odoo-plan-development/agents/odoo-plan-development.yaml`](../../odoo-plan-development/agents/odoo-plan-development.yaml)
(agent export), [`odoo-write-specifications/reports/industry_standards_audit.md`](../../odoo-write-specifications/reports/industry_standards_audit.md)
(audit shape). A skill-specific anchor goes under [`../anchors/`](../anchors/) and
mirrors [`solution-architect-anchor.md`](../anchors/solution-architect-anchor.md) (README § Adding a new anchor).

## Registering a new skill

In the same change as the skill itself:

- **README** — layout tree, § Skills table, § Anchor subagents table (if anchors were
  added; update the anchor counts), § Which skill when, § What's in each skill's
  `samples/` and `reports/`.
- **Roadmap** — if the skill graduated from [`roadmaps/skills.md`](../../roadmaps/skills.md),
  mark its entry built with the date and a link.
- **Release cadence** — if the skill ships version-calibrated assets, add their refresh
  step to [`../release_cadence.md`](../release_cadence.md).
- **Lint** — `python3 skills/_shared/scripts/_lint_troubleshooting.py --skill <skill-slug>` exits 0.

## Conformance of existing skills (2026-10-19)

Snapshot of how each `SKILL.md` lines up with the skeleton. It is recorded, not fixed:
restructuring a skill is its own change. A `✓` means present in template order.

| Section | plan-dev | spreadsheet-report | write-specs | mock-design | version-upgrade | data-migration |
|---|---|---|---|---|---|---|
| Scope | — | ✓ | inline in purpose | — | ✓ | ✓ |
| Entry | split in two by When To Use | split in two by When To Use | ✓ (exemptions) | ✓ (exemptions) | ✓ | ✓ |
| When To Use | ✓ | ✓ | missing | ✓ | ✓ | ✓ |
| Reference Material | ✓ | after Role-Based Questions | ✓ | ✓ | ✓ | ✓ |
| Pre-Flight | after Anchor Pass | split across two sections | ✓ | inside Generation Pipeline | ✓ | ✓ |
| Fixed / Role-Based Questions | ✓ | ✓ (own role list, not the shared checklists) | ✓ (per-workflow deep dive) | carve-out: no interview | ✓ | ✓ (+ mapping walk; Q4 free text) |
| Anchor Pass | ✓ | none | ✓ (post-interview) | inside Generation Pipeline § 4 | ✓ | ✓ |
| Validation | ✓ | ✓ | ✓ | inside Generation Pipeline § 4 | ✓ | ✓ |
| Production-readiness | ✓ | inside Design System | ✓ | after Iteration Etiquette | ✓ | ✓ |
| ≤ 500 lines | 629 | 381 ✓ | 782 | 785 | ✓ | ✓ |

When a skill is next restructured, use this table as its to-do list and update the row.

## Maintaining the template

A structural convention changes in one place: here. When a change to principles, the
anchor-pass mechanics or the folder footprint alters what every skill must carry,
update `skill.md` and this README in the same change, then re-check the conformance
table. A convention that only one skill needs belongs in that skill, not here.
