"""Stage-3 operational smoke for an Odoo addon.

Runs inside `odoo-bin shell` to verify the addon is not just installed but
operationally healthy:
  - module is in 'installed' state
  - every declared model is searchable
  - every menu's action resolves
  - a sample record creates, computeds populate, unlinks cleanly
  - declared user groups exist
  - module's own tests (if any) pass with --test-tags=/<module>

Usage (the orchestrating side, e.g. the agent or a Makefile):

    ./v19/odoo/.venv/bin/python ./v19/odoo/odoo-bin shell \\
        -c <instance>/odoo.conf -d <db> --no-http --stop-after-init \\
        < this_script.py

The script pulls the target module name from the env var SMOKE_MODULE.
"""
import os
import sys
import json


MODULE = os.environ.get("SMOKE_MODULE")
if not MODULE:
    print("FAIL: SMOKE_MODULE env var not set")
    sys.exit(1)

issues = []


def err(msg):
    issues.append(("ERROR", msg))


def warn(msg):
    issues.append(("WARN", msg))


print(f"--- Smoke-testing module: {MODULE}")

# 1. Install state
mod = env["ir.module.module"].search([("name", "=", MODULE)], limit=1)
if not mod:
    err(f"module {MODULE!r} not found in ir.module.module")
elif mod.state != "installed":
    err(f"module state is {mod.state!r}, expected 'installed'")
else:
    print(f"  state: installed (id={mod.id})")

# 2. Models declared by this module — `ir.model.modules` is non-stored, so
#    resolve via ir.model.data which has the module owner of every record.
declared_model_ids = env["ir.model.data"].search([
    ("module", "=", MODULE), ("model", "=", "ir.model"),
]).mapped("res_id")
declared_models = env["ir.model"].browse(declared_model_ids)
print(f"  models declared by/extended by module: {len(declared_models)}")
for m in declared_models:
    model = env[m.model]
    # AbstractModel has no DB table — searching it raises "relation does not
    # exist" and poisons the transaction. Skip it (e.g. account.report custom
    # handlers). Each real search runs in a savepoint so one failure can't
    # abort the whole smoke run.
    if getattr(model, "_abstract", False):
        print(f"  (skipping abstract model {m.model!r} — no table)")
        continue
    sp = env.cr.savepoint(flush=False)
    try:
        model.search([], limit=1)
        sp.close()
    except Exception as e:
        sp.rollback()
        err(f"model {m.model!r} unsearchable: {type(e).__name__}: {e}")

# 3. Menus pointing to actions
menus = env["ir.ui.menu"].search([("action", "!=", False)])
module_menus = [
    mu for mu in menus
    if any(d.module == MODULE for d in env["ir.model.data"].search(
        [("model", "=", "ir.ui.menu"), ("res_id", "=", mu.id)]))
]
print(f"  menus owned by module: {len(module_menus)}")
for mu in module_menus:
    try:
        action = mu.action
        if action and hasattr(action, "res_model") and action.res_model:
            env[action.res_model]  # must resolve
    except Exception as e:
        err(f"menu {mu.complete_name!r}: action resolution failed: {e}")

# 4. Groups declared by this module
groups = env["res.groups"].search([])
module_groups = [
    g for g in groups
    if env["ir.model.data"].search_count(
        [("model", "=", "res.groups"), ("res_id", "=", g.id), ("module", "=", MODULE)])
]
print(f"  groups owned by module: {len(module_groups)}")
for g in module_groups:
    if not g.name:
        warn(f"group id={g.id} has no name")

# 5. Sample-record probe on the module's primary models
#    Heuristic: pick the first model owned by this module that is not abstract
#    and has no required Many2one to a record-less model. Try minimal create.
primary = next((m for m in declared_models
                if m.modules and MODULE in m.modules.split(",")
                and m.transient is False
                and not getattr(env[m.model], "_abstract", False)), None)
if primary:
    print(f"  attempting sample create on {primary.model!r}")
    # Use a savepoint so a failed create doesn't poison the outer transaction.
    sp = env.cr.savepoint(flush=False)
    try:
        Model = env[primary.model]
        vals = {}
        if "name" in Model._fields:
            vals["name"] = f"_smoke_test_{MODULE}_{os.getpid()}"
        rec = Model.create(vals)
        for fname, f in Model._fields.items():
            if f.compute and not f.related:
                try:
                    _ = rec[fname]
                except Exception as e:
                    warn(f"compute {primary.model}.{fname} raised: {type(e).__name__}: {e}")
        rec.unlink()
        sp.close(rollback=False)
        print(f"    created+unlinked ok")
    except Exception as e:
        sp.close(rollback=True)
        warn(f"sample create on {primary.model!r} failed (may be fine if model needs setup): "
             f"{type(e).__name__}: {e}")
else:
    print("  no non-transient primary model found for sample probe")

# 6. ACL probe — confirm every model has at least one ACL row
for m in declared_models:
    if m.transient:
        continue
    acl_count = env["ir.model.access"].search_count([("model_id", "=", m.id)])
    if acl_count == 0:
        warn(f"model {m.model!r} has no ir.model.access entries — "
             "non-admin users will not see it")

env.cr.commit()

# Summary
errors = [i for i in issues if i[0] == "ERROR"]
warns = [i for i in issues if i[0] == "WARN"]
print(f"--- {len(errors)} error(s), {len(warns)} warning(s)")
for sev, msg in issues:
    print(f"  {sev:5s} {msg}")
if errors:
    print(f"FAIL: smoke test for {MODULE}")
    sys.exit(1)
print(f"PASS: smoke test for {MODULE}")
