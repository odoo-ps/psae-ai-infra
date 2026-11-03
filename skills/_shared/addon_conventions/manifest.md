# Manifest — `__manifest__.py`

*Calibrated against Odoo 19.0 and 20.0 source. Re-review on each major version bump — see [release cadence runbook](../release_cadence.md).*

The manifest is a single Python dict literal. Odoo merges it over its own defaults
(`_DEFAULT_MANIFEST` in `odoo/modules/module.py`, v19 `:56-96`, v20 `:60-98`),
normalises a few keys, and refuses or silently disables the module when one is wrong.
Stage 1 (`odoo-plan-development/reference/scripts/_lint_addon.py`) enforces the
mechanical rules marked **lint** below.

## Shape of a custom addon's manifest

```python
{
    "name": "Library Loans",
    "summary": "Lend books to members and track returns",
    "version": "20.0.1.0.0",
    "category": "Services/Library",
    "author": "Acme Consulting",
    "website": "https://www.example.com",
    "license": "OPL-1",
    "depends": ["mail", "stock"],
    "data": [
        "security/library_security.xml",
        "security/ir.access.csv",          # v19: security/ir.model.access.csv
        "data/library_data.xml",
        "views/library_book_views.xml",
        "views/library_menus.xml",         # menus last: they reference actions
    ],
    "demo": ["demo/library_demo.xml"],
    "assets": {"web.assets_backend": ["library/static/src/**/*"]},
    "application": True,
    "installable": True,
}
```

## Keys

| Key | Default (source) | Rule |
|---|---|---|
| `name` | none: mandatory | The display name in Apps. **lint**: required. |
| `author` | none: mandatory | Missing → load warning `Missing 'author' key in manifest`, defaulting to `contributors`/`maintainer` or `''`. **lint**: warns. |
| `license` | none: mandatory | Missing → warning, defaults to `LGPL-3`. Must be one of `GPL-2`, `GPL-2 or any later version`, `GPL-3`, `GPL-3 or any later version`, `AGPL-3`, `LGPL-3`, `Other OSI approved licence`, `OEEL-1`, `OPL-1`, `Other proprietary` (the `ir.module.module.license` selection, `ir_module.py:314-324`). Set it deliberately. **lint**: warns if missing, errors if not in the list. |
| `version` | `'1.0'` | 2 to 5 numeric parts. A short form (`1.0`, `1.2.0`) gets the series prefixed (`20.0.1.2.0`). A full version must start with the running series (`20.0.`). Otherwise Odoo logs "incompatible version, setting installable=False" and **the module silently disappears** from the install list. Use `<major>.0.<x>.<y>.<z>`, and bump it whenever a `migrations/` script must run. **lint**: errors on bad format or a series that does not match the target. |
| `depends` | `[]` → `['base']` injected | Every module whose models, views, data or assets this one uses, **direct dependencies only**. Never list `base`: it is injected when `depends` is empty, and upgrading `base` upgrades every module anyway. Resolve each model to its *owning* module ([`solution_architect.md`](../role_checklists/solution_architect.md)). **lint**: warns on `base`; no longer requires the key. |
| `data` | `[]` | Loaded on install **and every update**, in list order: a record's references first. Order security groups, then access rows, then data, then views and actions, then menus. Every entry must exist. **lint**: errors on a missing file. |
| `demo` | `[]` | Loaded only when the database was created with demo data. Never put records the module needs to work here. **lint**: errors on a missing file. |
| `summary` | `''` | One line under the name in Apps. |
| `description` | `''` → the module's `README.rst/.md/.txt` | Prefer a README; a long `description` string goes stale. |
| `category` | `'Uncategorized'` | `Parent/Child` path; missing categories are created. Pick an existing one (`Sales/Sales`, `Inventory/Inventory`, `Services/…`) so the module sorts with its peers. |
| `website` | `''` | — |
| `application` | `False` | `True` only for a full app with its own root menu: it gets a tile and the Apps-list icon (`static/description/icon.png`). Technical and extension modules stay `False`. |
| `installable` | `True` | Set `False` only to park a module; the version rule above can flip it silently. |
| `auto_install` | `False` | `True`: installed automatically once **all** `depends` are installed (a "link" module, e.g. `sale_stock`-style glue). A list: auto-installed when **those** modules are installed, and the list must be a subset of `depends` (an `assert` at load time otherwise). `[]`: always installed. Never on a client feature module. **lint**: errors when a list holds a non-dependency. |
| `external_dependencies` | `{}` | `{"python": ["pypi-name"], "bin": ["wkhtmltopdf"]}`. Checked at install: a missing one raises `MissingDependency`. Use the PyPI package name (Odoo warns otherwise). Install the package in the instance venv with `python -m pip`. |
| `assets` | `{}` | `{"<bundle>": [paths or ('include'/'remove'/'after', …) directives]}` — the only place static files join bundles (`web.assets_backend`, `web.assets_frontend`, `point_of_sale._assets_pos`, `web.report_assets_common`, …). Glob paths are relative to the addons root (`library/static/src/**/*`). |
| `pre_init_hook` / `post_init_hook` / `uninstall_hook` | `''` | The **name** of a function importable from the module's `__init__.py`, called with `env`. The pre- and post-init hooks run **only at install**, never on `-u` (`modules/loading.py`, v20 `:174-179, 237-240`); work an update needs belongs in a `migrations/` script. **lint**: errors when the named function is not defined or imported in `__init__.py`. |
| `post_load` | `''` | Server-wide hook at module import (rare; monkey-patching). |
| `countries` | `[]` | Localization modules only: the ISO codes the module applies to (also sets its flag icon). |
| `sequence` | `100` | Order in the Apps list. |
| `images` | `[]` | Apps-store screenshots. |
| `cloc_exclude` | `[]` | Paths left out of `odoo-bin cloc` line counts (e.g. vendored `static/lib/**`). |
| `iap_paid_service`, `other_files` | v20 only | New v20 keys: a paid IAP service flag; companion files that are not loaded. |
| `init_xml`, `update_xml`, `demo_xml` | v19 only | **Gone in v20.** Files listed there are silently not loaded. Use `data`/`demo` on every version. **lint**: errors on v20 targets, warns on v19. |

Keys Odoo reads but does not default (`maintainer`, `contributors`, `price`,
`currency`, `support`, `live_test_url`) are accepted. Any other key is almost always a
typo (`'data_files'`, `'depend'`), which Odoo ignores silently. **lint**: warns on unknown keys.

## The data-file order that works

```
security/<module>_security.xml   groups, privileges / categories
security/ir.access.csv           v20 (v19: security/ir.model.access.csv, then record-rule XML)
data/*_data.xml                  sequences, mail templates, crons, parameters
report/*_reports.xml             report actions and paperformats, then report/*_templates.xml
wizard/*_views.xml               transient views and actions
views/*_views.xml                views and window actions
views/*_menus.xml                menus last: a menu's action must already exist
```

`data` loads in one pass, so a reference to a record defined later fails at install with
"External ID not found" (plan-dev troubleshooting #47).

## Version notes

- **v20** removed `init_xml`/`update_xml`/`demo_xml`, and added `iap_paid_service` and
  `other_files`.
- **Both** versions require the full version to carry the running series (`19.0.` on
  v19, `20.0.` on v20). When an addon moves between versions, its version is the first
  thing to change (`odoo-version-upgrade` Stage 1 checks it).
