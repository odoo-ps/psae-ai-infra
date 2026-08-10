# Global Filters

Source: https://www.odoo.com/documentation/19.0/applications/productivity/spreadsheet/work_with_data/global_filters.html

Global filters apply to **all** data sources of a spreadsheet/dashboard simultaneously. They filter data **at the source**, before it loads — unlike sheet filters which only hide visible rows.

## Access
- Filters icon top-right of spreadsheet, OR dashboard search bar
- Editor rights to configure; dashboard users only apply

## Configure
1. Open spreadsheet
2. Filters → Create filter section
3. Choose filter type
4. Complete properties + Field matching (which field of each data source the filter binds to)
5. Save

## Filter Types
- **Date** — fixed or relative range (e.g. Last 7 Days, this_month)
- **Relation** — many2one/many2many target (e.g. Salesperson, Project)
- **Text** — string match
- **Yes/No** — boolean
- **Selection** — selection field options
- **Numeric** — number/range

## Field Matching
For each data source (list/pivot/chart), specify the field chain that the filter should restrict (e.g. `project_id.user_id` for a Project Manager filter on a timesheet list).

## Best Practices
- Avoid duplicating the global filter's domain in the data source's own domain
- Set default values for fast initial load and useful out-of-the-box view

## JSON shape (from samples)
```json
"globalFilters": [{
  "id": "<uuid>",
  "label": "Projects",
  "type": "relation",
  "modelName": "project.project",
  "domainOfAllowedValues": [["name","ilike","[DU-MMC]"]],
  "displayNames": ["[DU-MMC] Real Estate - Marya Development"]
}]
```
And on each list/pivot/chart:
```json
"fieldMatching": {
  "<filter_id>": {"chain": "project_id", "type": "many2one"}
}
```
