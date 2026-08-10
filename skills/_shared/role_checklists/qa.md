# QA — Tests and Smoke

*Calibrated against Odoo 19.0. Re-review on each major version bump.*

## Goal
Each acceptance criterion has at least one test that fails when the addon breaks. The smoke checklist confirms the addon is operational end-to-end after install.

## Key Questions to Ask the User
- Which user stories warrant a **unit test** (compute logic, helper methods)?
- Which warrant an **integration test** (multi-step workflow)?
- Is there a **UI flow** that justifies a **tour test** (cost: brittle; benefit: catches view regressions)?
- What's the **minimum acceptance** before declaring done — full test suite green, or smoke checklist passing?
- What's the right **test base class** per test — `TransactionCase` (per-test rollback, default), `SavepointCase` (per-class rollback, shared fixtures, faster), or `HttpCase` (browser-driven tour tests)?
- Does the addon **reserve / lock / commit** a resource? If so, which **reverse paths** (cancel frees, unreserve → restore, expire releases) and **contention** cases (two documents claiming the same unit) need a test? (principle #15)

## Mechanisms / Tools
- **Unit tests** under `<addon>/tests/test_<feature>.py`, inheriting from `odoo.tests.common.TransactionCase`. One assertion per method when possible.
- **Integration tests** inheriting from `TransactionCase` or `HttpCase` for the workflow path. Use `with_user(user)` to test ACL behaviour.
- **Tour tests** via `HttpCase.start_tour(...)` — only when the workflow has a non-trivial UI element (a wizard, a kanban drag, a button visible only via state). Tours are slow and brittle; use sparingly.
- **`@odoo.tests.tagged('post_install', '-at_install')`** — runs after all addons load; required for tests that depend on demo data or other modules.
- **Run tests**: `odoo-bin -c <conf> -d <db> --no-http --stop-after-init --test-enable --test-tags=/<addon>` (slash prefix means "this module's tests only").
- **Test base classes — pick the right one**:
  - `TransactionCase` — default. Each test method runs in its own transaction; rollback at end-of-method. Fixtures in `setUp` re-run per test (safe, slow).
  - `SavepointCase` — class-scoped savepoint; `setUpClass` runs once; per-test data shared across methods in the class. Faster when tests share an expensive fixture (e.g. a built-out sales order). Watch out: mutations in one test method ARE visible to others in the same class.
  - `HttpCase` — spins up an HTTP server; used for tour tests + RPC tests. Heavier; only when the browser is the right test driver.
- **`setUpClass` vs `setUp`** — `setUpClass` (classmethod, runs once per class) for expensive fixtures (model demo data, multi-record setups). `setUp` (per-test, runs each method) for state that must reset between tests. Default to `setUpClass` for read-only fixtures; `setUp` for fixtures that any test might mutate.
- **Tour-test selectors** — prefer `data-menu-xmlid="my_module.menu_root"`, `data-tooltip="..."`, or `button[name="action_confirm"]` (stable attributes). Avoid raw CSS selectors like `.o_form_view > div:nth-child(3) > input` — break on any upstream view xpath change.
- **`with_user(user)` vs `with_context(allowed_user_ids=...)`** — `with_user` re-evaluates ACL + record rules as that user (the correct way to test access boundaries). `with_context` doesn't change the active user, only context values; not a substitute for ACL testing.
- **ACL deny-case test pattern**:
  ```python
  from odoo.exceptions import AccessError
  with self.assertRaises(AccessError):
      record.with_user(self.non_admin).write({"state": "approved"})
  ```
- **Smoke checklist** (Stage 3 of validation, see SKILL.md):
  1. Module is in `installed` state.
  2. Each new model is searchable: `env[model].search([], limit=1)`.
  3. Each menu's action resolves to a real model/view.
  4. A sample record creates, computeds populate, and unlinks cleanly.
  5. ACLs enforce — non-admin user can do what they should and can't do what they shouldn't.
  6. Test suite (if any) passes with `--test-tags=/<addon>`.
- **Test pyramid** — unit (many, fast, narrow) > integration (some, slower, multi-record) > E2E/tour (few, slowest, brittle). The right ratio for an Odoo addon is roughly 10:3:1. Tours that exceed this ratio create CI-time pain disproportionate to the bug-catching they provide.
- **Reverse-path & lifecycle tests** — for every forward action that commits / locks / reserves, test its inverse: cancel frees the resource, unreserve → re-reserve restores the committed value, expiry releases a stale hold. A green happy-path is not coverage of the lifecycle (principle #15).
- **Self-vs-others availability test** — when the addon computes "available", assert the boundary explicitly: a confirmed document's *own* reservation must NOT read as a shortage, while *another* document's claim DOES reduce availability.
- **Framework-constraint fixture priming** — when a test creates a record on a framework-owned model (`payment.token`, `account.move`, `sale.order`, `stock.move`, `res.partner`, `mail.message`, …), the fixture must satisfy that model's NOT NULL / required-Many2one / required-column constraints **before** the assertion under test runs. Otherwise the framework's constraint fires first and the test fails on the wrong line — the constraint-under-test never gets exercised, and the iteration cycle is wasted decoding a misleading traceback. Concrete fixtures: `payment.token` needs `provider_ref`; `account.move` needs `move_type` + `journal_id`; `sale.order` needs `partner_id`; `stock.move` needs `name` + `product_uom` + `location_id` + `location_dest_id`. When in doubt, introspect required fields (`env['<model>']._fields`) and stub each.
- **Shared fixture helper for repeated framework-model creates** — once ≥ 3 tests each spin up the same framework-model record from scratch, pull the construction into `setUpClass` (TransactionCase) or a parametrised helper. Avoids drift between copies and keeps the priming inventory in one place.

## Common Pitfalls
- **Tests that depend on demo data** without `post_install` tag — fail at install-time because demo data isn't loaded yet.
- **Tests that don't reset state** — if a test creates a record but doesn't `with_context(no_reset=True)` cleanup, later tests in the same `TransactionCase` see it. (TransactionCase rolls back per test, so usually fine — except for cross-test cursor commits.)
- **Tour tests that hardcode CSS selectors** — view xpath changes upstream break the tour without changing the logic. Use `data-menu-xmlid` and other stable hooks.
- **Smoke test that only confirms install succeeds** — misses the whole class of "installed but unusable" bugs (missing ACL, broken view, NULL computed).
- **No negative tests** — happy-path coverage hides ACL bugs and validation gaps.
- **`SavepointCase` shared-fixture surprises** — a test that mutates the shared fixture (e.g. confirms a `setUpClass`-created sales order) breaks every subsequent test in the class that assumes draft state. Use `TransactionCase` when in doubt; reach for `SavepointCase` only when the speed-up is measurable and the fixture is genuinely read-only.
- **Tour test using `nth-child` / position selectors** — view xpath inheritance reorders elements. Any tour selector that depends on element position is brittle by design.
- **Happy-path-only coverage of a lifecycle** — create → confirm is tested, but cancel / unreserve / expire / restore never is, so the missing-inverse class of bug ships green.
- **Silencing a misfiring control by removing it** — when a guard or cap false-positives, the fix corrects its computation (and keeps the test); deleting the safeguard to pass is a regression, not a fix (principle #16).
- **Validation that stops at the first failure** — a gating check (e.g. confirm) should enumerate ALL blocking lines/rows at once; a test asserting only the first-failure message lets the aggregate reporting silently regress.
- **Constraint test that trips a framework NOT NULL first** — the test creates a `payment.token` to exercise its own `@api.constrains`, but omits `provider_ref` (or another required column). The framework's IntegrityError fires before the constraint-under-test, the traceback points at SQL not at the addon, and a green run actually proves the priming logic, not the constraint. Inventory required fields at fixture-design time, not when decoding the failure.
- **N tests creating the same framework-model record by hand** — copy-pasted `create({...})` blocks across multiple tests drift: one updates `provider_ref`, another doesn't, and the failure mode depends on which test ran first. Centralise the fixture once it appears in ≥ 3 places.

## Production-readiness criteria
- [ ] At least one test per primary acceptance criterion.
- [ ] At least one ACL test using `with_user(...)`.
- [ ] `--test-tags=/<addon>` passes from a clean install.
- [ ] Smoke checklist (6 items above) passes manually OR via `_smoke_module.py`.
- [ ] Tests have explicit teardown — no leaked records, no mutated demo data.
- [ ] Tests that depend on demo data carry `@tagged('post_install', '-at_install')`.
- [ ] If the addon reserves / locks / commits: a reverse-path test per forward path (cancel frees, unreserve → restore, expire releases) — or `N/A` (no such resource).
- [ ] If it computes availability: a self-vs-others test (own reservation ≠ shortage; another document's claim reduces availability).
- [ ] A gating validation that can fail on multiple items has a test asserting **all** are reported, not just the first.
- [ ] Every test that creates a record on a framework-owned model (`payment.token`, `account.move`, `sale.order`, `stock.move`, …) enumerates the model's required columns in the fixture — no test relies on the framework's IntegrityError as its assertion.

## Required artifacts (the plan must contain these)

1. **Test inventory** — list every test file the addon ships under `<addon>/tests/`, naming the artifact each test covers (model, button, compute, ACL rule, state transition). Empty list is valid for trivial single-field extensions but flag as a `nit`.
2. **Test-tag strategy** — for tests that need demo data or rely on other modules being installed, declare the `@tagged('post_install', ...)` decorator. For tests that exercise installation-time behaviour, declare `at_install`.
3. **ACL-test inventory** — at least one test per restricted action using `with_user(env.ref('base.user_demo'))` — both happy-path (allowed user) and deny-case (forbidden user). Empty list is valid only if the addon adds no ACL boundaries.
4. **Smoke-checklist mapping** — every new artifact in the Implementation block (model, menu, button, compute, server action, ACL row, record rule) must appear in the Stage 3 smoke section. The plan's Smoke section explicitly names which artifact each smoke step exercises. **For every model in the security checklist's Write-path inventory (security.md Required-artifact #6) whose write path runs in user context (not `.sudo()`), the smoke step that triggers that write MUST execute it via `with_user(env.ref('base.user_demo'))` (or another non-admin internal user the plan declares).** A trigger run as admin / superuser masks user-context ACL failures and is not coverage. SQL-view models (`_auto = False`) and FK-cascade-populated models are exempt from the non-admin trigger (state which).
5. **Failure-case inventory** — for each happy-path smoke check, name the matching deny-case check (constraint violation, ACL deny, missing dependency, locked record). Without this, the smoke catches only the install path, missing the "installed but unusable" bugs.
6. **Test-command snippet** — the exact `odoo-bin -c <conf> -d <db> --no-http --stop-after-init --test-enable --test-tags=/<addon>` line (with concrete conf path + DB name from this run) lives in the testing manual so the operator can re-run.
7. **Lifecycle / reverse-path inventory** — when the addon commits / locks / reserves, list the inverse tests (release, restore, terminal-state cleanup) and any contention test. `N/A` only when the addon introduces no such resource. (principle #15)
