# Skill Audit — `odoo-mock-design`

**Audit date:** 2026-06-15
**Audit subject:** the `odoo-mock-design` skill in its current state (SKILL.md 1011 lines; 6 reference docs; 4 Python scripts; 38 catalog component fragments; `odoo.css` ≈ 4734 lines; `walkthrough.js` ≈ 835 lines; `annotations.css` ≈ 1510 lines).
**Audit type:** Structural / quality / compliance audit against the eight core principles below.
**Auditor model:** Claude Opus 4.7.
**Auditor stance:** read-only, treating this skill independently of prior conversational context.

Evaluated against:

1. **Global Best Practices** — industry-standard structure for LLM tools/agents.
2. **Reliability & Execution** — consistent achievement of defined goals regardless of start point.
3. **Optimization & Bulk** — absence of redundant prompts/code that could be removed without quality loss.
4. **Procedural Drift** — structure/logic/phrasing pulling away from defined mechanisms.
5. **Self-Containment** — no extraneous external dependencies / context leakage.
6. **Constraint-Compliant Latency** — fastest turnaround consistent with defined procedures.
7. **Token Efficiency** — mechanical delivery to minimize I/O tokens via structural design.
8. **Structural Integrity** — no stale, broken, or outdated cross-references.

---

## 1. What this skill does well

- **Self-containment is mechanically enforced.** `_lint_mock.py` parses every HTML/CSS reference (`src`, `href`, `data`, `poster`, `xlink:href`, `url()`, `@import`), flags any external URL / path-escape / external SVG-use, and runs SHA-256 freshness diffs of every `assets/<x>` against `reference/catalog/<x>` (`STALE-ASSET` rule). This makes "ships offline" a release gate, not a hope.
- **Source-first catalog discipline.** `REFRESH.md` documents every catalog change with the Odoo path that produced it; `field_placement.md` Step 0 mandates a source-availability check before rendering; `view_types.md`, `style_guide.md`, `catalog_chrome.md`, and the fragments themselves carry header comments citing real `odoo/addons/...` paths. The catalog is a traceable mirror, not a stylistic invention.
- **Two-anchor pre-finish gate.** `mock-coverage-anchor` + `mock-fidelity-anchor` fire in one foreground parallel message, replace `ExitPlanMode`, and gate delivery on zero unresolved blockers. The skill cleanly carves out P11 (plan mode) and P13 (architecture detection) and justifies the exemption inline.
- **Eight-dimension coverage inventory** (actors, apps, new models + views, menus, reports, notifications, lifecycle states, guard rules) + a 9th "integration touchpoints (no-UI surfaces)" sub-class with mandatory cover-list rendering. Replaces the actor-only floor that previously let new config models / Configuration menus / reports / un-gated guards slip through.
- **Explicit Coverage-level gate** (Core / Standard / Comprehensive) asked ONCE before assembly, populated from the just-built inventory, with the rule that tier boundaries are fixed (an actor's primary touchpoint can't be downshifted to dodge work).
- **Variant-axis chip-row mechanism** (`data-mock-variant-axes` JSON + `data-mock-variant="axis=value,axis=value"`) folds guard-paths into State-axis variants on primary screens — eliminates the screen-multiplication failure of the previous segmented-pill design while keeping each axis lint-validated (JSON shape, ≥ 2 options per axis, default ∈ options, child references valid axis/value, ≤ 4 axes/screen).
- **Surface-native vocabulary table** (`style_guide.md` rule 14) maps backend-form chrome onto Website / Portal / POS equivalents and is mechanically enforced by `_lint_mock.py`'s `SURFACE-LEAK` + `INLINE-CALLOUT` rules — closes a long-running drift mode.
- **Marker discipline.** "4–7 per package," not per screen, anchored at load-bearing solution elements; `data-note` is the sole site for marker text (no inline body-copy leak); per-screen sequential numbering with cover example using `i`.
- **`_lint_mock.py` is comprehensive for what lint can catch** — `EXTERNAL`, `ESCAPE`, `SVG-USE`, `STALE-ASSET`, `PLACEHOLDER`, `COVERAGE`, `VARIANT` (per-axis structural checks), `WORKFLOW` (multi-shell hygiene + duplicate screen IDs + orphan screens), `INPUT-PENDING` (painted-but-dead affordance), `PAGE-REF` (dangling cover chip), `COVER-SUBGRID`, `KNOWN-BAD`, `SURFACE-LEAK`, `INLINE-CALLOUT`, `WORKFLOW-TITLE` (12-char cap), `MARKER-TEXT`, `RIBBON` (`data-text` attribute discipline). Each row has a documented rationale tied to a real observed regression.
- **Multi-workflow cover topology is fully specified** — per-workflow overview screens (`data-screen-kind="workflow-overview"`), main-cover CTA chips (`mock-step-axes-cta`) replace `data-mock-page-ref` (because page numbers are workflow-scoped), cross-workflow Next chaining, workflow-overview marker exemption.
- **Visual review is split across two harnesses with clear scopes.** `_render_catalog.py` is the gallery regression harness for catalog edits; `_render_mock_screens.py` drives `walkthrough.js`'s `#screen-id` hash convention to take exactly-one-screen PNGs per `.mock-screen`. The "visual review is OPT-IN, default is `Done — open <path>`" rule keeps the happy path fast.
- **Scaffolder (`_scaffold_mock.py`) is correctness-by-construction.** Emits canonical skeleton (favicon link, brand header, callout block, workflow-overview shells, placeholder screens with `<!-- SLOT: -->` markers, walkthrough bar) so a fresh build starts lint-clean. Stub-imports docx/PIL so the build script's `SPEC_DATA` dict can be read without requiring `python-docx`.
- **Iteration etiquette explicitly directs source-first.** When a needed view/widget isn't in the catalog, the documented loop is *check source availability → grep Odoo for the real implementation → port it → update `REFRESH.md` → use from the package* — with the token-only fallback ONLY when source is absent. Closes the leading "looks-Odoo but isn't" drift mode.
- **`view_types.md` density anchors are workflow-weighted**, not floor-enforced — both "padding for density" and "stripping for minimalism" are named as anti-patterns. This calibrates the smallest faithful mock instead of locking a row/field quota.

---

## 2. Areas for Improvement

- **SKILL.md is bloated (1011 lines).** Although `catalog_chrome.md` was created specifically to move per-fragment discipline out of SKILL.md (per its own intro), SKILL.md still embeds ~170 lines of cover-discipline templates, ~125 lines of multi-workflow cover topology, the entire KNOWN-BAD self-grep table, the eight-dimension inventory definitions, the coverage-gate worked example, and several `o_field_help` / `o_input_pending` per-pattern rules that belong in `interactions.md`. The orchestration entry-point has absorbed reference material it was supposed to delegate.
- **Triple-copy of the canonical "5 callouts" template** lives in (a) SKILL.md § Cover discipline item 3 with verbatim HTML, (b) `reference/samples/reference_pattern.md` § 2 with verbatim HTML, and (c) `_scaffold_mock.py::_cover_callouts()` with the strings hard-coded — any wording change requires three coordinated edits, with no test that they agree.
- **Documentation drift between SKILL.md and `walkthrough.js` on multi-workflow Next-button labels** (see §3 detailed analysis). SKILL.md describes labels the code does not produce; the actual labels live in `walkthrough_bar.html`'s header comment.
- **`page_skeleton.html` is out of sync with SKILL.md cover discipline.** The skeleton ships a 5-line "interactive mock walks through the proposed workflow … Numbered `i` markers explain each element" — paragraph, no favicon link, no `mock-cover-section`, no canonical 5-callout block, no brand header / kicker / watermark, no `mock-step-list-wrap`. Authors composing from the skeleton produce out-of-spec covers unless they also follow SKILL.md verbatim.
- **`_scaffold_mock.py` bypasses `page_skeleton.html`.** The scaffolder hand-builds its own `<!DOCTYPE>` + `<head>` + cover scaffold instead of templating from `page_skeleton.html`, so there are now TWO canonical "shape of `index.html`" definitions in the repo. They are not asserted-equivalent.
- **Agent YAML drift.** `agents/odoo-mock-design.yaml` was written before the coverage-level gate and the 8-dimension inventory landed; it still describes a generic 8-step pipeline, omits the coverage-gate ask, omits the eight inventory dimensions, and ends with "(8) Open `index.html` in a browser (or headless screenshot) to confirm screens render" — directly contradicting SKILL.md § Finish ("Default: print 'Done — open `<path>`' and stop. Visual review is opt-in.").
- **`reports/industry_standards_audit.md` is a 194-line, 2026-06-13 snapshot whose claims have decayed.** It still describes the "Supporting-surfaces sweep: default → opt-in" rule, but SKILL.md line 318 says: "This gate REPLACES the older 'supporting surfaces — opt-in' ask." Three Tier-1 improvements proposed there ("last refreshed against Odoo X.Y line," `role="tab"` on chips, `aria-label` for icon-only buttons) appear to remain unactioned.
- **Stale workspace artefacts checked in** — three `.DS_Store` files (root, `reference/`, `reference/catalog/`) and `reference/scripts/__pycache__/_lint_mock.cpython-312.pyc`. These are noise: macOS metadata + compiled bytecode.
- **An explicit `TODO` in SKILL.md line 521**: `the lint rule coverage:cover-step-cells should catch missing third cells (TODO: add when the corpus stabilises)`. This is a self-acknowledged un-shipped enforcement.
- **The Pre-anchor self-check KNOWN-BAD grep table (SKILL.md lines 612–643) duplicates work the lint already does.** Seven of the nine "30-second self-grep" patterns are exactly the same patterns the lint script enforces (`mock-cover-body`, `o_setting_searchbar`, `<table class="o_list_view"`, `data-workflow-title` length, the `>i<` workflow-screen marker pattern, etc.). Asking the LLM to grep before running the lint adds latency + tokens to do work the lint will catch zero seconds later.
- **The "device-trade-in" coverage-gate worked example (SKILL.md lines 287–295)** gives concrete numbers ("4 screens / 8 screens / 11 screens") with a sternly-worded "NEVER show the example figures above verbatim." The combination — vivid example PLUS prohibition — increases the chance an LLM cites it verbatim under pressure. Either drop the numbers, or move the example to a non-prescriptive appendix.
- **`reference_pattern.md` is 399 lines** and is described as the "calibration target." Half of it is a repeat of SKILL.md cover discipline plus an annotated worked example. A reader who has already read SKILL.md absorbs the cover-discipline section twice.
- **Tier definitions for the Coverage gate (Core / Standard / Comprehensive)** are repeated three times across SKILL.md (lines 261–319), the production-readiness checklist (lines 938–951), and the anchor instructions (lines 682–697). Synchronizing any tier definition requires three edits.
- **`field_placement.md` and SKILL.md repeat each other** on "discover from source / warn / fallback." SKILL.md § Comprehension step 1 spells out Step 0, then `field_placement.md` defines Step 0 in full. The SKILL.md inline restatement is summary-only and not auto-derived from the reference.

---

## 3. Detailed Problem Analysis

---

### Issue P-01 — Documentation drift: multi-workflow Next-button labels

* **Identification:** `next-button-label-drift`
* **Section Reviewed:**
  - `SKILL.md` lines 717–727 ("Reading flow (multi-workflow)")
  - `SKILL.md` lines 815–822 (the `walkthrough.js` mechanics table)
  - `reference/catalog/walkthrough.js` lines 139–170 (`nextButtonLabel()`)
  - `reference/catalog/components/walkthrough_bar.html` lines 30–36 (header comment)
* **Problem Observed:** Three sources describe three different sets of Next-button labels.

  | Source | Main cover (multi-WF) | Per-WF overview | Last screen of non-final WF |
  |---|---|---|---|
  | SKILL.md "Reading flow" diagram | `Get Started` | `Get Started` | `Next workflow: <next-title> →` |
  | SKILL.md mechanics table | `Get Started` | `Get Started` | `Next workflow: <next-title> →` |
  | `walkthrough.js::nextButtonLabel` | `Start: <name>` | `Get Started` | bare `<next-name>` |
  | `walkthrough_bar.html` header | `Start: <name>` | `Get Started` | bare `<name>` |

  The code agrees with the fragment-header comment; SKILL.md describes labels the code does NOT generate (for both the main cover and the last-screen-of-non-final-workflow case).
* **Risks Posited:** A reader following SKILL.md will check a generated mock against the documented labels, find a mismatch, and either (a) "fix" `walkthrough.js` back to the documented strings — regressing the implemented design — or (b) flag the lint as broken when nothing is broken. The mock-fidelity-anchor's UI vocabulary judgements may also drift if anchored on the wrong docs.
* **Rationale:**
  - Principle 8 (Structural Integrity): a 3-way stale-reference triangle.
  - Principle 4 (Procedural Drift): the documentation is leading the LLM toward a behavior the code does not produce.
* **Proposed Solution:**
  1. Edit `SKILL.md` lines 720, 723, 817, 819 (the diagram + table) to match the code's labels: `Start: <name>` for the main-cover entry in multi-workflow mode, bare `<next-name>` for the cross-workflow Next on the last screen of a non-final workflow.
  2. Add a comment block in `walkthrough.js::nextButtonLabel` that says "single source of truth — `walkthrough_bar.html` header + SKILL.md § Walkthrough.js mechanics must match this function."
  3. Optional: have `_render_mock_screens.py` (or a tiny dedicated check) assert that a mock's rendered Next labels match the documented vocabulary, so drift is caught automatically.
* **Solution Rationale:** Pins documentation to code (the only source that actually runs in front of the reader). Adds a forward guard against re-drift.
* **Risks of Solution:** Low. SKILL.md edits are textual; the JS comment is informational; the optional check is opt-in.
* **Trade-offs:** Slightly more verbose JS comment.

---

### Issue P-02 — Triple-copy of the canonical 5 callouts

* **Identification:** `cover-callouts-triplication`
* **Section Reviewed:**
  - `SKILL.md` lines 397–456 (the 5-callout block embedded with verbatim HTML)
  - `reference/samples/reference_pattern.md` lines 56–115 (verbatim repeat)
  - `reference/scripts/_scaffold_mock.py::_cover_callouts()` lines 165–204 (Python string literals)
* **Problem Observed:** Three artefacts carry the same canonical strings (callout headings, body wording, conditional-include rules) with no cross-reference. A wording change to "Interactive mock." requires three coordinated edits.
* **Risks Posited:**
  - On a wording change, the maintainer updates SKILL.md and forgets the scaffolder → generated mocks drift from documented canon.
  - Reviewers reading the worked example in `reference_pattern.md` may treat it as a *different* canonical voice and re-introduce hand-authored variation.
* **Rationale:**
  - Principle 3 (Bulk): same content repeated three times.
  - Principle 8 (Structural Integrity): the three copies have no automated agreement check.
* **Proposed Solution:**
  1. Make `_scaffold_mock.py` read the callouts from a single text file (`reference/templates/cover_callouts.html`) at run time and substitute the conditional flags.
  2. In `SKILL.md` and `reference_pattern.md`, replace the verbatim HTML with a code-quote of the template file's path + a short summary; tell the author to read the template, not paraphrase from memory.
  3. Add a tiny lint check (or `_scaffold_mock.py` self-test) that confirms the generated cover callouts hash-match `reference/templates/cover_callouts.html`.
* **Solution Rationale:** One source of truth + a hash gate means a wording change is one edit and one re-run. Removes the documentation-vs-code drift risk.
* **Risks of Solution:** The template file becomes a load-bearing artefact. If it is deleted, the scaffolder fails — but that failure is loud, not silent.
* **Trade-offs:** Slight indirection — readers need one extra hop to see the canonical text. The hop is to a file purpose-named for the text, which is reasonable.

---

### Issue P-03 — `page_skeleton.html` lags SKILL.md cover discipline

* **Identification:** `page-skeleton-stale-cover`
* **Section Reviewed:** `reference/catalog/components/page_skeleton.html` lines 27–41.
* **Problem Observed:** The shipped skeleton's cover section is a 7-line block with `<h1>` + `<p>` + an inline paragraph containing one `i`-marker example. None of these match the canonical cover SKILL.md § Cover discipline requires: there is no favicon `<link>` in `<head>`, no `mock-cover` brand header (kicker + watermark), no `mock-cover-section` wrapper, no 5-callout block, no `mock-step-list-wrap` workflow-narrative table.
* **Risks Posited:**
  - A generator using `page_skeleton.html` as the literal scaffold and only "filling SLOTs" produces a non-conforming cover that mock-coverage-anchor will flag.
  - The fragment is the natural primer for authors who haven't read SKILL.md cover discipline yet — those authors don't know what they're missing.
  - `_scaffold_mock.py` had to re-author the cover scaffold inline because the existing skeleton was unusable for the canonical shape.
* **Rationale:**
  - Principle 2 (Reliability & Execution): a fresh author starting from the skeleton cannot produce a passing mock without out-of-band knowledge.
  - Principle 8 (Structural Integrity): the skeleton encodes a stale design.
* **Proposed Solution:**
  1. Update `page_skeleton.html` so the cover matches the canonical structure: `<link rel="icon" href="assets/odoo-icon.svg"/>` in `<head>`, `mock-cover` div with kicker + watermark + title + summary, `mock-cover-section` wrapping all 5 callouts (use SLOT comments for the conditional ones), and a `mock-step-list-wrap` SLOT for the workflow narrative.
  2. Replace the inline `mock-marker` example with the canonical `mock-marker mock-marker-example` + the canonical `data-note` text.
  3. Have `_scaffold_mock.py` consume `page_skeleton.html` as its starting point (template substitution) instead of hand-building the structure.
* **Solution Rationale:** Aligns the skeleton with what SKILL.md mandates so the two artefacts can't disagree. Lets the scaffolder use the same skeleton as a hand-authoring author, eliminating the parallel "shape of `index.html`" definitions.
* **Risks of Solution:** A larger skeleton means more SLOT comments to navigate when hand-authoring — but the SLOTs are explicit, which is the right trade.
* **Trade-offs:** Skeleton file grows from 64 lines to ~120; scaffolder script shrinks by a comparable amount.

---

### Issue P-04 — Agent YAML drift from SKILL.md current procedure

* **Identification:** `agent-yaml-pipeline-drift`
* **Section Reviewed:** `agents/odoo-mock-design.yaml` lines 4–41 (`default_prompt`).
* **Problem Observed:** The agent's `default_prompt` was written for the pre-coverage-gate pipeline and is now ~3 generations behind SKILL.md:
  - No mention of the Coverage-level gate (Core / Standard / Comprehensive) asked once before assembly.
  - No mention of the eight-dimension surface/behaviour inventory (still says "screen list + click-path").
  - "(8) Open `index.html` in a browser (or headless screenshot) to confirm screens render" — contradicts SKILL.md § Finish which says default behaviour is "print `Done — open <path>` and stop. Visual review is opt-in."
  - Still references a pre-finish anchor pass but does not say `mock-coverage-anchor` consumes the eight-dimension inventory at the chosen tier.
* **Risks Posited:**
  - The agent YAML is what gets dropped into the conversation when a parent skill (e.g. `odoo-write-specifications`) invokes this skill — it's the primary entry-point for embedded mode.
  - LLMs reading the agent prompt will follow it instead of cross-reading SKILL.md, so the coverage-gate / inventory steps get skipped at the most common invocation path.
  - The forced browser-open step pulls the agent into actions SKILL.md explicitly defers.
* **Rationale:**
  - Principle 4 (Procedural Drift): the entry-point document says one thing, the reference document says another, and the entry-point wins by default.
  - Principle 8 (Structural Integrity): stale procedural reference.
* **Proposed Solution:**
  1. Rewrite `default_prompt` to match SKILL.md's current six-stage flow: Comprehension (+ 8-dimension inventory) → Coverage-level gate → Curate → Assemble → Verify (lint + anchors) → Finish.
  2. Drop the forced step-8 browser open; replace with "If the user requested a visual review or if the catalog has been edited recently, run `_render_mock_screens.py` per the SKILL.md § Optional appendix."
  3. Add a one-line "Read SKILL.md first; this prompt is a thin orchestration layer over it" hint at the top so future drift is obvious.
* **Solution Rationale:** Re-aligns the entry-point with the canonical procedure; removes the contradicted step.
* **Risks of Solution:** The agent prompt grows slightly. Mitigated by keeping the prompt as the orchestration shell, not the full procedure.
* **Trade-offs:** Marginally longer agent prompt for substantially better fidelity to SKILL.md.

---

### Issue P-05 — Pre-anchor KNOWN-BAD self-grep duplicates the lint

* **Identification:** `pre-anchor-grep-duplication`
* **Section Reviewed:** `SKILL.md` lines 612–643 (the KNOWN-BAD grep table + the "30-second self-grep" instruction).
* **Problem Observed:** The SKILL tells the LLM to grep for 9 patterns BEFORE firing the anchors:
  - `mock-cover-body` — duplicated by lint `KNOWN-BAD`
  - `o_setting_searchbar` — duplicated by lint `KNOWN-BAD`
  - `mock-marker[^>]*>i<` on workflow screens — duplicated by lint `MARKER-TEXT`
  - `<table class="o_list_view"` — duplicated by lint `KNOWN-BAD`
  - `alert alert-danger` on backend form — NOT in lint
  - Net-new field without `o_field_help` — NOT in lint
  - `Interactive walkthrough` cover wording — NOT in lint
  - `data-workflow-title="[^"]{13,}"` — duplicated by lint `WORKFLOW-TITLE`
  - Dead `o_input_pending` affordances — duplicated by lint `INPUT-PENDING`
  - Guards living only in marker notes — NOT in lint

  Six of the ten patterns are already enforced by the lint script that the SKILL says to run on the very next line.
* **Risks Posited:**
  - Asking the LLM to grep manually for patterns the lint will catch zero seconds later is wasted input/output tokens.
  - The two lists ("self-grep" and "lint catches") can drift; today the table inside SKILL.md is the maintenance-of-record.
  - The instruction implies the lint is incomplete in ways it isn't, which weakens trust in the lint.
* **Rationale:**
  - Principle 3 (Optimization & Bulk): the same checks twice.
  - Principle 6 (Latency): the manual grep step is pure overhead.
  - Principle 7 (Token Efficiency): the table itself + the instruction to run it consume input + output tokens.
* **Proposed Solution:**
  1. Remove the six grep rows that the lint already catches from SKILL.md.
  2. Promote the FOUR patterns that lint does NOT catch (`alert alert-danger` on backend form, missing `o_field_help` on net-new fields, `Interactive walkthrough` wording, guard-only-in-marker-note) into actual lint rules in `_lint_mock.py` — each is mechanical.
  3. After the four promotions, delete the entire "Pre-anchor self-check" section and replace with one sentence: "Run `_lint_mock.py` and fix findings; the anchors fire next."
* **Solution Rationale:** Lint becomes the single mechanical filter; the LLM stops doing work the lint already does; the four "missing" patterns get promoted to enforcement.
* **Risks of Solution:** The four new lint patterns need testing on the corpus to confirm they don't false-positive. (Guards-living-only-in-marker-notes is the trickiest — needs cross-referencing brief content to marker `data-note`, which a static lint can only approximate.)
* **Trade-offs:** ~30 lines removed from SKILL.md; ~80 lines added to `_lint_mock.py`. Net structural improvement: enforcement consolidates to one place.

---

### Issue P-06 — SKILL.md absorbs reference-only material it was supposed to delegate

* **Identification:** `skill-md-reference-absorption`
* **Section Reviewed:** `SKILL.md` overall structure (1011 lines), specifically:
  - Lines 367–541 (~170 lines): Cover-discipline section embedding verbatim HTML for brand header + 5 callouts + workflow narrative table + axis-chip semantics.
  - Lines 612–643: Pre-anchor self-check table (see P-05).
  - Lines 708–831 (~125 lines): Multi-workflow cover topology.
  - Lines 936–1011 (~75 lines): Production-readiness checklist with 18 items repeating constraints already named elsewhere.
* **Problem Observed:** `reference/catalog_chrome.md` was created with the explicit purpose "to collect the *per-fragment* discipline that previously lived in `SKILL.md`" (line 1–7). The migration is incomplete — SKILL.md still carries the cover scaffold, the multi-workflow chrome topology, axis-chip mechanics, the production checklist, and the workflow-bar mechanics-table — all of which are per-fragment or per-component rules.
* **Risks Posited:**
  - At 1011 lines, SKILL.md exceeds the "context-cheap orchestration entry-point" model: every invocation of the skill puts the entire content into the LLM context.
  - Burying orchestration-relevant steps (e.g. the Coverage-level gate at lines 261–318) inside per-fragment scaffolding makes them harder to locate and easier to skip.
  - When the canonical cover changes, two places (SKILL.md + `catalog_chrome.md`) must be considered for the edit, even though only the latter is purpose-named.
* **Rationale:**
  - Principle 1 (Best Practices): "thin orchestration + thick references" is the standard LLM-tool decomposition; SKILL.md violates it.
  - Principle 3 (Bulk): material that belongs in references is loaded every invocation.
  - Principle 7 (Token Efficiency): every embedded HTML example costs tokens on every read.
* **Proposed Solution:**
  1. Move § Cover discipline (lines 367–541) into a new `reference/cover_discipline.md` (or fold into `catalog_chrome.md`). Leave a 5-line summary + link in SKILL.md.
  2. Move § Multi-workflow cover topology (lines 708–831) into `catalog_chrome.md` § Multi-workflow chrome (which already exists; just absorb the cover-topology section there). Leave a 3-line summary + link in SKILL.md.
  3. Move § Production-readiness checklist (lines 936–1011) into `reference/checklist.md`. The orchestrating SKILL says "Run through `reference/checklist.md` before printing Done."
  4. Result: SKILL.md drops to ~600 lines, still orchestration + the Generation Pipeline + the Coverage gate + the Eight-dimension floor.
* **Solution Rationale:** Recovers the "thin entry-point" model. References are loaded only when needed (the LLM reads them based on the pipeline step it's executing).
* **Risks of Solution:** Loss of inline examples is a real cost — readers cannot see the canonical HTML in the same file as the orchestration. Mitigated by short summaries + explicit "see X" links and the SKILL's existing "Reference Material (Read Before Building)" section, which already gates the relevant references.
* **Trade-offs:** Slightly more file-hopping; substantially smaller orchestration prompt.

---

### Issue P-07 — Industry-standards-audit report contains stale state

* **Identification:** `industry-audit-stale-snapshot`
* **Section Reviewed:** `reports/industry_standards_audit.md` overall.
* **Problem Observed:**
  - Audit date 2026-06-13; current date 2026-06-15. The audit explicitly says it's a "Reference snapshot" with improvements deferred, but several of its descriptions are no longer accurate:
    - Line 178: "Supporting-surfaces sweep: default → opt-in. Trigger table no longer runs automatically. Single `AskUserQuestion` …" → SKILL.md line 318: "This gate REPLACES the older 'supporting surfaces — opt-in' ask." The audit describes a state the SKILL has since superseded.
    - Line 180: "Pipeline collapsed for speed. 8 sequential steps + multi-cycle reconciliation reduced to 5: (1) Comprehension … (4) Lint once + single anchor pass; (5) Finish." → SKILL.md now has Comprehension + Curate (with the Coverage-level gate) + Assemble + Verify + Finish, the Comprehension step itself runs the eight-dimension inventory in one pass. The phase counts and contents have shifted enough that the "5-step pipeline" description doesn't map cleanly to current SKILL.md numbering.
    - Tier-1 improvement #1 "Add a one-paragraph cross-reference to WCAG / Atomic Design / Nielsen heuristics in `style_guide.md`" — `style_guide.md` does not yet contain this paragraph; status unclear from the audit.
* **Risks Posited:**
  - A reader using the audit as a reference for "what the skill currently does" gets a stale picture.
  - The audit's Tier-1 / Tier-2 backlog has no last-revisited timestamp, so unclear which items are still pending vs already done.
* **Rationale:**
  - Principle 8 (Structural Integrity): stale doc.
  - Principle 4 (Procedural Drift): not catastrophic, since the audit is labelled a snapshot, but the un-pruned snapshot is itself drift if a reader treats it as canonical.
* **Proposed Solution:**
  1. Add a banner at the top of the file: "**STALE: snapshot from 2026-06-13. Authoritative current state is `SKILL.md`, `style_guide.md`, and `catalog/`. Items below may be out of date.**"
  2. Or: re-run the industry-standards audit and update the file in place (the same path the skill stores its audits to), keeping a "last reviewed" line at the top.
  3. Either way, cross-check the "Tiered improvement backlog" against current state and mark each item as `[done]`, `[pending]`, or `[supplanted]`.
* **Solution Rationale:** Removes the silent-drift risk; preserves the audit's value as a frame of reference.
* **Risks of Solution:** Re-running the audit is non-trivial; the banner option is cheap but partial.
* **Trade-offs:** Banner is fast and signals risk; full refresh is the right answer but takes work.

---

### Issue P-08 — Unactioned `TODO` inside SKILL.md

* **Identification:** `skill-md-todo-marker`
* **Section Reviewed:** `SKILL.md` line 521: `cells (TODO: add when the corpus stabilises).`
* **Problem Observed:** SKILL.md cover discipline § Workflow narrative item 4 includes: "The lint rule `coverage:cover-step-cells` should catch missing third cells (TODO: add when the corpus stabilises)." This is the only `TODO` in the skill's authored prose. It declares a known-missing enforcement.
* **Risks Posited:**
  - Low-grade trust-erosion: the skill that lints every package for "no placeholder strings" itself contains a placeholder marker.
  - The enforcement is named (`coverage:cover-step-cells`) but no rule with that key exists, so a future search for the rule fails.
* **Rationale:**
  - Principle 5 (Self-Containment): the skill claims completeness; an explicit TODO contradicts that.
  - Principle 8 (Structural Integrity): a forward reference with no target.
* **Proposed Solution:**
  1. Either implement the lint rule now (it's a 10-line regex check: every `<li>` inside `mock-step-list` must contain exactly 3 immediate-child `<span>`s — easy to write) and remove the TODO.
  2. Or remove the TODO sentence entirely — the rest of the bullet still explains the empty-third-cell requirement without inviting a "FIXME exists" finding.
* **Solution Rationale:** Closes the gap or hides the gap honestly.
* **Risks of Solution:** Implementing the rule risks false-positives on hand-crafted overview screens. Removing the TODO sentence loses the "future enforcement was planned" memory — recover via a `REFRESH.md` log entry.
* **Trade-offs:** Path 1 takes ~20 minutes; path 2 takes 2 minutes.

---

### Issue P-09 — Stale `.DS_Store` and `__pycache__` in the skill tree

* **Identification:** `stale-workspace-artefacts`
* **Section Reviewed:**
  - `skills/odoo-mock-design/.DS_Store`
  - `skills/odoo-mock-design/reference/.DS_Store`
  - `skills/odoo-mock-design/reference/catalog/.DS_Store`
  - `skills/odoo-mock-design/reference/scripts/__pycache__/_lint_mock.cpython-312.pyc`
* **Problem Observed:** macOS filesystem metadata (`.DS_Store`) and CPython bytecode caches (`__pycache__/*.pyc`) are present in the skill tree.
* **Risks Posited:**
  - Cosmetic only on import / use of the skill, but it muddies the skill's claim of "self-contained, portable."
  - `_render_mock_screens.py` and similar tools walk the tree; they ignore these today but a future `_lint_skill.py` (hypothetical) might trip on them.
  - Listing the skill folder for documentation purposes reveals platform artefacts that suggest the skill isn't curated.
* **Rationale:**
  - Principle 5 (Self-Containment): the skill says no external dependencies — leaving platform artefacts in the tree weakens the message.
  - Principle 8 (Structural Integrity): noise.
* **Proposed Solution:**
  1. Delete the four files.
  2. Add a `.gitignore` (or `.skillignore`, if one exists) at the skill root that lists `.DS_Store` and `__pycache__/`.
  3. Optional: have `_lint_mock.py` (or a new tiny check) flag stale artefacts in the skill folder itself, not just the generated mock.
* **Solution Rationale:** Trivial cleanup; gitignore prevents recurrence.
* **Risks of Solution:** None.
* **Trade-offs:** None.

---

### Issue P-10 — Coverage-tier worked example may be cited verbatim

* **Identification:** `coverage-tier-example-verbatim-risk`
* **Section Reviewed:** `SKILL.md` lines 287–295 (the device-trade-in worked example).
* **Problem Observed:** SKILL.md gives a concrete worked example for the Coverage gate options:
  > *Core* — "4 screens: Website form · Appraisal · POS Trade-In · POS Redemption."
  > *Standard* — "8 screens: Core + CRM Lead · Inventory Receipt · eWallet Card · …"
  > *Comprehensive* — "11 screens: Standard + Inspection Criteria config · Appraisal Pipeline (pivot) · …"
  followed by "Recompute these from the actual inventory every run — never show the example figures above verbatim."
* **Risks Posited:**
  - The vivid concrete example sits adjacent to the instruction not to use it. Under output-pressure (small context window, time-to-answer pressure), an LLM may default to the most-recently-seen specifics and ship the example's screen counts as the user's options.
  - The example happens to use a real solution domain (device trade-in / eWallet) so reads as plausible — a reader may not flag it as fictional.
* **Rationale:**
  - Principle 2 (Reliability & Execution): the instruction depends on the LLM correctly performing a "do not paraphrase" gate that LLMs frequently fail.
  - Principle 1 (Best Practices): pairing a vivid example with a prohibition is a known LLM-prompting anti-pattern; better to use either an abstract example or none.
* **Proposed Solution:**
  1. Replace the concrete numbers with structural shapes: "4 screens (Core: primary actor + main app + happy state), 6–10 (Standard: all actors + all primary states + all guards), 8–14 (Comprehensive: Standard + config + reports + notifications + edge states)."
  2. Or: move the device-trade-in example into a `reference/examples.md` appendix that is NOT loaded by default, so it can't leak into a generated coverage-gate dialog.
* **Solution Rationale:** Eliminates the verbatim-citation surface area while still teaching the option shape.
* **Risks of Solution:** A less vivid example may be less effective as a teaching tool. Mitigated by the production-readiness checklist already saying "each option's `description` must be populated from the actual inventory."
* **Trade-offs:** Slight loss of pedagogical concreteness; substantial reduction in regression-into-verbatim risk.

---

### Issue P-11 — Tier definitions repeated three times in SKILL.md

* **Identification:** `tier-definitions-three-copies`
* **Section Reviewed:**
  - `SKILL.md` lines 261–319 (Coverage-level gate prose with Core / Standard / Comprehensive definitions)
  - `SKILL.md` lines 682–697 (Verify step's instruction to the anchor with the tier semantics restated)
  - `SKILL.md` lines 938–951 (Production-readiness checklist with the tier-fit bullet)
* **Problem Observed:** The same three-tier semantic (Core / Standard / Comprehensive) is defined in three places. Each says slightly different things: the Coverage-gate section names eight dimensions; the Verify section names them with different ordering; the production checklist names the screen-count expectations differently again ("Core ~4–6; Standard scales with actors/apps/models/states; Comprehensive adds config/reports/notifications/edge states").
* **Risks Posited:**
  - A wording change to "Standard" needs three coordinated edits.
  - Subtle inconsistency between the three definitions risks the anchor (which reads the Verify section) judging at a slightly different tier shape than the Coverage gate (which reads the gate-section).
* **Rationale:**
  - Principle 3 (Bulk): three copies of the same definition.
  - Principle 4 (Procedural Drift): each restate is slightly different.
* **Proposed Solution:**
  1. Promote the tier definitions to a numbered, canonical glossary at the top of SKILL.md (or in `reference/coverage_levels.md`).
  2. Replace each of the three restatements with a one-line cross-reference: "(see Coverage levels § Standard)."
* **Solution Rationale:** Single source of truth; cross-references replace duplication.
* **Risks of Solution:** Authors who read SKILL.md top-to-bottom encounter the glossary first, before the pipeline; trade-off acceptable since the glossary is foundational.
* **Trade-offs:** Minor structural reordering of SKILL.md.

---

### Issue P-12 — `reference_pattern.md` carries duplicate canonical text

* **Identification:** `reference-pattern-overlap`
* **Section Reviewed:** `reference/samples/reference_pattern.md` lines 22–181 (Cover discipline / canonical 5 callouts / workflow narrative table / axis-chip semantics — all verbatim repeats of SKILL.md).
* **Problem Observed:** A reader who has just read SKILL.md § Cover discipline encounters its content again in `reference_pattern.md`. The file is described as a "worked example, calibrated against Odoo 19.0," but ~60% of its body is canonical-text repeat, not example.
* **Risks Posited:**
  - The reader's tokens are spent on re-reading the same prose.
  - If SKILL.md and `reference_pattern.md` ever differ, the discipline is the SKILL.md version — but `reference_pattern.md` is positioned as a calibration target, so a reader might trust it over SKILL.md.
* **Rationale:**
  - Principle 3 (Bulk).
  - Principle 7 (Token Efficiency).
  - Principle 8 (Structural Integrity).
* **Proposed Solution:**
  1. Strip `reference_pattern.md` to ONLY the worked-example deltas: the at-a-glance summary, the curation table (10 candidates → 5 screens), the index.html structure of the multi-axis screen, the per-package marker budget table.
  2. Replace canonical-text repeats with "see SKILL.md § Cover discipline" cross-references.
  3. End state: `reference_pattern.md` becomes ~150 lines of pure worked example rather than 400 lines of doc + example mix.
* **Solution Rationale:** Worked example becomes a worked example, not a recap. SKILL.md remains canonical for discipline; sample shows how that discipline lands in a real package.
* **Risks of Solution:** A reader who wanted ONE document with everything may dislike the split. Mitigated by clear cross-references.
* **Trade-offs:** Slightly more navigation; substantially less duplicated content.

---

### Issue P-13 — `field_placement.md` Step-0 also inlined in SKILL.md

* **Identification:** `field-placement-step-0-restate`
* **Section Reviewed:**
  - `SKILL.md` lines 136–141 (Comprehension step's "Source-availability check (field_placement.md Step 0)")
  - `reference/field_placement.md` lines 52–74 (Step 0 in full)
* **Problem Observed:** SKILL.md inlines a short restate of `field_placement.md` Step 0 — including the warning text the user should see — and then immediately tells the LLM to read `field_placement.md` for the full procedure. The summary and the full version diverge slightly in wording.
* **Risks Posited:** Small. The summary is at-most a sentence and a half. But it's a place where two documents own the same instruction.
* **Rationale:** Principle 8 — minor.
* **Proposed Solution:** Trim the SKILL.md restatement to "Run `field_placement.md` Step 0 (source-availability check). On miss, surface the canonical warning on the cover."
* **Solution Rationale:** Lets `field_placement.md` own the wording.
* **Risks of Solution:** None.
* **Trade-offs:** None.

---

### Issue P-14 — `_short_workflow_title` heuristic likely to ship under-13-char overflow

* **Identification:** `scaffold-workflow-title-naive-truncate`
* **Section Reviewed:** `reference/scripts/_scaffold_mock.py::_short_workflow_title` lines 138–150.
* **Problem Observed:** When a spec has `workflows[i].name = "Order Fulfillment"` (17 chars), the function returns `"Order"` (first word ≤ 12 chars) — which is correct for chip rendering. When it has `"Manufacturing Execution"`, the function returns `"Manufacturing"` (13 chars) — which the lint rule `WORKFLOW-TITLE` flags as `> 12`. The fallback path `first[:12]` returns `"Manufacturin"` (truncated, 12 chars). The scaffolder's own docstring (lines 142–144) admits the heuristic doesn't try to be smart and tells the author to review.
* **Risks Posited:**
  - Scaffolder claims "the skeleton passes `_lint_mock.py` BY CONSTRUCTION" (line 358 of SKILL.md), but for a brief whose first-word workflow name is 13+ chars, the skeleton ships a lint blocker.
  - "Manufacturin" / similar truncations look broken to a reviewer who skims the skeleton output before refining.
* **Rationale:**
  - Principle 2 (Reliability): "lint-passes-by-construction" is the documented contract; this is an edge case where it doesn't hold.
* **Proposed Solution:**
  1. Hard-cap to 12 chars in the truncate path AND surface a `WARN` line to stdout: `WARN: workflow "<name>" chip title set to "<truncated>"; review and shorten to a single business noun.`
  2. Or maintain a small alias table in the scaffolder for common cases (`"Order Fulfillment" → "O2C"`, `"Procurement" → "P2P"`) — surfaces the alias as a suggestion rather than a hard pick.
* **Solution Rationale:** Either approach restores the "lint passes by construction" contract for this case.
* **Risks of Solution:** Alias table risks drift; warn-on-truncate is the minimum.
* **Trade-offs:** Small added complexity in the scaffolder; reliability gain.

---

### Issue P-15 — Catalog gallery render commands rely on Chrome being installed; the SKILL doesn't gate on absence

* **Identification:** `chrome-availability-soft-gate`
* **Section Reviewed:** `_render_catalog.py` lines 42–49, `_render_mock_screens.py` lines 52–59. The visual-review § in SKILL.md (lines 851–894) tells the LLM to run the scripts but does not mention the Chrome-presence prerequisite.
* **Problem Observed:** Both scripts exit `2` with `"No Chrome/Chromium found"` when no Chrome binary is in `PATH` or in the candidates list. The SKILL § Optional — visual review block tells the LLM to run the command unconditionally. On a headless box without Chrome, the LLM sees `Render failed`, may treat that as a fatal pipeline error, and may attempt to install Chrome — none of which is necessary.
* **Risks Posited:**
  - The script fails open (exit 2 → caller sees error → caller may try to remediate).
  - Visual review is documented as opt-in but the failure mode of opt-in-failed isn't documented.
* **Rationale:**
  - Principle 2 (Reliability): the documented operation can fail for environment reasons the SKILL doesn't anticipate.
  - Principle 5 (Self-Containment): the skill claims minimal external dependency surface; a hidden Chrome dependency for opt-in visual review is acceptable but should be flagged.
* **Proposed Solution:**
  1. In SKILL.md § Optional — visual review, add one sentence: "Requires `google-chrome` / `chromium` / Edge on the path. Without one, skip the visual review — the lint + anchor pass cover mechanical correctness."
  2. Have the script print a clearer "skipping — install Chrome to enable" line when the binary isn't found, so the LLM doesn't try to remediate.
* **Solution Rationale:** Sets expectations + lets the LLM no-op when Chrome is absent.
* **Risks of Solution:** None.
* **Trade-offs:** None.

---

### Issue P-16 — `_lint_mock.py` does its asset-freshness check by SHA-256-ing every package run, but provides no `--update` flag

* **Identification:** `lint-stale-asset-no-fix-flag`
* **Section Reviewed:** `_lint_mock.py` lines 119–151 (`STALE-ASSET` rule).
* **Problem Observed:** When the catalog updates and the mock's `assets/` is stale, the lint correctly flags it as a blocker. The recovery action is "re-copy the catalog assets into `assets/`" but the user / LLM has to perform the copy manually (or rerun `_scaffold_mock.py --force`, which overwrites `index.html` too — destroying any post-scaffold edits).
* **Risks Posited:**
  - The blocker description ("Re-copy the catalog assets into `assets/`") doesn't say HOW; the LLM may either (a) write a quick shell command and forget one file, or (b) re-run the scaffolder and nuke its own edits.
  - The recovery path is the most-common operation after a catalog refresh; absence of an idempotent helper means every consumer of the catalog does this ad hoc.
* **Rationale:**
  - Principle 6 (Latency): manual re-copy is slow + error-prone.
  - Principle 2 (Reliability): under pressure the LLM may pick the destructive option.
* **Proposed Solution:**
  1. Add a `--refresh-assets` flag (or a separate tiny script `_refresh_assets.py`) that copies the catalog's three CSS / JS files + two brand images into `<package>/assets/`, leaves `index.html` untouched.
  2. In the `STALE-ASSET` finding text, point at that command.
* **Solution Rationale:** Single idempotent fix path for the most-common post-refresh action.
* **Risks of Solution:** None — the copy is deterministic.
* **Trade-offs:** None.

---

### Issue P-17 — `_lint_mock.py` HTML parsing uses regex for cross-section structure checks

* **Identification:** `lint-html-regex-parsing`
* **Section Reviewed:** `_lint_mock.py` lines 285–316 (multi-workflow shell + orphan-screen check), lines 348–359 (cover-subgrid check), lines 417–442 (surface wrapper extraction with depth counting).
* **Problem Observed:** The script uses `html.parser.HTMLParser` for URL extraction but switches to plain regex for the structural sections (multi-workflow wrapping, orphan-screen detection, surface-wrapper depth tracking). The depth-tracking regex loop at lines 417–442 hand-rolls a stack-depth `<div>` matcher; it works for clean HTML but is brittle against `<!-- div -->` style comments or self-closing void elements with `div` substrings.
* **Risks Posited:**
  - A future catalog change that introduces a regex-confusing pattern (e.g. an SVG with `<div>` in a `<title>` comment) silently confuses the parser.
  - Each new structural check needs to re-derive the same parsing logic; complexity accretes.
* **Rationale:**
  - Principle 2 (Reliability): regex-as-parser is a known anti-pattern.
* **Proposed Solution:**
  1. Add an internal lightweight DOM-walking helper that uses `html.parser` to collect section ranges + their parent chains.
  2. Replace the regex-loop depth tracking with the helper.
* **Solution Rationale:** Strengthens lint correctness; removes a class of latent bugs.
* **Risks of Solution:** Marginal lint-time increase. The script is run once per package, so the cost is negligible.
* **Trade-offs:** Bit more code in the lint; clearer structure.

---

### Issue P-18 — "Both anchors fired in parallel" instruction relies on the LLM remembering both

* **Identification:** `anchor-parallel-invocation-burden`
* **Section Reviewed:** `SKILL.md` lines 644–681 (Anchor pass — REQUIRED, NON-SKIPPABLE).
* **Problem Observed:** The SKILL says "Fire `mock-coverage-anchor` + `mock-fidelity-anchor` in ONE foreground message (parallel)" but provides no scaffolding helper — relies entirely on the LLM correctly emitting two parallel Agent calls in the same response. The instruction is correct, but it's a single failure point: if the LLM emits them sequentially, the wall-clock doubles + the LLM may forget to fire the second one entirely.
* **Risks Posited:**
  - In long-running sessions with attention pressure, an LLM may fire only `mock-coverage-anchor` and skip `mock-fidelity-anchor`, missing fidelity findings.
  - The instruction is repeated three times in SKILL.md (lines 644, 657, 660–661) precisely because this failure mode has been observed.
* **Rationale:**
  - Principle 2 (Reliability): a procedure that re-emphasises itself three times signals the procedure has been violated.
* **Proposed Solution:**
  1. Make the two anchors a single named "anchor-pair" agent type (e.g. `mock-anchor-pair`) that internally fans out the two checks and returns combined results. The SKILL fires ONE agent.
  2. Or: add a tiny orchestration script `reference/scripts/_run_anchors.py` that the LLM invokes; the script spawns both anchors and returns a single JSON result.
* **Solution Rationale:** Removes the LLM's burden of remembering both; converts a two-tool-call coordination into one.
* **Risks of Solution:** Adds an indirection layer; if one anchor evolves independently, the pair-orchestration needs updating.
* **Trade-offs:** Slight added structure; substantial reliability gain.

---

### Issue P-19 — Production-readiness checklist has 18 items, several restate constraints already enforced upstream

* **Identification:** `production-checklist-redundancy`
* **Section Reviewed:** `SKILL.md` lines 936–1011.
* **Problem Observed:** Of the 18 checklist items:
  - "**Coverage-level gate asked once**" — implicit in following § Curate.
  - "**Catalog fragments used verbatim**" — enforced by `mock-fidelity-anchor` (and the lint's `KNOWN-BAD` patterns).
  - "**Standard-field placement discovered from live source**" — enforced by anchor + warning on cover.
  - "**Real Odoo logo on the cover**" — enforced by `STALE-ASSET` (logo is a copied asset).
  - "**Body has padding-bottom for the fixed walkthrough bar**" — already baked into `annotations.css` per the bullet's own note.
  - "**`odoo.css` / `annotations.css` / `walkthrough.js` copied** into `<output>/assets/`; icon sprite **inlined**" — enforced by lint `SVG-USE` + `STALE-ASSET` + `ESCAPE`.
  - "**`_lint_mock.py <output> --steps ...` prints PASS**" — the lint itself is the gate.
  - "**Both anchors fired in one foreground message**" — covered by § Verify.
  - "**Output is in the right place**" — covered by § Entry: Output destination.
  About half the checklist restates upstream gates.
* **Risks Posited:**
  - Repetition adds tokens.
  - Items that look load-bearing on a checklist but are actually upstream-enforced give the reader a false sense of "I need to manually check this."
* **Rationale:**
  - Principle 3 (Bulk).
  - Principle 7 (Token Efficiency).
* **Proposed Solution:**
  1. Reduce the checklist to items that are NOT enforced by an upstream gate — i.e., judgment items: marker count, click-path connectivity beyond `data-mock-goto`'s target-resolves check, business-voice on prose, variant-axis appropriateness, density calibration.
  2. Move the upstream-enforced items into a "Mechanical gates (auto-checked)" footnote so the reader knows they exist but doesn't tick them.
* **Solution Rationale:** Recovers the checklist's value as a JUDGMENT scaffold; removes the noise.
* **Risks of Solution:** Small — items moved to the footnote stay discoverable.
* **Trade-offs:** Checklist drops to ~9 items; mechanical-gate footnote adds 5 lines.

---

### Issue P-20 — No version metadata on the catalog itself

* **Identification:** `catalog-version-unstamped`
* **Section Reviewed:** `reference/catalog/odoo.css`, `reference/catalog/components/*.html`.
* **Problem Observed:** `REFRESH.md` ("Current baseline: Odoo version: 19") declares the catalog targets Odoo 19, but the catalog files themselves do not carry a version stamp. A generated mock includes a copy of `odoo.css`; a reader inspecting the mock cannot tell which Odoo version it targets without finding the parent skill and reading `REFRESH.md`.
* **Risks Posited:**
  - Generated mocks ship without traceability to the source version.
  - A mock generated against Odoo 19 and reviewed after a hypothetical Odoo 20 catalog refresh would visually drift; the reviewer can't easily tell what changed.
  - The first Tier-1 Improvement in `industry_standards_audit.md` already names this gap.
* **Rationale:**
  - Principle 8 (Structural Integrity): catalog provenance is reachable only out-of-band.
* **Proposed Solution:**
  1. Add a header comment at the top of `odoo.css` and `annotations.css` and `walkthrough.js`: `/* Catalog generated from Odoo 19 (refreshed YYYY-MM-DD). See REFRESH.md for the source map. */`.
  2. Have the generated mock's cover kicker derive the version line from the same constant rather than the existing hand-authored "Odoo 19 · Enterprise".
* **Solution Rationale:** Traceability from any generated mock back to the catalog version that produced it.
* **Risks of Solution:** Minor — version constants need to update on refresh, which `REFRESH.md` already documents.
* **Trade-offs:** None.

---

## Summary

The skill's hard-edge mechanics — self-containment lint, asset freshness diff, the two-anchor pre-finish gate, the 8-dimension coverage inventory, the variant-axis chip-row, source-first catalog discipline — are strong and well-designed. The pain points sit at the documentation seams:

- **SKILL.md is too thick** (P-06). It has absorbed reference material that belongs in `catalog_chrome.md` / a future `cover_discipline.md` / `checklist.md`. The orchestration entry-point would be ~600 lines if the absorbed material went home.
- **Several canonical-text strings live in two or three places** (P-02, P-11, P-12, P-13). Each duplication is a future drift opportunity; SKILL.md already shows one such drift (P-01: Next-button labels).
- **One concrete drift between SKILL.md and the running JS code exists today** (P-01) and should be the first fix because it's a textual edit that can be done in 60 seconds.
- **The agent YAML is the most-likely consumer of stale material** (P-04). It's the first thing pasted into a parent-skill invocation and is several procedural generations behind SKILL.md.
- **A scattering of low-risk hygiene items** (P-08 TODO, P-09 stale files, P-15 / P-16 small UX gaps, P-20 missing version stamp) can be cleaned up together with low effort.

If only three changes were made, the highest-leverage triple is:

1. **P-01**: align SKILL.md Next-button labels with the code (silent correctness fix).
2. **P-04**: rewrite the agent YAML to match current SKILL.md procedure (alignment at the most-common entry-point).
3. **P-06**: migrate the absorbed reference material out of SKILL.md (~400-line reduction in the orchestration prompt every invocation pays for).

The remaining items are improvement-grade rather than risk-grade.
