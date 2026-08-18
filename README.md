# Skills

The Corpus pulled onto every Odoo.sh development branch: the Doctrine, the Policy Source, the Guard Hooks, and the skills a **functional consultant** may run. Each skill turns a recurring request — "write me a functional spec", "generate an Odoo spreadsheet report" — into a structured, repeatable process: a one-question-at-a-time interview, builder-driven generation, multi-stage validation, and a parallel Anchor Pass that re-anchors the artifact against every source of truth before the finish line.

Every skill here serves one of the three **Judge Gate** exits — make the Small Change, produce a Document, or Refer. A skill that requires an action the Policy Source denies does not belong in this Corpus; see [Adding a new skill](#adding-a-new-skill).

Invoke a skill by typing its name as a slash command (e.g. `/odoo-write-specifications`, `/odoo-spreadsheet-report`).

## Layout

The four layers of the Guardrail sit at the repo root; `skills/` is the fourth.
Bootstrap installs only `skills/` and `hooks/` onto a branch — everything else
here is maintainer-facing.

```
psae-ai-infra/
├── README.md                    ← this file
├── CLAUDE.md                    ← DOCTRINE: injected into every session by Bootstrap
├── guardrails.yaml              ← POLICY SOURCE: the whole policy in one piece
├── settings.json                ← PERMISSION LAYER: deny / ask / allow globs
├── hooks/                       ← GUARD HOOKS: the containment
│   ├── guard_change.py          ← PreToolUse on Edit|Write|MultiEdit — judges edit content
│   └── guard_bash.py            ← PreToolUse on Bash — blocks deployment / DB / dependency commands
├── tests/                       ← fixture corpus over both hooks (never installed on a branch)
│   ├── run_guardrail_fixtures.py
│   └── fixtures_change.py, fixtures_commands.py
├── roadmaps/                    ← non-committal backlogs (revisit when triggers land)
│   ├── skills.md                ← candidate future skills + likelihood
│   └── improvements.md          ← candidate corpus structural improvements
└── skills/                      ← THE SKILLS, installed onto every branch
    ├── functional-edits/, odoo-python/, odoo-views/,
    │   odoo-tests/, odoo-upgrade/   ← Small Change exit (5 Functional Skills)
    ├── odoo-write-specifications/, odoo-mock-design/,
    │   odoo-spreadsheet-report/     ← Document exit (3 Document Skills)
    └── _shared/                     ← detail below
```

Inside `skills/`:

```
skills/
├── _shared/
│   ├── principles.md            ← 16 cross-cutting principles every skill follows
│   ├── anchor_pass.md           ← the shared Anchor Pass procedure (invocation, reconciliation, skip rules)
│   ├── troubleshooting.md       ← addon-implementation failure-mode lookup (4-line entries)
│   ├── troubleshooting-archive.md ← retired entries, not loaded by default
│   ├── odoo_runtime_idioms.md   ← runtime gotchas that pass lint but break in the live UI
│   ├── role_checklists/         ← 11 role disciplines (BA, SA, security, …) — shared across skills
│   ├── anchors/                 ← 16 Claude Code anchor subagents (audit content during the Anchor Pass)
│   │   ├── principles-anchor.md, plan-structure-anchor.md, troubleshooting-anchor.md
│   │   ├── *-anchor.md (×11 role anchors — one per role checklist)
│   │   └── mock-coverage-anchor.md, mock-fidelity-anchor.md  ← odoo-mock-design's pre-finish gate
│   └── scripts/
│       ├── _lint_troubleshooting.py ← shared linter for every troubleshooting.md (4-line shape, ID uniqueness, archive candidates)
│       └── _check_odoo_source.py    ← resolves model → {exists, module, edition} against on-disk source
├── odoo-spreadsheet-report/          ← skill: build an Odoo Spreadsheet (`.osheet.json`) report
│   ├── SKILL.md
│   ├── reference/
│   │   ├── design_system.md          ← canonical layout, sizing, palette, number formats, styling
│   │   ├── cf_operators.md           ← CellIsRule + global-filter operator registries (verifier hashes against)
│   │   ├── troubleshooting.md        ← active failure-mode lookup (4-line entries, shared linter)
│   │   ├── troubleshooting-archive.md ← retired entries, not loaded by default
│   │   ├── samples/                  ← reference `.osheet.json` examples the skill mirrors shape from
│   │   ├── spreadsheet-docs/         ← cached Odoo Spreadsheet documentation (loaded on demand)
│   │   ├── o-spreadsheet-source/     ← cached o-spreadsheet upstream source — see .gitignore note
│   │   └── scripts/                  ← _sync_o_spreadsheet_source.py (refreshes the cache)
│   └── agents/
│       └── odoo-spreadsheet-report.yaml ← Claude.ai Agent export
├── odoo-write-specifications/        ← skill: write a .docx functional spec
│   ├── SKILL.md
│   ├── reference/
│   │   ├── content_outline.md       ← canonical 5-section + 11-subsection docx structure
│   │   ├── docx_styling.md          ← fonts, palette, spacing, table styles
│   │   ├── samples/                 ← reference_pattern.md (annotated walk-through of a real-world spec)
│   │   └── scripts/                 ← _build_spec.py (builder), _lint_spec.py (Stage-1 lint)
│   ├── reports/
│   │   └── industry_standards_audit.md ← snapshot audit vs IEEE 830 / BABOK / Agile / Volere
│   └── agents/
│       └── odoo-write-specifications.yaml ← Claude.ai Agent export
├── odoo-mock-design/            ← skill: generate self-contained interactive Odoo screen mocks
│   ├── SKILL.md
│   ├── reference/
│   │   ├── view_types.md            ← which Odoo view to mock per step + screen anatomy
│   │   ├── field_placement.md       ← where each field lands per view type
│   │   ├── interactions.md          ← per-component interaction rules (modal, tab, status bar, …)
│   │   ├── style_guide.md           ← design tokens, fidelity rules, Odoo source map
│   │   ├── REFRESH.md               ← how to refresh the catalog on an Odoo version bump
│   │   ├── catalog/                 ← baked, hand-derived assets (built once from Odoo source)
│   │   │   ├── odoo.css, annotations.css, walkthrough.js, icons.svg, _gallery.html
│   │   │   └── components/          ← HTML fragments (navbar, control panel, form, list, kanban, …)
│   │   └── scripts/                 ← _lint_mock.py (Stage-1 lint), _render_catalog.py (catalog refresh)
│   └── agents/
│       └── odoo-mock-design.yaml    ← Claude.ai Agent export
├── functional-edits/            ← skill: judge small-vs-refer, then make the smallest edit
│   └── SKILL.md
├── odoo-python/                 ← skill: field / constraint / short compute on an existing model
│   └── SKILL.md
├── odoo-views/                  ← skill: Cosmetic View Edit — the five tests a view record must pass
│   └── SKILL.md
├── odoo-tests/                  ← skill: a focused test under tests/
│   └── SKILL.md
└── odoo-upgrade/                ← skill: version upgrade requested (mostly: refer)
    └── SKILL.md
```

The five Functional Skills are one file each by design: they are guidance for an
edit the Guard Hook already bounds, not procedures that produce an artifact.

All Claude Code anchor subagents (16 `*-anchor.md` files) live under [`_shared/anchors/`](skills/_shared/anchors/) — see § Shared material below. The per-skill `agents/` folders shown in the tree hold Claude.ai web/desktop Agent exports (`.yaml`); they are unrelated to the anchors.

## Shared material (`_shared/`)

Cross-cutting content that ≥ 2 skills consume lives at `skills/_shared/`, not under any one skill. Today the shared corpus is:

| File | What it is | Who reads it |
|---|---|---|
| [`principles.md`](skills/_shared/principles.md) | 16 numbered cross-cutting principles (one-question-at-a-time, three-stage validation, troubleshooting-log discipline, version-aware content sectioning, …) | every skill; `principles-anchor` audits against it |
| [`role_checklists/`](skills/_shared/role_checklists/) | 11 role lenses (Business Analyst, Solution Architect, Security, …) — Goal · Key Questions · Mechanisms · Pitfalls · Production-readiness criteria per role | `odoo-write-specifications` interview, the 11 role anchors |
| [`anchors/`](skills/_shared/anchors/) | 16 Claude Code anchor subagents — read-only drift-detectors that fire during a skill's anchor pass. 13 audit `_shared/` material (principles, role checklists, troubleshooting); 3 audit one specific skill's structure (`plan-structure-anchor` against the calling skill's own Output Contract; `mock-coverage-anchor` + `mock-fidelity-anchor` for mock-design). | every skill's anchor pass; symlinked into `~/.claude/agents/` for Claude Code discovery |
| [`scripts/`](skills/_shared/scripts/) | Shared validators (`_lint_troubleshooting.py`) consumed by ≥ 2 skills | each skill's edit-troubleshooting loop |

**When to put something in `_shared/`.** Two tests, both required:

1. **Role-shaped or principle-shaped, not consumer-shaped.** The content describes a generic discipline ("what a Security reviewer always checks") rather than a specific skill's procedure ("how `odoo-write-specifications` lays out its docx"). If the prose naturally references one specific skill in its voice, it belongs under that skill's `reference/`, not `_shared/`.
2. **Already consumed by, or about to be consumed by, ≥ 2 skills.** A single-consumer file lives in that skill's `reference/`. The moment a second skill genuinely needs the same content (not a sibling — the same), promote to `_shared/` rather than fork.

**Anti-pattern.** Copying a `_shared/` file into a new skill's `reference/` because "we need a tweaked variant." If you find yourself drafting that copy, stop: either (a) the canonical file needs the addition — make the edit in `_shared/` and update consumers in lockstep, or (b) the tweak is consumer-specific and belongs as a per-skill override note inside the new skill's `SKILL.md`, not a fork.

**Anchors and discovery flatness.** `_shared/anchors/` houses every anchor subagent — the 13 that audit shared material AND the 3 that audit skill-specific structure (`plan-structure-anchor`, `mock-coverage-anchor`, `mock-fidelity-anchor`). They co-locate not because all the *content* they audit is shared, but because Claude Code requires flat agent discovery at `~/.claude/agents` (this repo's symlink target). Content ownership for skill-specific anchors is documented in each anchor's own prompt body — read the anchor file to know what it audits.

## Install

Symlink both trees into Claude Code's discovery paths:

```bash
ln -s "$(pwd)/skills"                  ~/.claude/skills
ln -s "$(pwd)/skills/_shared/anchors"  ~/.claude/agents
```

Verify in a Claude Code session:

- `/skills` lists the five Functional Skills (`functional-edits`, `odoo-python`, `odoo-views`, `odoo-tests`, `odoo-upgrade`) and the three Document Skills (`odoo-write-specifications`, `odoo-mock-design`, `odoo-spreadsheet-report`)
- `/agents` lists all 16 anchors
- `/doctor` reports no parse errors

For Claude.ai web / Claude Desktop, upload each skill folder as a separate zip (one `SKILL.md` per zip root) via Settings → Capabilities → Skills. Anchors are Claude Code only — there's no equivalent on the web.

**Python dependencies** — a skill that needs a package Odoo does not already ship declares it in its own `requirements.txt`, so a bootstrap can install them all in one sweep:

```bash
find <corpus_dir> -name requirements.txt -exec pip install -r {} \;
```

| Package | Declared in | Required by |
|---|---|---|
| `python-docx` | `odoo-write-specifications/requirements.txt` | always — the spec docx itself (`_build_spec.py`, `_lint_spec.py`) |

That is the whole list. Requirements are deliberately **unpinned**: a bare requirement is satisfied by whatever version is already installed, so pip won't upgrade — and break — Odoo's dependency set.

Packages Odoo's own `requirements.txt` already pins are **not restated** here, to avoid redundancy. On Odoo.sh and in any Odoo dev venv they are present; only a bare-Python venv would miss them, and the skills degrade gracefully or gate an install on user confirmation when they do:

- `Pillow` — BPMN swimlane diagrams and the modern `flow_strip` PNG (`odoo-write-specifications`); a new module's app icons (`odoo-plan-development`). Without it, BPMN-opting workflows emit a "Pillow not installed" placeholder and `flow_strip` falls back to a table renderer; the rest of the spec renders normally.
- `passlib` / `Werkzeug` — the `admin_passwd` pbkdf2-sha512 hash in `odoo-plan-development`'s `_create_instance.py`, which falls back through both to a stdlib `hashlib` hash.

One **non-pip** dependency the sweep cannot cover: `odoo-mock-design`'s `_render_mock_screens.py` and `_render_catalog.py` shell out to a headless **Chrome/Chromium binary** on `PATH` (`google-chrome`, `google-chrome-stable`, `chromium`, or `chromium-browser`). Install it with the OS package manager.

## Skills

| Skill | What it does |
|---|---|
| [`odoo-spreadsheet-report`](skills/odoo-spreadsheet-report/SKILL.md) | Plan and generate an Odoo Spreadsheet (`.osheet.json`) report. Validates by importing the JSON into the chosen DB via `odoo-bin shell` and fixing errors until it loads cleanly. |
| [`odoo-write-specifications`](skills/odoo-write-specifications/SKILL.md) | Interview business + technical stakeholders and produce a professionally formatted `.docx` Odoo functional specification at `<repo>/specifications/` for hand-off to a dev team. Documentation-only — touches no deployable code, so the Guardrail permits it fully. Cover + auto-populating Table of Contents + 6 numbered top-level sections (Odoo Version, Business Case, Success Criteria, Apps Impacted, Functional Layout, Per-Workflow Detail) + 10 table-based subsections per workflow. Optional per-workflow BPMN swimlane diagrams (data-driven, Pillow-rendered) for workflows with multiple actors or non-linear flow. Runs the 14-anchor Anchor Pass; the docx itself is the design document. At the finish line, optionally hands off to `odoo-mock-design` to visualise the screens. Next step in the chain is hand-off to the technical consultant, who implements against the same scope. |
| [`odoo-mock-design`](skills/odoo-mock-design/SKILL.md) | Generate a self-contained, click-through HTML mock of the proposed Odoo screens from an existing brief or `odoo-write-specifications` spec folder. Maps each workflow step to an Odoo view type and composes screens from a baked "recognizably-Odoo" component catalog (real Odoo 19 tokens, layouts, class names) — never re-deriving styling from Odoo source at generation time. Output is a portable folder (`index.html` + `assets/`) with workflow navigation and numbered annotation markers and **zero external/network dependencies** (lint-enforced). Runs embedded at the finish line of `odoo-write-specifications` (output to `<spec-folder>/mocks/`) or standalone against a brief (output to `<repo>/mocks/<kebab>/`). No plan mode; the pre-finish gate is the two mock anchors. |

Each skill is ≤500 lines (per Anthropic's [skill authoring guidance](https://code.claude.com/docs/en/skills.md#add-supporting-files)) — heavier procedural content lives under `reference/` and loads on demand.

## Anchor subagents

The 16 anchors in [`_shared/anchors/`](skills/_shared/anchors/) are read-only drift-detectors. 14 fire in parallel at `odoo-write-specifications`' post-interview gate (per [`_shared/anchor_pass.md`](skills/_shared/anchor_pass.md)), each re-anchoring the docx draft against one source of truth. The two `mock-*` anchors fire instead at `odoo-mock-design`'s pre-finish gate, against the generated mock package.

| Anchor | Audits against |
|---|---|
| `principles-anchor` | [`_shared/principles.md`](skills/_shared/principles.md) — the 16 numbered principles |
| `plan-structure-anchor` | the calling skill's own Output Contract (for write-specs: [`content_outline.md`](skills/odoo-write-specifications/reference/content_outline.md)) — required sections, ordering |
| `troubleshooting-anchor` | [`_shared/troubleshooting.md`](skills/_shared/troubleshooting.md) — flags re-derived workarounds, missing refs |
| `business-analyst-anchor` … `ux-ui-anchor` (×11) | the matching [`role_checklists/<role>.md`](skills/_shared/role_checklists/) file |
| `mock-coverage-anchor` | the source brief/spec — every workflow step has a reachable screen; markers grounded in the brief |
| `mock-fidelity-anchor` | the [`odoo-mock-design` catalog + style guide](skills/odoo-mock-design/reference/style_guide.md) — recognizably-Odoo styling + self-containment |

Findings come back as structured JSON with `severity` (`blocker` / `nit`), `tags` (deduped across anchors), and a concrete `suggestion`. The main Claude reconciles, presents blockers one at a time (per principle #10), patches the artifact, and finishes only when no blockers remain.

## Conventions

- **Odoo.sh is the only target architecture** (P13). No detection, no per-architecture branching, no `instances/` tree, no version folder. Skills operate on the current `git` branch only — never ask "which branch?", never touch another. Every output path is relative to the Project Repo root at `/home/odoo/src/user`, the only writable tree.
- **First-iteration plan mode** (P11). Every skill enters plan mode on invocation; the plan lands at `<repo_root>/plans/<instance>-<functionality>.md` (deterministic, never the harness's random slug). Use `skills-` or `repo-` as the synthetic prefix for plans with no specific Odoo instance.
- **One question at a time** (P10). Sequential asks, never batched — even when an outer Fixed Question looks multi-part.
- **Necessity filter** (P12). Skip questions whose answers are inferable from invocation, conf, or pre-flight detection. Skipped questions land in the plan's `Assumptions` section; the user overrides anything wrong at `ExitPlanMode`.
- **Confirm-before-destructive** (P4). Every DB write, IDE patch, `git push`, or filesystem mutation passes through an explicit `y/N` gate. The skill never assumes consent from prior approvals.
- **Three-stage validation** (P2). A single passing build does not satisfy "done." Each skill exits only after stage 1 (static lint) + stage 2 (install/upgrade) + stage 3 (operational smoke) all pass independently.
- **Troubleshooting-log discipline** (P6). `_shared/` owns the addon-implementation corpus at [`_shared/troubleshooting.md`](skills/_shared/troubleshooting.md); a skill with a materially different failure surface ships its own at `<skill>/reference/troubleshooting.md` — active lookup index, 4-line entries, monotonic IDs (never reused, even after archive), sectioned by failure surface, soft-capped at 250 lines / 35 entries. **Write gate**: a new entry only lands if the skills tree is git-cloned with push access OR not git-cloned at all; cloned-without-push runs surface the proposed entry to the user without writing (a write would be lost on the next `git pull`). Shared linter at [`_shared/scripts/_lint_troubleshooting.py`](skills/_shared/scripts/_lint_troubleshooting.py) — validates every skill's file from one source.
- **`reference/` vs `reports/`.** A skill's `reference/` folder holds **canonical structure** — files the skill or its lint reads at runtime (content outlines, role checklists, styling tokens). A skill's `reports/` folder holds **snapshot artefacts** — point-in-time audits, evaluation reports, and improvement backlogs that inform future iterations but never gate behaviour. The distinction is important: when refactoring, `reference/` files demand updates in lockstep with the skill code; `reports/` files are stale-tolerant and re-run on demand. See [`odoo-write-specifications/reports/industry_standards_audit.md`](skills/odoo-write-specifications/reports/industry_standards_audit.md) for the canonical example.
- **Version-aware content sectioning** (P14). Where a role checklist or anchor accumulates ≥ 3 patterns whose applicability is bounded by Odoo version (Odoo 17+, Enterprise edition only, …), section the file using subsections (`### Common (all supported versions)`, `### Odoo 17+`, `### Enterprise edition only (any supported Odoo version)`) under the existing standard headings. Below the threshold, inline tags suffice. See [`_shared/role_checklists/ux_ui.md`](skills/_shared/role_checklists/ux_ui.md) and [`_shared/anchors/ux-ui-anchor.md`](skills/_shared/anchors/ux-ui-anchor.md) for the worked example. The major-version refresh procedure lives in [`roadmaps/improvements.md`](roadmaps/improvements.md) (`release-cadence-runbook`).

## Roadmaps

Two non-committal backlogs live under [`roadmaps/`](roadmaps/), both revisited
when their respective triggers land:

- [`skills.md`](roadmaps/skills.md) — candidate *new* skills that would extend
  the suite (a configuration/Studio runbook, data-migration/import, QWeb PDF
  reports, performance / security audits of live instances, …).
  Likelihood-rated; when a new engagement matches a candidate, that's the
  signal to graduate it into `skills/<name>/` per § Adding a new skill below.
- [`improvements.md`](roadmaps/improvements.md) — structural improvements that
  tighten the *existing* suite (SKILL.md template, corpus CHANGELOG,
  Odoo-major-bump re-calibration runbook, self-audit meta-skill).
  Priority-rated; revisit before the next Odoo major bump or when corpus drift
  surfaces in practice.

The two are deliberately separated: one extends consultant-facing capabilities,
the other tightens the corpus's own scaffolding.

## Adding a new skill

1. Create `skills/<skill-name>/SKILL.md` with YAML frontmatter:
   ```yaml
   ---
   name: <skill-slug>
   description: <what + when, ≤1,536 chars including when_to_use>
   when_to_use: <one-line trigger>
   allowed-tools: Read, Edit, Write, Bash, Grep, Glob[, Agent]
   ---
   ```
2. Keep `SKILL.md` ≤500 lines. Move per-architecture branches and skill-specific reference material to `<skill>/reference/`. **Do not copy role checklists into `<skill>/reference/`** — they are cross-cutting and live in [`_shared/role_checklists/`](skills/_shared/role_checklists/) (see § Shared material).
3. Link [`_shared/principles.md`](skills/_shared/principles.md) from the Reference Material section (the 16 cross-cutting principles). If the skill runs a role-shaped interview, also link the relevant entries under [`_shared/role_checklists/`](skills/_shared/role_checklists/). Extend or override a principle or role checklist only with a justified inline note in the skill — never edit `_shared/` for one consumer's benefit.
4. If the skill is non-trivial enough to drift during a long walkthrough, add anchors under [`_shared/anchors/`](skills/_shared/anchors/) — one per source of truth (principles, structure, troubleshooting, per-role). Even skill-specific anchors live there for flat Claude Code discovery (see § Shared material § Anchors and discovery flatness).
5. Add any external-source cache the skill manages (e.g. `o-spreadsheet-source/`) to [`.gitignore`](.gitignore).

## Adding a new anchor

Mirror the shape of [`_shared/anchors/solution-architect-anchor.md`](skills/_shared/anchors/solution-architect-anchor.md):

```yaml
---
name: <slug>-anchor
description: <what it audits + read-only + use-during>
tools: Read, Grep, Glob[, Bash]
model: sonnet
---
```

The body says: where to find the source of truth, what required artifacts to extract from it, how to detect drift in the plan, and the exact JSON output shape with `tags: ["role:<slug>", "checklist:<aspect>"]`. Add the anchor to the calling skill's Anchor Pass list so it fires in parallel; the mechanics live in [`_shared/anchor_pass.md`](skills/_shared/anchor_pass.md).

## Maintenance

- **Line caps.** SKILL.md ≤500 lines (Anthropic guidance); troubleshooting.md ≤250 lines / 35 active entries (this repo's soft cap). Both linters warn when caps are exceeded.
- **Pruning troubleshooting.** Run [`_shared/scripts/_lint_troubleshooting.py`](skills/_shared/scripts/_lint_troubleshooting.py) — it reports archive candidates (entries `fixed` for 90+ days). When migrating off a major Odoo version, retire that section to `troubleshooting-archive.md` in one move.
- **Promoting incidents.** When the same cause appears across multiple troubleshooting entries, that pattern has graduated — promote it to a principle in [`_shared/principles.md`](skills/_shared/principles.md) or a role-checklist line in the relevant [`_shared/role_checklists/<role>.md`](skills/_shared/role_checklists/), mark the incident entries `Status: obsolete YYYY-MM-DD`, and archive them.

## Which skill when? (decision tree)

For an Odoo consultant deciding which skill to invoke first:

```
Customer asks for something Odoo-shaped.
│
├─ Is it a SMALL change to something that already exists?
│  (a field, a constraint, a short compute, a Cosmetic View
│   Edit, report wording, a translation) ────────── YES ─► /functional-edits
│                                                          (judges it, then makes the smallest edit)
│
├─ Is the ask "build me a working addon"? ──── YES ─► STOP. Refer it.
│                                                     (a new model, manifest, security, or controller is a
│                                                      Major Change — the technical consultant's job. Offer
│                                                      a handover, or scope it properly with write-specs.)
│
├─ Is the ask "give me a written spec we can sign off"?
│  (typically pre-development, often pre-contract) ─── YES ─► /odoo-write-specifications
│                                                            (interview → docx at <repo>/specifications/)
│                                                            (next step → hand off to the technical consultant)
│
├─ Is the ask "show me what it'll look like before we build"?
│  (visual mockup of proposed screens, for stakeholder
│   sign-off OR companion to the spec) ──────────── YES ─► /odoo-mock-design
│                                                          (HTML + assets/, fully self-contained)
│                                                          (often runs at the finish of write-specs)
│
└─ Is the ask "build me a KPI dashboard / report"?
   (an Odoo Spreadsheet .osheet.json) ──────────── YES ─► /odoo-spreadsheet-report
                                                          (plans + validates by importing into the DB)
```

**Common chain**: write-specifications → mock-design (optional, at finish line) → hand off to the technical consultant, who implements.

The skills don't replace each other — they're stages of the same customer journey, with hand-offs documented in each skill's Output Contract.

## End-to-end walkthrough — what one customer engagement looks like

For a customer asking for a small custom addon (e.g. "let sales reps pick a lot at quote stage"):

| Step | Skill | Output | Time |
|---|---|---|---|
| 1. Frame the problem + scope | `odoo-write-specifications` | `<repo>/specifications/<task-code> - <client> - <slug>/<docx>` — a signed-off functional spec | 30–60 min interview |
| 2. *(Optional)* Visualise the proposed screens | `odoo-mock-design` (called from write-specs at finish line) | `<spec-folder>/mocks/index.html` + `assets/` — clickable mock | 5–10 min after the spec is done |
| 3. Hand off for implementation | *(the technical consultant)* | the addon itself — built by them, outside this Corpus | their estimate |
| 4. *(If KPI reporting is in scope)* Build a companion dashboard | `odoo-spreadsheet-report` | A `.osheet.json` imported into the DB and verified loadable | 20–40 min |

Per-step entry point:

- **Step 1**: type `/odoo-write-specifications` and answer Q1 (Task code). The skill walks the interview; at the end, optionally invokes step 2 inline.
- **Step 2**: type `/odoo-mock-design`, or accept the prompt at the end of step 1.
- **Step 3**: send the spec folder to the technical consultant. Building the addon is a Major Change — it is theirs, not yours.
- **Step 4**: type `/odoo-spreadsheet-report`. The skill asks for the report shape and validates the JSON imports cleanly.

Each skill is independently invokable — you can start at step 3 if the spec already exists, or run step 4 standalone if there's no addon to build.

## What's in each skill's `samples/` and `reports/`

For every skill, two reference artefacts ship alongside the SKILL.md:

| Skill | `reference/samples/` (what good output looks like) | `reports/` (audit / calibration) |
|---|---|---|
| `odoo-spreadsheet-report` | [STRUCTURE.md + 2 `.osheet.json`](skills/odoo-spreadsheet-report/reference/samples/) — concrete dashboard JSON examples | [industry_standards_audit.md](skills/odoo-spreadsheet-report/reports/industry_standards_audit.md) — vs Stephen Few / Tufte / Material / Knaflic |
| `odoo-write-specifications` | [reference_pattern.md](skills/odoo-write-specifications/reference/samples/reference_pattern.md) — annotated walk-through of a spec docx | [industry_standards_audit.md](skills/odoo-write-specifications/reports/industry_standards_audit.md) — vs IEEE 830 / BABOK / Agile / Volere |
| `odoo-mock-design` | [reference_pattern.md](skills/odoo-mock-design/reference/samples/reference_pattern.md) — annotated walk-through of a mock package | [industry_standards_audit.md](skills/odoo-mock-design/reports/industry_standards_audit.md) — vs WCAG / Material / Atomic Design / self-containment |

Read the relevant `reference_pattern.md` once before invoking the skill for the first time — it shows what the skill's output should look like at the density and fidelity target. The `reports/industry_standards_audit.md` is consulted when you need to justify a structural decision against a named framework.

