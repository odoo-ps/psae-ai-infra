# Architecture branches

Non-Local execution paths for the `odoo-spreadsheet-report` skill. Referenced from [SKILL.md](../SKILL.md) and routed to by Q0's architecture detection (per principle #13).

Load only the branch that matches Q0's confirmed architecture:
- [`odoo.sh`](#odoosh-branch)
- [`docker`](#docker-branch-safety-net)
- [`bare_metal`](#bare-metal-branch-safety-net)

The `local` branch lives in [SKILL.md](../SKILL.md) — not here.

---

## Odoo.sh branch

Runs when Q0 confirmed `architecture: odoo.sh`. The skill still produces a `.osheet.json` via a Python builder — but the builder lives at the repo root (Odoo.sh has no `instances/` concept), and the JSON is imported via the Odoo.sh UI or the Odoo.sh shell, not a local `odoo-bin shell`.

### Output Contract differences (vs Local branch)

- **Builder path**: `<repo_root>/spreadsheet_reports/_build_<report_slug>.py` (repo root, sibling of `.odoo.sh.yaml`). NOT `<version_folder>/instances/<inst>/spreadsheet_reports/...`.
- **Generated JSON path**: `<repo_root>/spreadsheet_reports/<report_slug>.osheet.json`.
- **Validation script**: `<repo_root>/spreadsheet_reports/_validate_import.py` (same shape as Local, but invoked via the Odoo.sh shell — see Stage 2 below).
- **Docs**: `<repo_root>/spreadsheet_reports/doc/<report_slug>.md`.

### Fixed Questions adjustments

- **Q1 (instance)** → **skipped, not asked.** The skill operates on whichever branch the invocation happened on — detect via `git branch --show-current` (or `git rev-parse --abbrev-ref HEAD`) and surface under the plan's `Architecture` heading. Per principle #12, asking "which branch?" is friction without value: the developer is already checked out on the branch they want. Record the detected branch in `Assumptions`; user can override at `ExitPlanMode`. The Odoo.sh dev/staging DB tied to that branch is the validation target (Q7); never operate on a different branch's DB.
- **Q2 (Odoo version)** → read from `.odoo.sh.yaml` (`odoo_version` key); confirm with the user.
- **Q5 (data-source models)** → same as Local; resolve owning modules via `ir.model.data` against the Odoo.sh DB (see Stage 2 access path).
- **Q7 (validation DB)** → Odoo.sh's dev/staging DB name tied to the current branch (Q1); user can override via project config.

### Pre-Flight: Required Modules

Module presence check uses the Odoo.sh shell (project dashboard → branch → Shell) instead of local `odoo-bin`. The detection script body and the install command shape are the same; only the invocation host changes.

For modules that need installing: appropriate modules typically ship with Odoo.sh, but custom modules referenced by the report must already be deployed on the branch (push them via `git push` first — that's an `odoo-plan-development` concern, not this skill's).

### Validation (three-stage)

- **Stage 1 — Static JSON verifier**: runs unchanged (`_verify_sheets.py` walks the JSON locally — no Odoo runtime needed).
- **Stage 2 — Server-side import**: two options:
  - **Documents UI upload (recommended for non-developers)** — generated `.osheet.json` is downloaded to the user's machine, then uploaded to the Odoo.sh dev URL via Documents → New → Upload → Open with Odoo Spreadsheet. Validation runs in-browser as Stage 3.
  - **Odoo.sh shell** — open the project's Shell tab (or SSH), upload the JSON via `scp`/`git`/clipboard, run the same `_validate_import.py` against the dev DB. Slower but reproducible from a script.
- **Stage 3 — Browser-side sheet-by-sheet verification**: same checklist as Local — hard refresh, click into every visible sheet, watch for `UncaughtPromiseError`, missing chart data, `#ERROR` cells. Target the dev/staging URL (`https://<branch>-<project>-<hash>.dev.odoo.com/`).

### What explicitly does NOT apply on Odoo.sh

- Local `odoo-bin shell` invocations under `<version_folder>/instances/<inst>/...`.
- Local venv (`<version_folder>/odoo/.venv/bin/python`) — the builder runs with whatever Python the user has locally; only the **import** side touches Odoo.sh.
- The `_validate_import.py` flavor that assumes local config + local DB paths — adapt the script's `--conf` / `--db` arguments to whatever the user supplies for the Odoo.sh shell context.

---

## Docker branch (safety net)

Runs when Q0 confirmed `architecture: docker`. Follows the [safety-net handoff pattern in P13](../../_shared/principles.md). Skill-specific questions for step 2:

- "Where should the builder + generated JSON live in your layout?"
- "How do you invoke `odoo-bin shell` against the container? (`docker compose exec <service> odoo-bin shell ...`)"
- "Which DB does that target?"

---

## Bare-metal branch (safety net)

Runs when Q0 confirmed `architecture: bare_metal`. Follows the [safety-net handoff pattern in P13](../../_shared/principles.md). Skill-specific questions for step 2:

- "Where should the builder + JSON live? (e.g. `/opt/odoo/spreadsheet_reports/`, a sibling dir, your home dir?)"
- "Which `odoo-bin` / Python interpreter for the validator?"
- "Which conf + DB for the import target?"
