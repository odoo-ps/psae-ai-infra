---
name: odoo-plan-development
description: Plan and build a verified-installable, operationally-smoke-tested Odoo addon for a chosen instance. Asks structured questions one-by-one (instance/version/business need/brief), then role-based questions (consultant, BA, architect, security, performance, UX, devops, migration, localization, QA, docs); scaffolds the addon, runs three-stage validation (static lint → install → operational smoke), and finishes with user + testing manuals.
when_to_use: Use this skill when the user wants an Odoo addon built or modified, expects structured questions first, and needs the result demonstrably installed and operationally healthy (not just "the install command exited 0").
allowed-tools: Read, Edit, Write, Bash, Grep, Glob, Agent, EnterPlanMode, ExitPlanMode, AskUserQuestion, ToolSearch, TodoWrite
---
# Plan Development

Turn a user request into a working, installed Odoo addon — with planning, scaffolding, three-stage validation, and concise documentation. Skill-specific discipline below; cross-cutting principles live in [`skills/_shared/principles.md`](../_shared/principles.md) and apply to this skill too.

## Entry: Architecture detection (Q0, runs before everything else, per principle #13)

Before Q1, before Pre-Flight, before any filesystem write — detect the host architecture and confirm it with the user. Skipping this step is what causes Local-flavoured behaviour (Pre-Flight A instance scaffold, `createdb`, IDE patches) to fire on Odoo.sh / Docker / bare-metal repos and collide with their directives.

Run [`reference/scripts/_detect_environment.py`](reference/scripts/_detect_environment.py) — its top-level `architecture` field returns one of `local | odoo.sh | docker | bare_metal | unknown`. The signals it probes are listed in [P13](../_shared/principles.md); don't duplicate them here.

**Q0 ask** — surface the inference in the plan file under an `Architecture` heading and ask:

> Detected architecture: `<env>` (sources: `<signal(s) that fired>`). Proceed with the `<env>` branch? Override accepted.

Wait for explicit confirmation. On `unknown` or multiple-signal cases, list each plausible architecture with its supporting signals and ask the user to pick — never silently default to Local.

**Source-introspection probe (immediately after Q0 confirmation, before any branch).** Run `python3 skills/_shared/scripts/_check_odoo_source.py --probe`. On exit 1 (no addons paths reachable), surface the canonical warning and halt — every standard-Odoo claim downstream becomes unverifiable otherwise.

**Routing.** After confirmation, route to the matching branch:

- `architecture: local` → continue with the rest of this document (Output Contract through Iteration Etiquette are the Local branch). Pre-Flight details live in [`reference/pre_flight.md`](reference/pre_flight.md).
- `architecture: odoo.sh` → load [`reference/architecture_branches.md#odoosh-branch`](reference/architecture_branches.md#odoosh-branch).
- `architecture: docker` → load [`reference/architecture_branches.md#docker-branch-safety-net`](reference/architecture_branches.md#docker-branch-safety-net).
- `architecture: bare_metal` → load [`reference/architecture_branches.md#bare-metal-branch-safety-net`](reference/architecture_branches.md#bare-metal-branch-safety-net).

## When To Use

Use this skill when the user wants an Odoo addon built or modified, expects you to plan with structured questions first, and wants the result demonstrably installed and operationally healthy — not just "the install command exited 0."

## Entry: Plan mode for the first iteration

**First tool call — non-negotiable.** As the very first action on invocation,
before *any* `Bash`, `Read`, `Grep`, `Glob`, `Write`, `Edit`, `Agent`, or
`AskUserQuestion` call, **enter plan mode** by calling the `EnterPlanMode`
tool. `EnterPlanMode` and `ExitPlanMode` are deferred tools in Claude Code —
if their schemas aren't already loaded, fetch them first via
`ToolSearch` with query `select:EnterPlanMode,ExitPlanMode`. If plan mode is
already active (the user entered it via Shift+Tab before the slash command),
skip the entry call and proceed to Q0. Do not begin Q0 detection,
environment scanning, or interview questions until plan mode is confirmed
active — without it, the destructive-action guards under principle #4 are
not armed, and the entire walkthrough runs outside the gate that
`ExitPlanMode` is meant to close.

Per shared principle #11, this skill **always** runs its first iteration in
plan mode. Do all interview questions, environment detection (Section A.0),
model/version checks, and instance/DB design inside plan mode, building up the
plan file. Call `ExitPlanMode` once the design is complete and the
pre-ExitPlanMode anchor pass has surfaced no remaining blockers — that call
presents the plan to the user for approval; the user's Approve action is the
actual exit signal.

**Plan file path: `<repo_root>/plans/<instance>-<functionality>.md`** — at the
repo root's `plans/` directory (NOT `.claude/plans/`), deterministic, not
random. `<instance>` is the answer to Q1 (the target instance folder name);
underscores are allowed and expected because Odoo instance names follow
`^[a-z][a-z0-9_]*$` (Pre-Flight A.2). `<functionality>` is the addon name when
known (Q3 result for an update, or the chosen `module_name` for a new addon),
otherwise a 2–4-word kebab-case slug of the business need
(e.g. `sale-lot-selection`, `crm-leadtime-report`); functionality is
`[a-z0-9-]+` only (no underscores — kebab keeps the `-` that joins the two
segments unambiguous). Final examples: `muzu_credit_limit-padel-booking.md`,
`yoa_test-sale-lot-selection.md`, `ai_test-product-brand.md`.

For plans that have no specific Odoo instance (skill-level changes,
repo-wide migrations), use a synthetic prefix in place of `<instance>`:
`skills-` for changes to the skills themselves, `repo-` for repo-wide
layout / convention changes. Functionality slug still applies.

Create the `plans/` directory at the repo root if it doesn't yet exist — the
Write tool will auto-create it on first plan write; otherwise `mkdir -p plans`
is a no-op safe pre-step.

**Placeholder migration.** After `EnterPlanMode` is called, the harness creates
an auto-generated random-name plan file (e.g.
`.claude/plans/prancy-nibbling-unicorn.md`) as the working-state placeholder.
This file exists *because* plan mode was entered — if it doesn't exist, plan
mode wasn't actually active and the entry call must be retried. As soon as Q1
is answered and a functionality slug can be formed (typically by the end of Q3
or Q4), **write the plan content to `plans/<instance>-<functionality>.md` at
the repo root** and delete the `.claude/plans/<random>.md` placeholder so two
copies don't drift. All subsequent plan edits target the repo-root file. If
`plans/<instance>-<functionality>.md` already exists at the repo root
(re-running the skill on the same addon), reuse it — append or replace its
contents, do not create a `-2` variant.

The plan file replaces the standalone confirmation block in Section A.6 — the
information that block shows (folder paths, ports, dbfilter, DB name, admin
password plaintext, IDE patch target, nginx scaffold target) goes into the
plan file, and the user's `ExitPlanMode` approval is the gate that authorises
**A.1–A.4, A.10, and A.11** to run.

Subsequent fix-iterations (Stage-1/2/3 failures, builder re-runs) happen outside
plan mode.

**Do not open with "what do you want to do?"** — even when invoked while plan
mode is already active. The skill's first message to the user is always Q1 of
the Fixed Questions list (or the first that survives principle #12), never a
free-form scope prompt. Plan mode's default opener is an anti-pattern here; it
collapses Q1–Q3 into a single business-need answer and skips the instance /
version / addon-scope context that the Pre-Flight and validation stages depend
on. See principle #11 ("Plan mode normalizes execution state; it does not
reshape the interview.")

## Output Contract

Produce, in order:

- **Interactive planning questions** — one at a time per the shared principle.
- **Instance + DB scaffold** if the user named a fresh instance (Pre-Flight A below).
- **Addon scaffold** under `<version>/instances/<instance>/custom_addons/<module_name>/` (where `<version>` is the selected instance's version folder — `v19`, `v20`, …) containing manifest, models, security ACLs, views, demo data (if needed), and tests where risk warrants them. **For every root (parentless) `<menuitem>` the addon adds, ship an Odoo-style icon and wire it via `web_icon` (plus `static/description/icon.png` when `application=True`)** — see Implementation Rules § App icons.
- **Stage-1 static lint passes** (`reference/scripts/_lint_addon.py`) — zero errors.
- **Stage-2 install/upgrade succeeds** in the chosen DB (`reference/scripts/_install_module.py`).
- **Stage-3 operational smoke passes** (`reference/scripts/_smoke_module.py`): module installed, models searchable, menus resolve, sample record creates+computes+unlinks, ACLs cover every model. **When the addon commits / locks / reserves a resource, Stage 3 also proves the inverses** (per principle #15 and the QA checklist): a reverse-path check (cancel frees, unreserve→restore, expire releases), a self-vs-others availability check, and a deny-case per locked mutation path. A lifecycle with no tested inverse does NOT satisfy the contract.
- **Stage-3c frontend tier** when the addon ships `static/src` assets (OWL / POS): a server-method shell smoke that calls the JS-facing methods against the live DB (proving the server contract, incl. deny-cases), **plus** a manual UI checklist in the testing manual. The OWL UI itself is not backend-testable — state that caveat in the plan; it's accepted, not a gap. A frontend module whose logic lives in the JS instead of guarded server methods does NOT satisfy the contract.
- **User manual + testing manual** under `<addon>/doc/`.
- **Update [`reference/troubleshooting.md`](reference/troubleshooting.md)** with any new failure mode hit during the run, following the strict 4-line format per principle #6. **Honour the write gate** ([`../_shared/principles.md` § 6](../_shared/principles.md) — only write if the skills tree is git-cloned AND the user has push access, OR if not git-cloned at all; otherwise surface the proposed entry to the user without writing). Grep first for the literal error string; if an entry exists, update its `Last confirmed` rather than duplicating. Run the shared linter [`../_shared/scripts/_lint_troubleshooting.py --skill odoo-plan-development`](../_shared/scripts/_lint_troubleshooting.py) after editing.

A bare install that doesn't pass Stage 3 does NOT satisfy the contract.

## Reference Material (Read Before Building)

- [`skills/_shared/principles.md`](../_shared/principles.md) — cross-cutting discipline (one-question-at-a-time, builder-driven, three-stage validation, confirm-before-destructive, troubleshooting-log discipline, no-orphan-references, iteration etiquette, read-then-edit). Read this first.
- [`reference/troubleshooting.md`](reference/troubleshooting.md) — known Odoo addon failure modes (active lookup index, 4-line entries, sectioned by failure surface). Read before generating; grep for literal error strings during fixes. Sibling [`reference/troubleshooting-archive.md`](reference/troubleshooting-archive.md) holds fixed/obsolete entries — not loaded by default, consult only for "did we hit this before?"
- [`../_shared/role_checklists/*.md`](../_shared/role_checklists/) — per-role mechanisms (Goal · Key Questions · Mechanisms · Pitfalls · Production-readiness criteria).
- [`reference/odoo_runtime_idioms.md`](reference/odoo_runtime_idioms.md) — runtime & interaction gotchas that pass lint/install/smoke but break in the live UI (transient-wizard saves, onchange sibling-sums, list-button header shift, icon colour, availability semantics, guards vs system flows, cross-document contention). Read before building any wizard, editable list, inline button, status indicator, or guard on a committed value.
- **Upstream specification folder (if the invocation references one)** — when the user points at a `<repo>/specifications/<task-code> - <client> - <slug>/` folder (typically produced by `odoo-write-specifications`), read **all three artifact classes**, not just the docx:

  - the `.docx` — primary deliverable, full prose;
  - `_reference/_build_<task-code>.py` — the SPEC_DATA Python that built the docx; structured input (workflows, fields, roles, BPMN data). **Also check for a top-level `dev_handoff` key** — when present it carries P12 inferences (`assumptions[]`), process-skip markers (`process_log.critique_skipped` / `process_log.anchor_pass_skipped`), per-workflow completeness decisions (`completeness.{wfN}.lifecycle / contention / availability_frame / validation_surface`), integration touchpoints (`integration_surface`), performance signals (`dataset_scale`, `crons_introduced`), and standard-Odoo overlap outcomes (`overlap_decisions`). Each `dev_handoff` field is a documented P12 short-circuit for one of this skill's own questions — cite the source as `dev_handoff.<field>` in Assumptions when you skip an ask because of it. The key is optional; default gracefully when absent. See `../odoo-write-specifications/SKILL.md` § Dev-Only Hand-off to odoo-plan-development for the shape;
  - `_reference/<task-code>-wf<N>-bpmn.png` — BPMN diagrams (if present);
  - `mocks/index.html` + `mocks/assets/` — the visual contract for each screen (if present). The mocks pin form layout, list columns, kanban shape, status-bar buttons, smart buttons, chatter presence, and field placement. **Treat them as authoritative for view-design questions** — skipping them means re-deriving design from prose when a finalized visual already exists.

  When a spec folder is the input, **reproduce its user stories, success criteria, and standard-Odoo overlap decisions into the plan's `## Requirements (imported from spec)` heading** (see § plan headings). The role anchors read only the plan file; importing this content makes the plan self-contained and stops the recurring BA/consultant/SA "missing stories/criteria/overlap" false-positive.
- `odoo/` and `enterprise/` source trees — authoritative for the running Odoo version. Always grep before assuming.

## Fixed Questions (Ask In This Order)

### Interview discipline (mandatory)

Per principle #10:

1. **One atomic question per turn.** Never bundle sub-questions. "What's the
   problem, who has it, and why does it matter?" is three asks, not one — the
   user's answer to "what's the problem?" often makes the other two trivial
   or moot.
2. **Interview mode by default** — every interview question is asked via the
   `AskUserQuestion` tool, with 2–4 concrete options that cover the likely
   answer space. The tool produces clickable choices; the user picks one or
   selects "Other" to free-text. Do not pose the question in markdown prose
   expecting a free-form reply — that's the failure mode this section
   prevents.
3. **Free-text opt-in is per-question, on user signal only.** If the user
   says "let me write a brief" / "I'll give you a paragraph" / "let me just
   describe this in text" for a specific question, accept a free-form
   answer for THAT one question, then **resume `AskUserQuestion` for the
   next question.** The opt-out doesn't propagate; never assume it carries
   forward unless the user explicitly says "stop using the question tool
   for the rest of this interview."
4. **Reflect briefly between asks** — 1-2 sentences summarising the user's
   answer and what it implies (updated `Assumptions` section in the plan).
   Then move on. No long recaps.

### Necessity filter (P12) per question

Before asking each question, check: is the answer inferable from the
invocation, an existing conf/manifest, or a read-only pre-flight detection?
Would the answer materially change the addon? If either gate fails, skip the
question and record the inference under the plan's `Assumptions` heading.
The user overrides any wrong assumption at `ExitPlanMode` approval.

Typical skips for this skill:

- **Q1 (instance)** skipped if the invocation names it (`"add a field to the muzu_credit_limit account.move"` → instance is `muzu_credit_limit`).
- **Q2 (version)** skipped when the target version is unambiguous: an existing
  instance fixes its own version (the `version` folder it lives in — read from
  the detector's `instances[].version`); and a new instance auto-selects the
  sole version when only **one** version folder exists. Ask only when creating
  a new instance **and** the detector reports 2+ version folders.
- **Q3 (new vs update)** skipped if the invocation names a specific existing
  addon, or explicitly says "new addon called X."
- **Q6 (validation DB)** skipped if the canonical `<version>_<instance>` DB
  already exists; default it silently and note the choice in the plan.
- **Anything answered by a referenced spec folder** — when the invocation
  references `<repo>/specifications/<task-code> - <client> - <slug>/`, every
  Fixed Question AND every Role-Based Question runs through P12 against the
  spec's docx + SPEC_DATA Python + mocks. Cite the source in the inference
  note (e.g. *"Q5a primary workflow — inferred from spec § Per-Workflow
  Detail / WF1 + mocks/index.html step 3"*). Mocks count as spec content for
  view-design questions — don't re-ask "kanban or list?" if the mocks
  already show kanban.

**Completeness dimensions are never skipped by a spec (principle #16).** P12
skips *facts* a spec or invocation genuinely settles (instance, version, DB,
view type already shown in the mocks). It does **not** skip the *completeness
checks* the role checklists own — **lifecycle & reversibility** (release /
restore / cancel / expire), **cross-document contention**, **lock-all-mutation-
paths**, the **availability reference-frame**, and the **runtime idioms** in
[`reference/odoo_runtime_idioms.md`](reference/odoo_runtime_idioms.md). A spec
that answers "what" (commit lots, reserve on delivery) rarely covers these
edges; verify each against the spec and, where the spec is silent, elicit or
decide and record under `Assumptions`. The build owns these whether or not the
spec mentioned them — the skill is self-complete, not a pass-through for its
input's gaps.

Q4 sub-questions and Q5 sub-questions are almost never inferable — ask them
(one at a time) unless the invocation already contains a clear answer for
that specific sub-question.

### The questions

Each line below is **one** `AskUserQuestion` turn. Asks marked **(a/b/c)** are
sub-questions of the same outer Q-number; they are still separate, sequential
turns — never bundled into one ask.

**Q1. Which instance is this for?**
Options: every existing instance the detector reports in `instances[]`, each
labelled with its version folder (e.g. `ai_test (v19)`, `acme (v20)`) since
instances live under `v<major>/instances/` and the same name could exist in
more than one version — plus an "Other (new instance)" option. The user picks
one or names a new one via Other → free text. If new, the skill will scaffold
it (folder, conf, DB) under the chosen version per Pre-Flight A — confirm
before any creation per P4.

**Q2. Which Odoo version?**
Reads the detector's `versions[]` (each a `v<major>/` folder with its own odoo
source + venv + enterprise). The version fixes BOTH the on-disk stack the
instance routes to (`v<major>/odoo`, `v<major>/enterprise`, `v<major>/instances/`)
and DB naming (`<major>_<instance>`) + `dbfilter`.
- **Existing instance** → not asked; the version is the folder the instance
  already lives in (`instances[].version`). Its conf/odoo-bin/venv all come
  from that version; a `dbfilter`/`release.py` mismatch is an error.
- **New instance, one version folder** → not asked; auto-select it and note
  the choice in the plan.
- **New instance, 2+ version folders** → ask. Options: each detected version
  (newest first / recommended), labelled with its real series from
  `versions[].release_version` (e.g. `v20 — Odoo 20.0`). The pick is passed to
  `_create_instance.py --version <major>`.

**Q3. New addon or update to an existing one?**
Options: "New addon" + each existing addon under
`<version>/instances/<instance>/custom_addons/`. If update, ask follow-up **Q3a** (also
one `AskUserQuestion` turn): "What kind of change?" with options like "Add a
new field/model", "Modify existing model/view", "Bug fix", "Refactor".

**Q4. Business need** — *three sequential atomic asks*:

- **Q4a.** What is the **problem**? Options: 3–4 concrete patterns from the
  Consultant checklist (e.g. "Manual rework", "Missing data point", "Wrong
  data being reported", "Compliance gap") + Other.
- **Q4b.** Who has it? Options: the standard Odoo user-role buckets that fit
  the instance's installed addons (e.g. "Sales rep", "Operations manager",
  "Finance".) + Other.
- **Q4c.** Why does it matter? Options: "Lost revenue", "Compliance / audit
  risk", "User frustration / churn", "Manual rework eating capacity" + Other.

**Q5. Solution brief** — *four sequential atomic asks*:

- **Q5a.** What's the **primary workflow** (the happy path)? Free-form is
  acceptable here only if the user opts in — default is `AskUserQuestion`
  with 3–4 workflow-shape options (e.g. "New record created → state machine
  to completion", "Cron pulls from external, writes records", "User edits
  existing record, triggers downstream", "Report-only").
- **Q5b.** What screens / views are needed? Options: list-only, form-only,
  list+form, kanban+form, pivot/graph report, full-app (menus + multiple
  views) + Other.
- **Q5c.** Constraints? Options: "Multi-company", "Multi-currency", "Heavy
  data volume (>10k records)", "External integration", "Compliance audit
  trail required" — `multiSelect: true`.
- **Q5d.** Integrations? Options: "None", "Inbound webhook", "Outbound API
  call", "File import/export", "Email triggers" + Other.

**Q6. Validation DB.**
Options: the canonical `<version>_<instance>` DB (if it exists, listed first
as "Recommended") + "Other (specify)" for override.

After Q6, proceed with role-based questions — only those that materially
change the outcome.

## Role-Based Questions (Ask Only What Matters)

Eleven roles. Each has a deeper checklist under [`../_shared/role_checklists/`](../_shared/role_checklists/) covering Goal · Key Questions · Mechanisms · Pitfalls · Production-readiness. Don't recite all questions — ask the few that change the outcome for this specific addon.

| Role                           | When to engage                                                         | Checklist                                                              |
| ------------------------------ | ---------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| **Consultant**           | Always                                                                 | [consultant.md](../_shared/role_checklists/consultant.md)                 |
| **Business Analyst**     | Always                                                                 | [business_analyst.md](../_shared/role_checklists/business_analyst.md)     |
| **Solution Architect**   | Always                                                                 | [solution_architect.md](../_shared/role_checklists/solution_architect.md) |
| **Security Expert**      | Always (every model needs ACL)                                         | [security.md](../_shared/role_checklists/security.md)                     |
| **Performance Engineer** | When >10k records expected, or cron present                            | [performance.md](../_shared/role_checklists/performance.md)               |
| **UX/UI Designer**       | Whenever the addon adds a menu or form view                            | [ux_ui.md](../_shared/role_checklists/ux_ui.md)                           |
| **DevOps / Operability** | Whenever the addon ships cron, external calls, or upgrade hooks        | [devops.md](../_shared/role_checklists/devops.md)                         |
| **Data Migration**       | Whenever the addon modifies an existing populated model                | [data_migration.md](../_shared/role_checklists/data_migration.md)         |
| **Localization**         | When deployed in non-English locales, multi-currency, or multi-company | [localization.md](../_shared/role_checklists/localization.md)             |
| **QA**                   | Always (at minimum the smoke checklist)                                | [qa.md](../_shared/role_checklists/qa.md)                                 |
| **Documentation Expert** | Always (last)                                                          | [documentation.md](../_shared/role_checklists/documentation.md)           |

**Interview discipline (same as Fixed Questions):** every role question is
a single `AskUserQuestion` turn with 2–4 concrete options drawn from the
role's checklist. One atomic ask per turn. Free-text opt-in is per-question
and per user signal only — resume `AskUserQuestion` for the next role's
question afterwards.

Default: ask 1–2 questions per applicable role, max. If the user signals
complexity (e.g. "this needs to be fast" → engage Performance more deeply),
expand to 3–4 questions for that role. Otherwise keep total questions low.

Apply principle #12 here too: within an "engaged" role, skip individual
questions whose answer is inferable or moot. Sources of inference: the
invocation, the conf/manifest, Pre-Flight detection, AND — when the
invocation references a spec folder — the docx prose, the SPEC_DATA
Python builder, the BPMN diagrams, and the `mocks/` folder. Mocks
authoritatively answer UX/UI, Solution Architect (view design),
Documentation (visible flow), and parts of Security (field-level
visibility) questions.

**Anti-pattern: skipping a role wholesale because a spec exists.** P12
applies per-question, not per-role. Read the spec, skip each role
question whose answer is *actually* in the spec (with a citation in the
Assumptions section), and ASK any role question the spec doesn't answer.
A spec that doesn't mention performance constraints means the
Performance role's questions still get asked — not skipped because
"there's a spec."

**The completeness dimensions are always asked, spec or not (principle #16).**
When the addon commits / locks / reserves a resource or adds a state, the
**lifecycle & reversibility** (SA/BA/QA), **cross-document contention** (BA/SA),
**lock-all-mutation-paths** (security/SA), **availability reference-frame** (SA),
and **guard-vs-system-flow** (devops/SA) questions are not "inferable facts" a
spec settles — they are completeness checks the build owns. If the spec is
silent, elicit or decide and record under Assumptions; never pass the gap
through. (See the Necessity-filter rule above.)

If a role's *only* questions would all be skipped, the role drops out
entirely — record the default decision in the plan's Assumptions section
(e.g. "Security: standard model-level ACL for `group_user`; no record
rule needed since addon is single-company").

## Pre-ExitPlanMode Anchor Pass (drift detection)

After the linear role walkthrough completes and the plan file is fully written —
but BEFORE calling `ExitPlanMode` and BEFORE any Pre-Flight destructive action
runs — fire the full anchor set in parallel. Each anchor re-reads its
source-of-truth document and the plan, then reports drift.

**Pre-anchor source-claim sweep.** Before firing the anchors, run `python3 skills/_shared/scripts/_check_odoo_source.py --plan <plan_file>` once. The script regex-extracts every `_inherit` / `Many2one` / `Many2many` / `One2many` comodel / `env[...]` claim and verifies each against on-disk source. Any `exists=false` is a hard blocker — fix the plan (rename the claim, or confirm it's an addon-internal model) before issuing the anchor pass. If `<spec-folder>/_reference/_build_<task-code>.py` carries a `dev_handoff.overlap_decisions` block from `odoo-write-specifications`, treat those `{model, module}` pairs as already resolved and skip them; the sweep only re-verifies claims this plan introduces beyond the spec.

Drift is what context loss looks like in a substantial walkthrough: a checklist
item discussed in conversation but never landed in the plan; a principle
deferred-to-later that silently vanished; a role's required artifact
under-written because the conversation moved past it too fast. The walkthrough
is linear by design (each role builds on prior decisions, principle #10 keeps
one question at a time) — but linear *and* long is exactly where state can
erode. The anchor pass is the recovery mechanism: re-anchor every section of
the plan against the immutable source of truth before the gate.

### Invocation

**ALL 15 Agent calls go in ONE message, foreground only.** This is what makes
the anchor pass an actual gate:

- **One message, 15 tool calls.** Emit all 15 `Agent` tool calls in a single
  assistant message. The Claude Code harness runs tool calls inside one
  message concurrently and blocks the main Claude's next turn until every
  one completes — that block is the gate. If the main Claude finds itself
  splitting anchors across multiple turns (10 now, 4 later), the gate is
  broken: abort and re-issue all 14 in one message.
- **Foreground only.** Never set `run_in_background: true` — it returns a
  task ID without waiting, defeating the gate. The default (foreground)
  is what we need.
- **No `ExitPlanMode` in the Agent-call message.** It must land in a later
  message, after reconciliation — same-message inclusion races the gate.

All anchors fire concurrently, each reading the same frozen plan file:

- `principles-anchor` — vs `_shared/principles.md` (16 numbered principles)
- `plan-structure-anchor` — vs this file's Output Contract (mechanical heading presence / ordering / plan-file path)
- `scaffolding-anchor` — vs this file's Pre-Flight A/B sections (nginx, IDE patches, conf alignment, dbfilter, architecture-branch consistency)
- `troubleshooting-anchor` — vs `reference/troubleshooting.md` (catches re-derivation of known workarounds, missing/stale entry references)
- `business-analyst-anchor` — vs `../_shared/role_checklists/business_analyst.md`
- `consultant-anchor` — vs `../_shared/role_checklists/consultant.md`
- `data-migration-anchor` — vs `../_shared/role_checklists/data_migration.md`
- `devops-anchor` — vs `../_shared/role_checklists/devops.md`
- `documentation-anchor` — vs `../_shared/role_checklists/documentation.md`
- `localization-anchor` — vs `../_shared/role_checklists/localization.md`
- `performance-anchor` — vs `../_shared/role_checklists/performance.md`
- `qa-anchor` — vs `../_shared/role_checklists/qa.md`
- `security-anchor` — vs `../_shared/role_checklists/security.md`
- `solution-architect-anchor` — vs `../_shared/role_checklists/solution_architect.md`
- `ux-ui-anchor` — vs `../_shared/role_checklists/ux_ui.md`

Each anchor:

- gets the absolute plan-file path as its sole prompt argument
- has read-only tools (Read, Grep, Glob, Bash) — MUST NOT edit anything
- returns a structured JSON report with `findings[]` (severity, location, issue,
  suggestion, tags) **as the anchor's final assistant message** — the
  return-value IS the audit. Anchors must NOT write their findings to a file
  (no Write, no `> file` redirection through Bash). When phrasing the prompt
  to the anchor, do not ask it to "save" or "write" the audit anywhere; ask
  it to *return* the JSON. Past runs have had anchors emit `echo '{...}' > audit.json` because the prompt or the `## Output` heading was misread as
  "produce an output file"; the wording in the anchor files and in this
  invocation block exists to prevent that.

Anchors are stored at `<repo>/skills/_shared/anchors/<name>.md` (under the
cross-cutting `_shared/` zone, symlinked into `~/.claude/agents/` at install
time for Claude Code's flat agent discovery).

### Reconciliation

After all 14 reports return:

0. **Verify completeness — the gate's self-check.** Before touching findings,
   confirm a JSON response from every one of the 15 anchors (the `auditor`
   field in each payload should cover the set named in Invocation above).
   If any returned an error, no payload, or off-spec output, **re-call that
   single anchor in a new message** before moving to step 1. Never reconcile
   from partial coverage — if any of the 14 didn't audit the plan, the gate
   is open. Two consecutive failures of the same anchor surface as a
   `blocker` ("anchor X failed; cannot close the gate") rather than being
   silently dropped.
1. **Collect** all `findings` arrays.
2. **Dedupe by `tags`** — when two anchors flag the same underlying issue from
   different lenses, present it once and list every anchor that raised it. The
   tag namespace is: `principle:<n>`, `structure:<aspect>`, `role:<slug>`,
   `checklist:<artifact>`, `ts:<id>`, `drift:<pattern>`.
3. **Bucket by severity** — `blocker` (plan won't pass Stage 2/3 or violates a
   principle) gates `ExitPlanMode`; `nit` is non-gating.
4. **Surface blockers one at a time** to the user, per principle #10, with a
   single-question patch-or-override ask.
5. **Apply approved patches** to the plan file (only the main Claude edits,
   never the anchors).
6. **Re-run affected anchors** when a patch touches their domain — e.g.,
   adding a depend after `solution-architect-anchor` flagged it should re-run
   that anchor (and any with `tag:role:solution-architect` overlap) to
   confirm the patch resolved the finding without introducing a new one.
7. **Land nits** in a final summary block appended to the plan file:
   ```
   ## Anchor Pass — Open Nits (<date>)
   - [<anchor-name>] <issue> — <suggestion>
   ```
8. **Call `ExitPlanMode`** once no blockers remain.

### When to skip

- User explicitly asks: `--skip-audit`, "fast-mode", or equivalent. Record at
  the top of the plan: `Anchor pass: SKIPPED on <date> at user's explicit request.`
- Plan is a fix-iteration to an already-anchored plan and the only change is
  in response to a Stage 1/2/3 failure — anchor pass is for plan *decisions*,
  not build-loop fixes.

### Limit

Anchors catch **plan-vs-source-of-truth drift**, not **conversation-vs-plan
drift**. If a decision was deliberated then never landed in the plan, the
anchors catch that as "checklist item with no plan entry" (silent drift). What
they cannot catch is a decision recorded in the plan but contradicted by a
later conversation turn that also never reached the plan — but at that point
the plan itself is wrong and would fail Stage 2/3 anyway. This is acceptable:
the anchor pass is a re-anchor against the plan-as-frozen-document, which is
the artifact `ExitPlanMode` actually gates on.

## Pre-Flight: Instance, Database, Dependencies

Detailed procedures live in [`reference/pre_flight.md`](reference/pre_flight.md). The high-level shape:

- **Section A — Instance + DB scaffold** (only if Q1 named a fresh instance, only on `architecture: local`). Steps A.0 (environment detection) through A.11 (nginx scaffold). All destructive actions gated by user `ExitPlanMode` approval per principle #4.
- **Section B — Dependencies and Environment** (always applies):
  - **B.1 Module dependencies** — list every model touched, resolve owning module, verify each is `state='installed'` in the validation DB before Stage 2.
  - **B.2 Required configuration** — list every `res.groups` / `res.config.settings` toggle the workflow depends on, verify each is enabled in the validation DB before Stage 2.

### Plan-file named sections (required, always)

The plan file must include the following explicit headings — these are the gating surfaces the user reads at `ExitPlanMode`. Missing any of them is what causes destructive work to fire outside of explicit consent.

- **`## Dependencies`** — every module the addon directly uses, one line each (`<module> — <why>`), each verified `state='installed'` in the validation DB before Stage 2.
- **`## Required configuration`** — every `res.groups` / `res.config.settings` toggle the workflow needs, one line each (`<xml_id> — <why> — <UI path>`), each enabled (via `post_init_hook` or operator pre-step) before Stage 2.
- **`## nginx`** — one of:

  - `Scaffold: include_dir = <path>, log_dir = <path>, public URL = https://<host>.internal/, sudo follow-up = ./setup_nginx_sudo.sh` (when a fresh instance is named on Local and the detector reports `nginx.available = true`).
  - `Skip — --no-nginx requested.`
  - `Skip — no nginx include dir detected on this host (proxy_mode = True still written to conf).`
  - `N/A — existing instance / non-Local architecture.`
- **`## Requirements (imported from spec)`** — **required whenever the invocation references a spec folder**; omit entirely otherwise (the interview captured the same content inline). Reproduce into the plan body, with a one-line provenance citation each:

  - the per-workflow **user stories** (spec §5 / SPEC_DATA workflow stories),
  - the **success criteria** (spec §5.{n}.1 / SPEC_DATA `success_criteria`),
  - the **standard-Odoo overlap decisions** (spec §4 / `dev_handoff.overlap_decisions` — `<module> → extend|reuse|build`, with the reason).

  Rationale: the BA, consultant, and solution-architect anchors read **only the plan file**, not the spec. Without this import they flag stories / success-criteria / overlap as "missing" on every spec-driven plan (a recurring false-positive). Importing them makes the plan self-contained for the anchors AND gives the user one place to verify the build matches the spec's intent. This is a self-containment requirement, not a consent gate — but it lives in this list so `plan-structure-anchor` enforces its presence.

Missing deps/groups are caught at `ExitPlanMode` approval, not at Stage 2 failure. Anti-patterns this section prevents:

- troubleshooting #8 ("Addon installs but a core field/menu is invisible — required feature group never enabled")
- troubleshooting #33 ("nginx returns 502 Bad Gateway on a freshly-scaffolded instance")

## Implementation Rules

When you begin coding:

- **Standard Odoo first.** Search `odoo/` and `enterprise/` for prior art; prefer `_inherit` + `<xpath>` over parallel models.
- **Minimal code.** Fewer lines win, as long as correct, secure, and maintainable. No scaffolding for hypothetical future features.
- **Manifest correctness gates everything.** Missing `data` entry, wrong `depends`, demo loaded as data — every one is install-time pain that didn't need to happen.
- **App icons.** "An app" (a tile in the home-menu/app launcher) is a **root `<menuitem>`** — one with no `parent` (`ir.ui.menu.get_user_roots()` = `parent_id = False`), NOT the module. Two distinct concerns, both needed:
  - **Per root menuitem → a launcher icon.** Each parentless `<menuitem>` shows its own tile; its icon is that menuitem's `web_icon="<module>,static/description/<icon>.png"`. **A single addon can declare several root menus → several apps → several icons.** Give each its own image (e.g. `icon.png`, `icon_<app>.png`); they're only visually distinct if they point at different files. A root menu with no `web_icon` renders the generic placeholder.
  - **Module-level (`application=True`) → the Apps-list/store icon** at `static/description/icon.png`. Independent of the launcher: a module can be `application=True` with no root menu, or declare root menus without the flag.
  - **Convention:** a single-app addon points its one root menu's `web_icon` at `static/description/icon.png`, so launcher and store share one file. Multi-app addons need additional icon files.
  - **Style (every icon):** flat **rounded-square**, brand-appropriate solid background, a single simple **white glyph/monogram** for that app's purpose — not clipart, not a photo. Generate with Pillow (the `odoo-mock-design` catalog's `app-icons.svg` is a style reference) or adapt a thematically-related core app's icon, citing the source.
  - A module that only *extends* existing apps (all menus have a `parent`, no `application=True`) needs no icon.
- **Security-first.** No new model without a row in `ir.model.access.csv`. Multi-tenant data needs a record rule.
- **Internal-API only.** Don't reach into other addons' private (`_`-prefixed) methods. If you need a hook, file an issue or wrap a public helper.
- **No orphan references** (principle #7) — every menu, view, action, ACL, demo record this run emits must be referenced or removed. Pre-existing orphans in the addon (introduced by earlier work) get flagged in the plan's Findings section, not deleted, until the user explicitly approves cleanup.
- **Builder mindset** (principle #1) — use a builder when fix-iterations or repeated structure make hand-typing painful. Concretely: scaffolds with >5 models, repeated CSV/XML rows, or generated geometry. Below that, hand-type. A generator longer than the artifact is a smell.
- **Match existing style** (principle #8) — when editing an existing addon, mirror its naming, idioms, file organisation, and indentation. Don't re-style what you're inheriting.
- **Runtime idioms** — before building any wizard, editable list, inline action button, status indicator, or guard on a committed value, consult [`reference/odoo_runtime_idioms.md`](reference/odoo_runtime_idioms.md). These are the defects that pass lint/install/smoke and only break in the live UI.
- **Lifecycle completeness** (principle #15) — every state / commit / lock / reservation the addon introduces is built *with* its inverse (release, restore) and its terminal-state cleanup (cancel / expire frees what was held). A guard protecting a committed value must exempt the system flows that share its code (cancel, unreserve, validate) and block only the manual path.
- **Reconcile against the mock** (principle #16) — when a mock or spec screen exists, diff the implemented interaction (widget, picker-vs-grid, labels, layout) against it before declaring the surface done. The mock's interaction shape is part of the requirement, not a suggestion.

## Three-Stage Validation

Mirror of the pattern from `odoo-spreadsheet-report`. Each stage catches a different failure class. Skipping a stage to "save time" loses time downstream.

### Stage 1 — Static lint ([`_lint_addon.py`](reference/scripts/_lint_addon.py))

Pure-Python walk of the addon directory. No Odoo runtime needed. Validates:

- `__manifest__.py` parses to a single dict with `name`, `version`, `depends`, `data`.
- Every entry in manifest `data` and `demo` exists on disk.
- `security/ir.model.access.csv` exists when models are declared, with required columns; flags models lacking an ACL row.
- Every XML file parses (well-formed XML).
- Best-effort: every `_inherit` target is grep-resolvable in `addons_path`.
- No `print(...)` statements; no syntax errors; no mixed tabs/spaces.

Run before invoking Odoo. Exit non-zero on any error.

### Stage 2 — Install / Upgrade ([`_install_module.py`](reference/scripts/_install_module.py))

Wraps `odoo-bin -i <module>` (auto-switches to `-u` if module already installed). Captures the log and flags suspicious lines (`ERROR`, `Traceback`, `Failed to load`, …). Exits non-zero if the process fails OR if any flagged line appears.

`<version>` below is the selected instance's version folder (`v19`, `v20`, …) — the one `instances[].version` reports for it. All odoo-bin / venv / conf paths route to that version; never assume `v19`.

```
./<version>/odoo/.venv/bin/python skills/odoo-plan-development/reference/scripts/_install_module.py \
    --venv-python ./<version>/odoo/.venv/bin/python \
    --odoo-bin ./<version>/odoo/odoo-bin \
    --conf <version>/instances/<instance>/odoo.conf \
    --db <db> \
    --module <module>
```

### Stage 3 — Operational smoke ([`_smoke_module.py`](reference/scripts/_smoke_module.py))

Runs inside `odoo-bin shell`. Confirms operationally healthy, not just "installed":

1. Module is in `installed` state.
2. Every declared model is searchable.
3. Every menu's action resolves.
4. Sample record creates, computeds populate, unlinks cleanly.
5. Every declared user group exists.
6. Every model has at least one ACL row (warn-only — sometimes intentional).

```
SMOKE_MODULE=<module> ./<version>/odoo/.venv/bin/python ./<version>/odoo/odoo-bin shell \
    -c <version>/instances/<instance>/odoo.conf -d <db> --no-http --stop-after-init \
    < skills/odoo-plan-development/reference/scripts/_smoke_module.py
```

If the addon ships its own tests, also run `--test-tags=/<module>` as a separate Stage 3b.

### Stage 3c — Frontend (OWL / POS) tier (only when the addon ships `static/src` assets)

An OWL frontend — POS control button, popup, custom widget — is **invisible to Stage 1/2/3 and `--test-tags`**; nothing automated drives the JS. A clean install of a module with a broken popup tells you nothing. (A spec flags this early via `dev_handoff.completeness.{wfN}.validation_surface = "owl-frontend" | "mixed"` — when you see it, design the thin-frontend / fat-server split from the start and plan for this tier.) Two complementary checks close the gap:

1. **Server-method shell smoke.** In `odoo-bin shell`, call the exact methods the JS calls, using the JS arg convention, against the live DB — e.g. `env["m"].browse([]).lookup(ref)` and `env["m"].browse([id]).accept(val)` (see `odoo_runtime_idioms.md` § POS / OWL frontends). This proves the server contract the OWL code depends on, including the deny-cases. Because the design keeps business logic server-side (thin frontend / fat guarded methods — `solution_architect.md`), this tier validates *the logic*; only pixels remain manual.
2. **Manual UI checklist** in the testing manual — the steps a human runs in a live session (open POS, click the button, look up, accept, pay), with the deny-cases called out. State plainly in the plan that the OWL UI is not backend-testable; this caveat is accepted, not a gap.

If the live server holds port 8069, pass a free `--http-port=<n>` on test/shell runs — `--no-http` does not reliably prevent the bind.

If a stage fails: fix, regenerate (via builder if used), re-run all stages from the top — never skip Stage 1 just because "I only changed XML."

## Documentation (Always Last)

After all three stages pass:

- `<addon>/doc/user_manual.md` — purpose, primary workflow, field reference (sparingly), edge cases, glossary.
- `<addon>/doc/testing_manual.md` — install command, upgrade command, test command, manual smoke checklist (mirrors Stage 3), uninstall command. Copy-paste-ready.
- `__manifest__.py` `description` — one short paragraph; surfaces in the Apps list.
- Public-method docstrings — one-line summary, parameter types, return type, raises.

See [documentation.md](../_shared/role_checklists/documentation.md) for full structure.

## Production-readiness checklist (before declaring done)

- [ ] **`EnterPlanMode` was the very first tool call of this skill invocation.** Verify in the transcript: there must be an `EnterPlanMode` call before any `Bash`, `Read`, `AskUserQuestion`, or other tool. If absent, the destructive-action guards under principle #4 were not armed and the entire walkthrough ran outside the gate — re-run the skill from scratch with `EnterPlanMode` first.
- [ ] **All 15 anchor responses landed before `ExitPlanMode` was called** (unless `--skip-audit` was honored — see § Pre-ExitPlanMode Anchor Pass · When to skip). Verify in the transcript: every one of the 15 anchor names appears as an `auditor` field in a returned JSON payload, all of them landing in the assistant turn immediately after the single batched Agent-call message. If any are missing or `ExitPlanMode` fired before that turn completed, the gate was open — re-run the anchor pass.
- [ ] Plan file lives at `<repo_root>/plans/<instance>-<functionality>.md` (no leftover `.claude/plans/<random>.md` placeholder, no leftover random-name file at the repo root either).
- [ ] Plan file's **Dependencies** section lists every module the addon directly uses, each verified installed in the validation DB before Stage 2.
- [ ] Plan file's **Required configuration** section lists every `res.groups` / settings toggle the workflow needs, each enabled (via `post_init_hook` or operator pre-step) before Stage 2.
- [ ] Stage 1 lint exits 0.
- [ ] Stage 2 install/upgrade succeeds; no flagged log lines.
- [ ] Stage 3 smoke exits 0.
- [ ] If addon has tests: `--test-tags=/<addon>` exits 0.
- [ ] If addon ships `static/src` (OWL/POS): Stage-3c done — server-method shell smoke passes (JS-facing methods + deny-cases) AND a manual UI checklist is in the testing manual; business logic is in guarded server methods, not the JS.
- [ ] User manual + testing manual present under `<addon>/doc/`.
- [ ] No orphan references (menu, view, action, ACL).
- [ ] **Every root (parentless) `<menuitem>` has a `web_icon`** pointing at an Odoo-style icon (rounded-square, brand colour, simple white glyph) — N root menus need N icons, none on the generic placeholder. If `application=True`, `static/description/icon.png` (the Apps-list/store icon) is also present.
- [ ] Multi-tenant models have `company_id` + record rule.
- [ ] Cron jobs (if any) have batch limits and try/except.
- [ ] Public routes (if any) have CSRF posture, rate-limit, sanitisation reviewed.
- [ ] Manifest `version` reflects any migration script that must run.
- [ ] `reference/troubleshooting.md` updated **if the write gate passes** (skills tree is git-cloned with push access, OR not git-cloned at all — see [`../_shared/principles.md` § 6](../_shared/principles.md)) with any new failure mode hit during the run (4-line format, grep-first to avoid duplicates); if the gate fails (cloned without push), the entry was surfaced to the user without writing. `../_shared/scripts/_lint_troubleshooting.py --skill odoo-plan-development` exits clean.

## Iteration Etiquette

Per principle #8. Skill-specific notes:

- When the user reports an install failure, never disable hooks or constraints (`--no-http` is fine; `--without-demo`, `--no-tests`, schema bypasses are not) unless explicitly authorised.
- When the user reports a render bug, run Stage 3 smoke first — it often reproduces immediately and points at the exact line.
- When you've fixed something, regenerate via the builder (if used), re-run all three stages, then tell the user **what specifically changed and why** in concrete terms. They need a reason to retest.

---
