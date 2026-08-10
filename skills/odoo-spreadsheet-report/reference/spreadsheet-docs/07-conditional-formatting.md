# Conditional Formatting

Source: https://www.odoo.com/documentation/19.0/applications/productivity/spreadsheet/visualize_data/conditional_formatting.html

Auto-updates when Odoo data refreshes.

## Access
Format → Conditional formatting (right panel). "+ Add another rule" / "Add range".

## Four types

### 1. Single Color
- Pick condition from "Format cells if..."
- Set font formatting / font color / background
- E.g. mark `FALSE` cells red

### 2. Color Scale
- Minpoint (low), optional Midpoint, Maxpoint (high)
- Assign color to each
- Example: white → green (sales)

### 3. Icon Set
- Choose set (arrows / smileys / dots)
- Threshold value for icon 1 and icon 2
- Comparator: `>` or `≥`
- Threshold type: Number / Percentage / Percentile / Formula
- Icon 3 = below icon 2

### 4. Data Bar
- Bars in cells proportional to value
- "Apply to range" = where bars draw
- "Range of values" = source data (can differ)

## JSON shape
```json
"conditionalFormats": [
  {
    "id": "<uuid>",
    "ranges": ["A2:A100"],
    "rule": {
      "type": "CellIsRule",
      "operator": "GreaterThan",
      "values": ["0"],
      "style": {"fillColor": "#EA6175", "textColor": "#000000"}
    }
  }
]
```
Other rule types: `ColorScaleRule`, `IconSetRule`, `DataBarRule`.
