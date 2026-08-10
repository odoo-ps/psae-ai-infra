# Improvement Roadmap — candidate corpus improvements

A **non-committal backlog** of structural improvements to the *existing*
corpus. Distinct from its sibling [`skills.md`](skills.md), which catalogues
*new* skills. Nothing here is scheduled; tasks remain on
the backlog until a real trigger (new skill being scoped, Odoo major bump
imminent, observed corpus drift) picks one up.

Each task names its **deliverable**, the **elements it touches**, the
**rationale**, **cost**, **value**, **risks it introduces**, **risks it
caps**, **tradeoffs**, and a **likelihood**. Tasks are independent unless a
dependency is stated.

The corpus has a stable shape today — four consultant-facing skills, a
shared discipline layer under `_shared/`, an anchor pass per skill. What
it lacks is the scaffolding for *evolution*: release-cadence discipline,
drift detection between artefacts, and structural conventions that new
skills inherit rather than reinvent. The tasks below address that gap.

## Likelihood legend

| Rating | Meaning |
|---|---|
| **High** | Closes an active drift surface (something already moves out of sync between artefacts) or unlocks downstream work that's blocked without it. Build next. |
| **Medium** | Real value, clean fit, no active drift yet but predictable demand on the next Odoo major. Build before the next major bump. |
| **Low** | Speculative or contingent on adoption depth; defer until a concrete signal arrives. |

## Summary

| Task | Likelihood |
|---|---|
| [`skill-template`](#skill-template--canonical-skillmd-skeleton--medium) — canonical SKILL.md skeleton | **Medium** |
| [`corpus-changelog`](#corpus-changelog--versioned-changelog-at-skills-root--high) — versioned changelog at skills root | **High** |
| [`release-cadence-runbook`](#release-cadence-runbook--odoo-major-bump-refresh-procedure--high) — Odoo-major-bump refresh procedure | **High** |
| [`skill-corpus-lint`](#skill-corpus-lint--maintenance-rule-linter--medium) — extend lint to README maintenance rules | **Medium** |
| [`corpus-self-audit`](#corpus-self-audit--coherence-verification-tool--medium) — coherence verification tool | **Medium** |

---

## `skill-template` — canonical SKILL.md skeleton — **Medium**

**Deliverable.** A canonical `SKILL.md` template under
`_shared/templates/skill.md` that new skills inherit from.

**Covered elements.**
- New file: `_shared/templates/skill.md` with YAML frontmatter (`name` /
  `description` / `when_to_use` / `allowed-tools`) + standard section sequence
  (Goal → Entry → Output Contract → Reference Material → Validation →
  Iteration Etiquette → Production-readiness checklist) + role-walk pattern
  + anchor-pass invocation + troubleshooting / samples / reports footprint.
- README update: `§ Adding a new skill` gains a *"start by copying the
  template"* directive.

**Rationale.** The 4 existing SKILL.md files have converged at slightly
different conventions (heading naming, section ordering, Pre-Flight
numbering). A template locks the convergence formally so new skills inherit
a known shape rather than being written from scratch.

**Cost.** ~1 hr to extract the template from the 4 existing SKILL.md files
+ ~15 min to update README.

**Value.** New skill author starts from a known shape instead of cargo-
culting from whichever existing skill they happened to read first.
Comparison of existing SKILL.md files against the template becomes
mechanical, surfacing convention drift.

**Risks introduced.** A template can ossify decisions that should evolve.
Each future structural change must update the template too — a small but
real maintenance tax. Skills that legitimately need to deviate from the
template (e.g. `odoo-write-specifications` already skips plan mode) need
explicit carve-outs documented in their SKILL.md.

**Risks capped.** Convention drift between skills (the new 5th skill goes
its own way because no template existed). New-skill authors reinventing the
shape from scratch and missing load-bearing sections.

**Tradeoffs.** Upfront extraction + ongoing maintenance vs. acceleration of
new-skill creation + cross-skill consistency. The break-even is when a 5th
skill ships — before that, the template's value is only "audit existing
skills for drift," which is real but lower-leverage.

**Likelihood: Medium.** No new skill is scheduled; the template's full
value is realised only on new-skill creation. Build before the next new
skill, not on a deadline.

---

## `corpus-changelog` — versioned changelog at skills root — **High**

**Deliverable.** A `CHANGELOG.md` at the skills root tracking material
changes to the corpus per Odoo major version.

**Covered elements.**
- New file: `skills/CHANGELOG.md` following the `Keep a Changelog` shape
  (`Added` / `Changed` / `Removed` / `Fixed` per release, with a
  "Calibrated against Odoo X.Y" line per release).
- Optional cross-reference: each role checklist's calibration line can
  link to the most-recent CHANGELOG entry instead of restating the date.
- Optional anchor enhancement (deferred): `principles-anchor` could cite
  the CHANGELOG when reporting a calibration mismatch.

**Rationale.** The calibration line per role checklist
(`*Calibrated against Odoo 19.0*`) is decentralised across 11 files plus
the 4 industry-standards audits plus the 17 anchor files. A CHANGELOG
centralises *"the corpus shifted on `YYYY-MM-DD` because Odoo Y landed"*
so consumers don't grep every artefact. Active drift surface today —
nothing single-points-of-truth the current calibration version.

**Cost.** ~1 hr initial + ~30 min per release going forward.

**Value.** Consumers (and future-self) can answer "what changed between
the corpus's state two months ago and now?" without reading commit-log
noise. Anchor-pass JSON findings can cite a CHANGELOG entry when a
calibration shift explains a sudden flip in audit verdict. Single shared
reference for "current corpus state."

**Risks introduced.** Yet another file to keep current. An outdated
CHANGELOG is worse than no CHANGELOG (it misleads). The discipline
required: every meaningful corpus change touches both the affected files
AND the CHANGELOG. Skipped CHANGELOG entries silently rot the file's
authority.

**Risks capped.** Calibration drift across decentralized files; lost
institutional memory between consultant sessions; downstream consumers
(anchors, audits, new consultants reading the corpus) having no shared
reference for "current corpus state"; pre-Odoo-major-bump uncertainty
about *what's currently in scope*.

**Tradeoffs.** Maintenance discipline required at every commit vs.
single-source-of-truth for corpus state. The discipline scales with
the corpus's size; right now (4 skills, 17 anchors, 11 checklists) it's
modest. As the corpus grows, the CHANGELOG becomes more load-bearing.

**Likelihood: High.** Closes an active drift surface that's already
visible — calibration lines are scattered across 11+ files and nothing
ties them together. The discipline cost is low at current size.

---

## `release-cadence-runbook` — Odoo-major-bump refresh procedure — **High**

**Deliverable.** A `_shared/release_cadence.md` (or `RELEASE_CHECKLIST.md`
at the root) documenting the Odoo-major-bump corpus refresh procedure.

**Covered elements.**
- New file: a step-by-step runbook covering: re-read 11 role checklists
  against the new Odoo version's release notes, update calibration lines,
  surface new patterns (e.g. new view type, new helper), retire deprecated
  patterns, re-audit 4 industry-standards reports for currency, walk
  troubleshooting files (promote version-specific entries to archive), bump
  `CHANGELOG.md`.
- Cross-reference from `_shared/principles.md` (under the Troubleshooting-
  log discipline principle, or as a new principle if it earns one).
- Cross-reference from each role checklist's calibration line as a
  *"see [release cadence runbook]"* pointer (optional).

**Rationale.** Every role checklist explicitly says *"Re-review on each
major version bump"* but no runbook documents *how*. Today the work would
be ad-hoc; without the runbook the first re-calibration loses signal
piecemeal (a checklist gets refreshed but its paired anchor doesn't, or
the industry-standards audit goes stale, or the CHANGELOG entry doesn't
land).

**Cost.** ~1 hr to write the process doc. No scripting.

**Value.** Deterministic answer to *"what we do when Odoo 20 ships"*.
Reduces re-calibration from recollection to a checklist. Coherent
artefact refresh — checklist + anchor + audit + troubleshooting + CHANGELOG
all move together rather than independently.

**Risks introduced.** A process doc that isn't followed is worse than none
(misleading). Ossification: the runbook can lock in an order of operations
that's wrong for some future Odoo release.

**Risks capped.** Piecemeal calibration drift; tribal-knowledge dependency
for the major-version refresh; the *"oops the role checklist says Odoo 20
but the anchor still references Odoo 19 patterns"* class of silent staleness.

**Tradeoffs.** Documented process vs. fluid response to whatever the next
Odoo release surprises with. Mitigated by treating the runbook as
revisable — after each first real use, refine.

**Likelihood: High.** Required work on every annual major Odoo bump.
Without this, the first re-calibration this corpus undergoes will be ad-hoc
and lossy.

---

## `skill-corpus-lint` — maintenance-rule linter — **Medium**

**Deliverable.** Extend `_shared/scripts/` with a `_lint_skill_corpus.py`
script that enforces the README's maintenance rules across every skill.

**Covered elements.**
- New file: `_shared/scripts/_lint_skill_corpus.py` with checks:
  - **SKILL.md line cap** — `wc -l` ≤ 500 for every `<skill>/SKILL.md`
    (warn at 450, error at 500). Per [README § Maintenance](../README.md).
  - **SKILL.md frontmatter shape** — `name` / `description` / `when_to_use` /
    `allowed-tools` present; `name` matches folder slug.
  - **Standard sections present** — Goal / Entry / Output Contract /
    Reference Material / Validation. Exact heading text + ordering, once
    `skill-template` lands. Until then, presence-only with name fuzziness.
  - **Cross-skill consistency** — every skill that runs an anchor pass
    references the same Pre-ExitPlanMode Anchor Pass anchor list shape
    (or documents the carve-out, e.g. write-specs skips `scaffolding-anchor`).
  - **`_shared/` non-fork rule** — no role-checklist or principle copied
    into `<skill>/reference/` (grep heads of `_shared/role_checklists/*.md`
    against every skill's `reference/`).
  - **Per-skill troubleshooting present** — every skill folder has a
    `reference/troubleshooting.md` (or an explicit "no troubleshooting
    needed because …" carve-out in SKILL.md).
- Hook into the same exit-code shape as `_lint_troubleshooting.py`
  (0 clean / 1 warnings / 2 hard errors) so both linters can chain in CI.
- README update: § Maintenance gains a "Run `_lint_skill_corpus.py` before
  promoting changes" line.

**Rationale.** README's maintenance rules (SKILL.md ≤ 500 lines, structural
conventions, no-fork discipline, cross-skill consistency) are stated as
prose but not enforced. Today only troubleshooting is lint-covered. The
gap is invisible until a skill drifts — at which point catching it after
the fact is more expensive than mechanically blocking the drift.

**Cost.** ~3 hrs for the script (line counts, frontmatter parse, ordering
checks, grep-based non-fork detection). ~30 min to wire CI / mention in
README.

**Value.** Mechanical enforcement of conventions the corpus already
declares but doesn't police. Catches "SKILL.md crept to 540 lines"
before the file lands. Catches a future skill author copying a role
checklist into their `reference/` (the anti-pattern README explicitly
warns about). Same shape as `_lint_troubleshooting.py` so the two linters
read uniformly.

**Risks introduced.** A noisy lint trains people to ignore it. The
hardest part isn't the script — it's tuning thresholds so the lint stays
load-bearing. False positives on legitimate carve-outs (skills that
deliberately deviate from the template, write-specs skipping `scaffolding-anchor`)
need explicit allow-listing inside the script, not silenced via prose.

**Risks capped.** Silent SKILL.md bloat past the 500-line guidance.
Forking of `_shared/` content into per-skill `reference/` folders.
Section-order drift between SKILL.md files. Stale anchor-pass references
in skill files when the anchor inventory changes.

**Tradeoffs.** Script + allow-list maintenance vs. mechanical enforcement
of stated conventions. Pairs with `skill-template` — once the template
lands, the lint's structural checks tighten from "fuzzy presence" to
"exact match against template." Pre-`skill-template`, the lint is
checking against the de-facto convention extracted from the 4 existing
SKILL.md files.

**Likelihood: Medium.** Closes a real gap (README maintenance rules are
unenforced) but no active drift signal yet. Build alongside
`skill-template` so the template and its enforcer ship together.

---

## `corpus-self-audit` — coherence verification tool — **Medium**

**Deliverable.** A tool (skill or maintainer script) that re-validates
corpus internal consistency on demand. Output: a structured report listing
drift between artefacts.

**Covered elements.**
- Either a new skill under `skills/corpus-audit/` (consultant-facing) or
  a script under `_shared/scripts/_corpus_audit.py` (maintainer-only). Lean
  toward script first; promote to skill if consultants invoke it ad-hoc.
- Checks performed:
  - **Checklist → anchor traceability**: for each role checklist's
    Required-artifacts block, verify the paired anchor has a corresponding
    drift pattern.
  - **Calibration currency**: every checklist's calibration line points at
    the same Odoo version; matches the most-recent CHANGELOG entry; matches
    the troubleshooting files' "Applies" lines.
  - **Sample / report currency**: each skill's `reports/industry_standards_audit.md`
    references the current calibration version.
- Output format: JSON report mirroring the anchor-pass shape, with
  severity-graded drift findings.

**Rationale.** Periodic "is the corpus still coherent?" verification stops
being a manual diff against memory. After a few Odoo-major bumps and many
small edits, manual coherence drift is inevitable; this catches it.

**Cost.** ~4 hrs (script + report shape). Promotion to consultant-facing
skill: another ~3-4 hrs if/when warranted.

**Value.** On-demand coherence verification. Pre-Odoo-major-bump audit gate.
Surfaces calibration drift before consultants experience it as wrong
anchor verdicts or stale audit reports.

**Risks introduced.** Another tool to maintain. Could become noise if it
surfaces too many minor signals (typical "lint that warns at everything"
trap). Needs careful severity grading.

**Risks capped.** Silent corpus drift (the most dangerous class: anchors
flag real bugs incorrectly because the checklist's Required artifacts
moved without the anchor following). Calibration mismatches between
checklists, audits, CHANGELOG, and troubleshooting files. Tribal knowledge
of "what's coherent" becoming the only check.

**Tradeoffs.** Build cost + ongoing tuning of severity thresholds vs.
mechanical drift detection. **Dependency**: blocked on `corpus-changelog`
landing first (the CHANGELOG is the calibration source-of-truth this tool
would diff against). Indirectly benefits from `skill-template` (gives a
canonical shape to verify SKILL.md drift against) and `skill-corpus-lint`
(covers the structural / line-cap layer this audit sits on top of).

**Likelihood: Medium.** Real value, but contingent on `corpus-changelog`
+ `release-cadence-runbook` landing first to give it ground truth to
audit against.

---

## Deliberately out of scope (considered, not planned)

- **Anchor regression testing.** A CI harness that feeds known-bad inputs
  to each anchor and asserts the expected drift findings come back would
  formalise regression detection. Premature today — there's no signal of
  anchor drift in practice. The right move when the signal arrives is to
  build the harness directly (feed-and-assert against the live anchors),
  not to ship static prose fixtures documenting what the harness should do.
- **Per-skill anchor coverage metrics.** *"What % of Production-readiness
  criteria are auditable by an anchor?"* is a defensible metric but easier
  to re-run by hand at a major-bump moment than to maintain as a dashboard.

---

*Revisit this file when (a) a new skill is being scoped (does any task
above block clean integration?), (b) an Odoo major bump is imminent
(`release-cadence-runbook` becomes urgent), or (c) corpus drift surfaces
in practice (`corpus-self-audit` becomes urgent).*
