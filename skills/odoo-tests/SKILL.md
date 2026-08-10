---
name: odoo-tests
description: >-
  Use when adding or running a focused test under tests/ in an Odoo module on
  Odoo.sh as a functional consultant, verifying a constraint or small change
  you made.
---

# Odoo tests — a focused test for your change

Scope: a **single focused test** for the small change you made (e.g. that your
constraint raises) is fine. A broad suite, tours, or reworking existing tests is
the technical consultant's job → refer. Never change the business flow that an
existing test asserts.

## Write it

```python
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import ValidationError


@tagged("post_install", "-at_install")
class TestMyConstraint(TransactionCase):
    def test_end_after_start(self):
        with self.assertRaises(ValidationError):
            self.env["my.model"].create({
                "date_start": "2026-01-02",
                "date_end": "2026-01-01",
            })
```

- `TransactionCase` is the default (each test rolls back). Use `HttpCase` only
  when you need HTTP — controllers, sessions, tours.
- `@tagged("post_install", "-at_install")` for most custom tests (never
  `-at_install` alone — the test would never run).
- Assert specific exceptions (`assertRaises(ValidationError)`, not bare
  `Exception`) and on stable field values, not translatable UI labels.

## Discovery (easy to get wrong)

`tests/__init__.py` must import **every** test file, alphabetically — a missing
import means the test silently never runs. The module root `__init__.py` never
imports `tests`.

## Run (Odoo.sh)

```bash
odoo-bin -u <module> --test-enable --stop-after-init --no-http   # the module's tests
odoo-bin --test-tags /<module> --stop-after-init --no-http       # select by tag
```

Login users (`admin` / `demo` / `portal`) have **no password** on a fresh build —
set one (the single sanctioned `psql` write) before a test that logs in:

```bash
psql -c "UPDATE res_users SET password='admin' WHERE login='admin';"
```

Odoo re-hashes the plaintext on first login, so this is expected — a later login
failure is not a code bug. Quote the actual test output — never claim a pass
without it.
