# Spreadsheet Report — Operator Registries

Canonical lookup card for **conditional-format `CellIsRule` operators** and **global-filter `defaultValue` operators**. Both registries are runtime-validated; the wrong name causes the errors in troubleshooting #3 and #4.

The Stage-1 verifier at `<instance>/spreadsheet_reports/_verify_sheets.py` hashes against the tables below — if you add a new operator to either registry, update both this file and the verifier in lockstep.

---

## CellIsRule operators (conditional formats)

For `conditionalFormats[*].rule` of `"type": "CellIsRule"`. The runtime resolves the `operator` value against `criterionEvaluatorRegistry` in the o-spreadsheet source. **Use the full camelCase form** — PascalCase only resolves through legacy migration paths that do NOT run on fresh JSON at `version >= 18.5.1`, and short forms (`equal`, `gt`) are for a different registry entirely.

| Use | Operator |
|-----|----------|
| equal | `isEqual` |
| not equal | `isNotEqual` |
| greater than | `isGreaterThan` |
| greater or equal | `isGreaterOrEqualTo` |
| less than | `isLessThan` |
| less or equal | `isLessOrEqualTo` |
| between | `isBetween` |
| not between | `isNotBetween` |
| begins with text | `beginsWithText` |
| ends with text | `endsWithText` |
| contains text | `containsText` |
| does not contain text | `notContainsText` |
| is empty | `isEmpty` |
| is not empty | `isNotEmpty` |

Example:

```json
"rule": {
  "type": "CellIsRule",
  "operator": "isGreaterThan",
  "values": ["0"],
  "style": {"fillColor": "#F4CCCC", "bold": true, "textColor": "#990000"}
}
```

If you see "Cannot find Equal/GreaterThan in this registry!" at render time, the operator name doesn't match this table. See troubleshooting #4 for the failure mode.

---

## Global-filter `defaultValue` operators

For `globalFilters[*].defaultValue`. The shape depends on the filter type — the runtime expects a type-shaped object with the operators below. Wrong shape produces "No behavior found for filter type X and operator undefined" (troubleshooting #3).

| Filter type | `defaultValue` shape | Operators |
|---|---|---|
| **relation** | `{"operator": <op>, "ids": [int, …]}` | `in`, `not in`, `child_of` |
| **numeric** | `{"operator": <op>, "targetValue": <num>}` | `=`, `!=`, `>`, `<`, `between` |
| **text** | `{"operator": <op>, "strings": [str, …]}` | `ilike`, `not ilike`, `in`, `not in`, `starts with` |
| **boolean** | `{"operator": <op>}` | `set`, `not set` |
| **date** | string default (e.g. `"this_year"`, `"last_30_days"`) | — (operator omitted; predefined string range) |

Common traps:

- **Relation with `[]`** still requires `"operator": "in"` — an empty array does NOT mean "use the default operator." The operator key is mandatory.
- **Numeric `"="` not `==`** — JavaScript convention does not apply here.
- **Text `"ilike"` not `"like"`** — the case-insensitive form is the default operator.

---

## Why this lives outside troubleshooting

Both registries are *reference cards*, not symptom-fix entries. The 4-line troubleshooting format would amputate the tables. Keeping them here lets the registries grow as the runtime adds new operators, while troubleshooting #3 and #4 stay symptom-focused and cite this file.

When the o-spreadsheet runtime adds a new operator (rare but happens on minor-version bumps), update:

1. This file's table.
2. `<instance>/spreadsheet_reports/_verify_sheets.py` so Stage 1 will reject the absent operator.
3. The canonical samples under `reference/samples/` if the new operator demonstrates a previously-impossible pattern.
