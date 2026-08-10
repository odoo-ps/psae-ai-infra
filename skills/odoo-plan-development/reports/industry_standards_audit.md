# Industry Standards Audit — `odoo-plan-development` skill

**Date:** 2026-06-13
**Audit subject:** the `odoo-plan-development` skill as it stands after the Phase-1 calibration commit (`97fbda3`).
**Auditor:** Claude (Opus 4.7)
**Status:** Reference snapshot. Improvements deferred to future skill iterations, pending user prioritization. Not canonical structure — the canonical structure is [`../SKILL.md`](../SKILL.md) and [`../reference/samples/reference_pattern.md`](../reference/samples/reference_pattern.md).

## Purpose of this report

A point-in-time evaluation of the skill against external frameworks for engineering discipline, security, performance, and operability. The report exists to:

- Inform future improvements (which gaps are worth closing, in what order).
- Justify deliberate exclusions, so future iterations don't accidentally re-introduce removed sections without first re-reading the rationale.
- Provide a baseline for re-audit when the skill structure changes materially or when the underlying frameworks evolve.

Re-run the audit (or update this report in place) when:

- A new top-level section is added or removed from the Output Contract.
- The 15 anchors' drift patterns materially shift.
- A new Odoo major version requires re-calibration.
- A new external framework relevant to Odoo addon development is published.

---

## Frame of reference

Compared against four external reference points:

1. **SOLID principles** (Robert C. Martin) — object-oriented design discipline; particularly Single Responsibility, Liskov Substitution (relevant to `_inherit`), and Dependency Inversion (relevant to module deps).
2. **12-factor app** (Heroku, 2011) — operability discipline for backing services, config, logs, processes; relevant to the DevOps role.
3. **OWASP Top 10 (2021)** — web-application security baseline; relevant to the Security role.
4. **Google SRE workbook** — operability discipline at scale; relevant to cron resilience, external-call discipline, observability.

These four are widely-recognized in the engineering community Odoo consultants come from. They're not invoked as authorities; they're invoked as connection points between the skill's Odoo-specific discipline and the practitioner's existing knowledge.

---

## How the skill maps to each framework

### SOLID

| Principle | Where the skill enforces it |
|---|---|
| Single Responsibility | Role checklists separate concerns (consultant frames the problem; BA writes stories; SA maps to primitives; QA tests). The plan file's section sequence mirrors this. |
| Open/Closed | `_inherit` (extension without modification) is the default pattern; the SA checklist's "Default rule: prefer `_inherit` over a parallel model" is the LSP-friendly default. |
| Liskov Substitution | `_inherit` preserves the parent's contract; `_inherits` (delegation) when the new model has its own lifecycle. The SA checklist's mechanism table calls this out. |
| Interface Segregation | Less applicable in Odoo's ORM-centric world; partially reflected in not forcing models to inherit unnecessary mixins. |
| Dependency Inversion | Manifest `depends` is the explicit dependency declaration; the SA-anchor's depend-gap check enforces it. `ir.config_parameter` for external-service configs (DI for env-specific values). |

**Gaps**: The skill doesn't explicitly cite SOLID. Future iteration could add a one-line note in solution_architect.md mapping the Open/Closed → `_inherit` correspondence so the principle name resonates for SOLID-trained practitioners.

### 12-factor app

| Factor | Skill enforcement |
|---|---|
| I. Codebase | Git-managed addon under `custom_addons/`. |
| II. Dependencies | `__manifest__.py:depends` is the explicit declaration; SA-anchor audits. |
| III. Config | `ir.config_parameter` for env-specific values; devops-anchor flags hardcoded URLs/credentials. |
| IV. Backing services | Odoo's `mail.template` + external HTTP calls via `requests` with timeout; devops-anchor audits. |
| V. Build, release, run | Odoo.sh enforces this for hosted deployments (build hook → staging → prod). On-prem mirrors via `_create_instance.py` + canonical conf. |
| VI. Processes | Workers stateless modulo the DB + `ir.config_parameter`. Devops checklist names this implicitly. |
| VII. Port binding | `--workers`, `--cron-threads`, `--http-port` flags; documented in DevOps checklist. |
| VIII. Concurrency | Worker model scales horizontally (Odoo.sh's container model); cron-threads scale separately. |
| IX. Disposability | `--limit-time-cpu` / `--limit-time-real` / `--limit-memory-hard` kill misbehaving workers; respawn cleanly. |
| X. Dev/prod parity | Odoo.sh's staging branches enforce this; on-prem uses the same conf template across envs. |
| XI. Logs | `_logger` to stdout (12-factor compliant); devops-anchor flags `print(...)`. |
| XII. Admin processes | `odoo-bin shell`, migration scripts, `post_init_hook` — all run in the same image as the app. |

**Gaps**: The skill's coverage of 12-factor is implicit — the principles are spread across the DevOps and Solution Architect checklists without naming the factor. Future iteration could add a one-paragraph note in devops.md mapping the 12-factor names.

### OWASP Top 10 (2021)

| OWASP entry | Skill enforcement |
|---|---|
| A01 Broken Access Control | ACL CSV + `ir.rule` + portal vs internal user discipline. Security checklist + security-anchor. |
| A02 Cryptographic Failures | `ir.config_parameter` for secrets; no creds in plan / code / tests. Security checklist's secret-handling discipline. |
| A03 Injection | ORM `search()` with domain (never `cr.execute` with f-strings); `t-esc` not `t-raw`. Security checklist. |
| A04 Insecure Design | Threat modeling not formally part of the skill; partially addressed by the consultant's problem-framing discipline. |
| A05 Security Misconfiguration | Public routes have CSRF + rate-limit + input sanitisation reviewed. Security checklist. |
| A06 Vulnerable Components | Manifest `depends` declares explicit modules; upgrade via Odoo Upgrade Service keeps Odoo itself current. |
| A07 Identification and Authentication Failures | Portal vs internal user discipline; `auth_totp` 2FA for admin/finance groups. Security checklist. |
| A08 Software and Data Integrity Failures | Manifest version bumping + `noupdate` policy for data files. DevOps + Data Migration checklists. |
| A09 Logging and Monitoring Failures | `mail.thread` + `tracking=True` on PII; `_logger` discipline. Security + DevOps checklists. |
| A10 SSRF | External HTTP calls never use user-controlled host; allowlist required. Security checklist. |

**Gaps**: A04 (Insecure Design) is the thinnest — the consultant role does problem framing but not formal threat modeling. Future iteration could add a one-bullet "threat-model surface" question for compliance-sensitive addons.

### Google SRE workbook (observability + resilience)

| SRE concept | Skill enforcement |
|---|---|
| SLI / SLO / error budget | Not formally part of the skill; partially addressed by performance checklist's P50/P95 framing. |
| Four golden signals (latency, traffic, errors, saturation) | Performance checklist names latency budgets; cron / external-call discipline addresses errors + saturation. |
| Toil reduction | Studio-first prototyping replaces dev cycles; `post_init_hook` automation of `res.config.settings` reduces operator toil. |
| Postmortem | Troubleshooting.md is the running postmortem catalog; troubleshooting-anchor enforces "cite past lessons." |
| Cascading failure prevention | Cron without retry/failure mode = blocker; external call without timeout = blocker. Both prevent the worker-pool-exhaustion cascade. |

**Gaps**: SLI/SLO/error-budget framing is not explicit. Future iteration could add a one-paragraph note in performance.md mapping the latency-budget concept to SLO terminology.

---

## What the skill does well (no industry-framework gap)

- **Three-stage validation** (P2: static lint → install → operational smoke) is a custom invariant not borrowed from any framework — it's stricter than what 12-factor or SRE would require. The skill's claim: a passing install doesn't satisfy done; operational behaviour must be verified.
- **Architecture-aware execution** (P13: `local | odoo.sh | docker | bare_metal` detected at Q0) is Odoo-specific and well-shaped. No framework forced this; it emerged from the failure mode that Odoo.sh and on-premise have different scaffolding paths.
- **Anchor pass before `ExitPlanMode`** (15 anchors in parallel, one batched message) is a corpus-specific quality discipline that exceeds most industry CI pre-merge checks in coverage breadth.
- **Troubleshooting log as institutional memory** (4-line format, monotonic IDs, archive-90-day rule) outclasses the typical "wiki of incidents" pattern in most engineering orgs.

---

## What the skill explicitly does NOT do (justified exclusions)

- **No SOLID / 12-factor / OWASP citations in role checklists.** Per the calibration session, embellishment with framework names is bloat for Odoo consultants. Industry hooks were limited to 1 per role where load-bearing; the rest are connection points in this audit, not first-class content.
- **No anchor regression testing.** No CI harness feeds known-bad inputs to anchors to verify expected findings. Phase 1.3 produced documentation fixtures for this, but they had no consumer and were removed. If observed anchor drift becomes a real concern, build the executable harness directly — not static prose fixtures.
- **No formal threat-modeling step.** A04 OWASP coverage is implicit through the consultant's problem framing. Adding a STRIDE-style threat model question would suit compliance-heavy clients but is overkill for the typical Odoo customisation.
- **No SLI/SLO/error-budget formalism.** Performance checklist names latency budgets in P50/P95 vocabulary; the full SRE workbook discipline is out of scope.

---

## Tiered improvement backlog

### Tier 1 — low cost, immediate clarity

- Add a one-line SOLID note to solution_architect.md mapping Open/Closed → `_inherit` for SOLID-trained readers.
- Add a one-paragraph 12-factor cross-reference to devops.md.
- Add a one-line A04 (Insecure Design) threat-model hint to security.md for compliance-sensitive addons.

### Tier 2 — moderate

- Build an executable anchor regression harness (feed known-bad inputs, assert expected drift findings) if observed anchor drift in practice justifies the infrastructure.
- Add a "performance assumption" question to performance.md that ties P50/P95 latency budget to an explicit SLO statement.

### Tier 3 — speculative

- Add a formal STRIDE threat-model step in the consultant role for compliance-sensitive addons (only if customer demand surfaces).
- Add an SLI/SLO/error-budget formalism to performance.md (only if a specific deployment needs it).

---

## What changed between this audit and the next

This baseline:
- 15 anchors firing at `ExitPlanMode`.
- 11 role checklists calibrated against Odoo 19.0 with junior + senior coverage.
- Required-artifact sections in every checklist.

Re-audit triggers:
- Odoo 20 release (re-calibrate role checklist content).
- New role added or removed.
- A new external framework relevant to Odoo gains traction (e.g. CNCF observability standards if Odoo.sh adopts them).
