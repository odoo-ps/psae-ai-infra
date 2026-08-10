# Production-readiness checklist (before declaring done)

Walk this list before printing `Done — open <path>`. The items below are
**judgment checks** — things a mechanical lint or anchor can't fully see.
Mechanical gates (lint, asset-freshness diff, anchor pass) are listed at the
bottom as a footnote — they run automatically and aren't manual ticks.

## Judgment checks

- [ ] **Edition gate honoured** (SKILL.md § Comprehension → "Edition gate").
      Enterprise source (`enterprise/` with `web_enterprise`) present ⇒ the
      mock uses **Enterprise** chrome (bare `<body>`, `· Enterprise` kicker);
      Enterprise source **absent** ⇒ the user was **asked** (Enterprise vs
      Community), never silently defaulted to Community. Never infer Community
      from where core models resolve — they always live under `odoo/addons`
      even on an Enterprise install. (The present⇒Enterprise and
      body/kicker-consistency halves are also enforced mechanically by the
      `EDITION` gate below; the *ask-when-absent* half is a judgment check
      because a lint can't prompt.)
- [ ] **Coverage-level gate was asked once** (Core / Standard / Comprehensive)
      with each option showing the **concrete, inventory-derived contents
      for this task** (screen count + actual surfaces as a delta, not the
      generic tier label) — OR a level was supplied by the user/caller. The
      assembled package matches the chosen level. Default tier is Standard.
- [ ] **Full step-1 inventory reconciled at the chosen level** — all eight
      dimensions (actors, apps, new models + views, menus, reports,
      notifications, lifecycle states, guard rules): every in-tier item has
      a screen / rendering; every out-of-tier item is a recorded exclusion
      (no silent drops). Plus integration touchpoints (no-UI surfaces)
      rendered as their effect + listed in the cover callout.
- [ ] **Screen count fits the chosen level** — Core ~4–6; Standard scales
      with actors / apps / models / states; Comprehensive adds config /
      reports / notifications / edge states. Padding (not driven by the
      inventory) is the anti-pattern, in either direction.
- [ ] **Catalog fragments used verbatim** for navbar, control panel, form,
      list, kanban, dialog, chatter, settings — no hand-coded alternatives.
- [ ] **Standard-field placement discovered from live source** (per
      [`field_placement.md`](field_placement.md)) — net-new fields placed
      by judgment; best-effort warning surfaced on cover when source absent
      (canonical wording in
      [`templates/source_unavailable_warning.md`](templates/source_unavailable_warning.md)).
- [ ] **Variant axes on screens where the brief encodes them** (tracking /
      state / actor / pricing-tier …); each axis is a chip in the chrome's
      filter-chip row. Guard rules typically appear as **State-axis values**
      on the relevant primary screen, NOT as separate screens.
- [ ] **Data multiplicity is shown as data, not as a variant axis.** If the
      data model naturally carries multiple items (multiple lines on one
      order, multiple cards on one kanban), they coexist on the screen — no
      axis needed (see [`style_guide.md`](style_guide.md) § Variants vs data
      multiplicity).
- [ ] **Guards render as UserError modals** — when a State value represents
      a blocking error, the screen carries a UserError dialog
      (`.o_dialog_user_error`) opened by default, NOT a custom inline banner
      (see [`interactions.md`](interactions.md) § UserError / ValidationError
      dialog).
- [ ] **Annotation markers: 4–7 per package**, each anchored to a load-bearing
      solution element. No marker explanatory text appears as inline body
      copy (`data-note` is the sole site for marker text).
- [ ] **Input-pending state** rendered + wired on "before user input"
      screens — `o_input_pending` class + a `data-mock-*` interaction. No
      painted-but-dead affordances. Picker panels are shared (one per axis,
      not N parallel).
- [ ] **Click-path connects every reachable screen** via Next / Prev or
      `data-mock-goto`. Every `data-mock-goto` target resolves to an
      existing `data-screen`.
- [ ] **Interactive path is walkable.** Every in-screen action that changes
      a downstream screen's state carries `data-mock-set-variant` alongside
      `data-mock-goto` — the reviewer can click Save → see the Quote at the
      post-save state, click Confirm → see Delivery, without manually
      pivoting chip-row chrome (per [`style_guide.md`](style_guide.md)
      § Interactive-path completeness).
- [ ] **Multi-workflow cover topology** (when ≥ 2 workflows): every
      user-facing workflow opens with a `data-screen-kind="workflow-overview"`
      screen as its first `.mock-screen`; the main cover carries the
      "Multiple workflows" how-to callout and CTA chips
      (`data-mock-goto="<slug>-overview"`) on workflow-index rows instead of
      `data-mock-page-ref`. See
      [`catalog_chrome.md`](catalog_chrome.md) § Multi-workflow chrome.
- [ ] **Cover discipline** complete — favicon, brand header (kicker +
      watermark), the 5 canonical callouts (conditional ones included per
      package structure), three-cell workflow narrative table. See
      [`cover_discipline.md`](cover_discipline.md).
- [ ] **Output is in the right place** — `<spec-folder>/mocks/` whenever
      the input is or sits under a spec folder (both workflows); the
      `<repo_root>/mocks/<kebab>/` fallback applies ONLY when the input has
      no spec-folder context.

## Mechanical gates (auto-checked, not manual ticks)

These are enforced by `_lint_mock.py` and the two anchors. They fail loud
if missed — you don't have to remember them:

- Self-containment: no external refs, no path escapes, no external SVG
  `<use>`, no placeholders (`Lorem ipsum` / `TODO` / `TBD`).
- Edition (`EDITION`): if `enterprise/` is present in the workspace, the mock
  must not carry Community chrome (`o-community` / `· Community`); and the
  `<body>` class and cover kicker must name the same edition. (The
  *ask-when-absent* half is the judgment check above — a lint can't prompt.)
- Asset freshness: SHA-256 diff against catalog (`STALE-ASSET`).
- Variant-axis JSON well-formed; defaults ∈ options; child references
  valid axis/value.
- Multi-workflow shell: every wrapper has `data-workflow` +
  `data-workflow-title` (≤ 12 chars); `data-screen` IDs globally unique;
  no orphan `.mock-screen` outside a wrapper.
- Input-pending wiring: every `o_input_pending` carries one of
  `data-mock-toggle` / `-modal-open` / `-goto`.
- Page-ref resolution: every `data-mock-page-ref` matches a real
  `data-screen`.
- Workflow-screen markers are numeric per-screen (the cover `i` is the
  only non-numeric marker).
- Corner ribbons draw their band from `data-text=` (not child text).
- No backend chrome classes inside `.o_website` / `.o_portal` / `.pos`.
- No inline-styled tinted callouts inside non-backend surfaces.
- Cover step-list inside `.mock-step-list-wrap` so subgrid alignment holds.
- KNOWN-BAD patterns (`mock-cover-body`, `o_setting_searchbar`, invented
  `o_website_form` / `o_website_page` / `o_website_container`,
  `Interactive walkthrough` cover wording, `alert alert-danger` on backend
  forms).

After lint passes, fire `mock-coverage-anchor` + `mock-fidelity-anchor` in
one foreground message (parallel); reconcile blockers; declare done.
