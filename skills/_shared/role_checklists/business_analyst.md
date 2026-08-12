# Business Analyst — Functional Spec

*Calibrated against Odoo 19.0. Re-review on each major version bump.*

## Goal
Translate the consultant's brief into concrete user stories and acceptance criteria the QA role can test against.

## Key Questions to Ask the User
- What are the **3–5 user stories** in "As a X, I want Y, so that Z" form?
- For each story, what's the **acceptance criterion** (a state-and-action pair, e.g. "after clicking Approve, the record state is `approved` and the requester gets an email")?
- What **integration points** exist with other Odoo modules (sale, account, project, etc.) — does this read from them, write to them, or both?
- What **demo data** is needed to make the workflow look real on first install?
- Are there **emails / notifications / reports** triggered by the workflow?
- What **feature toggles** does each story silently assume? For each integration point, walk through: "if Settings shows this feature as OFF, does my workflow still make sense?" (Examples: lot/serial tracking, multi-currency, analytic accounting, variants, pricelists, multi-step routes, sub-tasks.) Any "no, the story breaks" answer = a row in the plan's **Required configuration** list with the relevant `res.groups` xml_id (see the Solution Architect checklist, § Required configuration).
- What are the **non-functional requirements**? Expected record volume (orders of magnitude), latency tolerance (sub-second / under-a-minute / batch-only), availability (business-hours-only / 24×7), audit trail (chatter sufficient / regulatory log required). Only applicable when the addon touches > 1k records or external integrations; for trivial extensions, declare "non-functional reqs N/A — single-user / low-volume workflow."
- Does the workflow **commit / lock / reserve** a resource, or add a **state**? If so: what **releases** it, what **restores** it, what does **cancel / expire** do — and can **two documents** claim the same unit (and what frees a stale claim)? (principle #15) Declare `N/A` when the workflow introduces no such resource.

## Mechanisms / Tools
- Capture user stories in `<addon>/doc/user_manual.md` as the canonical spec — this same file also surfaces in the Apps store description if mirrored to `static/description/`.
- For each story, write the acceptance criterion as a one-sentence test, e.g. "`record.action_approve()` transitions state to `approved`."
- Map each story to one or more concrete deliverables: model field, button, view, automated action, `mail.template`, `mail.activity.type`, `ir.actions.server`.
- **Validate stories in Studio before coding.** Studio's view editor + automated actions + approval rules let you build a working prototype the user clicks through in their browser — catches "the workflow doesn't match my mental model" gaps before any custom code is written. Only commit to a custom module after the Studio prototype passes user review.
- **Notification choice per state transition**: `mail.template` for email sent to a party; `mail.activity.type` for a to-do that lands on a user's dashboard with a deadline. Both at once when the recipient needs both an email reminder and a tracked follow-up.
- **Approval workflow choice**: Studio approval rules (gate a record from leaving a state until N approvers OK it — visible audit, no code) vs the Approvals app (`approval.request` records — heavier, multi-approver, attachable) vs custom `state` field + button method (highest control, full code path, fits when neither standard fits). Default-first: Studio rule. Step up only when Studio's limits (no per-line conditions, no cross-record gates) bite.
- **INVEST sanity-check per story** — Independent / Negotiable / Valuable / Estimable / Small / Testable. A story that fails Small (can't fit a sprint) needs to be split; a story that fails Testable (no concrete state change) needs a sharper acceptance criterion.
- **Map the full lifecycle, not just the forward transition.** For each new state or commitment, write its inverse (release / restore) and terminal-state cleanup as acceptance criteria *alongside* the forward one — a "reserve" story implies a "free it on cancel" story (principle #15).

## Common Pitfalls
- Stories that describe the implementation ("the user clicks the button") instead of the goal ("the user approves the request").
- Acceptance criteria that aren't testable ("it works", "it's fast").
- Forgetting the **negative path** — what happens when the user lacks permission, the data is invalid, the record is locked?
- **Custom-coding what Studio + automated actions could do.** A user story that maps to "add a field, hide it when state=draft, send mail on confirm" is a Studio configuration, not a custom module. Recognise this before scoping a dev sprint.
- **`mail.activity.type` and `mail.template` confused.** Activities are user to-dos that block records and surface on the user's dashboard; templates are emails. Picking the wrong one means the user either gets spammed (template when an activity was needed) or never notices (activity when an email was needed).
- **Specifying the forward action without its inverse** — "commit the lot" with no "free it on cancel", "reserve" with no "unreserve → restore". The inverse is part of the story, not a later follow-up.
- **Ignoring contention** — two users claim the same unit on separate quotations; without a hold + release-valve rule, both promise it and one fails late.

## Production-readiness criteria
- [ ] All user stories captured with acceptance criteria.
- [ ] Negative paths covered (permission denied, invalid input, locked record).
- [ ] Demo data sufficient for a fresh installer to see the workflow without typing anything.
- [ ] Integration points listed with read/write direction.
- [ ] Feature toggles each story depends on are listed in the plan's **Required configuration** section (or explicitly noted as "none required").
- [ ] Emails / notifications / reports triggered by each state transition are enumerated.
- [ ] Each user story has an actor mapped to a `res.groups` xml_id (or the actor is `base.group_user`).
- [ ] Each state / commit / reservation story states its inverse (release, restore) and terminal-state (cancel/expire) behaviour as acceptance criteria — or `N/A` (no such resource).
- [ ] Contention is addressed where a finite resource can be claimed by multiple documents (a hold rule + what releases a stale claim) — or `N/A`.

## Required artifacts (the plan must contain these)

1. **User stories list** — 3–5 stories in `As a <role>, I want <action>, so that <outcome>` form. Each story names a `res.groups` actor.
2. **Acceptance criteria** — one or more per story, expressed as a `state + action → expected state + side effect` tuple (e.g. *"Click Approve on a draft record → state becomes `approved`, the requester receives `mail.template my_module.approval_done`"*).
3. **Negative-path inventory** — for every primary acceptance criterion, the failure mode the user sees (permission denied → which user message? invalid input → which validation? locked record → which error?).
4. **Integration-points list** — every other Odoo module the workflow reads from or writes to, with direction (`read` / `write` / `both`).
5. **Feature-toggles inventory** — for each integration point, walk through: *"if Settings shows this feature OFF, does my workflow still make sense?"* Any "no, the story breaks" answer = a row in the plan's **Required configuration** section with the `res.groups` xml_id. Empty list (no toggles required) is a valid answer but must be stated, not assumed.
6. **Notifications inventory** — emails / activities / reports triggered by which state transition; named by `mail.template` xmlid or `mail.activity.type` xmlid. Empty list is valid.
7. **Demo-data plan** — what records the addon ships in `demo/` so a fresh installer sees the workflow without typing anything. Empty (no demo data) is valid only if the workflow is visible against base demo data alone — state which.
8. **Non-functional requirements statement** — expected volume, latency tolerance, availability window, audit-trail level. Required when the addon touches > 1k records or external integrations. For trivial extensions, "N/A — single-user / low-volume workflow" is a valid statement.
9. **Lifecycle & contention statement** — when the workflow commits / locks / reserves or adds a state: per resource, the release, restore, and terminal-state (cancel/expire) behaviour; and — if a finite resource can be claimed by multiple documents — the contention rule plus what releases a stale claim. `N/A` only when the workflow introduces no such resource. (principle #15)
