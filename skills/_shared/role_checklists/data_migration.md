# Data Migration Specialist

*Calibrated against Odoo 20.0. Re-review on each major version bump — see [release cadence runbook](../release_cadence.md).*

## Goal
When the addon modifies an existing model with live data, ensure the upgrade path is safe — no data loss, no failed installs, no orphaned references. When legacy data is loaded into Odoo (`odoo-data-migration`, or a spec's Data Migration subsection), ensure every record traces to its source row, a re-run cannot duplicate, and the load reconciles to the legacy reports the business trusts.

## Key Questions to Ask the User
- Is this addon **modifying an existing model** that already has records? Which model?
- Are we **adding required fields** to a populated table?
- Are we **renaming or removing fields**?
- Is the **module version bumping** (e.g. 1.0 → 1.1)?
- Are there **cross-DB consumers** (other addons, integrations) that depend on fields we're changing?
- Is this a **cross-Odoo-version migration** (e.g. 17 → 19)? That's the Odoo Upgrade Service ([upgrade.odoo.com](https://upgrade.odoo.com/)), not addon migrations. For Enterprise customers it's the official path; the service ingests a DB dump and returns an upgraded dump.
- How **large** is the populated table? A 10k-row backfill in `post_init_hook` takes seconds; a 10M-row backfill needs batching, commit cadence, and a downtime estimate before it ships.
- Are we doing a **one-time bulk import** of customer data? That is a legacy data import — see the questions below and the `odoo-data-migration` skill.

### Legacy data import
- **Which objects, and how much history?** Default: masters, open documents and opening balances at the cut-over date; full history only with a stated reason.
- **Which legacy reports must the totals tie to** (aged receivables/payables, stock valuation, trial balance at cut-over)? Each becomes a reconciliation control.
- **What is each extract's key, and is it unique?** A duplicate in a key-like column is a data problem to resolve, not a reason to key on names.
- **Which records already exist in Odoo** (the company's own partner, users' partners, a first batch typed by hand)? Match by a reliable key, or state there are none.
- **Is any balance loaded twice?** Receivables loaded as open invoices are not also in the opening trial balance; stock posted by inventory application is not also there.
- **Who signs off** the migrated data, and against what?

## Mechanisms / Tools
- **Migration scripts** live under `<addon>/migrations/<version>/<pre|post>-<step>.py`. Odoo runs them during `-u <addon>` based on the manifest version bump:
  - `pre-` runs before the addon's models are loaded — safe place for raw SQL on the old schema.
  - `post-` runs after the addon's models are loaded — use ORM to backfill.
- **Required fields on existing records**: never declare `required=True` directly. Either:
  1. Declare it `required=False` first, ship a migration to backfill, then bump and add `required=True` in a follow-up release.
  2. Add a `default=` callable that handles all existing rows (safe but only if a sensible default exists).
- **Field renames**: write a `pre-` script that runs `ALTER TABLE my_model RENAME COLUMN old_name TO new_name;` so Odoo doesn't drop+recreate (which would lose data).
- **Field removals**: if the field had data of value, write a `pre-` script that backs it up to another field, then let Odoo drop the column. Don't rely on the user remembering.
- **Manifest `version` bumping**: format `<odoo_major>.<addon_major>.<addon_minor>.<patch>` (e.g. `20.0.1.2.0`). Bump when migration scripts must run.
- **`noupdate="1"` data files**: do NOT change records the user has edited. If you need to update them, write a one-off migration script with explicit rationale.
- **Rollback path for destructive changes**: every column drop, model rename, or data merge documents the undo procedure in the migration script's docstring. The pattern: write the destructive `pre-` migration with a `# Rollback: <SQL or steps>` comment naming the inverse operation, even if it requires backing up to another column first. Without this, the operator hitting a bad upgrade has no escape.
- **Demo data + migration script ordering**: when `demo/` data fixtures touch a model that a migration script also writes to, declare the order of operations in the plan. Default: migrations run first (during `-u`), demo data loads only on fresh install. But when the migration *creates* records the demo data then *references*, the order matters and must be stated.
- **`-u` (upgrade) behaviour**: `-u <addon>` reloads the addon's data files (data + view + security), runs `pre-` migrations for any version path crossed, applies schema changes (column add / type change), loads models, then runs `post-` migrations. `-i` (install) skips migrations and just installs. `-u base` upgrades EVERY addon — never the default on a customer DB.
- **`_log_access = False` on staging / migration tables**: Odoo's default 4 implicit columns (`create_date`, `write_date`, `create_uid`, `write_uid`) come with 4 indexes; a one-shot staging table for migration data doesn't need them. Set `_log_access = False` on the staging model and skip the index cost — relevant only for high-volume migration scratch tables.
- **Idempotency check pattern**: before applying a non-idempotent change, query the current state first — `cr.execute("SELECT 1 FROM <table> WHERE <state-already-applied-condition> LIMIT 1")` then conditionally mutate. Without this, a re-run double-applies.
- **Legacy data import goes through `Model.load()`** — the engine behind the Import button, so every constraint, relational lookup and compute fires. Give every record an external id built from its legacy key (`<prefix>.<dataset>_<key>`): re-runs update instead of duplicating, and reconciliation and rollback can find every migrated record. The prefix must not be a module name — Odoo deletes such records when that module is upgraded (`odoo/orm/models.py:4708`). Dry-run by loading inside a transaction and rolling it back; load in batches, rolling back a whole batch on any error. Relational values by external id, not by name; `name_create_enabled_fields` in context lets the import create missing tags or categories. `odoo-data-migration` implements all of this; for a one-off of a few rows, the Import button's *Test* then *Import* is enough.
- **Expand/contract pattern for renames** — for a field that's read by external consumers, ship the new column alongside the old, dual-write for one release (both updated on every write), let consumers migrate to the new column, then drop the old in the next release. Avoids the "rename = consumers break" failure mode.
- **Cross-Odoo-version migrations — Odoo Upgrade Service**. For Enterprise customers (and Odoo.sh tenants), the official upgrade path is the Odoo Upgrade Service at `upgrade.odoo.com`: submit a DB dump (via the web form or via Odoo.sh's automated upgrade button on staging branches), the service returns an upgraded dump with standard-model data and standard-addon configurations remapped to the target Odoo version. Free for active Enterprise subscriptions. For *custom* addon code, Odoo's `upgrade_code` scripts (`odoo/upgrade_code/`), run **standalone on a copy of the custom addons** — never through `odoo-bin upgrade_code`, which swaps in the full addons path and rewrites core Odoo too; `odoo-version-upgrade` wraps this safely — they apply Odoo's automated code transformations (deprecated-API rewrites, signature shifts, removed-call substitutions). Addon migration scripts (`<addon>/migrations/<version>/...`) cover within-Odoo-version addon-version bumps; the Upgrade Service + the `upgrade_code` scripts cover the underlying Odoo platform upgrade. The two are complementary, not interchangeable. For Community / self-hosted deployments without an Enterprise contract, the upgrade path is manual schema work guided by Odoo's per-version migration notes — significantly more effort; recommend a tier upgrade where feasible.

### Odoo 20+
- **`__manifest__.py` load-hook keys removed**: `init_xml`, `update_xml`, `demo_xml`, and `images_preview_theme` are gone from the default manifest (`odoo/modules/module.py` `_DEFAULT_MANIFEST`). A custom manifest still listing `init_xml` / `update_xml` / `demo_xml` silently loses those load hooks — migrate the referenced files into the `data` key (for `init_xml` / `update_xml`) and the `demo` key (for `demo_xml`) before the v20 upgrade, or the data / views / demo records simply don't load.
- **`__manifest__.py` keys added**: `iap_paid_service` and `other_files` are new default-manifest keys in v20 — available for modules that declare a paid IAP service or ship non-loaded companion files.
- **`upgrade_code` rewrite scripts**: v20 ships official code-transformation scripts under `odoo/upgrade_code/` that flag code-level breaks a custom module must adapt for the platform bump — `ir.access` rename, ormcache-on-transaction, Owl 3 migration, `rec_names_search` returning a tuple, and `t-call` template syntax. Run them standalone on a copy of the custom addons — never via `odoo-bin upgrade_code`, which rewrites core Odoo too (`odoo-version-upgrade` troubleshooting #1) — as part of a cross-Odoo-version upgrade, alongside pushing the DB dump through the Upgrade Service.

## Common Pitfalls
- **Adding `required=True` field to populated table** — install/upgrade fails because existing rows have NULL. Catch in Stage 1 by inspecting field definitions vs target DB row count.
- **Renaming a field without a migration** — Odoo drops the old column and creates the new one; data lost silently.
- **Removing a field referenced by views** — Odoo's view validation catches this; install fails. The fix is to update the view in the same release.
- **Migration script using ORM in `pre-`** — models aren't loaded yet, `env['my.model']` doesn't exist. Use `cr` (raw cursor) instead.
- **Migration script with no idempotency** — running it twice corrupts data. Always check current state before mutating.
- **Forgetting to bump manifest version** — Odoo doesn't run the migration scripts; the user thinks the upgrade ran but it didn't.
- **Destructive migration with no rollback** — column drop / model rename runs cleanly the first time, fails on a subsequent retry with no way back to the prior schema. Always document the undo path inline.
- **Demo data overwrites migrated content** — fresh install loads demo data after the migration, demo overwrites what the migration just created. Pin `noupdate="1"` on the migration's outputs OR sequence demo loading to skip records the migration owns.
- **Running `-u base` on a customer DB** — upgrades every installed addon, takes hours, mass-locks the DB, and is almost never what the operator meant. Targeted `-u <addon>` is the only safe upgrade command.
- **Backfill in a hot loop without batching** — `post_init_hook` that walks 5M rows in one Python loop locks the DB for the duration. Prefer one set-based SQL `UPDATE` in a `migrations/` script; batch ORM work with `limit=N` and no per-row calls. Don't `cr.commit()` inside an install or `-u` (the framework owns that transaction; a commit followed by a failure leaves a half-migrated database). A backfill too large for one transaction moves to a cron that records progress with `ir.cron._commit_progress`.
- **Treating addon migration scripts as Odoo-version migration tooling** — they aren't. `<addon>/migrations/` runs on `-u <addon>` for addon-version bumps within a single Odoo major. Crossing Odoo majors (17 → 19) is the Odoo Upgrade Service's job for the database (`upgrade.odoo.com`) plus the `upgrade_code` scripts, run standalone, for source-tree transformations (`odoo-version-upgrade`).

- **Legacy import — balances counted twice** — open receivables loaded as invoices *and* inside the opening trial balance; the general ledger is overstated by exactly the receivable total.
- **Legacy import — value maps from memory** — chart-of-accounts, journal, tax and payment-term ids are per company in charts built from templates (`account.<company id>_<template id>`); ids typed from memory or another database do not resolve. Take them from the target.
- **Legacy import — importing a derived field** — a read-only stored compute is recomputed away (v20 `res.partner.is_company` is derived from the VAT number); map what it is computed from.
- **Legacy import — passwords or credentials in the load** — never; users are invited after the load.
- **Legacy import — loading production without a snapshot** — the only rollback that also undoes posting and stock application is restoring the pre-load dump.

## Production-readiness criteria
- [ ] If the addon modifies an existing populated model, a migration script exists or it's documented why none is needed.
- [ ] Manifest `version` is bumped if migration scripts must run.
- [ ] Required-field additions follow the two-step pattern OR have a safe default.
- [ ] Field renames have explicit `ALTER TABLE` SQL in a pre-migration.
- [ ] Each migration script is idempotent — running it twice is safe.
- [ ] Smoke test runs `-u <addon>` on a DB with pre-existing data and confirms data is intact.
- [ ] Every destructive migration (drop / rename / merge) has a `# Rollback:` comment naming the undo path.
- [ ] Demo data and migrations don't fight over the same records — order of operations is stated when both touch the same model.
- [ ] **Legacy import:** every dataset reconciles (records present per legacy key, money and stock totals tied to a legacy report), the load was rehearsed on a staging copy, and production is loaded only after a snapshot, with its own confirmation.

## Required artifacts (the plan must contain these)

1. **Migration applicability statement** — for each existing model the addon modifies, declare "no migration needed (greenfield extension)" OR "migration script at `<addon>/migrations/<version>/<pre|post>-<step>.py`" with the specific change it performs.
2. **Manifest version bump** — when migration scripts ship, the plan declares the new manifest version (e.g. `20.0.1.2.0` → `20.0.1.3.0`) and the addon-major / minor / patch level the bump represents.
3. **Backfill strategy per required-field addition** — for every new `required=True` field on an existing populated model, declare which of the two-step / default-callable / post_init_hook patterns is used.
4. **Field-rename SQL inventory** — for every renamed field, name the `ALTER TABLE <model> RENAME COLUMN <old> TO <new>;` statement and where it lives in the pre-migration.
5. **Rollback inventory** — for every destructive change (column drop, model rename, data merge), name the rollback procedure inline. Empty list (no destructive changes) is a valid answer.
6. **Cross-DB consumer disclosure** — if any field being changed is read by external systems (other addons, integrations, reports), name those consumers and confirm they've been notified or that the change is backward-compatible. Empty list is valid.

When the plan **loads legacy data** (otherwise these do not apply):

7. **Dataset inventory in load order** — every source table is a dataset (model, legacy key, row count) or an exclusion with a reason.
8. **Re-run and existing-record policy** — the external-id prefix (not a module name), `match` against records already in Odoo, and update-or-skip on re-run for posted or applied records.
9. **Reconciliation controls** — per dataset, the record count plus a total tied to a named legacy report for every money or stock dataset.
10. **Cut-over and rollback** — rehearsal on a staging copy, freeze, production snapshot before the load, fresh confirmation for the production load.
