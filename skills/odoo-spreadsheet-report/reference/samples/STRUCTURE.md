# Reference Sample Structure

Two real `.osheet.json` files were provided as canonical examples:

1. **`[DU-MMC] Project KPI Dashboard.osheet.json`** — multi-sheet KPI dashboard:
   - `KPI Dashboard` (presentation) — scorecards + odoo_bar charts arranged in a grid with merged header cells, banded color blocks (negative markers in red `#F4CCCC`, performance in green `#D9EAD3`).
   - `KPI Markers` (calc layer) — formulas like `SUMPRODUCT(...)` against the data sheets, returning the scorecard values.
   - `Budget Tracker`, `All Tasks`, `All Timesheets`, `All Milestones`, `All Projects`, `All Project Updates` — pure `ODOO.LIST(list_id, index, "field")` data sheets, one per Odoo model.
   - `Pending Changes and Suggestions`, `Feedback Sheet` — manual notes.

2. **`Team Performance Tracker.osheet.json`** — team utilization:
   - `Dashboard`, `Report`, `Breakdown` (presentation/aggregation).
   - `Hours Calculation`, `Reduced Hours Days`, `Holiday Adjustments` (helpers, hidden via `isVisible: false`).
   - `Team Data`, `Team Joining Dates`, `Billable Rate per Type` (config/master data).
   - `Timeoff` — `ODOO.LIST` of `account.analytic.line` filtered to time-off project.
   - Uses `PIVOT.VALUE(pivot_id, "unit_amount:sum", "employee_id", 'Team Data'!A2)` heavily.

## Top-level JSON shape

```json
{
  "version": "19.1.2",
  "sheets": [ { "id": "...", "name": "...", "colNumber": 26, "rowNumber": 100,
                "rows": {}, "cols": {"0": {"size": 100}},
                "merges": ["A2:F2"],
                "cells": {"A1": "..."},
                "styles": {"A1:T1": 1},
                "formats": {"G2": 1},
                "borders": {"A1:F1": 1},
                "conditionalFormats": [],
                "dataValidationRules": [],
                "figures": [{"id":"...","tag":"chart","data":{"type":"scorecard", ...}}],
                "tables": [{"range":"A1:T1","type":"static","config":{...}}],
                "areGridLinesVisible": true,
                "isVisible": true,
                "headerGroups": {"ROW": [], "COL": []},
                "comments": {} } ],
  "styles": { "1": {"fillColor": "#D2D9DB", "fontSize": 24, "align": "center"} },
  "formats": { "1": "0.00" },
  "borders": { "1": {"left": {"color":"#000000","style":"thin"}} },
  "settings": {"locale": {"code":"en_US","weekStart":7, ...}},
  "pivots": { "1": {"type":"ODOO","model":"...","domain":"...","measures":[...],"rows":[...],"columns":[...]} },
  "pivotNextId": 20,
  "lists": { "1": {"id":"1","name":"...","model":"...","columns":[...],"domain":[...],"context":{...},"orderBy":[...],"fieldMatching":{...}} },
  "listNextId": 11,
  "globalFilters": [{"id":"...","label":"Date","type":"date","defaultValue":"this_month"}],
  "revisionId": "<uuid>",
  "uniqueFigureIds": true,
  "customTableStyles": {},
  "odooLinkReferences": {}
}
```

## Key patterns to imitate

### 1. Cell formula expansion
`ODOO.LIST` rows use a compact range form:
- `A2`: `=ODOO.LIST(2,1,"project_id")` (first row, full formula)
- `A3:A1480`: `{"N":"=|+1","S":["="]}` — the `+1` means index increments per row

This is how the spreadsheet stores expansion of a single formula across many rows. Generated reports MUST use this compressed form for big ranges, not 1480 explicit copies.

### 2. List + Data Source
For each Odoo data source (list ID `n`), populate top-level `lists[n]` AND a sheet whose cells are `ODOO.LIST(n, ...)`.

Required keys in `lists[n]`:
- `id`, `name`, `model`, `domain`, `context`, `columns`, `orderBy`, `actionXmlId` (optional), `fieldMatching` (one entry per global filter)

### 3. Pivot data sources
Top-level `pivots[<id>]` with: `type:"ODOO"`, `model`, `domain`, `measures`, `rows`, `columns`, `context`, `name`, `formulaId`, `fieldMatching`.
Reference in cells via `=PIVOT.VALUE(<id>, ...)`.

### 4. Charts (figures)
Each chart on a sheet is a `figure` with `tag:"chart"`, `col`, `row`, `offset`, `width`, `height`, and `data` containing chart-type-specific config. For Odoo-live charts, include `metaData`, `searchParams`, `actionXmlId`, and `fieldMatching` for global filters.

### 5. Color semantics (from samples)
- Negative markers (issues to act on): red background `#F4CCCC`
- Performance metrics (info): green background `#D9EAD3`
- Headers: `#D2D9DB` dark gray, white text
- `baselineColorUp: #43C5B1`, `baselineColorDown: #EA6175` on scorecards

### 6. Global filters
Defaults: `"this_month"` for date; relation filters can pre-fill `domainOfAllowedValues` and `displayNames`.
Each list/pivot/chart references the filter via `fieldMatching: {<filter_id>: {"chain":"project_id","type":"many2one"}}`.

### 7. Hidden helper sheets
Setting `"isVisible": false` hides calc/master-data sheets from end users without removing them.

## Drop the original files here
The two source `.osheet.json` files are the authoritative reference. If absent, copy them into this folder so the agent can grep them for live shape examples.
