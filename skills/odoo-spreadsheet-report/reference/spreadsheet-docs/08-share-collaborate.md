# Share and Collaborate

Source: https://www.odoo.com/documentation/19.0/applications/productivity/spreadsheet/share_collaborate.html

## Access Levels
- **Owner** — full control + delete + role mgmt
- **Editor** — modify content, can't change ownership
- **Viewer** — read-only via link
- **No Access**

Owner or any Editor can manage access on folder or spreadsheet.

## Static vs Dynamic
- **Static** (manual data) — can be shared internally OR externally via Share
- **Dynamic** (Odoo data sources / formulas) — internal only; data respects each user's record rules
- For external share of dynamic: File → Share → **Freeze and share** (converts formulas to values)

## Collaboration
- **Cell comments** — @mentions, emoji, edit/delete (owner/editor only)
- **Chatter thread** — general thread on the document (Documents app info panel)
- Real-time collab + version history audit trail
