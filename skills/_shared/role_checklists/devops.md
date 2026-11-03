# DevOps / Operability

*Calibrated against Odoo 20.0. Re-review on each major version bump — see [release cadence runbook](../release_cadence.md).*

## Goal
Make the addon installable, upgradable, and observable in production without on-call surprises.

## Key Questions to Ask the User
- Will this addon be **upgraded** in place (existing installs need migration), or only freshly installed?
- Are there **scheduled jobs** (cron) that should be visible in the Settings → Technical → Scheduled Actions UI?
- Does the addon write to **external services** (HTTP, SMTP, S3)? Failure modes?
- Will the addon be deployed to **multiple environments** (dev, staging, prod) with different configs?
- Is the deployment **Odoo.sh** or **on-premise**? Odoo.sh has staging / prod branch flow, build hooks via manifest, log streams via the web UI; on-prem has direct file/log access and full host-shell control.
- What's the expected **load profile** — number of concurrent users, cron job frequency, longpolling subscriber count? Drives `--workers` / `--cron-threads` sizing.

## Mechanisms / Tools
- **Logging**: import `logging` at the top of every model, get a logger via `_logger = logging.getLogger(__name__)`. Use `_logger.info` for normal flow, `_logger.warning` for recoverable issues, `_logger.error` for failures the operator must see. Never `print(...)`.
- **Upgrade hooks** in `__manifest__.py`:
  ```python
  "pre_init_hook": "_pre_init_hook",      # before any models load
  "post_init_hook": "_post_init_hook",    # after install completes
  "uninstall_hook": "_uninstall_hook",    # cleanup on uninstall
  ```
  Use them sparingly — most data changes belong in migration scripts.
- **Migration scripts** under `<addon>/migrations/<version>/<pre|post>-<step>.py` — see `data_migration.md`.
- **`noupdate` policy**: data files declared with `noupdate="1"` are loaded only on first install; subsequent `-u` won't update them. Use for seed data the customer will edit. Use `noupdate="0"` (default) for data we want to keep in sync with the addon.
- **Cron**: declare via `<record model="ir.cron">` in a data file. Set `interval_number`, `interval_type`, `numbercall=-1`, and importantly `priority` and `active=True`. Always include a defensive `try/except` in the cron's Python entry point — uncaught exceptions on cron go to the log and the cron auto-disables.
- **External service calls**: timeout every HTTP call (`requests.post(..., timeout=10)`); catch `requests.exceptions.RequestException`; log the failure with context; surface as a user-visible chatter message if the call was triggered by a user action.
- **Config via `ir.config_parameter`**: never hardcode environment-specific values. `self.env['ir.config_parameter'].sudo().get_param('my_module.api_url')` — settable from the UI or via `-d ... --load-language` style scripts.
- **Cron `numbercall` semantics**: `-1` = run forever (default for recurring jobs); `1` = run once and disable (for one-shot scheduled actions). `priority` orders concurrent crons (lower = sooner); `active=True` is the default but worth declaring explicitly.
- **Odoo.sh branch flow**: feature branches → push triggers a build → merge to `staging` branch → build + restore-from-prod → merge to `prod` → build + deploy. Builds run a `__manifest__.py`-declared dep install + a `-i / -u <module>` cycle; no host-shell access. What's allowed: Python deps in manifest's `external_dependencies`, addon-bundled assets. What's forbidden: arbitrary OS packages, host-shell scripts, custom binaries.
- **Production sizing flags**: `--workers <N>` sets HTTP worker count (rule of thumb: 2× CPU cores for I/O-heavy Odoo workloads, 1× for CPU-heavy). `--cron-threads <N>` sets cron worker count (default 2; raise for cron-heavy deployments). `--limit-time-cpu <s>` and `--limit-time-real <s>` bound per-request CPU / wall-clock — workers get killed and respawned on overrun. `--limit-memory-hard <bytes>` likewise for memory. `--max-cron-threads` caps cron concurrency.
- **Longpolling**: a separate worker pool that holds long-lived HTTP connections for chat / notifications. Backlog on longpolling = users see UI lag on chatter updates; size with `--longpolling-port` and ensure your reverse proxy routes WebSocket traffic correctly.
- **Health and observability**: `/web/health` returns 200 when Odoo is responsive. Log-stream consumption on Odoo.sh via the web UI; on-prem via the configured `logfile` or stdout (12-factor logs-to-stdout pattern). Structured JSON logging is not Odoo's default but can be configured via `logging` module handlers in `pre_init_hook` if downstream tooling needs it.
- **12-factor app discipline** — config in env / `ir.config_parameter`, logs to stdout, processes stateless (`ir.config_parameter` and the DB are the only stateful surfaces). Maps cleanly onto Odoo.sh's container model.

### Odoo 20+
- **Runtime floor raised**: minimum Python is now **3.12** (was 3.10) and minimum PostgreSQL is now **16** (was 13) — `odoo/release.py` sets `MIN_PY_VERSION=(3, 12)` and `MIN_PG_VERSION=16`. Provision the base image / host with these before a v20 deploy; an older interpreter or DB server won't start.
- **`requirements.txt` changes**: the legacy `python_version < 3.11/3.12` fallback pins are dropped, `xlwt` is **removed** (XLS *write* via xlwt is gone — retest any `.xls` export path; it must move to `xlsxwriter` / `.xlsx`), and `h11` is added. Re-freeze the deployment's pinned deps against the v20 file rather than carrying the v19 set forward.
- **CLI `odoo populate` removed**, replaced by the new **`odoo duplicate`** command (`odoo/cli/duplicate.py`). Any deploy / test script that seeded scale data via `odoo populate` must switch to `odoo duplicate`.
- **`ir.cron` resilience overhaul** (`addons/base/models/ir_cron.py`): `MIN_TIME_PER_JOB` is raised from 10s to **120s** (a job scheduled more frequently is throttled to the floor); a cron that fails repeatedly is now **auto-deactivated** (after 5 failures / 7 days) with an admin notification; and each job now runs in an **isolated `contextvars` `copy_context()`** so one job can't leak context onto the next. Size cron intervals for the 120s floor, and don't rely on a cron self-healing silently — the 5-failure deactivation is visible and terminal until an admin re-enables it.

## Common Pitfalls
- **Cron with no batch limit** — degrades silently as data grows; in prod it'll start missing its window.
- **Cron with no error handling** — one transient HTTP failure auto-disables it; no one notices for days.
- **`pre_init_hook` touching the module's own models** — it gets `env`, but runs before this module's models are loaded, so only models of modules already loaded are usable and this module's tables do not exist yet. Easy to break.
- **`uninstall_hook` not actually removing data** — uninstall leaves orphan tables; reinstall fails because the tables already exist with a different schema.
- **Hardcoded URLs / credentials** — fine in dev, blocking in prod. Use `ir.config_parameter` from day one.
- **Logging at `info` for hot-path events** — log volume explodes; switch to `debug`.
- **Assuming Odoo.sh allows host-shell tooling** — it doesn't. Anything that needs `apt-get`, system services, or shell scripts won't deploy. Re-shape as a manifest-declared Python dep or a custom binary bundled in the addon's `static/` dir (and even that has limits).
- **Cron `numbercall=-1` on a hot-path script** — recurring with no batch limit means the script runs every minute, accumulates work, and eventually misses its window. Always pair with `limit=N` on `search()` calls and commit between batches.
- **Default `--workers=0` in production** — Odoo's default is single-process; under multi-user load that's a brick wall. Set `--workers` to ~2× CPU cores before any production traffic hits.
- **A guard that breaks a standard operation** — a `write`/`create`/`unlink` guard added to protect committed data also fires from cancel, unreserve, validation, or backorder (which traverse the same code), so the document can't be cancelled or shipped. Identify the system flows that cross the guard and exempt them via a trusted-operation context flag; block only the manual path. (principle #15)

## Production-readiness criteria
- [ ] Every Python module imports `logging` and uses `_logger`, never `print`.
- [ ] Cron jobs have batch limits, commit between batches, and wrap their entry point in try/except with logging.
- [ ] External calls have timeouts and exception handling.
- [ ] Environment-specific values use `ir.config_parameter`, not hardcodes.
- [ ] Upgrade hooks (if any) are minimal and idempotent.
- [ ] `uninstall_hook` cleans up any non-Odoo state the addon created (external resources, custom DB objects).
- [ ] `pre_init_hook` (if any) does not touch the module's own models (they are not loaded yet).
- [ ] Hot-path log lines are at `_logger.debug`, not `_logger.info`.
- [ ] Any model-level guard on a committed value exempts the legitimate system flows (cancel / unreserve / validate / backorder) that traverse the same code; only the manual path is blocked.

## Required artifacts (the plan must contain these)

1. **Logger discipline statement** — declare that every new Python file uses `_logger = logging.getLogger(__name__)` and `_logger.{info,warning,error,debug}` — never `print(...)`.
2. **Cron inventory** — for every `ir.cron`, name the trigger schedule, the `limit=` per batch, the commit cadence between batches, and the error-handling pattern (silent skip / raise / alert via mail). Empty list (no cron) is valid.
3. **External-call inventory** — every HTTP / SMTP / S3 / message-queue call the addon makes, with timeout, retry policy, and where credentials come from (`ir.config_parameter` key). Empty list is valid.
4. **Hook inventory** — declare which of `pre_init_hook` / `post_init_hook` / `uninstall_hook` are used and what each does in one sentence. For `post_init_hook`, state how it stays idempotent: it runs on every install, including a reinstall after an uninstall, and never on `-u`; a one-time flag needs the `uninstall_hook` to delete it. For `pre_init_hook`, confirm it does not touch the module's own models.
5. **Environment-config inventory** — every `ir.config_parameter` key the addon reads, with the UI path the admin uses to set it and the fallback / default behaviour.
6. **Uninstall cleanup checklist** — for every non-Odoo resource the addon creates (S3 buckets, external webhooks, third-party records, custom DB objects), name the cleanup step in `uninstall_hook`. Empty list is valid if the addon is Odoo-only.
