# Architecture branches

Non-Local execution paths for the `odoo-plan-development` skill. Referenced from [SKILL.md](../SKILL.md) and routed to by Q0's architecture detection (per principle #13).

Load only the branch that matches Q0's confirmed architecture:
- [`odoo.sh`](#odoosh-branch) — Odoo-managed cloud platform; no local Odoo runtime
- [`docker`](#docker-branch-safety-net) — containerised; deployment specifics vary
- [`bare_metal`](#bare-metal-branch-safety-net) — system-installed Odoo; deployment specifics vary

The `local` branch lives in [SKILL.md](../SKILL.md) and [pre_flight.md](pre_flight.md) — not here.

---

## Odoo.sh branch

Runs when Q0 confirmed `architecture: odoo.sh`. Odoo.sh manages the instance lifecycle, the database, and the runtime — so Pre-Flight A (instance + DB scaffold), nginx, IDE patches, and local `odoo-bin` calls **do not apply**. The skill's job here is to scaffold the addon at the repo root, push to a dev branch, and verify the deploy.

### Pre-Flight differences

- **Skip Pre-Flight A entirely** (no `_create_instance.py`, no `createdb`, no IDE patch, no nginx scaffold). The Odoo.sh project already exists; the user has access to its dashboard.
- **Pre-Flight B (dependencies + required configuration) still applies** with two adjustments:
  - Python deps go into `requirements.txt` at the **repo root** (not a local venv).
  - Module dep verification uses the Odoo.sh staging shell (Odoo.sh dashboard → branch → Shell), not local `psql`.

### Fixed Questions adjustments

- **Q1 (instance)** → **skipped, not asked.** The skill operates on whichever branch the invocation happened on — detect via `git branch --show-current` (or `git rev-parse --abbrev-ref HEAD`) and surface under the plan's `Architecture` heading. Per principle #12, listing remote branches and asking "which one?" is friction without value: the developer is already checked out on the branch they want, and a wrong inference is obvious to them at `ExitPlanMode` (where they can override). Record the detected branch in the `Assumptions` section so the override path stays explicit. Never push to or modify any branch other than the current checkout.
- **Q2 (Odoo version)** → read from `.odoo.sh.yaml` (`odoo_version` key) or the project's runtime version visible in the dashboard. User confirms; never assume.
- **Q3 (new vs update)** → list existing addons at the **repo root** (siblings of `.odoo.sh.yaml`), not under `instances/<name>/custom_addons/`.
- **Q4 / Q5** (business need, solution brief) → unchanged; architecture-independent.
- **Q6 (validation DB)** → resolved from the project's dev/staging DB name (Odoo.sh provisions it; visible in the dashboard). User can override.

### Addon scaffold path

`<repo_root>/<module_name>/` (at the repo root, sibling of `.odoo.sh.yaml` and `requirements.txt`). NOT `instances/<name>/custom_addons/<module_name>/` — that path doesn't exist on Odoo.sh's addons_path.

### Validation stages

- **Stage 1 — Static lint** ([`scripts/_lint_addon.py`](scripts/_lint_addon.py)) — runs unchanged, pointed at the repo-root addon path.
- **Stage 2 — Install via deploy**: `git push origin <dev-branch>` triggers an Odoo.sh build. Watch the build via the project dashboard (Builds tab) or the Odoo.sh API. Fail the stage if the build exits non-zero, times out, or surfaces module-load errors in the build log.
  - **Confirm-before-push per principle #4** — a push to Odoo.sh is destructive (triggers a deploy, mutates the staging DB, can break the branch URL). Present the dev-branch name, the commit message, and the expected build duration; wait for explicit `y`.
  - Do NOT run local `odoo-bin -i` — there's no local Odoo runtime to install into.
- **Stage 3 — Operational smoke**: hit the dev branch's public URL (typically `https://<branch>-<project>-<hash>.dev.odoo.com/`), log in as the admin user, click through the new menu / view / workflow. Same smoke checklist as Local Stage 3 (module installed, models searchable, menus resolve, sample record CRUD, ACLs enforced) — just remote, via the browser, not via `odoo-bin shell`.

### What explicitly does NOT apply on Odoo.sh

- nginx reverse-proxy scaffold (Odoo.sh provides its own ingress).
- IDE launch.json patches (the user's IDE doesn't run Odoo locally for this project).
- `createdb` / `dropdb` (DB lifecycle is managed by the platform).
- The two-step DB-naming convention (`<version>_<instance>`) — Odoo.sh names its own DBs.
- Local `odoo-bin shell` for Stage 3 smoke — use the Odoo.sh shell from the dashboard if shell-level access is needed, or rely on browser-side click-through.

---

## Docker branch (safety net)

Runs when Q0 confirmed `architecture: docker`. Follows the [safety-net handoff pattern in P13](../../_shared/principles.md). Skill-specific questions for step 2:

- "Where do your custom addons live in the repo? (e.g. mounted volume path, repo-root subdir)"
- "How do you invoke `odoo-bin`? (e.g. `docker compose exec odoo odoo-bin ...`)"
- "Where is `odoo.conf` mounted from? (host path → container path)"
- "Which container/service runs Postgres, and how do you reach it from the Odoo container?"
- "How do you typically install / upgrade modules? (compose restart, exec into the container, rebuild image?)"

---

## Bare-metal branch (safety net)

Runs when Q0 confirmed `architecture: bare_metal`. Follows the [safety-net handoff pattern in P13](../../_shared/principles.md). Skill-specific questions for step 2:

- "Where do custom addons live? (e.g. `/opt/odoo/addons/`, `/usr/lib/python3/dist-packages/odoo/addons/`)"
- "Which `odoo-bin` path do you use? Which Python interpreter?"
- "Where is `odoo.conf`? Which DB does it target?"
- "How do you restart Odoo? (`sudo systemctl restart odoo`, supervisor, custom init?)"
