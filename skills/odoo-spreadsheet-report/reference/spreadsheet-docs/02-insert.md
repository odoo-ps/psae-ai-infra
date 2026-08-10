# Insert and Link to Odoo Data

Source: https://www.odoo.com/documentation/19.0/applications/productivity/spreadsheet/insert.html

## Overview

Lists, pivot tables, and charts inserted from Odoo become live data sources. They refresh on open or via Data → Refresh all data.

## Data Sources

- Identified by icon + ID + name, e.g. `(#1) Sales Analysis by Product`
- Accessed via Data menu; properties via right-click or menu icon
- Deleting inserted list/pivot cells does NOT remove the data source — only deleting the data source itself does
- Deleting a chart removes its data source

### Accessing underlying records
- Lists: right-click row → See record
- Pivot: right-click cell → See records
- Charts: click data point
- Ctrl/Cmd + click opens in new tab

## Inserting Lists

1. Open list view in DB
2. Actions → Spreadsheet → Insert list in spreadsheet
3. Edit name; specify number of records; choose new or existing spreadsheet; Confirm

Notes:
- Lists do not auto-expand for new records — pre-allocate extra rows
- Default row count = visible records on first page

### List formulas
```
=ODOO.LIST.HEADER(list_id, field_name)
=ODOO.LIST(list_id, index, field_name)
```
- `list_id`: sequential, first list = 1
- `index`: row position, first = 1
- `field_name`: technical field name (e.g. `project_id`, `unit_amount`)

### List Properties
- List #
- List Name
- Model
- Columns (fields at insertion time)
- Domain (filter)
- Sorting

## Inserting Pivot Tables

Live, refresh automatically. Organize by dimensions + measures (like the DB pivot view).

## Inserting Charts

From graph views. Some elements editable but not full data manipulation like lists/pivots.

## Clickable Links
- Links to Odoo menu items
- Links to other sheets
- External URLs
- Add from cells or chart data points

## Financial Data
Specialized ODOO.* financial functions — see functions doc.

## Data Management Tips
- Configure visible fields/filters/sort BEFORE insertion
- Watch dataset size for performance
- Do NOT change list IDs in sheet names — IDs are persistent
- Disconnect a list: select → copy → Paste special → Paste as value

Multiple lists/pivots/charts from different apps can coexist in one spreadsheet.
