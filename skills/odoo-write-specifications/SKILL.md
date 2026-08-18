---
name: odoo-write-specifications
description: Produce a professionally formatted Odoo functional specification as a .docx file for hand-off to a development team. Interviews business and technical stakeholders one question at a time and **drafts the document to disk incrementally** as each section's input lands — no plan mode, no end-of-interview cliff. After the interview, runs a 14-anchor parallel quality review against the docx draft; user accepts/rejects findings; final docx lands at <repo_root>/specifications/. The spec serves both audiences — business stakeholders sign off on the workflow shape; developers pick it up as the input to odoo-plan-development.
when_to_use: Use this skill when the user wants a written Odoo functional specification (typically pre-development, often pre-contract) — NOT when they want code built. The next step after this skill is odoo-plan-development against the same scope.
allowed-tools: Read, Edit, Write, Bash, Grep, Glob, Agent, Skill, AskUserQuestion, ToolSearch, TodoWrite
---

# Specification Development

Turn a business request into a `.docx` functional specification suitable for hand-off to a development team. The audience is **both business and technical** — procurement officers and finance managers read the same document the developers later use as the input to `odoo-plan-development`. Skill-specific discipline below; cross-cutting principles live in [`skills/_shared/principles.md`](../_shared/principles.md) and apply here too.

This skill is **documentation-only**. It produces a Word document, not deployable code. No `instances/` to scaffold, no `createdb`, no `odoo-bin` calls.

## Entry: Incremental drafting (no plan mode)

**Do NOT call `EnterPlanMode` at any point during this skill, ever.** If you feel the urge to summarise an approach before acting, write that summary as a reflection in your reply and proceed — the on-disk docx is the gating artefact, not an `ExitPlanMode` prompt. If you read `_shared/principles.md` mid-run and notice P11 telling interactive planning skills to enter plan mode, **this skill carves out an explicit exemption** (next paragraph); the carve-out overrides the default for this skill specifically.

**Plan mode is deliberately skipped.** Per shared principle #11, interactive planning skills *normally* enter plan mode on first iteration — but this skill draws an explicit exemption. The reasons:

- **No destructive actions to gate.** The skill writes only to `<repo>/specifications/` (its own output folder, never destructive per P4). No DB writes, no module installs, no `git push`.
- **The docx grows with the interview.** Each answered question maps directly to a section the skill can write *now*; nothing has to wait for an end-of-interview compile. The user gets a visible draft early instead of an `ExitPlanMode`-cliff payoff.
- **A long interview is friendlier when it's visibly producing something.** Multi-workflow specs run 30+ pages across 5+ workflows — a 60-minute interview before the user sees a single page is bad UX.

See the P11 exemption note in [`../_shared/principles.md`](../_shared/principles.md) for the shared-principle carve-out.

**Architecture detection (principle #13) is also skipped.** This skill produces a `.docx`. The host architecture doesn't affect the artifact's shape. The spec *content* may reference target architecture (`Odoo.sh` vs Local) inside Section 2, but that's authored by the user during the interview — never detected by the skill.

**Do not open with "what do you want to do?"** — the skill's first question is always Q1 (Task code).

### How incremental drafting works

The flow on invocation runs **six questions in logical order — identify, brief, frame, enumerate**:

| # | Question | Mode | Why this position |
|---|----------|------|---|
| Q1 | Task code | **Free-text — NOT `AskUserQuestion`.** Plain prose ask, free-text reply. See § Free-text carve-outs below. | Identification — locks part 1 of the docx filename. Asked first because everything downstream filenames off it. |
| Q2 | Client name | **Free-text — NOT `AskUserQuestion`.** Plain prose ask, free-text reply. See § Free-text carve-outs below. | Identification — locks part 2 of the docx filename. |
| Q3 | Odoo version | `AskUserQuestion`, version-list (Recommended from active venv + 1–2 alternatives) | Framing — single-line Section 1. |
| Q4 | Type of development | `AskUserQuestion`, multi-select (New App / Extension / Enhancement / Migration) | Framing — informs Section 4 wording (reuse-vs-net-new). |
| Q5 | **Business need brief** | **Free-text — NOT `AskUserQuestion`. See § Free-text carve-outs below.** | The "what's the problem, who has it, why it matters" — the substance of the whole spec. The user types a paragraph; the skill parses it into Business Case row entries AND derives the slug. Asked after framing because the slug auto-derives from the brief and locks the spec folder. |
| Q6 | Workflows (count bucket, then names) | `AskUserQuestion`, buckets 1 / 2–3 / 4–5 / 6+, then list | Enumeration — drives Section 5 table + the per-workflow deep-dive. |

After every answered question, the builder re-runs and writes the corresponding section into the on-disk docx. The user can open the file in Word/Pages between answers and watch it grow.

**Spec folder lock happens after Q5.** Q1 + Q2 + the slug auto-derived from Q5 give the skill everything it needs to commit a final folder name; the docx (which was `_draft.docx` during Q1/Q2/Q3/Q4/Q5) is renamed atomically. Q6 writes into the now-locked folder.

After Q6 lands:

7. **Critical Brief Evaluation** (see § Critical Brief Evaluation below). Pause and critique Q5+Q6 against principle #12 and the Consultant checklist — surface scope-sanity, standard-Odoo-overlap, value-clarity, and complexity-vs-value concerns **one ask at a time, every ask through `AskUserQuestion`** (no bundling — see § Interview discipline). Revisions land back in Q5 / Q6 / Section 4 (Apps Impacted) before the per-workflow deep-dive starts.
8. **Per-workflow role deep-dive.** For each workflow in the (possibly revised) Q6, the role checklists drive a focused interview. Each role question answered → corresponding subsection populated → builder re-runs → docx on disk reflects the new content immediately. **Every role question is a single `AskUserQuestion` call.** Never bundle two sub-questions into one ask.
9. **Post-interview anchor pass** (see § Post-Interview Anchor Pass below). Quality review, not a gate.
10. **Final lint + visual review.** The user opens the docx, scans, declares done.
11. **Offer mock screens** (see § Offer mock screens (finish line) below). After the docx is accepted, ask once whether the user wants interactive visual mocks of the proposed screens; if yes, hand off to `odoo-mock-design`.

No `EnterPlanMode`/`ExitPlanMode` calls. The docx itself is the working artifact AND the deliverable.

## Output Contract

Produce, in this order:

- **`specifications/` directory** at the repo root — created by the Write tool on first run if it doesn't already exist.
- **One folder per spec** at `<repo_root>/specifications/<task-code> - <client-name> - <3-word-functionality>/`. Each spec is self-contained inside its own folder. Spaces in folder name are allowed and expected; slashes / colons / asterisks are rejected by the filename safety check.
- **The Word file** lives at the **root of the spec folder**: `<repo_root>/specifications/<task-code> - <client-name> - <3-word-functionality>/<task-code> - <client-name> - <3-word-functionality>.docx`. Opening the spec folder in Finder / Explorer shows the docx and a single `_reference/` subfolder — nothing else clutters the view.
- **Python builder + supporting files** live under `<spec-folder>/_reference/`:
  - `_build_<task-code>.py` — the python-docx builder with the SPEC_DATA dict for this task. Source of truth per principle #1; the docx is regenerated from it on every iteration. Hand-edits to the docx vanish on next regen.
  - `odoo-logo.png` — **copy the skill's [`reference/assets/odoo-logo.png`](reference/assets/odoo-logo.png) into `_reference/` when you move the builder in.** The builder embeds it in the running header and on the cover (Odoo template styling); it looks for the logo as a sibling first, then falls back to the skill's `assets/`. If it's genuinely absent the build still succeeds, just without the logo (graceful degradation).
  - Rendered diagram PNGs (`<task-code>-wf<N>-bpmn.png` / `-flow.png`) are regenerated here on every build; never hand-edit them.
  - The underscore-prefix on `_reference/` is intentional: it visibly marks the folder as "supporting files, not the deliverable" while staying cross-platform-friendly (no dotfile semantics). Future supplementary inputs (the original brief PDF, screenshots, stakeholder emails) drop into the same folder.
- **Spec folder lock happens AFTER Q5 (business need brief) lands.** Q1 (task code) and Q2 (client) are asked first and consecutively as **free-text plain-prose asks** (see § Free-text carve-outs — NOT `AskUserQuestion` turns); the docx writes to `_draft.docx`. Q3 (Odoo version) and Q4 (type of development) land via `AskUserQuestion` while the docx is still `_draft.docx`. Q5 is the **free-text business-need brief** (also see § Free-text carve-outs — NOT an `AskUserQuestion` turn). Once Q5 lands the skill **auto-derives the 3-word kebab functionality slug** from the brief (see § Slug derivation), creates `<spec-folder>/_reference/`, moves the builder in, and renames `_draft.docx` to the final filename. No user question is asked for the slug.
- **Interactive interview** — one `AskUserQuestion` turn at a time per principle #10, with 2–4 options drawn from the relevant role checklist + implicit Other (Q1, Q2, and Q5 are the free-text exceptions — see § Free-text carve-outs). After **every** answered question post-Q5, the builder re-runs and the docx is updated on disk. The user sees the document grow live.
- **Post-interview anchor pass** — fires the full 14-anchor set in parallel against the on-disk docx (per § Post-Interview Anchor Pass below). Findings come back as severity-graded suggestions; the user accepts or rejects each blocker; the skill applies approved patches and re-runs affected anchors.
- **Stage 1 lint** + **Stage 3 visual review** as the final exit checks (see § Validation below).
- **Optional `mocks/` subfolder** — if the user accepts the finish-line offer to visualise the screens, `odoo-mock-design` writes a self-contained interactive HTML mock to `<spec-folder>/mocks/` (see § Offer mock screens (finish line)). The docx remains the primary deliverable; the mock is a companion. Absence of `mocks/` never fails the contract.
- **Optional `dev_handoff` key in SPEC_DATA** — a top-level key inside the builder's SPEC_DATA dict carries structured context for the downstream `odoo-plan-development` skill (P12 inferences, lifecycle/contention decisions, per-workflow validation surface, process-skip markers, integration surface, dataset scale, standard-Odoo overlap decisions). **The builder ignores this key**, so nothing renders to the docx — the docx stays clean for stakeholders while plan-dev consumes the structure directly from `_reference/_build_<task-code>.py`. Absence of `dev_handoff` never fails the contract; see § Dev-Only Hand-off to odoo-plan-development.

A docx that's missing any of the **5 numbered top-level sections** (or the Table of Contents front-matter page), lives outside its per-spec folder, has placeholder strings (`TODO`, `TBD`, `Lorem ipsum`), or fails the filename convention does NOT satisfy the contract.

**Document outline shape** (front matter unnumbered; sections 1–5 numbered):

1. Cover *(front matter)*
2. Table of Contents *(front matter; **populated** — Heading 1–3 titles + page numbers rendered on disk, clickable, page numbers refresh on open. NOT a blank "right-click to update" field — see `content_outline.md` § Table of Contents)*
3. `1. Odoo Version`
4. `2. Business Case`
5. `3. Apps Impacted / New Apps Proposed` — both sub-tables now widened to 3 cols: `3.1 Impacted Standard Apps — App | Objective | Functional changes`; `3.2 New Custom Apps — App | Objective | Key capabilities`. **Stay abstract**: each row is one impact area or capability abstraction (e.g. "in-transit modelling between cities", "back-end approval gating") — never a list of fields / menus / models / groups (those belong in §5 per-workflow). If a cell needs more than two distinct items, collapse to the abstraction or it duplicates §5.
6. `4. Functional Layout — Workflows`
7. `5. Per-Workflow Detail` — workflows are `5.{n} <name>` and each of the **11** subsections is `5.{n}.{1..11}` (Success Criteria is the new subsection #1 per workflow; see § Per-Workflow Role-Based Deep Dive). No top-level Success Criteria, no Glossary appendix.

## Reference Material (Read Before Building)

- [`skills/_shared/principles.md`](../_shared/principles.md) — cross-cutting discipline. Read first.
- [`reference/content_outline.md`](reference/content_outline.md) — cover + Table of Contents + 6 numbered top-level sections × 10 per-workflow subsections, canonical structure including the numbering scheme. Stage 1 lint reads this as the source of truth.
- [`reports/industry_standards_audit.md`](reports/industry_standards_audit.md) — point-in-time audit of the skill against IEEE 830 / 29148 / BABOK / Volere / Agile / Odoo conventions. Tiered improvement backlog + concrete sample renderings based on Pilot01. Snapshot reference, NOT canonical structure — consult before proposing structural changes; re-audit when the docx outline shifts materially.
- [`reference/docx_styling.md`](reference/docx_styling.md) — fonts, palette, spacing, table styles. The 7 C's of communication enforced at the visual layer.
- [`reference/samples/reference_pattern.md`](reference/samples/reference_pattern.md) — annotated walk-through of a real-world reference spec. The shape and depth to emit; never copy verbatim.
- [`../_shared/role_checklists/*.md`](../_shared/role_checklists/) — the eleven role disciplines. The per-workflow interview pulls its questions from here. Re-used, not duplicated.

## Pre-Flight: Tooling

`python-docx` is always required. `Pillow` is required only when a workflow opts into a BPMN diagram. `python-docx` is declared in this skill's [`requirements.txt`](requirements.txt), which the repo bootstrap installs (`find <corpus_dir> -name requirements.txt -exec pip install -r {} \;`) — so on a bootstrapped container its check below should pass; the check stays in place for hand-run / bare-venv invocations. `Pillow` is not declared there because Odoo already pins it.

**`python-docx`** — check at skill entry. This skill is documentation-only (no instance / no version routing), so it just needs *an* Odoo dev venv with `python-docx`. `v19/odoo/.venv` is shown throughout as the concrete example — substitute whichever version folder exists (`v20/odoo/.venv`, …); any of them works.

```bash
./v19/odoo/.venv/bin/python -c "import docx" 2>&1
```

If the import fails, surface the install command and gate it behind explicit user confirmation per principle #4: `./v19/odoo/.venv/bin/pip install python-docx`. Builder fails fast with `ModuleNotFoundError` if invoked without it — no silent fallback to plain-text output.

**`Pillow`** — Pillow ships with Odoo's `requirements.txt`, so it's already present on any Odoo dev venv and on Odoo.sh. Bare-Python-venv invocations are the only realistic miss. Check happens at the **Diagram-choice checkpoint** (after Q6, see § Diagram-choice checkpoint) — not at skill entry, because BPMN need is content-dependent. The checkpoint runs the import-test, prompts to install via `AskUserQuestion` per P4 if missing, or demotes BPMN choices to `flow_strip` on decline. The builder also raises `ImportError` defensively at use-site as a safety net.

## Fixed Questions (Ask In This Order)

### Interview discipline — invariant for the entire skill

**This block is the non-negotiable invariant for the entire skill — not just the Fixed Questions section.** Every interactive moment in this skill — fixed questions, slug confirmation, brief critique, per-workflow role deep-dive, anchor-pass reconciliation — obeys it. Per principle #10:

1. **One atomic question per turn.** Never bundle sub-questions. "What's the task code AND client?" is two asks, not one. "Which lots can be picked, and how should they sort?" is two asks. If a `?` is followed by ` and ` or ` plus ` or a second `?`, it's bundled — split it.
2. **Interview mode by default — `AskUserQuestion` for every question.** Every question goes through the `AskUserQuestion` tool with 2–4 concrete options drawn from the relevant checklist, plus implicit Other for free-text. Plain-text questions in user-facing prose are violations, regardless of how rhetorical they feel. **EXCEPTIONS**: Q1 (task code), Q2 (client name), and Q5 (business need brief) are the only standing free-text questions in the entire skill — see § Free-text carve-outs below. No other exceptions exist; if you are tempted to ask a free-text follow-up outside these three, you are violating this rule.
3. **Free-text opt-in is per-question, on user signal only.** "Let me write a paragraph" opts out for ONE question; resume `AskUserQuestion` for the next. The opt-out doesn't propagate.
4. **Reflect briefly between asks — never combine reflection with the next question.** 1–2 sentences summarising the previous answer, then a NEW `AskUserQuestion` call for the next ask. The reflection and the next ask are separate turns.

The drift this invariant prevents: bundling appears at *transitions* — moving from one section to the next, or after a long reflection block, where the model is tempted to "just also confirm one more thing while I'm here." Don't. Make the next ask its own turn.

### Free-text carve-outs (Q1, Q2, Q5 — exceptions to interview mode)

Three questions in the entire skill bypass `AskUserQuestion` and ask plainly in assistant prose; the user replies with free-text. Every other question stays interview-mode (one `AskUserQuestion` turn each).

**Q1 (Task code) and Q2 (Client name)** are short free-form identifiers. There is no useful option set to draw from: placeholder chips would either anchor on past projects (drift — the model picks up `KAY-014` from memory and the user has to override) or be obvious noise the user has to dismiss every time. A plain ask + free-text reply is the right shape.

- **Q1 ask shape** (paste verbatim or paraphrase): *"What's the task code for this spec? Any short identifier you use to track this work — typically a short prefix + dash + sequence. I'll use it as the first segment of the docx filename, so it can't contain `/`, `:`, `*`, or `|`."*
- **Q2 ask shape**: *"Who's the client? Use the company or organization name as you'd want it to appear in the docx — I'll use it as the second segment of the docx filename."*

Apply the filename safety check (no `/ : * |`) to Q1's reply; if it fails, re-ask. Do not pre-fill, suggest, or carry forward a value from memory or a prior spec — the user supplies the real identifier directly. No `res.partner` lookup for Q2 (the on-disk demo data is noise, not signal).

**Q5 (Business need brief)** is also free-text but a different shape: a paragraph or two of narrative rather than a short identifier. Why: the business need is the substance of the whole spec — problem, who has it, why it matters, what changes if we don't fix it. Trying to bucket that into 4 multi-choice options is the wrong shape; the user has the narrative in their head, the skill needs the narrative, and forcing a multi-choice ask costs information.

- **Q5 ask shape**: *"Tell me the business need in your own words — what's the problem, who's living with it, and why it matters. A paragraph or two is enough; I'll parse it into the Business Case section."*

The skill then parses the reply into three Business Case dimensions (problem / affected role / why it matters), uses the same parse to auto-derive the slug, and proceeds to Q6.

**Interview mode resumes at Q3 / Q4** (between the identifier asks and the brief) **and at Q6 onward** — `AskUserQuestion` is the default for every other turn in the entire skill.

### Necessity filter (P12) per question

Before asking each question: is the answer inferable from the invocation, an on-disk artifact, or a read-only pre-flight? Would the answer materially change the spec? If either gate fails, skip and append the inference to `dev_handoff.assumptions` in SPEC_DATA (see § Dev-Only Hand-off to odoo-plan-development) — `{question, inferred, source}`. The docx stays clean; the inferences travel to plan-dev structurally rather than as a docx appendix. If the user wants to see the running set during the interview, point them at `_reference/_build_<task-code>.py`.

Tie cases (two interpretations roughly equally plausible) surface alternatives + ask per P12's tie-case rule — never silently pick.

### Q1 — Q2: Identification

**Q1. Task code.** **Free-text plain-prose ask — NOT `AskUserQuestion`** (see § Free-text carve-outs). Apply the filename safety check on the reply: no slashes, colons, asterisks, or pipes — if any are present, re-ask with a one-line "that character isn't allowed in filenames, please retype" note. Do not pre-fill, suggest, or carry forward a code from memory or a prior spec; the user supplies the real value directly.

**Q2. Client name.** **Free-text plain-prose ask — NOT `AskUserQuestion`** (see § Free-text carve-outs). Use the value the user types directly as part 2 of the docx filename. Do not look up `res.partner` for option suggestions, and never carry a real client name forward from memory — the user names the client.

### Q3 — Q4: Framing

**Q3. Odoo version.** `AskUserQuestion`. Options: the version implied by the active venv's `release.py` as the first (Recommended) option, plus 1–2 plausible alternatives (17 / 18 / Online). Renders as the single-line Section 1 of the docx (just the version number, no paragraph).

**Q4. Type of development.** `AskUserQuestion`. Options: New App / Extension of standard Odoo / Enhancement to existing custom / Migration. Section 4 of the docx expands the chosen category into the reuse-vs-net-new wording; multiple categories may apply (`multiSelect: true`).

### Q5: Business need brief (free-text — see carve-out above)

**Q5. Business need brief.** **Free-text only — no `AskUserQuestion`.** The user types a paragraph or two. The skill parses the response into the three Business Case dimensions (problem / affected role / why it matters) AND uses the same parse to auto-derive the slug.

Ask shape (paste verbatim or paraphrase): *"Tell me the business need in your own words — what's the problem, who's living with it, and why it matters. A paragraph or two is enough; I'll parse it into the Business Case section."*

If the user's reply is ambiguous on one of the three dimensions, the skill follows up with a single targeted `AskUserQuestion` turn for that dimension only — never bundle. Example: brief gives strong problem + affected-role signal but no "why it matters" → one `AskUserQuestion` ask for why-it-matters, with options drawn from [consultant.md](../_shared/role_checklists/consultant.md). Other dimensions stay derived from the brief.

**Optional `out_of_scope` row.** If the user volunteers a scope boundary in the Q5 brief (or the Critical Brief Evaluation Check 1 narrows scope and the user explicitly states what fell out), the skill writes that as a fourth `business_case.out_of_scope` row in SPEC_DATA. The builder renders it as a fourth row in the §2 Business Case table (`["Out of scope", <statement>]`); when the field is absent the §2 table stays at three rows. Never invent an out-of-scope row — only write it when the user explicitly bounded scope.

### Slug derivation (auto, post-Q5 — no question is asked)

The functionality slug — used as the third segment of the spec-folder name and the docx filename — is **derived silently** by the skill once the Q5 brief has landed. **No `AskUserQuestion` turn is spent on the slug.** The user is told what the skill derived as part of the reflection between Q5 and Q6; nothing to confirm, nothing to choose.

**Derivation rule.** Take the principal noun + the principal verb from the Q5 brief's problem statement, plus an optional qualifier from the affected-role or domain signal. Compose 2–3 lowercase words, hyphen-joined, ≤30 chars total. Filename-safe characters only (`[a-z0-9-]+`).

Examples:

| Q5 brief signal (problem + role) | Derived slug |
|---|---|
| Sales reps cannot pick a specific lot/serial on a Sales Order line | `sale-lot-selection` |
| Stock transfers need a manager approval step before posting | `approved-stock-transfers` |
| Partner credit limits aren't blocking confirmation on Sales Orders | `partner-credit-hold` |
| Subscriptions need a custom billing cycle for our distributor channel | `distributor-billing-cycle` |

If two candidate slugs are equally plausible the skill picks one and proceeds — slug is mechanically reversible (the spec folder + docx are renamed atomically if the user objects later). It is **not** a question.

The reflection between Q5 and Q6 surfaces the derived slug inline: *"Locking the spec folder as `<task-code> - <client> - <derived-slug>/`. Renaming `_draft.docx` to the final filename now."*

**Drift guard.** If you find yourself drafting an `AskUserQuestion` to confirm the slug ("I've derived `sale-lot-selection` — OK?"), **stop**. The slug is mechanically reversible — if the user objects later, rename the folder + docx atomically. A confirmation turn here is exactly the courtesy-driven extra ask the carve-out exists to suppress. Announce the slug as part of the reflection, proceed to Q6.

### Q6: Workflow enumeration

**Q6. How many distinct business workflows does this development cover?** `AskUserQuestion`. Options: 1 / 2–3 / 4–5 / 6+ — choose the bucket, then list the names (one ask per turn — the bucket pick and the name list are two separate `AskUserQuestion` calls). The reference pattern has five; most specs land between 1 and 8. Each named workflow becomes a row in the Section 5 workflows table AND a sub-section under Section 6 (Per-Workflow Detail). The Section 5 summary for each workflow is **10–12 words**; no block diagram.

> **When the skill is *proposing* the workflow decomposition** (the delegated-brief case — the user said "you draft it"), the rigid count-then-names two-step is awkward: you already know the candidate workflows. Collapse it into a **single scope-shaped `AskUserQuestion`** whose options are concrete workflow-set choices (e.g. "Report only (1 WF)" / "Report + expected-date field (2 WF)" / "Report + field + config (3 WF)"), each describing exactly what's in scope. That one ask settles both count and names, and doubles as Critical-Brief-Evaluation Check 1 (scope sanity).

After Q6, **pause and critique the brief** — see § Critical Brief Evaluation below — *before* opening the per-workflow role-based deep dive.

## Critical Brief Evaluation (post-Q6, pre-deep-dive)

The skill's job is not transcription. After Q6 lands the workflow list, **pause and challenge the brief** before going into per-workflow detail. The doctrine is principle #12 ("push back when warranted") + the Consultant checklist's anti-Salesforce stance ("'Just like X but tailored for us' — usually a sign the standard module would fit with config"), operationalised here as one to four targeted asks.

The skill runs four checks against the Q5 brief + Q4 + Q6's accumulated answers; surface only the ones where the answer trips a concrete trigger. If all four come back clean, skip this section silently. **Honest passes happen** — a single tightly-scoped workflow against a focused brief is the most common clean-pass case. Do not manufacture concerns to justify running the section; an empty critique on a clean brief is the right outcome.

Each ask is **one `AskUserQuestion` turn** per the interview invariant (§ Interview discipline) — never bundle critiques. "We have a scope-sanity concern and also a standard-Odoo-overlap concern" is two asks, in two turns, with reflection on the first answer landing before the second ask is posed. The user can accept the concern (which may revise Q5 or Q6 in place), explain why the concern doesn't apply (which gets noted on the relevant per-workflow Success Criteria subsection), or override (which is acknowledged inline in Section 3's "Apps Impacted" reuse-vs-net-new wording — no separate appendix).

### Check 1 — Scope sanity

**Trigger**: number of workflows in Q6 disproportionate to the Q5 brief's problem scope. E.g., Q5 frames "manual rework around credit holds" (focused) and Q6 names 5 workflows.

**Ask**: "Q6 lists N workflows for what the Q5 brief framed as a focused problem. Either (a) the problem is broader than the brief captured — revise the brief + keep N workflows, or (b) only 1–2 of these workflows are core to the stated problem — narrow Q6. Which?"

Force a choice. "Both" is not an answer. The spec scope is what's in Q6 at the end of this check.

### Check 2 — Standard-Odoo overlap

**Trigger**: a workflow's described functionality already exists in standard Odoo. **Run `python3 skills/_shared/scripts/_check_odoo_source.py --models <every standard model named in Q5/Q6 / overlap candidates>` once before this check fires** — its output is the source of truth for module ownership / edition / existence. `exists=false` halts the check (ask the user to clarify the model name); `dev_handoff.overlap_decisions[].module` MUST be the script's resolved module, never inferred from memory. Examples to recognise:

- "credit hold / credit limit" → `res.partner.credit_limit` + the standard credit-control flow already cover the common case.
- "lot / serial tracking" → `stock.lot` + `stock.group_production_lot` already cover this once the feature group is on.
- "appointment booking" → the enterprise `appointment` module already covers calendar + bay scheduling.
- "approval workflow" → `studio.approval.rule` / `web_studio` covers the standard approval pattern.
- "expense reimbursement" → `hr_expense` covers it.
- "subscription billing" → `sale_subscription` covers it.

**Ask**: "Workflow X overlaps with standard Odoo's `<module>`. Options: (a) **use standard Odoo as-is**, with a one-line 'configuration only' note in Section 4; (b) **extend the standard module** with a small custom addon — usually the right answer; (c) **build custom from scratch** — only if you can name a concrete reason standard Odoo doesn't fit. Which?"

The Consultant checklist's pitfall reminder applies here: usually a "Just like X but tailored for us" framing means the standard module would fit with configuration. Push back unless the user surfaces a genuine fit gap.

### Check 3 — Value clarity

**Trigger**: a workflow's stated outcome doesn't tie cleanly to the "why it matters" clause of the Q5 brief. The self-test: write a one-sentence "this workflow exists because `<Q5 why-it-matters clause>`" for every workflow in Q6. If you can't, surface the gap.

**Ask**: "Workflow Y doesn't connect to the reasons captured in the Q5 brief's why-it-matters. Either tighten Q5's why-it-matters to include the outcome Y delivers, or drop Y from scope. Which?"

### Check 4 — Complexity vs value

**Trigger**: a workflow looks heavy for what the business case describes as routine. This check usually triggers mid-deep-dive (you can't tell a workflow is heavy until the role questions accumulate user stories + new fields), not at the post-Q6 moment. When it triggers, pause the deep-dive and ask.

**Ask**: "Workflow Z has accumulated `<N>` user stories + `<M>` new fields — that's a multi-week build for what the Q5 brief framed as a routine optimization. Is the impact worth the build, or should we narrow Z?"

### Check 5 — Logical-consequence catch (reason from invariants, don't pattern-match)

Checks 1–4 are trigger-and-example driven — they fire when a named pattern matches. This one is different: it is a **reasoning pass**, not a lookup, and it is the check that catches the gaps no example in this file names. The recurring failure is not "the skill lacked an example" — it is "the skill never reasoned forward from what the feature logically *entails*." Two flavours, both caught by thinking through consequences rather than matching a pattern:

**(a) Domain-invariant consequences.** Name the platform objects the feature touches, recall each object's **hard invariants** (the facts that are *always* true of it in Odoo), and for every invariant the brief is silent on, raise a question. The invariant forces the question — you don't wait for the user to volunteer it.

- The method, not the list: `feature touches object X → X has invariant I → does the brief answer what I implies? → if not, ask.`
- Illustrative invariants (**NOT exhaustive** — derive the ones *your* feature actually touches; do not treat this as a checklist to match): stock / lots / quants are **location- and warehouse-scoped** (any lot / serial / availability feature must answer "scoped to which warehouse / location?"); monetary amounts are **currency- and company-scoped**; quantities must **reconcile** (the parts sum to the whole); dates have **ordering** (start ≤ end); a record's **company** constrains the companies of every record it points at; tracked products are **lot-or-serial**, never both.
- The tell that you skipped this: the *user* surfaces a scoping or consequence question you should have asked ("shouldn't this consider warehouse?"). When that happens, the fix is to add the **invariant class** to your reasoning, not just patch in that one example.

**(b) Action-guard completeness.** For **every state-changing action** the workflow introduces or relies on (Confirm, Validate, Post, Approve, Assign, Reserve, …), ask: *what happens when its precondition is not met?* Each gated action needs its unmet-precondition path written into **Business Rules & Validations** and surfaced as a negative-path user story — never left implicit. Enumerate the actions first, then walk each one's failure case; "the happy path works" is not coverage.

- The method: `list every state-changing action → state each one's precondition → write the error / guard path for when that precondition fails.`
- The tell that you skipped this: a Business Rule exists for the *success* condition but there is no rule or message for the action firing while that condition is unmet (e.g. a rule says "all units must be allocated to confirm" but nothing says what the user sees when they press **Confirm** on an unallocated line).
- Like Check 4, (b) often can't be fully walked until the deep-dive has enumerated the actions — re-run it as user stories accumulate.

**(c) Lifecycle-inverse & contention completeness.** For **every commit / lock / reservation** the workflow introduces (reserve a lot, lock a field after confirmation, claim a unit), reason forward to its *whole* lifecycle — the brief almost always gives the forward action and is silent on the rest. (principle #15 + #16)

- The method: `for each commit/lock/reserve → what RELEASES it (cancel, unreserve)? what RESTORES it (stock becomes available again)? what does the TERMINAL state (cancel / expire / done) do to it? can ANOTHER document claim the same unit — and what frees a stale claim?`
- Each answer lands in an **existing** subsection — inverse behaviours in **Automated Behaviours**, lock and contention rules in **Business Rules & Validations** — never a new section; `N/A — <specific reason>` when the workflow commits / locks / reserves nothing.
- The tell that you skipped this: the spec says "on confirm the chosen lots are reserved" but never says what *cancelling* does to that reservation, or whether two quotations can reserve the same serial.

Surface each gap as a single `AskUserQuestion` per the interview invariant. A clean pass is valid — but here "clean" means you *reasoned through* the invariants, the action guards, and the lifecycle inverses and found nothing open, **not** that you skipped the reasoning because no Check-2-style trigger fired.

### Where the critique outputs flow

The critical evaluation **amends Q5 and Q6 in place**. The docx reflects the post-critique state. There is no separate "what we critiqued" section in the docx — that would be process noise.

What lands where:

- **Q6 (revised)** — workflow list may shrink or grow; the per-workflow detail follows the final list.
- **Q5 (revised)** — business need brief may tighten to reflect what was kept in scope; the Business Case table (Section 2) and the per-workflow Success Criteria subsections rebuild from the revised brief.
- **Section 4 (Apps Impacted)** — natural home for "we use standard X for this; we extend Y for that". The wording must make explicit what's reused vs net-new (e.g., "Sales — standard Odoo flow, no changes" vs "Sales — extended to support serial-selection at the SO line").
- **User overrides on Check 2** (chose custom despite standard-Odoo overlap) are folded into the Section 4 "Apps Impacted" wording rather than a separate appendix — e.g., `Sales — extended despite overlap with standard credit-hold flow; reason: <user-supplied>`. The Open Nits appendix was removed per the conciseness pass.

### When to skip

- **User explicitly asks**: `--skip-critique`, "fast-mode", or equivalent. Record under `dev_handoff.process_log.critique_skipped = '<YYYY-MM-DD>'` in SPEC_DATA (see § Dev-Only Hand-off to odoo-plan-development) so plan-dev knows the critique wasn't run on its inputs. The docx stays clean — no top-of-document SKIPPED banner. Mirrors the anchor-pass skip convention.
- **Iteration on an already-critiqued spec** (re-running on the same task code with unchanged Q5/Q6) — the critique was done the first time; skip silently. If Q5 or Q6 changed since the first pass, re-run.

### What this is NOT

- **Not the anchor pass.** Anchors come AFTER the per-workflow walkthrough, audit the on-disk docx against role checklists. The critique comes BEFORE per-workflow deep-dive, audits the BRIEF against principles + Consultant logic.
- **Not paternalistic.** The user always decides. The skill surfaces concerns; the user picks. The output is a more honest spec — not a smaller one by default.

## Diagram-choice checkpoint (post-critique, pre-deep-dive)

Surface the per-workflow Process Flow diagram choices in a single inventory before opening the per-workflow walkthrough. Makes the BPMN-vs-flow_strip-vs-none decision explicit and overridable instead of an opaque agent judgement.

**Heuristic** — for each workflow named in Q6 (post-critique state):

- **BPMN** if ≥2 actors OR a non-linear flow (decision gateway, error / branch / loop)
- **flow_strip** if 1 actor and ≥3 sequential steps with no branching
- **none** otherwise (1 actor, ≤2 steps, or non-sequential / stateless)

**Pillow pre-flight + install gate** — only if the computed inventory includes ≥1 BPMN. Pillow ships with Odoo's `requirements.txt`, so present on any Odoo dev venv / Odoo.sh; the missing-Pillow case is the bare-Python-venv invocation.

1. Run `./v19/odoo/.venv/bin/python -c "import PIL" 2>&1`.
2. **If import succeeds**: proceed to the accept-or-override ask.
3. **If import fails**: `AskUserQuestion` per P4 (pip install mutates the venv) with two options:
   - **Install Pillow now** — run `./v19/odoo/.venv/bin/pip install Pillow` via Bash, then proceed with the original inventory.
   - **Skip Pillow** — demote all BPMN entries in the inventory to `flow_strip` (call out the demotion in the narration); proceed with the demoted inventory.

The `ImportError` in `render_bpmn_image` (build-time) is the defensive safety net for skill-bypass paths — it should not fire when this checkpoint is honoured.

**Accept-or-override ask** — narrate the (possibly post-demotion) inventory in one block, then ask ONCE via `AskUserQuestion`:

> *"Based on workflow shape, planned diagrams: Workflow 1 (3 actors, gateway) → BPMN; Workflow 2 (1 actor, 5 steps) → flow_strip; Workflow 3 (1 actor, 2 steps) → none. Accept, or override any?"*

Atomic decision: accept the inventory or specify overrides. Apply overrides; per-workflow walkthrough proceeds with the locked inventory.

**Skip rule**: if every workflow's computed choice is `none`, the checkpoint runs silently (nothing to confirm).

## Per-Workflow Role-Based Deep Dive

For **each** workflow listed in Q6, walk the role checklists **as the interview script** — see § How to run the walk below for the exact procedure. **The 11 docx subsections are output slots, not the interview index.** Answers from a role-checklist question land in whichever docx subsection naturally fits its shape; the mapping table below is read **role → subsections it feeds** (right-to-left), not subsection → questions to invent (left-to-right). If you find yourself walking the subsection list and authoring `AskUserQuestion` options to fill each subsection's table, you are drifting — re-anchor on the role checklists.

The docx uses **business-language headings** and **all subsections are table-based** (see [`reference/content_outline.md`](reference/content_outline.md) § Style principles + § Per-workflow subsections). Each docx subsection's label is the user-facing one — the role checklists below are the *source* for what to ask, not the *voice* of what to write.

### How to run the walk

For each role checklist in this canonical order — **business_analyst → consultant → solution_architect → security → ux_ui → devops → data_migration → documentation → performance → localization → qa** — repeat:

The first eight roles each own at least one subsection (see output mapping table below). The last three — performance, localization, qa — are **cross-cutting nudgers** that adjust already-populated subsections; walk them last so their nudges layer on, not over. Inventing a fresh subsection to hold a performance / localization / qa answer is documented drift — see "Cross-cutting roles" note under the output mapping table.

1. **Open the checklist file** in [`../_shared/role_checklists/<role>.md`](../_shared/role_checklists/).
2. **Read its "Key Questions to Ask the User" section verbatim.** Those questions ARE your interview script for this role.
3. **Apply P12 (necessity filter)** per question: is the answer already inferable from Q1–Q6, the brief, a prior role's answer, or an on-disk artefact? If yes, skip and record the inferred value. If no, the question survives.
4. **For each surviving question, post one `AskUserQuestion` turn.** Options come from the checklist's own framing — its Mechanisms / Tools / Common Pitfalls / Mode-of-Use sections give the option vocabulary. Never write option text that has no corresponding line in the checklist.
   - **Thin-vocabulary fallback.** If the checklist's Key Question gives you fewer than 2 concrete option strings to draw from, ask **Other-only (free-form)** with a single illustrative example rather than padding to four invented options. The user's free-text reply is data; four plausible-sounding invented options are noise that pulls the answer toward the option set rather than the truth. `ux_ui.md` and `documentation.md` are the most common thin-vocabulary cases.
5. **Translate the answer into business language** per the six tone rules below, and write it into the SPEC_DATA subsection(s) the role feeds (see output mapping table below).
6. **Re-run the builder.** Move to the next role checklist.

**Pre-ask gate (drift guard).** Before posting any `AskUserQuestion` in this section, you must be able to name aloud (a) which role checklist file the question is sourced from and (b) the specific "Key Questions to Ask" line it paraphrases. If you cannot, **stop, open the checklist, re-anchor.** What you would have asked is docx-shape-driven, not role-driven, and the spec will end up describing the table you wanted to fill rather than the system you are spec'ing.

### Output mapping — where each role's answers land

The table below is the **output mapping**, not the interview index. Read it as `role → subsections it feeds`: when you finish walking a role checklist, its answers land in the docx subsections shown. Walking the table top-to-bottom (subsection-by-subsection) is the documented anti-pattern — see § How to run the walk above.

| # | Per-workflow subsection (in the docx, table) | Role checklist(s) sourced from |
|---|---|---|
| 1 | **Success Criteria** *(workflow-aggregate; `Criterion \| How we measure it`)* | [business_analyst.md](../_shared/role_checklists/business_analyst.md) + [consultant.md](../_shared/role_checklists/consultant.md) |
| 2 | **User Stories & Steps** *(4 cols: `# \| User Story \| Actor \| Step` — no per-step Success Criterion column; that rolled up to subsection 1)* | business_analyst.md |
| 3 | **New Models** *(renamed from "New Data Captured"; 6 cols: `Purpose \| Name \| Technical Name \| Parent Menu \| Views Required \| Required Features`; `N/A — no new model introduced` when none)* | [solution_architect.md](../_shared/role_checklists/solution_architect.md) |
| 4 | **New Fields & Information** *(6 cols: `Model \| Field Name \| Captures \| Type \| Options/Remarks \| Location/Visibility`)* | solution_architect.md |
| 5 | **Navigation & Menus** | [ux_ui.md](../_shared/role_checklists/ux_ui.md) |
| 6 | **Screens & Interactions** *(merged: was Screens & Interactions + User Touchpoints)* | ux_ui.md + business_analyst.md |
| 7 | **Automated Behaviours** | solution_architect.md + [devops.md](../_shared/role_checklists/devops.md) |
| 8 | **Business Rules & Validations** | solution_architect.md + [security.md](../_shared/role_checklists/security.md) |
| 9 | **Reports & Analytics** | [documentation.md](../_shared/role_checklists/documentation.md) + solution_architect.md |
| 10 | **Data Migration** | [data_migration.md](../_shared/role_checklists/data_migration.md) |
| 11 | **Access & Permissions** *(two sub-tables: `11.1 New Groups — Group \| Reason created \| What it achieves`; `11.2 Existing Groups mentioned — Group \| Reason in spec \| Change`)* | security.md |

**Cross-cutting roles (no dedicated subsection).** Three checklists in the canonical walk order — `performance.md`, `localization.md`, `qa.md` — do **not** own a subsection. Their answers are **cross-cutting nudges** that layer onto subsections already populated by other roles:

- **performance.md** → adjusts **Automated Behaviours** (e.g., batch-size, scheduled-job cadence) and **Business Rules & Validations** (e.g., indexed-field implications, search constraints).
- **localization.md** → adjusts **Apps Impacted** (e.g., per-region currency, fiscal localization), **Business Rules & Validations** (e.g., locale-sensitive validation), and **Screens & Interactions** (e.g., RTL flips, locale-aware field labels).
- **qa.md** → adjusts **Success Criteria** (specifically the "How we measure it" column — qa's framing makes the measurement testable rather than aspirational) and **User Stories & Steps** (failure-case coverage). This is where **Check 5(b) — action-guard completeness** lands at deep-dive time: as the actions accumulate, walk each state-changing action and confirm its unmet-precondition path exists as a negative-path story + a Business Rule, not just the happy path.

Walk these three roles **last** in the per-workflow walk so their nudges layer on the already-populated subsections rather than initialising them. None of these three legitimately produces a brand-new subsection — if you find yourself trying to invent one, you have drifted.

**Tone enforcement.** Six style principles apply to every subsection (see [`reference/content_outline.md`](reference/content_outline.md) § Style principles). Read these BEFORE writing any cell — they shape the prose, not just review it.

1. **Business language first, technical identifiers parenthetical.** Lead with the user-facing concept ("Sales Order line"); drop the technical name in parens only when the dev audience genuinely needs the anchor, and only once per concept per section. Avoid `_inherit`, `_compute`, `xpath`, `@api.depends`, `post_init_hook`, `record rule`, `ACL`, `domain` in body prose — soften to business equivalents.
2. **Describe what changes, not what stays.** Only **new** content per workflow. If a workflow extends an existing concept, name the concept once in business terms and describe the additions. Don't enumerate inherited fields, existing menus, existing automations, or existing access rights.
3. **The docx's primary focus is the customization required.** Every subsection that DOES have new content should make the new development as explicit as possible — not bury it in narrative. Tables before prose. Standard Odoo behaviour is implied unless it's being modified.
4. **Specificity over abstraction.** Prefer concrete Odoo-mapped phrasing over consulting / business jargon. If a phrase doesn't map to a concrete Odoo concept, behaviour, or visible change, replace it with one that does. Three sub-rules:
   - **Concrete over abstract.** ❌ "approval governance" → ✅ "approval workflow on Internal Transfers". ❌ "in-transit modelling" → ✅ "transit-location modelling between warehouses". ❌ "capacity control" → ✅ "per-van load cap". ❌ "working-capital drag" → ✅ "working capital tied up in unsold stock". ❌ "reconciliation gaps" → ✅ "books diverge from physical stock".
   - **Regional / regulatory acronyms expanded on first use.** When a regional or regulatory acronym appears the first time in the docx, expand it inline with the issuing authority. Examples: *"ZATCA (Saudi Arabia's Zakat, Tax and Customs Authority)"*, *"GDPR (EU General Data Protection Regulation)"*, *"GST (India Goods and Services Tax)"*, *"FATCA (US Foreign Account Tax Compliance Act)"*. After the first use, the abbreviation alone is fine.
   - **Disambiguate generic terms with multiple Odoo implementations.** When a generic concept term maps to two or more Odoo features, name each implementation on first use. Common collisions: "approval" → *Approvals app (multi-approver Approval Request) vs Studio approval rules (gates on record validation) vs custom Python*; "rule" → *record rule vs server-action constraint vs Studio approval rule*; "automation" → *server action vs cron vs Studio automated action*.
5. **Prose discipline — no symbols, consistent case.**
   - **No operator symbols in body prose.** Banned: `→`, ` + ` (between concept words), ` = ` (between concept words), `>` / `<` (between worded concepts), `AND` / `OR` in caps. Replacements: `→` → *"leads to"* / *"then"* / restructure as a flow strip; ` + ` → *"and"*; ` = ` → *"is set to"* / *"becomes"*; `>` → *"exceeds"*; `AND` → *"and"*. Allowed exceptions: `×` in formulas (`sales price × on-hand`), `→` in menu paths (`Approvals → New Request`), real code-snippet references.
   - **Capitalisation convention.** Title-case for named roles / groups / Odoo features when referring to the named entity: *Store Keeper, Sales Agent, Accountant, Supervisor, Approvals app, Internal Transfer*. Lowercase for adjectival qualifiers in prose: *sender Store Keeper, receiver Accountant* (sender / receiver are adjectives, not part of the role name).
6. **Cross-workflow references restate the condition.** When workflow N references workflow M's behaviour, restate the trigger or condition in full rather than referencing an internal label. ❌ *"Studio approval cycle does not attach (Workflow 1 skip-rule a)"* → ✅ *"Studio approval cycle does not attach (destination warehouse's Resupply From is empty)"*. Internal labels (*"step 7"*, *"skip-rule a"*, *"rule 3"*) are invisible from outside that workflow — restate the condition each time.

The interview questions still pull from the role checklists (which are written for the technical audience of `odoo-plan-development`), but the **answers landing in the docx are translated to business language** before they're written and pass these six rules. Stage 1 lint catches the worst technical-jargon leaks and the post-interview anchor pass surfaces tone drift.

**Interview discipline (same as Fixed Questions — invariant)** — every per-workflow question is a single `AskUserQuestion` turn with 2–4 options drawn from the role checklist file you are currently walking. One atomic ask per turn. **This is the highest-drift section of the entire skill**: 11 role checklists × N workflows means a long sequence of role asks, and bundling temptation compounds with fatigue. Pause and re-read the § Interview discipline invariant before opening each role checklist if you feel tempted to combine. Never ask "what fields does the user see, and which are required?" — that's two asks across two turns.

**Strict-`N/A — <reason>` discipline.** Subsections that don't apply must be **explicitly marked** `N/A — <one-line reason>` in the docx, never silently omitted (per principle #6's "name what's missing" spirit and the 7 C's "complete"). The reason must be **specific**, not generic:

- ✅ `N/A — standard Odoo credit-control flow unchanged for this workflow`
- ✅ `N/A — no new model introduced; the workflow extends existing Sales Order`
- ✅ `N/A — workflow only creates new records; no existing data to migrate`
- ❌ `N/A — not applicable` *(rejected by Stage-1 lint)*
- ❌ `N/A — not specified yet` *(rejected by Stage-1 lint)*
- ❌ `N/A — TBD` *(rejected by Stage-1 lint)*

The principle: if the reason can't be specific, the question wasn't asked thoughtfully. Re-ask before writing N/A.

**P12 (necessity filter) examples** for the role-walk:
- **solution_architect.md** → if the workflow only adds fields to existing models, the "new model state machine?" question collapses to "no new model" and the New Models subsection lands as `N/A — no new model introduced for this workflow; extends existing X`.
- **data_migration.md** → if the workflow only creates new records (no existing populated data touched), the entire role's questionnaire collapses to one inferred answer; the Data Migration subsection lands as `N/A — workflow only creates new records; no existing data to migrate`.
- **documentation.md** → if the workflow ships no new report, the "what reports?" question collapses and the Reports & Analytics subsection lands as `N/A — no new report; existing Sales reports surface this data`.

Default: ask 2–4 questions per **applicable role checklist** per workflow, max — measured by role, not by subsection. A role with no surviving questions (after P12) contributes zero asks; a complexity-heavy role (e.g., security on a compliance-sensitive workflow) can exceed four. The output docx still has 11 subsections regardless — silent / unfilled ones land as specific `N/A — <reason>` (see strict-N/A discipline above).

## BPMN diagram block (optional per-workflow process visualisation)

A workflow may opt into a BPMN-style swimlane diagram for its Process Flow subsection by populating a `bpmn_diagram` block in its SPEC_DATA entry. The builder's `render_bpmn_image` helper rasterises the lanes to a PNG via Pillow; `make_diagram_heading` emits the diagram's `title` + `subtitle` as **real docx text** above the image (so they stay at true point size — a wide swimlane scaled to the column would otherwise shrink the caption to a few points), and `make_bpmn_diagram` embeds the PNG at its readable native width capped to the content column (`_diagram_width`). If the block is absent, the workflow falls back to a `flow_strip` (modern block diagram, see below) or to nothing if neither is set.

The renderer is tuned to read like a human drew it in a proper BPMN tool, not an auto-layout engine: **solid plum role sidebars** with white role names, **alternating lane tints**, lane dividers and an outer pool frame for clear role separation; **orthogonal (90°) connectors** that leave and enter shapes at their side-centres with right-angle elbows through an inter-lane channel; nodes **clamped inside their own lane** (an error-end event never floats across a swimlane boundary); and label/shape sizes chosen so type stays legible on the page. Keep diagrams to roughly **≤6 columns** where you can — a portrait A4 figure scaled to the content column gets small per-column space, so a long flow reads better split across two workflows or simplified.

**When to choose BPMN over flow_strip.** Use the BPMN diagram when the workflow has either (a) **≥2 actors** (multiple swimlanes — e.g. a Sales Rep + the Sales Order system + a Warehouse user), or (b) a **non-linear flow** (decision gateway, error branch, parallel paths). Use the `flow_strip` for purely sequential single-actor workflows with ≥3 steps.

**Flow strip (modern block diagram).** When a workflow specifies `flow_strip` as a list of step labels, the builder renders a modern PIL-based PNG: rounded plum-outlined pills with an accent top-stripe, numbered step badges, and clean plum arrows between them — visually consistent with the BPMN diagram language. `render_flow_strip_image` + `make_flow_strip_diagram` produce and embed it (also at readable native width). The legacy table-based `make_flow_strip()` renderer remains as the **fallback path** only (when Pillow is unavailable) — white-fill cells with a plum border, numbered `1. … 2. …` prefixes, and floating `→` connectors between pills. The graceful degradation reads as a refinement of the same flow language, not a different aesthetic.

**Pillow dependency.** Both BPMN AND the modern flow_strip use Pillow. `render_bpmn_image` raises `ImportError` if Pillow is missing (defensive — should not fire when the Diagram-choice checkpoint is honoured). `flow_strip` degrades gracefully to the legacy table renderer if Pillow is missing — the docx still builds. Install with `./v19/odoo/.venv/bin/pip install Pillow`. Pillow ships with Odoo's `requirements.txt`, so it's already present in any Odoo dev venv and on Odoo.sh; the missing-Pillow case is the bare-venv scenario only.

### Schema

```python
"bpmn_diagram": {
    "title": "Process — <Workflow Name>",        # rendered as docx text above the image
    "subtitle": [                                  # optional, 1–3 lines of context (docx text)
        "What the process does, in business language.",
        "Triggered when …",
    ],
    "caption": "Figure 1 — …",                    # optional italic caption below the embed
    "lanes": [                                     # list, top-to-bottom in the diagram
        {"name": "Sales Agent", "sub": "Order desk"},
        {"name": "Sales Order", "sub": "Confirmation & reserve"},
        {"name": "Warehouse", "sub": "Fulfilment"},
    ],
    "nodes": [                                     # list, drawing order doesn't matter
        # Every node carries: id (unique within this diagram), kind, lane (0-indexed),
        # col (0-indexed logical column). Optional: y_offset_in_lane (px nudge ± from
        # the lane centre — CLAMPED so the node + its label always stay inside the
        # lane; it can't push a shape across a swimlane boundary).
        {"id": "start", "kind": "start_event", "lane": 0, "col": 0,
         "label": "Draft SO opened"},
        {"id": "t1", "kind": "task", "lane": 0, "col": 1, "step": 1,
         "action": "Add order line",
         "description": "Sales rep adds a lot-tracked product to the SO"},
        # ...
        {"id": "err", "kind": "end_event", "lane": 1, "col": 4,
         "variant": "error", "label": "Order rejected (lot conflict)"},
        {"id": "gw", "kind": "gateway", "lane": 1, "col": 5,
         "label": "Lot still available?"},
        {"id": "end", "kind": "end_event", "lane": 2, "col": 7,
         "label": "Order fulfilled"},
    ],
    "edges": [                                     # list, drawn before nodes (lines tuck under shapes)
        {"from": "start", "to": "t1"},            # plain arrow
        {"from": "gw", "to": "rsv", "label": "Yes", "label_colour": "success"},
        {"from": "gw", "to": "err", "label": "No",  "label_colour": "warn"},
        # ...
    ],
    "legend": True,                                # optional — default True
},
```

Give the error-end its own column beside the gateway (rather than stacking it in the same column with a big negative `y_offset`); the orthogonal router then draws a clean same-lane elbow to it and it stays inside the lane. `\n` in labels is honoured but rarely needed — labels wrap to the shape width automatically.

### Node kinds

| `kind` | Required fields | Visual |
|---|---|---|
| `start_event` | `lane`, `col`, optional `label` | Thin plum-ringed open circle. Label below the circle in grey, clamped off the role sidebar. |
| `end_event` | `lane`, `col`, optional `label`, optional `variant: "error"` | Thick-ringed circle: success-green by default, warn-orange when `variant: "error"`. Label placed below if the lane has room, else above — never crossing the lane boundary. |
| `task` | `lane`, `col`, `action`, optional `description`, optional `step` (numbered badge top-left) | Rounded white card, plum outline + accent top-stripe, action as primary copy and description as supporting grey prose. All task cards share one content-sized height so descriptions never spill. |
| `gateway` | `lane`, `col`, `label` | Diamond with an X marker (exclusive-OR gateway). Label sits **above** the diamond (clearing the downward/sideways branch edges and their Yes/No labels, which would collide with a below-placed question); falls to below only when there's no room above. |

### Task action labels: verb phrases, not states

The `action` string on a `task` node is a **verb phrase** describing what the actor / system DOES at this step — not a state the artefact is IN. Diagram reads in consistent grammatical voice across all tasks.

- ❌ "Stock in transit" *(state — describes what stock IS)*
- ✅ "Dispatch first leg" / "Move stock to transit" / "Validate first transfer" *(action — describes what HAPPENS)*
- ❌ "Order rejected" *as a task label* *(state — but legitimate on an `end_event`)*
- ✅ "Reject and notify" *as a task label*

If the natural label is a state, it usually belongs on an `end_event` (terminal states) or as the Outcome of a preceding task — not as the task itself.

### Edge auto-routing (orthogonal / 90° elbows)

The renderer routes every connector with right angles, picking the path automatically from the source and target positions — **no manual coordinates required**. Lines exit and enter at shape **side-centres** (never an arbitrary corner) and turn at 90°:

- **Same lane, forward (col increases)** → straight horizontal (source right-centre → target left-centre); a Z-elbow if the two sit at different heights.
- **Same lane, backward** → mirror of the above (e.g. a gateway's "No" branch to an error-end placed one column back).
- **Cross-lane** → exit the facing edge (bottom going down / top going up), stub into the lane margin, then run the long vertical leg in a **column gutter** — the node-free band halfway between two column centres, half a column to the source-side of the target column — and stub into the target. Routing the riser through the gutter (not down the source or target column) means it can never pierce an intermediate node that happens to share a column the edge passes through (e.g. a second task stacked in the same column in another lane).
- **Same lane + same column** (stacked via `y_offset_in_lane`) → a short vertical connector.

Lines are drawn **before** the shapes so their ends tuck under the node outlines. **Edge labels are drawn in a final pass, on top of every shape and shape-label**, so a `"Yes"`/`"No"`/branch label is never buried under a node or another label. Each edge may carry an optional `label` placed on its first visible run (the first segment long enough to clear the exit stub, so the label sits on a readable length rather than crammed against the source shape) with a white halo, and an optional `label_colour` (`"success"` paints green, `"warn"` paints orange, omitted defaults to ink). The connector line itself is always plum; only the label takes the colour.

### Where the PNG lands

The builder writes the rendered PNG to `<spec-folder>/_reference/<task-code>-wf<N>-bpmn.png` (one file per workflow). The image is regenerated on every builder run; never hand-edit the PNG — edit the `bpmn_diagram` block in SPEC_DATA and re-run (principle #1).

## Post-Interview Anchor Pass (quality review, not a gate)

After the linear per-workflow walkthrough completes — the docx is already fully drafted on disk at this point — fire the full 14-anchor set in parallel. **Anchor target: hand each anchor the absolute path to `_reference/_build_<task-code>.py` — its `SPEC_DATA` dict is the readable source of truth.** Do NOT point anchors at the `.docx`: it is a binary zip the Read/Grep-only anchors cannot parse, and the builder emits no JSON intermediate. (Tell each anchor explicitly that the `.docx` is the rendered form and `SPEC_DATA` is what to audit.) This is a **quality review**, not a destructive-action gate: the docx exists, the user can already open it, and the anchors surface drift between what the role checklists demand and what landed in the document.

### Invocation

**ALL 14 Agent calls go in ONE message, foreground only.** (Write-specs runs 14 anchors — plan-dev runs 15, the extra one being `scaffolding-anchor`. Scaffolding correctness is plan-dev-specific and doesn't apply to a docx artifact.) The single-batched-message rule survives even though we're no longer using it as a plan-mode gate — running anchors sequentially or in separate messages defeats the parallel-perspective benefit. See [`../odoo-plan-development/SKILL.md` § Pre-ExitPlanMode Anchor Pass](../odoo-plan-development/SKILL.md) for the procedural mechanics (anchor invocation, tag namespace); only the anchor *target* (here, the `_build_<task-code>.py` SPEC_DATA — see § Invocation note above; plan-dev anchors read the markdown plan file directly), what the anchors audit *against*, and what happens after differ:

- `principles-anchor` — vs `_shared/principles.md` (16 numbered principles)
- `plan-structure-anchor` — adapted: audits the docx's 5 numbered top-level sections (+ Cover + TOC front matter) + 11 per-workflow subsections against [`reference/content_outline.md`](reference/content_outline.md), not odoo-plan-development's Output Contract
- `troubleshooting-anchor` — vs `../odoo-plan-development/reference/troubleshooting.md` (catches the spec re-deriving a known workaround instead of citing the entry)
- `business-analyst-anchor` … `ux-ui-anchor` (×11) — vs the matching role checklist, audited against the docx's per-workflow subsection that the role owns

### Reconciliation (no gate — user decides)

After all 14 reports return:

1. **Verify completeness** — all 14 `auditor` fields present in the returned JSON. Re-call any anchor that errored, before reconciling.
2. **Collect, dedupe, bucket** findings by `tags` and `severity`. Same tag namespace as odoo-plan-development: `principle:<n>`, `structure:<aspect>`, `role:<slug>`, `checklist:<artifact>`, `drift:<pattern>`.
3. **Present blockers to the user one at a time** per the interview invariant (§ Interview discipline), each with a single-question `AskUserQuestion` patch-accept-reject ask. Never bundle two blockers into one ask, even if they're in the same section. The docx is already on disk so the user can open it, see the flagged section, and decide.
   - **Bundling self-test.** If your drafted `AskUserQuestion` body contains "Blocker 1" / "Blocker 2", the phrase ` and also `, or two `?`s, **that's bundling — split into two turns.** Same-section blockers are still two turns; section affinity is not a bundling licence.
4. **Apply approved patches** to the builder's `SPEC_DATA` (not the docx directly — P1), re-run the builder, the docx updates. Re-run any anchors whose domain a patch touched.
   - **Route by audience, not by severity.** A finding patches the **docx body** only if it changes something a business stakeholder reads — a workflow step, a business rule, a success criterion, an app-impact statement. A finding that is **implementation discipline** — constant-time secret compare, cron `limit=`/give-up terminal, expression index, sudo narrowness, timeout on an outbound call — lands in `dev_handoff` (the matching `assumptions[]` / `*_notes` slot), NOT the docx. The integration/security/devops anchors legitimately raise many of the latter against a business spec; routing them to `dev_handoff` keeps the docx clean while the discipline still reaches plan-dev. When unsure which a finding is, ask: "would a procurement officer reading the spec act on this?" — if no, it's `dev_handoff`.
5. **Nit-severity findings are NOT appended to the docx.** The Open Nits appendix was removed per the conciseness pass. If a nit is worth keeping for the dev team, fold it into the relevant per-workflow subsection inline (e.g., as a row note in the Business Rules & Validations table). Otherwise drop it.
6. **No `ExitPlanMode`.** When the user accepts the docx as-is, the docx on disk is the deliverable. Before the final "Done", make the finish-line mock offer (§ Offer mock screens (finish line)); then say "Done — open `<path>`" and stop.

### When to skip

- User explicitly asks: `--skip-audit`, "fast-mode", or equivalent. Record under `dev_handoff.process_log.anchor_pass_skipped = '<YYYY-MM-DD>'` in SPEC_DATA (see § Dev-Only Hand-off to odoo-plan-development) so plan-dev knows the docx wasn't self-vetted on role-checklist drift. The docx stays clean — no top-of-document SKIPPED banner.
- Iteration on an already-anchored docx where the only change is a typo or styling tweak — anchors are for spec *decisions*, not formatting fixes.

## Dev-Only Hand-off to odoo-plan-development

The interview generates context that's valuable for the downstream developer skill but would clutter the docx for business stakeholders. The builder reserves a top-level `dev_handoff` key in SPEC_DATA for exactly this: **anything inside `dev_handoff` is read by `odoo-plan-development` (which loads `_reference/_build_<task-code>.py` directly per its own SKILL.md § Reference Material) but is NOT rendered to the docx.** The docx stays clean; the structured hand-off survives.

`odoo-plan-development` runs `SPEC_DATA.get("dev_handoff", {})` when ingesting a spec folder and uses each field below to P12-skip its own interview questions (citing the `dev_handoff` source in its Assumptions section, per its P12 rule). Every field is **optional** — a spec that omits `dev_handoff` entirely still satisfies the contract; plan-dev defaults gracefully when a field is absent.

### Fields

```python
"dev_handoff": {
    # P12 inferences the spec interview chose to make rather than ask.
    # Each entry pairs the question with the inferred answer and the
    # source it came from (a brief excerpt, a workflow subsection, an
    # earlier role answer). plan-dev cites these when it P12-skips the
    # same question on its side.
    "assumptions": [
        {"question": "dataset scale",
         "inferred": "<10k records",
         "source": "Q5 brief — 'sales reps select lot/serial per order line' implies order-line volume only"},
    ],

    # Process events that previously had no docx slot. Replaces the
    # 'Critical evaluation: SKIPPED on <date>' and 'Anchor pass: SKIPPED
    # on <date>' top-of-docx markers earlier drafts of this skill wrote.
    "process_log": {
        "critique_skipped": "2026-06-14",          # ISO date, or omit
        "anchor_pass_skipped": "2026-06-14",       # ISO date, or omit
        "critique_outcomes": [                      # one-liners per Check that fired
            "Check 2: Sale Subscriptions overlap considered; user chose extend, reason: per-distributor cycle not in standard.",
        ],
    },

    # P16 completeness decisions per workflow. The spec body captures
    # these as Business Rules / Automated Behaviours rows; this is the
    # structured mirror plan-dev needs to skip its lifecycle &
    # contention asks. Key each entry by the workflow's snake_case slug
    # (derived from its `name`), or by 1-indexed position ("wf1", "wf2").
    # Omit a workflow's entry entirely if it commits/locks/reserves
    # nothing.
    "completeness": {
        "wf1": {
            "lifecycle": {
                "commits": ["lot allocation on SO line"],
                "releases_via": "order cancelled / draft re-opened",
                "restores_via": "stock available again in same warehouse",
                "terminal": "delivery validated → allocations frozen",
            },
            "contention": {
                "can_double_claim": False,
                "frees_stale_via": "warehouse refresh on quote expiry",
            },
            "availability_frame": "warehouse-scoped",
            # Where this workflow's behaviour lives, so plan-dev knows up
            # front which automated tier can prove it (and which can't):
            #   "backend"      — pure server/ORM; Stage 1/2/3 + tests cover it.
            #   "owl-frontend" — POS button/popup, custom OWL widget; INVISIBLE
            #                    to every automated stage. plan-dev must split
            #                    the logic into guarded server methods (testable)
            #                    + a thin frontend, and budget a manual UI
            #                    checklist + server-method shell smoke (Stage 3c).
            #   "mixed"        — both; mark it so neither half is forgotten.
            # Omit only when genuinely unknown; default-assume "backend".
            "validation_surface": "backend",
        },
    },

    # Q5d-equivalent for plan-dev. Often invisible in prose. Keep
    # structured so plan-dev's devops-role gate ("external surface?")
    # is answerable without re-reading the whole spec.
    "integration_surface": ["none"],
    # Valid entries: "none", "inbound webhook", "outbound API call",
    # "file import/export", "email triggers". List form so multiple
    # touchpoints can coexist.

    # Performance-role engagement gate for plan-dev. Plan-dev engages
    # Performance on >10k or cron present — make the signal explicit
    # instead of inferred from "feels routine."
    "dataset_scale": "<10k",            # "<10k" / "10k-100k" / ">100k"
    "crons_introduced": 0,              # count; 0 → Performance role can stay quiet

    # Critical Brief Evaluation Check 2 outcomes structured. The §4
    # Apps Impacted prose covers this for stakeholders; the structured
    # form lets plan-dev assess complexity-vs-reuse without re-eliciting
    # the standard-module overlap list.
    "overlap_decisions": [
        {"workflow": "wf1", "module": "stock", "choice": "extend",
         "reason": "lot reservation gate at SO line is not in standard quote-to-delivery."},
    ],

    # Free-form role-discipline notes routed here from the anchor pass
    # (see § Reconciliation step 4 "Route by audience"). These are the
    # implementation-discipline findings that would clutter the docx but
    # plan-dev's matching role gate should see. Each is a list of short
    # strings; omit any slot that's empty. plan-dev reads them as
    # advisory build obligations, not interview answers.
    "security_notes": [
        "webhook secret stored in ir.config_parameter, system-group read only.",
        "constant-time compare (hmac.compare_digest) on the inbound token.",
    ],
    "devops_notes": [
        "outbound FX call: explicit timeout + raise_for_status, off the web request thread.",
        "retry cron: batch limit + give-up terminal state after N attempts.",
    ],
    "i18n_notes": [
        "customer-facing mail templates render in partner.lang.",
    ],
}
```

### Drift guard

- **Never render `dev_handoff` content in the docx.** If a stakeholder needs to see one of these facts, lift the specific finding into the matching docx subsection (e.g. an availability-frame decision becomes a Business Rule row). Don't echo the whole `dev_handoff` block — that's the same docx-clutter this carve-out exists to prevent.
- **Don't mirror.** If a fact is already captured as a Business Rule row, an Automated Behaviours row, or in the New Models / New Fields table, do NOT also stamp it into `dev_handoff.completeness`. The structured form is for facts the docx CAN'T cleanly carry (the lifecycle inverse never written, the dataset-scale assumption no row captures), not a redundant shadow of everything.
- **Lint silence is intentional.** Stage 1 lint walks the rendered docx; it does not validate `dev_handoff` shape. The builder treats unknown SPEC_DATA keys as no-ops. The principle here is "extra context is cheap; wrong docx content is expensive" — keep the validation gate on what reaches stakeholders.
- **Append, don't rewrite.** During the interview, when a question gets P12-skipped or a critique check fires, *append* the new entry to the relevant `dev_handoff` field rather than rewriting the structure. The accumulated list is the audit trail plan-dev consumes.

## Validation (three stages, reshaped for documentation)

The three-stage validation pattern from `odoo-plan-development` and `odoo-spreadsheet-report` adapts to a documentation artifact:

### Stage 1 — Static docx lint ([`reference/scripts/_lint_spec.py`](reference/scripts/_lint_spec.py))

Pure-Python walk of the docx (via `python-docx`; the Stage-1 lint can parse the binary, unlike the Read-only anchors). No Odoo runtime needed. Validates:

- **Filename** matches `<task-code> - <client-name> - <3-word-func>.docx`. Rejects path separators, colons, asterisks, pipes.
- **All 5 numbered top-level sections** (+ Cover + Table of Contents front matter) present per `reference/content_outline.md`.
- **Every workflow listed in Q6** has a sub-section under Section 5 with all 11 table-based subsections present OR explicitly marked `N/A — <specific reason>` (vague reasons like "not applicable" / "not specified" are rejected — see § Per-Workflow Role-Based Deep Dive Strict-N/A discipline).
- **No placeholder strings** anywhere in body text: `TODO`, `TBD`, `<fill in>`, `Lorem ipsum`, `XXX`, `[client]`, `[task]`.
- **Cover-page metadata block complete**: Prepared by, Role, Client, Companion to (optional), Scope, Date, Version. An additional optional `metadata.consultancy` is read by the builder for the footer's "Confidential — `<client>` / by `<consultancy>`" line; when absent the builder derives it from the `role` string (e.g. "Functional Consultant, Odoo" → "Odoo"). Stage 1 lint does not require it.
- **7 C's surface-level checks**: no paragraph > 4 lines; no casual-hedging strings (`I think`, `probably`, `obviously`, `maybe`, `sort of`).
- **No orphan headings**: every heading has at least one paragraph under it.

Exit non-zero on any error.

### Stage 2 — Anchor pass

Detailed in § Post-Interview Anchor Pass above. Drift detection against role checklists and principles; runs after Stage 1 passes. **Not a hard gate** — the user accepts or rejects each blocker, the skill applies approved patches, and the docx is regenerated.

### Stage 3 — Visual review

Render the docx, open it in Word / Pages / LibreOffice. Visual checks:

- Table widths align with section margins; no row overflow.
- Section heading sizes taper (cover title 26 → H1 20 → H2 16 → H3 14 → H4 12 pt, Montserrat Medium, grey ink ramp — see `docx_styling.md`).
- Cover shows the Odoo logo; the running header (page 2+) shows the task-code label + Odoo logo with a thin rule; the footer shows the confidentiality line + Page N of T.
- Bullet indentation is consistent across sections.
- Cover page logo / metadata block is centred and legible.
- Per-workflow Process Flow strips (optional, only for workflows with ≥3 sequential steps) render without overlap.

The user's eyes are the final check. The skill renders; the user opens. If layout breaks, fix the builder (not the docx — per P1, hand-edits to the docx vanish on the next regen).

If any stage fails: fix, regenerate the docx via the builder, re-run all three stages from the top — never skip Stage 1 just because "I only changed wording."

## Offer mock screens (finish line)

After the docx is accepted (anchor pass reconciled, Stage 1 + Stage 3 passed) and
**immediately before** the final "Done — open `<path>`" message, offer to
visualise the proposed screens. A written spec tells the reader the workflow; an
interactive mock *shows* it — useful for stakeholder sign-off and as a companion
the dev team reads alongside the spec.

1. **Ask once, via a single `AskUserQuestion`** (interview invariant — this is one
   atomic ask, not bundled with anything): "The spec is done. Want me to generate
   interactive visual mocks of these screens?" Options: **Yes, generate mocks
   (Recommended)** / **No, the docx is enough**.
   - **Skip the ask entirely when the invocation already committed to mocks** —
     e.g. the user pre-declared a pipeline ("write-specs → mock-design →
     plan-dev") or asked for mocks up front. Re-asking is pure ceremony; proceed
     straight to step 3 and note that you're doing so.
2. **If No** — say "Done — open `<path>`" and stop. Nothing else changes.
3. **If Yes** — invoke `odoo-mock-design` via the **Skill tool**, in the main
   thread, passing the **absolute spec-folder path**. That skill detects
   Workflow 1 (a spec-folder path was handed in), reads this spec's structured
   `SPEC_DATA` from `_reference/_build_<task-code>.py` (no re-interview), and
   writes a self-contained interactive mock to `<spec-folder>/mocks/`. It runs
   its own self-containment lint + two-anchor (`mock-coverage`, `mock-fidelity`)
   gate before finishing.
4. When `odoo-mock-design` returns, report both artifacts: "Done — open
   `<docx path>` (spec) and `<spec-folder>/mocks/index.html` (interactive mock)."

This is the only hand-off `odoo-write-specifications` makes. It never re-interviews the
user for the mock — the spec already holds everything the mock needs. (Invoking
via the Skill tool keeps full context and the tools `odoo-mock-design` needs; a
spawned subagent is an acceptable variant but inline is the default.)

## Documentation of the spec itself (Always Last)

The docx is itself the documentation. There is no separate `doc/` folder per spec — the spec stands alone. **No appendices.** The Glossary appendix, the Acknowledgement page, and the Anchor-Pass-Open-Nits appendix were all removed per the conciseness pass. The docx is the spec, not a sign-off ceremony, and not a vocabulary lesson — the body keeps technical jargon out of prose (tone rule #1) so a glossary is unnecessary.

## Production-readiness checklist (before declaring done)

- [ ] **Plan mode was NOT entered** — this skill is exempt from P11 per the incremental-drafting carve-out in `_shared/principles.md`. If a transcript shows an `EnterPlanMode` call, something else triggered it (e.g. the user pressed Shift+Tab); that's fine, but the skill itself never calls it.
- [ ] Per-spec folder exists at `<repo>/specifications/<task-code> - <client> - <func>/`. Opening it shows exactly two entries: the `.docx` and `_reference/`. No `_draft.docx`, no stale builder at the `specifications/` root.
- [ ] Builder script lives at `<repo>/specifications/<task-code> - <client> - <func>/_reference/_build_<task-code>.py` and is idempotent (running it twice produces byte-identical docx).
- [ ] Docx lives at `<repo>/specifications/<task-code> - <client> - <func>/<task-code> - <client> - <func>.docx`.
- [ ] Stage 1 lint exits 0 (all 5 numbered top-level sections present; 11 per-workflow subsections complete or marked with specific `N/A — <reason>`; no placeholders; no casual hedging; no vague N/A reasons; filename matches convention).
- [ ] Stage 2 anchor pass completed (all 14 anchor `auditor` fields present in returned JSON; blockers presented to user and resolved; nits either folded inline into the relevant subsection or dropped — no Open Nits appendix).
- [ ] Stage 3 visual review done by the user — they opened the docx and confirmed layout is clean.
- [ ] Cover-page metadata block complete.
- [ ] **No appendices** — Glossary, Acknowledgement, and Open Nits are explicitly removed (see `content_outline.md` § Explicitly NOT present).
- [ ] Every workflow under Section 5 has all 11 table-based subsections (present or explicitly `N/A — <specific reason>`).
- [ ] **Finish-line mock offer made** — before the final "Done", the user was asked once (single `AskUserQuestion`) whether to generate interactive mocks; if accepted, `odoo-mock-design` ran against the spec folder and `<spec-folder>/mocks/` exists. (Declined is a valid outcome; the offer itself is the checklist item.)

## Iteration Etiquette

Per principle #8. Skill-specific notes:

- When the user reports the docx renders wrong, fix the **builder's `SPEC_DATA`** (not the docx directly). Hand-edits to the docx vanish on next regen — P1.
- When a stakeholder pushes back on content mid-interview, update the affected section's `SPEC_DATA` entry, re-run the builder, the docx on disk refreshes immediately. The user can confirm the fix in Word before you ask the next question.
- After every fix, re-run Stage 1 lint. Even one-sentence changes can break a structural rule (placeholder snuck in, section heading typo'd).
- **Match existing style** (principle #8). When editing an existing spec, mirror its tone and section depth — don't re-write to a different voice.
- Tell the user **what specifically changed** in concrete terms after a fix — they need a reason to reopen the file. "Updated §8.3 Models to add `dms.parts.staging.order`" beats "fixed the parts thing".
