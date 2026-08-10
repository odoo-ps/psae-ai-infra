# Industry Standards Audit — `odoo-write-specifications` skill

**Date:** 2026-06-03
**Audit subject:** the `odoo-write-specifications` skill as it stood after the Q3↔Q5 reorder commit ([64b8543](../../) in the `skills/` repo).
**Auditor:** Claude (Opus 4.7)
**Status:** Reference snapshot. Improvements deferred to future skill iterations, pending user prioritization. Not canonical structure — the canonical structure is [`../reference/content_outline.md`](../reference/content_outline.md).

## Purpose of this report

A point-in-time evaluation of the skill against external specification frameworks. The report exists to:

- Inform future improvements to the skill (which gaps are worth closing, in what order).
- Justify deliberate exclusions, so future iterations don't accidentally re-introduce removed sections without first re-reading the rationale.
- Provide a baseline for re-audit when the skill structure changes materially or when industry frameworks evolve.

Re-run the audit (or update this report in place) when:

- A new top-level section is added or removed from the docx outline.
- The Stage 1 lint's `REQUIRED_TOP_LEVEL_SECTIONS` changes.
- The question sequence in `SKILL.md § Fixed Questions` materially shifts.
- A new industry framework relevant to ERP / Odoo specs is published.

---

## Frame of reference

Compared against five external reference points:

1. **IEEE 830-1998 / IEEE ISO IEC 29148** — the SRS canon.
2. **BABOK v3 / Volere Requirements Template** — business-analyst playbooks.
3. **ERP-implementation spec patterns** used by Big-4 and boutique Odoo partners.
4. **Agile spec patterns** — Cohn's user-story format, Gherkin / BDD acceptance criteria.
5. **Odoo's internal functional-analyst conventions** — the in-house bar this skill is implicitly chasing.

---

## What the skill does well (industry-strong or industry-leading)

| # | Strength                                                               | Why it's strong                                                                                                                                                                                                    |
| - | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1 | **Opinionated structure with mandatory subsections**             | Industry templates leave per-feature shape free-form, which produces specs that vary in depth and skip rigor. The 10 mandatory per-workflow subsections are equivalent to BABOK's elicitation framework, baked in. |
| 2 | **Builder-driven generation from `SPEC_DATA`**                 | Single source of truth — beats the standard "Word doc in SharePoint, edited live by 4 people" anti-pattern. Idempotent rebuilds + diffable Python state.                                                          |
| 3 | **"What's new only" rule + per-row word caps**                   | Combats the IEEE 830 "200-page spec nobody reads" failure mode. Forces signal-to-noise discipline.                                                                                                                 |
| 4 | **Stage 1 lint + 14-anchor quality review**                      | Most consultancies rely on peer review; this skill bakes structural and tone checks into the workflow.                                                                                                             |
| 5 | **Critical Brief Evaluation step (standard-Odoo overlap check)** | Genuinely best-in-class. Most consultancies transcribe what the client said and over-engineer. The "use standard Odoo first" forcing function is consulting maturity rare in templates.                            |
| 6 | **Business + technical dual-audience tone enforcement**          | IEEE 830 produces dev-readable specs; BABOK produces business-readable specs. Few templates address both. The tone rules + lint catch jargon leak.                                                                 |
| 7 | **Workflow-centric per-feature structure**                       | Better than IEEE 830's "Functional Requirements Section 3.x.y" tree, which fragments. Workflows map to user mental models.                                                                                         |

---

## Gaps vs industry baseline

Grouped by category. Severity:

- **HIGH** — gap means the spec can't legally or practically substitute for an industry spec.
- **MEDIUM** — gap creates risk.
- **LOW** — nice-to-have.

### A. Non-functional and quality requirements

| #  | Gap                                                                                                                                                                   | Severity                                | Note                                                                                     |
| -- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------- | ---------------------------------------------------------------------------------------- |
| A1 | **No Non-Functional Requirements (NFRs) section.** No performance targets, no scalability, no availability/uptime, no browser support, no accessibility (WCAG). | **HIGH**                          | IEEE 830 §5 mandates NFRs. Currently scattered across Business Rules + Access.          |
| A2 | **No security / compliance matrix.** GDPR, ZATCA/FATOORA (KSA), GST (India), SOC2, audit-logging requirements aren't surfaced.                                  | **HIGH** for regulated industries | The lint flags `ACL` as a jargon term but the underlying requirement isn't structured. |
| A3 | **No audit trail / logging requirements.** Who can see what, what's logged, retention period.                                                                   | **MEDIUM**                        | Per-workflow Access & Permissions covers role-based access; logging is silent.           |

### B. Scope and boundary

| #  | Gap                                                                                                                                                                                                              | Severity         | Note                                                                                            |
| -- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | ----------------------------------------------------------------------------------------------- |
| B1 | **No mandatory top-level Out-of-Scope statement.** Pilot01 has one (optional, under Success Criteria); the skill doesn't enforce it.                                                                       | **HIGH**   | The most common ERP-spec dispute is scope creep — explicit OOS is industry-standard insurance. |
| B2 | **No Assumptions / Dependencies / Constraints (ADC) section.** Pilot01 has Assumptions (optional). No "what external systems must be ready" (Dependencies). No "regulatory / technical / org constraints". | **HIGH**   | IEEE 830 §2.5 mandates this.                                                                   |
| B3 | **No Phasing / Roadmap section** when scope spans multiple releases. Cover has a `scope: Phase 1` field but no phase description.                                                                        | **MEDIUM** | Most engagements >3 weeks need this.                                                            |

### C. Stakeholders and accountability

| #  | Gap                                                                                                | Severity                                | Note                                                                                                                             |
| -- | -------------------------------------------------------------------------------------------------- | --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| C1 | **No Stakeholder / RACI matrix.**                                                            | **MEDIUM**                        | The cover has Prepared-by + Role + Client but no per-workflow stakeholder mapping. RACI is BABOK 9.1 standard.                   |
| C2 | **No Sign-off / Acknowledgement page.** Removed in the conciseness pass.                     | **HIGH for contract-grade specs** | Functional specs frequently become contract exhibits; sign-off is the enforcement mechanism. The skill explicitly excludes this. |
| C3 | **No Document Control / Version history.** Removed earlier. Cover has one `version` field. | **MEDIUM**                        | Hard to audit who changed what and when across iterations.                                                                       |

### D. Risk and decisions

| #  | Gap                                                                                                                                                                                            | Severity         | Note                                                                                  |
| -- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | ------------------------------------------------------------------------------------- |
| D1 | **No Risks / Mitigations section.**                                                                                                                                                      | **MEDIUM** | PMBOK basics. Even a 3-row global risk table would catch "this might fail because X". |
| D2 | **No Decision Log** (date, decision, rationale, approver). Open Nits was removed as process noise — fair — but a Decision Log is different and adds traceability for long engagements. | **MEDIUM** |                                                                                       |
| D3 | **No Open Questions / TODO surface in the docx.** The lint blocks `TODO` strings; the skill has no positive surface for "we haven't resolved this yet".                                | **LOW**    | Implicit in `Assumptions`, but doesn't promote questions to a tracked artifact.     |

### E. Acceptance and testing

| #  | Gap                                                                                                                                                      | Severity         | Note                                                              |
| -- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | ----------------------------------------------------------------- |
| E1 | **Acceptance criteria bundled into User Stories table** ("Success Criterion" column). Industry/Agile separates ACs into Given/When/Then (Gherkin). | **MEDIUM** | One user story typically has 3–5 ACs; one column conflates them. |
| E2 | **No Test Strategy / UAT plan.**                                                                                                                   | **MEDIUM** | What gets tested, how, by whom, sign-off mechanism.               |
| E3 | **No Definition of Done per workflow.**                                                                                                            | **LOW**    | Agile concept; helpful when teams iterate.                        |

### F. Integration and interfaces

| #  | Gap                                                                                                                                                                         | Severity                                   | Note                                                          |
| -- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------ | ------------------------------------------------------------- |
| F1 | **No Integration / Interfaces section.** External-system interactions (HubSpot, Salesforce, banking APIs, e-invoicing portals) end up buried in Automated Behaviours. | **HIGH for integration-heavy specs** | Industry ERP specs always carve this out.                     |
| F2 | **No data model diagram or entity-relationship overview.** Per-workflow "New Data Captured" exists but no spec-level data picture.                                    | **MEDIUM**                           |                                                               |
| F3 | **No wireframes / mockups support.** The skill produces a docx but has no provision for embedding screen designs or linking Figma.                                    | **MEDIUM**                           | Screens & Interactions table describes screens in prose only. |

### G. Process / business

| #  | Gap                                                                                                                                        | Severity         | Note                                                     |
| -- | ------------------------------------------------------------------------------------------------------------------------------------------ | ---------------- | -------------------------------------------------------- |
| G1 | **No spec-level Process Flow / BPMN.** Optional per-workflow flow strip exists but only as a flat arrow chain — not a true diagram. | **MEDIUM** |                                                          |
| G2 | **No Glossary upfront** — only as a conditional appendix (≥5 terms).                                                               | **LOW**    | Most industry specs put it at the front for orientation. |
| G3 | **No Training / Change Management section.** Common for ERP rollouts.                                                                | **LOW**    |                                                          |
| G4 | **No global Reports & Analytics view.** Per-workflow only. A "what dashboards do we need across the spec?" view is missing.          | **LOW**    |                                                          |

### H. Innovation risks (things the skill does that industry doesn't, with tradeoffs)

| #  | Risk                                                                                                                                                                              | Note                                                                                         |
| -- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| H1 | **Q5 free-text brief parsed by the skill.** Innovative; risk is parse misses nuance the user thought was clear. Most industry templates use structured Business Case grids. | Consider keeping free-text as default but offering a structured opt-in.                      |
| H2 | **Slug auto-derivation removes user control.** Friction reduction is good; loss of override is a tradeoff.                                                                  | Consider surfacing the derived slug for one-shot confirmation OR offering `--manual-slug`. |
| H3 | **Per-row word caps (≤20, ≤25, ≤30 words).** Good for conciseness; risks dropping nuance for complex requirements.                                                       | No per-cell override path.                                                                   |
| H4 | **14-anchor pass against a docx.** Novel and expensive. Industry uses peer review. Anchors may produce noise on subjective issues.                                          | Reasonable as a one-time quality check, less so as a per-iteration gate.                     |
| H5 | ~~**TOC requires Word "Update Field"** on first open.~~ **RESOLVED 2026-06-13** — the TOC is now rendered POPULATED on disk (titles + page numbers via bookmarks/PAGEREF) with `updateFields=true`; no manual update, and titles show even in non-refreshing viewers. | ~~Friction. Pages auto-populates; Word doesn't always.~~ Closed.                              |

---

## Recommendations — prioritized

### Tier 1 — High value, low cost (highest-leverage additions)

1. **Add mandatory Out-of-Scope as Section 3** (push Success Criteria → 4, etc.) — or merge as a `3. Scope` section with `In Scope` + `Out of Scope` sub-tables. Industry's #1 spec-dispute defuser.
2. **Add Assumptions / Dependencies / Constraints (ADC) as Section 4** (or merge into Scope). Three short tables. IEEE 830 §2.5 equivalent.
3. **Add Non-Functional Requirements as a new top-level section** (between Apps Impacted and Functional Layout). One table with rows like Performance / Availability / Security / Localisation / Browser support / Accessibility — each with a target.
4. **Split "Success Criterion" out of User Stories** into a separate `Acceptance Criteria` column or sub-table per story, in Given/When/Then style. Aligns with Agile + BDD norms.
5. **Add Risks / Mitigations table** — either global (one table) or per-workflow. Even 3 rows changes the negotiation.
6. **Promote Glossary from conditional appendix to mandatory Section 2** (before Business Case) — even short specs benefit from upfront term definitions.

### Tier 2 — Medium value, moderate cost

7. **Re-introduce Sign-off page as an optional final appendix** (not the first page that was rejected). One client + one consultancy signature block. Contract-grade insurance.
8. **Re-introduce Document Control as a compact 4-row table on the cover or last page** (Version / Date / Author / Change summary). Audit trail without process noise.
9. **Add Integration / Interfaces subsection** as the 11th per-workflow table, OR as a Section 5.5. Critical for integration-heavy specs.
10. **Add Stakeholders / RACI** matrix — global table, not per-workflow.
11. **Add Test Strategy / UAT section** as Section 7 (before Per-Workflow Detail), or as an 11th per-workflow subsection. Even a 5-row table on test approach helps.
12. **Add lightweight Effort sizing per workflow** in the Section 5 Functional Layout table — T-shirt size column (S/M/L/XL). Not dollars; just signal.
13. **Support wireframe references** — add an optional `Wireframes / Mockups` row pointing to Figma / Excalidraw URLs, within the Screens & Interactions table or as an 11th subsection.

### Tier 3 — Strategic / architectural

14. **Decision Log appendix** — date, decision, rationale, approver. Especially valuable for engagements >4 weeks.
15. **Traceability Matrix appendix** — business need → workflow → user story → acceptance criterion. Demonstrates spec rigor; helps QA.
16. **Phasing section** — when the engagement spans multiple releases.
17. **Compliance / Regulatory matrix** — when client is in a regulated jurisdiction. Templated by region (EU/GDPR, KSA/ZATCA, India/GST, US/SOX).
18. **Spec-level Process Flow diagram support** — embedding a Mermaid / BPMN / swimlane image (Excalidraw or PlantUML link).

### Tier 4 — Toggles / overrides (low cost, gives flexibility)

19. **`--full-mode` flag** — emit the IEEE 830 / 29148 full template for clients who require comprehensive docs. Current default stays as "concise mode."
20. **`--manual-slug=...` flag** — let users override the auto-derived slug.
21. **`--structured-brief` flag** — switches Q5 from free-text to a structured Business Case grid (Problem / Stakeholder / Impact / Current state / Desired state / Benefit).
22. **Per-cell word-cap override** — allow `"long_form": true` on a row to bypass the cap for complex requirements.

---

## Deliberate exclusions — leave as-is (tradeoffs working)

These were either explicitly removed in earlier iterations or are intentional boundaries. Future maintainers should re-read the rationale before reverting any of them.

- **"What's new only" rule.** Excellent against IEEE 830 bloat.
- **Per-row word caps as the default.** Good signal-to-noise.
- **Excluding cost / commercial terms.** Right boundary.
- **Excluding code snippets.** Right boundary — this is a functional spec, not a tech spec.
- **Builder + `SPEC_DATA` model.** Architecturally sound.
- **Plan-mode exemption + incremental drafting.** UX win.
- **Critical Brief Evaluation.** Best-in-class differentiator; keep it.
- **Q3 / Q5 ordering** (technical framing before business brief). Counter-intuitive but works once you see it: locks the technical envelope before the business narrative drifts.

---

## Concrete sample renderings (based on Pilot01)

Each of the three highest-leverage additions (Tier 1.1, 1.3, 1.4) rendered with Pilot01's existing `SPEC_DATA` to show what the section would look like in practice. Section numbers below assume all three additions land — final ordering is a separate decision.

### Sample A — `§3 Scope` (replaces Pilot01's optional `out_of_scope` block; adds explicit `in_scope` mirror)

#### 3.1 In Scope

| Workflow                            | Coverage                                                                                                                     |
| ----------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Lot/Serial Selection on Sales Order | Single-warehouse, single-company; lot picking at the Sales Order line; reservation carried through to the resulting delivery |

#### 3.2 Out of Scope

| Item                                                                 | Reason / Disposition                                                                                                 |
| -------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| Backorders and partial-delivery re-allocation of lots                | Standard Odoo backorder logic continues to govern; the pilot does not override re-pick behaviour on backorder splits |
| Splitting a single order line across lots in more than one warehouse | Multi-warehouse lot allocation is a Phase 2 candidate; the pilot is single-warehouse only                            |
| Returns / RMA lot handling                                           | The standard Odoo return wizard governs; lot reversal on returns is out of scope for the pilot                       |
| Lot selection for kit or BoM components on the order line            | Component-level lot picking is a downstream warehouse decision; the order line stops at the parent product           |

*Source: existing `out_of_scope` block in Pilot01's SPEC_DATA. The `In Scope` row is synthesised from `workflows[0].summary` to enforce the in/out pairing.*

### Sample B — `§6 Non-Functional Requirements` (new section between Apps Impacted and Functional Layout)

| Category                  | Requirement                                                                 | Target                                                                             | Notes                                                                               |
| ------------------------- | --------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| **Performance**     | Lot/serial selector populates the dropdown                                  | < 1 second for products with up to 500 in-stock lots                               | Selector limits to `free_qty > 0` server-side to keep the result set bounded      |
| **Performance**     | Order confirmation validation (every line has a valid allocation) completes | < 2 seconds for orders with up to 100 lines                                        | Validation runs server-side on confirm, not per-keystroke                           |
| **Concurrency**     | Two sales reps cannot reserve the same lot/serial for separate orders       | Second confirmation fails atomically with a clear error naming the conflicting lot | No race window — reservation check is part of the same transaction as confirmation |
| **Availability**    | No new uptime target                                                        | Inherits Odoo.sh standard SLA for the host instance                                | —                                                                                  |
| **Browser support** | Sales rep desktop browsers                                                  | Latest two versions of Chrome, Edge, Safari, Firefox                               | No mobile UX in the pilot                                                           |
| **Accessibility**   | Lot selector keyboard-navigable                                             | WCAG 2.1 Level AA conformance for the many2one widget                              | Inherits Odoo's standard widget — no custom UI needs separate audit                |
| **Localisation**    | Lot labels render unmodified                                                | N/A — lot identifiers are language-neutral                                        | Selector chrome (labels, errors) follows existing Odoo translation                  |
| **Security**        | Lot selector visibility                                                     | Visible only to users with `sales_team.group_sale_salesman` or higher            | Aligns with existing SO-line edit rights                                            |
| **Auditability**    | Lot allocation changes are logged                                           | Every change recorded in the SO line's chatter via standard tracking               | No separate audit log required                                                      |
| **Data retention**  | N/A — no new retention requirement                                         | N/A                                                                                | Inherits Odoo standard retention                                                    |
| **Compliance**      | N/A — no regulated-industry impact                                         | N/A                                                                                | No GDPR PII, no e-invoicing change, no tax-engine impact                            |

*Source: synthesised from workflow nature (sales-line UI + reservation reads), `apps_impacted` (Sales + Inventory), and Pilot01's `who: Sales rep / order desk`. Compliance row marked N/A — but stage-1 lint would still require the row, not silent omission.*

### Sample C — `§8.1.2 Acceptance Criteria` (new per-workflow subsection between User Stories & Steps and New Data Captured)

| AC #  | Given                                                                                              | When                                                     | Then                                                                                                             |
| ----- | -------------------------------------------------------------------------------------------------- | -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| AC1.1 | A Sales Order line for a lot-tracked storable product                                              | The sales rep opens the lot/serial selector on that line | Only lots with `free_qty > 0` for the product appear in the dropdown                                           |
| AC1.2 | A Sales Order line with a chosen lot                                                               | The Sales Order is confirmed                             | The resulting delivery reserves that exact lot — not Odoo's auto-assigned one                                   |
| AC1.3 | A lot becomes fully reserved by another order between selection and confirmation                   | The current Sales Order tries to confirm                 | Confirmation fails with a clear error naming the conflicting lot                                                 |
| AC1.4 | A Sales Order line with partial lot allocation (e.g. 5 units, 3 allocated to lot A, 2 unallocated) | The Sales Order is saved as draft                        | Save succeeds; the order remains in draft with the partial allocation preserved                                  |
| AC1.5 | A Sales Order line with partial lot allocation                                                     | The Sales Order is confirmed                             | Confirmation fails with an error requiring full allocation before proceeding                                     |
| AC1.6 | A lot whose `free_qty` drops to zero (consumed by another flow) while the rep is on the line     | The rep re-opens the selector for that line              | The depleted lot no longer appears in the dropdown                                                               |
| AC1.7 | A Sales Order delivery has been created from a confirmed order with chosen lots                    | The warehouse user opens the delivery                    | The lot field on the delivery move line is pre-populated with the lot chosen on the SO line; no re-pick required |
| AC1.8 | An order line for a non-lot-tracked product (`tracking = 'none'`)                                | The rep edits the line                                   | The lot/serial selector is hidden — standard behaviour preserved                                                |

*Source: synthesised from Pilot01's existing 7-row `success_criteria` block. Mapping: AC1.1↔SC1+SC2, AC1.2↔SC3, AC1.3↔SC5, AC1.4↔SC7-draft-half, AC1.5↔SC7-confirm-half, AC1.6↔SC6, AC1.7↔SC4, AC1.8 is implied negative-path coverage from `out_of_scope[3]`.*

#### Sizing impact on Pilot01 specifically

| Section                                                   | Approx. rows  | Approx. page growth                                                                |
| --------------------------------------------------------- | ------------- | ---------------------------------------------------------------------------------- |
| §3 Scope                                                 | ~5            | ~½ page                                                                           |
| §6 NFRs                                                  | ~11           | ~1 page                                                                            |
| §8.1.2 Acceptance Criteria (per workflow; Pilot01 has 1) | ~8            | ~1 page                                                                            |
| **Total**                                           | **~24** | **~2½ pages** added to the current ~10–12 page Pilot01 docx (≈25% growth) |

That sits in the right ballpark for "contract-grade without bloat."

---

## Bottom line

The skill is **above industry baseline for concise functional specs** (what BABOK calls "lean" requirements) and **below industry baseline for contract-grade or compliance-grade specs** (what IEEE 830 / 29148 demand). The deliberate exclusions — sign-off, version history, NFRs — are the right calls for a 30-minute interview producing a 20-page docx, but they bite when the spec needs to anchor a 6-month engagement or pass a regulated-industry audit.

**The three highest-leverage additions** (Tier 1.1, 1.3, 1.4) would close roughly **60% of the gap** to industry baseline without bloating the docx — at the cost of ~25% page growth on a typical spec like Pilot01.

---

## Re-audit checklist

When this report is next reviewed:

- [ ] Are the five reference frameworks still the right benchmark? (Check for newer IEEE / ISO / BABOK / Odoo editions.)
- [ ] Have any Tier 1 items been implemented? If so, move them out of "Gaps" and into "Strengths" or "Deliberate exclusions kept as-is".
- [ ] Have any Tier 4 toggles been implemented? Update the "Innovation risks" section accordingly.
- [ ] Has the docx outline changed materially? Re-render the Pilot01 samples to match.
- [ ] Are the deliberate exclusions still defensible? Re-read the rationale and reconfirm or revise.
