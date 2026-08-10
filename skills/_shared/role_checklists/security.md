# Security Expert

*Calibrated against Odoo 19.0. Re-review on each major version bump.*

## Goal
Make sure every new model, route, attachment, and PII field is access-controlled correctly before the addon ships.

## Key Questions to Ask the User
- What **user groups** should see / edit / delete each new model? (default: internal users read+write; admins delete)
- Is the data **multi-tenant** (records belong to a company / partner / department)? If yes, a record rule is needed.
- Does the addon expose **public HTTP routes** (`@http.route(auth='public')`)? If yes, what's the rate-limit and CSRF posture?
- Are there **PII / sensitive fields** (national ID, salary, medical) that need group-restricted read access?
- Are there **attachment fields** (`Binary`, `Image`)? Who can upload, who can download, what's the size cap?
- Does the addon call **`.sudo()`** anywhere? Every escalation needs a stated reason.
- Does the addon make **external HTTP calls** (third-party APIs, webhooks)? Where do the credentials come from (`ir.config_parameter`, env var, secret store)?
- Will the addon be reachable by **portal users** (external customers, partners) or only **internal users**? Two different access surfaces with two different default rules.
- Does the workflow involve **financial transactions / admin actions** for which 2FA should be required? Odoo Enterprise ships `auth_totp`; deployments with compliance constraints should require it for admin groups.

## Mechanisms / Tools
- **Every new model needs a row in `security/ir.model.access.csv`.** No exceptions. Without it, only superuser can read the model — and the bug surfaces only when a non-admin uses the addon.
  ```csv
  id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
  access_my_model_user,my.model.user,model_my_model,base.group_user,1,1,1,0
  access_my_model_manager,my.model.manager,model_my_model,my_module.group_my_manager,1,1,1,1
  ```
- **Record rules** for multi-tenant data: define groups (`security/security.xml`), then `<record model="ir.rule">` with a domain like `[("company_id", "in", company_ids)]`.
- **Field-level access**: use `groups="my_module.group_my_manager"` on `<field>` to hide it from unauthorised users. Note: this hides in views but the field is still readable via ORM unless ACL'd at model level.
- **Public routes**: validate input, use `csrf=False` only when explicitly justified, rate-limit via Odoo's `WebRequest` mechanisms, never trust `request.params` without sanitisation.
- **PII fields**: add `groups="..."` and consider `tracking=True` to log access via the chatter.
- **`.sudo()` discipline**: every `.sudo()` call needs a one-line comment justifying the escalation. Default-deny on uncommented sudo. The two legitimate patterns are (a) "needed because the caller is a portal/public user but the read target is internal-only" and (b) "needed because cross-company data access is the intentional product behaviour." Anything else is suspicious.
- **Context bypass discipline**: `with_context(active_test=False)`, `with_context(no_audit=True)`, `with_context(tracking_disable=True)`, and equivalent escape hatches need the same one-line comment as sudo. They suppress checks for a reason; state the reason.
- **External call authentication**: every external HTTP call must read its credential from `ir.config_parameter` (or env via the same), never hardcoded. Set the parameter on first install via `post_init_hook` with a placeholder + log line telling the admin to fill it in; or document the manual step in the testing manual.
- **Secret-handling in artefacts**: no credentials in plan files, no credentials in test fixtures, no credentials in committed code. The plan file must NEVER contain a literal API key, password, or basic-auth URL. Use placeholders (`<API_KEY>`) and reference the storage mechanism.
- **Portal users vs internal users — different surfaces.** `base.group_user` (internal) gets the back-end UI + most read access by default. `base.group_portal` (external customer / partner) gets a restricted web view + heavily-locked-down ACL — record rules typically narrow to `[("partner_id", "=", user.partner_id.id)]` or equivalent. A custom model that's portal-reachable needs both an ACL row for portal AND a record rule scoping it; without the rule, every portal user sees every record.
- **QWeb XSS — `t-esc` (escapes) vs `t-raw` (raw HTML, no escape)** — `t-esc` is the default and is safe for user-controlled content. `t-raw` is almost never the right call; the legitimate uses (trusted HTML, rich-text fields) need a one-line justification next to the directive. A `t-raw` on a `Char` or user-input field is an XSS hole.
- **CSRF discipline on `@http.route`** — POST routes default to CSRF-token-required. `csrf=False` removes that check; use only when (a) the route is genuinely public (no session) AND (b) input is authenticated by a separate mechanism (signed payload, API token). A logged-in POST with `csrf=False` and no replacement is a cross-site-request-forgery hole.
- **`@http.route` route-level XSS / SSRF**: `request.params` is user-controlled — sanitise before rendering or before passing as a URL to `requests.get/post`. SSRF specifically: never use user-controlled host in an outbound HTTP call without an allowlist of acceptable hosts.
- **`with_user(user)` vs `.sudo()` — different semantics.** `sudo()` skips ACL + record rules entirely; the operation runs as superuser. `with_user(user)` re-evaluates ACL + record rules as that specific user — the right tool for "do this action on behalf of partner X" (their access boundaries still apply). Reach for `with_user` first; `.sudo()` is a privilege escalation that bypasses the access model.
- **`mail.thread` + `tracking=True` for PII access audit** — sensitive fields with `tracking=True` log every change to the record's chatter (who, when, old value → new value). Required for GDPR-relevant data; useful for any compliance regime that demands audit trails. Pair with `groups="..."` to restrict who sees the chatter entry.
- **2FA via `auth_totp` (Odoo Enterprise)** — admin and finance groups should require 2FA in production deployments. The module is enabled per user-group via Settings → Users; the addon can enforce it via a constraint on the relevant `res.groups` if compliance demands it.
- **Immutability is enforced at the model, not the view.** To make a committed field/record unchangeable by a role, a `readonly` in one view is not enough — `create`, other views, import, barcode, and RPC all bypass it. Guard `write` (the changed field), `create` (a foreign/extra value), AND `unlink` at the model layer, and **remove the UI control** (e.g. a readonly o2m has no Add/Delete) so it can't merely error on save. Crucially, exempt the legitimate **system** flows that share the code (cancel → unreserve, validation writing done qty) via a trusted-operation context flag — block only the *manual* override. (principle #15)

## Common Pitfalls
- **No ACL CSV at all** — the model installs but is invisible to non-admins. Catch in Stage 1 lint.
- **Record rule with `noupdate="0"`** (default) — gets recreated on every `-u`, wiping admin's manual edits.
- **`groups="..."` only on the view** — non-admin can still read via `read()` / RPC. Need ACL at model level.
- **Public route exposing internal model fields** — `request.env['hr.employee'].sudo().read([...])` leaks the whole HR table. Always sudo with a narrow read.
- **Forgetting `company_id` on a multi-company model** — record rule can't filter by company; cross-company data leaks.
- **`.sudo()` without justification** — once acceptable in a code base, every subsequent sudo gets justified by reference to the unjustified one. Default to the strictest possible access; escalate explicitly.
- **Hardcoded API key / token in code or plan** — even in private repos, secrets in git history are a recurring breach vector. The plan must use placeholders; the code must read from `ir.config_parameter`.
- **`t-raw` on user-controlled content** — classic XSS surface. Default to `t-esc`; reach for `t-raw` only with explicit justification + trusted source.
- **`csrf=False` on an authenticated POST without replacement** — CSRF hole. Either keep CSRF or replace with a signed-payload / API-token check.
- **`.sudo()` where `with_user(...)` was the right tool** — escalates beyond the intended scope. Audit every sudo: if the action is "on behalf of user X," `with_user(X)` is correct; `.sudo()` is overreach.
- **Portal-reachable model without record rule** — every portal user sees every record. The ACL row alone is not enough for portal; a record rule narrowing to the user's partner is required.
- **`readonly` treated as a security control** — it disables a field in one view; `create`, other views, import, and RPC still mutate it. Enforce immutability at the model layer (write+create+unlink) and remove the UI control — don't rely on `readonly` alone.
- **A lockdown guard that also blocks the resource's release** — e.g. an `unlink` guard so strict the order can't be cancelled/unreserved. Exempt system-initiated flows via a trusted context; block only manual edits.

**OWASP Top 10 mapping** (quick reference — the security checklist's pieces and what OWASP category each addresses):
- A01 Broken Access Control → ACL CSV + record rules + portal-vs-internal discipline
- A02 Cryptographic Failures → `ir.config_parameter` for secrets, no creds in plan/code/tests
- A03 Injection → ORM `search()` with domain (never `cr.execute` with f-strings), `t-esc` not `t-raw`
- A05 Security Misconfiguration → public routes have CSRF + rate-limit + input sanitisation reviewed
- A07 Identification and Authentication Failures → portal vs internal user discipline, 2FA via `auth_totp` for admin/finance groups
- A09 Logging and Monitoring Failures → `mail.thread` + `tracking=True` on PII fields for access audit
- A10 SSRF → external HTTP calls never use user-controlled host; allowlist required

## Production-readiness criteria
- [ ] Every new model has at least one row in `ir.model.access.csv`.
- [ ] Multi-tenant models have a record rule scoping to `company_id` / `user_id` / `partner_id`.
- [ ] No public routes added, OR added ones have CSRF/rate-limit/sanitisation reviewed.
- [ ] PII fields have group restrictions both at view level (`groups=`) and model level (ACL).
- [ ] Smoke test impersonates a non-admin user (`with_user(env.ref('base.user_demo'))`) and confirms the workflow still works.
- [ ] Every `.sudo()` call in the plan or codebase has a one-line justification comment.
- [ ] Every `with_context(active_test=False)` / `no_audit` / `tracking_disable` escape hatch has the same.
- [ ] External HTTP calls read credentials from `ir.config_parameter` (or equivalent secret store); zero hardcoded keys.
- [ ] Plan file contains no literal credentials (placeholders only, with the storage mechanism documented).
- [ ] A value meant to be immutable to a role is guarded at the model layer (write + create + unlink), the UI control is removed (not just `readonly`), and system release flows (cancel / unreserve / validate) are exempted.

## Required artifacts (the plan must contain these)

1. **ACL coverage statement** — for every new model in the Implementation block, name the group(s) and CRUD bits granted (or cite the `security/ir.model.access.csv` rows). The bits stated MUST cover every verb the plan's *write path* for that model actually performs (see #6); a read-only ACL on a model the plan also writes to is a contradiction.
2. **Record-rule statement** — for every new model that holds company-scoped, user-scoped, or partner-scoped data, declare the record rule (or explicitly note "single-tenant, no rule needed").
3. **`.sudo()` inventory** — list every place the addon calls `.sudo()` with a one-line justification each. Empty list (no sudo) is a valid answer.
4. **External credential inventory** — for every external HTTP call the addon makes, name the `ir.config_parameter` key + UI path the admin uses to set it. Empty list (no external calls) is a valid answer.
5. **PII / sensitive field inventory** — list every new field that holds PII, financial data, or otherwise sensitive content, with the access-restriction decision per field. Empty list is a valid answer.
6. **Write-path inventory per new model** — for every new model, enumerate every code path that *mutates* it (creates, updates, or unlinks rows). Sources to scan: overrides of `create` / `write` / `unlink` on this or any related model; `base.automation` records targeting this or a parent model; `ir.actions.server` rows; cron jobs; wizard `action_*` methods; computed fields with `store=True` that write to other records; `onchange` handlers that persist; ORM calls from controllers. For each entry, state **(a)** the trigger location, **(b)** the verb performed (`create` / `write` / `unlink`), **(c)** the security context the path will run under (`base.group_user`, `base.group_portal`, a custom group declared in the plan, `sudo()` with a justification, or "automated context = the acting user's groups"). The ACL coverage statement (#1) must grant each (verb, group) pair listed here, OR the path must use `.sudo()` listed in the sudo inventory (#3). A path that writes "as the acting user" against a model whose ACL grants the user only `perm_read=1` is a hard contradiction — flag at plan time, not at smoke time. Empty list (model is populated only by other models via FK + cascade, or is a SQL view with `_auto = False`) is valid; state which.
