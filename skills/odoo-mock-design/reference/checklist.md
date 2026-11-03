# Production-readiness checklist (before declaring done)

Walk this list in SKILL.md § 5 Finish — after lint + anchors, BEFORE
bundling, so any fix lands in `_reference/` ahead of the single file.
The items below are **judgment checks** — things a mechanical lint or anchor can't fully see.
Mechanical gates (lint, asset-freshness diff, anchor pass) are listed at the
bottom as a footnote — they run automatically and aren't manual ticks.

## Judgment checks

- [ ] **Edition gate honoured** (SKILL.md § Comprehension → "Edition gate").
      Enterprise source (`enterprise/` or `versions/v*/enterprise/` with
      `web_enterprise`) present ⇒ the mock uses **Enterprise** chrome (bare
      `<body>`, `· Enterprise` kicker);
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
      list, kanban, dialog, chatter, settings — copied from the CURRENT
      catalog (the version in the `odoo.css` stamp), not from an older mock;
      no hand-coded alternatives.
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
      (`.o_dialog_user_error`), NOT a custom inline banner. It opens on the
      gated click for a setup value and is open by default only for an
      attempt value — never on a state the reader lands on (`GUARD-LANDING`).
      The dialog is
      titled after the exception ("Invalid Operation" for a UserError,
      "Validation Error"…), one `btn-primary` Close, no coloured header
      (see [`interactions.md`](interactions.md) § UserError / ValidationError
      dialog; catalog `components/dialog.html`).
- [ ] **Annotation markers: 4–7 per package**, each anchored to a load-bearing
      solution element. No marker explanatory text appears as inline body
      copy (`data-note` is the sole site for marker text).
- [ ] **Custom marking complete and exact** — every element the solution
      adds or changes carries `mock-custom` on its outermost wholly-custom
      element, every screen that shows a custom model's own view (or a new
      report / page) carries it on its `.mock-screen`, and nothing standard
      is marked. Walk the spec's new fields, models, menus, buttons and
      reports against the screens (see [`interactions.md`](interactions.md)
      § Custom elements). The lint only sees "?" fields; the rest is judgment.
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
      watermark), the 6 canonical callouts (conditional ones included per
      package structure), three-cell workflow narrative table. See
      [`cover_discipline.md`](cover_discipline.md).
- [ ] **Spec departures listed** — every place the mock follows the target
      Odoo source over the spec, or fills in text/screens the spec left
      undefined, is under `## Spec departures` in `_reference/README.md`
      with its source `path:line` (SKILL.md § 5 Finish). None hidden as a
      silent fix.
- [ ] **Output is in the right place** — `<mocks>` is `<spec-folder>/mocks/`
      whenever the input is or sits under a spec folder (both workflows); the
      `<repo_root>/mocks/<kebab>/` fallback applies ONLY when the input has
      no spec-folder context. The working package (`index.html` + `assets/`)
      sits in `<mocks>/_reference/`; the deliverable sits beside it as
      `<mocks>/<name> - mock.html`.

## Mechanical gates (auto-checked, not manual ticks)

These are enforced by `_lint_mock.py` and the two anchors. They fail loud
if missed — you don't have to remember them:

- Self-containment: no external refs, no path escapes, no external SVG
  `<use>`, every `<use href="#id">` resolves to an inlined sprite id
  (`UNRESOLVED-USE`), no placeholders (`Lorem ipsum` / `TODO` / `TBD`).
- Edition (`EDITION`): if `enterprise/` is present in the workspace, the mock
  must not carry Community chrome (`o-community` / `· Community`); and the
  `<body>` class and cover kicker must name the same edition. (The
  *ask-when-absent* half is the judgment check above — a lint can't prompt.)
- Asset freshness: SHA-256 diff against catalog (`STALE-ASSET`). A
  non-failing `NOTE` flags a cover version that differs from the version in
  the `odoo.css` stamp (the screens show the calibrated version's chrome).
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
- Custom marking: every "?" field sits in a `mock-custom` element or on a
  `mock-custom` screen (`CUSTOM-UNMARKED`); no mark on the cover / overviews,
  inside a custom screen, or nested (`CUSTOM-PLACEMENT`).
- Guard dialogs: no error dialog is open by default on a state the reader
  lands on — axis default, click-through, or a completed action's Ok
  (`GUARD-LANDING`).
- Corner ribbons use the real widget markup (`.ribbon > span.text-bg-*`)
  or an empty `data-text=` element — never bare child text.
- No backend chrome classes inside `.o_website` / `.o_portal` / `.pos`.
- No inline-styled tinted callouts inside non-backend surfaces.
- Cover step-list inside `.mock-step-list-wrap` so subgrid alignment holds.
- KNOWN-BAD patterns (`mock-cover-body`, `o_setting_searchbar`, invented
  `o_website_form` / `o_website_page` / `o_website_container`,
  `Interactive walkthrough` cover wording, `alert alert-danger` on backend
  forms) plus markup a catalog recalibration retired (gear `o_cp_cog`
  action menu, old breadcrumb/search/pager/settings/kanban/chatter
  classes, "User Error" dialog titles, unsized confirmation dialogs,
  `o_btn_outline` in dialog footers) — each finding names the replacement.
- Bundle gate: `_bundle_mock.py` refuses a legacy flat package, re-runs
  the lint and refuses a failing package, and writes the single file only
  if it references nothing outside itself.

After lint passes, fire `mock-coverage-anchor` + `mock-fidelity-anchor` in
one foreground message (parallel) on `<mocks>/_reference/`; reconcile
blockers; walk the judgment checks above; then bundle LAST with
`_bundle_mock.py "<mocks>"` (re-bundle after any later edit to
`_reference/` — the lint's bundle `NOTE` flags a missing or stale bundle)
and print `Done — open <mocks>/<name> - mock.html`.
