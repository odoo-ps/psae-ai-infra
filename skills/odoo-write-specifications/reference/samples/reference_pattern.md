# Reference Pattern — Annotated Spec Walk-through

Annotated walk-through of a real-world reference spec used as the visual + structural benchmark for this skill. The reference PDF itself is not shipped — what matters is the *shape and depth* the pattern demonstrates. Read this file to calibrate the level of detail the skill's output should aim for; never copy verbatim.

The reference was a multi-workflow Dealer Management System spec authored by a regional consultancy for a fleet-equipment client. Identifying details have been stripped — what's preserved here is the structural anatomy and the calibration cues.

---

## At-a-glance

- **~32 pages** total.
- **5 business workflows** (in the reference: Procurement, Sales, Helpdesk, Repairs, Accounting — any spec's workflows will be domain-specific).
- **Each workflow uses a uniform 5-block structure** (described below).
- **Phase markers** (Phase 1 baseline, Phase 2 polish) used throughout, colour-coded burnt orange for Phase 2.
- **Companion to** a parent Functional Scope document (the contractual scope reference). The spec is the execution map, not the scope itself.

This is the density target. A spec for a smaller engagement (one workflow, one phase) should emit a *similarly proportioned* document — same care per page, just fewer pages.

---

## What the reference does well (adopt)

- **Uniform per-workflow structure.** Every workflow uses the same five blocks: Flow strip → Step-by-step table → Customized development → Configurations → Accounting impact. The reader internalises the structure after the first workflow and skims subsequent ones efficiently. The skill's per-workflow subsection list ([`../content_outline.md`](../content_outline.md)) generalises this idea: 11 subsections, every workflow, always in the same order, N/A markers when one doesn't apply.
- **"How to Read This Document" up front.** Page 2 explicitly tells the reader what each block contains. The skill **omits** this — Context / Preface was removed in the conciseness pass; the table-based structure is self-explanatory.
- **Phase markers.** Default text is in scope ("Phase 1 is the spine"); Phase 2 polish is explicitly prefixed and visually distinguished. The reader always knows what's in vs deferred. The skill adopts the `▌ PHASE 2 —` convention.
- **Flow strip diagrams.** Each workflow opens with a one-line `A ▶ B ▶ C ▶ D` strip. Lightweight, renders anywhere, instantly orients the reader. The skill's per-workflow Process Flow subsection emits these.
- **Step-by-step tables with explicit Actor column.** Every step names *who* does *what*. The skill enforces this in the Step-by-step subsection.
- **Customized development is broken into four parallel categories**: Extra fields (per model), Automations, Customized views, New models. The skill's per-workflow subsections (New Data Captured, New Fields & Information, Screens & Interactions, Automated Behaviours) generalise these.
- **Accounting impact per workflow, plus a global summary.** The reference dedicates a sub-section per workflow AND a consolidated matrix in its Accounting section. The skill mirrors this by letting users name a dedicated "Accounting" workflow in Q7 when cross-workflow financial impact is material.
- **Cross-flow handover diagram near the end.** A table showing each handover between workflows as a system event. Adopt this for any spec with ≥3 workflows; the skill folds it into Section 5 (Functional Layout — Workflows) as additional rows or columns when applicable.
- **Critical end-to-end test scenarios.** A list of must-pass UAT scenarios spanning multiple flows. The skill's anchor pass (qa-anchor) recommends including a similar block when the spec has ≥2 workflows that interact.
- **Acknowledgement page.** Final page is a signature block (two-column: client + consultancy). Always emit this.

---

## What the reference does that the skill should NOT copy

- **No table of contents.** A 32-page document with no ToC is a navigation tax. The skill emits a ToC after the cover page (python-docx's `paragraph.add_run` of a `<w:fldSimple>` field).
- **No section numbering beyond manually-typed "1.1", "1.2".** Word's built-in multilevel list numbering is more reliable. The skill uses Heading styles bound to a multilevel list; numbers regenerate on every print.
- **Page-1 has no version-history block.** The skill also omits this — per the conciseness pass, no Revisions / Version-history table.
- **No glossary.** Business-side readers may not know `stock.lot`, `_inherit`, `noupdate`. The skill's glossary appendix (when ≥5 terms used) fills this gap — and is the **only** appendix in the docx.
- **Burnt-orange Phase 2 is the *only* colour accent.** This is fine for a single-phase-marker convention, but the skill should not introduce a *second* accent colour without a clear reason. One colour = one meaning.
- **Reference is technical-leaning; the skill output is more business-language.** The reference PDF freely uses model technical names like `stock.lot`, `_inherit`, `post_init_hook`, and `noupdate="1"` in body prose. The skill **inverts this**: user-facing labels lead every sentence ("Sales Order line", "Vehicle master record"), technical anchors go in parens only at the first mention per section, and Odoo-internal verbs (`_inherit`, `@api.depends`, `xpath`, `post_init_hook`, `record rule`, `ACL`) are soft-warned by Stage 1 lint when they appear in body prose. The reference's tone is fine for an internal consultancy deliverable; the skill's tone is broader because the same docx is read by procurement officers, finance managers, and sales reps who don't know what `_inherit` means.
- **Reference enumerates existing Odoo behaviour.** It lists "Standard Odoo Purchase: create purchase.order in 'Draft' state…", "Standard Odoo Inventory: stock.picking validated…", etc. — describing what standard Odoo already does as part of each step. The skill **only describes what's new** per [`../content_outline.md`](../content_outline.md) § Style principle #2. If a step uses standard Odoo behaviour unchanged, name it once in business terms ("warehouse validates the receipt") and move on — no enumeration of what standard Odoo already provides.

---

## Per-section calibration

What "good enough" looks like at the section level, calibrated against the reference. The skill emits **6 top-level sections** (vs the reference's freer-form structure); the conciseness pass removed Context / Preface, Business Case (replaced by Success Criteria), and Type of Development.

### Section 1 (Title / cover)

The skill follows Odoo's prescribed template cover: centred **Odoo logo**, Montserrat-Medium title (26 pt), grey subtitle (15 pt), a thin plum rule, then the left-aligned metadata block. Cover page contains **only** these elements — no body text, no preview, no Sponsor/Acceptor/Alternatives-Considered fields. (See [`../docx_styling.md`](../docx_styling.md) § Cover page.)

### Section 2 (Odoo Version)

The reference doesn't have an explicit "Odoo version" section. The skill emits a one-line section containing just the version number (e.g. `19.0`) — no paragraph, no version-specific notes.

### Section 3 (Success Criteria)

The reference's business case lives in the parent Functional Scope. The skill emits a **table** with `Criterion` and `How we measure it` columns — each row ≤20 words across both cells. Distils Q5a (problem) + Q5b (who) + Q5c (why) into testable success statements. Replaces the previous Business Case paragraphs.

### Section 4 (Apps Impacted / New Apps Proposed)

The reference scatters this across each workflow's "Configurations" block. The skill **consolidates** into Section 4 for at-a-glance visibility, as two short tables (impacted standard apps + new custom apps). Reuse-vs-net-new wording must be explicit, especially when the user overrode a Check-2 critique to build custom despite standard overlap.

### Section 5 (Functional Layout — Workflows)

Reference's "how the workflows fit together" page is the conceptual ancestor — but the skill emits **only a table** (workflow name + 10–12 word summary). The sequential block diagram was misleading because workflows aren't necessarily sequential; removed.

### Section 6 (Per-workflow detail)

The bulk of the document. Per-workflow subsections in the skill mirror the reference's five blocks plus extensions, all **table-based** after the conciseness pass. The 10-subsection skeleton ([`../content_outline.md`](../content_outline.md)) covers what the reference covered plus User Stories & Steps and Access & Permissions. Step-by-step + User Stories merged into one table; Screens & Interactions + User Touchpoints merged into one table.

---

## Density target

The reference's per-workflow detail averages ~6 pages per workflow at its looser typography (12 pt body, 22 mm margins). The skill uses the Odoo template's typography (11 pt body / 10 pt tables, **25.4 mm / 1-inch margins**, Montserrat-Medium headings, fit-content tables) — a touch more generous than the older tight layout, so expect roughly **~3–4 pages per workflow** for the same substantive detail. For a 5-workflow spec:

- Cover + Table of Contents + Section 1 (Odoo Version) + Section 2 (Business Case): ~2–3 pages
- Section 3 (Apps Impacted) + Section 4 (Workflows table): ~1 page
- Section 5 (5 workflows × ~3–4 pages each): ~15–20 pages

**Total: ~20–25 pages for a 5-workflow spec.** No appendices (Glossary / Acknowledgement / Open-Nits were removed). A 1-workflow spec might be 5–6 pages. The skill should not feel pressured to hit a length — depth is what matters. The 11-subsection skeleton scales naturally.

---

## What graduates this annotation

When the skill emits a spec that matches the reference's level of polish + density + clarity, this annotation can be retired (or moved to `samples/`-as-archive). Until then, anchor pass calibration uses this file as the "what good looks like" benchmark.
