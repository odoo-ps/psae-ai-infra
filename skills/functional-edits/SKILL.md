---
name: functional-edits
description: >-
  Use when a functional consultant asks for any Odoo change on Odoo.sh — a
  label, help text, view layout, search filter, report wording, translation, or
  a small field / constraint / compute — and you must judge whether it is small
  and in-scope to do now, or large enough to refer to the technical consultant.
---

# Functional edits (Odoo.sh) — assess first, then act

You guard what the technical consultant built. Your first job is **assessment**,
not editing. Make the smallest safe change, or refer it. Enforcement lives in
the project's permissions + PreToolUse hooks; this skill is the guidance so you
cooperate and give good UX.

## Judge gate — run before every change

Assess out loud:

1. **Needs code at all?** If the ask is to scope new work, visualise screens, or
   answer a reporting question, it takes the **Document** exit — `odoo-write-specifications`,
   `odoo-mock-design`, `odoo-spreadsheet-report`. That is yours; don't refer it.
2. **Small?** field · constraint · short compute (~2–5 lines) · action button
   wired to an existing method/action · **Cosmetic View Edit** · label / filter /
   report / translation tweak. NOT a new model, new logic, or a rewrite.
3. **In my allowed area?** (table below)
4. **Preserves the architecture?** smallest edit, reuse what exists, match style.

All yes *and* you're confident → do it. Otherwise → **stop and refer**.
When in doubt, it's major. The letter of these limits IS their spirit — no
partial versions, no workarounds, never reroute around a blocked tool call.

## Allowed (do it) vs Major (refer)

| Allowed — small, in-scope | Major — refer to technical |
|---|---|
| label / help / placeholder | new model / wizard / module |
| field order, layout in an existing view | non-view `<record>`: action / menu / security / cron |
| **Cosmetic View Edit** — an `ir.ui.view` record that *extends* an existing view | a standalone view (no `inherit_id`), `mode=primary`, `type=qweb`, `active=False`, or `position="replace"` |
| search filter / group-by on existing fields | controllers, security, JS / OWL (`static/src/`) |
| action button wired to an existing method / action | a new action / server action / handler behind a button |
| report wording, email / website text | override `create`/`write`/`unlink`, real business logic |
| translations (`i18n/*.po`) | edit `__manifest__.py`, add dependencies |
| add a field / constraint / short compute | rename / retype / remove a field (schema migration) |
| a focused test for your change | `git push`, merge, staging/prod, pip / npm install |

## Do a safe change well

1. Restate, in one line, what you will change.
2. Make the minimal edit — only the `string=` / `help=` attribute, the `.po`
   entry, or the one field / constraint / compute.
3. Apply & verify: `odoo-bin -u <module> --stop-after-init --no-http`, then
   propose a test URL (`echo $ODOO_BUILD_URL`).
4. Commit, then `odoosh-push` to the **dev** branch (never `git push`; unpushed
   work is lost when the container rebuilds).

The file-type conventions load automatically: **odoo-python** (model/wizard),
**odoo-views** (XML), **odoo-tests** (a focused test).

## Refer a major change

1. **Stop** — no workaround, no partial version.
2. Say: "This goes beyond a small functional change and touches the architecture
   the technical consultant built — please refer it to them."
3. Offer a **handover** and, if accepted, write `handovers/<short-name>.md`: the
   client's intent in plain language, the models / fields / security it would
   touch, and any acceptance criteria. A doc, not code.

A Handover is reactive — you were stopped and you are preserving work in flight.
If instead the client is scoping something new that nobody has started, that's a
**Spec Folder**: run `odoo-write-specifications`.

## Never

- Never edit controllers, security, the manifest, or `static/src/`.
- Never create a model / module, override ORM CRUD, or add a **non-view** record /
  action / menu. (An *inheriting* `ir.ui.view` record is allowed — see the table.)
- Never `git push`, merge, switch to staging / production, or install packages.
