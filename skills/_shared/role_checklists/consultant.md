# Consultant — Problem Framing

*Calibrated against Odoo 19.0. Re-review on each major version bump.*

## Goal
Make sure the addon solves a real, scoped problem before any code is written. The consultant role is the first line of defence against scope creep and the "build me a Salesforce" anti-pattern.

## Key Questions to Ask the User
- Who is the **primary user** (role, not name)? Whose day improves if this works?
- What **decision or action** does the addon enable that they can't do today?
- What's the **success criterion** in one sentence (something measurable, not "looks good")?
- What's **explicitly out of scope**? (force a list of at least 2 things you won't build)
- Is there an **existing standard Odoo module** that already covers most of this need?
- Could **Studio + Automation rules + Approval rules** cover this without a custom module? If yes, the spec is a Studio configuration, not a code spec.
- What **subscription tier** is the client on? Custom unlocks dev / Studio; Standard does not. A spec that needs custom code on a Standard tenant is dead on arrival until the tier moves.
- Is this an **Odoo.sh** or **on-premise** deployment? Drives what's possible (Odoo.sh forbids host-shell access, OS packages, arbitrary binaries) and who owns operational concerns.

## Mechanisms / Tools
- Search Odoo's apps store and `enterprise/` for prior art before scoping new code.
- Use a one-paragraph "elevator brief" the user signs off on before moving to the BA role.
- For ambiguity, prefer **subtractive scoping**: list what's in, ask which to drop.
- **Studio-first prototype** — before scoping a custom module, build the closest approximation in Studio (view edits + automated actions + approval rules). A working Studio prototype passes user review faster than a written spec and exposes mental-model gaps. Custom code is the *fallback* when Studio's limits bite, not the default.
- **Implementation phases** — `Discovery` (this checklist) → `Implementation` (BA + SA + the rest) → `Go-Live` (validation + cutover) → `Optimization` (post-live tuning). The consultant owns Discovery's exit criterion: a signed-off brief.
- **Subscription-tier impact** — Custom subscription enables developer mode, Studio's full surface, custom modules. Standard subscription limits the customer to configuration. Confirm tier *before* scoping anything that needs developer mode; a Standard-tier client either upgrades or de-scopes to config-only.

## Common Pitfalls
- "Just like X but tailored for us" — usually a sign the standard module would fit with config.
- Conflating *report* with *workflow* — a report doesn't change records, a workflow does.
- Building for an unnamed future user. If no one's asking for it now, don't build it now.
- **Scoping a custom module before testing Studio.** "We need custom code for this" is rarely true on the first ask. Studio + automated actions + the Approvals app cover ~70% of "we want to tweak a form / gate a confirmation / send a follow-up" requests.
- **Ignoring subscription tier.** Specs that assume developer mode on a Standard-tier tenant land DOA. Confirm the tier in Discovery, not after the BA spec is signed.
- **Treating Odoo.sh and on-premise as interchangeable.** They aren't: Odoo.sh forbids OS-level access, restricts package installs to manifest-declared Python deps, and runs builds through their own pipeline. A spec that assumes host-shell tooling won't deploy.

## Production-readiness criteria
- [ ] One-sentence success criterion captured.
- [ ] At least 2 out-of-scope items listed.
- [ ] Confirmed no standard Odoo module covers ≥ 70% of the need (or explicitly chose to extend rather than reuse).
- [ ] Report-vs-workflow framing matches the Implementation block (a "report" doesn't mutate; a "workflow" does).
- [ ] Every feature in scope has a named current requester (no "users might want this someday").

## Required artifacts (the plan must contain these)

1. **Problem statement** — one paragraph naming the pain, the affected role, and the measurable outcome of fixing it. Not a description of the solution.
2. **Primary user statement** — the role whose day improves if this ships (e.g. "Sales rep building quotations"), not the named individual who asked for it.
3. **One-sentence success criterion** — measurable, with a yes/no test. *"Sales reps can pick a lot at quote stage"* is too soft; *"100% of confirmed SOs for lot-tracked products carry a committed lot"* is concrete.
4. **In-scope / out-of-scope lists** — at least 2 entries in each column. The out-of-scope column is the more important one — it's where scope creep dies.
5. **Standard-Odoo overlap statement** — one of: (a) "no overlap — net-new functionality", (b) "extends standard `<module>` — reusing X, adding Y", or (c) "custom despite overlap with `<module>` — reason: `<concrete fit gap>`". Required for every plan. No third option.
6. **Report-vs-workflow tag** — one word: `report` (read-only aggregation, no state mutation) or `workflow` (mutates records / state). The Implementation block must match the tag.
