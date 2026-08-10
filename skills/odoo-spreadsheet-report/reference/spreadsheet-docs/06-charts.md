# Charts

Source: https://www.odoo.com/documentation/19.0/applications/productivity/spreadsheet/visualize_data/charts.html

## Create
Select data cells → Insert → Chart. Odoo suggests a type. Properties panel on right.

## Types

**Trend:** line, stacked line, combo
**Categorical:** column, bar, stacked column, stacked bar
**Proportional:** pie, doughnut, sunburst, treemap
**Specialized:** scatter, waterfall, funnel, radar, geo
**KPI / Metric:** gauge, scorecard

## Configuration tab
- Chart type
- Domain (filter rules)
- Clickable link to an Odoo menu item

## Design tab
- Background color
- Title formatting
- Legend position
- Data visibility
- Series colors and names

## JSON `figures` shape (from samples)

### Scorecard
```json
{
  "tag": "chart",
  "data": {
    "type": "scorecard",
    "title": {"text": "Missing Planned Hours"},
    "background": "#F4CCCC",
    "keyValue": "'KPI Markers'!G3",
    "keyDescr": {"text": "Task(s)"},
    "baseline": "'KPI Markers'!H18",
    "baselineDescr": {"text": "Hours Expected"},
    "baselineMode": "difference",   // or "text"
    "baselineColorUp": "#43C5B1",
    "baselineColorDown": "#EA6175"
  }
}
```

### Odoo Bar (live data)
```json
{
  "tag": "chart",
  "data": {
    "type": "odoo_bar",
    "title": {"text": "Weekly by Employee"},
    "metaData": {
      "groupBy": ["date:week", "employee_id"],
      "measure": "unit_amount",
      "resModel": "account.analytic.line",
      "mode": "bar"
    },
    "searchParams": {
      "context": {"group_expand": true, "is_timesheet": 1},
      "domain": [["project_id", "!=", false]],
      "groupBy": ["date:week", "employee_id"]
    },
    "stacked": true,
    "actionXmlId": "hr_timesheet.timesheet_action_all"
  }
}
```

### Static line/bar
```json
{
  "tag": "chart",
  "data": {
    "type": "line",
    "dataSets": [{"dataRange": "Report!B2:B11"}],
    "labelRange": "Report!A3:A11",
    "title": {"text": "Target Vs. Achieved"}
  }
}
```
