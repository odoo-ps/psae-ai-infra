# Python: models, ORM, fields, controllers

*Calibrated against Odoo 19.0 and 20.0. Re-review on each major version bump — see [release cadence runbook](../release_cadence.md).*

Performance rules (batch ORM calls, domains over `filtered`) live in
[`performance.md`](../role_checklists/performance.md); security rules (sudo, SQL, routes,
XSS) in [`security.md`](../role_checklists/security.md). This file is the rest of the
house style for Python in an addon.

## Imports

Four groups, each sorted: stdlib, third-party, `odoo` (`from odoo import Command, api,
fields, models`), then `odoo.addons.*` only when a module's code must be reused.

## Recordsets, domains, context

- Prefer `filtered`, `mapped`, `sorted` and `grouped` where they read better than a loop.
  Test emptiness with `if records:`, not `len()`.
- Reading a plain field on a multi-record set raises: iterate, or `mapped`. Guard
  single-record code with `ensure_one()`.
- Combine domains with `Domain` (`from odoo.fields import Domain`, v19 and v20):
  `domain & Domain('state', '=', 'done')`, `Domain.AND([...])`, `Domain.OR([...])`.
  Never hand-build `'&'`/`'|'` prefix lists, and never concatenate a caller-supplied list
  onto a security domain.
- Context is immutable: `with_context(...)`. Prefix module-specific keys
  (`library_skip_check`). A stray `default_<field>` key leaks into every `create`
  downstream.
- `_inherits` (delegation) shares fields, **not** methods. Avoid it for new designs, and
  never chain it.

## Computes, onchange, constraints

- `create` overrides take a list: decorate with `@api.model_create_multi`.
- `@api.depends` lists **every** field the compute reads, dotted chains included. Stored
  computes have no side effects.
- `@api.onchange` is UI-only: it never protects data (imports, RPC and other modules skip
  it). Enforce invariants with `@api.constrains`, or SQL constraints declared as model
  attributes: `_isbn_unique = models.UniqueIndex('(isbn)')`,
  `_qty_positive = models.Constraint('CHECK (qty >= 0)', 'Quantity must be positive.')`.
  The attribute name starts with `_`.
- `_sql_constraints = [...]` is **ignored** on v19 and v20 (a warning is logged and no
  constraint is created): always use `models.Constraint` / `models.Index` /
  `models.UniqueIndex`.

## Methods and extension points

- **Private by default.** A method without `_` is an RPC entry point: anyone with access
  to the model can call it with any arguments, on any records. Make a method public only
  when the client or another system must call it; decorate a public name that must not
  be exposed with `@api.private` (v19 and v20).
- Put logic another module will override into its own small method
  (`_get_due_domain()`), so others extend a method, not a line. Don't pre-split for
  extension points nobody needs yet.
- No `odoo.http.request` in model code: it does not exist in crons, RPC, tests or the
  shell. The controller passes in what the model needs.

## Transactions and exceptions

- Never `cr.commit()` or `cr.rollback()` on the framework's cursor; the request, cron or
  install owns the transaction. A cron that must commit progress uses
  `self.env['ir.cron']._commit_progress(processed, remaining=…)` (v19 and v20). A commit
  inside a method called from a test raises (plan-dev troubleshooting #59).
- Catch the specific exception, around the smallest block. To recover from a failing
  write, wrap it in `with self.env.cr.savepoint():`. More than about 64 savepoints in one
  transaction degrades PostgreSQL, so bound the batch.

## Translatable strings

- Translate **static literals** only, passing values as arguments:
  `self.env._("Book %s is already lent", book.display_name)`, named placeholders when
  there are several. Never format inside `_()` (`_("…%s" % x)`, f-strings) or after it
  (`_("…%s") % x`): the first matches no exported term, the second bypasses placeholder
  checks and Markup escaping. Pass a list for "a, b and c" lists.
- `self.env._` (v19 and v20) is the API in model code; bare `_` guesses the environment
  from the call stack and silently fails in plain functions and comprehensions.
- Nothing translatable at module or class level: use `_lt = LazyTranslate(__name__)` and
  resolve it where the language is known. Field values translate through
  `translate=True`, never `_()`.

## Fields

- `index=True` only on fields that are searched **and** selective (many distinct values).
  An index on a boolean or a state is wasted space and slows every write. Typed indexes:
  `index='btree_not_null'`, `index='trigram'` (for `ilike` search); multi-column ones are
  model attributes (`models.Index('(a, b)')`).
- Use reserved fields for their built-in behaviour: `active` (archive with
  `action_archive`), `state`, `company_id` (with `_check_company_auto` / `check_company=True`),
  `parent_id` + `parent_path` with `_parent_store` for trees.
- Check every relational definition: comodel, `ondelete`, `required`, a `currency_id`
  next to every `Monetary`.
- **`related` through an x2many is silently wrong:** the ORM truncates each one2many or
  many2many hop to its first record. Reach the target through `Many2one` hops (ending on
  an x2many is fine).
- `related` fields read as superuser by default (`related_sudo`, v19 `fields.py:456`,
  v20 `:482`): a related chain to sensitive data through a user-editable `Many2one` leaks
  it. Set `related_sudo=False` on such chains.
- Don't share one `inverse` method between fields: during the inverse, every field
  sharing it reads as `False` when not cached.

## Controllers

- Routes live on an `http.Controller` subclass. Always re-decorate an override with
  `@http.route()` (an empty decorator keeps the parent's arguments). An override can
  never change `type`.
- `type` is `'http'`, `'jsonrpc'` or `'json2'` (v19 and v20); `'json'` is a deprecated
  alias of `'jsonrpc'` (warns).
- Choose `auth` per route (`user`, `public`, `none`, `bearer`); the security rules for
  public routes are in [`security.md`](../role_checklists/security.md).

## Comments and messages

ASCII punctuation in code comments, docstrings, user-facing strings and commit messages:
no em or en dashes, curly quotes or ellipsis characters. They arrive by copy-paste,
can't be typed into a grep, and split one translatable term into two. Use a comma, colon,
semicolon or parentheses.
