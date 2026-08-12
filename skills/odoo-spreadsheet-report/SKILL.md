---
name: odoo-spreadsheet-report
description: Plan and generate an Odoo Spreadsheet (.osheet.json) report on an Odoo.sh development branch by asking structured questions (business need/brief/models/filter/output) then role-based questions; produce an importable spreadsheet JSON, validate it by importing into the branch DB via odoo-bin shell, and fix errors until it loads cleanly.
when_to_use: Use this skill when the user wants a new Odoo Spreadsheet KPI/dashboard report generated on the current Odoo.sh branch and validated by import into its DB.
allowed-tools: Read, Edit, Write, Bash, Grep, Glob
---

# Spreadsheet Report

Turn a reporting objective into a working Odoo Spreadsheet report (`.osheet.json`) that imports cleanly into the branch's Odoo DB.

## Scope — NEVER custom development

This skill produces a **reporting artifact only** — a spreadsheet document, a dashboard, docs. It **never** adds Python code, models, fields, views, or automations to any addon (custom or standard). If the ask cannot be satisfied by (a) formulas over standard model fields, (b) existing custom-addon fields consumed *as installed*, or (c) o-spreadsheet's built-in operators / pivots / lists / charts, then this skill is the wrong tool — halt and tell the user the ask is out of scope. Custom addons already deployed on this branch are read-only dependencies here; their code is not touched.

## Environment — Odoo.sh, always (principle #13)

**No architecture detection. No Q0.** This skill runs inside an Odoo.sh
development-branch container and nowhere else. There is no `instances/` tree, no
version folder, no local venv, and no `odoo-bin shell` you may run against an
arbitrary DB.

What that fixes:

- **Everything this skill writes lands under `spreadsheet_reports/` at the
  Project Repo root** (`/home/odoo/src/user`). That folder is a Document Skill
  output root — the Guard Hook exempts it from the Python and XML floors so the
  builder can be a real builder. Writing anywhere else is refused.
- **The branch is the one you are on.** `git branch --show-current`. Never ask
  "which branch?", never operate on another branch's DB.
- **The Odoo version is `$ODOO_VERSION`.** Read it; never infer it from a folder
  name.
- **The DB is the one injected for this branch.** Never name it, create it, or
  pass `-d` / `--database` — the Guard Hook denies all three.

## When To Use

Use this skill when the user wants a new Odoo Spreadsheet KPI/dashboard report generated on the current branch and validated by import into its DB.

## Entry: Plan mode for the first iteration

Per shared principle #11, this skill always enters plan mode on invocation for its
first iteration. Do all interview questions, the o-spreadsheet source sync check,
model/field verification, version detection, and Pre-Flight module resolution
inside plan mode, building up the plan at `<repo_root>/plans/<slug>.md` (the
repo root's `plans/` directory, NOT `.claude/plans/` — the Write tool
auto-creates the dir if missing; the harness's auto-generated
`.claude/plans/<random>.md` placeholder should be deleted once the deterministic
file is written, so two copies don't drift). Call `ExitPlanMode` once the
design is complete.

The module-install confirmation under "Pre-Flight: Required Modules / Confirm with
the user before installing" stays as a separate execution-time gate — installs
mutate the DB and run after plan approval, not during planning.

Subsequent fix-iterations (verifier failures, re-imports, browser-error fixes)
happen outside plan mode.

**Do not open with "what do you want to do?"** — even when invoked while plan
mode is already active. The skill's first message to the user is always Q1 of
the Fixed Questions list (or the first that survives principle #12), never a
free-form scope prompt. Plan mode's default opener is an anti-pattern here; it
collapses the opening questions into a single business-need answer and skips the
model-source context that the Pre-Flight and three-stage validation depend on. See principle #11 ("Plan mode normalizes execution state;
it does not reshape the interview.")

## Output Contract

Produce:

- **Interactive Planning Questions**: ask questions **one by one** (never as a batch). After each answer, update assumptions and ask the next single best question.
- **Python builder script** at `spreadsheet_reports/_build_<report_slug>.py` that emits the JSON. The builder is the source of truth — JSON is regenerated from it. Hand-editing the JSON is not the workflow.
- **Generated Report**: a single `.osheet.json` written to `spreadsheet_reports/<report_slug>.osheet.json` by running the builder.
- **Validation script** at `spreadsheet_reports/_validate_import.py` that imports via `odoo-bin shell` and verifies round-trip.
- **Validated Import**: the JSON is imported into the branch's DB. Errors are fixed iteratively until the report **loads cleanly in the browser** (server-side round-trip is necessary but not sufficient — always reload the page).
- **Production-ready visuals**: layout, color palette, conditional formatting, and number formats follow the Design System section. A "functional but ugly" report does NOT satisfy the contract.
- **Short docs**: `spreadsheet_reports/doc/<report_slug>.md` covering what the report shows, refresh, and re-import instructions.

All paths are relative to the Project Repo root — the only writable tree.

Do not output a generation prompt. Start producing the JSON once minimally unblocked.

## Interaction Rules

Follows the shared principles in [`skills/_shared/principles.md`](../_shared/principles.md): one question at a time (#10), builder-driven generation (#1), three-stage validation (#2), confirm-before-destructive (#4), troubleshooting-log discipline (#6), no orphan references (#7), iteration etiquette (#8), read-then-edit (#9). Read that file first; the rest of this skill is the spreadsheet-specific overlay.

## Fixed Questions (Ask In This Order)

Per shared principle #10, ask one at a time, reflect, ask the next.

**Apply principle #12 (necessity filter) to every question below.** Before asking,
check: is the answer inferable from the invocation, an existing builder/report, or
a read-only pre-flight (`$ODOO_VERSION`, o-spreadsheet bundle version, installed
modules, `ir.model.data`)? Would the answer materially change the report shape?
If either gate fails, skip the question and record the inference under an
**Assumptions** heading in the plan file. User overrides at `ExitPlanMode`.

Typical skips for this skill:
- **Q1 (instance)** and **Q2 (Odoo version)** are never asked at all — see below.
- **Q6 (data-source models)** partially skipped when the invocation already names
  them ("AR aging by partner" → `account.move`, `account.move.line`, `res.partner`
  are obvious); still confirm the list in the plan.
- **Q8 (validation DB)** never asked — the branch's injected DB is the only target.

Q3 (business need), Q4 (delivery shape), Q5 (report brief), and Q7 (primary filter
/ scope) are almost never inferable in full — ask unless the invocation already
contains them.

1. ~~**Which instance is this for?**~~ — **never asked.** There is one branch and
   one DB. Detect the branch with `git branch --show-current` and record it under
   the plan's `Assumptions`; the user overrides at `ExitPlanMode`. Every custom
   addon already deployed on this branch counts as an additional source of
   models/fields, read-only.

2. ~~**Which Odoo version is this for?**~~ — **never asked.** Read `$ODOO_VERSION`
   and cross-check it against the o-spreadsheet bundle's `@version` JSDoc. Surface
   a mismatch; do not ask the user to arbitrate a fact both sources state.

3. **What is the business need?** (problem + who consumes the report + what decision it informs)

4. **What's the delivery shape?**
   - `spreadsheet` — editable Documents-backed spreadsheet, live-linked to Odoo. Users can slice, re-formula, share edits.
   - `dashboard` — read-only, always-refreshed, appears in the Dashboards app. Native Print-to-PDF button for stakeholders who want a paper copy.
   - `both` — spreadsheet as the source-of-truth + a dashboard published from it for consumption / print.
   - If the ask fits Odoo's built-in **Analysis view** (Sales / Purchase / Timesheet / etc. Analysis + a saved favorite), consider that path first — halt this skill and point the user there; a spreadsheet is heavier than needed for a stock pivot/graph slice.
   - The answer drives Stage 2's target (`documents.document` vs `spreadsheet.dashboard`) and Pre-Flight Layer A (`documents_spreadsheet` vs `spreadsheet_dashboard`).

5. **What is the report brief?** (KPIs, charts, layout sections — high level; sample structures live under `reference/samples/STRUCTURE.md`)

6. **Which Odoo models are the data sources?** (e.g. `project.task`, `account.analytic.line`)
   - Verify each model exists by searching first in `/home/odoo/src/odoo/`, then `/home/odoo/src/enterprise/`, then this branch's own addons. All three are read-only.
   - If a needed field doesn't exist, surface this immediately — do NOT silently invent it, and do NOT propose adding it here (see § Scope).

7. **What is the primary filter / scope?** (global filters: date range, project, employee, manager — type each as `date | relation | text | selection | numeric | boolean`)

8. **Which DB should the report be imported into for validation?**
   - Never asked — the branch's injected DB is the only target.

After these, proceed with role-based questions.

## Role-Based Questions (Ask Only What Matters)

Keep total questions low. Prefer questions that change KPI semantics, data shape, performance, or visibility.

Apply principle #12 here too: skip individual role questions whose answer is
inferable (e.g. Performance is moot for a <1k-row report; Security defaults are
fine when the report respects standard record rules and adds no extra `domain`).
Record the default in the plan's Assumptions section rather than asking.

### Data Analyst (Metric Semantics)
Confirm exact formulas, edge cases (empty data, division by zero, missing dates), thresholds for "good vs bad."

### BI / Visualization Designer (Layout)
Confirm chart type per KPI (scorecard / bar / line / pivot / gauge), grouping, sheet structure (one dashboard sheet vs split). Color semantics and the navy/red/amber/green palette are pre-set in the Design System — only ask if the user wants to override. Do confirm whether each KPI is a "negative marker" (issues to fix, painted red) or "performance metric" (informational, painted green/neutral).

### Odoo Solution Architect (Model & Field Validity)
Confirm which standard Odoo models/views to read from. If a needed value is not directly on a model, decide between (a) a derived spreadsheet formula, or (b) a different model that already carries the value. **No custom addon work — see § Scope.** If neither (a) nor (b) fits, halt: the ask is out of scope for this skill.

### Security Expert (Access)
Confirm record rules / ACLs the report should respect (e.g. PMs see only their projects). Spreadsheet data sources respect each user's record rules — but configured `domain` filters in lists/pivots must not over-expose data.

### Performance Engineer (Scale)
Confirm expected dataset size. Prefer `ODOO.PIVOT` / `PIVOT.VALUE` over `ODOO.LIST` for aggregations. Pre-allocate `rowNumber` on list sheets correctly. Tighten domains. Consider hiding helper sheets via `isVisible: false`. Flag any list expected to exceed a few thousand rows.

### QA (Validation)
Confirm acceptance: import succeeds, every formula evaluates without `#ERROR`, every chart renders, every global filter narrows data as expected.

### Documentation Expert
Confirm what should appear in `doc/<report_slug>.md`: business definition of each KPI, refresh cadence, and how to re-import.

## Reference Material (Read Before Generating, in order of authority)

Always consult before producing JSON. Listed in **descending authority** — when sources conflict, the higher entry wins:

1. **`reference/o-spreadsheet-source/`** — local clone of [github.com/odoo/o-spreadsheet](https://github.com/odoo/o-spreadsheet) checked out at the runtime's stable branch (e.g. `19.0`). Synced via `reference/scripts/_sync_o_spreadsheet_source.py`. **This is the authoritative source for code-level questions** about formulas, registries, plugins, migrations, chart shapes, and conditional-format operators. Always grep here first — the readable TypeScript with comments and JSDoc is far more reliable than the minified bundle. Gitignored.
2. `odoo/addons/spreadsheet/static/src/o_spreadsheet/o_spreadsheet.js` — the minified runtime bundle shipped with the running Odoo. Useful as a last-resort check that something exists in this exact build (bundle ≠ source if Odoo is mid-upgrade or pinned to a sub-version), but minification means field names are mangled and comments stripped. Treat as a fallback, not a primary reference.
3. [`skills/_shared/principles.md`](../_shared/principles.md) — cross-cutting discipline that applies to this skill. Read first.
4. `reference/spreadsheet-docs/00-index.md` (and the 8 cached page files) — Odoo 19 Spreadsheet end-user documentation. Conceptual / how-to material; **not** authoritative for code shapes. Hybrid policy: re-fetch a page if the cached copy is older than 60 days, or if you encounter an unfamiliar formula/feature.
5. `reference/samples/STRUCTURE.md` plus the two `.osheet.json` files in the same folder — concrete shape examples (top-level keys, list/pivot/chart/figure shapes, color semantics).
6. [`reference/design_system.md`](reference/design_system.md) — canonical layout, sizing, palette, number formats, and styling rules for visible sheets. The SKILL.md Design System section now just hosts the production-readiness checklist; the *rules* live here.
7. [`reference/cf_operators.md`](reference/cf_operators.md) — canonical `criterionEvaluatorRegistry` lookup card for `CellIsRule` operators plus the global-filter `defaultValue` shape registry. The Stage-1 verifier hashes against this file.
8. [`reference/troubleshooting.md`](reference/troubleshooting.md) — known failure modes (4-line entries, sectioned by failure surface). Read before generating; append to it after every new issue per shared principle #6. Linter: `../_shared/scripts/_lint_troubleshooting.py --skill odoo-spreadsheet-report`.

## Pre-Flight: Sync the o-spreadsheet source

Before grepping for any o-spreadsheet shape (operators, registries, formula signatures, chart configs), run:

```bash
python3 skills/odoo-spreadsheet-report/reference/scripts/_sync_o_spreadsheet_source.py
```

The script:
- Reads `@version <semver>` from the bundle's JSDoc header (e.g. `19.0.32`).
- Maps it to the stable branch `<major>.0` (e.g. `19.0`).
- Clones (or fetches updates for) `github.com/odoo/o-spreadsheet` into `reference/o-spreadsheet-source/` (partial clone, fast for branch switching).
- Checks out the matching stable branch.

It's idempotent — re-running is a fast fetch + checkout. If the network is unavailable or the branch can't be resolved, the script exits non-zero and the agent falls through to the bundle (with a clear note in `reference/troubleshooting.md` describing what to do).

## Generation Rules (Functional)

When you begin generating the JSON:

- **Use real models/fields only.** Before emitting JSON, run `python3 skills/_shared/scripts/_check_odoo_source.py --models <comma-list of every metaData.resModel + every fieldMatching.chain root model>` once. `exists=false` halts (ask the user); `edition=enterprise` on a community-only instance is a hard rejection. (The Stage 2 shell import catches missing-field errors as a backstop — this gate catches missing *models* and edition drift before the file is even written.)
- **For o-spreadsheet shapes, grep the source first.** Operator names, registry keys, formula signatures, chart `data` shapes, conditional-format rules, migrations — all live in `reference/o-spreadsheet-source/src/`. Reading the readable TypeScript saves you from the minified-bundle traps that bit this skill earlier (see [`reference/cf_operators.md`](reference/cf_operators.md) for the canonical `criterionEvaluatorRegistry` lookup, and [`reference/troubleshooting.md`](reference/troubleshooting.md) #4 + #12 for the symptoms). Fall back to the bundle only when the source is unavailable.
- **Compressed formula expansion.** The compact `{"N":"=|+1","S":["="]}` range-key cell form is a 19.x feature. For older runtimes (e.g. 18.5.x) expand each cell individually. Detect runtime version FIRST (see Pre-Flight) and pick the right form. See [`reference/troubleshooting.md`](reference/troubleshooting.md) #2.
- **Wire global filters everywhere.** Each list, pivot, and Odoo-live chart must include `fieldMatching` entries for every global filter, with the correct `chain` and `type`. If a filter doesn't apply to a data source, add an empty entry `{}` for that filter id rather than omitting it.
- **Filter `defaultValue` shape.** Relation: `{"operator":"in","ids":[]}`. Numeric: `{"operator":"=","targetValue":<n>}`. Text: `{"operator":"ilike","strings":[]}`. Boolean: `{"operator":"set"}`. Date: string like `"this_year"`. The full operator registry per filter type lives in [`reference/cf_operators.md`](reference/cf_operators.md) § Global-filter operators; see [`reference/troubleshooting.md`](reference/troubleshooting.md) #3 for the symptom when the shape is wrong.
- **No orphan data sources.** Every entry in top-level `lists` and `pivots` MUST be referenced from at least one cell formula (`=ODOO.LIST(id, ...)`, `=ODOO.LIST.HEADER(id, ...)`, `=PIVOT(id, ...)`, `=PIVOT.VALUE(id, ...)`) or removed. `odoo_bar` / `odoo_line` / `odoo_pie` charts embed their OWN data source from `metaData` + `searchParams` and do **not** consume a top-level pivot — defining a pivot "for the chart" leaves a dead data source that Odoo flags with a warning icon. Either reference it from a `=PIVOT.VALUE(...)` cell or drop it.
- **Hide helper sheets.** Calc/master-data sheets get `"isVisible": false`. The user should see only presentation sheets by default.
- **Pre-allocate rows on list sheets.** `rowNumber` and per-cell formula expansion must comfortably exceed expected record count. Lists do **not** auto-expand. Pick a realistic upper bound (e.g. invoices: 500–2000; projects: 200; cash accounts: 100) and document the cap.
- **One source of truth for filters.** Don't duplicate a global filter's logic in a data source's own `domain` — the global filter is `AND`-ed in at runtime.
- **Builder-driven generation.** Write a Python builder script that produces the JSON; never hand-edit the JSON for non-trivial structure. Builders make iteration safe (style numbers consistent, repeated patterns DRY, layout coordinates calculable). Per shared principle #1, this skill always uses a builder — the JSON shape is regenerated on every fix iteration, so the builder always pays for itself.

## Design System (Visual Production-Readiness)

A report that loads but looks chaotic is not done. Every visible sheet must follow the canonical layout, sizing, palette, and styling rules in [`reference/design_system.md`](reference/design_system.md), and every conditional format must use a registered operator from [`reference/cf_operators.md`](reference/cf_operators.md). Both files are authoritative; SKILL.md does not duplicate their content.

The production-readiness checklist below is *verification*, not reference — run it after generation to confirm the design-system rules are honoured.

### Production checklist (run before declaring done)
- [ ] Title bar visible on every visible sheet, navy + white, height 50.
- [ ] No figure anchored at `row=0` (would overlap title).
- [ ] All visible sheets have `areGridLinesVisible: false`.
- [ ] Helper / data sheets have `isVisible: false`.
- [ ] **Sheet width fits 1320 px** (canonical 12 × 110 col grid). No horizontal scroll on a 14" laptop.
- [ ] **Same-tier widgets have identical dimensions** (all scorecards in a row, all charts in a row).
- [ ] **All figure widths are integer multiples of 110 px** (220, 330, 440, 660, 1320). No 430 px scorecards.
- [ ] **Spacer rows are 10 px (under title) or 16 px (between sections), nothing larger.**
- [ ] **`rowNumber` matches the last row of real content + a few**, not 50% empty padding.
- [ ] No floating "KPIs" / "Trend" labels next to figures (title is enough).
- [ ] Title sizes taper: sheet 22 → section 16 → chart 14 → scorecard 12 → descriptor 10.
- [ ] Every amount / count / percentage cell has a number format.
- [ ] Every KPI scorecard's `keyValue` resolves to a real cell reference (no `=NA()` / `#REF!`).
- [ ] Every "status" column has conditional formatting covering all possible values.
- [ ] No top-level `pivots`/`lists` entry without a cell reference (or it's been removed).
- [ ] Browser reload shows zero `⚠️` warning icons in the Data menu.
- [ ] Browser reload shows zero `#ERROR` cells.
- [ ] **Every visible sheet tab clicked through in the browser** — no `UncaughtPromiseError` toasts.
- [ ] **Static verifier (Stage 1) passes with zero errors** before invoking the shell-side import.
- [ ] Each chart has axis titles set.
- [ ] Two-bar dashboards use side-by-side layout (anchors col=0 and col=6, not stacked).

## Pre-Flight: Required Modules

Before generating or importing, ensure the target DB has every module needed to (a) host the spreadsheet and (b) back every data source the report references. **Both** layers must be installed — installing only the spreadsheet modules leaves data-source models missing at runtime.

### Layer A — Spreadsheet hosting (always)
- `spreadsheet`
- `documents`
- `documents_spreadsheet` — provides `documents.document` with `handler='spreadsheet'` and the full editable Spreadsheet UX.

Without `documents_spreadsheet` the report can only be registered as a read-only `spreadsheet.dashboard`.

### Layer B — Data-source modules (per report)
For each model referenced in `lists`, `pivots`, or chart `metaData.resModel`, resolve the **owning module** by checking `ir.model.data` (the `module` field on the `ir.model` external ID). Examples:
- `account.move`, `account.account`, `account.payment`, `account.bank.statement.line`, `account.analytic.line`, `res.partner` → `account` (and `analytic` for analytic lines, usually pulled in transitively)
- `project.project`, `project.task`, `project.milestone` → `project`
- Timesheets analytic lines with timesheet semantics → `hr_timesheet`
- `sale.order`, `sale.order.line` → `sale_management`
- `purchase.order` → `purchase`
- `hr.employee` → `hr`
- `stock.move`, `stock.picking` → `stock`
- `crm.lead` → `crm`

When unsure, run the resolver below.

### Detection script

```python
# Run via: odoo-bin shell --no-http --stop-after-init < this.py
# (No -c, no -d: Odoo.sh injects the config and the DB. Passing -d is denied.)
HOSTING = ["spreadsheet", "documents", "documents_spreadsheet"]
MODELS  = ["account.move", "project.project", "account.analytic.line"]  # extend per report

owners = set(HOSTING)
for m in MODELS:
    try:
        model_record = env["ir.model"]._get(m)
        mods = env["ir.model.data"].search([("model","=","ir.model"),("res_id","=",model_record.id)]).mapped("module")
        owner = next((x for x in mods if x != "base"), mods[0] if mods else None)
        if owner: owners.add(owner)
        else: print(f"  {m}: NO OWNER FOUND")
    except KeyError:
        print(f"  {m}: MODEL MISSING (owning module not installed yet)")

missing = env["ir.module.module"].search([("name","in",list(owners)),("state","!=","installed")]).mapped("name")
print("MISSING:", ",".join(sorted(missing)) if missing else "none")
print("ALL_NEEDED:", ",".join(sorted(owners)))
```

### Install missing modules in one shot

```
odoo-bin -i <comma,separated,missing> --no-http --stop-after-init
```

This prompts for confirmation (it mutates the branch DB) — expected, per principle #4.

### Confirm with the user before installing
Module installs add data, ACLs, menus, and may pull in transitive deps. Show the user the exact list (`Layer A + Layer B`) and ask before running `-i`. Honor overrides (e.g. user may decline `documents_spreadsheet` and accept dashboard-only target).

### Re-run detection after install
The first install may pull in transitive modules that themselves register new data-source models the user wants. After installing, re-run the detection script to confirm `MISSING: none` before proceeding to generate the JSON.

## Validation (three-stage)

Server-side import succeeding does NOT mean the report renders. Conditional formats, scorecard refs, and chart data ranges are checked only at browser render time — and the registry-lookup errors there are silent until the user reloads. Catch them earlier with this three-stage flow.

### Stage 1 — Static JSON verifier (run before importing)
Run a small Python verifier that walks the generated JSON and surfaces structural problems without needing Odoo:

- **CF operators**: every `conditionalFormats[].rule.operator` must be in the runtime registry (see the table above). Reject `equal`, `gt`, `Equal`, `GreaterThan`, etc.
- **Filter `defaultValue` shapes**: per-type operator validation (relation `in/not in/child_of`, numeric `=/!=/>/</between`, etc.).
- **Cross-sheet refs**: every scorecard `keyValue` referencing `'<Sheet>'!A1` must point to a sheet that exists. Same for native bar/line `dataSets[].dataRange` and `labelRange`.
- **Orphan data sources**: every `lists[id]` and `pivots[id]` must be referenced by at least one cell formula (`=ODOO.LIST(id,...)`, `=PIVOT(.VALUE)?(id,...)`).
- **Visible sheet sanity**: title in A1 (or merged A1:_:1), `areGridLinesVisible: false`.
- **Bracket balance** on every formula cell.

A reference verifier ships at `spreadsheet_reports/_verify_sheets.py` (extend per report). Exit code 1 on any error. Run before invoking the shell-side validator.

### Stage 2 — Server-side import (odoo-bin shell)

Once Stage 1 passes:

1. `odoo-bin` is on `PATH`; the config and DB are injected by the platform. Do not locate, author, or pass either.
2. Open a shell session against the branch DB:
   ```
   odoo-bin shell --no-http --stop-after-init
   ```
   This prompts for confirmation (the ORM shell can mutate) — expected.
3. Load the `.osheet.json`. **Prefer** `documents.document` (full editable UX); fall back to `spreadsheet.dashboard` only when `documents_spreadsheet` is not installed and the user declined to install it:
   - **`documents.document`** — `create({"name": ..., "handler": "spreadsheet", "mimetype": "application/o-spreadsheet", "folder_id": <id>, "spreadsheet_data": <raw_json>})`
   - **`spreadsheet.dashboard`** — `create({"name": ..., "dashboard_group_id": <id>, "spreadsheet_data": <raw_json>})`
   - Commit, then re-read and verify the data field round-trips without exception.
4. If the import fails, capture the traceback. Common failure modes and fixes:
   - **`KeyError: 'documents.document'`** — `documents_spreadsheet` not installed → install it (see Pre-Flight) or fall back to dashboard target.
   - **Model not found at runtime** — referenced model's module not installed → install or fix `model`.
   - **Field not found / chain broken** — fix `field_name` or `chain` in `fieldMatching`.
   - **Domain syntax error** — `domain` in lists/pivots must be valid Python list-of-tuples.
   - **Browser load error: "Data version X postdates current version Y"** — match `version` in the JSON to the o-spreadsheet runtime version (grep `CURRENT_VERSION` in `odoo/addons/spreadsheet/static/src/o_spreadsheet/o_spreadsheet.js`, or pick the highest version found in shipped sample files under `enterprise/spreadsheet_dashboard_*/data/`).
   - **Browser load error: `Invalid cell description: A5:A200`** — the compressed range-key form `{"A3:A1480": {"N":"=|+1","S":["="]}}` is a 19.x feature; for older runtimes, expand each cell individually (`A3`, `A4`, `A5`, …).
   - **Browser load error: `No behavior found for filter type "relation" and operator "undefined"`** — `defaultValue` on relation/numeric filters must be an object with `operator`. Use `{"operator": "in", "ids": []}` for relation, `{"operator": "=", "targetValue": <n>}` for numeric. Date filters can keep string defaults like `"this_year"`.
   - **`#ERROR` cells in UI** — `ODOO.LIST` row index past last record (rendered as `#ERROR` in some versions; otherwise blank). Reduce `max_rows` if list size is small, or accept it.
5. Cleanup duplicates: `documents.document.search([("name","=",NAME),("handler","=","spreadsheet")])` may return multiple rows from earlier imports. Keep only the most recent and `unlink()` the rest — otherwise the user opens an old copy and sees stale errors.
6. Iterate until clean.

### Stage 3 — Browser-side sheet-by-sheet verification

Server import success ≠ browser render success. Always:

1. Reload the document in the browser (hard refresh — Cmd+Shift+R on macOS — to bust any cached spreadsheet bundles).
2. Click into **every visible sheet tab in turn**. The o-spreadsheet errors that don't surface server-side (registry lookups, missing sheet refs, bad chart data ranges) fire **only when that specific sheet renders**. A clean Dashboard does not mean a clean Aging or Project Cash sheet.
3. For each sheet, check:
   - No `UncaughtPromiseError` toast appears.
   - All scorecards show real values (not `#REF!`, not blank, not `#ERROR`).
   - All charts render with bars / lines.
   - Conditional formats colour cells as expected (try editing a cell to flip its status — colour should update).
   - The `Data` menu shows all defined lists/pivots without ⚠️ icons.
4. Open Filters panel and confirm each global filter loads without throwing.
5. If an error appears: capture the full message, identify the sheet, then either fix the JSON & re-run all three stages OR add the new failure mode to `reference/troubleshooting.md` and the static verifier (so it's caught at Stage 1 next time).

### Failure-mode quick reference

If the import fails, capture the traceback. Common failure modes and fixes:

## Documentation (Always Last)

After import succeeds, formulas evaluate, and the **production checklist** passes:

- Write `spreadsheet_reports/doc/<report_slug>.md` with:
  - One-paragraph business purpose (who consumes it, what decision it informs)
  - Sheet inventory (visible + hidden) with one-line role each
  - KPI table: name · plain-English formula · source model · healthy threshold · color semantics
  - Chart inventory: type · what it shows · what clicking it opens
  - Global filters table: label · type · default · which data sources it's bound to
  - How to re-import (exact commands: builder, validator, with venv path)
  - How to regenerate (edit builder, rerun)
  - Known limitations (row caps, hidden sheets, sharing constraints, data source modules required)

Keep it under one screen of detail per section — not a manual, a quick reference for the next person.

## Iteration Etiquette

When the user pushes back on visuals:
- Don't apologise and revert to safe defaults — diagnose the specific complaint, then fix.
- A "looks all over the place" comment usually maps to one of: figures overlapping the title (anchored at row 0), inconsistent column anchors, mixed scorecard widths, missing spacer rows, wrong number formats, or unset gridlines on a presentation sheet. Check the Design System checklist before guessing.
- After fixing, regenerate, re-validate, and tell the user what visually changed — they need a reason to reload.
- **Match existing style** (principle #8). When editing an existing report's builder, mirror its naming and layout idioms; don't re-style on the side.

---

