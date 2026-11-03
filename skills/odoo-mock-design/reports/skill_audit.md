# Skill Audit — `odoo-mock-design` (re-audit)

**Audit date:** 2026-10-08
**Supersedes:** the 2026-06-15 audit (preserved below as the *Prior-audit verification table*). That snapshot is stale — it describes an 1011-line SKILL.md, 38 components, 4 scripts, an unstamped catalog and no `.gitignore`; none of its line numbers resolve against the current tree.
**Audit subject (current state):** SKILL.md **784 lines**; **13** reference docs/templates; **8** Python scripts + **4** calibrate `*.js`; **41** catalog component fragments; `_lint_mock.py` **1237 lines**; catalog **calibrated to Odoo 20 Enterprise (2026-10-07)** with a machine-read version stamp on `odoo.css` line 1.
**Method:** four parallel read-only dimension audits — (A) SKILL.md structure/self-duplication, (B) cross-file drift, (C) scripts correctness/robustness, (D) catalog/calibration governance — each re-verifying the prior P-items against the live files and hunting new issues. The two HIGH findings were independently re-verified at the code+fact level by the lead.
**Stance:** read-only; findings cite live `file:line`.

---

## Executive verdict

The skill is in **materially better shape than the prior audit** — the architecture (self-containment lint, live-hash asset freshness, two-anchor pre-finish gate, 8-dimension coverage inventory, source-first catalog discipline, single-file bundle output) is strong, and **17 of the 20 prior P-items are fixed or resolved** (table below). The re-audit's own value is concentrated in **two newly-introduced HIGH-severity lint bugs that false-FAIL a *canonical* mock** — i.e. the lint now blocks correct output composed verbatim from the catalog, and because lint gates `_bundle_mock.py`, it blocks delivery. These are the priority fixes. Everything else is Medium/Low: calibration-uniformity overclaim, residual duplication, and the long-standing regex-as-HTML-parser debt (which has grown, and is the root cause of both HIGH bugs).

**Fix these two first (both verified, both hard blockers):**
1. **H-1 — `CLASS-UNKNOWN` false-fails verbatim catalog fragments.**
2. **H-2 — `VARIANT` check truncates the screen body at the first nested `</section>`.**

---

## Remediation status (acted on 2026-10-08, same day)

Findings below were acted on immediately after this audit. Commits (skills repo):
`29f93ef` (lint/script fixes), `4b9be94` (calibration honesty / drift / de-dup / hygiene).

| Finding | Status | Where |
|---|---|---|
| H-1 CLASS-UNKNOWN false-fail | **Fixed** (regression-verified) | `29f93ef` — `_catalog_class_tokens()` credits catalog-fragment classes |
| H-2 VARIANT nested-`</section>` truncation | **Fixed** (regression-verified) | `29f93ef` — `_screen_segments()` bounds at screen openers |
| M-1 regex-as-HTML-parser debt | **Mitigated** | `29f93ef` — comment-blanked depth balancers + H-2 segmentation; full `html.parser` rewrite not done |
| M-2 calibration-uniformity overclaim | **Documented** | `4b9be94` — REFRESH.md carry-over list; actual recalibration deferred to next pass (needs live v20 + captures) |
| M-3 `_gallery.html` sync gap | **Documented** | `4b9be94` — REFRESH.md step 6 resync note; auto-generation not done |
| M-4 SKILL.md length | **Partial** | `4b9be94` — de-dups applied (784→771); deeper Verify/Edition compression deferred (owner call — trades documented anti-pattern detail for length) |
| M-5 exact-vs-flexible matching | **Fixed** | `29f93ef` |
| L-1 output-destination 3× | **Fixed** | `4b9be94` |
| L-2 asset-handling 2× | **Fixed** | `4b9be94` |
| L-3 tier behavioral rules | **Fixed** | `4b9be94` → `coverage_levels.md` |
| L-4 Next-label 4th copy | **Fixed** | `4b9be94` |
| L-5 agent-YAML enforced gate | **Fixed** | `4b9be94` |
| L-6 page_skeleton hardcoded version | **Fixed** | `4b9be94` (SLOT) |
| L-7 small intra-SKILL repeats | **Partial** | `4b9be94` — edition-gate argument de-duped; anchor-emphasis-3× and the 8-dimension re-enumeration left as-is |
| L-8 reference_pattern axis-chip restatement | **Fixed** | `4b9be94` |
| L-9 undocumented components | **Fixed** | `4b9be94` — `view_types.md` |
| L-10 twin overclaim | **Fixed** | `4b9be94` |
| L-11 dual stamp drift | **Fixed** | `4b9be94` |
| L-12 script edge cases | **Fixed** | `29f93ef` — bundle `data=`, calibrate Chrome guard, quote-tolerant axes |
| I-1 on-disk `.DS_Store`/`__pycache__` | **Fixed** | deleted (were untracked/gitignored) |
| I-2 industry-audit backlog re-status | **Fixed** | `4b9be94` |

**Still open:** M-2 recalibration (the actual capture/probe pass for the 9 frontend fragments), M-4 deeper length reduction, M-1 full parser rewrite, and the two L-7 residuals. All are judgment/effort calls left for the skill owner, not blockers.

---

## Findings (severity-ranked)

### HIGH — real bugs that block a correct mock

**[H-1] [correctness] `CLASS-UNKNOWN` rejects container classes the catalog styles only via child selectors — `_lint_mock.py:939-995`**
The rule credits a class only if a matching token appears in some CSS selector, but its crediting regex `re.finditer(r'\.([_a-zA-Z][\w-]*)', css_text)` captures the *full hyphenated* token. So `.o-mail-ActivityList-header` credits `o-mail-ActivityList-header`, never the bare container `o-mail-ActivityList`.
**Verified:** `odoo.css` defines only `.o-mail-ActivityList-header` and `.o-mail-ActivityList-title` — there is no bare `.o-mail-ActivityList` selector — yet `components/chatter.html:153` uses `<div class="o-mail-ActivityList">`. Composing the canonical `chatter.html` fragment verbatim therefore raises a `CLASS-UNKNOWN` blocker (agent also reproduced it live; same class of failure hits `studio.html`'s `o_web_studio_*` and `website_form.html`'s `o_mark_required` / `s_website_form_label_content`). This directly contradicts SKILL.md's "compose from `components/*.html` verbatim" happy path.
**Fix:** credit a class when it appears as *any* selector segment (treat `o-mail-ActivityList` as defined if `.o-mail-ActivityList-header` or `.o-mail-ActivityList .x` exists), or keep a small allowlist of container-only classes. Then re-run against every fragment to confirm zero false-positives.

**[H-2] [correctness] `VARIANT` reads only up to the first nested `</section>` — `_lint_mock.py:251-266`**
The screen-body matcher `<section[^>]*mock-screen...>(.*?)</section>` is non-greedy under `re.DOTALL`, so it stops at the first `</section>` *inside* the screen.
**Verified:** six catalog components contain nested `<section>` (`website_form.html`, `portal.html`, `dashboard_sidebar.html`, `search_panel.html`, `login_website.html`, `page_skeleton.html`). A `.mock-screen` built from one of these whose `data-mock-variant` children sit after the inner `<section>` wrongly fails `[VARIANT] axes declared but no child carries data-mock-variant`, and per-value validation past the inner close is silently skipped. An empty-form-vs-confirmation State axis on a website/portal screen is a common, legitimate case this blocks.
**Fix:** segment the document at `.mock-screen` openers (the `GUARD-LANDING` block at `:891-895` already does this) instead of bounding on `</section>`.

### MEDIUM

**[M-1] [robustness] Regex-as-HTML-parser debt has grown (root cause of H-1/H-2) — `_lint_mock.py:692-705, 856-869, 1026-1039, 1086-1098`** (prior **P-17**, now worse). `SURFACE-LEAK` (×2), `GUARD-BANNER`, and `NESTING` extract a wrapper body by counting `<div`/`</div>` via repeated `re.search`, blind to HTML comments, CDATA and `<div/>`. A comment like `<!-- wrap each row in a <div> -->` skews the depth count. More regex structural rules (`GUARD-LANDING`, `NESTING`, two `SURFACE-LEAK` variants, `CLASS-UNKNOWN`) were added since the last audit. **Fix:** one shared `html.parser`-based range/parent helper, reused by all structural rules (fixes H-2 and this class together).

**[M-2] [freshness/governance] Global "Odoo 20" stamp overclaims uniformity — 9 frontend fragments were never recalibrated — `components/{login,login_website,website,website_form,portal,portal_my,pos,checkout,report}.html`.** These carry June mtimes; the 2026-10-07 pass (per `REFRESH.md`) redesigned only the backend webclient, and all 15 calibration-screen twins are backend. The single stamp asserts a v20 calibration that wasn't performed for these surfaces, with no per-fragment marker to tell verified from carried-over. **Fix:** re-verify them against v20 source/screens, or add an explicit "carried over from v19 — version-stable" list to `REFRESH.md` so the stamp doesn't assert work not done.

**[M-3] [hygiene] `_gallery.html` is a 194 KB hand-inlined duplicate of the fragments with no sync guard — `reference/catalog/_gallery.html`.** `_render_catalog.py` only *screenshots* the static gallery; nothing assembles it from `components/*.html` or SHA-diffs the two, so a fragment edit silently leaves the gallery stale (currently in sync — Oct-7 mtime). **Fix:** generate `_gallery.html` from the fragments at render time, or add a lint/CI check that each fragment's markup is current in the gallery.

**[M-4] [length] SKILL.md still 784 lines, above the ~600 target — prior P-06 only partially closed — `SKILL.md:1-784`.** Big verbatim blocks were correctly delegated (cover HTML → `cover_callouts.html`/`cover_discipline.md`; checklist → `checklist.md`; multi-workflow topology → `catalog_chrome.md`). Still bloated/self-repetitive: the Edition gate (`176-218`), the Verify step (`492-597`, mostly anti-pattern war-stories), and the eight-dimension inventory (`229-294`). **Fix:** compress the anti-pattern narration to one line each and tighten the Edition gate; target ~600.

**[M-5] [robustness] Inconsistent `.mock-screen` / `.mock-marker` matching (exact vs flexible) — `_lint_mock.py:804, 891, 522` vs `252`.** `VARIANT` matches `class="[^"]*\bmock-screen\b[^"]*"` (tolerant), but `GUARD-LANDING`, `MARKER-TEXT` and the inline-position marker checks require the *exact* literal `class="mock-screen"` / `class="mock-marker"`. A screen authored as `class="mock-screen o_cover"` is silently skipped by the exact-match rules (false-negatives). **Fix:** use the `\b…\b` form everywhere.

### LOW

- **[L-1] [self-dup] Output-destination derivation stated 3× in SKILL.md** (`:44-51` full rule, `:70-75`, `:384-387`) + a 4th in `checklist.md:92-97`. Keep the full rule in § Entry; reduce the others to "(`<mocks>` per § Entry)".
- **[L-2] [self-dup] Asset-handling rules stated twice in full** — `SKILL.md:79-90` (§ Output Contract) vs `:430-442` (§ Assemble), same copy-list + same `file://` rationale. State the mechanism once in § Assemble.
- **[L-3] [cross-file dup] Tier *behavioral* rules restated** — `SKILL.md:357-360` & `:368-373` ≈ `coverage_levels.md:69-86` (report-centric collapse; fixed boundaries). Canonical tier *definitions* are single-sourced (good); replace these two with a cross-ref. (prior **P-11** residual)
- **[L-4] [duplication] Untracked 4th copy of the Next-button labels** — `walkthrough.js` (declared SSOT) names only `walkthrough_bar.html` + `catalog_chrome.md` in its sync comment, but `cover_discipline.md:141-152` restates the full label set. All agree today; a future change following the sync-comment would miss it. Add `cover_discipline.md § 5` to the sync comment or cross-ref it. (prior **P-01** residual)
- **[L-5] [drift] Agent YAML omits the enforced model-verification gate** — `SKILL.md:170-174` mandates `_check_odoo_source.py --models …` with an `exists=false` halt; `agents/odoo-mock-design.yaml:33-40` covers only `field_placement.md` Step 0. Add the call to the YAML step 1.
- **[L-6] [drift] `page_skeleton.html:54` hardcodes `Odoo 20 · Enterprise`** while `cover_discipline.md:28-33` says the scaffolder writes the version and authors must never hard-code it. The skeleton is the hand-author path → a verbatim copy inherits a literal "20". Make it a `<!-- SLOT: Odoo <major> · <edition> -->`.
- **[L-7] [self-dup] Several smaller intra-SKILL repeats** — Edition-gate "standard models live under odoo/addons" argument twice (`:190-192`, `:199-203`); eight dimensions re-enumerated at `:571-573` (cross-ref § Comprehension step 1 instead); "both anchors in one parallel message" emphasized 3× (`:530-531, 548, 570`). (prior **P-18** observation; the anchor-pair orchestration script was never adopted — a design choice, not a bug.)
- **[L-8] [duplication] `reference_pattern.md:117-129` still restates 4 axis-chip rules** already canonical in `cover_discipline.md § 4` (the worst P-12 copy — the 5-callout text — is fixed via cross-ref). Trim to the cross-ref.
- **[L-9] [coverage] Two components undocumented** — `checkout.html`, `portal_my.html` are routed by no doc (`view_types.md` points checkout authors at `website.html`). Both are styled/valid → doc gap. Add to `view_types.md § App surfaces`, or retire `portal_my.html` if `portal.html` supersedes it.
- **[L-10] [freshness] `REFRESH.md` step 5 claims "every capture has a twin" but 9 of 24 `screens.json` entries have no twin** in `reference/calibration/screens/`. Add the missing twins or soften the wording.
- **[L-11] [governance] Dual version stamp can drift** — `odoo.css` line 1 (machine-read) vs line 5 (human-only, unparsed); `REFRESH.md` step 2 bumps both by hand. Make the human header reference the parsed line, or assert equality.
- **[L-12] [robustness] Script edge cases:** `GUARD-LANDING` only matches single-quoted `data-mock-variant-axes` (`_lint_mock.py:897`); `_bundle_mock.py:52` rewrites only `href|src|poster` so a lint-accepted `<object data="assets/x.svg">` can never bundle (fails closed); `calibrate/render.js:13` & `probe.js:22` don't guard undefined `C.CHROME` (opaque error vs `capture.js`'s clean exit 2); dead `short = _short_workflow_title(...)` assignments at `_scaffold_mock.py:281, 328`.

### INFO / hygiene

- **[I-1]** `.DS_Store` (×3) and `__pycache__/*.pyc` (×7) are physically present in the tree, though now correctly covered by `.gitignore` (prior **P-09**: gitignore half done, delete half not). Not git-tracked — local only.
- **[I-2]** `reports/industry_standards_audit.md` has the STALE banner (good) but its Tier-1/2/3 backlog still isn't re-statused `[done]/[pending]/[supplanted]` (at least one Tier-1 item — the version stamp — is now done). (prior **P-07** residual)

---

## Prior-audit verification table (P-01 … P-20)

| # | Title (abbrev) | Status | Note |
|---|---|---|---|
| P-01 | Next-button label 3-way drift | **FIXED** | SKILL single-sources from `walkthrough.js`; residual untracked 4th copy → L-4 |
| P-02 | Triple-copy of 5 callouts | **FIXED** | `cover_callouts.html` is SSOT; scaffolder parses it at runtime |
| P-03 | `page_skeleton.html` stale cover | **FIXED** | now ships favicon, brand header, callout SLOT, step-list table; residual hardcoded version → L-6 |
| P-04 | Agent YAML pipeline drift | **FIXED** | rewritten as thin shell w/ current 6-stage flow; residual → L-5 |
| P-05 | Pre-anchor grep duplicates lint | **FIXED** | trimmed to the patterns lint can't catch |
| P-06 | SKILL.md absorbs reference material | **PARTIAL** | 1011→784; still > ~600 target → M-4 |
| P-07 | Industry-audit stale snapshot | **FIXED (banner)** | backlog not re-statused → I-2 |
| P-08 | Unactioned TODO in SKILL.md | **FIXED** | no TODO/FIXME in prose |
| P-09 | Stale `.DS_Store`/`__pycache__` | **PARTIAL** | `.gitignore` added; files still on disk → I-1 |
| P-10 | Coverage worked-example cited verbatim | **ADDRESSED** | relocated out of SKILL.md to on-demand `coverage_levels.md:120-125` (the proposed fix); verbatim numbers still there |
| P-11 | Tier definitions 3× in SKILL.md | **FIXED** | canonical in `coverage_levels.md`; residual behavioral-rule restatement → L-3 |
| P-12 | `reference_pattern.md` duplicate canon | **FIXED** | 5-callout text cross-ref'd; residual axis-chip rules → L-8 |
| P-13 | `field_placement.md` Step-0 inlined | **FIXED** | SKILL.md:170 is now the one-line reference |
| P-14 | Scaffold title naive truncate | **FIXED** | hard-caps `[:12]` + emits the WARN line |
| P-15 | Chrome soft-gate | **FIXED (doc)** | SKILL.md:669 gates it; script message wording still terse |
| P-16 | STALE-ASSET no fix flag | **FIXED** | `_refresh_assets.py` added (idempotent, SHA-gated, leaves index.html) |
| P-17 | Regex HTML structural parsing | **CONFIRMED (worse)** | more regex rules added; root cause of H-1/H-2 → M-1 |
| P-18 | Anchor-pair orchestration | **NOT ADOPTED** | still two manual anchors; design choice, not a defect |
| P-19 | 18-item checklist restates upstream | **FIXED** | split into Judgment / Mechanical-gates in `checklist.md` |
| P-20 | Catalog unstamped | **RESOLVED** | stamp on `odoo.css` line 1, machine-read by scaffolder + lint |

Scoreboard: **12 FIXED · 3 FIXED-with-residual (P-01/P-11/P-12) · 1 RESOLVED (P-20) · 1 ADDRESSED (P-10) · 2 PARTIAL (P-06/P-09) · 1 FIXED-doc (P-15) · 1 CONFIRMED-worse (P-17) · 1 NOT-ADOPTED (P-18).**

---

## What's strong (keep)

- **Self-containment is a release gate**, not a hope — the lint rejects external refs / path-escapes / external SVG `use`, and `_bundle_mock.py` produces one offline file.
- **Asset freshness uses live SHA-256 diffs** of each mock's `assets/<x>` vs `catalog/<x>` — no stored-hash drift class — with `_refresh_assets.py` as an idempotent, non-destructive fix path.
- **Single-source canon**: 5 callouts (`cover_callouts.html`), tier definitions (`coverage_levels.md`), source-unavailable warning (`source_unavailable_warning.md`) are each defined once and consumed by SKILL.md + docs + scaffolder, with cross-refs rather than copies.
- **Version governance**: a real machine-read stamp drives both scaffolder and lint; the cover-vs-stamp check is correctly a non-failing NOTE.
- **Clean tooling**: all 8 Python scripts byte-compile, all 4 calibrate JS pass `node --check`, CLIs match SKILL.md, and the scaffold→lint→bundle chain fails closed.
- **Output model is described identically** across SKILL.md, agent YAML, and every reference doc (one bundled `<name> - mock.html` from an editable `_reference/` package).

## Top recommendations (highest leverage first)

1. **Fix H-1 and H-2** — they block correct, canonical mocks today. Best done together via M-1 (one `html.parser` helper replaces the regex body/segment extraction and the class-crediting scan).
2. **Resolve the calibration overclaim (M-2)** — either recalibrate the 9 frontend fragments to v20 or document them as version-stable carry-overs, so the stamp tells the truth.
3. **Add a `_gallery.html` sync guard (M-3)** and finish the SKILL.md slim-down (M-4).
4. **Mop up the residual duplications and drift seams (L-1…L-8)** — each is a one-edit cross-reference that removes a future drift opportunity.

*Written for: maintainers of the `odoo-mock-design` skill.*
