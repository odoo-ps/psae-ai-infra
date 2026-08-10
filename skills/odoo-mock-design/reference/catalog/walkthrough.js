/*
 * walkthrough.js — click-through navigation + annotation overlay for Odoo mock
 * packages. Vanilla JS, no dependencies. Master copy; copied verbatim into each
 * package's ./assets/. Pairs with annotations.css.
 *
 * Catalog version: Odoo 19 (last refresh: 2026-06-15).
 * See ../REFRESH.md for the change history.
 *
 * Data API (authored into index.html by the odoo-mock-design skill):
 *   <section class="mock-screen" data-screen="ID" data-title="..." data-desc="...">
 *       ... Odoo chrome ...
 *   </section>
 *   data-mock-goto="ID"   on any element -> click navigates to screen ID
 *   data-mock-next        -> go to the next screen in order
 *   data-mock-prev        -> go to the previous screen
 *   <span class="mock-marker" data-note="explanation">N
 *       (callout is generated from data-note; or nest .mock-callout yourself)
 *   </span>
 *
 * The skill must include exactly one #mock-walkthrough bar (see component
 * fragment walkthrough_bar.html). Everything else is wired automatically.
 */
(function () {
  "use strict";

  // All screens in the document, in source order (used for #hash lookup +
  // global goto targets). Navigation/Next/Prev are scoped to the CURRENT
  // workflow's screens via activeScreens() — single-workflow packages
  // collapse to "all screens" naturally.
  var screens = [];
  var workflows = [];     // [{slug, title, screens:[...]}, ...]; empty when no wrappers
  var currentWf = 0;
  var current = 0;        // index into activeScreens()

  function qsa(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }

  function activeScreens() {
    return workflows.length ? workflows[currentWf].screens : screens;
  }

  function indexOfScreen(id) {
    var list = activeScreens();
    for (var i = 0; i < list.length; i++) {
      if (list[i].getAttribute("data-screen") === id) return i;
    }
    return -1;
  }

  // Find a screen across ALL workflows (data-mock-goto can cross-workflow).
  function findScreenAnywhere(id) {
    for (var i = 0; i < screens.length; i++) {
      if (screens[i].getAttribute("data-screen") === id) return screens[i];
    }
    return null;
  }

  function workflowOfScreen(screenEl) {
    for (var i = 0; i < workflows.length; i++) {
      if (workflows[i].screens.indexOf(screenEl) >= 0) return i;
    }
    return -1;
  }

  function show(i) {
    var list = activeScreens();
    if (i < 0 || i >= list.length) return;
    current = i;
    // Hide ALL screens (across workflows), then activate just the one.
    screens.forEach(function (s) { s.classList.remove("is-active"); });
    list[current].classList.add("is-active");
    updateBar();
    closeAllCallouts();
    closeModals();
    closeAllToggles();
    window.scrollTo(0, 0);
  }

  function goTo(id) {
    var target = findScreenAnywhere(id);
    if (!target) return;
    var wf = workflowOfScreen(target);
    if (wf >= 0 && wf !== currentWf) {
      currentWf = wf;
      rebuildWorkflowChrome();
    }
    var i = indexOfScreen(id);
    if (i >= 0) show(i);
  }

  /* ---- Cross-workflow navigation -------------------------------------------
   * Next/Prev step within the current workflow until they hit a boundary,
   * then cross into the adjacent workflow. A multi-workflow package reads as
   * one continuous narrative: cover → WF1 overview → WF1 screens → WF2
   * overview → WF2 screens → … → last screen of last workflow (terminal).
   * Single-workflow packages collapse to a flat list (workflows.length === 0).
   */
  function nextScreenTarget() {
    if (workflows.length) {
      var list = workflows[currentWf].screens;
      if (current < list.length - 1) return { wf: currentWf, screen: current + 1 };
      if (currentWf < workflows.length - 1) return { wf: currentWf + 1, screen: 0 };
      return null;                                       // last screen of last workflow
    }
    if (current < screens.length - 1) return { wf: 0, screen: current + 1 };
    return null;
  }
  function prevScreenTarget() {
    if (workflows.length) {
      if (current > 0) return { wf: currentWf, screen: current - 1 };
      if (currentWf > 0) {
        var prevList = workflows[currentWf - 1].screens;
        return { wf: currentWf - 1, screen: prevList.length - 1 };
      }
      return null;                                       // first screen of first workflow (cover)
    }
    if (current > 0) return { wf: 0, screen: current - 1 };
    return null;
  }
  function switchToWorkflow(idx) {
    // Sync the active-workflow index + dropdown chip. Caller follows up with
    // show(N) to land on a specific screen of the new workflow.
    if (!workflows.length || idx === currentWf) return;
    currentWf = idx;
    // Re-render the chip so its visible value reflects the new workflow
    // (the chip is rebuilt from `currentWf` by rebuildWorkflowChrome).
    rebuildWorkflowChrome();
  }
  function next() {
    var t = nextScreenTarget();
    if (!t) return;
    if (workflows.length && t.wf !== currentWf) switchToWorkflow(t.wf);
    show(t.screen);
  }
  function prev() {
    var t = prevScreenTarget();
    if (!t) return;
    if (workflows.length && t.wf !== currentWf) switchToWorkflow(t.wf);
    show(t.screen);
  }

  /* ---- Walkthrough bar -------------------------------------------------
   *
   * SINGLE SOURCE OF TRUTH for the Next-button label set.
   *
   * Two other places describe these labels — keep them in sync with the
   * function below:
   *   - reference/catalog/components/walkthrough_bar.html (header comment)
   *   - reference/catalog_chrome.md § Multi-workflow chrome / walkthrough.js
   *     mechanics table
   * If the labels change here, update those two files in the same commit.
   */
  function nextButtonLabel(currentScreen) {
    // Cover entry. In multi-workflow mode, NAME the destination so the
    // reader knows what they're committing to ("Start: Purchase"). The
    // overview pseudo-workflow is workflows[0]; the first user-facing
    // workflow is workflows[1]. In single-workflow mode (no wrappers),
    // fall back to the generic "Get Started" — there's nothing to name.
    // The chevron icon next to the label in the button markup conveys
    // the forward-direction visual — no text arrow needed.
    if (currentScreen.getAttribute("data-screen") === "cover") {
      if (workflows.length >= 2 && workflows[1]) {
        return "Start: " + workflows[1].title;
      }
      return "Get Started";
    }
    // Per-workflow overview = workflow entry: take the reader into the first
    // content screen of THIS workflow. Distinct from the cover's "Start: X"
    // label so the two entry-points read differently when seen back-to-back.
    if (currentScreen.getAttribute("data-screen-kind") === "workflow-overview") return "Get Started";
    // Last screen of a workflow that has a successor → name the destination
    // workflow on the Next button. The chevron icon in the button markup
    // provides the forward-direction arrow; the label just carries the
    // workflow name. Combined with the cover's "Multiple workflows"
    // callout — which teaches that the Next button on the last step
    // continues into the next workflow — a bare "<name>" reads cleanly.
    if (workflows.length && currentWf < workflows.length - 1) {
      var list = workflows[currentWf].screens;
      if (current === list.length - 1) {
        return workflows[currentWf + 1].title;
      }
    }
    return "Next";
  }

  function updateBar() {
    var bar = document.getElementById("mock-walkthrough");
    if (!bar) return;
    var list = activeScreens();
    var s = list[current];
    if (!s) return;
    var title = s.getAttribute("data-title") || "";
    var desc = s.getAttribute("data-desc") || "";

    var titleEl = bar.querySelector(".mock-wt-title");
    var descEl = bar.querySelector(".mock-wt-desc");
    var counterEl = bar.querySelector(".mock-wt-counter");
    /* Title gets its text only (the page title is authored short — no
       expand-on-hover affordance). The description gets a styled
       `data-mock-tooltip` so the full text reveals on hover when the
       1-line clamp ellipsis-truncates it — same immediate-show bubble
       as the per-screen dot tooltips. */
    if (titleEl) { titleEl.textContent = title; }
    if (descEl)  {
      /* Inner span carries the ellipsis-clipping `overflow: hidden`; the
         desc element stays overflow-visible so its `[data-mock-tooltip]`
         `::after` bubble can render ABOVE the desc without being clipped
         by its own ellipsis container. */
      descEl.textContent = "";
      var descTextSpan = document.createElement("span");
      descTextSpan.className = "mock-wt-desc-text";
      descTextSpan.textContent = desc;
      descEl.appendChild(descTextSpan);
      descEl.setAttribute("data-mock-tooltip", desc);
    }
    if (counterEl) counterEl.textContent = (current + 1) + " / " + list.length;

    var prevBtn = bar.querySelector("[data-mock-prev]");
    var nextBtn = bar.querySelector("[data-mock-next]");
    // Visibility tied to navigation feasibility, not list position — so
    // cross-workflow chaining works. Previous hides only on the very first
    // screen (the main cover); Next hides only on the very last screen of
    // the last workflow. Everywhere else, both stay visible.
    //
    // Hide rather than disable: disabled buttons read as "you cannot go here";
    // hiding reads as "this is the endpoint." Use the [hidden] attribute so
    // CSS `:has(> [hidden])` rules in the catalog can detect the alone-
    // button state and round the visible button's corners to match the
    // cluster's curve.
    var hasPrev = !!prevScreenTarget();
    var hasNext = !!nextScreenTarget();
    if (prevBtn) {
      prevBtn.disabled = false;
      prevBtn.hidden = !hasPrev;
    }
    if (nextBtn) {
      nextBtn.disabled = false;
      nextBtn.hidden = !hasNext;
      // The Next button has FOUR labels depending on context (the button's
      // chevron icon provides the forward-direction arrow in every case —
      // labels carry no text arrows):
      //   "Start: <name>"   on the main cover, multi-workflow mode (names
      //                     the first user-facing workflow)
      //   "Get Started"     on the main cover in single-workflow mode, AND
      //                     on every per-workflow overview (enters the
      //                     workflow's screens)
      //   "<name>"          on the last screen of a non-final workflow
      //                     (the destination workflow's name; chevron icon
      //                     signals forward-direction)
      //   "Next"            anywhere else
      // One button, four labels — back-to-back screens read differently, so
      // no two "starts" land in sequence.
      var nextLabel = nextBtn.querySelector(".mock-wt-btn-label");
      if (nextLabel) nextLabel.textContent = nextButtonLabel(s);
    }

    qsa(".mock-wt-dot", bar).forEach(function (dot, idx) {
      dot.classList.toggle("is-active", idx === current);
    });
    renderVariantChrome(bar, s);
  }

  function buildDots() {
    var holder = document.querySelector("#mock-walkthrough .mock-wt-dots");
    if (!holder) return;
    holder.innerHTML = "";
    activeScreens().forEach(function (s, idx) {
      var dot = document.createElement("span");
      dot.className = "mock-wt-dot";
      /* data-mock-tooltip (vs native title) so the CSS tooltip below
         shows immediately on hover instead of waiting for the browser's
         ~1500ms native title delay. */
      dot.setAttribute("data-mock-tooltip", s.getAttribute("data-title") || ("Screen " + (idx + 1)));
      dot.addEventListener("click", function () { show(idx); });
      holder.appendChild(dot);
    });
  }

  /* ---- Workflow selector (multi-workflow packages) --------------------- */
  function discoverWorkflows() {
    var wraps = qsa(".mock-workflow");
    if (wraps.length < 2) return;          // 0 or 1: stay single-workflow
    workflows = wraps.map(function (w) {
      return {
        slug: w.getAttribute("data-workflow") || "",
        title: w.getAttribute("data-workflow-title") || w.getAttribute("data-workflow") || "Workflow",
        screens: qsa(".mock-screen", w),
      };
    });
  }

  function rebuildWorkflowChrome() {
    var bar = document.getElementById("mock-walkthrough");
    if (!bar) return;
    var wrap = bar.querySelector(".mock-wt-workflow");
    if (!wrap) return;
    if (!workflows.length) { wrap.hidden = true; return; }
    wrap.hidden = false;
    /* Render as a CHIP (label + value + caret + custom dropdown menu) via
       the same buildChip() the variant + annotations chips use. Gives
       visual + interaction consistency across all dropdowns in the bar —
       same skin closed, same custom menu open (instead of a native <select>
       popup which renders OS-styled and breaks the visual rhythm). */
    var axis = {
      key: "_workflow",
      label: "Workflow",
      options: workflows.map(function (wf, idx) { return [String(idx), wf.title]; }),
    };
    wrap.innerHTML = "";
    var chip = buildChip(axis, String(currentWf), function (val) {
      currentWf = parseInt(val, 10) || 0;
      buildDots();
      show(0);
      rebuildWorkflowChrome();
    });
    wrap.appendChild(chip);
    buildDots();
  }

  /* ---- Variant filter-chip row (multi-axis, Odoo search-view style) ----
   * A screen declares its axes via data-mock-variant-axes (JSON):
   *   [{"key":"tracking","label":"Tracking","default":"lot",
   *     "options":[["lot","Lot"],["serial","Serial"]]},
   *    {"key":"state","label":"State","default":"unallocated",
   *     "options":[["unallocated","Unallocated"],...]}]
   * Children swap on data-mock-variant="<axis>=<value>[,<axis>=<value>]" —
   * AND-conditioned: every listed pair must match the current selection. */
  function parseAxes(screen) {
    var raw = screen.getAttribute("data-mock-variant-axes");
    if (!raw) return [];
    var parsed;
    try { parsed = JSON.parse(raw); } catch (e) { return []; }
    if (!Array.isArray(parsed)) return [];
    // FINDINGS#2: accept either `key` (canonical) or `axis` (natural English
    // alias) — they mean the same thing. Normalize to `key` for the rest of
    // the pipeline so the consumer code stays single-form.
    return parsed.map(function (a) {
      if (a && !a.key && a.axis) { a.key = a.axis; }
      return a;
    });
  }

  function currentSelection(screen, axes) {
    // Stored on the screen as data-variant-<key>; falls back to default.
    var sel = {};
    axes.forEach(function (a) {
      sel[a.key] = screen.getAttribute("data-variant-" + a.key) || a.default
        || (a.options && a.options[0] && a.options[0][0]) || "";
    });
    return sel;
  }

  function applyVariants(screen) {
    var axes = parseAxes(screen);
    if (!axes.length) return;
    var sel = currentSelection(screen, axes);
    qsa("[data-mock-variant]", screen).forEach(function (el) {
      if (el.closest(".mock-screen") !== screen) return;
      var spec = el.getAttribute("data-mock-variant") || "";
      // Cross-axis AND: comma-separated pairs (`a=x,b=y` → a==x AND b==y).
      // Same-axis OR: pipe-separated values (`a=x|y|z` → a in {x,y,z}).
      // Mirrors real Odoo's view-attrs convention (`('state','in',[...])`).
      var pairs = spec.split(",").map(function (p) { return p.trim(); }).filter(Boolean);
      var match = pairs.every(function (p) {
        var bits = p.split("=");
        if (bits.length !== 2) return false;
        var axis = bits[0].trim();
        var values = bits[1].split("|").map(function (v) { return v.trim(); });
        return values.indexOf(sel[axis]) !== -1;
      });
      el.classList.toggle("is-variant-active", match);
    });
  }

  function buildChip(axis, currentValue, onPick) {
    var chip = document.createElement("div");
    chip.className = "mock-wt-chip";
    chip.setAttribute("data-axis", axis.key);

    var label = document.createElement("span");
    label.className = "mock-wt-chip-label";
    label.textContent = (axis.label || axis.key) + ":";
    chip.appendChild(label);

    var currentLabel = (axis.options.find(function (o) { return o[0] === currentValue; }) || [currentValue, currentValue])[1];

    var button = document.createElement("button");
    button.type = "button";
    button.className = "mock-wt-chip-button";
    button.innerHTML = '<span class="mock-wt-chip-value"></span> <svg class="o_icon o_icon_xs"><use href="#o-caret-down"/></svg>';
    var valueSpan = button.querySelector(".mock-wt-chip-value");
    valueSpan.textContent = currentLabel;
    /* Hover-truncation tooltip: when the chip's value ellipsis-truncates
       (narrow 2-chip case, long workflow name), `data-mock-tooltip` on
       the chip reveals the full "Label: Value" via the same styled
       immediate-show bubble used by the per-screen dot tooltips. The
       attribute lives on the CHIP (not the value span) so the bubble's
       `::after` isn't clipped by the value's `overflow: hidden`. */
    chip.setAttribute("data-mock-tooltip", axis.label + ": " + currentLabel);
    chip.appendChild(button);

    var menu = document.createElement("div");
    menu.className = "mock-wt-chip-menu";
    axis.options.forEach(function (o) {
      var item = document.createElement("button");
      item.type = "button";
      item.className = "mock-wt-chip-item" + (o[0] === currentValue ? " is-active" : "");
      item.textContent = o[1];
      item.addEventListener("click", function (e) {
        e.stopPropagation();
        onPick(o[0]);
      });
      menu.appendChild(item);
    });
    chip.appendChild(menu);

    button.addEventListener("click", function (e) {
      e.stopPropagation();
      // Close other open chips ACROSS THE DOCUMENT (not just this wrap) so
      // opening the workflow chip closes any open variant chip and vice
      // versa — only one dropdown visible at a time, anywhere on the bar.
      qsa(".mock-wt-chip.is-open").forEach(function (c) {
        if (c !== chip) c.classList.remove("is-open");
      });
      chip.classList.toggle("is-open");
    });
    return chip;
  }

  function renderVariantChrome(bar, screen) {
    var wrap = bar.querySelector(".mock-wt-chips");
    if (!wrap) return;
    var axes = parseAxes(screen);
    if (!axes.length) { wrap.hidden = true; wrap.innerHTML = ""; return; }
    wrap.hidden = false;
    var sel = currentSelection(screen, axes);
    applyVariants(screen);
    wrap.innerHTML = "";

    // Pick chrome mode: parallel (1-2 axes) or dependent (>=3 axes, or
    // explicit data-mock-variant-mode="dependent").
    var explicitMode = screen.getAttribute("data-mock-variant-mode");
    var dependent = explicitMode === "dependent" || (!explicitMode && axes.length >= 3);

    if (!dependent) {
      // Parallel chips: one per axis
      axes.forEach(function (axis) {
        var chip = buildChip(axis, sel[axis.key], function (val) {
          screen.setAttribute("data-variant-" + axis.key, val);
          renderVariantChrome(bar, screen);
        });
        wrap.appendChild(chip);
      });
    } else {
      // Dependent pair: Type chip (which axis to pivot) + Value chip (the chosen axis's value)
      var typeKey = screen.getAttribute("data-variant-pivot") || axes[0].key;
      var typeAxis = {
        key: "_type",
        label: "Variant",
        options: axes.map(function (a) { return [a.key, a.label || a.key]; }),
      };
      var typeChip = buildChip(typeAxis, typeKey, function (val) {
        screen.setAttribute("data-variant-pivot", val);
        renderVariantChrome(bar, screen);
      });
      wrap.appendChild(typeChip);

      var activeAxis = axes.find(function (a) { return a.key === typeKey; }) || axes[0];
      var valueChip = buildChip(activeAxis, sel[activeAxis.key], function (val) {
        screen.setAttribute("data-variant-" + activeAxis.key, val);
        renderVariantChrome(bar, screen);
      });
      // Value chip's own label says "Value" generically; the Type chip already
      // shows which axis is being pivoted.
      var valueLabel = valueChip.querySelector(".mock-wt-chip-label");
      if (valueLabel) valueLabel.textContent = "Value:";
      wrap.appendChild(valueChip);
    }

    // Click-outside handling is now global (wired once in init() via
    // wireChipCloseOnOutsideClick) so it covers the workflow chip + the
    // annotations chip too, not only the variant chips wrap.
  }

  /* ---- Annotation markers + field-help: ONE body-level floating tooltip ---
   * Rendered on <body> with position:fixed so NO ancestor overflow (sheet,
   * list, notebook) can clip it and it always sits on the top layer. Used by
   * numbered .mock-marker (click) and custom-field .o_field_help "?" (hover). */
  var floatEl = null, floatAnchor = null;

  function escHtml(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function floatLayer() {
    if (!floatEl) {
      floatEl = document.createElement("div");
      floatEl.className = "mock-float";
      document.body.appendChild(floatEl);
    }
    return floatEl;
  }

  function positionFloat(anchor) {
    var el = floatLayer();
    var r = anchor.getBoundingClientRect();
    var vw = document.documentElement.clientWidth;
    var vh = document.documentElement.clientHeight;
    var w = el.offsetWidth, h = el.offsetHeight;
    var left = r.left;
    var top = r.bottom + 8;                       // default: below the anchor
    if (left + w > vw - 8) left = vw - 8 - w;     // clamp to right edge
    if (left < 8) left = 8;
    if (top + h > vh - 8) top = r.top - 8 - h;    // flip above if no room below
    if (top < 8) top = 8;
    el.style.left = Math.round(left) + "px";
    el.style.top = Math.round(top) + "px";
  }

  function showFloat(anchor, html) {
    var el = floatLayer();
    floatAnchor = anchor;
    el.innerHTML = html;
    /* Tag the float so the cover-page example marker's tooltip stays
       visible even when Annotations is toggled off (the example marker is
       always-visible instructional content). */
    el.classList.toggle("is-from-example", anchor.classList.contains("mock-marker-example"));
    el.classList.add("is-shown");
    positionFloat(anchor);
  }

  function hideFloat() {
    floatAnchor = null;
    qsa(".mock-marker.is-open").forEach(function (m) { m.classList.remove("is-open"); });
    if (floatEl) floatEl.classList.remove("is-shown");
  }
  // Kept name: show()/Esc/nav all call this to dismiss an open annotation.
  function closeAllCallouts() { hideFloat(); }

  function markerHtml(marker) {
    return '<div class="mock-float-note">' + escHtml(marker.getAttribute("data-note") || "") + "</div>";
  }

  // Odoo-style help for a CUSTOM field: help text (highlighted) + attribute list.
  function fieldHelpHtml(el) {
    var html = "";
    var help = el.getAttribute("data-help");
    if (help) html += '<div class="mock-float-help">' + escHtml(help) + "</div>";
    var rows = "";
    ["label", "field", "model", "type", "readonly"].forEach(function (k) {
      var v = el.getAttribute("data-" + k);
      if (v) rows += "<li><b>" + k.charAt(0).toUpperCase() + k.slice(1) +
        ":</b> <code>" + escHtml(v) + "</code></li>";
    });
    if (rows) html += '<ul class="mock-float-attrs">' + rows + "</ul>";
    return html || '<div class="mock-float-note">(custom field)</div>';
  }

  function wireMarkers() {
    // Numbered markers — click toggles the floating note.
    document.addEventListener("click", function (e) {
      var marker = e.target.closest ? e.target.closest(".mock-marker") : null;
      if (marker) {
        var reopen = !(marker.classList.contains("is-open") && floatAnchor === marker);
        hideFloat();
        if (reopen) { marker.classList.add("is-open"); showFloat(marker, markerHtml(marker)); }
        return;
      }
      if (!(e.target.closest && e.target.closest(".mock-float"))) hideFloat();
    });

    // Custom-field "?" — hover (and click, for touch) shows the attribute tooltip.
    qsa(".o_field_help").forEach(function (el) {
      el.addEventListener("mouseenter", function () { showFloat(el, fieldHelpHtml(el)); });
      el.addEventListener("mouseleave", function () { if (floatAnchor === el) hideFloat(); });
      el.addEventListener("click", function (e) { e.stopPropagation(); showFloat(el, fieldHelpHtml(el)); });
    });

    // Keep the tooltip glued + on-screen when the page or a container scrolls.
    window.addEventListener("scroll", function () { if (floatAnchor) positionFloat(floatAnchor); }, true);
    window.addEventListener("resize", function () { if (floatAnchor) positionFloat(floatAnchor); });
  }

  /* Annotations toggle rendered as a chip (label + value + caret), same
     pattern as the variant chips above. Two values: Show / Hide; default
     Show. Selecting Hide adds `mock-annotations-off` to <body> (which
     hides all pinned markers + the floating tooltip via annotations.css);
     selecting Show removes the class. Re-renders on each pick so the chip
     value reflects the live state. */
  function renderAnnotationsChip() {
    var host = document.querySelector(".mock-wt-toggle");
    if (!host) return;
    var current = document.body.classList.contains("mock-annotations-off") ? "hide" : "show";
    var axis = {
      key: "_annotations",
      label: "Annotations",
      options: [["show", "Show"], ["hide", "Hide"]],
    };
    host.innerHTML = "";
    var chip = buildChip(axis, current, function (val) {
      var off = (val === "hide");
      document.body.classList.toggle("mock-annotations-off", off);
      if (off) hideFloat();
      renderAnnotationsChip();
    });
    host.appendChild(chip);
  }

  function wireAnnotationToggle() {
    /* Back-compat: if an old-style <input id="mock-annotations-toggle"> is
       still in the page, keep wiring its change event. New mocks render the
       chip via renderAnnotationsChip() at init time. */
    var toggle = document.getElementById("mock-annotations-toggle");
    if (toggle) {
      toggle.addEventListener("change", function () {
        document.body.classList.toggle("mock-annotations-off", !toggle.checked);
        if (!toggle.checked) hideFloat();
      });
    }
    renderAnnotationsChip();
  }

  /* ---- Interactive elements (v2): tabs, modals, toggles, toasts -------- */
  // Notebook tabs that actually switch panels within a screen.
  // <span class="nav-link" data-mock-tab="other"> ... <div data-mock-tabpanel="other">
  function switchTab(el) {
    var key = el.getAttribute("data-mock-tab");
    var scope = el.closest(".o_notebook") || el.closest(".mock-screen") || document;
    qsa("[data-mock-tab]", scope).forEach(function (t) {
      t.classList.toggle("active", t === el);
    });
    qsa("[data-mock-tabpanel]", scope).forEach(function (p) {
      p.classList.toggle("is-active-tab", p.getAttribute("data-mock-tabpanel") === key);
    });
  }

  // In-place modal: <div class="o_dialog_backdrop" data-mock-modal="ID"> opened by
  // [data-mock-modal-open="ID"], closed by [data-mock-modal-close] / Esc / backdrop.
  function openModal(id) {
    var m = document.querySelector('[data-mock-modal="' + id + '"]');
    if (m) m.classList.add("is-open");
  }
  function closeModals() {
    // Skip "blocking" modals — those that are the persistent rendering of a
    // guard State variant (UserError / ValidationError dialogs). Otherwise
    // screen-show's auto-closeModals would dismiss them on every navigation
    // and they'd never be visible in static review. User can still close
    // them via a button carrying data-mock-modal-close, which uses
    // closeNearestModal() to target only that specific modal.
    qsa('[data-mock-modal].is-open').forEach(function (m) {
      if (m.classList.contains("mock-blocking-modal")) return;
      m.classList.remove("is-open");
    });
  }
  function closeNearestModal(el) {
    var modal = el.closest('[data-mock-modal]');
    if (modal) modal.classList.remove("is-open");
  }

  // Toggle (dropdown / expander): [data-mock-toggle="ID"] flips [data-mock-toggleable="ID"].
  function toggleEl(id) {
    var t = document.querySelector('[data-mock-toggleable="' + id + '"]');
    if (!t) return;
    var wasOpen = t.classList.contains("is-open");
    closeAllToggles();
    if (!wasOpen) t.classList.add("is-open");
  }
  function closeAllToggles() {
    qsa('[data-mock-toggleable].is-open').forEach(function (t) { t.classList.remove("is-open"); });
  }

  // Transient Odoo-style toast: [data-mock-toast="message"] (optional
  // data-mock-toast-type="success|warning|danger|info").
  function showToast(msg, type) {
    var holder = document.getElementById("mock-toast-holder");
    if (!holder) {
      holder = document.createElement("div");
      holder.id = "mock-toast-holder";
      holder.className = "o_notification_manager";
      document.body.appendChild(holder);
    }
    var t = document.createElement("div");
    t.className = "o_notification" + (type ? " o_notification_" + type : " o_notification_success");
    t.textContent = msg;
    holder.appendChild(t);
    requestAnimationFrame(function () { t.classList.add("is-shown"); });
    setTimeout(function () {
      t.classList.remove("is-shown");
      setTimeout(function () { if (t.parentNode) t.parentNode.removeChild(t); }, 300);
    }, 2600);
  }

  /* ---- Cross-screen variant mutation -----------------------------------
   * data-mock-set-variant="<screen-id>:<axis>=<value>[;<screen>:<axis>=<value>...]"
   * Runs BEFORE the click's data-mock-goto, so the target screen renders
   * with the new variant already applied. Without this, the chip-row chrome
   * is the only way to change a screen's State / Tracking / etc., breaking
   * the interactive path: clicking "Save" in the picker can't naturally
   * advance the Quote to state=allocated. */
  function applySetVariant(el) {
    var spec = el.getAttribute("data-mock-set-variant");
    if (!spec) return;
    spec.split(";").forEach(function (one) {
      var parts = one.split(":");
      if (parts.length !== 2) return;
      var screenId = parts[0].trim();
      var axisValue = parts[1].split("=");
      if (axisValue.length !== 2) return;
      var axisKey = axisValue[0].trim();
      var value = axisValue[1].trim();
      if (!screenId || !axisKey || !value) return;
      var targetScreen = findScreenAnywhere(screenId);
      if (targetScreen) {
        targetScreen.setAttribute("data-variant-" + axisKey, value);
        // If the target screen is already active, re-apply variants immediately
        // so the chrome reflects the change without needing a goto.
        if (targetScreen.classList.contains("is-active")) {
          applyVariants(targetScreen);
          updateBar();
        }
      }
    });
  }

  /* ---- Navigation + action wiring -------------------------------------- */
  function wireActions() {
    document.addEventListener("click", function (e) {
      if (!e.target.closest) return;
      var el = e.target.closest(
        "[data-mock-goto],[data-mock-next],[data-mock-prev]," +
        "[data-mock-tab],[data-mock-modal-open],[data-mock-modal-close]," +
        "[data-mock-toggle],[data-mock-toast],[data-mock-set-variant]"
      );
      if (!el) return;
      if (el.classList.contains("mock-marker")) return; // markers handle their own clicks
      e.preventDefault();
      // Side effects first (these can co-occur with a goto on the same element).
      if (el.hasAttribute("data-mock-set-variant")) applySetVariant(el);
      if (el.hasAttribute("data-mock-toast")) {
        showToast(el.getAttribute("data-mock-toast"), el.getAttribute("data-mock-toast-type"));
      }
      // User-triggered close: target the modal containing the click (works
      // for both blocking and non-blocking modals); closeModals() is the
      // automatic close for navigation, which respects the blocking class.
      if (el.hasAttribute("data-mock-modal-close")) closeNearestModal(el);
      // Self-contained interactions (no navigation).
      if (el.hasAttribute("data-mock-tab")) return switchTab(el);
      if (el.hasAttribute("data-mock-toggle")) return toggleEl(el.getAttribute("data-mock-toggle"));
      if (el.hasAttribute("data-mock-modal-open")) return openModal(el.getAttribute("data-mock-modal-open"));
      // Navigation.
      if (el.hasAttribute("data-mock-next")) return next();
      if (el.hasAttribute("data-mock-prev")) return prev();
      var target = el.getAttribute("data-mock-goto");
      if (target) { closeModals(); goTo(target); }
    });

    document.addEventListener("keydown", function (e) {
      if (e.target && /^(INPUT|TEXTAREA|SELECT)$/.test(e.target.tagName)) return;
      if (e.key === "Escape") { closeModals(); closeAllToggles(); closeAllCallouts(); return; }
      if (e.key === "ArrowRight") next();
      else if (e.key === "ArrowLeft") prev();
    });
  }

  /* ---- step-axes page-number resolver ----------------------------------
   * A chip carries `data-mock-page-ref="<screen-id>"` on
   * `.mock-step-axes-page-num` (or on its `.mock-step-axes` parent).
   * Compute "Page N" at init time from the screen's position in the
   * walkthrough order. SCOPE is workflow-local in multi-workflow mode:
   *
   *   - If the chip lives inside a `.mock-workflow`, "Page N" counts
   *     within that workflow's screens (matches the bar's counter on
   *     the referenced screen).
   *   - Otherwise (no wrapper / orphan), fall back to the global list
   *     excluding the cover (legacy single-workflow behavior).
   *
   * Authors never hand-write a page number; the resolver keeps it
   * accurate across screen reorders. Missing refs get "Page ?" so
   * the lint can flag them.
   */
  function resolveStepAxesPageNumbers() {
    var globalFallback = screens.filter(function (s) {
      return s.getAttribute("data-screen") !== "cover";
    });
    qsa(".mock-step-axes-page-num[data-mock-page-ref], " +
        ".mock-step-axes[data-mock-page-ref] > .mock-step-axes-page-num").forEach(function (cell) {
      var host = cell.hasAttribute("data-mock-page-ref")
        ? cell
        : cell.parentNode;
      var ref = host.getAttribute("data-mock-page-ref");
      if (!ref) return;
      // Determine the scope: workflow-local when the chip sits inside a
      // .mock-workflow wrapper (so "Page N" matches the counter the user
      // sees when they're ON that screen).
      var chipScreen = cell.closest(".mock-screen");
      var wrapper = chipScreen ? chipScreen.closest(".mock-workflow") : null;
      var scope = wrapper ? qsa(".mock-screen", wrapper) : globalFallback;
      var idx = -1;
      for (var i = 0; i < scope.length; i++) {
        if (scope[i].getAttribute("data-screen") === ref) { idx = i; break; }
      }
      if (idx < 0) {
        cell.textContent = "Page ?";
        cell.setAttribute("data-mock-page-ref-resolved", "missing");
      } else {
        cell.textContent = "Page " + (idx + 1);
        cell.setAttribute("data-mock-page-ref-resolved", String(idx + 1));
      }
    });
  }

  function wireChipCloseOnOutsideClick() {
    /* Single document-level click handler — closes EVERY open chip in
       the bar (workflow chip, variant chips, annotations chip) when the
       user clicks anywhere that isn't a chip. Chip buttons stopPropagation
       on their own clicks so this handler doesn't fire from chip itself. */
    document.addEventListener("click", function (e) {
      if (!e.target.closest || !e.target.closest(".mock-wt-chip")) {
        qsa(".mock-wt-chip.is-open").forEach(function (c) {
          c.classList.remove("is-open");
        });
      }
    });
  }

  function init() {
    screens = qsa(".mock-screen");
    if (!screens.length) return;
    discoverWorkflows();
    rebuildWorkflowChrome();
    buildDots();
    resolveStepAxesPageNumbers();
    wireMarkers();
    wireAnnotationToggle();
    wireActions();
    wireChipCloseOnOutsideClick();
    // Honour a #screen-ID hash on load, else start at the first screen.
    var hash = (window.location.hash || "").replace(/^#/, "");
    if (hash) {
      goTo(hash);
    } else {
      show(0);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
