# Spreadsheet Report — Troubleshooting

Lookup index of known failure modes — symptom-first, four lines each. Read before generating; consult when a new error appears (grep the literal error string here first). See [`troubleshooting-archive.md`](troubleshooting-archive.md) for fixed/obsolete entries.

**Migration note (2026-06-13):** This file was reformatted from a 121-line mixed-content log to a sectioned 4-line lookup that matches the shared discipline. Two pieces of reference content were extracted into siblings: the design-system rules went to [`design_system.md`](design_system.md), and the conditional-format operator registry went to [`cf_operators.md`](cf_operators.md). Two process rules were promoted into SKILL.md (Stage 3 per-sheet walk and sync-source-first). Old IDs 1–15 do NOT map to new IDs — old plans citing "troubleshooting #N" by number need rewiring against this file's renumbered IDs.

**Write gate (per principle #6):** A new entry only lands if the skills tree is git-cloned AND the user has push access, OR if the skills tree is not git-cloned at all. Otherwise surface the proposed entry to the user without writing. The full check + rationale lives in [`../../_shared/principles.md` § 6](../../_shared/principles.md).

**Update protocol (per principle #6, after the write gate has passed):**
1. Before appending: grep this file for the literal error string. If an entry exists, update its `Last confirmed` date and refine `Cause`/`Fix` if the new occurrence taught something — don't duplicate.
2. New entries take the next free integer in the global ID space (highest active or archived ID + 1). IDs are never reused, even after archive.
3. When the file exceeds 250 lines or 35 active entries, prune (move fixed-for-90+-days entries to archive, retire whole version-specific sections when a major version is no longer supported, promote recurring patterns to principles/role checklists or to sibling reference files).
4. Run `../../_shared/scripts/_lint_troubleshooting.py --skill odoo-spreadsheet-report` after editing — it validates entry shape, flags duplicate IDs, and reports archive candidates.

---

## Browser-side errors (data load / render)

### 1. Browser: "Data version X.Y.Z postdates the current version of o-spreadsheet (version A.B.C)"
Applies: all versions. Status: active. Last confirmed: 2026-06-13.
Cause: JSON `version` field is newer than the o-spreadsheet bundle shipped with the running Odoo. Older Odoo can't read JSON written for a newer runtime.
Fix: Set `version` in the JSON to a value `≤` the runtime. Detect runtime with `grep CURRENT_VERSION odoo/addons/spreadsheet/static/src/o_spreadsheet/o_spreadsheet.js`; or grep the highest version in shipped samples under `enterprise/spreadsheet_dashboard_*`.

### 2. Browser: "Invalid cell description: A5:A200"
Applies: Odoo ≤ 18.5.10. Status: active. Last confirmed: 2026-06-13.
Cause: The compressed range-key cell form `{"A5:A200": {...}}` is a 19.x feature. Older runtimes only accept single-cell keys.
Fix: Expand each cell individually (`A5`, `A6`, `A7`, …) so every key is a single cell coord. Expect JSON size to grow — drop `max_rows` per list to a realistic cap to compensate.

### 3. Browser: "No behavior found for filter type \"relation\" and operator \"undefined\""
Applies: all versions. Status: active. Last confirmed: 2026-06-13.
Cause: A global filter's `defaultValue` does not match its declared type — the runtime expects type-shaped objects with an `operator` key.
Fix: Use the type-correct shape — relation: `{"operator":"in","ids":[]}`; numeric: `{"operator":"=","targetValue":N}`; text: `{"operator":"ilike","strings":[]}`; boolean: `{"operator":"set"}`; date: a string like `"this_year"` is fine. See the operators column in [`cf_operators.md`](cf_operators.md) § Global-filter operators for the full registry.

### 4. Browser: "Cannot find Equal/GreaterThan/equal/gt in this registry!"
Applies: Odoo ≥ 18.5.1. Status: active. Last confirmed: 2026-06-13.
Cause: `CellIsRule.operator` is not a registered key in the runtime's `criterionEvaluatorRegistry`. PascalCase forms (`Equal`, `GreaterThan`) only resolve through legacy `cfConversionMap` migration; short forms (`equal`, `gt`, `lt`) are filter-context operators, not CellIs operators.
Fix: Use the full camelCase form — `isEqual`, `isGreaterThan`, `isLessThanOrEqualTo`, etc. The canonical 14-row registry table lives in [`cf_operators.md`](cf_operators.md) § CellIsRule operators; the `_verify_sheets.py` Stage-1 verifier rejects any operator not in that table.

### 5. Browser: Empty dashboard / nothing loads
Applies: all versions. Status: active. Last confirmed: 2026-06-13.
Cause: Silent JSON shape error — a required key is missing on a sheet, figure, or data source. The runtime fails on first load without surfacing a console error.
Fix: Compare the failing sheet against the canonical samples in `reference/samples/`. Every sheet needs the full set: `id, name, colNumber, rowNumber, rows, cols, merges, cells, styles, formats, borders, conditionalFormats, dataValidationRules, figures, tables, areGridLinesVisible, isVisible, headerGroups, comments`.

### 6. UI: Cells render as `#ERROR`
Applies: all versions. Status: active. Last confirmed: 2026-06-13.
Cause: Most commonly `ODOO.LIST(id, idx, "field")` where `idx` exceeds the available record count for the data source, sometimes compounded by a 19.x-only feature being used at an older runtime.
Fix: Lower the list's `max_rows` to a realistic upper bound for the data. Confirm model + field name still resolve at this Odoo version (rename / removal between versions is common).

### 7. UI: Data sources show ⚠️ "This pivot is not used" / "This list is not used"
Applies: all versions. Status: active. Last confirmed: 2026-06-13.
Cause: A top-level `pivots[id]` or `lists[id]` entry exists but no cell formula references it. Common trap: defining a pivot "for" an `odoo_bar` / `odoo_line` / `odoo_pie` chart — those chart types embed their own data source via `metaData` + `searchParams`, they do NOT read from the defined pivot.
Fix: Either reference the data source from a cell (`=PIVOT.VALUE(id, ...)`, `=ODOO.LIST(id, ...)`, etc.) or remove the entry from `pivots` / `lists` (and update `pivotNextId` / `listNextId` so the next-id counter doesn't drift).

### 8. UI: "Empty data" scorecards display as `0.00` instead of `–`
Applies: all versions. Status: active. Last confirmed: 2026-06-13.
Cause: `SUM` / `SUMPRODUCT` on empty data evaluates to `0`. With `humanize: true` this renders as `0.00`. For "no data yet" cases this looks misleading; for "zero is the right answer" (zero overdue = healthy) it is correct.
Fix: Wrap the formula `=IFERROR(IF(<source_count>=0,"–",<sum_formula>),"–")` only where "no data" semantically differs from "zero." Don't silently hide real zeros.

---

## Shell-side errors (odoo-bin shell import)

### 9. Shell: `KeyError: 'documents.document'`
Applies: all versions. Status: active. Last confirmed: 2026-06-13.
Cause: `documents_spreadsheet` (and its dependency `documents`) is not installed in the target DB.
Fix: Install — `odoo-bin -i documents,documents_spreadsheet --no-http --stop-after-init`. Confirm with the user before running per principle #4.

### 10. Shell: Data source model not found at runtime
Applies: all versions. Status: active. Last confirmed: 2026-06-13.
Cause: The owning module of a referenced model is not installed. Spreadsheet JSON references the model name; if no module owning that name is installed, the lookup fails at import time.
Fix: Identify the owning module from `odoo/addons/<x>/models/...` (or `ir.model.data` lookup), then install it: `-i <module>`. Confirm before running.

---

## Layout symptoms (figure placement / dashboard composition)

### 11. UI: Title bar invisible / scorecards stacked at top of sheet
Applies: all versions. Status: active. Last confirmed: 2026-06-13.
Cause: One or more figures anchored at `row=0`. The title is on row 1 (index 0), so figures at `row=0` overlap it. Multiple figures sharing the same `row` and `col` offset stack on top of each other.
Fix: Anchor first content figures at `row >= 2` (row 1 = title, row 2 = spacer). For a row of N scorecards, anchor each at `col = i * card_width_in_cols`, all sharing the same `row`. For broader composition rules see [`design_system.md`](design_system.md).

### 12. UI: Errors only appear when clicking specific sheet tabs
Applies: all versions. Status: active. Last confirmed: 2026-06-13.
Cause: Conditional formats, chart data ranges, and scorecard refs are evaluated **lazily per sheet** during render, not at JSON parse. A clean Dashboard tab does not mean a clean Aging tab — the runtime crash on bad operators or missing refs only fires when that sheet renders.
Fix: Walk every visible sheet at validation time — see SKILL.md § Stage 3 per-sheet walk for the mandatory procedure. After fixing, also clean up duplicate docs in the DB (`Doc.search([("name","=",NAME),("handler","=","spreadsheet")])` may return multiple from prior imports — user might open an older copy).
