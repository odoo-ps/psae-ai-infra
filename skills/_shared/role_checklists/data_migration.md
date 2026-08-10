# Data Migration Specialist

*Calibrated against Odoo 19.0. Re-review on each major version bump.*

## Goal
When the addon modifies an existing model with live data, ensure the upgrade path is safe — no data loss, no failed installs, no orphaned references.

## Key Questions to Ask the User
- Is this addon **modifying an existing model** that already has records? Which model?
- Are we **adding required fields** to a populated table?
- Are we **renaming or removing fields**?
- Is the **module version bumping** (e.g. 1.0 → 1.1)?
- Are there **cross-DB consumers** (other addons, integrations) that depend on fields we're changing?
- Is this a **cross-Odoo-version migration** (e.g. 17 → 19)? That's the Odoo Upgrade Service ([upgrade.odoo.com](https://upgrade.odoo.com/)), not addon migrations. For Enterprise customers it's the official path; the service ingests a DB dump and returns an upgraded dump.
- How **large** is the populated table? A 10k-row backfill in `post_init_hook` takes seconds; a 10M-row backfill needs batching, commit cadence, and a downtime estimate before it ships.
- Are we doing a **one-time bulk import** of customer data? Different tooling: Odoo's import wizard (`base_import`) for CSV/Excel; a Python script using `env['model'].create([{...}])` for richer logic.

## Mechanisms / Tools
- **Migration scripts** live under `<addon>/migrations/<version>/<pre|post>-<step>.py`. Odoo runs them during `-u <addon>` based on the manifest version bump:
  - `pre-` runs before the addon's models are loaded — safe place for raw SQL on the old schema.
  - `post-` runs after the addon's models are loaded — use ORM to backfill.
- **Required fields on existing records**: never declare `required=True` directly. Either:
  1. Declare it `required=False` first, ship a migration to backfill, then bump and add `required=True` in a follow-up release.
  2. Add a `default=` callable that handles all existing rows (safe but only if a sensible default exists).
- **Field renames**: write a `pre-` script that runs `ALTER TABLE my_model RENAME COLUMN old_name TO new_name;` so Odoo doesn't drop+recreate (which would lose data).
- **Field removals**: if the field had data of value, write a `pre-` script that backs it up to another field, then let Odoo drop the column. Don't rely on the user remembering.
- **Manifest `version` bumping**: format `<odoo_major>.<addon_major>.<addon_minor>.<patch>` (e.g. `19.0.1.2.0`). Bump when migration scripts must run.
- **`noupdate="1"` data files**: do NOT change records the user has edited. If you need to update them, write a one-off migration script with explicit rationale.
- **Rollback path for destructive changes**: every column drop, model rename, or data merge documents the undo procedure in the migration script's docstring. The pattern: write the destructive `pre-` migration with a `# Rollback: <SQL or steps>` comment naming the inverse operation, even if it requires backing up to another column first. Without this, the operator hitting a bad upgrade has no escape.
- **Demo data + migration script ordering**: when `demo/` data fixtures touch a model that a migration script also writes to, declare the order of operations in the plan. Default: migrations run first (during `-u`), demo data loads only on fresh install. But when the migration *creates* records the demo data then *references*, the order matters and must be stated.
- **`-u` (upgrade) behaviour**: `-u <addon>` reloads the addon's data files (data + view + security), runs `pre-` migrations for any version path crossed, applies schema changes (column add / type change), loads models, then runs `post-` migrations. `-i` (install) skips migrations and just installs. `-u base` upgrades EVERY addon — never the default on a customer DB.
- **`_log_access = False` on staging / migration tables**: Odoo's default 4 implicit columns (`create_date`, `write_date`, `create_uid`, `write_uid`) come with 4 indexes; a one-shot staging table for migration data doesn't need them. Set `_log_access = False` on the staging model and skip the index cost — relevant only for high-volume migration scratch tables.
- **Idempotency check pattern**: before applying a non-idempotent change, query the current state first — `cr.execute("SELECT 1 FROM <table> WHERE <state-already-applied-condition> LIMIT 1")` then conditionally mutate. Without this, a re-run double-applies.
- **One-time data import via the import wizard**: for customer data loads (legacy system → Odoo), use the Import wizard (`base_import`) reachable from any list view → cogwheel → Import records. Maps CSV/Excel to fields, supports external IDs for relations, dry-runs before commit. Python `env[...].create([{...}])` is the alternative when the import needs custom transformation logic the wizard can't express.
- **Expand/contract pattern for renames** — for a field that's read by external consumers, ship the new column alongside the old, dual-write for one release (both updated on every write), let consumers migrate to the new column, then drop the old in the next release. Avoids the "rename = consumers break" failure mode.
- **Cross-Odoo-version migrations — Odoo Upgrade Service**. For Enterprise customers (and Odoo.sh tenants), the official upgrade path is the Odoo Upgrade Service at `upgrade.odoo.com`: submit a DB dump (via the web form or via Odoo.sh's automated upgrade button on staging branches), the service returns an upgraded dump with standard-model data and standard-addon configurations remapped to the target Odoo version. Free for active Enterprise subscriptions. For *custom* addon code, the companion CLI `odoo-bin upgrade-code --script=<migration-script.py>` runs Odoo's official automated code-transformation passes against the source tree (deprecated-API rewrites, signature shifts, removed-call substitutions). Addon migration scripts (`<addon>/migrations/<version>/...`) cover within-Odoo-version addon-version bumps; the Upgrade Service + `upgrade-code` cover the underlying Odoo platform upgrade. The two are complementary, not interchangeable. For Community / self-hosted deployments without an Enterprise contract, the upgrade path is manual schema work guided by Odoo's per-version migration notes — significantly more effort; recommend a tier upgrade where feasible.

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
- **Backfill in a hot loop without batching** — `post_init_hook` that walks 5M rows in one Python loop locks the DB for the duration. Batch with `limit=N`, `cr.commit()` between batches.
- **Treating addon migration scripts as Odoo-version migration tooling** — they aren't. `<addon>/migrations/` runs on `-u <addon>` for addon-version bumps within a single Odoo major. Crossing Odoo majors (17 → 19) is the Odoo Upgrade Service's job for the database (`upgrade.odoo.com`) plus `odoo-bin upgrade-code` for source-tree transformations.

## Production-readiness criteria
- [ ] If the addon modifies an existing populated model, a migration script exists or it's documented why none is needed.
- [ ] Manifest `version` is bumped if migration scripts must run.
- [ ] Required-field additions follow the two-step pattern OR have a safe default.
- [ ] Field renames have explicit `ALTER TABLE` SQL in a pre-migration.
- [ ] Each migration script is idempotent — running it twice is safe.
- [ ] Smoke test runs `-u <addon>` on a DB with pre-existing data and confirms data is intact.
- [ ] Every destructive migration (drop / rename / merge) has a `# Rollback:` comment naming the undo path.
- [ ] Demo data and migrations don't fight over the same records — order of operations is stated when both touch the same model.

## Required artifacts (the plan must contain these)

1. **Migration applicability statement** — for each existing model the addon modifies, declare "no migration needed (greenfield extension)" OR "migration script at `<addon>/migrations/<version>/<pre|post>-<step>.py`" with the specific change it performs.
2. **Manifest version bump** — when migration scripts ship, the plan declares the new manifest version (e.g. `19.0.1.2.0` → `19.0.1.3.0`) and the addon-major / minor / patch level the bump represents.
3. **Backfill strategy per required-field addition** — for every new `required=True` field on an existing populated model, declare which of the two-step / default-callable / post_init_hook patterns is used.
4. **Field-rename SQL inventory** — for every renamed field, name the `ALTER TABLE <model> RENAME COLUMN <old> TO <new>;` statement and where it lives in the pre-migration.
5. **Rollback inventory** — for every destructive change (column drop, model rename, data merge), name the rollback procedure inline. Empty list (no destructive changes) is a valid answer.
6. **Cross-DB consumer disclosure** — if any field being changed is read by external systems (other addons, integrations, reports), name those consumers and confirm they've been notified or that the change is backward-compatible. Empty list is valid.
