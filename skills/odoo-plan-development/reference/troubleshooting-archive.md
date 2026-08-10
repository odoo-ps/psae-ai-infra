# Plan Development — Troubleshooting Archive

Fixed, obsolete, or version-retired troubleshooting entries. Not loaded by the skill at run time — consult only when investigating "did we hit this before?"

**ID space is shared with the active file** ([`troubleshooting.md`](troubleshooting.md)) — never reused. Entries here keep the ID they had when active.

**Promotion criteria for new archival:**
- Status `fixed` for 90+ days with no recurrence (`Last confirmed` is the recurrence trigger — bumping it on re-encounter takes the entry back to active).
- Whole version-specific section retired when no supported deployment runs that Odoo version.
- Cause has been promoted to a principle or role checklist (insight is now codified upstream).

When archiving, set `Status: fixed YYYY-MM-DD` (or `obsolete YYYY-MM-DD`) and add a one-line `Retired: <reason>` at the end of the entry.

---

## Fixed bugs in skill tooling

### 13. Smoke script aborts mid-run after a failed sample-create probe
Applies: all versions. Status: fixed 2026-06-13. Last confirmed: 2026-05-20.
Cause: When `Model.create({})` fails (e.g. `sale.order` requires `partner_id`), Postgres leaves the transaction in aborted state — subsequent queries raise `InFailedSqlTransaction`.
Fix: Wrap sample-create probes in `env.cr.savepoint()` and rollback on exception. Already applied to `_smoke_module.py`.
Retired: Internal tooling fix applied in `_smoke_module.py`; recurrence not possible once the script is patched. Permanently retain after 2026-09-11.

### 20. `_create_instance.py` aborts with `All default ports (8069, 8019, 8029, 8039, 8049, 8059) are in use`
Applies: tooling. Status: fixed 2026-06-13. Last confirmed: 2026-05-20.
Cause: `free_http_port()` had a hard-coded six-port pool — exhausted after six sibling instances.
Fix: Pool widened to `(8069, *range(8019, 8200, 10))` — 19 ports, +10 increments so longpolling fallback (`http_port + 4`) still holds.
Retired: Internal tooling fix applied in `_create_instance.py`; recurrence not possible once the script is patched. Permanently retain after 2026-09-11.

### 31. `launch.json` patch is missing the `python` interpreter field
Applies: tooling. Status: fixed 2026-06-13. Last confirmed: 2026-05-20.
Cause: `_create_instance.py` called `Path(venv).resolve().relative_to(repo_root)`. `.resolve()` follows symlinks; `odoo/.venv/bin/python` symlinks into `~/.pyenv/...` outside the repo, so `relative_to()` raised `ValueError`, was caught, and the patcher silently omitted `python`.
Fix: Don't `.resolve()` before `.relative_to()` — keep the literal symlink path. Already applied to `_create_instance.py`.
Retired: Internal tooling fix applied in `_create_instance.py`; recurrence not possible once the script is patched. Permanently retain after 2026-09-11.

### 37. Smoke script `ir.model.search([("modules", "ilike", X)])` raises "not stored"
Applies: Odoo 19. Status: fixed 2026-06-13. Last confirmed: 2026-05-20.
Cause: `ir.model.modules` became computed/non-stored in Odoo 19 — can't be used in a domain.
Fix: Resolve via `ir.model.data` instead: `env["ir.model.data"].search([("module","=",MODULE),("model","=","ir.model")]).mapped("res_id")` then `env["ir.model"].browse(ids)`. Already applied to `_smoke_module.py`.
Retired: Internal tooling fix applied in `_smoke_module.py`; recurrence not possible once the script is patched. Permanently retain after 2026-09-11.

### 45. `_create_instance.py --write` crashes with `FileNotFoundError` on `nginx.conf` write
Applies: tooling, `_create_instance.py`. Status: fixed 2026-05-13. Last confirmed: 2026-05-13.
Cause: Ordering bug in `main()` — `write_nginx_config()` was called before `instance_dir.mkdir(...)` ran, so when nginx was enabled the call raised `FileNotFoundError` writing into a non-existent folder. The IDE patch ran earlier in the same invocation and was left applied — partial state on re-runs.
Fix: Moved the nginx execution call (`write_nginx_config(..., dry_run=False)`) to after the `instance_dir.mkdir(...)` block inside the `if args.write:` branch of `main()`. Dry-run printout still produced earlier for the non-`--write` path.
Retired: Confirmed clean in the wkc_demo scaffold (2026-05-13) and subsequent instance creates. Permanently move to archive after 90 days no-recurrence (2026-08-11).
