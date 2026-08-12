# Shared Principles for Odoo-Dev Skills

Cross-cutting discipline that every skill in this Corpus (`odoo-write-specifications`, `odoo-mock-design`, `odoo-spreadsheet-report`, future) is expected to follow. Skills link to this file in their **Reference Material** section. A skill may extend or override a principle for skill-specific reasons — but the override must be explicit and justified inline.

Read this once at the start of any skill run. The skill's own SKILL.md handles the details specific to its artifact; this file is the operating doctrine.

---

## 1. Builder-driven generation (and minimum code)

**Minimum code that solves the problem.** No features beyond what was asked. No abstractions for single-use code. No speculative flexibility, configurability, or error handling for impossible scenarios. If a senior engineer would call it overcomplicated, simplify.

**When a builder pays for itself, use one.** Builders earn their keep when (a) the artifact will be regenerated during fix-iterations, (b) it contains repeated structure (≥5 models, ≥3 nearly-identical XML/CSV blocks, generated geometry like layout coordinates), or (c) hand-editing the artifact loses information that would be diffable in a generator. Otherwise — hand-type and skip the builder. The shared rule is intentionally soft; each skill states its own concrete threshold in its SKILL.md.

Why builders pay off when they fit: hand-edited artifacts drift across iterations. Builders make repeats safe — style numbers stay consistent, repeated patterns stay DRY, layout coordinates stay calculable, and "what changed and why" lives in one diffable place.

Practical rules (apply when a builder is in use):
- Place the builder under the skill's own output folder at the Project Repo root (e.g. `spreadsheet_reports/_build_<slug>.py`, `specifications/<folder>/_reference/_build_<task-code>.py`). Those roots are the Document-path carve-out; a builder written anywhere else is measured against the Python floor and refused.
- Make the builder idempotent — running it twice produces byte-identical output.
- Hand-edits to the artifact must be back-ported into the builder before the next run, or they vanish.

**If your generator is longer than the artifact, the artifact wins.** If you write 200 lines of builder for what could be 50 lines of hand-typed XML, rewrite. The point of the builder is to amortise — once that doesn't hold, drop it.

---

## 2. Three-stage validation

Before running the validation pipeline, restate the user's request as a **verifiable goal** — a state-and-action pair the three stages can check against. "Add validation" → "Write tests for invalid inputs, then make them pass." "Fix the bug" → "Write a test that reproduces it, then make it pass." "Refactor X" → "Ensure tests pass before and after." Weak goals ("make it work", "looks good") force constant clarification; strong goals let the skill loop independently. The plan file's Context section is where the goal lives.

Every skill that produces an artifact intended to load in Odoo (or any other runtime) must then validate in three stages, each catching a different failure class:

| Stage | What it catches | Cost |
|-------|-----------------|------|
| **1. Static** (no runtime needed) | Schema shape, missing refs, bad operator names, orphan IDs, unbalanced syntax | Seconds |
| **2. Server-side** (runtime parses/imports) | Module dependencies missing, model/field not found, domain syntax errors, install failures | Tens of seconds |
| **3. Client / operational** (the user actually opens it) | Browser registry lookups, missing chart data, view rendering, ACL enforcement, computed-field correctness | Browser reload + click-through |

**Server-side success ≠ client success.** Always reload the artifact in the browser (or run the operational smoke) as a final check. If a runtime error fires only at stage 3, add a Stage 1 check that catches it the next time.

---

## 3. Pre-flight dependency resolution

Before generating anything, resolve and confirm:
- Every model / field / module the artifact will reference.
- The runtime version (Odoo, o-spreadsheet bundle, etc.) so version-specific syntax is right.
- Whether each owning module is **installed** in the target DB. If not, surface the install command, list what gets installed, and confirm with the user before running it.

Don't silently invent a model or field that doesn't exist — surface the gap immediately.

---

## 4. Confirm-before-destructive

Any of the following require an explicit user confirmation block listing the exact change before it runs:

- Installing or uninstalling Odoo modules (state changes, ACLs, menus).
- Writing files outside the skill's own output folder.
- Modifying or deleting existing user data.
- Sending messages to chat platforms, tickets, or external services.

**Not confirmable — these are DENIED outright** by the Guard Hooks, so never
offer them behind a `y/N`: creating, dropping, initialising, or naming a
database (`createdb` / `dropdb` / `-d` / `--database`); `git push` / `merge` /
`rebase`; switching to staging or production; installing pip or npm packages.
Offering a confirmation for an action that cannot run wastes the consultant's
turn and teaches them the gate is theatre. Stop and refer instead.

The confirmation block must be a single, scannable list — not a paragraph. Wait for an explicit `y` (or equivalent). Treat anything else as decline → halt.

---

## 5. Cleanup duplicates

When re-running a generator that creates DB-backed records (documents, dashboards, modules), search for prior copies and remove the obsolete ones before creating the new one. Otherwise the user opens an old copy and chases ghost bugs.

```python
prior = Model.search([("name", "=", NAME), <other discriminating filters>])
if prior:
    prior.unlink()
```

---

## 6. Troubleshooting-log discipline

The addon-implementation corpus lives at `_shared/troubleshooting.md` with its sibling `_shared/troubleshooting-archive.md` (fixed/obsolete/retired entries, not loaded at run time). A skill whose failure surface is materially different ships its own pair under `<skill>/reference/` — today only `odoo-spreadsheet-report` does. Either way the active file is a **living lookup**, not an append-only journal: read it before generating, update it after every new failure mode encountered.

Each entry follows this strict four-line shape (Fix may include a minimal snippet when essential):

```
### N. <symptom one-liner — include the literal error string when there is one>
Applies: <version / scope>. Status: <active | fixed YYYY-MM-DD | obsolete YYYY-MM-DD>. Last confirmed: <YYYY-MM-DD>.
Cause: <one sentence>.
Fix: <one or two sentences, or a copy-pasteable snippet>.
```

**Write gate — when to write at all (prerequisite for the protocol below):**

A new entry only lands if **at least one** of these conditions holds:

1. **The skills tree is git-cloned AND the user has push access to its remote** — the write propagates back to the canonical corpus on push; future runs benefit.
2. **The skills tree is not git-cloned** (local-only install, tarball, in-place edit on a non-versioned copy) — the write is local-only by definition; no synchronization concern.

If the skills tree IS git-cloned but the user does NOT have push access, **do not write the entry**. Surface it to the user instead:

> *"Discovered a new failure mode worth adding to troubleshooting.md: `<symptom + cause + fix>`. You don't have push access to the skills repo, so writing it here would be lost on the next `git pull` from upstream. Save it to your own notes and share with the skills maintainer."*

Operational check the skill runs before writing (one-liner that returns a yes/no):

```bash
SKILL_DIR="<absolute path to the skill's folder>"

if ! git -C "$SKILL_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    # Not a git working tree — local-only install, write freely
    WRITE_OK=true
elif [ -z "$(git -C "$SKILL_DIR" remote get-url --push origin 2>/dev/null)" ]; then
    # Git working tree but no remote — local git only, write freely
    WRITE_OK=true
else
    # Remote exists. Do NOT probe with `git push --dry-run` — pushing from a
    # branch is denied by the Guard Hook, and `git -C <dir> push` only slips
    # past it on a technicality. Assume no push access and surface the entry
    # to the user instead of writing it.
    WRITE_OK=false
fi
```

The check is deliberately conservative: a Corpus clone on a branch has a remote and no push path, so the answer is almost always "surface, don't write". That is the correct default — a surfaced entry is recoverable from session notes; a write lost on the next `git pull` is silently gone. The Corpus is maintained in the Infra Repo, not from a consultant's branch.

**Update protocol — required, not optional, AFTER the write gate has passed:**

1. **Before appending: grep the file for the literal error string.** If an entry already exists, update its `Last confirmed` date and refine `Cause`/`Fix` if the new occurrence taught something new — never duplicate.
2. **Monotonic IDs.** New entries take the next free integer in the *combined* ID space (active + archive). IDs are never reused, even after an entry archives.
3. **Categorical, not chronological.** Group entries under the section headers in the active file (Install / Stage 1 / Stage 3 / Demo data / Compute-API / Views / Version-specific / Planning-process). Within a section, IDs run in declaration order.
4. **Prune at thresholds.** When the active file exceeds 250 lines or 35 active entries, move `fixed`-for-90+-days entries to archive, retire whole version-specific sections when no supported deployment runs that version, and promote recurring patterns to principles/role checklists (incidents that abstracted upstream don't belong here).
5. **Lint the file.** The shared linter at [`_shared/scripts/_lint_troubleshooting.py`](scripts/_lint_troubleshooting.py) validates every skill's troubleshooting file against the 4-line shape. Run it after editing — `_shared/scripts/_lint_troubleshooting.py --skill <skill-name>` audits one skill; the same command without `--skill` audits all skills that ship a troubleshooting file. The linter flags duplicate IDs, malformed dates, and reports archive candidates (entries fixed for 90+ days).

Adding entries is part of the skill, not optional. Future runs avoid the same trap because the lookup is searchable and the linter keeps it honest.

---

## 7. No orphan references

Every declared resource — data source, ACL, view, menu, module dep, conditional format — must be referenced by something downstream. Orphans waste reader attention, sometimes throw warning icons in the UI, and grow into "I don't know if it's safe to delete" cruft over time. The Stage 1 verifier flags orphans, but what happens next depends on *who introduced them*.

**Orphans the current run introduces** — every declared resource emitted by this skill run must be referenced. Unreferenced ones get deleted automatically; this is the skill's own mess to clean up.

**Orphans the current run encounters in surrounding code** — flag in the plan file's Findings section (path, declaration line, suspected reason it's unused), but **do not delete without explicit user approval**. Per principle #4 (confirm-before-destructive), present the orphan with discovery context and wait for explicit `y`; anything else → leave it alone. Pre-existing orphans often turn out to be load-bearing through indirect references (dynamic ref lookups, external integrations, ad-hoc operator scripts); the skill is not the right place to decide they're safe to drop.

---

## 8. Iteration etiquette

**Touch only what you must.** Every changed line should trace directly to the user's request. Don't "improve" adjacent code, comments, or formatting that's outside the scope you were asked about. If you notice unrelated dead code or smells, mention them in the plan file's Findings section — don't fold the fix into this change.

**Match existing style.** When editing existing code, mirror the surrounding style: naming conventions, indentation, comment density, idiomatic patterns. Don't re-style what you're inheriting, even when you have a strong opinion. The diff should read as a focused change, not a re-formatting pass.

When the user pushes back ("this looks wrong", "it broke", "this is ugly"):

1. **Diagnose** against the relevant skill's checklist before guessing. Most complaints map to a known item.
2. **Fix** the specific cause, not the safe-default neighborhood.
3. **Regenerate** via the builder (don't patch the artifact directly).
4. **Re-validate** all three stages.
5. **Tell the user what changed** in concrete terms — they need a reason to reload, and naming the change avoids "did you actually fix it?" loops.

Don't apologise and revert to a generic safe baseline; that erases work the user already approved.

---

## 9. Read-then-edit, not assume

Field names rot. Method signatures move. Module ownership shifts across versions. Before extending or referencing existing code:

- Re-grep the source (`/home/odoo/src/odoo/`, `/home/odoo/src/enterprise/`, and this branch's own addons under `/home/odoo/src/user`), or run `_shared/scripts/_check_odoo_source.py --models <list>`.
- Confirm the field type, method signature, and owning module match what you're about to write.
- Treat in-tree code as authoritative for the running version, not memory or training data.

---

## 10. One question at a time

Interactive planning skills always:

1. Ask exactly **one** atomic question per turn — never bundle sub-questions even when an outer Fixed Question looks multi-part ("what's the problem, who has it, and why does it matter?" is three turns, not one).
2. Use **interview mode** by default — every question goes through the `AskUserQuestion` tool with 2–4 concrete options drawn from the relevant checklist, plus implicit "Other" for free-text. Do NOT pose questions in markdown prose expecting a free-form reply.
3. Wait for the user's answer.
4. Reflect the answer briefly (1–2 sentences) as updated assumptions in the plan file.
5. Ask the next **one** atomic question.

**Free-text opt-in is per-question, on explicit user signal only.** If the user says "let me write a brief" / "I'll give you a paragraph" / "let me just describe this in text" for a specific question, accept a free-form answer for THAT one question, then resume `AskUserQuestion` for the next. The opt-out doesn't propagate — never assume it carries forward unless the user explicitly says "stop using the question tool for the rest of this interview."

**Why both rules together:** the user's answer to question N often changes whether question N+1 is even needed (P12 necessity filter operates per-question). Bundling defeats that filter; markdown-prose asks defeat the structured-options shortcut that lets the user click through fast. The combined discipline is what makes a long interview feel cheap to the user instead of like a form to fill out.

A useful self-test before sending: count the question marks plus implicit "tell me X" bullets. If >1, cut it down to 1. Then check: is this an `AskUserQuestion` call? If not, and the user didn't opt out, you're about to violate this principle.

---

## 11. First-iteration plan mode

Interactive planning skills always enter **plan mode** for their first iteration — the
interview + pre-flight + design pass, before any artifact is generated.

Why: plan mode is read-only by construction, so the agent cannot start writing files
mid-interview. The user gets one consolidated approval gate (`ExitPlanMode`) covering
the whole approach, instead of a scattering of per-step `[y/N]` prompts. Fix-iterations
that happen after approval (re-generating a builder after a Stage-2 failure, patching
a manifest) run normally, outside plan mode.

How it works:
1. **On invocation, check plan mode state.** If a `<system-reminder>` confirms plan
   mode is already active, continue. Otherwise call `EnterPlanMode` (fetch its
   schema via `ToolSearch` first if it's deferred).
2. **Conduct the interview** (fixed questions, then role-based) one-at-a-time per
   principle #10. All read-only.
3. **Run read-only pre-flight**: model/field verification, module-dependency
   resolution, `$ODOO_VERSION`. Do NOT install modules or write builder scripts
   yet. (There is no environment detection and no DB creation — see P13.)
4. **Build up the plan file** at `<repo_root>/plans/<slug>.md` incrementally (the repo root's `plans/` directory, NOT `.claude/plans/`; create the dir if missing — Write auto-creates parents). The plan
   must include: the scoped artifact (addon name or report slug),
   models/fields used, owning modules to install, validation strategy, and a
   verification section.
5. **Call `ExitPlanMode`** to request approval. The user's approval is the gate for
   moving from design to execution.
6. **After approval**, proceed with scaffolding/builder generation, the three-stage
   validation (#2), and any subsequent fix-iterations — outside plan mode.

Only the **first** iteration is wrapped in plan mode. Subsequent runs of the same
skill (e.g. user comes back next week to add a sheet to the same report) re-enter
plan mode again because each invocation is a fresh "first iteration."

**Incremental-documentation skills are exempt.** A skill that drafts its
artifact to disk **section by section** as the interview progresses — with no
destructive actions, no DB writes, no `git push`, only writes inside its own
output folder — does not need plan mode. The user gets visible progress
question-by-question instead of an `ExitPlanMode`-cliff payoff. The exemption
is narrow: it applies only when (a) every write is inside the skill's own
output folder, (b) no DB or module install happens at any point, and (c) the
artifact is documentation, not deployable code. `odoo-write-specifications` is the
canonical case — see its SKILL.md for the documented carve-out. Skills that
qualify must justify the exemption inline in their SKILL.md and replace the
plan-mode gate with an end-of-interview anchor pass (or equivalent quality
review) that the user can accept or reject without an `ExitPlanMode` call.

**Plan mode normalizes execution state; it does not reshape the interview.** When
the skill is invoked while plan mode is *already* active (the user opened plan
mode first, then invoked the skill), the skill MUST still follow its own Fixed
Questions in declared order. Do **not** open with plan mode's generic "what do
you want to accomplish?" prompt — that anti-pattern collapses Q1–Q3
(instance / version / new-or-update) into a single open-ended business-need
answer, drops the scoping context the rest of the skill depends on, and produces
a half-specified plan. The interview shape belongs to the skill, not to plan
mode. Apply principle #12 the same way regardless of how plan mode was entered.

Concretely: the first question the user sees from the skill is always Q1 of the
skill's Fixed Questions list (or the first that survives principle #12), never a
free-form "describe your task." If the invocation already names the
instance / addon / report, surface that as an inferred assumption in the plan
file and proceed to the next question — do not re-derive scope via an open
prompt.

---

## 12. Necessity filter for questions

Before asking any question — fixed or role-based — apply a two-gate filter. **Ask
only if BOTH gates pass.**

**Gate 1 — Not inferable.** The answer is not already determinable from:
- The user's invocation prompt or earlier conversation.
- An existing `__manifest__.py`, builder script, or other on-disk artifact.
- A read-only pre-flight: `$ODOO_VERSION`, the current git branch, the
  o-spreadsheet bundle version, installed modules, `ir.model.data` ownership.

When the answer IS inferable, surface the inference in the plan file under an
**Assumptions** heading — `Assumed <X> from <Y>` — rather than asking. The user
overrides any wrong assumption at `ExitPlanMode` approval (principle #11), not via
upfront interrogation.

**Gate 2 — Material impact.** The answer would change the generated artifact in a
non-trivial way. Skip questions whose answer is functionally moot for this specific
request:
- Localization when the instance is single-company, single-currency, English-only.
- Performance when expected dataset size is small (<10k records, no cron).
- UX when the addon ships no menu or form view.
- Data Migration when no existing populated model is touched.
- DevOps / Operability when there's no cron, no external call, no upgrade hook.
- Security questions beyond the default ACL row when the addon is single-company
  and ships no record rules.

Default state for the role-based gates is already in the role table — extend the
same logic to fixed questions: the Odoo version is always `$ODOO_VERSION` (never
ask), and if Q3 (new vs update) is inferable from the invocation ("add a field to
`muzu_credit_limit.account_move`"), don't re-ask. Note the inference, move on.

**Tie case — multiple plausible interpretations.** When two or more interpretations are roughly equally plausible (no clear winner from the invocation + on-disk artifacts + pre-flight detection), do **not** pick one silently and bury the alternative in Assumptions. Surface both — list them in the plan file under a `Plausible interpretations` heading AND ask via the interview to pick. The bar to skip the question is *one confident inference*, not "I'd guess (a)." If you find yourself thinking "I'll just pick the more likely one," stop — that's the trap this clause exists to catch.

**Push back when warranted.** If you can see a simpler approach than the one the user is asking for, say so before implementing. If the request rests on an assumption you can grep-prove wrong (a field that doesn't exist, a model that's been renamed, a setting that's already on), surface the contradiction rather than silently working around it. State assumptions explicitly; if uncertain, ask; if unclear, stop — name what's confusing.

Friction from one extra question is lower-cost than building an artifact on a wrong assumption. The bar to skip is *confident* inference or *genuinely* moot impact — not "probably fine."

Combined with principle #10: questions that survive both gates are still asked one
at a time.

---

## 13. Odoo.sh is the only target architecture

**Every skill in this Corpus runs inside an Odoo.sh development-branch container. There is no architecture detection and no per-architecture branching.** Do not probe for Docker, bare-metal, or a local multi-version workstation; do not ask the user which host they are on. It is a question with only one possible answer.

What that fixes in place:

- **The writable tree is the Project Repo** at `/home/odoo/src/user`, checked out on the **development** branch. Nothing else on the filesystem is writable, and the Guard Hook denies any write that resolves outside it.
- **The framework source is read-only** at `/home/odoo/src/{odoo,enterprise,themes}`.
- **The database is injected.** Never create, drop, name, or re-wire it — no `createdb` / `dropdb`, no `-d` / `--database` on `odoo-bin`. There is no `instances/` tree, no `odoo.conf` to author, no venv to build, no nginx to scaffold, no IDE patch to apply. Those are workstation concepts and none of them exist here.
- **The Odoo version is in `$ODOO_VERSION`.** Read it; never infer it from a folder name like `v19/`.
- **The container is ephemeral.** Uncommitted or unpushed work is lost on rebuild — commit and `odoosh-push` once a change is verified. Plain `git push` fails on Odoo.sh.
- **Promotion development → staging → production is the user's job in the Odoo.sh UI**, never a skill's.

Any path a skill writes must therefore be relative to the Project Repo root. A skill that inherited a `v<major>/instances/<name>/…` output path from a workstation corpus is broken on a branch — the write is refused by the Guard Hook, not merely misplaced.

**Documentation-only skills** (e.g. `odoo-write-specifications` emits a `.docx`) never needed detection anyway; the host does not affect the artifact's shape. The spec *content* may still name a target architecture — that is authored by the user during the interview, never detected.

---

## 14. Version-aware content sectioning

The corpus stays calibrated against a single current Odoo major (today: 19.0) — there is no parallel tree per version. Patterns that vary by Odoo version are surfaced *inside* the artifact via explicit subsections under the standard role-checklist / anchor section headings (`Mechanisms`, `Pitfalls`, `Required artifacts`, anchor drift-pattern lists).

The audience is functional consultants — they should never need to `git checkout` a tag mid-engagement or load a parallel skills tree to filter version-specific patterns. The version is a property of the *content* they read, not the *tree* they navigate.

**Sectioning convention** — used inside the standard section headings, NOT as top-level structure:

```markdown
## Mechanisms / Tools

### Common (all supported versions)
- _inherit vs _inherits decision …
- @api.constrains vs @api.onchange boundary …

### Odoo 17+
- OWL component model …
- Command.create / Command.update / Command.link for x2many writes …

### Odoo 19+
- ir.cron paired with ir.actions.server …
- res.groups.privilege_id replacing category_id …
```

**Apply sectioning when** a section in a role checklist / anchor has 3+ version-specific patterns. Below that threshold, an inline tag — *"OWL component model (Odoo 17+ default)"* — is enough and reads naturally.

**Apply consistently to**:
- Role checklists under `_shared/role_checklists/` — `Mechanisms / Tools`, `Common Pitfalls`, `Required artifacts` sections.
- Anchors under `_shared/anchors/` — drift-pattern lists.
- Troubleshooting files (`_shared/troubleshooting.md`, `<skill>/reference/troubleshooting.md`) — already follow this convention via dedicated `## Version-specific — Odoo X` sections and per-entry `Applies: <version>` lines.

**Does NOT apply to calibration-snapshot artifacts**:
- Mock-design's `reference/` catalog files (`style_guide.md`, `field_placement.md`, `view_types.md`, `interactions.md`, `REFRESH.md`) — the entire catalog represents one Odoo major version end-to-end. Per-version sectioning would fork every file; the discipline instead is a wholesale catalog refresh per `odoo-mock-design/reference/REFRESH.md` on each major bump.
- `reports/industry_standards_audit.md` per skill — point-in-time audits, stale-tolerant by design (per [README § Conventions](../../README.md) `reference/` vs `reports/` distinction). Re-run on demand against the new version rather than sectioned in-file.
- SKILL.md files — describe the *process*, not version-specific patterns. Version-bound content belongs in the role checklists / reference assets the SKILL.md links to.

Rule of thumb: P14 sections content that describes *patterns spanning versions*; calibration-snapshot content (one version represented in full) refreshes wholesale instead.

**Calibration line** at the top of each role checklist (`*Calibrated against Odoo 19.0*`) names the **baseline current major**. Version subsections always tag their minimum version, not their maximum — `Odoo 17+` is forward-compatible until explicitly retired. On the next major bump, run `release-cadence-runbook` (in `roadmaps/improvements.md`): add the new `### Odoo X+` subsection where needed; retire `### Odoo Y+` subsections only when version Y falls out of support.

**Why this principle exists.** Without it, version-specific patterns accumulate inline-mixed with timeless patterns. A consultant working on Odoo 18 has to mentally filter every recommendation — *"does this exist in my version?"* — and false-positive anchors flag drift against patterns the target version doesn't have. Sectioning makes the filter mechanical; the consultant reads only the sections that match.

---

## 15. Lifecycle completeness & reversibility

Model the whole lifecycle, not the happy path. Any **state, commitment, lock, or reservation** a change introduces must have a defined **release** and **restore**, and every **terminal state** (cancel / expire / done) must **free what it held**. The recurring failure is the inverse: the forward action is designed and built, but unreserve, re-reserve, cancel-frees, and expire-releases are discovered only when a user hits the wall.

- **Specs** describe the full lifecycle — for each new state/commit/reservation: what creates it, what releases it, what restores it, what cancel/expire does — folded into the relevant existing section, or explicitly `N/A` when the change introduces no such resource.
- **Plans** build *and test* the inverses: a reverse-path test for every forward path (cancel frees, release→restore, expire releases), and terminal-state cleanup.
- **Guards** added to protect a committed resource must not break its legitimate release flows (cancel / unreserve / validate) — exempt system-initiated operations, block only the manual override.

A "reserve" with no "free", a "lock" with no "unlock", or a terminal state that strands a held resource is an incomplete design, not a finished one.

**Why this principle exists.** Half the post-delivery defects on a healthy-installing addon are missing inverses: the build passed every static and smoke check because the happy path worked, but the resource could never be released, restored, or freed on cancel. Reversibility is a design dimension, not an afterthought.

---

## 16. Verify inputs; don't inherit their gaps

An upstream artifact — a stakeholder's answer, a brief, a spec, or a mock — is an input to **verify**, never a guarantee of completeness to trust. Each skill independently checks its own required dimensions (lifecycle, contention, security, runtime correctness, the dimensions its role checklists name); **silence in the input is elicited or decided and recorded**, never passed through unexamined.

- A spec answering "what" (commit lots, reserve on delivery) does **not** exempt the plan from checking the edges the spec was silent on (cancel, unreserve, contention, exception states). The necessity filter (P12) skips *facts* that are genuinely inferable from the input, not *completeness dimensions*.
- A mock or spec screen is reconciled against the implementation before "done" — the interaction shape it shows (picker vs grid, widget, labels) is part of the requirement, not a suggestion.
- A stakeholder volunteering only the happy path is probed for the rest; the interview surfaces the inverses and the contention cases the stakeholder didn't think to mention.

**Why this principle exists.** A downstream skill that trusts its input inherits the input's blind spots. The first build of a spec inherited every gap the spec had — because nothing re-checked completeness at the build stage. Each skill must be **self-complete**: correct even when its input is partial.

---

## How skills extend this file

A skill may add skill-specific principles in its own `SKILL.md` (e.g. odoo-spreadsheet-report's Design System). It should not silently violate a shared principle — if there's a reason to deviate, document it inline with the deviation.
