# Dynamic Pivot Tables

Source: https://www.odoo.com/documentation/19.0/applications/productivity/spreadsheet/work_with_data/dynamic_pivot_tables.html

Dynamic pivots use a single array formula that grows with data. Static pivots use one function per cell and don't auto-expand.

## Creation
1. Pivot properties → gear icon → Duplicate (new data source, same styling)
2. Data → Re-insert dynamic pivot → choose existing pivot (shares data source)

## PIVOT Formula

```
=PIVOT(pivot_id, [row_count], [include_total], [include_column_titles], [column_count])
```

- `pivot_id`: sequential
- `row_count` / `column_count`: output dims
- `include_total`, `include_column_titles`: `0` to exclude

## PIVOT.VALUE (single cell)
Used in static pivots and direct cell formulas:
```
=PIVOT.VALUE(pivot_id, "<measure>:<aggregator>", "<groupby_field>", <value>, ...)
```
Example: `=PIVOT.VALUE(19,"unit_amount:sum","employee_id",'Team Data'!A2)`

## Manipulation (via properties)
- Flip axes (rows ↔ columns)
- Add/remove/reorder groupings, change axis, sort
- Add/hide measures, edit names, calculated measures
