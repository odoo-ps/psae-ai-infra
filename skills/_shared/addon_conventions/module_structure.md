# Module structure and naming

*Calibrated against Odoo 19.0 and 20.0. Re-review on each major version bump — see [release cadence runbook](../release_cadence.md).*

## Layout

```
library/
├── __init__.py                 imports models, controllers, wizard, report; defines hook functions
├── __manifest__.py             see manifest.md
├── models/                     one model class per file: library_book.py, res_partner.py
├── views/                      *_views.xml (backend), *_templates.xml (QWeb pages), *_menus.xml
├── security/                   <module>_security.xml (groups, …) + the access CSV
├── data/                       *_data.xml (records the module needs), loaded on every update
├── demo/                       *_demo.xml, loaded only with demo data
├── wizard/                     <transient>.py + <transient>_views.xml
├── report/                     printable: <model>_reports.xml + <model>_templates.xml;
│                               SQL-view analysis: <model>_report.py + <model>_report_views.xml
├── controllers/                feature-named files, or <inherited_module>.py when extending
│                               another module's controller (portal.py); main.py is legacy
├── migrations/<x.0.a.b.c>/     pre-/post-/end- scripts (see data_migration role checklist)
├── static/
│   ├── description/icon.png    Apps-list icon (application modules)
│   ├── src/                    JS, OWL templates, SCSS — see web.md
│   └── lib/                    vendored third-party code, unminified
├── tests/                      test_*.py, imported from tests/__init__.py — see tests.md
└── doc/                        user and testing manuals (plan-dev convention)
```

- One model class per file, named after the model with dots as underscores
  (`library_book.py`, `res_partner.py`), whether the class creates a model or extends
  one with `_inherit`.
- File and folder names are Python identifiers: lowercase `[a-z0-9_]`.
- **Access file per version:** v19 `security/ir.model.access.csv` (plus `ir.rule`
  records in XML); v20 `security/ir.access.csv` (rows carry the record-rule domain).
  See [`security.md`](../role_checklists/security.md).

## Naming

**Models.** `_name` is dotted, starts with the module's own prefix, and is **singular**
(`library.book`, not `library.books`). A wizard is `<base model>.<action>`
(`library.book.return`). A SQL-view analysis model is `<base model>.report.<subject>`.

**Fields.** `Many2one` ends in `_id`; `One2many` and `Many2many` end in `_ids`. A field
and a method cannot share a name.

**Methods.** Compute `_compute_<field>`, inverse `_inverse_<field>`, search
`_search_<field>`, default `_default_<field>`, selection `_selection_<field>`, onchange
`_onchange_<field>`, constraint `_check_<rule>`. A button action is `action_<verb>` and
starts with `self.ensure_one()`. Every other method starts with `_` unless it must be
callable over RPC (see [`python.md`](python.md) § Methods).

**Variables.** A model class is PascalCase (`Book = self.env['library.book']`). A
variable holding ids ends in `_id`/`_ids`; one holding records does not (`partner`,
not `partner_id`, for a `res.partner` record).

**Class body order.** `_name`, `_description`, `_inherit`, `_order` → default methods →
fields → `models.Constraint` / `models.Index` attributes → compute, inverse and search
methods (in field order) → selection methods → `@api.constrains` / `@api.onchange` →
CRUD overrides → `action_*` methods → other business methods.

**External ids.**

| Record | Pattern | Example |
|---|---|---|
| View | `<model>_view_<type>` | `library_book_view_form` |
| Window action | `<model>_action[_<detail>]` | `library_book_action` |
| Menu | `<model>_menu[_<detail>]` or `<module>_menu_root` | `library_book_menu` |
| Group | `<module>_group_<name>` | `library_group_manager` |
| Record rule (v19) / access row (v20) | `<model>_rule_<group>` / `access_<model>_<group>` | `library_book_rule_user` |
| Inheriting view | the parent's id, in your module's namespace; `name` suffixed `.inherit.<module>` | `library.view_partner_form` inheriting `base.view_partner_form`, name `res.partner.form.inherit.library` |

The record `name` mirrors the id with dots; actions get a real display name. Existing
client addons keep their established ids: renaming an id loses the link to user data.
