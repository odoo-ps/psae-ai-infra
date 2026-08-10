---
name: odoo-mock-design
description: Generate a self-contained, click-through HTML mock of the proposed Odoo screens so stakeholders and developers can *see* a solution before it's built. Reads an existing solution artifact (an odoo-write-specifications spec folder, or a written brief), maps each workflow step to an Odoo view type (form / list / kanban / wizard), and composes screens from a baked "recognizably-Odoo" component catalog (real Odoo 19 design tokens, layouts, class names). Output is a portable folder — index.html + assets/ — with workflow navigation and numbered annotation markers, and ZERO external/network dependencies (lint-enforced). Runs two ways: embedded at the finish line of odoo-write-specifications, or standalone against a brief/spec you point it at.
when_to_use: Use this skill when someone wants a visual mock-up of proposed Odoo screens to explain or sign off a solution — either right after odoo-write-specifications, or standalone against an existing brief/spec. NOT for building a working addon (that's odoo-plan-development) and NOT for writing the spec itself (that's odoo-write-specifications).
allowed-tools: Read, Edit, Write, Bash, Grep, Glob, Agent, AskUserQuestion, ToolSearch, TodoWrite
---

# Odoo Mock Design

Turn a written solution into an interactive visual mock of its Odoo screens.
Skill-specific discipline below; cross-cutting principles live in
[`skills/_shared/principles.md`](../_shared/principles.md) and apply here too.

The defining rule: **the catalog is built once; generation composes from it.**
Odoo source was read at skill-build time to author `reference/catalog/`. Mock
generation reads the catalog and its reference docs — it does **not** re-derive
styling from Odoo source per run.

## Entry: two invocation modes (no plan mode)

This skill is **exempt from plan mode (P11)** and from architecture detection
(P13): it writes only inside its own output folder, touches no DB, installs
nothing, and produces a mock — not deployable code. The quality gate is the
pre-finish anchor pass, not `ExitPlanMode`. Same carve-out `odoo-write-specifications`
uses; see the P11 exemption note in `_shared/principles.md`.

- **Workflow 1 — embedded.** `odoo-write-specifications` invokes this skill at its
  finish line and passes a **spec-folder path**. No interview: read the spec and
  generate.
- **Workflow 2 — standalone.** The user runs this skill directly. It **requires
  an existing brief or spec as input** — there is no solution interview. Ask the
  user for the path to either an `odoo-write-specifications` spec folder, or a written
  brief (`.md`/`.txt`).

Mode is detected by whether a spec-folder path was handed in (Workflow 1) or the
user is starting cold (Workflow 2).

**Output destination is derived from the input, not the workflow mode.**
Inspect the input path:

- **If the input IS a spec folder** (matches `<repo>/specifications/<task-code> - <client> - <slug>/`, or contains `_reference/_build_<task-code>.py` / a spec-shaped `.docx`), output goes **inside that spec folder** at `<spec-folder>/mocks/`. Applies to BOTH workflows — a standalone invocation pointed at a spec folder still lands the mock alongside the spec, not orphaned at the repo root.
- **If the input sits *under* a spec folder** (e.g. the user pointed at a workflow-specific brief inside `<spec-folder>/_reference/notes/wf1.md`), walk upward to the nearest spec-folder ancestor and use `<spec-folder>/mocks/`.
- **Only when the input has no spec-folder context** (a bare `.md`/`.txt` brief outside any `specifications/` tree) does the fallback apply: output to `<repo_root>/mocks/<3-word-kebab>/` (slug auto-derived from the brief). Create `mocks/` on first run.

The rule is *"output lives next to the spec it visualises whenever a spec exists; orphaned mocks only when nothing to attach to."* Mocks generated from a spec but stored at the repo root drift from the spec they explain — keep them adjacent.

## When To Use

A mock explains a *proposed* solution visually. Reach for it after a spec exists
(or a solid brief), when a stakeholder needs to see the screens to sign off, or
when a developer wants the screen shapes alongside the spec. It is not a working
app and never pretends to be — fields don't compute, records don't save. It
shows **states and the path between them**.

## Output Contract

Produce, in order:

- **A package folder** — destination is derived from the input (see § Entry,
  *Output destination*): `<spec-folder>/mocks/` whenever the input is or sits
  under a spec folder; `<repo_root>/mocks/<3-word-kebab>/` only when the input
  has no spec-folder context. The fallback creates `mocks/` on first run.
- **`index.html`** at the package root — one `.mock-screen` section per
  meaningful workflow step, composed from catalog fragments, plus exactly one
  walkthrough bar.
- **`assets/`** inside the package — a **copy** of the catalog assets the page
  uses: `odoo.css`, `annotations.css`, `walkthrough.js`. Copied, not linked;
  `index.html` references only `./assets/...` for these.
- **Inline the icon sprite** — paste the contents of `catalog/icons.svg` into
  `index.html` (a hidden `<svg>` at the top of `<body>`) and reference glyphs
  with same-document `<use href="#o-id">`. Do **NOT** copy `icons.svg` as a
  separate asset and link it: external SVG `<use href="file.svg#id">` is blocked
  over `file://`, so every icon silently vanishes when the package is opened as a
  local file. (`_lint_mock.py` flags any external `.svg#` ref as `SVG-USE`.)
- **Self-contained & portable** — no `http(s)`/CDN references, no external fonts
  or images, and no path that escapes the package root (into `skills/`, an
  absolute path, or a parent dir). Mechanically enforced by `_lint_mock.py`.
- **Complete** — every workflow step has a screen; the click-path connects them;
  annotation markers are grounded in the brief; no placeholder strings
  (`TODO`/`TBD`/`Lorem ipsum`).

A package that references the skill folder, has a step with no screen, carries
placeholder strings, or fails the self-containment lint does NOT satisfy the
contract.

## Reference Material (Read Before Building)

- [`skills/_shared/principles.md`](../_shared/principles.md) — cross-cutting
  discipline. Read this first.
- [`reference/view_types.md`](reference/view_types.md) — which Odoo view type
  to mock for each step; per-view anatomy + density anchors.
- [`reference/style_guide.md`](reference/style_guide.md) — design tokens, the
  rules that make a screen read as Odoo, annotation conventions, source map.
- [`reference/cover_discipline.md`](reference/cover_discipline.md) — what the
  cover screen must carry (favicon, brand header, 5-callout block, workflow
  narrative table, Get Started). Cover callout text is single-sourced from
  [`reference/templates/cover_callouts.html`](reference/templates/cover_callouts.html).
- [`reference/catalog_chrome.md`](reference/catalog_chrome.md) — per-fragment
  author discipline (navbar systray order, home-menu brand colors,
  control-panel cog placement, settings tab icons, kanban polish, pivot
  expand affordances) AND § Multi-workflow chrome (cover topology,
  walkthrough-bar layout, per-workflow overview shape, Next-button labels).
- [`reference/field_placement.md`](reference/field_placement.md) — how to
  discover where standard fields live, at runtime, from live
  `odoo/` / `enterprise/` source. Best-effort warning when source absent is
  single-sourced from
  [`reference/templates/source_unavailable_warning.md`](reference/templates/source_unavailable_warning.md).
- [`reference/interactions.md`](reference/interactions.md) — the `data-mock-*`
  interaction API (tabs, modals, toggles, toasts, variant axes, UserError
  modals, custom-field help). Wired by `walkthrough.js`.
- [`reference/templates/coverage_levels.md`](reference/templates/coverage_levels.md)
  — canonical Core / Standard / Comprehensive definitions used by the
  Coverage-level gate (see § Curate the screen list).
- [`reference/checklist.md`](reference/checklist.md) — production-readiness
  judgment checks before declaring done; mechanical gates listed as a
  footnote.
- [`reference/catalog/`](reference/catalog/) — the baked component library:
  `odoo.css`, `annotations.css`, `walkthrough.js`, `icons.svg`,
  `app-icons.svg`, and 38 `components/*.html` fragments covering every
  standard Odoo view type and every major app surface (backend, POS,
  website, portal, account_report, spreadsheet, dashboard, gantt, activity,
  cohort, map, grid, hierarchy, studio, discuss, settings, printed PDF,
  login, apps_menu, calendar week). See `view_types.md` § App surfaces for
  which fragment to pick. Render the gallery with
  `reference/scripts/_render_catalog.py` to eyeball after edits.
- [`reference/samples/reference_pattern.md`](reference/samples/reference_pattern.md)
  — annotated walk-through of a polished mock package; the calibration
  target.
- [`reference/REFRESH.md`](reference/REFRESH.md) — how to refresh the catalog
  on an Odoo version bump (it's hand-authored, not generated).

## Generation Pipeline (both modes)

**Curate, don't bulk-up.** The skill aims for **the smallest faithful
mock** — typically **4–6 primary screens** for a workflow, lifted to 7–8
only when the brief genuinely requires it (multi-actor, multi-workflow,
explicit supporting-surface request). Every additional screen, marker,
field, row, and supporting surface earns its place — pass it through
*"would the reader miss this if it weren't there?"* If no, drop it.

### 1. Comprehension (ingest + screen list, single pass)
- **Spec folder** (Workflow 1, or Workflow 2 pointed at one): prefer the
  structured `SPEC_DATA` dict in `<spec-folder>/_reference/_build_<task-code>.py`.
  Fall back to the `.docx` if absent.
- **Brief** (Workflow 2 with no spec): read the `.md`/`.txt`.
- **Source-availability check** (`field_placement.md` Step 0). Without
  `odoo/`/`enterprise/`, screens become best-effort — say so on the cover.
- **Model verification (enforced).** Run
  `python3 skills/_shared/scripts/_check_odoo_source.py --models <comma-list of standard Odoo models named in brief/spec>`
  once. `exists=false` halts screen composition; `edition=enterprise`
  on a community instance triggers the enterprise/community cover callout.
- **Edition gate (ENFORCED — sets the mock's default look & feel; NEVER
  inferred, NEVER silently defaulted).** The chrome edition (Enterprise =
  white navbar, no `o-community`; Community = purple navbar via
  `<body class="o-community">`) is DETECTED from source presence, then baked
  into `<body>` and the cover kicker (`Odoo <ver> · Enterprise` /
  `· Community`). Decision procedure, in order:
  1. Probe for Enterprise source once:
     `ls -d enterprise 2>/dev/null && ls enterprise/web_enterprise 2>/dev/null`
     (the presence of an `enterprise/` addons tree containing `web_enterprise`
     is the signal).
  2. **If Enterprise source IS present → the mock MUST default to Enterprise
     chrome.** Do NOT add `o-community` to `<body>`; kicker reads
     `· Enterprise`. This is **not overridable by inferring "Community" from
     where standard models resolve** — standard models ALWAYS live under
     `odoo/addons` (Community core) even on an Enterprise install, so their
     resolution path says nothing about the deployment edition. Enterprise
     source present ⇒ Enterprise look.
  3. **If Enterprise source is NOT present → do NOT assume Community. ASK the
     user** with a single `AskUserQuestion` (options: *Enterprise
     (Recommended)* / *Community*) which edition the target deployment runs,
     and apply their answer. Only a user "Community" answer (or an explicit
     Community-only workspace the user confirms) sets `o-community`.

  The recurring failure this gate closes: standard models resolving under
  `odoo/addons` were mistaken for a *Community deployment*, so the mock
  shipped with the wrong purple chrome even though `enterprise/` was present.
  Presence of Enterprise source is authoritative; absence is a QUESTION, not
  a Community default.

  **This gate is enforced in three layers, not just this prose:**
  - *By construction* — `_scaffold_mock.py` emits a bare `<body>` + a
    `· Enterprise` kicker, so the skeleton starts Enterprise. Switching it to
    Community is a deliberate act that must be justified by the ask in step 3
    (Enterprise source absent + user chose Community) — never a reflex.
  - *Mechanically* — `_lint_mock.py`'s `EDITION` rule (step 4) walks up to the
    workspace, and **FAILS** the build if `enterprise/` is present while the
    mock carries `o-community`/`· Community`, or if the `<body>` class and the
    cover kicker disagree. The lint cannot enforce the *absent ⇒ ask* branch
    (a lint can't prompt) — that stays your responsibility here.
  - *By review* — `mock-fidelity-anchor` (step 4) independently re-probes
    `enterprise/` and checks the chrome against it, rather than trusting a
    stated edition.

In ONE pass over the artifact, build the **workflow list + screen list +
variant axes**:

- Enumerate workflows (`SPEC_DATA['workflows']` or brief section breaks).
  Multiple workflows still produce ONE package; the chrome's workflow
  selector scopes navigation (`interactions.md` § Multi-workflow packaging).
- **Build the FULL surface inventory FIRST — this is the coverage floor.**
  Before listing screens, enumerate EVERY surface-bearing thing the spec
  names — not a partial slice. The floor has EIGHT dimensions in two classes;
  reconcile each item to ≥ 1 screen (or rendering) **or** an
  explicitly-recorded exclusion reason. **SURFACE dimensions** (does a screen
  exist?):
  1. **Actors** — the BPMN swimlane `lanes` (`name`/`sub`) on each workflow,
     plus user-story actors. (A "Customer / Online" lane with no website
     screen is a hole.)
  2. **Apps / surfaces** — §3 Apps Impacted + §3.2 New Custom Apps, AND the
     `Automated Behaviours` triggers (a row like "online submission → create
     a CRM lead" names a **website** and a **CRM** surface even when no
     `Screens & Interactions` row does).
  3. **New models** — every `New Models` row across all workflows. Each new
     model's **`Views Required`** is a promise of a surface (a List/Form
     gets a screen, or is explicitly folded/excluded). A new model that
     lives inside an already-covered app (e.g. a config/criteria model in
     the custom app) is STILL its own surface — app coverage does NOT imply
     model coverage.
  4. **Menus** — every `Navigation & Menus` entry, especially
     `… → Configuration` menus. A config menu names a setup surface.
  5. **Reports** — every `Reports & Analytics` row (pivot / graph /
     dashboard). A named report is a surface (or an explicitly-recorded
     opt-out).
  6. **Notifications** — emails / activities / printed PDFs the spec names
     (a voucher email, an expiry activity, a receipt PDF). Each is a surface
     (an email/PDF preview) or a recorded opt-out.

  **BEHAVIOUR dimensions** (is the behaviour RENDERED somewhere — a State-axis
  value or a dialog, not necessarily a NEW screen?):
  7. **Lifecycle states** — every value of a model's status field + the state
     transitions in `Automated Behaviours`. Each meaningful state is a
     State-axis variant on its screen (draft → agreed → validated → redeemed
     → expired → void), or an explicit exclusion.
  8. **Guard rules / negative paths** — every `Business Rules & Validations`
     row + every unmet-precondition path of a state-changing action. Each
     renders as a UserError dialog / guard State / banner, or is excluded.
     (This is the dimension whose omission produced an un-gated "Agree" with
     no blocked-precondition rendering.)
  9. **Integration touchpoints (no-UI surfaces)** — every inbound webhook,
     outbound API call, and email-alias intake the spec names
     (`dev_handoff.integration_surface`, §3 Automated Behaviours). These have
     **no screen of their own** — they are the first case where a coverage-floor
     item is NOT a surface. Render each as its **effect**: the State-axis value
     the integration drives (e.g. *Approved (via partner webhook)*,
     *Conversion failed*, an *Email* source badge on the intake screen) **plus a
     marker** explaining the mechanism. Then **list every integration touchpoint
     in the cover's "marker-only integration" callout** — that list IS the
     recorded coverage, and the coverage-anchor audits against it. The recurring
     failure mode is dropping one channel (an email intake left off the callout
     reads as a silent omission, not an intentional no-screen). Never invent a
     screen for an integration that has no UI; never leave one entirely
     unrendered either.

  (`New Fields` is NOT a floor dimension — it is per-screen fidelity: every
  solution-added field appears on its screen with the `o_field_help` "?"
  marker. "Solution-added" covers stored, computed, related, and relational
  fields (Many2one / One2many / Many2many), plus standard fields the solution
  overrides — see `reference/interactions.md` § Custom-field help. Don't
  conflate field-rendering with screen-coverage.)

  **Do NOT derive the screen list from the per-workflow `Screens &
  Interactions` subsection alone** — it is typically operator-centric and
  silently omits customer-facing, CRM, Inventory, Loyalty, config-model and
  reporting surfaces the other four dimensions still demand. **Reconcile the
  WHOLE inventory in one pass — do not stop at actors/apps.** The recurring
  failure mode is a *partial* floor: closing the actor/app holes while a new
  config model, a Configuration menu, or a named report (each inside an
  already-covered app) silently falls through. Record the inventory + each
  item's screen-or-exclusion so the anchor can audit against it (§ Verify).
- Per workflow, identify the **primary states the user moves through**.
  Usually 3–5 in a typical engagement.
- Per primary state, identify the **axes of variation** the brief makes
  load-bearing — tracking type (Lot/Serial), state (Unallocated / Partial /
  Allocated / Locked), actor (Sales rep / Manager / Portal). Each genuine
  axis becomes a chip on that screen's walkthrough-bar chip-row
  (`interactions.md` § Screen variants).
- Identify the **guard rules** the brief defines. By default each guard
  lives as a **State-axis value on the relevant primary screen**, not as
  its own screen. A guard earns its own screen only when it redirects to a
  different surface or the brief narrates it as a standalone step.

If the artifact is too thin to support a screen list (no models, no
actors, no workflow), **stop and recommend running
`odoo-write-specifications` first.** Inventing screens the brief doesn't
support is the primary failure mode here — refuse.

### 2. Curate the screen list
With the candidate list in hand, prune to the smallest faithful set:

- **Drop screens that don't change what the reader sees.** Two screens
  that differ only by a badge or a single field → one screen + a State
  axis on it.
- **Never prune below the coverage floor (step 1).** Pruning removes
  *redundant* screens; it must NOT remove the **only** representation of an
  actor or an impacted app. Collapsing the customer's website entry, the CRM
  lead the workflow creates, the inventory receipt it performs, or the
  eWallet balance it mints into "implied by a marker on another screen" is
  under-coverage, not curation. When in doubt between dropping a screen and
  keeping it, keep it if it's the sole surface for an actor/app.
- **Default screen count: 4–6 primary screens per workflow.** Above 6
  means the workflow is being over-narrated; ask whether two adjacent
  screens collapse into a State variant.
- **Apply per-view density anchors** per `view_types.md` §
  Density — populate to *workflow weight*, not to a row/field quota.
- **Pre-plan markers per package, NOT per screen**: aim for 4–7
  total markers across the package, each pointing at a load-bearing
  solution element (`style_guide.md` § Annotation discipline).
- **Pre-plan field placement** from live source for standard models
  (`field_placement.md`). Standard fields the brief doesn't change stay
  where Odoo puts them — `sale.order` Warehouse / Salesperson live on
  *Other Info*, NOT the main sheet.

**Coverage-level gate — one explicit choice, asked ONCE.** Three tiers
(Core / Standard / Comprehensive) — canonical definitions live in
[`reference/templates/coverage_levels.md`](reference/templates/coverage_levels.md).
After building the step-1 inventory and BEFORE assembling, surface a single
`AskUserQuestion` so the user explicitly picks how much to render. Skip the
ask only when the level was already supplied (user named one; a caller
passed one — e.g. `odoo-write-specifications`'s finish-line handoff). Default
tier is **Standard**.

**The choices shown to the user MUST be concrete for THIS task — never the
generic labels.** Populate each `AskUserQuestion` option from the step-1
inventory just built, so the user sees exactly what their package will
contain before choosing. For each option give a **screen count** + the
**actual surfaces/screens**, phrased as the DELTA over the lower tier in the
option's `description`; use `preview` when a tier's full list is long.
Recompute every run. If the inventory can't differentiate the tiers (e.g.
single-actor, single-app brief where Core = Standard = Comprehensive), say
so and skip the gate.

**Report-centric / analytics specs collapse Standard into Comprehensive** —
the Comprehensive add-ons (peripheral config / reports / notifications) are
the subject itself, so Standard ≈ Comprehensive. Offer the two that actually
differ (typically Core vs Standard) instead of three identical packages.

Each of the eight step-1 dimensions is reconciled **at the chosen level**:
in-tier items have a screen / rendering; out-of-tier items are
**explicit, recorded exclusions** (never silent drops). The anchor audits
against this contract.

**Tier boundaries are fixed — don't reclassify to dodge work.** A surface
that is an actor's primary touchpoint or a core workflow step (the website
page where the journey *starts*, the CRM lead it *creates*, the inventory
receipt it *performs*, every primary state, every guard) is **Standard** —
never push it to Comprehensive-only to skip it at Standard. Conversely,
config / settings, reports, notifications and edge states are
**Comprehensive-only** — don't pull them into Standard by default.

**For ≤ 6 screens with a clear brief, do NOT confirm the screen list
with a separate AskUserQuestion.** Proceed directly to assembly. For
larger packages, surface a single confirmation listing screens by
title.

### 3. Assemble the package
- **Compose `index.html` in-conversation; never via a sub-agent. `Agent`
  is reserved for the Verify-step anchors.**
- Create the output folder + `assets/` subfolder (output destination per
  § Entry — `<spec-folder>/mocks/` whenever a spec is in the input
  context; orphan-path fallback only otherwise).
- **Optional starter scaffolder — `_scaffold_mock.py`.** If the input
  is a spec folder (Workflow 1 OR Workflow 2 pointed at a spec), you
  can emit a canonical skeleton in one shot:
  ```
  python3 skills/odoo-mock-design/reference/scripts/_scaffold_mock.py \
      "<spec-folder>"
  ```
  The script reads `_reference/_build_<task-code>.py`'s `SPEC_DATA`
  dict and writes `<spec-folder>/mocks/index.html` + the 5 catalog
  assets. The skeleton has:
    - Canonical brand header + favicon link
    - The conditional five cover callouts (only the ones whose
      trigger fires per the spec — multi-workflow inclusion, axes-
      hint inclusion, new-fields inclusion)
    - Per-workflow `<div class="mock-workflow">` shells with overview
      screens (multi-workflow)
    - One `<section class="mock-screen">` placeholder per `flow_strip`
      step with a `<!-- SLOT: -->` comment pointing at
      `components/*.html`
    - Walkthrough bar at the bottom
  The skeleton passes `_lint_mock.py` BY CONSTRUCTION. Generators
  then fill in each placeholder by composing from the catalog
  components. The scaffolder is purely additive — it doesn't decide
  WHICH screens belong, only emits placeholders for what's in
  `flow_strip`; pruning + supporting-surface curation remain the
  generator's job (see § Curate the screen list above).
  Skip the scaffolder if you prefer to hand-author from
  `page_skeleton.html` + `walkthrough_bar.html`; both paths produce
  the same canonical structure.
- **Cover discipline** — the cover screen carries the reader's
  onboarding. Full discipline lives in
  [`reference/cover_discipline.md`](reference/cover_discipline.md): five
  required structural elements (favicon, brand header, canonical 5-callout
  block, three-cell workflow narrative table, Get Started). Reader-facing
  prose follows [`reference/style_guide.md`](reference/style_guide.md)
  § Cover, overview, and meta-content voice — business, never technical.
  Canonical callout wording is in
  [`reference/templates/cover_callouts.html`](reference/templates/cover_callouts.html)
  (single source of truth). Cross-references replace inlining so wording
  changes propagate in one edit.
- **Copy** `odoo.css`, `annotations.css`, `walkthrough.js`,
  `odoo-logo.png`, AND `odoo-icon.svg` from `reference/catalog/`
  into `<output>/assets/`. The wordmark logo
  (`<img src="assets/odoo-logo.png">`) is the cover's right-side
  watermark; the icon-style logo (`<img src="assets/odoo-icon.svg">`)
  is the kicker icon AND the favicon
  (`<link rel="icon" href="assets/odoo-icon.svg"/>`). Both image
  assets resolve inside the package and pass the self-containment lint.
- **Inline `icons.svg`** at the top of `<body>` (do NOT copy it as a
  linked asset — external SVG `<use>` dies on `file://`).
- Build `index.html` from `components/page_skeleton.html`. **Compose
  screens from `components/*.html` fragments verbatim** — copy the
  markup, fill the SLOT comments, keep the catalog's classnames. Do not
  improvise alternative chrome from scratch. (The most common
  regression: hand-coding a navbar / control-panel / settings page that
  doesn't match the fragment, so the catalog's CSS doesn't recognize
  it.) When the catalog lacks something the brief needs, *extend the
  catalog and propose promotion in `REFRESH.md`* — see § Catalog
  governance below — never invent on the fly inside the package.
- **Surface-native vocabulary — backend classes don't cross.** Inside
  `.o_website`, `.o_portal`, or `.pos`, NEVER use backend form chrome
  (`o_field_row`, `o_form_label`, `o_field_widget`, `o_input`, `o_group`,
  `o_inner_group`, `o_list_view`). Each surface has its own catalog
  vocabulary for label/value rows, custom inputs, and inline callouts —
  see `reference/style_guide.md` rule 14 for the full
  Backend → Website → Portal → POS mapping table, and the corresponding
  catalog component files (`portal.html`, `website_form.html`,
  `pos.html`) for worked markup. Also NEVER hand-roll an inline
  `style="background:color-mix(...);border:..."` callout — every surface
  has a `.*-callout` / `.*-note` class that uses palette tokens. Both
  drifts are flagged by mock-fidelity-anchor as
  `fidelity:surface-backend-leak` / `fidelity:inline-callout` and by
  `_lint_mock.py` as KNOWN-BAD.
- **Multi-workflow shell** (only when ≥ 2 workflows): wrap each
  workflow's screens in `<div class="mock-workflow" data-workflow="…"
  data-workflow-title="…">`. Single-workflow → skip the wrapper. See
  [`reference/catalog_chrome.md`](reference/catalog_chrome.md)
  § Multi-workflow chrome for the full pattern (main cover + per-workflow
  overviews + cross-workflow Next chaining + walkthrough.js mechanics).
- **Variant axes on the screen**: set
  `data-mock-variant-axes='[{...}]'` (JSON) on `.mock-screen` for each
  screen that has > 0 axes. Tag swappable children with
  `data-mock-variant="<axis>=<value>"` (or comma-separated for
  AND-conditions). One axis on the screen → one chip in the chrome;
  multi-axis → multi-chip row.
- **Input-pending state**: every input awaiting user supply uses
  `o_input_pending` + a `data-mock-*` wiring (toggle / modal-open /
  goto). Painted-but-dead affordances are a fidelity blocker. Share
  picker panels (one `data-mock-toggleable="lot-picker"` for all rows
  pointing at it) — don't render N parallel dropdowns.
- **Annotation markers**: 4–7 per package; never paste marker
  explanatory text as inline `<p>` body copy — the `data-note`
  attribute is the marker's content, full stop.
- Every screen needs `data-screen`, `data-title`, `data-desc`. Wire
  navigation with `data-mock-goto` / `data-mock-next`.

### 4. Verify (single pass, lint once + single anchor pass)
- **Stage 1 lint** — run ONCE after assembly is complete:
  ```
  python3 skills/odoo-mock-design/reference/scripts/_lint_mock.py \
      <output_dir> --steps "Screen title 1" "Screen title 2" ...
  ```
  **`--steps` are SCREEN titles (one per content `.mock-screen`, matched
  against `data-title`), NOT the cover's numbered workflow steps and NOT
  variant/state labels.** Passing a state like `"Drill-down"` (a variant axis,
  not a screen) fails with `[COVERAGE] no screen found for workflow step`. List
  the content-screen titles; omit the cover and per-workflow overview screens.
  Fix mechanical findings (external refs, escapes, placeholders,
  variant attribute hygiene, multi-workflow shell hygiene). Re-run
  only after the fixes — not after every edit.
- **Pre-anchor hand-author check.** Two patterns the lint can't fully
  catch are worth a quick scan before the anchors fire:
  1. **Dead input-pending affordances.** Every `o_input_pending` /
     `data-mock-toggle="X"` MUST have a matching `data-mock-toggleable="X"`
     panel (or use `data-mock-modal-open`). The lint's `INPUT-PENDING`
     rule catches the toggle-with-no-wiring case; the corresponding
     panel-with-no-toggler case (a `data-mock-toggleable` that no element
     references) is worth a grep.
  2. **Guards living only in marker notes.** Every guard rule from the
     brief (`Business Rules & Validations`) must render as an actual State
     variant or an `o_dialog_user_error` modal — NOT merely described in
     a `data-note`. If the only place a rule appears is a marker's text,
     it isn't covered; `mock-coverage-anchor` will flag this.

  Other anti-patterns previously flagged here as a grep table have moved
  into `_lint_mock.py` (KNOWN-BAD / GUARD-BANNER / WORKFLOW-TITLE /
  MARKER-TEXT / SURFACE-LEAK / INLINE-CALLOUT rules). Don't re-grep what
  the lint already catches.
- **Anchor pass — REQUIRED, NON-SKIPPABLE.** Fire `mock-coverage-anchor`
  + `mock-fidelity-anchor` in ONE foreground message (parallel). This
  replaces `ExitPlanMode`. **The mock is not deliverable until both
  anchors return with zero unresolved `blocker` findings. Lint PASS is
  NOT a substitute** — lint catches mechanical drift (placeholders,
  external refs, the small bag of KNOWN-BAD patterns); the anchors catch
  the deeper "does this read as Odoo / does it cover the spec" judgment
  the lint cannot see. **A failure mode observed when generating
  multiple mocks in sequence: lint passes on a script-templated build,
  the author assumes "script-generated == canonical by construction,"
  declares done, and the anchor-only drift ships (backend-class leakage
  into a non-backend surface, inline-styled callouts, missing guard
  renderings, surface-vocabulary mistakes the catalog doesn't
  document). The script's outputs are only as canonical as the template
  the author wrote — fresh script ≠ exempt from the anchor pass.**
  When building N mocks in a batch, run the anchors on EVERY mock, not
  just the first one. Concrete outcomes:
    - **Zero blockers from both anchors** → proceed to Finish.
    - **Any blocker** → fix it in `index.html`, then re-fire the anchor
      that flagged it to verify the fix. Don't declare done until the
      re-fire returns clean.
    - **A blocker you cannot fix** (e.g. the spec genuinely contradicts
      itself) → record it as a documented limitation in the package's
      README/footer with the anchor's tag (`coverage:…` /
      `fidelity:…`) AND surface it to the user before declaring done.
      Don't silently ship a flagged blocker.
    - **Nits** are not blockers but should be addressed unless the
      cost is disproportionate; record any deliberately-deferred nit
      the same way you'd record an unfixable blocker.
  **Anti-pattern observed in practice:** generator hits a runtime
  rendering issue, patches the SYMPTOM by adding catalog CSS for the
  broken pattern (or by tweaking the markup until it visually settles),
  and never runs the anchor pass. Then the anchor pass would have said
  *"this pattern is the wrong one — switch to the canonical alternative
  from `style_guide.md` § X."* The anchor pass is what catches "you're
  using `.alert` as a guard banner — use the UserError modal" or "the
  spec lists Settings + Pipeline as surfaces, neither is in your mock."
  Skipping it means shipping drift that downstream consumers inherit.
  - **Audit against the FULL step-1 inventory (all eight dimensions) AT THE
    CHOSEN COVERAGE LEVEL — not the cover's step list, not one slice.** When
    invoking `mock-coverage-anchor`, hand it (i) all eight dimensions —
    actors, apps, new models (+ Views Required), menus (esp. Configuration),
    reports, notifications, lifecycle states, guard rules — and (ii) the
    chosen coverage level (Core / Standard / Comprehensive). Ask it to flag,
    for each dimension: any **in-tier** item with no screen/rendering AND no
    recorded exclusion (a coverage hole), and — informational — any item
    excluded as out-of-tier (confirm it's a recorded decision, not a silent
    drop). Failure modes this guards against, all seen in practice: (a)
    auditing the cover narrative is *circular* (a dropped surface is usually
    dropped from the cover too); (b) auditing only actors/apps lets a new
    **config model**, a **Configuration menu**, a **report**, an unrendered
    **lifecycle state**, or an un-gated **guard** inside an already-covered
    app slip through — app coverage implies none of these. The independent
    yardstick is the complete enumerated inventory judged at the chosen tier.
  - **Tell `mock-fidelity-anchor` to re-derive the edition, not trust it.** In
    its prompt, instruct it to independently probe for `enterprise/` in the
    workspace and check the mock's chrome (`<body>` `o-community` class + cover
    kicker) against the § Edition gate: `enterprise/` present ⇒ must be
    Enterprise. Do NOT state the edition as a settled fact in the prompt — a
    stated edition just gets echoed back as accepted (the exact way the
    Community regression slipped past review). The `EDITION` lint rule is the
    hard gate; the anchor is the second, independent set of eyes.

### 5. Finish
- **Default**: print "Done — open `<path>`" and stop.
- **Visual review is opt-in.** If you want a headless screenshot pass
  before declaring done, run the helper command shown in the
  "Optional — visual review" appendix below. Otherwise skip it — the
  Stage-1 lint + anchor pass cover mechanical correctness; pixel
  inspection is for cases where the catalog has changed or a complex
  layout was added.

## Multi-workflow cover topology

A multi-workflow package (≥ 2 `.mock-workflow` wrappers, not counting the
`overview` pseudo-wrapper) has its own cover topology, walkthrough-bar order,
and Next-button relabel rules — **not** the single-workflow pattern with an
extra dropdown. Full pattern lives in
[`reference/catalog_chrome.md`](reference/catalog_chrome.md) § Multi-workflow
chrome: reading flow, walkthrough-bar layout, per-workflow overview screen
shape, main-cover differences (CTA chips, Multiple-workflows callout),
walkthrough.js mechanics table, and the canonical Next-button label set.

The Next-button label set is single-sourced from
[`catalog/walkthrough.js`](reference/catalog/walkthrough.js) `nextButtonLabel()`
— don't restate the labels here.

## Catalog governance (R7)

The catalog is the source of truth for chrome and design tokens. Two
disciplines keep it from drifting:

1. **Use catalog fragments verbatim.** When composing a screen, copy
   the relevant `components/*.html` markup and fill the SLOT comments
   — don't invent your own variant of "what a navbar looks like." If
   the catalog's fragment is wrong, fix the catalog, not the package.
2. **Justify every catalog edit by a real Odoo path.** Edits to
   `catalog/` must cite the Odoo 19 source path they're derived from
   (e.g. `odoo/addons/web/static/src/views/form/...`). The reference
   ensures the catalog stays calibrated to a real version.

When extending the catalog with a new fragment, render the gallery
(`reference/scripts/_render_catalog.py`) and visually verify against
the source. Add the source path + Odoo version to `REFRESH.md`.

## Optional — visual review (headless screenshots)

**Requires `google-chrome` / `chromium` / Edge on PATH.** Without one, skip
this step — the lint + anchor pass cover mechanical correctness; pixel
inspection is for cases where the catalog has changed or a complex layout
was added.

Run this when (a) the catalog has been edited and you need to confirm
existing mocks still render, (b) the lint + anchors are clean but you
suspect a visual gap they can't see (a reversed grid template, an
unstyled class, a marker floating with no anchor), or (c) the user
asks for a screenshot review.

Use `reference/scripts/_render_mock_screens.py` — it drives walkthrough.js
via the `#screen-ID` hash convention so each PNG shows exactly one
`.mock-screen` plus the walkthrough bar (the same composition the
reader sees opening the mock and pressing Next to that step):

```
python3 skills/odoo-mock-design/reference/scripts/_render_mock_screens.py \
    "<mock-dir>" [<screen-id> ...]
```

  - No screen-ids → renders every `.mock-screen` declared in
    `<mock-dir>/index.html` (cover + every workflow step).
  - Output defaults to `/tmp/mock_renders/<mock-name>/<screen-id>.png`;
    override with `--out`.
  - `--width / --height` override the default 1440×900 viewport.

What lint + the fidelity anchor CAN'T catch but the visual review does:

  - **Stale `assets/odoo.css`** — markup uses new catalog classes but the
    mock's `assets/odoo.css` is the old copy, so the classes render
    un-styled. `_lint_mock.py`'s STALE-ASSET rule SHA-256-diffs every
    `assets/<file>` against `reference/catalog/<file>` now, but the
    visual review confirms the rendered fix.
  - **Grid / layout bugs** in catalog CSS — e.g. `.o_portal_doc`'s
    `grid-template-columns: 280px 1fr` paired with DOM order
    `doc_main` first squeezed the document into the narrow slot. Lint
    PASS, anchor clean, looked broken in render only.
  - **Cosmetic positioning** — marker floats, button-row alignment,
    sidebar width pressure, line wrapping. Anchors don't check pixel
    layout.

Eyeball each shot for: breadcrumbs not duplicated, dialog screens with
the walkthrough bar visible above the backdrop, form screens with
workflow buttons in the statusbar only (not also in the control panel),
and the document/sidebar widths look right for the surface.

## Iteration Etiquette

Per principle #8. Skill-specific notes:
- When the user asks to change a screen, edit `index.html` directly — the package
  is the artifact (there's no separate builder dict for mocks).
- **When the user asks for a view type, fragment, widget, or visual element
  that the catalog doesn't have, the FIRST move is to look at the Odoo
  source — NOT to invent it from `odoo.css` tokens.** The catalog is supposed
  to be a faithful mirror of Odoo's actual chrome; building something new
  from tokens drifts the corpus away from real Odoo.

  The lookup loop, in order:
  1. **Verify Odoo source is reachable.** `field_placement.md` Step 0 (the
     source-availability check) tells you whether `odoo/` / `enterprise/`
     are present in the workspace.
  2. **Find the real implementation.** `grep -rn` the SCSS / XML / OWL
     template under `odoo/addons/` and `enterprise/` for the class name,
     widget name, or visible label the user described. Read the file(s).
  3. **Port it into the catalog.** Add (or extend) the relevant
     `catalog/components/*.html` fragment + the matching block in
     `catalog/odoo.css`. Cite the Odoo source path in a comment above the
     new block, per catalog governance (R7). Render
     `reference/scripts/_render_catalog.py` if the new piece adds visual
     surface area.
  4. **Update `REFRESH.md`** with the source path + version, so the next
     Odoo bump knows what to re-verify.
  5. **Use it from the package** — refresh the package's `assets/` copies.

  **Fallback (Odoo source NOT present in the workspace).** Only when the
  source-availability check fails — and only then — build the piece from
  the existing `odoo.css` tokens, keep it recognisably Odoo, and add a
  `REFRESH.md` entry flagging that the fragment was authored
  best-effort without source verification. The next agent run with source
  available should re-derive it from real Odoo.

  This is the same discipline as `field_placement.md` for fields:
  source-of-truth FIRST, best-effort fallback ONLY when source isn't
  there. Inventing a "looks-Odoo" widget from tokens is the leading
  cause of catalog drift across iterations.
- Re-run `_lint_mock.py` after every edit — self-containment rots silently.

## Production-readiness checklist (before declaring done)

Walk [`reference/checklist.md`](reference/checklist.md). It lists the
**judgment checks** that a mechanical lint or anchor can't fully see (coverage
inventory reconciled, marker budget honoured, click-path walkable, etc.) and
documents the mechanical gates as a footnote so you don't manually re-tick
them. Lint + anchors fail loud — they don't need a checkbox.
