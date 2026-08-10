# Content Outline — `odoo-write-specifications`

Canonical structure for every spec docx the skill emits. Stage 1 lint ([`scripts/_lint_spec.py`](scripts/_lint_spec.py)) reads this file as the source of truth — add a section here and the lint enforces it; remove one here and the lint stops complaining about it.

Load on demand, only when the skill is mid-interview building the draft.

---

## Style principles (apply throughout the docx)

### 1. Business language first, technical identifiers parenthetical

The audience is **both** business stakeholders and the dev team.

- Lead every sentence with the user-facing concept ("Sales Order line"), not the Odoo technical name (`sale.order.line`).
- Technical name in parens, **once per concept per section**, only when the dev audience needs the anchor.
- No Odoo jargon in headings.
- Common Odoo verbs to soften in body prose: `_inherit` → "extending", `_compute` → "automatically calculated", `post_init_hook` → "runs once on first install", `@api.constrains` → "validation rule", `record rule` → "row-level access rule", `xpath` → "view inheritance".

### 2. Describe what changes, not what stays

- **Never list inherited fields, existing menus, existing access rights unchanged.**
- Name an existing concept once in business terms, then describe only the additions.
- The dividing line: if the reader needs to know about it to use the new functionality, include it. If they could find it by clicking around standard Odoo, leave it out.

### 3. Conciseness over completeness

- Tables over prose wherever the content is enumerable.
- Cells / bullets / rows trimmed to the essential — ≤20 words per row for criterion-style tables, ≤30 words for description-style cells.
- No padding paragraphs. No throat-clearing. No restating what a section header already says.

---

## Front matter (2, always present) + Top-level sections (5, always present)

The docx opens with **two unnumbered front-matter pages** (Cover, Table of Contents), then **five numbered top-level sections** (1–5) rendered as level-1 headings. Stage 1 lint enforces all five numbered sections are present and non-empty.

### Numbering scheme

- **Front matter is unnumbered**: the cover page and Table of Contents do not take a `1.` / `2.` prefix.
- **Top-level sections are numbered `1.` through `5.`** in the heading text itself (e.g. `1. Odoo Version`, `2. Business Case`). Stage 1 lint uses substring matching so the numeric prefix doesn't break section detection.
- **Section 3 has two sub-headings** numbered `3.1` and `3.2`.
- **Section 5 (Per-Workflow Detail)** numbers each workflow `5.{n}` and each of the 11 subsections under a workflow `5.{n}.{1..11}` — e.g. `5.1.1 Success Criteria`, `5.1.2 User Stories & Steps`, …, `5.2.1 Success Criteria` for the second workflow.

### Table of Contents

**The TOC must be POPULATED on disk — titles + page numbers visible — never a blank "right-click to update" field.** The builder renders it from an explicit ordered `(level, heading_text)` entry list (levels 1–3) derived from the same structure `build()` emits, so it can't drift from the headings. Each entry is a hyperlink to the heading's bookmark + a dot-leader tab + a `PAGEREF` page-number field; `make_heading` bookmarks every level-1–3 heading so those references resolve. The document carries `w:updateFields="true"` (see `set_update_fields`) so Word/Pages/LibreOffice recompute the page numbers on open — but the titles are real text and show even in viewers that don't refresh fields. A bare `TOC` field whose result is the placeholder string does NOT satisfy the contract.

### Front matter

| # | Section | Required content | Source |
|---|---------|------------------|--------|
| — | **Cover** | Title, subtitle (one-line description), prepared-by / role / client / companion-document (optional) / scope / date / version block. Centred, no body text. **No** Sponsor, Acceptor, or Alternatives-Considered fields. | Q1 (task code), Q2 (client), Q4 (type of development), interview metadata |
| — | **Table of Contents** | A **populated** TOC (Heading 1–3 titles + page numbers) rendered from an explicit entry list; clickable (bookmarks) and page numbers refresh on open (`updateFields`). NOT a blank field with a "right-click to update" placeholder. | Generated from the same heading structure the builder emits |

### Numbered top-level sections

| # | Section | Required content | Source |
|---|---------|------------------|--------|
| 1 | **Odoo Version** | Just the version number on a single line (e.g. `19.0`). No paragraph, no version-specific notes. | Q3 |
| 2 | **Business Case** | A concise 3-or-4-row table — `Problem` / `Affected role` / `Why it matters`, plus an optional `Out of scope` row (the builder reads `business_case.out_of_scope` and appends the row only when it's set) — pulled verbatim from the Q5 free-text brief (parsed into the three core dimensions; the out-of-scope row is added when the user explicitly bounded scope, typically during Critical Brief Evaluation Check 1). Each row ≤25 words; no padding paragraphs. The "why this exists" rationale for the dev team and the business stakeholder both. | Q5 (business need brief); optional out-of-scope from Check 1 |
| 3 | **Apps Impacted / New Apps Proposed** | Two short tables in business names, both widened to 3 columns to make customization-required functionally explicit: (a) `3.1 Impacted Standard Apps — App \| Objective (why we're touching it) \| Functional changes (what users see and behave differently)`; (b) `3.2 New Custom Apps — App \| Objective (business purpose) \| Key capabilities (what it enables)`. **Stay abstract** — every row is one **impact area** or one **capability abstraction** (e.g. "in-transit modelling between cities", "back-end approval gating"); do NOT enumerate fields, menus, models, or groups (those live in the per-workflow detail). If you find yourself listing more than two distinct items in a cell, you're re-stating §5 — collapse to the abstraction. | Per-workflow synthesis |
| 4 | **Functional Layout — Workflows** | A table listing the workflows with their 10–12-word summaries. One row per workflow named in Q6. **No** block / strip / sequential diagram at this level — workflows aren't necessarily sequential, the diagram is misleading. | Q6 |
| 5 | **Per-Workflow Detail** | One level-2 heading (`## 5.{n} <workflow name>`) per workflow named in Q6. Each contains the **11 mandatory table-based subsections** below (plus an optional Process Flow diagram) numbered `5.{n}.{1..11}` — every subsection describes **only what's new** for this workflow. | Per-workflow interview |

**No appendices.** The docx ends at Section 5.

**Explicitly NOT present** in the docx (removed for conciseness):

- Context / Preface section.
- Top-level Success Criteria section (moved to per-workflow subsection 1 — see below).
- Type of Development section (the per-category framing lived here).
- **Glossary appendix** (removed; tone rule #1 keeps technical jargon out of body prose, so a glossary is redundant).
- Acknowledgement page (no client/consultancy signature blocks).
- Anchor Pass — Open Nits appendix.
- Revisions / Version-history table.
- Alternatives Considered section.
- Sponsor / Acceptor metadata fields on the cover page.

The Open Nits, Glossary, and Acknowledgement removals are intentional: the docx is the spec, not a sign-off ceremony or a vocabulary lesson. Anchor pass findings still inform the draft (the user accepts/rejects each blocker), but no separate appendix.

---

## Per-workflow subsections (11 mandatory + 1 optional, every workflow)

Each workflow under Section 5 is a level-2 heading (`## 5.{n} <name>`). Underneath, the **11 mandatory subsections** appear as level-3 headings (`### Heading`), in the order below. An optional **Process Flow** diagram can prepend them when the workflow benefits from one (BPMN swimlane preferred over flat strip; see SKILL.md § BPMN diagram block).

### Strict-N/A discipline

Every subsection is either **filled** with content sourced from the per-workflow interview **or explicitly marked**:

```
N/A — <one-line specific reason this subsection doesn't apply to this workflow>
```

**Silent omission is rejected by Stage 1 lint. Vague reasons are also rejected:**

- ✅ `N/A — workflow extends existing Sales Order; no new model introduced`
- ✅ `N/A — standard Odoo credit-control flow unchanged for this workflow`
- ❌ `N/A — not applicable` *(rejected)*
- ❌ `N/A — not specified yet` *(rejected)*
- ❌ `N/A — TBD` *(rejected)*

The principle: if the reason can't be specific, the question wasn't asked thoughtfully. Re-ask before writing N/A. The docx's primary focus is the customization required — every N/A is documented as "standard Odoo applies, here's why".

**All subsections are table-based.** Prose paragraphs are allowed only when the subsection content can't be enumerated (e.g. a single Data Migration note). Default to tables; fall back to prose only when justified.

**Split compound triggers across rows.** In Trigger / Action / Outcome tables (especially Automated Behaviours and Business Rules), if a single row's Outcome needs *"For X..., for Y..."* framing to describe more than one scenario, **split into separate rows** — one per scenario — with the Trigger column carrying each scenario's specific condition. The row stays one-trigger-one-outcome, which scans cleanly and lets a dev write one branch at a time without untangling compound prose. ❌ One row with Outcome *"For warehouse-to-warehouse, destination = transit location; push rule creates the follow-on. For van requests with assigned warehouse, a single one-step transfer is created"* → ✅ Two rows: one for the warehouse-to-warehouse scenario, one for the warehouse-to-van scenario, each with its own Trigger + Outcome.

| # | Subsection | Required table shape | Role checklist (interview source) |
|---|------------|----------------------|-----------------------------------|
| 0 | **Process Flow** *(optional, before subsection 1)* | Optional. Renders one of two shapes: (a) a **BPMN swimlane diagram** when the workflow includes a `bpmn_diagram` block in its SPEC_DATA — actors as lanes, tasks with numbered step badges, exclusive gateways, labelled start/end events; (b) a **modern block diagram (flow strip)** when only `flow_strip` is set — rounded pills with numbered step badges and clean arrows, visually consistent with the BPMN diagram language (same Odoo-plum palette, same shape vocabulary; orthogonal 90° connectors and solid role sidebars on the BPMN). When Pillow is unavailable in the venv (bare-Python install that declined the install gate), the flow strip falls back to a legacy table-based renderer (`Step A → Step B → Step C`) — graceful degradation, not the primary path. (c) nothing if neither is present. Use BPMN when the workflow has ≥2 actors or a non-linear flow (decision gateway, error branch); use the flow strip for purely sequential single-actor workflows with ≥3 steps. See SKILL.md § BPMN diagram block + § Diagram-choice checkpoint. | derived from User Stories + actor inventory |
| 1 | **Success Criteria** | Table: `Criterion`, `How we measure it`. One row per workflow-aggregate outcome (the "this workflow is done when X" bar). Each row ≤20 words. Workflow-level, not per-step — per-step success rolls into the user story narrative in subsection 2. | business_analyst.md + consultant.md |
| 2 | **User Stories & Steps** | Table: `#`, `User Story`, `Actor`, `Step (what happens)`. One row per story-aligned step. Story written as "As a `<role>`, I want `<action>`, so that `<outcome>`". **Per-step Success Criterion column removed** — it rolled up to subsection 1 as workflow-aggregate criteria. | business_analyst.md |
| 3 | **New Models** *(renamed from "New Data Captured")* | Table: `Purpose`, `Name`, `Technical Name`, `Parent Menu`, `Views Required`, `Required Features`. Six columns. `Views Required` = comma-separated of `List, Kanban, Form, Pivot, Calendar, Graph`. `Required Features` = comma-separated of `Chatter, Activities, Archiving, Company Specific Records, Multi-currency`. Mark `N/A — no new model introduced; this workflow extends existing <model>` if no new model is added. | solution_architect.md |
| 4 | **New Fields & Information** | Table: `Model`, `Field Name`, `Captures`, `Type`, `Options/Remarks`, `Location/Visibility`. Six columns. `Type` carries the relation target inline for relational types (e.g. `Many2one → stock.lot`); blank/`Char`/`Integer`/`Boolean` for others. Only new fields. | solution_architect.md |
| 5 | **Navigation & Menus** | Table: `Menu label`, `Lives under`, `Who sees it`. Only new menus. | ux_ui.md |
| 6 | **Screens & Interactions** | Table: `Surface`, `Kind` (form / list / kanban / button / notification / status change), `What user sees or does`. **This combines what was previously Screens & Interactions plus User Touchpoints.** | ux_ui.md + business_analyst.md |
| 7 | **Automated Behaviours** | Table: `Trigger`, `Action`, `Outcome`. Plain language; no Odoo internals. **When the workflow commits / locks / reserves a resource, the inverse behaviours belong here too** — what `cancel` / `expire` / `unreserve` triggers and its outcome (frees the units, releases a stale hold, restores the commitment when stock is re-available). The forward action and its inverse are both rows; strict-N/A applies when the workflow introduces no such resource. (principle #15) | solution_architect.md + devops.md |
| 8 | **Business Rules & Validations** | Table: `Rule`, `Error message shown to user`. Both columns in business language. **Lock and contention rules live here when they apply**: who may no longer change a committed value after confirmation (with the message), and — if a finite resource can be claimed by more than one document — that it can't be double-committed plus what releases a stale claim. Strict-N/A when no such resource. (principle #15) | solution_architect.md + security.md |
| 9 | **Reports & Analytics** | Table: `Report`, `What it shows`, `Who reads it`, `Cadence`. Only new reports. | documentation.md + solution_architect.md |
| 10 | **Data Migration** | Table: `Existing data`, `What changes`, `Approach`. Only when existing populated data is touched. | data_migration.md |
| 11 | **Access & Permissions** | Two sub-tables: (a) `11.{n}.1 New Groups — Group \| Reason created \| What it achieves`; (b) `11.{n}.2 Existing Groups mentioned — Group \| Reason in spec \| Change`. Three columns each. Use the strict-N/A marker on the absent sub-table when only one applies. | security.md |

---

## Naming conventions inside the docx

- **User-facing labels first**: "Sales Order", "Quotation", "Workshop Bay".
- **Technical names in parens, first mention per section only**: "On the Sales Order line (`sale.order.line`), …". Lint warns when density is heavy.
- **Buttons**: bold, in quotes ("**Confirm**", "**Approve**").
- **Menu paths**: arrow-separated, in quotes ("Sales → Orders → Quotations").
- **No `xpath`, `_inherit`, `@api.depends`, `noupdate`, `post_init_hook`, `record rule`, `ACL`, `domain` in body prose** — soften to business equivalents. Use the technical word only inside the Glossary entry.

---

## What stays out of the docx

- **Implementation-time mechanics**: file paths, class names, decorators, manifest layout, view-XML.
- **Enumeration of existing Odoo behaviour**: existing menus, inherited fields, existing access rights.
- **Cost / commercial terms**.
- **Hosting / deployment specifics** (Odoo.sh project names, IP allowlists).
- **Code snippets** (Python / XML / CSV). State configuration values as prose.
- **Sponsor / Acceptor / Alternatives Considered / Revisions / Acknowledgement** — removed per conciseness pass.
