# Source-unavailable warning — canonical text

**SINGLE SOURCE OF TRUTH** for the warning surfaced to the user (and on the
mock's cover) when the workspace lacks the Odoo source checkouts that
`field_placement.md` Step 0 requires for faithful field placement.

This file is referenced by [`field_placement.md`](../field_placement.md) Step 0
and by [`SKILL.md`](../../SKILL.md) § Comprehension step 1. Wording changes
here propagate to every consumer.

---

## The warning (verbatim)

> ⚠ Odoo source (Community/Enterprise) was not found at `odoo/` / `enterprise/`.
> Field placement and screen structure are **best-effort and may not match real
> Odoo**. Provide the checkout for faithful screens, or treat these mocks as
> approximate.

## When to surface it

- **At skill start**, when `field_placement.md` Step 0's source-availability
  check fails — print the warning to the user before proceeding.
- **On the mock's cover**, as a small callout below the brand header, so any
  reader who opens the package knows the screens are best-effort.

## When to suppress it

- When **both** `odoo/` and `enterprise/` checkouts are present and readable
  in the workspace.

## Community-only case

When only `odoo/` is present (no `enterprise/`), use this softer variant:

> ⚠ Only the Odoo Community source is present at `odoo/`. Enterprise-only
> fields and pages won't appear; enterprise screens may differ from reality.
