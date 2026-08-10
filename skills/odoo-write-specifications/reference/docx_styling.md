# Docx Styling — `odoo-write-specifications`

The visual layer of the 7 C's of communication. The builder script ([`scripts/_build_spec.py`](scripts/_build_spec.py)) applies these to every spec the skill emits so successive docs feel like they came from the same publishing pipeline. Hand-editing the docx vanishes on next regen (P1) — change values here and in the builder, not in Word.

**Source of truth: Odoo's prescribed "Generic document" template.** The type ramp, colour discipline, margins, and header/footer below mirror that template's `word/styles.xml` — a monochrome grey heading ramp set in **Montserrat Medium**, **Open Sans** body, the Odoo brand **plum** (`#714B67`) as the single structural accent, and the Odoo logo in the running header. The annotated reference pattern at [`samples/reference_pattern.md`](samples/reference_pattern.md) shows the depth of content; the Odoo template governs the look.

---

## Page setup

- **Paper**: A4 (210 × 297 mm). Single source — never mix Letter.
- **Margins**: **25.4 mm (1 inch) on all four sides** — matches the Odoo template (1440-twip margins). Usable column ≈ 159 mm; `make_table()` computes fit-to-content widths so even the 6-column field tables stay inside it.
- **Header (every page except the cover)**: the running label `<task-code> — <client-name> — Functional Specification` in italic 8 pt grey (`#666666`), left-aligned, with the **Odoo logo** right-aligned on the same line and a thin plum rule below. The cover (first page) suppresses the running header — its logo sits in the cover body instead.
- **Footer (every page including cover)**: 8.5 pt grey (`#666666`), centred, `Confidential — <client> & <consultancy>  |  Page N of T`, over a thin plum rule. Page numbers are live `PAGE`/`NUMPAGES` fields. (We keep the spec's confidentiality footer rather than the template's `www.odoo.com` marketing line — these are client deliverables.)

The header/footer are wired by `setup_page_furniture(doc, spec_data, output_path)`; the logo asset travels at [`assets/odoo-logo.png`](assets/odoo-logo.png) (the skill copies it into each spec's `_reference/` at scaffold time so the builder finds it as a sibling).

---

## Type ramp

Two faces, mirroring the Odoo template: **Montserrat Medium** for every heading and the cover title, **Open Sans** for body and tables. Weight on headings comes from the *Medium* face itself — headings are **not** bolded on top (matches the template's heading `rPr`).

| Use | Family | Size | Weight | Colour |
|-----|--------|------|--------|--------|
| Cover title | Montserrat Medium | **26 pt** | medium | `#21272B` |
| Cover subtitle | Open Sans | **15 pt** | regular | `#666666` |
| Body | Open Sans (fallback: Calibri) | **11 pt** | regular | `#21272B` |
| Table body cell | Open Sans | **10 pt** | regular | `#21272B` |
| Inline technical anchor (sparingly, in parens) | JetBrains Mono (fallback: Consolas) | **9.5 pt** | regular | `#21272B` |
| Heading 1 (top-level §) | Montserrat Medium | **20 pt** | medium | `#21272B` |
| Heading 2 (per-workflow) | Montserrat Medium | **16 pt** | medium | `#21272B` |
| Heading 3 (subsection) | Montserrat Medium | **14 pt** | medium | `#434343` |
| Heading 4 (rare; sub-subsection) | Montserrat Medium | **12 pt** | medium | `#666666` |
| Table header | Open Sans | **10 pt** | bold | `#FFFFFF` on plum fill |
| Running header | Open Sans | 8 pt | italic | `#666666` |
| Footer / caption | Open Sans | 8.5–9 pt | regular | `#666666` |

Sizes taper — cover title 26 → H1 20 → H2 16 → H3 14 → H4 12 → body 11. Colour darkens-to-lightens down the ramp (`#21272B` → `#434343` → `#666666`), exactly as the template prescribes. The "shouting at every level = shouting at none" rule still holds; the hierarchy now reads through size **and** ink weight.

> **Font availability.** The docx *names* Montserrat Medium / Open Sans (it does not embed them). Odoo workstations ship both, so they render natively; a host lacking them substitutes a fallback (Calibri-class). The diagram PNGs fall back to Helvetica/Arial at render time. Font embedding is a possible future enhancement, not required for the Odoo audience.

---

## Colour palette

| Use | Hex | Notes |
|-----|-----|-------|
| Strong ink | `#21272B` | Cover title, Heading 1–2, body text, TOC level-1 |
| Medium ink | `#434343` | Heading 3, TOC level-2/3 |
| Muted ink | `#666666` | Heading 4, subtitle, captions, running header, footer |
| Plum (brand accent) | `#714B67` | Table-header fill, thin rules, first-column emphasis, BPMN/flow shape language. The plum of the Odoo logo's first "o". |
| Pale plum | `#F1ECEF` | Banner / alternating-row tints (used sparingly) |
| White (on plum) | `#FFFFFF` | Table-header text |
| Table border | `#B7B7B7` | Thin (0.5 pt) |
| Phase-2 (or beyond) | `#B45309` burnt orange | Items prefixed with `▌ PHASE 2`. A **semantic** colour, deliberately distinct from the brand plum. |
| Caution / risk callout | `#FFF2CC` fill, `#8A6D00` text | Sparingly — for material risks only |
| Success end (diagrams) | `#15803D` green | BPMN success end-event ring |

One colour = one meaning. The plum is the **brand/structure** accent (headings stay grey; plum carries tables, rules, and diagram shapes); burnt orange is **Phase-2 / caution** only; green is **success** only. Headings are never plum, and plum is never used for a warning.

---

## Spacing

- **Before heading 1**: 20 pt. **After**: 6 pt. (Matches the template's 400/120-twip heading spacing.)
- **Before heading 2**: 14 pt. **After**: 6 pt.
- **Before heading 3**: 10 pt. **After**: 4 pt.
- **Body paragraph spacing**: 0 pt before, 4 pt after. **Line spacing 1.15.**
- **Bullet lists**: 0 pt before each item, 2 pt after. Indent 6 mm per nesting level.
- **Tables**: cell padding **2 pt top/bottom, 4 pt left/right.** Cells are content-sized — no minimum row height.

The builder honours these via `python-docx`'s `paragraph_format.space_before` / `space_after`. With the template's 1-inch margins and 11 pt body, a 5-workflow spec runs a little longer than the older tight layout — the prescribed look is the priority.

---

## Tables

Tables carry most of the spec's information density — after the conciseness pass, nearly every per-workflow subsection IS a table. Conventions:

- **Header row**: plum fill (`#714B67`), white text (`#FFFFFF`), bold, 10 pt. Repeats across page breaks (`tblHeader` property).
- **Body rows**: 10 pt body text. Alternate-row fill OFF (cleaner against the body text). Use it only for very long tables (>20 rows) where eye-tracking benefits.
- **Borders**: thin (0.5 pt), colour `#B7B7B7`, on all sides. No double borders.
- **Column widths**: **fit-to-content** — narrow columns shrink, prose columns get the remainder of the row width. Avoid `autofit` (Word/Pages render it inconsistently); the builder computes content-sized widths in `make_table()`. Tables never overflow the right margin.
- **First column ("#" or short label)**: bold body text, plum `#714B67`.
- **Inline technical anchor** (parenthetical model/xml-id): monospace (JetBrains Mono), 9.5 pt.

The builder provides a `make_table(rows, header_row=True, first_col_emphasis=True)` helper that wires the above automatically.

---

## Process visuals (per-workflow) — flow strips & BPMN

Each per-workflow section opens with a process visual: a **flow strip** for a purely sequential single-actor flow, or a **BPMN swimlane** when there are ≥2 actors or a decision/branch. Both are PIL-rendered PNGs sharing one visual language (rounded plum-outlined cards, numbered step badges, accent top-stripe, clean arrows). See SKILL.md § BPMN diagram block for the BPMN schema and routing.

- **Flow strip** — `render_flow_strip_image` draws rounded pills with a plum accent top-stripe, a numbered step badge, the step label, and plum arrows between pills. `make_flow_strip_diagram` embeds it.
- **BPMN swimlane** — `render_bpmn_image` draws solid plum role sidebars, alternating lane tints, lane dividers, an outer pool frame, plum task cards, exclusive gateways, start/end events, and **orthogonal (90°) connectors**. The diagram's title + subtitle are emitted as real docx text above the image (`make_diagram_heading`) so they stay at true point size; the image carries the lanes only.
- **Readable on the page.** Both renderers work in pixels at `_BPMN_DPI` (220) and are embedded at native width capped to the content column (`_diagram_width`) — not stretched to a fixed width, which used to crush labels to a few points.
- **Legacy fallback** — when Pillow is unavailable, `make_flow_strip(steps)` renders a table-based strip (white pills, plum border, numbered prefixes, `→` connectors). Graceful degradation only.

---

## Cover page

Centred block in the upper third of the page:

1. **Odoo logo** — centred, ~22 mm tall, from [`assets/odoo-logo.png`](assets/odoo-logo.png).
2. **Title** — Montserrat Medium, **26 pt**, `#21272B`, centred (`<client> — <functionality>`).
3. **Subtitle** — Open Sans, **15 pt**, `#666666`, centred. One line (e.g. "Functional Specification").
4. **Horizontal rule** — thin plum (`#714B67`) line under the subtitle.
5. **Metadata block** — 11 pt Open Sans `#21272B`, left-aligned within the cover's centred column. Lines:
   - `Prepared by: <name>`
   - `Role: <title>, <consulting firm>`
   - `Client: <client name>`
   - `Companion to: <parent document name>` *(optional; include when the spec is a child of a Functional Scope or similar)*
   - `Scope: <Phase 1 | Phase 1+2 | etc>`
   - `Date: <Month Year>`
   - `Version: <X.Y>`

No body text on the cover. The running header is suppressed on the cover; the footer (confidentiality + page number) is present. Page break to the Table of Contents right after.

---

## Phase markers

When the spec covers multiple phases (Phase 1 baseline + Phase 2 enhancements, as in the reference PDF), default content stays unmarked. Phase 2+ content prefixes with:

```
▌ PHASE 2 — <phrase>
```

The `▌` is U+2590 (RIGHT HALF BLOCK) in burnt-orange (`#B45309`), followed by the phase label and an em-dash, then the content. The builder's `add_phase_marker(text, phase=2)` helper renders this consistently.

Stage 1 lint can confirm Phase markers only appear at headings or table-row starts, never mid-sentence.

---

## The 7 C's, enforced visually

The styling rules above are not arbitrary — each maps to one of the 7 C's:

| C | Visual rule that enforces it |
|---|------------------------------|
| **Clear** | Two-face type system (Montserrat Medium headings / Open Sans body); high-contrast grey-on-white headings; user-facing labels everywhere in body prose; technical names only in parentheses on first mention, set in monospace to signal "this is a literal identifier, not prose." |
| **Concise** | 4-line paragraph soft cap (lint-checked); table-first layout; bullet form for lists. |
| **Concrete** | Business-language headings + only-what's-new content force the writer to commit to user-visible behaviour, not abstract design language. The lint also rejects placeholder strings (`TODO`, `TBD`, `Lorem ipsum`). |
| **Correct** | Phase markers (`▌ PHASE 2`) prevent mid-document drift between in-scope and out-of-scope items. Anchor pass + Stage 1 lint also enforce this. |
| **Coherent** | Type ramp + spacing scale + Odoo template palette + the logo header = visual continuity from cover to last page. The reader trusts the document because every page feels like an Odoo document. |
| **Complete** | Section heading numbering (1 → 5) + per-workflow N/A markers → no missing surfaces. Lint enforces. |
| **Courteous** | Restrained palette (grey ink + plum accent + white + the logo); no emoji in headings; no exclamation marks; no first-person ("we'll do X" → "X is done"). |

---

## Builder hooks

The `_build_spec.py` skeleton exposes these helpers (signatures only — the implementation lives in the script):

- `setup_page_furniture(doc, spec_data, output_path)` — wires the Odoo-logo running header + confidentiality footer (different first page).
- `make_cover(doc, title, subtitle, metadata, logo_path)` — renders the cover page (logo, Montserrat title, rule, metadata).
- `make_heading(doc, text, level)` — binds the `Heading {level}` style and applies the Montserrat-Medium / grey-ramp run formatting.
- `make_table(doc, rows, header_row=True, first_col_emphasis=True)` — standard table (plum header fill, fit-to-content widths).
- `make_diagram_heading(doc, title, subtitle_lines)` — process-diagram title + subtitle as real docx text above the embedded image.
- `render_bpmn_image(data, path, draw_header=False)` / `make_bpmn_diagram(doc, path, caption)` — BPMN swimlane PNG + embed.
- `render_flow_strip_image(steps, path)` / `make_flow_strip_diagram(doc, path)` — flow-strip PNG + embed; `make_flow_strip(doc, steps)` is the table fallback.
- `add_phase_marker(doc, text, phase=2)` — `▌ PHASE 2 — text` callout.
- `_apply_font(run, name)` — binds a font across all four OOXML script slots (used for Montserrat headings).

No Glossary / Acknowledgement / Open-Nits helpers — those appendices were removed per the conciseness pass. Hand-editing the docx after generation is **not** the workflow. Edit the builder, re-run, re-lint, re-anchor.
