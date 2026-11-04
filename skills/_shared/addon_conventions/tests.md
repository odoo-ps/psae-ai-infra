# Tests

*Calibrated against Odoo 19.0 and 20.0. Re-review on each major version bump — see [release cadence runbook](../release_cadence.md).*

What to test (lifecycle inverses, deny-cases, availability boundaries, fixture priming)
is the [QA role checklist](../role_checklists/qa.md). This file is how to write tests so
they actually run.

## Base classes

- `TransactionCase` (each test rolls back) for business logic; `HttpCase` for tours and
  routes. **`SavepointCase` no longer exists** (absent from v19 and v20
  `odoo/tests/common.py`): class-level fixtures go in `setUpClass` of a
  `TransactionCase`.
- New business tests start from `odoo.addons.base.tests.common.BaseCommon` (its own
  non-admin user and company, mail side effects off). Use `TransactionCaseWithUserDemo` /
  `HttpCaseWithUserDemo` when demo data is needed; demo data is not guaranteed to be
  present.
- Assert behaviour, not implementation.

## Tags — the default changed between versions

| | v19 | v20 |
|---|---|---|
| Default tags of a test class | `standard`, `at_install` (`tests/common.py:317`) | `standard`, `post_install` (`tests/common.py:605`) |

- Set exactly one of `at_install` / `post_install` when it matters. **Both** makes the
  class run twice; **neither** (`@tagged('-at_install', '-post_install')`) makes it never
  run, with only a log warning.
- A test that needs other modules' data or a fully loaded registry is `post_install`. On
  v19 that must be explicit: `@tagged('post_install', '-at_install')`. On v20 it is the
  default. An `HttpCase` stays `post_install`.
- Tests run only for installed modules: `--test-tags=/<module>` on a database where the
  module is installed.

## Tests that silently never run

- The file must be named `test_*.py` **and** imported from `tests/__init__.py`.
- The class must be **defined** in that file; a class merely imported into it is skipped.
- Inherited `test_*` methods are not collected: a subclass that defines no test of its own
  runs nothing unless it sets `allow_inherited_tests_method = True`.

Check the run log for the expected test count, not just a green exit.

## Other rules

- Wrap expected errors and warnings in `mute_logger('<logger>')` so the run log stays
  clean and real errors stand out.
- `assertQueryCount` only in dedicated performance tests, with `@warmup` and `@users`;
  never in a business test (it breaks on unrelated ORM changes). Only exceeding the
  budget fails, so keep budgets exact.
- Tours: a step that unloads the page sets `expectUnloadPage: true`, and the last step
  leaves the client stable (no pending edit, no in-flight request).
- A method under test that calls `cr.commit()` raises inside tests (plan-dev
  troubleshooting #59); see [`python.md`](python.md) § Transactions.
