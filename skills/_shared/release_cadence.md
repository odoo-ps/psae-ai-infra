# Release Cadence Runbook — Odoo major-version bump

The deterministic procedure for re-calibrating the skills corpus when a new
Odoo major ships. Implements the **"Re-review on each major version bump"**
promise printed on every role checklist, and the bump half of
[principle #14 (version-aware content sectioning)](principles.md#14-version-aware-content-sectioning).

> **Why this exists.** Every calibration artefact (role checklist, anchor,
> industry-standards report, troubleshooting file, mock catalog) says it is
> pinned to one Odoo major, but the refresh work is easy to do piecemeal — a
> checklist gets updated while its paired anchor doesn't, or the mock catalog
> goes stale against new chrome. This runbook makes the refresh a checklist so
> the artefacts move **together**.

---

## When to run this

Run it when a new Odoo major **becomes the working baseline** — i.e. it's the
version most engagements now target, or the current baseline is nearing
end-of-support. **Do NOT run it just because a new `versions/v<major>/` stack was cloned
to disk.** The corpus stays calibrated to a single current major (P14); adding
a version folder is an environment change, not a corpus change.

The bump is **additive**: you add the new version's patterns and re-point the
baseline. You retire the *previous* version's content only when that version
falls out of support (see § Retirement policy).

Throughout, `X` = the new major (e.g. `20`), `Y` = the outgoing baseline
(e.g. `19`). The worked example at the bottom is the `19 → 20` bump.

---

## Pre-flight

- [ ] The new stack exists on disk: `versions/v<X>/odoo` (+ `versions/v<X>/enterprise` if used),
      cloned to the same shape as the existing stack.
- [ ] Its dependencies are installed in `versions/v<X>/odoo/.venv` and `odoo-bin --version`
      reports `Odoo Server <X>.0`.
- [ ] `_detect_environment.py` reports the new version in `versions[]`. **No
      script edits should be needed** — routing globs `versions/v<major>/` (see § What
      NOT to touch). If a script *does* need a change, that's a routing bug to
      fix separately, not part of calibration.
- [ ] Read the new major's official release notes / "what's new" before touching
      any checklist — the calibration edits below are only as good as the
      release-note pass behind them.

---

## Phase 1 — `_shared` baseline

- [ ] **Calibration lines (11 role checklists).** Change
      `*Calibrated against Odoo Y.0*` → `*Calibrated against Odoo X.0*` in every
      file under [`_shared/role_checklists/`](role_checklists/): `business_analyst`,
      `consultant`, `data_migration`, `devops`, `documentation`, `localization`,
      `performance`, `qa`, `security`, `solution_architect`, `ux_ui`.
- [ ] **Baseline statement.** [`principles.md`](principles.md) — update the P14
      line that names the baseline major (`today: Y.0` → `today: X.0`).
- [ ] **Illustrative version strings.** Refresh example manifest versions
      (`Y.0.1.2.0` → `X.0.…`) in `data_migration.md`, `documentation.md`, and
      `anchors/data-migration-anchor.md`. Cosmetic — the format is already
      generic (`<odoo_major>.<addon_major>.<addon_minor>.<patch>`).

## Phase 2 — Patterns: role checklists + anchors move together

For each role checklist, and **its paired anchor** in [`_shared/anchors/`](anchors/):

- [ ] **Add `### Odoo X+` subsections** under the standard headings
      (`Mechanisms / Tools`, `Common Pitfalls`, `Required artifacts`; anchor
      drift-pattern lists) wherever the new major introduces a genuinely new
      pattern (new view type, new helper, renamed field/model, new API idiom).
      Apply the P14 threshold: a dedicated subsection at 3+ patterns, an inline
      `(Odoo X+ …)` tag below that.
- [ ] **Leave all existing `### Odoo 17+` / `### Odoo Y+` blocks in place** —
      they are forward-compatible (minimum-version tagged) and still apply to X.
- [ ] **Pair check:** if a checklist gained an `### Odoo X+` pattern, confirm its
      anchor's drift-pattern list can detect drift against it (and vice-versa).
      A pattern added to a checklist but not its anchor is the classic
      piecemeal-drift failure this runbook prevents.

## Phase 2b — Addon conventions

- [ ] Refresh [`addon_conventions/`](addon_conventions/) against the new major. Two inputs:
      the new stack's source, and the guideline skills Odoo ships in it (the repository's
      `skills/odoo-guidelines`, `odoo-web-guidelines` and `odoo-security`, present from v20).
      Diff those guidelines against the previous major's copy, carry each new or changed rule
      into the matching file **in our own words**, and verify it in source before it lands.
      Version-dependent rules keep a tag per version (v<Y> vs v<X>), because the corpus still
      serves the outgoing major. Never link or symlink Odoo's tree: the conventions stay
      self-contained.
- [ ] Update [`addon_conventions/manifest.md`](addon_conventions/manifest.md) from the new
      `_DEFAULT_MANIFEST` (`odoo/modules/module.py`), and the license list from
      `ir_module.py`; mirror any change in `odoo-plan-development/reference/scripts/_lint_addon.py`
      (`KNOWN_KEYS`, `LICENSES`, `REMOVED_IN_*`).

## Phase 3 — Per-skill calibration assets (wholesale refresh, not sectioning)

- [ ] **mock-design catalog** — run [`odoo-mock-design/reference/REFRESH.md`](../odoo-mock-design/reference/REFRESH.md)
      against `versions/v<X>/odoo` (+ `versions/v<X>/enterprise`): rebuild `odoo.css`,
      `components/*.html`, `style_guide.md`, `view_types.md`, `field_placement.md`;
      re-render the gallery to verify; append to the Design refresh log. Honour
      the Enterprise-vs-Community edition gate (default Enterprise when
      `versions/v<X>/enterprise` exists).
- [ ] **Catalog core-fidelity check (the reference point).** `versions/v<X>/odoo` core is
      the authoritative source — the catalog must not encode class names the new
      major renamed or removed. Extract every structural `o_*` class the catalog
      treats as canonical Odoo (the ones mirroring real view/chrome DOM, not the
      catalog-coined composition helpers) and confirm each still exists in
      `versions/v<X>/odoo` (+ enterprise) core; reconcile every mismatch. New view types
      must be grounded in real core classes (e.g., Odoo 20's `card` view →
      `.o_card_record` / `.o_card`, verified against `web/views/card/`).
      **Method — compare against BOTH the old and new core, not just the new
      one.** A catalog class is *drift* only if it is present in `v<Y>` core but
      absent in `v<X>` core. A class absent from *both* is a catalog-coined
      composition helper (`.o_login_card`, `.o_portal_kv`, `.o_card_grid`, …) and
      is fine. Checking only `v<X>` produces **false positives** — a coined
      helper looks "removed" when it was never core. (Build one `o_*` token index
      per version from `versions/v*/odoo/addons` + `versions/v*/enterprise` static assets, then
      intersect: `drift = catalog ∩ v<Y> ∩ ¬v<X>`.) *The 19→20 pass, done this
      way, found **0 real drift** — all 230 real Odoo classes the catalog uses are
      stable across 19→20; the ~485 catalog-coined helpers are by design.*
- [ ] **plan-dev troubleshooting** — add an `## Odoo X` section to
      [`odoo-plan-development/reference/troubleshooting.md`](../odoo-plan-development/reference/troubleshooting.md)
      and any new idioms to `reference/odoo_runtime_idioms.md`. Keep the `Odoo Y`
      sections. Update the surface-map note in
      [`anchors/troubleshooting-anchor.md`](anchors/troubleshooting-anchor.md) if
      a new version section was added.
- [ ] **troubleshooting archive** — walk each skill's `troubleshooting.md` and
      promote entries that only applied to a now-superseded version to the
      `troubleshooting-archive.md`, per the troubleshooting-log discipline.
- [ ] **version-upgrade hop catalog** — add
      [`odoo-version-upgrade/reference/hops/v<Y>-v<X>.md`](../odoo-version-upgrade/reference/hops/)
      per its README § Adding a hop: draft entries from the removed-symbol sweep
      (`_scan_addon.py --target-stack versions/v<X> --from-stack versions/v<Y>` on a few real
      addons), the new `upgrade_code` scripts, the deprecation shims that name the version,
      and module-folder renames. Every `Source:` must be a path in the two stacks. Then
      confirm `_plan_hops.py --source <Y> --target <X>` reports the hop with a catalog.
- [ ] **data-migration patterns** — re-prove
      [`odoo-data-migration/reference/patterns.md`](../odoo-data-migration/reference/patterns.md)
      on the new major: rebuild the synthetic reference run of
      [`reference/samples/reference_pattern.md`](../odoo-data-migration/reference/samples/reference_pattern.md)
      against a throwaway `v<X>` database (snapshot → lint → dry run → load → reconcile),
      update every pattern whose fields, computes or post-load actions changed, and
      refresh the `Source:` paths. Then update the calibration line atop `patterns.md`.
- [ ] **o-spreadsheet source** — re-run
      [`odoo-spreadsheet-report/reference/scripts/_sync_o_spreadsheet_source.py`](../odoo-spreadsheet-report/reference/scripts/_sync_o_spreadsheet_source.py)
      so the vendored bundle + `spreadsheet-docs/` track the `X.0` branch (the
      script derives the stable branch dynamically — a straight re-sync).

## Phase 4 — Industry-standards reports

- [ ] Re-audit the per-skill `reports/industry_standards_audit.md` files (one
      per skill) for currency against the new major. These are point-in-time,
      stale-tolerant by design — re-run the audit rather than editing in place.

## Phase 5 — Changelog

- [ ] Record the bump in the corpus changelog **if it exists**
      (`corpus-changelog` is itself a roadmap item — see
      [`roadmaps/improvements.md`](../roadmaps/improvements.md)). One entry:
      *"Baseline calibrated to Odoo X.0"* naming the artefacts refreshed. If the
      changelog isn't built yet, skip this step — don't block the bump on it.

## Phase 6 — Verification

- [ ] `_detect_environment.py` reports both `v<Y>` and `v<X>` (coexistence).
- [ ] Scaffold a throwaway instance on the new stack
      (`_create_instance.py --instance smoke_x --version X`) and confirm every
      path routes to `versions/v<X>/odoo`, `versions/v<X>/enterprise`, `versions/v<X>/odoo/.venv`; then
      remove it.
- [ ] Re-run each skill's anchor pass against a `v<X>` target and confirm **no
      false drift** is flagged against patterns the new major doesn't have, and
      no new-major pattern is missed.
- [ ] Grep the corpus for a stray `Y.0` baseline reference the calibration pass
      missed (excluding legitimate `### Odoo Y+` sections and archive entries).
- [ ] **`versions/v<X>/odoo` core is the reference point.** Every factual claim added in
      this bump — checklist patterns, anchor drift rules, troubleshooting entries,
      catalog class names — must be verified against the new core, not from
      memory or the previous major. Self-consistency checks (lint, brace balance,
      internal reference resolution) are necessary but NOT sufficient: they prove
      the artifact is internally coherent, not that it matches Odoo X. When in
      doubt, grep `versions/v<X>/odoo` and cite the file.

---

## What NOT to touch (already version-dynamic)

These resolve the version at runtime; a bump must not hardcode `v<X>` into them:

- **Routing scripts** — `_detect_environment.py`, `_create_instance.py`,
  `_install_module.py`, `_smoke_module.py`, the four `odoo-version-upgrade` scripts
  (they discover stacks, `upgrade_code` scripts and hop catalogs at run time), and
  `_shared/scripts/_check_odoo_source.py`
  (its `--root-prefix` defaults to the `v*` glob spanning every stack;
  callers pin `versions/v<major>` for their target version, and an unpinned
  claim check warns when more than one stack exists).
- **SKILL.md routing language** — all four skills already say "never assume
  `v19`" and route to `instances[].version`.
- **`odoo-write-specifications`** — version-neutral: scripts report the install
  path via `sys.executable`; SKILL.md resolves the newest `versions/v*/odoo/.venv`.

If you find yourself editing any of the above to name the new version, stop —
that's a routing regression, not a calibration step.

---

## Retirement policy (removing the old major)

Retire `### Odoo Y+` subsections and archive Y-only troubleshooting entries
**only when Odoo Y falls out of support**, not at the X bump. Version subsections
are tagged by *minimum* version and are forward-compatible until explicitly
retired — removing them early strands consultants still on Y. Retirement is its
own pass, triggered by Y's end-of-support date, not by X shipping.

---

## Worked example — the 19 → 20 bump

`Y = 19`, `X = 20`. Concrete edits when 20.0 is promoted to baseline:

- 11 calibration lines: `Calibrated against Odoo 19.0` → `20.0`.
- `principles.md` P14: `today: 19.0` → `today: 20.0`.
- Add `### Odoo 20+` subsections where 20 introduces new patterns; keep every
  `### Odoo 17+` / `### Odoo 19+` block.
- mock-design catalog: `REFRESH.md` against `versions/v20/odoo` + `versions/v20/enterprise`.
- plan-dev: add `## Odoo 20` troubleshooting/idiom sections; keep `Odoo 19`.
- o-spreadsheet: re-sync to the `20.0` bundle.
- Retire nothing yet — Odoo 19 remains supported.

The baseline was promoted to **20.0** on 2026-09-30 (Phase 1 calibration flip:
11 role-checklist lines + `principles.md` + example version strings). Odoo 19
remains supported, so **no `### Odoo 19+` content was retired** — those
subsections stay valid under the forward-compatibility rule (see § Retirement
policy). Phase 2 (new `### Odoo 20+` patterns) is applied from a v19→v20 source
review; Phase 3 asset refreshes (mock catalog, o-spreadsheet re-sync) follow.
