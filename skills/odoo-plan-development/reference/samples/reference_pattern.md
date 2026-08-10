# Reference Pattern — Annotated Plan Walk-through

*Calibrated against Odoo 19.0. Re-review on each major version bump.*

Annotated walk-through of a real-shape plan file emitted by this skill, used as the structural + density benchmark for `odoo-plan-development`'s Output Contract. The reference plan itself is not shipped — what's preserved here is the **shape and depth** the skill targets. Read this file to calibrate the level of detail the skill's output should aim for; never copy verbatim.

The reference was a single-instance plan for a financial-reporting extension on a real customer DB. Identifying details are stripped — what's preserved is the structural anatomy and the calibration cues.

---

## At-a-glance

- **~280 lines** total plan file.
- **One Odoo 19 customer** (Local-architecture, Custom subscription tier).
- **One new addon** (~7 new fields on existing models, 1 new model, 1 cron, 1 report).
- **Uniform top-level section sequence** (described below).
- **All 15 anchor reports** confirmed in the transcript before `ExitPlanMode` was called; 1 blocker accepted + patched, 2 nits folded inline.
- **Calibrated against** Odoo 19.0; the SA-anchor and devops-anchor surfaced `Command.create` and `--workers` discipline.

This is the density target. A plan for a smaller addon (one field added) should emit a *similarly proportioned* document — same care per section, just fewer lines. A plan for a larger addon (new app with 5 models, multiple workflows) should grow proportionally; if it crosses 600 lines, the addon probably needs splitting.

---

## Top-level section sequence (the Output Contract)

Every plan file emits these sections in this order. The `plan-structure-anchor` audits the mechanical presence; the role anchors audit the content within each.

1. **Architecture** (P13) — `local | odoo.sh | docker | bare_metal` detected at Q0, with signal source.
2. **Assumptions** (P12) — questions skipped by the necessity filter, with the inferred answer for each.
3. **Business Case** — the consultant brief's problem statement, primary user, success criterion, scope inclusions/exclusions, standard-Odoo overlap statement.
4. **Dependencies** (Pre-Flight B.1) — every model the addon touches resolved to its defining module; each marked verified-in-validation-DB.
5. **Required configuration** (Pre-Flight B.2) — every `res.groups` / `res.config.settings` toggle the addon's workflow depends on, with xml_id + UI path. Empty list ("none required") is a valid answer.
6. **nginx** — `Scaffold: ...`, `Skip — --no-nginx requested`, `Skip — no nginx include dir detected`, or `N/A — existing instance / non-Local`.
7. **Implementation** — the actual addon design: models, fields, views, security, automated behaviours, business rules, automations, reports, data migration. Per-role content is what the role anchors audit against.
8. **Stage 1** — static lint command snippets (`_lint_addon.py`) with the concrete conf path + addons path + module name.
9. **Stage 2** — install/upgrade command snippets (`_install_module.py`) with the concrete DB + module name.
10. **Stage 3** — operational smoke command snippets (`_smoke_module.py`) with the concrete checks: model search, menu resolution, sample-create-compute-unlink, ACL deny-case.
11. **User manual + Testing manual paths** — declares `<addon>/doc/user_manual.md` and `<addon>/doc/testing_manual.md` as deliverables.
12. **Troubleshooting** — any new failure mode discovered during the run, in 4-line format, ready to be appended to `reference/troubleshooting.md`.

The plan **never** has appendices beyond these 12. If you find yourself adding a 13th section, it belongs inside one of the 12.

---

## What the reference plan does well (adopt)

- **Plan-file path matches `<repo>/plans/<instance>-<functionality>.md`** — not `.claude/plans/<random>.md`. The skill never accepts the harness's auto-generated random slug; per P11, the plan lives at the canonical path. The reference's filename was `plans/dev_v19-cashflow-report.md`.

- **Architecture detected automatically, not asked.** The Q0 architecture detection ran via `_detect_environment.py` before any user-facing question. The plan's Architecture section reads "local (detected: `./v19/odoo/.venv/bin/python` + `./v19/instances/dev_v19/odoo.conf`)" — concrete signal source, not "the user said local."

- **Assumptions block records skipped questions.** P12 (necessity filter) skipped 3 questions in this run; each lands in Assumptions with the inferred answer. The user reads Assumptions at `ExitPlanMode` approval and can override anything.

- **Dependencies section explicitly verifies each declared module** is installed in the validation DB. The format is one line per dep: `account — verified installed (ir_module_module.state = "installed" on dev_v19)`. The SA-anchor refuses to approve a plan with an unverified depend.

- **Required configuration block** names every `res.groups` flag with its xml_id AND its UI path. Format: `account_analytic.group_analytic_accounting — Settings → Accounting → Analytic Accounting`. Plan declares whether the toggle is enabled via `post_init_hook` or documented as an operator pre-step.

- **`Command.create` / `Command.update` / `Command.link` in x2many writes**, not the legacy `(0, 0, {...})` tuples. The reference plan was Odoo 19; the SA-anchor would flag legacy tuples as a nit.

- **`_check_company` decorator on every `Many2one` to a company-scoped target.** The reference's new `Many2one("account.journal", check_company=True)` had this; the SA-anchor would have flagged its absence.

- **Stage snippets are copy-paste-ready** with the concrete conf path, DB name, and module name from this run — not placeholders. The testing manual mirrors them.

- **Sub-headings are stable across plans.** Implementation uses fixed sub-headings: Models, Fields, Views, Security, Automated Behaviours, Business Rules & Validations, Reports & Analytics, Data Migration, Access & Permissions. The role anchors audit against these sub-headings.

- **Studio-vs-code boundary stated explicitly** in the Implementation section. For each Implementation choice, the plan declares either "custom code because `<concrete fit gap>`" or "Studio handles this — implementation note rather than code." The SA-anchor would flag a custom module for what's clearly Studio-doable.

- **Anti-patterns prevented citations.** The plan's pre-flight discipline section cites specific troubleshooting entries it's structured to avoid (e.g. *"Anti-patterns this section prevents: troubleshooting #6 (`required=True` on populated model — handled via two-step), troubleshooting #8 (feature group never enabled — handled in Required configuration), troubleshooting #33 (nginx 502 — handled in nginx section's log pre-touch note)"*).

- **Pre-flight Pillow / OS-package checks** are gated behind explicit user confirmation per P4 — no silent installs. The plan declares the gate explicitly: `if Pillow missing: AskUserQuestion 'install via pip?' → execute on yes / demote on no`.

- **Anchor-pass discipline at `ExitPlanMode`** — single batched message, all 15 Agent calls foreground. The reference's transcript shows one tool-use turn with 15 Agent invocations; the next turn has 15 JSON responses; the assistant turn after that reconciles. No anchor was missing.

- **Blocker reconciliation one at a time.** When 3 blockers came back from the anchor pass, the user was asked one per `AskUserQuestion` turn, never bundled. Reflection between asks was 1–2 sentences; the next ask was a separate turn.

---

## What a less-disciplined plan does (avoid)

- **Mixes architecture detection with user-facing questions.** A plan that asks "Is this Odoo.sh or local?" as Q0 wastes a turn — the answer is detectable from the file system. P13 + `_detect_environment.py` are non-negotiable.

- **Treats `Required configuration` as optional.** Skipping the block when the addon happens to not need it is wrong — the plan should EXPLICITLY say "none required" so the SA-anchor knows the BA walked the feature-toggle question for every integration point, not just forgot.

- **Stage 3 only checks install succeeded.** Stage 3 is *operational* smoke (search models, resolve menus, CRUD a sample record, exercise ACLs as a non-admin). A plan whose Stage 3 just re-runs the install command satisfies the contract on paper but misses the "installed but unusable" failure class. The qa-anchor catches this.

- **`post_init_hook` without an idempotency gate.** Re-runs on every `-u`, re-applies whatever it does. The devops-anchor flags this.

- **Plan file at `.claude/plans/<random>.md`.** The harness's auto-generated random-name file is a placeholder; the canonical plan lives at `<repo>/plans/<instance>-<functionality>.md`. The plan-structure-anchor refuses to approve a plan at the harness path.

- **`ExitPlanMode` fired before the 15 anchor responses landed.** The contract is: anchor responses arrive in the assistant turn immediately after the single batched Agent-call message, THEN the reconciler runs, THEN `ExitPlanMode` is called. Calling `ExitPlanMode` before the responses arrive is a gate violation.

- **Custom-coding what Studio handles.** A plan that proposes a custom module for "add a field, hide it conditionally, send mail on confirm" is Studio territory. The SA-anchor flags this; the consultant-anchor backs it up.

---

## Per-section calibration

What "good enough" looks like at the section level, calibrated against the reference.

### Architecture (P13)

- Single line. `local | odoo.sh | docker | bare_metal` + the signal source (file path that surfaced it).
- Example: `local (signal: ./v19/instances/dev_v19/odoo.conf and ./v19/odoo/.venv/bin/python both present; no .odoo-sh/ marker)`.

### Assumptions (P12)

- One line per skipped question, with the inferred answer and the source of the inference.
- Example:
  ```
  - Q4 (DB name) — inferred dev_v19_cashflow from instance name + functionality slug (skipped per P12; user can override at ExitPlanMode)
  - Q7 (target Odoo version) — inferred 19.0 from instance conf (skipped per P12)
  - Q12 (notification mail required?) — inferred yes from the brief mentioning "send the report to finance"; ask was redundant (skipped per P12)
  ```

### Business Case

- One paragraph each: Problem, Primary user, Success criterion (measurable), In-scope, Out-of-scope, Standard-Odoo overlap statement.
- Reference's length: ~25 lines for a focused addon. Doubles if the addon spans multiple workflows.

### Dependencies (Pre-Flight B.1)

- Table or bullet list, one entry per direct manifest depend, with the verification result.
- Example bullet:
  ```
  - account (account.move, account.move.line) — verified installed in dev_v19_cashflow
  - account_reports (account.report) — verified installed
  - mail (mail.template) — verified installed
  ```
- Transitive deps don't list (they're pulled in by the direct ones).

### Required configuration (Pre-Flight B.2)

- Table or bullet list, one entry per `res.groups` / `res.config.settings` toggle.
- Example:
  ```
  - account_analytic.group_analytic_accounting — Settings → Accounting → Analytic Accounting → enable. Set via post_init_hook (idempotency: skips if already enabled).
  - account.group_account_manager — Settings → Users → assign to the report-runner user. Documented as operator pre-step in testing_manual.md.
  ```
- Empty list valid: `none required` (explicit, not implied).

### nginx

- Single line declaring the disposition. One of: `Scaffold: instance dev_v19_cashflow.test:443 with shared cert at .nginx/certs/instances.test.pem (HTTPS)`, `Skip — --no-nginx requested`, `Skip — no nginx include dir detected`, `N/A — existing instance / non-Local`.
- For Scaffold: include the log-pre-touch note ("`_create_instance.py` pre-touches access/error logs as invoking user — see troubleshooting #33").

### Implementation

- The longest section. Sub-headings: Models, Fields, Views, Security, Automated Behaviours, Business Rules, Reports, Data Migration, Access & Permissions.
- Each sub-heading: a brief list of what's NEW (per the "describe what changes, not what stays" rule). Standard Odoo behaviour is implied unless modified.
- For Fields: name, model it lives on, type (with `check_company=True` where relational + company-scoped), purpose, location/visibility, `tracking=True` if chatter logs changes.
- For Security: ACL rows + record rules + `.sudo()` inventory with justifications + PII / sensitive-field inventory + external-credential inventory.

### Stages 1 / 2 / 3

- Each stage: ONE copy-paste-ready command, concrete conf path + DB name. The testing manual mirrors the same commands.
- Stage 3 is operational, not bare-install. Example smoke checklist for the reference plan:
  1. Module is in `installed` state (verify via `ir.module.module` row).
  2. New model `x.cashflow.report` is searchable (`env["x.cashflow.report"].search([], limit=1)`).
  3. New menu `Accounting → Reports → Cashflow` resolves to the action (verify via `ir.ui.menu`).
  4. Sample record creates, computeds populate (`compute_balance` returns non-None), unlinks cleanly.
  5. ACL enforces: non-admin user can read the report; non-finance user gets `AccessError` on write.
  6. Test suite passes: `--test-tags=/<addon>`.

### Troubleshooting

- 0–N new failure modes discovered during the run, in 4-line format.
- Reference plan added 1 entry: `### 49. Cashflow report _compute_balance returns 0 for empty date range on Odoo 19 (read_group lazy=False default change)`.
- Pre-existing failure modes that bit during the run get their `Last confirmed` date bumped to today; no duplicates.

---

## Length expectations by addon size

| Addon shape | Plan length | Notes |
|---|---|---|
| Single field added to existing model | 80–120 lines | Implementation section ~30 lines; stages ~10 lines each |
| New addon, 3–5 fields, 1 new model | 200–300 lines | Reference plan size |
| New addon, multiple models, cron + report | 400–600 lines | Split into separate plans if it crosses 600 |
| App-level (new top-level menu + ~10 models) | Split | Should be 2–3 separate plans, one per workflow |

---

## Calibration cues at a glance

- **Did the architecture get detected, not asked?** P13 violation if asked.
- **Does every skipped question have an Assumptions entry?** P12 violation if not.
- **Does every declared depend have a "verified installed" line?** SA-anchor blocker if not.
- **Does every `res.groups` toggle have an xml_id + UI path?** SA-anchor blocker if not.
- **Is `nginx` section present (Scaffold / Skip / N/A)?** scaffolding-anchor blocker if missing on Local-arch.
- **Are Stages 1 / 2 / 3 commands concrete or placeholders?** documentation-anchor blocker if placeholders.
- **Did the anchor pass run all 15 anchors in ONE message?** Procedural violation if sequential.
- **Were anchor blockers reconciled one at a time?** Interview-invariant violation if bundled.

These are the cues that distinguish a passing plan from a plan that *looks* passing.
