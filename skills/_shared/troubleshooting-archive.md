# Odoo addon implementation — Troubleshooting Archive

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

---

# Retired 2026-08-12 — workstation-only, Odoo.sh is the sole target

These entries described a local multi-version workstation: DB creation/renaming,
IDE and skill-script scaffolding, and homebrew nginx / macOS DNS. On Odoo.sh the
DB is injected, there is no `instances/` tree, and the platform owns the proxy —
none of it is reachable, and several fixes named commands the Guard Hook denies.

## DB / Pre-Flight

### 16. `dropdb: database "X" is being accessed by other users`
Applies: all versions. Status: active. Last confirmed: 2026-05-20.
Cause: Odoo's HTTP server or a previous shell session is still connected.
Fix: `REVOKE CONNECT ON DATABASE <db> FROM PUBLIC; SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '<db>';` then retry `dropdb`. Or restart Odoo first.

### 17. New instance's DB doesn't show up in browser DB selector
Applies: all versions. Status: active. Last confirmed: 2026-05-20.
Cause: `dbfilter` in the conf doesn't match the DB name — e.g. `dbfilter = ^19_acme_dev$` won't match `19_acme_dev_staging`.
Fix: Use `dbfilter = ^<version>_<instance>(_.*)?$` so siblings of the same instance are visible too. `_create_instance.py` renders this exact pattern.

### 18. `ALTER ROLE odoo CREATEDB` requires superuser
Applies: all versions. Status: active. Last confirmed: 2026-05-20.
Cause: The Postgres user running the privilege probe doesn't have superuser rights.
Fix: `sudo -u postgres psql -c "ALTER ROLE odoo CREATEDB;"` or have the DBA do it. The skill never attempts this automatically — privilege probe in `_create_instance.py` catches it before `createdb`.

### 19. After renaming a Postgres DB, attachments fail with `FileNotFoundError` on hashed paths
Applies: all versions. Status: active. Last confirmed: 2026-05-20.
Cause: Odoo's filestore is keyed by DB name (`~/Library/Application Support/Odoo/filestore/<db>/` on macOS). `ALTER DATABASE … RENAME TO …` doesn't move the filestore — every `ir.attachment` row's `store_fname` resolves to the old path.
Fix: Rename the filestore dir to match: `mv "$FS/<old>" "$FS/<new>"` after confirming any stub at the new name has only matching content-addressed hashes. Pair SQL rename with filestore rename in the same step.

---

## Tooling (skill scripts / IDE)

### 28. `launch.json` patch produces invalid JSON / corrupts comments
Applies: tooling. Status: active. Last confirmed: 2026-05-20.
Cause: Naive `json.dump`-and-rewrite loses comments and trailing commas; or the array-end finder picks the wrong `]` (inside a nested string).
Fix: Use the patcher in `_create_instance.py` — it strips JSONC only for validation, walks balanced brackets to find the configurations array's end, inserts adjacent to the previous entry, and re-validates the output. On failure: SKIP, no rewrite.

### 29. Skill assumes `<instance>/odoo.conf` layout, breaks on a server with a different convention
Applies: tooling. Status: active. Last confirmed: 2026-05-20.
Cause: Hard-coded canonical layout in agent actions.
Fix: Always run `_detect_environment.py` first. If a sibling instance exists, mirror its `conf_filename` / `custom_addons_dirname` / `dbfilter_pattern`. If nothing exists, propose the canonical layout and get user approval before writing.

### 30. Skill prints IDE setup instructions on a headless server
Applies: tooling. Status: active. Last confirmed: 2026-05-20.
Cause: Old behaviour fell back to a template even when no IDE was detected.
Fix: Detection is by file presence (`.vscode/`, `.cursor/`, `.idea/`, `*.code-workspace`). If nothing found, skip the IDE step silently — no template, no instructions.

### 32. Detector returns no instances after the layout migration
Applies: tooling. Status: active. Last confirmed: 2026-05-20.
Cause: As of 2026-05-08 the convention is `<repo>/instances/<name>/` instead of `<repo>/<name>/`. `_detect_environment.py` only scans under `instances/`.
Fix: `mkdir -p instances && mv <name> instances/<name>` then update the conf's addons_path tail and any IDE `launch.json` `--config` arg. DBs/filestores aren't affected (keyed by DB name, not path).

Applies: tooling. Status: active. Last confirmed: 2026-06-13.
Cause: The CLI translation-export option is not exposed in this build's `odoo-bin` (the option parser rejects `--i18n-export=` outright with exit 2), so the documented one-liner to generate `i18n/<module>.pot` fails.
Fix: Export via the `base.language.export` wizard in `odoo-bin shell` instead: create one with `format='po'`, `modules=[(6,0,[mod.id])]`, call `act_getfile()`, then `base64.b64decode(exp.data)` and write to the addon's `i18n/<module>.pot`. Leave `lang` blank for a POT template.

---

## nginx / macOS env

### 33. nginx returns 502 Bad Gateway on a freshly-scaffolded instance even though upstream is healthy
Applies: tooling, macOS + homebrew nginx. Status: active. Last confirmed: 2026-05-20.
Cause: nginx master (running as root) creates the missing `odoo_<instance>.{access,error}.log` as `root:wheel` 644 on first reload. `nginx -t` validates as the worker user (`nobody`), which can't write to root-owned 644 logs → `nginx -t` fails. `setup_nginx_sudo.sh` aborts AFTER `/etc/hosts` was edited but BEFORE reload — nginx keeps serving 1d+ old config and returns 502 for unknown server_names.
Fix: `write_nginx_config()` now pre-touches the log files as the invoking user. Repair an existing case: `sudo chown "$USER":admin /opt/homebrew/var/log/nginx/odoo_<instance>.{access,error}.log && sudo nginx -s reload`. Diagnostic: compare nginx master etime vs conf mtime; if master is older, reload was the missing step.

### 34. `<instance>.local` URLs stall ~5s on macOS before resolving
Applies: macOS. Status: active. Last confirmed: 2026-05-20.
Cause: macOS reserves `.local` for mDNS/Bonjour. Every `*.local` lookup is sent to mDNS first; only after the 5s mDNS timeout does the resolver fall back to `/etc/hosts`.
Fix: Use a reserved, mDNS-free dev TLD. This repo uses `.internal` (ICANN-reserved for private use since 2024); `.test` (RFC 6761) is an equally valid alternative. Both skip the mDNS hook and resolve instantly from `hosts(5)`. Do NOT use a real public gTLD (`.run`, `.dev`, `.app`) — those are registrable and leak unlisted lookups to public DNS. `_create_instance.py` writes `.internal` URLs into `odoo.conf` and `nginx.conf` from the start.

### 48. Downloads from `<host>.internal` hang in browser queue (Chrome/Arc `.crdownload` placeholder never finalizes)
Applies: tooling, macOS + homebrew nginx + Chromium-based browsers (Arc especially). Status: active. Last confirmed: 2026-05-23.
Cause: Chromium browsers (Arc more aggressively than vanilla Chrome) treat `http://*.internal` as an untrusted insecure origin — `localhost` has an explicit secure-context carve-out but a custom dev TLD doesn't (the same applies to `.test` or any non-localhost host). For downloads from insecure origins the browser holds the `.crdownload` placeholder waiting for additional end-of-stream signals beyond `Content-Length`. Arc's download tray will silently hang indefinitely; vanilla Chrome shows a warning chip. Surface-level nginx tweaks (`proxy_buffering off`, `keepalive_timeout 0`, etc.) either make it worse (Content-Length framing breaks → 216-byte truncation, or premature stream close) or have no effect.
Fix: switch instance URLs to HTTPS. `brew install mkcert && mkcert -install` once (adds local CA to macOS keychain, auto-trusted by Arc/Chrome/Safari). Generate `.nginx/certs/instances.internal.pem` covering every `<host>.internal` SAN, then each `<version_folder>/instances/<name>/nginx.conf` has a 301-redirect server on `:80` + a real `listen 443 ssl;` server with the cert paths. `_create_instance.py` does this end-to-end for new instances (regenerating the shared cert with all hostnames each scaffold). Keep the standard `proxy_http_version 1.1; proxy_set_header Connection "";` on `location /`. Temporary workaround if HTTPS isn't set up yet: use Safari, or access via `http://localhost:<http_port>/` (localhost is a secure context).

### 63. Discuss shows "Real-time connection lost…" — nginx routes /websocket to an unbound longpolling/gevent port
Applies: Odoo 16+ (websocket bus), any reverse-proxied single-process instance. Status: active. Last confirmed: 2026-06-15.
Cause: The bus/Discuss WebSocket (`/websocket`) only binds a *separate* gevent port in MULTI-worker mode (`workers >= 1`). A dev instance with `workers` unset (= 0, threaded) serves the WebSocket on the MAIN `http_port`. If the nginx `*_chat` upstream points at a dedicated port (the old `longpolling_port`, e.g. 8073), nothing listens there → every handshake is refused → the Discuss client loops "real-time connection lost, trying to reconnect." Regular pages work because `location /` points at the live http port. Compounded by `longpolling_port`/`xmlrpc_port` being unknown options in v19 (ignored), so a stale conf value silently mislead the nginx template.
Fix: point the nginx `/websocket` (and legacy `/longpolling`) upstream at the SAME `127.0.0.1:<http_port>` for single-process instances; keep the `Upgrade`/`Connection: upgrade` headers on the `/websocket` block. `_create_instance.py` now generates this (chat upstream = http port). Only split to a separate port if you actually run `workers >= 1` — then set `gevent_port` in the conf and route `/websocket` to it. Verify: `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:<http_port>/websocket` returns `400` (alive, wants upgrade); a refused connection on the chat port confirms the mismatch.

---
