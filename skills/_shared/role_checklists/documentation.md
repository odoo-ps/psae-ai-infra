# Documentation Expert

*Calibrated against Odoo 19.0. Re-review on each major version bump.*

## Goal
A future developer (or future-you) should be able to understand what the addon does, how to install it, and how to test it within five minutes of cloning the repo.

## Key Questions to Ask the User
- Is there an **established docs convention** in this repo (docs/, README.md, doc/)?
- Should the docs include **screenshots**, or is the addon simple enough to describe in text?
- What's the **target reader** — developer maintaining the code, end user using the UI, or both?
- Will this addon ship to the **Odoo Apps store**? If yes, `<addon>/static/description/index.html` is the storefront card; `__manifest__.py` `description` is the fallback if `index.html` is absent.

## Mechanisms / Tools

### `<addon>/doc/user_manual.md`
Covers what the addon does for the end user. Sections:
- **Purpose** — one paragraph: who uses it, what decision it supports.
- **Primary workflow** — step-by-step, written as imperative ("Open Sales → Quotations → Create. Set the customer. Click Confirm.").
- **Field reference** — only fields whose meaning isn't obvious from the label.
- **Edge cases** — known limits, "what happens if..."
- **Glossary** — domain terms specific to this addon.

### `<addon>/doc/testing_manual.md`
Covers how to install and verify the addon. Sections:
- **Install command** — exact, copy-paste, including conf path and DB name.
- **Upgrade command** — same with `-u`.
- **Run tests** — `odoo-bin -u <addon> --test-enable --test-tags=/<addon> --stop-after-init --no-http`.
- **Manual smoke checklist** — module installed, models searchable, menus resolve, a sample record creates/computes/unlinks, ACLs cover every model.
- **Uninstall command** — including any cleanup the user must do (external resources, custom DB objects).

### `<addon>/__manifest__.py` `description`
A short paragraph at the top of the manifest, surfaced in the Apps list. One sentence per: purpose, primary workflow, target user. **HTML is supported** in this field (renders in the Apps store / on-tenant Apps list); use it sparingly — a short `<p>` + bullet list reads cleanly, anything more is bloat.

### `<addon>/static/description/index.html` (Apps-store card)
When present, overrides the manifest `description` in the Apps store / tenant Apps list with a richer card. Standard structure:
- A hero `<section>` with title + one-line value statement.
- A workflow section (2–4 screenshots illustrating the primary flow).
- A feature-list section (bulleted, max ~8 features).
- Pair with `<addon>/static/description/icon.png` (128×128 PNG, square, transparent background) — the icon Odoo shows in the Apps grid.

### Screenshot conventions
- Capture the **full Odoo chrome** (top app bar, breadcrumb, the form/list itself) so the reader knows *where* they are, not just what they're looking at.
- Use a **clean demo DB** (no half-completed records, no debug-mode UI bleed-through).
- Resize to **1280×800** or similar 16:10 — Odoo's design language assumes wide aspect.
- Store under `<addon>/static/description/` for store / manifest screenshots; under `<addon>/doc/img/` for screenshots embedded in `user_manual.md`.
- Keep the screenshot count low — 4 is the right ballpark, 10+ is doc-bloat. Stale screenshots are worse than no screenshots.

### Code-level
- **Public methods** (no leading underscore) deserve a docstring with: one-line summary, parameter types, return type, raises.
- **Compute methods** explain the formula in plain English in a docstring.
- **Tour tests** include a comment explaining what UI flow they cover (tours are dense and easy to misread).

### Doc shape — four kinds (Diataxis)

The same addon's documentation serves four distinct reader needs. Don't blur them:

- **Tutorial** (`user_manual.md` primary-workflow section) — a hand-held walkthrough for a first-time user, ending in a working result. Imperative voice, no branching, no theory.
- **How-to** (`user_manual.md` field reference / edge cases) — task-oriented, assumes the reader knows what they want and is hunting for the steps.
- **Explanation** (`__manifest__.py` description, `user_manual.md` purpose section) — *why* the addon exists, the problem it solves. Not actionable on its own.
- **Reference** (`user_manual.md` field reference / glossary, public-method docstrings) — exhaustive, dry, lookup-oriented.

A user manual that mixes all four in one section confuses every reader. Keep them sectioned.

### `<addon>/doc/CHANGELOG.md` (for upgrade-type addons)
For any addon already installed in a prior release (shipping a manifest version bump and a migration script), the changelog records what changed between versions. Sections per release:
- **Version** — the manifest version this entry covers (e.g. `19.0.1.3.0`).
- **Date** — release date in ISO format.
- **Schema changes** — fields added / renamed / removed; migration script path.
- **Behaviour changes** — new methods, changed defaults, removed features.
- **Upgrade notes** — anything the operator needs to do beyond `-u <addon>` (set an `ir.config_parameter`, enable a feature group, run a manual cron).

## Common Pitfalls
- **README written for developers but called "user manual"** — confuses the audience. Split into two files.
- **Step-by-step that uses internal field names** ("set `state` to `done`") — end users see UI labels, not field names.
- **Docs that drift** — updated in the first PR, never again. Include a "last verified against version X.Y" line.
- **Screenshots for everything** — they go stale fast. Only screenshot complex UI (multi-tab forms, kanban drag flows).
- **Upgrade-type addon with no changelog** — operators have no way to know what changed between versions. The migration script alone is not documentation; the changelog explains *why*.

## Production-readiness criteria
- [ ] `<addon>/doc/user_manual.md` exists and covers purpose + primary workflow.
- [ ] `<addon>/doc/testing_manual.md` exists with copy-paste install/upgrade/test/uninstall commands.
- [ ] `__manifest__.py` `description` is non-empty and informative.
- [ ] All public methods have a one-line docstring.
- [ ] Documentation has a "last verified against version" line at the top.
- [ ] Upgrade-type addons have `<addon>/doc/CHANGELOG.md` with an entry for the current manifest version.

## Required artifacts (the plan must contain these)

1. **User manual entry** — Output Contract requires `<addon>/doc/user_manual.md`. Declare the file as a deliverable with sections (Purpose / Workflow / Field reference / Edge cases / Glossary).
2. **Testing manual entry** — declare `<addon>/doc/testing_manual.md` as a deliverable. Commands must be copy-paste-ready with the concrete conf path + DB name from this run, not placeholders.
3. **Uninstall path** — the testing manual's uninstall section must name the actual steps. On Odoo.sh uninstalling is done from Apps in the UI (or an ORM shell `module.button_immediate_uninstall()`), plus any external cleanup. Do not document a `-d <db>` command line: it is denied by the Guard Hook, and `-u <addon>` is upgrade, not uninstall.
4. **Manifest description** — declare the one-paragraph description that ships in `__manifest__.py`.
5. **Public method docstring inventory** — list every new public method (no leading underscore) the addon adds. Each gets a one-line docstring before the build is declared done.
6. **Changelog entry** — for any upgrade-type addon, declare the `CHANGELOG.md` entry for the new manifest version. Empty for greenfield first-install addons.
7. **"Last verified against version X.Y"** — both user_manual.md and testing_manual.md carry this line near the top, naming the Odoo version the docs were last walked against.
