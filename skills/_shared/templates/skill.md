---
name: <skill-slug>
description: <What the skill produces and how it validates it, in one or two sentences. Name the artifact, the interview, and the validation loop. Together with when_to_use, at most 1,536 characters.>
when_to_use: Use this skill when <the one-line trigger>. NOT for <the nearest neighbour skill's job> (that's <other-skill>).
allowed-tools: Read, Edit, Write, Bash, Grep, Glob, Agent, EnterPlanMode, ExitPlanMode, AskUserQuestion, ToolSearch, TodoWrite
---
<!-- TEMPLATE: copied from skills/_shared/templates/skill.md. Read
     skills/_shared/templates/README.md before filling it in. Delete every
     TEMPLATE comment before the skill ships. Keep the section order below;
     a section that does not apply stays as its heading plus one line that
     says why ("N/A — <reason>") or is removed with a carve-out recorded under
     § Entry. Keep the finished file at or under 500 lines; move procedures
     longer than a screen into reference/. -->

# <Skill Title>

<One paragraph: the request this skill turns into an artifact, who reads the
artifact, and the defining rule of the skill.> Skill-specific discipline below;
cross-cutting principles live in [`skills/_shared/principles.md`](../_shared/principles.md)
and apply here too.

## Scope

<!-- TEMPLATE: optional. Keep it when the skill has a hard boundary another
     skill owns (spreadsheet-report: "NEVER custom development"). Say what the
     skill never does and what to do instead. Delete the section otherwise. -->

This skill produces <artifact> only. It never <out-of-scope action>; when the ask
needs that, halt and point the user at `<other-skill>`.

## Entry: <Architecture detection | exemption> and <plan mode | exemption>

<!-- TEMPLATE: two decisions live here, both shared principles.
     1. P13 architecture detection. Skills that touch an instance, a DB or a
        deploy target run Q0 with the shared detector. Documentation-only
        skills record the exemption in one paragraph instead.
     2. P11 plan mode. Skills with any destructive step call EnterPlanMode as
        the very first tool call and gate execution on ExitPlanMode. Skills
        that only write inside their own output folder (write-specs,
        mock-design) record the exemption and name the gate that replaces
        it (an anchor pass, a lint). -->

**Q0 — architecture (principle #13).** Before any other action, run
[`../odoo-plan-development/reference/scripts/_detect_environment.py`](../odoo-plan-development/reference/scripts/_detect_environment.py)
and read its `architecture` field (`local | odoo.sh | docker | bare_metal | unknown`).
Surface the inference under an `Architecture` heading in the plan and confirm it
with one `AskUserQuestion`. Never default silently to Local.

Routing after confirmation:

- `local` → the rest of this file.
- `odoo.sh` / `docker` / `bare_metal` → [`reference/architecture_branches.md`](reference/architecture_branches.md),
  which follows the P13 safety-net handoff pattern for any branch not fully specified.

**Plan mode (principle #11).** The first tool call of the skill is `EnterPlanMode`
(fetch it with `ToolSearch` `select:EnterPlanMode,ExitPlanMode` when deferred),
unless plan mode is already active. The interview, read-only pre-flight and design
happen inside plan mode. The plan lands at `<repo_root>/plans/<scope>-<slug>.md`,
not `.claude/plans/`; delete the harness placeholder once the real file exists.
`ExitPlanMode` is called only after the anchor pass reports no blockers, and the
user's approval is what authorises every destructive step listed in the plan.

**Do not open with "what do you want to do?"** The first question the user sees is
Q1 (or the first question that survives principle #12).

## When To Use

<Two or three sentences: the trigger, the lifecycle position (what runs before and
after this skill), and the nearest skill it is not.>

## Output Contract

Produce, in order:

- **Interactive questions**, one at a time (principle #10).
- **<Primary artifact>** at `<path convention>`.
- **<Builder / scripts>** where principle #1 says a builder pays for itself.
- **Stage 1 / 2 / 3 validation passed** (see § Validation).
- **Documentation** at `<path>` (see § Documentation).
- **[`reference/troubleshooting.md`](reference/troubleshooting.md) updated** with any new
  failure mode, honouring the principle #6 write gate; run
  `../_shared/scripts/_lint_troubleshooting.py --skill <skill-slug>` after editing.

<One sentence naming the minimum that does NOT satisfy the contract, e.g. "An
artifact that loads but fails Stage 3 does NOT satisfy the contract.">

## Reference Material (Read Before Building)

- [`skills/_shared/principles.md`](../_shared/principles.md) — cross-cutting discipline. Read first.
- [`reference/troubleshooting.md`](reference/troubleshooting.md) — known failure modes
  (4-line entries). Read before generating; grep the literal error string during fixes.
  The archive sibling is consulted only for "did we hit this before?".
- [`../_shared/role_checklists/<role>.md`](../_shared/role_checklists/) — the roles this
  skill's interview walks (§ Role-Based Questions).
- [`../_shared/addon_conventions/`](../_shared/addon_conventions/) — only when the skill writes
  or rewrites addon code: the manifest, layout, Python, views, tests and web house style.
- [`reference/<canonical-structure>.md`](reference/) — <the skill's own canonical
  structure: outline, catalog, design system>.
- [`reference/samples/reference_pattern.md`](reference/samples/reference_pattern.md) —
  annotated walk-through of good output at the target density.
- The target version's `odoo/` and `enterprise/` source — authoritative for every claim
  about standard Odoo (principle #9). Pin it with
  `python3 skills/_shared/scripts/_check_odoo_source.py --probe --root-prefix versions/v<major>`.

## Pre-Flight

<!-- TEMPLATE: read-only probes run inside plan mode (detection, model
     checks, source probes, tooling checks). Anything destructive is LISTED
     here and in the plan, and runs only after approval (principle #4). -->

- **Read-only (inside plan mode):** <probes — source probe, model verification, tooling check>.
- **Destructive (after approval only):** <installs, DB creation, writes outside the
  skill's output folder>. Each one is listed in the plan and confirmed per principle #4.

## Fixed Questions (Ask In This Order)

### Interview discipline (mandatory)

Per principle #10: one atomic question per turn; every question through
`AskUserQuestion` with 2–4 concrete options; free-text only for the one question
the user opts out of, then back to the tool; one or two sentences of reflection
between asks, never fused with the next ask.

<!-- TEMPLATE: list any standing free-text carve-outs here with their reason
     (write-specs: task code, client, business brief). No carve-out, no
     paragraph. -->

### Necessity filter (P12) per question

Before each ask: is the answer inferable from the invocation, an on-disk artifact or a
read-only probe, and would it change the artifact? Skip what fails either gate and
record `Assumed <X> from <Y>` under the plan's `Assumptions` heading. Two equally
plausible readings are asked, never silently picked.

Typical skips for this skill:

- **Q1** skipped when <inference source>.

### The questions

**Q1. <Question>?** Options: <where the options come from>.

**Q2. <Question>?** Options: <…>.

## Role-Based Questions (Ask Only What Matters)

Each role has a checklist under [`../_shared/role_checklists/`](../_shared/role_checklists/).
Ask the one or two questions per engaged role that change the outcome; record the
default for every role that drops out.

| Role | When to engage for this skill | Checklist |
|---|---|---|
| **<Role>** | <trigger> | [<role>.md](../_shared/role_checklists/<role>.md) |

Completeness dimensions (lifecycle, contention, guards — principles #15 and #16) are
asked whenever they apply, even when an input artifact seems to answer them.

## Anchor Pass

<!-- TEMPLATE: plan-mode skills place this section here, because it gates
     ExitPlanMode. Exempt skills keep the heading here but describe a
     post-draft quality review instead (write-specs) or a pre-finish gate
     (mock-design). Skills with no drift-prone walkthrough say "N/A —
     <reason>" (spreadsheet-report today). -->

After the plan is fully written and **before** `ExitPlanMode`, fire every anchor below
in **one message, foreground only** (one `Agent` call per anchor, no
`run_in_background`, no `ExitPlanMode` in the same message). Each anchor gets the
absolute plan path and returns its JSON findings as its final message; it never
writes a file.

| Anchor | Audits against |
|---|---|
| `principles-anchor` | `_shared/principles.md` |
| `troubleshooting-anchor` | `reference/troubleshooting.md` |
| `<role>-anchor` | the matching role checklist |
| `<skill-specific>-anchor` | <the skill's own structure contract> |

The role anchors are written for plan-dev plan files. Give each prompt a one-paragraph
**<skill>-mode brief**: what the artifact is, which plan-dev-only rules do not apply,
and what to audit instead.

**Reconciliation.** (0) Confirm a JSON payload from every anchor; re-call any that
failed. (1) Collect findings. (2) Dedupe by `tags`. (3) Bucket by `severity`.
(4) Present blockers one at a time (principle #10). (5) Patch the plan — only the main
agent edits. (6) Re-run anchors whose domain a patch touched. (7) Append nits under
`## Anchor Pass — Open Nits (<date>)`. (8) Call `ExitPlanMode` when no blocker remains.

**When to skip.** Only on an explicit user request (`--skip-audit`), recorded at the
top of the plan, or for a fix-iteration that changes no plan decision.

## <Skill-specific execution sections>

<!-- TEMPLATE: the skill's own procedure lives here, in the order it runs:
     Implementation Rules (plan-dev), Generation Rules + Design System
     (spreadsheet-report), Generation Pipeline (mock-design), Per-Workflow
     Deep Dive (write-specs). Use as many ## sections as the procedure
     needs. Move anything longer than a screen into reference/ and link
     it. -->

## Validation

Three stages (principle #2); each catches a different failure class, and none is
skipped to save time.

### Stage 1 — Static

`<command>` — <what it checks without a runtime>. Exit non-zero on any error.

### Stage 2 — Server-side

`<command>` — <install, import or load into the target DB>.

### Stage 3 — Operational

`<command or manual check>` — <what proves the artifact works, not just loads>.

If a stage fails: fix, regenerate through the builder, re-run every stage from Stage 1.

## Documentation (Always Last)

After all three stages pass, write `<path>`: <the sections the reader needs>. See
[`documentation.md`](../_shared/role_checklists/documentation.md).

## Production-readiness checklist (before declaring done)

- [ ] Plan-mode / exemption rule honoured (`EnterPlanMode` was the first tool call, or the documented exemption applied).
- [ ] Every anchor returned a payload before `ExitPlanMode`, and no blocker was left open.
- [ ] Artifact at its path convention; no placeholder strings; no leftover harness placeholder plan.
- [ ] Stage 1, Stage 2 and Stage 3 each passed on the final artifact.
- [ ] Documentation present.
- [ ] `reference/troubleshooting.md` updated if the write gate passed; `_lint_troubleshooting.py --skill <skill-slug>` exits clean.

## Iteration Etiquette

Per principle #8. Skill-specific notes:

- <Where fixes go — the builder, never the generated artifact.>
- <Which stage to run first when the user reports a symptom.>
- After a fix, re-run every stage and tell the user what changed in concrete terms.
