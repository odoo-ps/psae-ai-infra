---
name: odoo-python
description: >-
  Use when editing a model or wizard .py file in an Odoo module on Odoo.sh as a
  functional consultant — adding or adjusting a field, an @api.constrains or SQL
  constraint, or a short computed field on an existing model or wizard.
---

# Odoo Python — small functional changes

Scope check first: only a **field**, a **constraint**, or a **short compute
(~2–5 lines)** on an existing model or wizard is yours. A new model (`_name = …`),
an ORM override (`create` / `write` / `unlink`), a controller, or real business
logic → **refer to the technical consultant**. Always `_inherit` to extend an
existing model; never create one. Match the file's style; don't restructure it.

## Field naming

Many2one `*_id` · One2many / Many2many `*_ids` · Boolean `is_*` / `has_*`.

## Version-sensitive APIs (check `$ODOO_VERSION` — model knowledge is often stale)

- **Constraints, v19+:** `_sql_constraints` was removed — use a class attribute:
  ```python
  _uniq = models.Constraint('unique(name, company_id)', 'Name must be unique per company')
  ```
  On **v18 and below** use the old form:
  ```python
  _sql_constraints = [('uniq', 'unique(name, company_id)', 'Name must be unique per company')]
  ```
- **Domains, v19+:** `from odoo.fields import Domain` (combine with `&` / `|`).
  Not `odoo.osv.expression` (legacy), not `odoo.tools.domain` (does not exist).

## Computes & constraints

```python
amount_total = fields.Monetary(compute="_compute_amount_total", store=True)

@api.depends("line_ids.price_subtotal")
def _compute_amount_total(self):
    for record in self:
        record.amount_total = sum(record.line_ids.mapped("price_subtotal"))
```

- `@api.depends(...)` must list every field the compute reads.
- `store=True` only when the field must be searched / grouped — it backfills on
  `-u`; if the data set is large that is getting complex → refer.
- `@api.constrains("field")` raises `ValidationError(_("…%s", value))`.
- `tracking=True` needs `mail.thread` in `_inherit`; `index=True` for fields used
  in frequent filters; `copy=False` for values that must not duplicate.
- Never `self.env.cr.commit()` — Odoo owns the transaction. Translate with
  `_("…%s", value)`, never `.format()` or concatenation inside `_()`.

## Apply

`dev=reload` reloads code automatically, but a new or changed **field** is a
schema change — apply it:

```bash
odoo-bin -u <module> --stop-after-init --no-http
```

Read the traceback if it fails; only then search the standard source.
