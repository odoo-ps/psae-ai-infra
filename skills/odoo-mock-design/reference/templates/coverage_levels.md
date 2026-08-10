# Coverage levels — Core / Standard / Comprehensive

**SINGLE SOURCE OF TRUTH** for the three coverage-level tier definitions. SKILL.md
§ Curate, the production-readiness checklist, and the mock-coverage-anchor's
instructions all cross-reference this file instead of restating the tiers
inline. A wording change here propagates to every consumer.

The coverage-level gate is asked **once** by the skill, before assembly,
populated from the step-1 eight-dimension inventory. Default tier is **Standard**.

The eight dimensions of the coverage floor are (see SKILL.md § Comprehension
step 1 for the full enumeration):

- **SURFACE** dimensions (does a screen exist?): actors, apps, new models +
  views, menus, reports, notifications.
- **BEHAVIOUR** dimensions (is the behaviour rendered somewhere?): lifecycle
  states, guard rules / negative paths.

Plus a 9th sub-class — **integration touchpoints (no-UI surfaces)** — rendered
as their effect (a State value, a source badge) + a cover callout listing
every touchpoint. See SKILL.md § Comprehension step 1 dimension 9.

---

## Core — happy path

The primary actor's journey only:
- The main app(s).
- The primary model.
- The happy lifecycle state(s).
- Guard rules shown **as markers**, not as renderings.
- **Excludes:** config, reports, notifications, edge states.

Smallest faithful mock. Typical size: **~4–6 screens**.

**Use when:** the reviewer wants a quick walkthrough of the main flow.

## Standard — full workflow (DEFAULT, RECOMMENDED)

The complete workflow coverage floor:
- EVERY actor (BPMN swimlane lanes + user-story actors).
- EVERY impacted app (§3 Apps Impacted + Automated Behaviours triggers).
- EVERY new model AND its `Views Required`.
- ALL primary lifecycle states as State-axis variants.
- EVERY guard rule rendered (UserError modal / State variant / guard banner).
- **Excludes:** peripheral config/settings pages, analytics reports,
  notification surfaces (emails/PDFs), lifecycle edge states.

Tells the whole operational story without reference clutter. Typical size
scales with actor / app / model / state count.

**Use when:** the reviewer needs to sign off on the workflow.

## Comprehensive — Standard + reference & peripheral surfaces

Standard PLUS:
- Configuration menus and config-model screens.
- Reports & Analytics (pivot / graph / dashboard).
- Notification surfaces (emails, printed PDFs).
- Lifecycle EDGE states.

For a sign-off package that shows every corner of the spec. Typical size:
Standard + ~3–5 additional screens depending on spec breadth.

**Use when:** the package is the final hand-off artefact.

---

## Tier boundaries are FIXED

A surface that is an actor's primary touchpoint or a core workflow step (the
website page where the journey *starts*, the CRM lead it *creates*, the
inventory receipt it *performs*, the eWallet it *mints*, every primary state,
every guard) is **Standard** — never push it to Comprehensive-only to skip it
at Standard.

Conversely, config/settings, reports, notifications and edge states are
**Comprehensive-only** — don't pull them into Standard by default.

## Report-centric specs

When the spec's own subject is a report or dashboard, OR its configuration IS
a core workflow (not a peripheral settings page), the Comprehensive add-ons
mostly don't exist and Standard ≈ Comprehensive. Don't manufacture a third
tier — say the tiers collapse, fold the core config into Standard, and offer
the two that actually differ (typically Core vs Standard).

## Reconciliation discipline

At the chosen tier, each of the eight dimensions is reconciled:

- **In-tier item** must have a screen / rendering.
- **Out-of-tier item** must be an explicitly-recorded exclusion (never a
  silent drop).

`mock-coverage-anchor` audits against this — "every in-tier item covered;
every out-of-tier item intentionally excluded."

---

## Presentation to the user (AskUserQuestion options)

When surfacing the gate, **populate each option from the actual inventory**
just built. Each option's `description` shows the screen count and the
**actual surfaces / screens** as a delta over the lower tier. Use the
option's `preview` field for long lists.

**Never show generic tier labels or example figures verbatim** — recompute
from the real inventory every run. If the inventory is too thin to
differentiate the tiers (single-actor / single-app brief where Core =
Standard = Comprehensive), say so and skip the gate.

For the option-presentation pattern, see the example pattern in the appendix
below (NEVER cite the example values verbatim in a real run).

---

## Appendix — example pattern (DO NOT cite verbatim)

For a hypothetical device-trade-in spec the options would read:

- *Core* — "4 screens: Website form · Appraisal · POS Trade-In · POS Redemption."
- *Standard* — "8 screens: Core + CRM Lead · Inventory Receipt · eWallet Card ·
  Draft/Agreed/Expired states · over-band & Agree-incomplete guards."
- *Comprehensive* — "11 screens: Standard + Inspection Criteria config ·
  Appraisal Pipeline (pivot) · Redemption Summary (graph) · voucher email."

This shape — concrete screen count + concrete surfaces as a delta — is the
target. Numbers and surfaces shown here are illustrative only; every real
package recomputes them from its own inventory.
