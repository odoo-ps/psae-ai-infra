---
name: odoo-views
description: >-
  Use when editing a view, report, or data XML file in an Odoo module on Odoo.sh
  as a functional consultant — adjusting labels, field order or layout, search
  filters or group-bys, or report wording on an existing view.
---

# Odoo views / XML — small functional changes

Yours: label / help text, field order or placement in an **existing** view,
search filters & group-bys on **existing** fields, report wording. A new
`<record>`, action, menu, or structural xpath that reshapes the view → **refer
to the technical consultant**. Edit through inheritance; never rewrite the
technical consultant's arch.

## Inherited view — three rules

1. `id` = the parent view's XML ID exactly (no `_inherit` suffix).
2. `name` = the parent's dot-name + `.inherit.<your.suffix>`.
3. `inherit_id` ref = `<module>.<parent_xml_id>`.

```xml
<record id="view_order_form" model="ir.ui.view">
    <field name="name">sale.order.form.inherit.my.note</field>
    <field name="model">sale.order</field>
    <field name="inherit_id" ref="sale.view_order_form"/>
    <field name="arch" type="xml">
        <xpath expr="//field[@name='partner_id']" position="after">
            <field name="my_field"/>
        </xpath>
    </field>
</record>
```

The `expr` must match the parent's **current** arch — re-check after any parent
change.

## Version split — conditional attributes (check `$ODOO_VERSION`)

- **v17+:** inline expressions — `invisible="state == 'done'"`,
  `readonly="state not in ('draft', 'sent')"`.
- **≤ v16:** `attrs="{'invisible': [('state', '=', 'done')]}"`, `states="draft"`.
  `attrs` / `states` were removed in v17+ and now raise.

## Action buttons

Wiring a button in a view to something that **already exists** is a view change:

```xml
<button name="action_confirm" type="object" string="Confirm"/>
<button name="%(mail.action_view_mail_mail)d" type="action" string="Emails"/>
```

`type="object"` calls a model method; `type="action"` opens an action by XML ID.
The target must already exist. Creating a **new** action / server action / window
action (a new `<record>` / `<act_window>`) to back the button is structural →
refer. If `type="object"` needs a brand-new handler, only a short method (~2–5
lines, no ORM override) is in scope — see odoo-python; otherwise refer.

## Hard rules

- **No `<?xml version=…?>` declaration** in module XML (audit:
  `grep -rn '<?xml version' <module>/`).
- Lists: `column_invisible` (v17+) hides a whole column; `invisible` is per-cell;
  `optional="show"` for secondary columns.
- A `<search>` view always has fields / filters / group-bys — never empty.

## Apply

A view / arch change needs an update to take effect:

```bash
odoo-bin -u <module> --stop-after-init --no-http
```

Then propose the build URL (`echo $ODOO_BUILD_URL`) so it can be checked in the
browser.
