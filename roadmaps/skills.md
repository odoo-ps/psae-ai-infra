# Skills Roadmap — candidate future skills

> **Stale premise — read first.** Entries below reason about
> `odoo-plan-development` as a live skill that builds addons. It was **removed
> from the Corpus** (ADR 0003): every item of its output contract —
> `__manifest__.py`, `security/`, a new model `_name`, a deployment push — is a
> Major Change the Guardrail denies, so it could not run on a branch at all.
> Where an entry says "plan-development does X" or "pairs with
> plan-development", read that as **"the technical consultant does X, outside
> this Corpus"**. Any skill admitted from this backlog must declare which Judge
> Gate exit it serves and must require no action the Policy Source denies.

A **non-committal backlog** of skills that would extend the Odoo suite. Nothing
here is scheduled; this is the shortlist to revisit when a real engagement makes
one of these worth building. Each entry states what the skill does, the
**artifact it produces + how it validates** (so it fits the suite's
`interview → artifact → validate` pattern, not a one-off script), where it slots
into the delivery lifecycle, **whether an existing skill in the inventory could
already cover the work and why a separate skill is the right answer instead of
an extension**, and a **likelihood** we build it.

The current suite covers: **specify** (`odoo-write-specifications`) →
**visualise** (`odoo-mock-design`) → **build code** (`odoo-plan-development`) →
**build KPI reports** (`odoo-spreadsheet-report`). The gaps below are what that
lifecycle does *not* yet cover.

## Likelihood legend

| Rating | Meaning |
|---|---|
| **High** | Fills a gap the current suite *actively creates* (a documented path that dead-ends), or recurs in nearly every engagement. Build next. |
| **Medium** | Common, clearly valuable, clean fit with the existing pattern. Build when an engagement needs it. |
| **Low** | Valuable but narrow trigger or heavy to build / hard to make repeatable. Build on concrete demand. |

## Summary

| Candidate skill | Produces | Validates by | Likelihood |
|---|---|---|---|
| `odoo-configure` | A configuration / Studio runbook (no custom code) | Applying to the instance + asserting state via `odoo-bin shell` | **High** |
| `odoo-data-migration` | Field-mapping spec + import files + load script | Importing into the DB + reconciling counts | **High** |
| `odoo-uat` | Customer UAT pack — business-language test-case catalogue + tester manual + pre-validated result document | Pre-executing every test case against the built instance; pack ships only when all pass | **High** |
| `odoo-manual-design` | End-user manual / training walkthrough — clickable HTML pages built from screens captured off a running instance | Re-running the capture + diff-matching each step against the live UI; `_lint_mock.py` self-containment pass | **Medium** |
| `odoo-pdf-report` | A QWeb printed document (`ir.actions.report` + paperformat) | Rendering the report for a sample record (PDF, no error) | **Medium** |
| `odoo-version-upgrade` | A migrated addon (+ migration scripts) for a newer Odoo major | Install/upgrade on the target version + smoke (reuses plan-dev stages 2/3) | **Medium** |
| `odoo-perf-audit` | A tuning runbook for a live instance (slow-query inventory + index/config/sizing recommendations + applied fixes) | Re-measuring P50/P95 against the same query mix after applying recommendations | **Medium** |
| `odoo-security-audit` | A security findings + remediation runbook for a live instance (ACL/rule gaps, sudo escalations, public-route surface, secret-handling) | Re-running the audit + confirming each finding is closed | **Medium** |
| `odoo-diagnose` | A diagnosis + applied fix for a misbehaving instance/addon | Reproduce → fix → re-test the symptom | **Low** |

---

## `odoo-configure` — configuration-only / Studio runbook — **High**

**What.** For solutions that need *no custom code*: `res.config.settings` toggles,
Studio view edits, automated / server actions, approval rules, access groups. It
produces a step-by-step configuration runbook — the no-code analogue of
`odoo-plan-development`'s plan file.

**Validates by.** Applying the runbook against the chosen instance and asserting
the resulting state via `odoo-bin shell` (toggle on, field visible, rule fires) —
the same "validate against a live DB" loop `odoo-spreadsheet-report` uses for
import.

**Slots in.** The target when `odoo-write-specifications` Check 2 picks option (a)
*"use standard Odoo as-is, configuration only"*, or when the Studio-first doctrine
concludes no code is needed.

**Could an existing skill cover this?** Partially. The consultant + solution-
architect + ux-ui role checklists actively push *"Studio-first; custom code is
the fallback,"* and `odoo-write-specifications` Check 2 has an explicit
"configuration only" off-ramp. But no skill currently *executes* the
configuration — the spec describes the changes, the role checklists tell you to
prefer config, and `odoo-plan-development` then builds a custom addon. The
execution gap sits between spec and code.

**Why a separate skill.** Different artefact (step-by-step runbook of
configuration actions vs addon code vs spec document). Different validation
(apply-then-verify-state in `odoo-bin shell` vs install-then-smoke vs sign-off).
Plan-dev's machinery — 3-stage validation, 15-anchor pass, full Output Contract
— is overkill for what's essentially a Studio + automated-action + approval-
rule recipe with no code surface. Folding into plan-dev would require either
contorting its "addon" framing or shipping a "no-code mode" flag that bypasses
most of plan-dev's value.

**Why High.** This is a *self-contradiction* in the current suite, not just a
missing nice-to-have. The role checklists repeatedly push **"Studio/config-first;
custom code is the fallback"** (`consultant.md`, `solution_architect.md`,
`ux_ui.md`, the ux-ui anchor), and the spec workflow has an explicit
"configuration only" off-ramp — yet the only downstream *build* skill builds a
custom addon. A consultant who honestly concludes "this is configuration" today
falls off a cliff. Smallest, most pattern-consistent addition; closest sibling is
`odoo-spreadsheet-report`.

## `odoo-data-migration` — legacy data import / migration — **High**

**What.** Plan + execute loading legacy or external data into Odoo: a
field-mapping spec, the import files (CSV/XML), and a load + idempotency + dedup +
reconcile loop.

**Validates by.** Importing into the DB and reconciling record counts / spot-check
against source — a direct fit for the validate-by-import pattern.

**Slots in.** The go-live phase. Pairs with `odoo-plan-development` (once the
target model exists) or runs standalone for a pure data-load engagement.

**Could an existing skill cover this?** Partially. The `data_migration` role
checklist ([`_shared/role_checklists/data_migration.md`](../skills/_shared/role_checklists/data_migration.md))
exists and is rich — but it's consumed *inside* `odoo-plan-development` when
an addon modifies an existing populated model. A standalone legacy-data load
(legacy CRM → Odoo, no new addon involved) isn't plan-dev's surface — it's a
pure data engagement.

**Why a separate skill.** Different validation (reconcile row counts +
spot-check against source, not install + smoke). Different interview shape
(mapping-by-mapping, not role-by-role). Different output (mapping spec +
import files + load script, not addon code). The role checklist is consumed
by both — that's healthy reuse, not duplication. Folding into plan-dev would
force every data-load engagement through plan-dev's addon-building
scaffolding, most of which doesn't apply.

**Why High.** Nearly every go-live involves data migration, and today it is only a
*role checklist* (`_shared/role_checklists/data_migration.md`) consulted inside a
build — never a phase with its own artifacts. Arguably the highest *raw* value of
the candidates; ranked level with `odoo-configure` because it is a missing phase
rather than an internal contradiction.

## `odoo-uat` — customer UAT pack (test cases + tester manual + pre-validated result) — **High**

**What.** Turn the spec's acceptance criteria + workflow list into a
customer-executable UAT pack: (a) a **test-case catalogue** in
business-language step-by-step form (setup / preconditions / steps /
expected result / actual result), grouped by workflow, one entry per
acceptance criterion — traceable back to the spec via a criterion id;
(b) a **tester manual** — how to log in, how to reset state between
tests, how to record pass / fail, how to file defects; (c) a **result
document** — the same test-case list with the pass / fail / notes columns
already filled in from the skill's own pre-validation run, plus a
one-page summary the customer signs against. Deliverable format is
docx (mirrors `odoo-write-specifications`), optionally with an xlsx
test-tracker for progress reporting during the customer's own run.

**Validates by.** Running every test case's steps against the built
instance before the pack ships — either driving the UI headless via a
Chromium session (à la the proposed `odoo-manual-design`) or scripting
the mutation via `odoo-bin shell` where the step is testable that way —
and asserting the expected result. Any pre-validation failure blocks
delivery; the pack ships only when all tests pass. The customer's own
UAT then starts from a known-green baseline instead of catching defects
that should have been caught pre-handover.

**Slots in.** Immediately after `odoo-plan-development` ships (Stage 2
+ 3 green) and before the addon is handed to the customer for sign-off.
Consumes the spec's acceptance criteria (via `SPEC_DATA` when a spec
exists) and the plan's Implementation block; produces the pack the
customer's UAT actually runs against.

**Could an existing skill cover this?** No. `odoo-plan-development`
produces a **developer-facing** testing manual (Stage 3 smoke: `odoo-bin`
commands, ACL boundary checks, `env['<model>'].search([], limit=1)`) —
the audience is the developer verifying operational health, not the
customer verifying business acceptance. `odoo-write-specifications`
produces the **acceptance criteria** (via the BA role checklist) but
stops at the criteria; it never translates them into executable step-
by-step test cases in business language, and it never runs them. The
gap is exactly that translation plus the pre-validation loop.

**Why a separate skill.** Different audience (business/customer vs
developer). Different artifact shape (step-by-step business-language
test cases + a filled-in result doc, not `odoo-bin` commands or Python
unit tests). Different validation loop (pre-execute-until-all-green,
then hand off; not install + smoke). Different lifecycle position
(post-build pre-handover, not during-build). Folding into
`odoo-plan-development` would conflate the developer's operational
smoke — a Stage 3 gate on the build — with the customer's acceptance
test, a separate document at a separate audience and a separate moment
in the lifecycle. The `qa` role checklist is shared infrastructure both
consume; that's healthy reuse.

**Why High.** Every engagement ends in some form of UAT, and today the
suite dead-ends at developer-facing Stage 3 smoke — the customer sign-
off pack is authored ad-hoc every time, on a green build that hasn't
been pre-validated against the acceptance criteria. This is the most
common **"the developer said it worked, then the customer found ten
defects on day one of UAT"** failure mode. Building the pack + pre-
running it against the build catches those defects before the customer
ever sees them; on the days when the addon isn't quite ready, the
failing test cases become the punchlist that closes the gap. Same
value shape as the other High items — fills an active gap the current
suite creates, recurs in nearly every engagement.

## `odoo-manual-design` — end-user manual / training walkthrough — **Medium**

**What.** Sibling of `odoo-mock-design`. Same self-contained interactive HTML
output (a `manuals/`-style folder with per-step screens + walkthrough bar), but
the per-step screen markup is *captured from a running Odoo instance* rather
than composed from the baked catalog. The skill drives a headless Chromium
session against the target tenant, walks each step the user defines (login →
menu → record → action → result), snapshots the DOM at each pause, sanitises
the captured HTML (inline computed CSS so the page survives offline, hash +
bundle inline images, strip access-token query strings, remove `<script>` and
event handlers), and assembles the result as a portable folder any browser can
open over `file://`.

**Validates by.** Re-running the capture against the live instance and diff-
matching each step's snapshot against the current screen (same DOM shape +
same screenshot under a fixed viewport). The output also passes
`odoo-mock-design`'s `_lint_mock.py` self-containment lint (no external
references, no absolute URLs, no escapes out of the package root).

**Slots in.** The end-user training / handover phase, post-build. Pairs with
`odoo-mock-design` as the *as-built* counterpart to mock-design's *as-proposed*
artifact: the mock shows what was sold, the manual shows what was shipped.
Useful for onboarding training, customer success handoffs, post-go-live
documentation, and audit trails of "what the UI looked like on the day of
launch."

**Could an existing skill cover this?** No. `odoo-mock-design` produces
*designed* screens composed from the baked catalog — useful before the build
exists, deliberately unfaithful to the running instance (the catalog tracks
Odoo majors, not your tenant's exact data and configuration). The
[`documentation` role checklist](../skills/_shared/role_checklists/documentation.md)
covers *written* end-user manuals (markdown / docx prose embedded inside
plan-dev), but no skill captures and bundles the live system's actual UI as a
clickable artifact. Screencast tools sit outside the suite and don't produce
HTML you can search, paste, or attach to a PR.

**Why a separate skill.** Different input (live instance URL + session +
click-path vs catalog fragments). Different validation (snapshot diff against
live vs the catalog's pre-finish anchor pass). Different fidelity contract
(faithful-to-instance vs recognisably-Odoo). Different decay profile
(re-capture on every UI change in the tenant vs catalog refresh on Odoo major
bumps). Folding into `odoo-mock-design` would conflate two distinct outputs —
*"here is how it could look"* vs *"here is how it actually looks today"* —
under one entry point, and the catalog discipline (the mock-design's whole
value) would have to coexist with a code path that bypasses it entirely.

**Why Medium.** Common ask once a deployment is live (every onboarding wants
some form of "click-through me" walkthrough), and a clean pattern match to
mock-design. Lower than High because:
(a) `odoo-mock-design` + the documentation role checklist already cover most
engagements' needs without instance plumbing;
(b) the implementation is heavier than mock-design — Chromium driver, DOM
snapshot pipeline, computed-CSS inliner, asset bundler, token redaction,
diff-against-live validation — each of which has a real maintenance tax as
Odoo's frontend evolves;
(c) "the manual must BE the actual UI" is a real but not universal
requirement; some clients are happy with the catalog-composed mock or
markdown prose.

## `odoo-pdf-report` — QWeb printed documents — **Medium**

**What.** Custom printed business documents — invoice / quotation layouts,
delivery slips, certificates — via QWeb templates + paperformat
(`ir.actions.report`).

**Validates by.** Rendering the report for a sample record through the report
engine / `odoo-bin shell` and confirming it produces a PDF without error.

**Slots in.** Parallels `odoo-spreadsheet-report` (which covers *KPI spreadsheets*
only); together they would cover both reporting modes — analytical and printed.

**Could an existing skill cover this?** Yes, partially. `odoo-plan-development`
can already scaffold a QWeb report as part of a larger addon — the
`documentation` and `solution_architect` role checklists cover
`ir.actions.report`. For a *standalone* PDF-only deliverable (invoice layout,
certificate, delivery slip — no other addon surface), plan-dev's machinery is
overkill: no models to declare, no security rows to ship, no operational
smoke beyond *"render produces a PDF."*

**Why a separate skill.** Lifecycle scope is narrower than a full addon. The
validation pattern (render-for-sample-record) parallels
`odoo-spreadsheet-report`'s narrow "import + load cleanly" rather than
plan-dev's 3-stage discipline. Easier to reach for, easier to reason about,
harder to overbuild. The fork keeps plan-dev from being the only path for
what's a small deliverable.

**Why Medium.** Common deliverable and a clean parallel, but narrower than the two
High items, and `odoo-plan-development` can already scaffold a report as part of a
larger addon, so the standalone trigger is less frequent.

## `odoo-version-upgrade` — cross-major addon / DB migration — **Medium**

**What.** Migrate a custom addon (and optionally its data) across Odoo majors
(e.g. 17 → 19): deprecations, API changes, view/field renames, `migrations/`
scripts.

**Validates by.** Installing/upgrading the migrated addon on the target version
and running operational smoke — reuses `odoo-plan-development`'s Stage 2/3.

**Slots in.** Triggered by a version bump, not a new build.

**Could an existing skill cover this?** Partially. The migrated addon's
install + operational smoke IS `odoo-plan-development`'s Stage 2/3. The Odoo
Upgrade Service handles the DB; `odoo-bin upgrade-code` handles automated
source-tree transformations. What's left — and what plan-dev doesn't do today
— is the manual deprecation walkthrough: re-mapping removed APIs, fixing view
xpath drift, bumping the manifest version, surfacing the new Odoo major's
release-notes patterns against the existing addon.

**Why a separate skill.** Different trigger (Odoo major bump, not a new
build) + different upstream interview (deprecation surface against this
version's release notes, not requirements brief). Reuses plan-dev's Stage 2/3
for verification — that's healthy infrastructure sharing, not duplication.
The role checklists need re-calibration against the new Odoo version
(see `release-cadence-runbook` in
[`improvements.md`](improvements.md)) before plan-dev's anchors
are reliable on the new major; this skill is the per-engagement consumer of
that re-calibration.

**Why Medium.** High value but episodic trigger and heavy: the deprecation surface
shifts every release, so the skill's reference material would need refreshing each
major — a real maintenance tax.

## `odoo-perf-audit` — performance audit of a live instance — **Medium**

**What.** Targets an *existing* deployment, not a per-addon build. Inventories
slow queries (via `--log-sql`, `pg_stat_statements`, `EXPLAIN ANALYZE` on
the top offenders), surfaces missing indexes, computed fields without
`store=True` referenced in domains, cron jobs without batching, undersized
worker pools (`--workers`, `--cron-threads`, `--limit-time-*`). Produces a
tuning runbook with prioritized recommendations (impact vs effort) and applies
the agreed-on subset.

**Validates by.** Re-measuring the same workload after applying recommendations
— same set of pages / RPC calls / cron runs — and confirming P50 / P95
improvement against the pre-audit baseline. Reuses
[`_shared/role_checklists/performance.md`](../skills/_shared/role_checklists/performance.md)
as the per-role lens.

**Slots in.** Triggered by a customer reporting "Odoo is slow." Distinct from
`odoo-plan-development`'s per-addon performance role: that role audits a
*planned* addon's performance shape; this skill audits a *deployed*
instance's *actual* behaviour.

**Could an existing skill cover this?** No, not in current shape.
`odoo-plan-development`'s `performance-anchor` audits a planned addon's
performance shape — forward-looking ("will this addon scale?"). This skill
is backward-looking ("why is this deployment slow today?"). The
[`performance` role checklist](../skills/_shared/role_checklists/performance.md) is
the shared input — both consume it — but the walkthroughs differ: plan-dev
applies it to one new addon; perf-audit applies it to a whole tenant.

**Why a separate skill.** Different scope (whole live tenant vs one planned
addon). Different validation (re-measure baseline against same workload vs
install + smoke). Different evidence source (live `--log-sql` +
`pg_stat_statements` + `EXPLAIN ANALYZE` output vs plan inspection).
Different trigger (reactive — customer complaint — vs proactive — addon
being built). The role checklist is shared infrastructure; the audit's
surface is its own.

**Why Medium.** Common consultant task with a clean fit (interview → tuning
runbook → re-measure validates). Lower than High because the trigger is
episodic (a customer complains, not every engagement) and the work is
already partially covered by the performance role's Production-readiness
criteria once a tuning is proposed.

## `odoo-security-audit` — security audit of a live instance — **Medium**

**What.** Targets an *existing* deployment. Walks
[`_shared/role_checklists/security.md`](../skills/_shared/role_checklists/security.md) +
the OWASP Top 10 mapping against the live tenant: ACL coverage on every
custom model, record-rule scoping on company-scoped data, public-route
inventory + their CSRF / rate-limit / auth posture, `.sudo()` inventory + per-
call justification, `ir.config_parameter` for secrets (no hardcoded keys),
PII fields + `tracking=True` audit, 2FA on admin / finance groups. Produces
a findings report (severity-graded) and a remediation runbook; applies the
agreed-on subset.

**Validates by.** Re-running the audit and confirming each finding is closed
(ACL row added, record rule shipped, sudo justified, etc.). Final state has
zero blocker-severity findings.

**Slots in.** Triggered by a compliance review, a pre-go-live check, or a
post-incident hardening pass. Like `odoo-perf-audit`, it audits a *deployed*
instance — distinct from the per-addon `security-anchor` which audits a
planned addon.

**Could an existing skill cover this?** No, not in current shape. Same
pattern as `odoo-perf-audit`: `security-anchor` audits a planned addon;
this audits a deployed tenant. The
[`security` role checklist](../skills/_shared/role_checklists/security.md) + OWASP
Top 10 mapping are the shared input; the walkthroughs differ.

**Why a separate skill.** Different scope (every existing custom model +
every public route + every existing `.sudo()` vs only the new ones in a
plan). Different validation (re-run audit until zero blocker findings vs
install + smoke). Different trigger (compliance review / pre-go-live /
post-incident hardening, not addon construction). Parallels
`odoo-perf-audit`: both consume an existing role checklist in a new
walkthrough oriented at a deployed instance. Building them as a pair would
let them share the *walk-the-live-tenant* plumbing.

**Why Medium.** Clean fit and high-stakes when triggered, but the trigger is
episodic (compliance windows, breach response, pre-go-live). Most engagements
don't ask for a formal security audit; the ones that do require it
unambiguously.

## `odoo-diagnose` — instance / addon troubleshooting — **Low**

**What.** Diagnose a misbehaving instance or addon — read logs, reproduce,
localise, propose/apply a fix.

**Validates by.** Reproduce → fix → re-test: confirm the symptom is gone.

**Slots in.** The support / maintenance phase. Would lean heavily on the existing
per-skill `troubleshooting.md` corpus.

**Could an existing skill cover this?** Partially, and ambiguously. The
`troubleshooting.md` files per skill capture the static knowledge — known
failure modes + fixes. `odoo-perf-audit` and `odoo-security-audit` cover
proactive review. Diagnose is *reactive* and *symptom-specific*: read THIS
instance's logs, reproduce THIS user's bug, localise THIS commit's
regression. The diagnostic loop sits between the static catalog and the
proactive audits.

**Why a separate skill (if at all).** The diagnostic loop (instrument →
reproduce → localise → fix → verify) doesn't fit any existing skill's
`interview → artifact → validate` shape; the "artifact" is a fix that
might be a code change, a config change, or a one-off DB cleanup — not a
standardised output. The rated **Low** reflects this: the corpus might
never have a clean repeatable shape for diagnose, and the
`troubleshooting.md` static catalog already captures the highest-value
patterns without needing a driver skill on top. Realistic outcome: builds
as a thin tool (live log inspection + grep against troubleshooting.md)
or stays out.

**Why Low.** Valuable but open-ended and hard to shape into a repeatable
interview-driven process; the `troubleshooting.md` files already capture the
highest-value knowledge without needing a driver skill on top.

---

## Deliberately out of scope (considered, not planned)

- **Estimation / SoW / pricing.** Commercial, and `odoo-write-specifications`'
  `content_outline.md` explicitly excludes cost from specs. A pricing skill would
  cut against that boundary.
- **Standalone test-authoring (unit / tour suites).** Refers to *developer-
  written automated* tests (pytest / `HttpCase.start_tour`).
  `odoo-plan-development` already ships operational smoke + a testing manual; a
  full automated-suite skill is low marginal value until a client specifically
  requires a regression suite as a deliverable. Customer-facing manual UAT is a
  separate audience and shape — covered by `odoo-uat` above, not by this
  out-of-scope entry.
- **Odoo training / certification prep.** The audience (learners studying for
  an exam) doesn't fit the suite's `interview → artifact → validate` pattern —
  there's no consultant-produced deliverable to validate. Better served by
  Odoo's own learning platforms.
- **Change management / go-live runbook.** Covered by the combination of
  `odoo-configure` (config runbook) + `odoo-data-migration` (data loading +
  reconciliation) + the testing manual already produced by
  `odoo-plan-development`. A separate go-live skill would mostly orchestrate
  existing artefacts.
- **Dataset cleanup / health check.** Subsumed by `odoo-diagnose`'s reactive
  troubleshooting + `odoo-data-migration`'s reconciliation step. A standalone
  preventive-health-check skill would duplicate both with thinner scope.

---

*Revisit this file when scoping a new engagement: if the ask matches a candidate
above, that's the signal to graduate it from roadmap to `skills/<name>/`. Follow
[README.md § Adding a new skill](../README.md#adding-a-new-skill) when you do.*
