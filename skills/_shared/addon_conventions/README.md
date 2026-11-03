# Addon conventions

House rules for the **code** inside an Odoo addon: the manifest, the module layout and
naming, Python, views and data, tests, and web assets. Every skill that writes or
rewrites addon code follows them:

- `odoo-plan-development` when it scaffolds and builds an addon;
- `odoo-version-upgrade` when it carries one to a newer major.

The role checklists ([`../role_checklists/`](../role_checklists/)) are the review lenses
(what a security reviewer, a performance engineer or QA looks for). This folder is the
style those lenses assume. Security and performance rules live in their checklists,
not here.

| File | Read it when |
|---|---|
| [`manifest.md`](manifest.md) | writing or changing `__manifest__.py`: every key, its default, the version and series rule, data-file order |
| [`module_structure.md`](module_structure.md) | creating files or folders, naming a model, field, method, variable or external id |
| [`python.md`](python.md) | writing models, computes, constraints, controllers, translatable strings, fields |
| [`views_and_data.md`](views_and_data.md) | writing XML records, inheriting a view, QWeb templates and reports |
| [`tests.md`](tests.md) | writing `tests/`: base classes, tags per version, tests that silently never run |
| [`web.md`](web.md) | anything under `static/`: JS, OWL templates, SCSS, assets |

## Where this comes from

The rules are distilled from the guideline skills Odoo ships in its own source tree
from v20 (`odoo-guidelines`, `odoo-web-guidelines` and `odoo-security`, under the
repository's `skills/` folder). They are written for Odoo's master branch, so every rule
that depends on the version was checked against both the v19 and the v20 source on
disk, and is tagged where they differ. Some of Odoo's master-branch rules are wrong for
v19, for example the default test tags, `ir.access`, `t-esc`, and `base.group_everyone`.

This folder is **self-contained**: no skill reads Odoo's `skills/` folder at run time,
and nothing here is a symlink. When a new major ships updated guidelines, refresh these
files through the [release cadence runbook](../release_cadence.md); never point at the
Odoo tree instead.

The mechanical parts are enforced: plan-dev's
[`_lint_addon.py`](../../odoo-plan-development/reference/scripts/_lint_addon.py)
checks the manifest rules marked **lint** in [`manifest.md`](manifest.md), and
`odoo-version-upgrade`'s scanner catches the version-specific ones on an upgrade.
