# Odoo Spreadsheet Functions

Source: https://www.odoo.com/documentation/19.0/applications/productivity/spreadsheet/work_with_data/functions.html

## Categories
Array, Date, Financial, Lookup, Math, Misc, Operators, Statistical, Text — plus Odoo-specific.

## Odoo-Specific Functions

### Array / Data Source
- `ODOO.LIST(list_id, index, "field_name")` — single value from a list
- `ODOO.LIST.HEADER(list_id, "field_name", ["custom_label"])` — header label
- `ODOO.PIVOT(pivot_id, ...)` — pivot value (legacy form)
- `ODOO.PIVOT.HEADER(pivot_id, ...)` — pivot header
- `PIVOT(pivot_id, [row_count], [include_total], [include_column_titles], [column_count])` — dynamic pivot array
- `PIVOT.VALUE(pivot_id, "measure:agg", "groupby_field", value, ...)` — static pivot single cell

### Filter
- `ODOO.FILTER.VALUE("filter_label")` — current value of a global filter

### Financial
- `ODOO.RESIDUAL(...)` — remaining balance
- `ODOO.CREDIT(...)` — credit on account
- `ODOO.DEBIT(...)` — debit on account
- `ODOO.BALANCE(...)` — account balance
- `ODOO.CURRENCY.RATE(from, to, [date])` — FX rate

### Date / Fiscal
- `ODOO.FISCALYEAR.START([date], [fiscal_offset])`
- `ODOO.FISCALYEAR.END([date], [fiscal_offset])`

### Lookup / Accounting
- `ODOO.ACCOUNT.GROUP(...)`

## Patterns from sample sheets

- `=ODOO.LIST(1,1,"date")` then `=ODOO.LIST(1,2,"date")` — index increments per row
- `=ODOO.LIST.HEADER(2,"project_id")` — header for list 2's project_id column
- `=PIVOT.VALUE(19,"unit_amount:sum","employee_id",'Team Data'!A2)` — sum of unit_amount filtered by employee_id

## Practical Notes
- A list ID is assigned at insertion (sequential).
- Field names are technical (e.g. `project_id`, not "Project").
- Dotted chains supported: `project_id.user_id`, `last_update_id.date`.
- `ODOO.LIST` does NOT auto-expand row count — pre-allocate enough rows in the sheet.
