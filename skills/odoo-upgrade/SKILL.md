---
name: odoo-upgrade
description: >-
  Use when a client asks to upgrade or migrate an Odoo module to a newer Odoo
  version on Odoo.sh, or mentions porting a module between major versions.
---

# Odoo upgrade — mostly: assess and refer

A version upgrade is usually a **technical** task. Your job is to scope it safely
and hand the heavy parts over. Confirm both versions first: the **source** (the
module's current major) and the **target** (`$ODOO_VERSION`) — ask the user for
the source if it has not been given.

## Check what became standard (cheapest first — stop and discuss at each step)

1. **Your own knowledge** of the target version — which custom features may now
   be standard? Present findings, wait for the user.
2. **Official docs** for the target version.
3. **Release notes** between source and target (odoo.com/page/release-notes).
4. **Only if still uncertain:** search `/home/odoo/src/{odoo,enterprise}`.

Agree KEEP / DROP / REWRITE with the user before touching code. A feature now
covered by standard is a DROP, not a port.

## What's yours vs the technical consultant's

- **Yours (small):** label / view / filter / wording adaptations to the new
  version; swapping a removed view attribute for its v17+ inline form (see
  odoo-views); verifying with `odoo-bin -u <module> --stop-after-init --no-http`.
- **Refer:** rewriting Python logic or ORM overrides; **schema changes** (renamed
  or dropped fields) needing `migrations/<version>/pre-migration.py` /
  `post-migration.py`; installing `odoo_upgrade` or editing `requirements.txt`.
  These are migration engineering — hand over with a short note of what changed.

Keep existing tests; adapt only their **syntax** to the new version, never the
business flow they assert.
