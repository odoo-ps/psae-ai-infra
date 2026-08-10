# Pre-Flight: Instance, Database, Dependencies

Detailed pre-flight procedures for the `odoo-plan-development` skill — Section A (instance + DB scaffold) and Section B (dependencies + required configuration). Referenced from [SKILL.md](../SKILL.md). Authorised by user `ExitPlanMode` approval; all destructive actions are gated on that confirmation per principle #4.

This file is loaded on demand when Q0 confirms `architecture: local` and a fresh instance is named, or when dependency/config resolution kicks in after the role walkthrough. It is not loaded for the `odoo.sh` / `docker` / `bare_metal` branches — those run from [architecture_branches.md](architecture_branches.md).

---

## A. Instance + DB scaffold (only if fixed-question 1 named a fresh instance)

When the user names an instance that doesn't yet exist as a folder, scaffold a complete, self-contained working environment for it before going further. Instructions are explicit and don't reference any other instance — they remain correct even if all current instances are deleted.

### A.0 Environment detection (run first)

Before assuming any layout, run [`scripts/_detect_environment.py`](scripts/_detect_environment.py). It emits a JSON report with:

- **Version folders** — `versions[]`, one per `v<major>/` stack (v19, v20, …), each with its `major`, real `release_version`, and per-version `odoo_bin` / `venv` / `enterprise` paths. This is the source of truth for *which version a path routes to*. Every entry in **Existing instances** is tagged with the `version` folder it lives in.
- **IDEs present** — `.vscode/launch.json`, `.cursor/launch.json`, `.idea/`, `*.code-workspace`. Detection is by file presence; if nothing is found, **skip the IDE step entirely** — no fallback templates printed.
- **Existing instances** — sibling folders with an `odoo.conf` and the layout they imply (conf filename, `custom_addons` dirname, `dbfilter` shape, ports in use).
- **Inferred convention** — the most-recent existing instance's layout, ready to mirror. If no sibling instances exist, the inference is empty and the agent must propose the canonical layout (Section A.2 below) and ask the user whether to proceed or adjust.
- **Python venv** — preferred location if found.
- **Postgres** — `psql`/`createdb` on PATH and reachable.
- **nginx** — first matching include dir from the candidate list (`/opt/homebrew/etc/nginx/servers`, `/usr/local/etc/nginx/servers`, `/etc/nginx/conf.d`, `/etc/nginx/sites-enabled`) plus the corresponding log dir, plus whether the `nginx` binary is on PATH. Drives whether A.11 (reverse-proxy scaffold) runs or is skipped. If the report shows `nginx.available = false`, A.11 is silently skipped and `proxy_mode = True` is still written into the conf (so a future manual setup just works).
- **mkcert** — `_create_instance.py`'s `regenerate_instances_cert()` checks for `mkcert` on PATH when scaffolding nginx. If present, it regenerates `.nginx/certs/instances.internal.pem` covering every `<host>.internal` SAN, signed by the user's local CA (one-time `mkcert -install` puts the CA in the macOS keychain). If `mkcert` is missing, the script warns and emits the HTTPS nginx config anyway — the user can install mkcert and re-run separately. Required because `http://*.internal` URLs hit a Chromium insecure-origin trap (troubleshooting #48) that breaks downloads.

Behaviour rules:
- **Target version** → the `v<major>/` folder every path routes to (`<version_folder>` throughout this section). For an **existing** instance it is fixed by `instances[].version`. For a **new** instance it is SKILL.md Q2: auto-selected when only one version folder exists, otherwise asked (newest recommended). Pass the major to `_create_instance.py --version <major>`.
- **Convention exists** → mirror it (`conf_filename`, `custom_addons_dirname`, `dbfilter_pattern`).
- **No convention** → present the canonical layout in the user-confirmation block and ask explicitly: "no existing instance to mirror — use canonical, or describe your own layout?" Only proceed on a clear answer.
- **Server / headless** (no IDE files, no instances) → skip IDE step; otherwise proceed normally with the canonical layout (after user confirms).

The detector is read-only; nothing is created until A.6 confirmation passes.

### A.1 Folder structure to create

Every instance lives under `<repo_root>/<version_folder>/instances/<name>/`, where `<version_folder>` is the target version's folder (`v19`, `v20`, …) resolved in A.0. The skill creates the `<version_folder>/instances/` parent automatically when scaffolding the first instance for that version.

```
<version_folder>/instances/          # e.g. v19/instances/
└── <instance>/
    ├── custom_addons/
    │   └── .gitkeep
    └── odoo.conf
```

### A.2 `<version_folder>/instances/<instance>/odoo.conf` template

Render the following, substituting placeholders:

```ini
[options]
; --- Security ---
admin_passwd = {{ pbkdf2_sha512_hash_of_random_24_char_password }}

; --- Database Settings ---
db_host = localhost
db_port = 5432
db_user = odoo
dbfilter = ^{{ version }}_{{ instance }}(_.*)?$

; --- Network Settings ---
; Single-process dev (workers=0): Discuss WebSocket rides http_port; nginx proxies /websocket here.
http_port = {{ http_port }}

; --- Addons Paths ---
addons_path =
    {{ repo_root }}/v{{ version }}/odoo/odoo/addons,
    {{ repo_root }}/v{{ version }}/odoo/addons,
    {{ repo_root }}/v{{ version }}/enterprise,
    {{ repo_root }}/v{{ version }}/instances/{{ instance }}/custom_addons
```

Placeholder rules:
- `{{ version }}` — major Odoo version (e.g. `19`); the on-disk stack is the matching `v{{ version }}/` folder (so `v19/`, `v20/`). Both are settled in A.0.
- `{{ instance }}` — must match `^[a-z][a-z0-9_]*$` (valid Postgres identifier).
- `{{ http_port }}` — first free from `8069, 8019, 8029, 8039, …` not used in any sibling `*/odoo.conf`. The WebSocket rides this same port in single-process mode — no separate longpolling/gevent port is allocated.
- `{{ pbkdf2_sha512_hash }}` — `passlib.hash.pbkdf2_sha512.using(rounds=600000).hash(<plain>)` over a 24-char URL-safe random password. Show the plaintext to the user **once** in the confirmation block; never log it elsewhere.
- `{{ repo_root }}` — absolute path containing the version folders (`v19/`, `v20/`, …) and `skills/`. Determined dynamically; never hardcoded.

### A.3 DB naming

`<db> = <version>_<instance>` (lowercase). Example: `19_acme_dev`.

### A.4 DB creation — two explicit steps

```bash
createdb -h localhost -p 5432 -U odoo <db>
./<version_folder>/odoo/.venv/bin/python ./<version_folder>/odoo/odoo-bin \
    -c <version_folder>/instances/<instance>/odoo.conf -d <db> \
    --no-http --stop-after-init -i base --without-demo=all
```

If step 2 fails: `dropdb -h localhost -p 5432 -U odoo <db>` to leave nothing partial, then surface the traceback.

### A.5 Privilege probe (run before A.4)

```bash
psql -h localhost -p 5432 -U odoo -tAc \
    "SELECT rolcreatedb FROM pg_roles WHERE rolname='odoo';"
```

Expected output: `t`. If `f` or empty, halt and surface the SQL the DBA must run as a Postgres superuser:

```sql
ALTER ROLE odoo CREATEDB;
```

### A.6 User confirmation gate (mandatory, per principle #4)

Before running anything in A.1–A.4 (and the IDE patch in A.10, and the nginx scaffold in A.11), present this block:

```
About to create new instance:
  Folder            <repo_root>/<version_folder>/instances/<instance>/
  Conf              <repo_root>/<version_folder>/instances/<instance>/<conf_filename>
  Custom addons dir <repo_root>/<version_folder>/instances/<instance>/<custom_addons_dirname>/
  Ports             http=<http_port>  (WebSocket on same port; single-process)
  DB filter         <dbfilter_pattern resolved>
  DB to create      <db>  (initialised with -i base --without-demo=all)
  Admin pwd         <plaintext>  (also stored in conf as pbkdf2-sha512 hash)
  Convention        mirror <existing_instance>  |  canonical (no sibling found)
  IDE patch         (one of)
                    - .vscode/launch.json — add "Odoo <instance> (<version_folder>)" config
                    - .cursor/launch.json — add "Odoo <instance> (<version_folder>)" config
                    - .idea/ detected — print suggested run config (manual)
                    - none detected — skip
  nginx scaffold    (one of)
                    - write <version_folder>/instances/<instance>/nginx.conf (HTTPS on :443,
                      with HTTP→HTTPS 301 redirect on :80)
                      → symlink <include_dir>/odoo_<instance>.conf
                      → pre-touch <log_dir>/odoo_<instance>.{access,error}.log
                      → regenerate .nginx/certs/instances.internal.pem via
                        mkcert with all instance SANs (idempotent)
                      → public URL https://<host>.internal/
                      → user must run sudo ./.nginx/setup_nginx_sudo.sh at the end
                      → first instance only: user must also run mkcert -install
                        once to trust the local CA in macOS keychain
                    - --no-nginx flag → skip (proxy_mode=True still set)
                    - no nginx include dir detected → skip (proxy_mode=True still set)
                    - mkcert not on PATH → nginx config emitted as HTTPS, but
                      cert not regenerated; user must install mkcert + re-run
Proceed? [y/N]
```

Wait for explicit `y`. Anything else → halt.

### A.7 Demo data

Default off (`--without-demo=all`). Enabling demo is an explicit per-instance opt-in (e.g. user runs the skill with a demo flag), not a fixed question.

### A.8 Canonical validation DB

After A.4 succeeds, treat `<db>` as the default answer to fixed question 6. User may still override.

### A.9 Idempotency

If the instance folder already exists, do NOT overwrite the conf or recreate the DB. Skip A.1–A.4 and proceed to addon scaffolding. If the user wants a clean slate, they delete the folder + drop the DB manually — destructive enough that the skill won't do them automatically.

The IDE patch in A.10 is independently idempotent: re-running it with the same instance name detects an existing `Odoo <instance> (<version_folder>)` configuration and skips.

### A.10 IDE configuration patches (only if A.0 detected an IDE)

Triggered automatically by `_create_instance.py --write` when an IDE config was detected.

- **`.vscode/launch.json` and `.cursor/launch.json`** — auto-patched. The patcher uses a JSONC-tolerant in-place edit:
  - Strips `// …` and `/* … */` comments + trailing commas only for parsing/validation.
  - Locates the `configurations` array textually and inserts a new entry adjacent to the closing `}` of the previous entry.
  - Original comments and formatting outside the inserted block are preserved.
  - Skips if a configuration with the name `Odoo <instance> (<version_folder>)` already exists.
  - Validates the patched output still parses as JSONC; on validation failure, the original file is left untouched and a clear error is reported.

  The new configuration uses:
  ```json
  {
    "name": "Odoo <instance> (<version_folder>)",
    "type": "python",
    "request": "launch",
    "program": "${workspaceFolder}/<version_folder>/odoo/odoo-bin",
    "console": "integratedTerminal",
    "args": ["--config", "${workspaceFolder}/<version_folder>/instances/<instance>/<conf_filename>",
             "--limit-time-real", "9999", "--dev=all"],
    "justMyCode": false,
    "cwd": "${workspaceFolder}",
    "env": {"PYTHONUNBUFFERED": "1"},
    "python": "${workspaceFolder}/<version_folder>/odoo/.venv/bin/python"   // only if venv detected
  }
  ```

- **`.idea/` (JetBrains)** — NOT auto-patched. The XML run-config format is too easy to corrupt with naive edits. Instead, the script prints a ready-to-paste run config (Name, Script, Args, Interpreter) for the user to add manually.

- **No IDE detected** → skip silently. No "fallback" template is printed. The user can add a launch config later if they install an IDE.

A reference Python helper that prints the plan and (with `--write`) creates folder + conf and patches IDE configs is at [`scripts/_create_instance.py`](scripts/_create_instance.py).

### A.11 nginx reverse-proxy scaffold (only if an nginx servers dir is detected)

Triggered automatically by `_create_instance.py --write` when an nginx include dir is found. Goal: each instance is reachable at `https://<host>.internal/` instead of `http://localhost:<port>/`, which removes port-collision confusion, lets developers bookmark stable URLs across instance creates/drops, AND avoids Chromium-based browsers (Arc especially) holding downloads in `.crdownload` purgatory because `http://*.internal` is treated as an insecure origin (see troubleshooting #48).

**`<host>` is version-qualified — it is the instance's DB name** (`<major>_<instance>`, i.e. the `dbfilter` core). A v19 `ai_test` serves at `https://19_ai_test.internal/` and a v20 `ai_test` at `https://20_ai_test.internal/` — the two coexist, never colliding on hostname, vhost symlink (`odoo_<host>.conf`), upstream name, or log file. A legacy folder that already embeds its version (e.g. `19_keeper`, DB `19_keeper`) stays `19_keeper.internal` — host is the DB name, not a mechanical `v<major>`+folder concat. `_create_instance.py` derives `<host>` for you (`instance_host()`); never hand-build it.

**Why `.internal` and not `.local`:** macOS reserves `.local` for Multicast DNS / Bonjour. Even with `/etc/hosts` entries in place, every `.local` lookup blocks ~5 s waiting for mDNS to time out before the resolver falls back to `hosts(5)`. `.internal` is ICANN-reserved for private use (2024), has no mDNS hook, never resolves publicly, and resolves instantly from `/etc/hosts`. (`.test`, RFC 6761, is an equally valid reserved alternative; avoid real gTLDs like `.run`/`.dev` — registrable and leak to public DNS.)

**Why HTTPS (not just HTTP):** `localhost` is a Chromium secure-context carve-out — downloads, service workers, and many other browser APIs work cleanly there. `.internal` does NOT inherit that carve-out: HTTP downloads from `http://<host>.internal` get held silently by Chrome/Arc. The fix is to serve every instance over HTTPS using a mkcert-issued local cert. mkcert installs a per-user root CA into the macOS keychain (one-time `mkcert -install`) and that CA signs the per-repo wildcard-style cert in `.nginx/certs/instances.internal.pem`. Browsers trust it automatically; curl needs `-k` (or `--cacert "$(mkcert -CAROOT)/rootCA.pem"`) for local-CA awareness.

Detection probes these dirs in order, first match wins:
- `/opt/homebrew/etc/nginx/servers/` (macOS Apple Silicon, brew)
- `/usr/local/etc/nginx/servers/` (macOS Intel, brew)
- `/etc/nginx/conf.d/` (RHEL/CentOS apt yum)
- `/etc/nginx/sites-enabled/` (Debian/Ubuntu)

If none exist → skip silently and the conf still gets `proxy_mode = True` so a manual setup later "just works".

Per-instance scaffold:
- `<version_folder>/instances/<name>/nginx.conf` — the source of truth (version-controlled, instance-co-located). Contains TWO server blocks:
  - 301-redirect server on `:80` → forwards to `https://<host>$request_uri`
  - Real `listen 443 ssl;` server with `ssl_certificate` + `ssl_certificate_key` pointing at the shared cert under `.nginx/certs/`
- Symlink `<servers_dir>/odoo_<name>.conf` → the conf above.
- Reverse-proxies `https://<host>.internal/` to `127.0.0.1:<http_port>`, with `/websocket` (and the legacy `/longpolling`) routed to the **same** `127.0.0.1:<http_port>` — single-process instances serve the bus WebSocket on the main port (no separate gevent port is bound when `workers = 0`; routing the WebSocket to an unbound port is what produces Discuss's *"real-time connection lost"* — see [troubleshooting.md](troubleshooting.md) #63). Sets `X-Forwarded-Host`, `X-Forwarded-For`, `X-Forwarded-Proto`, `X-Real-IP`; the `/websocket` block adds the `Upgrade`/`Connection: upgrade` headers. Long timeouts (720s) for module install.
- Static-asset caching on `/web/static/`.
- Per-instance access + error logs under the platform's nginx log dir. **Pre-touched as the invoking user** at scaffold time so the first `sudo nginx -s reload` doesn't create them as `root:wheel` (which would silently break the next `nginx -t` — see [troubleshooting.md](troubleshooting.md) #33, "nginx returns 502 on a freshly-scaffolded instance").

Shared cert (`.nginx/certs/instances.internal.pem` + `-key.pem`):
- Generated by `_create_instance.py`'s `regenerate_instances_cert()` helper — runs `mkcert` with the union of every `<host>.internal` hostname currently under `<version_folder>/instances/` as the SAN list. Idempotent: same set → same cert.
- The helper runs automatically each time a new instance is scaffolded, so adding an instance updates the shared cert to cover it.
- If `mkcert` isn't on PATH, the helper warns but doesn't fail — the user can `brew install mkcert && mkcert -install` and re-run the script to populate the cert.

Always-applied conf change (regardless of nginx detection):
- `proxy_mode = True` is set in the rendered `odoo.conf`.
- A `# Public URL: https://<host>.internal/` comment is included near the top.

The two sudo steps the script will NEVER run automatically (port 80/443 bind + `/etc/hosts` write both need root). Prefer the repo's helper if present, otherwise inline:

```bash
# Preferred — auto-discovers every instance under ./v*/instances/, repairs any
# root-owned log files left over from past sudo runs, then validates + reloads.
# Idempotent.
sudo ./.nginx/setup_nginx_sudo.sh

# Fallback if .nginx/setup_nginx_sudo.sh is not in the repo:
echo '127.0.0.1   <host>.internal' | sudo tee -a /etc/hosts
sudo brew services restart nginx        # macOS/brew
# OR Linux:  sudo systemctl reload nginx
```

**Final-ask requirement.** When (and only when) the nginx scaffold in this section actually ran for the new instance, the *last* thing the skill says to the user — after Stage 3 and the documentation step — must be a single, unmissable ask to run the sudo step above. Without it, `https://<host>.internal/` silently fails to resolve and the user discovers it cold the next time they open the URL. If this is the FIRST instance ever scaffolded in this repo, the final ask must also include `mkcert -install` (the user-side one-time CA trust step). Skip the final ask if nginx scaffolding was skipped (`--no-nginx`, no nginx dir detected, or `proxy_mode` only).

Verification (after the user runs the sudo step):
```bash
curl -kI https://<host>.internal/web/login
```
(`-k` skips local-CA verification at curl level. In the browser the cert is trusted automatically once `mkcert -install` has been run.)

Skip entirely with `--no-nginx` for headless / server / containerised setups.

---

## B. Dependencies and Environment

A bare `depends = ["sale_stock"]` is not enough — the addon also needs Odoo's *functional configuration* (feature groups, settings toggles) to be in the right state for its workflow to actually run. Section B has two sub-tracks: **B.1 module dependencies** (what goes in the manifest's `depends`) and **B.2 required configuration** (what must be enabled in the running DB). Both must be resolved *and applied* before Stage 2.

### B.1 Module dependencies

- Confirm Python virtualenv (`<version_folder>/odoo/.venv/bin/python` if present, else system Python with deps).
- Resolve `depends` for the new addon: every model used must be backed by a declared module dep. Walk `ir.model.data` for `ir.model` external IDs (same resolver pattern as `odoo-spreadsheet-report`). Include transitive-feeling deps explicitly when the addon actually uses their fields/views (e.g. don't depend on `sale_stock` alone if you also xpath a `sale.order` view — depend on both `sale` and `sale_stock` so the depends graph documents intent).
- Detect Odoo runtime version from `<version_folder>/odoo/odoo/release.py` and align manifest `version` to it (`<odoo_major>.<addon_major>.<addon_minor>.<patch>`).
- **List every resolved dep in the plan file** under a `Dependencies` heading with one line each: `<module> — <why this addon needs it>`. The user sees the full list at `ExitPlanMode` approval; missing deps are caught there, not at Stage 2 failure.
- **Before Stage 2, verify each dep is installed** in the validation DB:
  ```bash
  psql -h localhost -p 5432 -U odoo -d <db> -tAc \
    "SELECT name FROM ir_module_module WHERE name = ANY(ARRAY['<dep1>','<dep2>',...]) AND state='installed';"
  ```
  Any missing → install them with a single `-i <dep1>,<dep2>,…` run *before* installing the new addon. Don't rely on Odoo's auto-install-of-deps to mask a malformed `depends` list; install them explicitly so a missing entry surfaces as a clear "module not found" instead of a runtime model lookup error.
- Confirm with user before installing any new dependency module (per principle #4).

### B.2 Required configuration (feature groups & settings)

Many Odoo workflows are gated by **feature groups** activated through `res.config.settings` — they're not module deps, so they don't appear in `depends`, but the addon is non-functional without them. Examples:

| Functionality the addon uses             | Required group / setting                                    |
|------------------------------------------|-------------------------------------------------------------|
| Lot / serial number fields on stock moves| `stock.group_production_lot` ("Lots & Serial Numbers")      |
| Multi-step routes on warehouses          | `stock.group_adv_location`                                  |
| Variants on `product.template`           | `product.group_product_variant`                             |
| Pricelists                               | `product.group_product_pricelist`                           |
| Analytic accounts                        | `analytic.group_analytic_accounting`                        |
| UoM on product / move lines              | `uom.group_uom`                                             |
| Multi-currency on `account.move`         | `base.group_multi_currency`                                 |
| Multi-company                            | `base.group_multi_company`                                  |
| Discounts on sale order lines            | `product.group_discount_per_so_line`                        |
| Sub-tasks on `project.task`              | `project.group_subtask_project`                             |
| Skills on HR employees                   | `hr_skills` (full addon, not a group)                       |

This table is non-exhaustive; the addon-specific list is the **Solution Architect's** responsibility (technical surface: which fields/views need unlocking) and the **Business Analyst's** responsibility (functional surface: which workflow steps are gated by which setting). Both roles must include config toggles in their findings.

**Process:**

1. While planning, list every required group / setting in the plan file under a `Required configuration` heading: `<group_xml_id> — <why>` and the UI path that toggles it (e.g. "Inventory → Configuration → Settings → Traceability → Lots & Serial Numbers"). The user sees this at `ExitPlanMode` approval.
2. **Before Stage 2, verify each group is enabled** in the validation DB:
   ```bash
   ./<version_folder>/odoo/.venv/bin/python ./<version_folder>/odoo/odoo-bin shell \
     -c <version_folder>/instances/<instance>/odoo.conf -d <db> --no-http --stop-after-init <<'PY'
   for xmlid in ['stock.group_production_lot', ...]:
       grp = env.ref(xmlid, raise_if_not_found=False)
       print(xmlid, 'ENABLED' if grp and env.ref('base.group_user') in grp.implied_ids or grp in env.user.groups_id else 'OFF')
   PY
   ```
   For any `OFF`, decide which mechanism is appropriate:
   - **Addon owns the toggle** — add a `post_init_hook` that does `env.ref('base.group_user').implied_ids = [(4, env.ref('<xml_id>').id)]` (or sets the equivalent `res.config.settings` field). Use this when the addon *requires* the feature to function.
   - **Operator-managed toggle** — document in `<addon>/doc/user_manual.md` and `<addon>/doc/testing_manual.md` that the operator must enable it via the Settings UI before installing the addon. Use this when the addon is enhanced by the feature but optional administrators may legitimately want it off (rare).
3. If the addon's `post_init_hook` enables groups, that hook **must** also be tested in Stage 3 smoke — verify `env.ref('<xml_id>') in env.user.groups_id` after install. A silently broken hook is the failure mode in troubleshooting #8 ("Addon installs but a core field/menu is invisible — required feature group never enabled") and the reason this section exists.

**Anti-pattern this section prevents** (logged as troubleshooting #8): planning a `sale_stock` addon that depends on lot tracking, declaring `depends = ['sale_stock']`, passing Stage 1 + Stage 2, then discovering at Stage 3 (or worse, when the user clicks around) that the lot field on the move line is invisible because `stock.group_production_lot` was never enabled in the fresh validation DB. The addon "installs" but does nothing.
