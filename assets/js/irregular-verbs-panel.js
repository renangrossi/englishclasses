/*!
 * Renan the Teacher — Floating Irregular Verbs panel
 * Included only on exercise pages whose grammar point genuinely needs
 * irregular past-simple/past-participle recall (passive voice, perfect
 * tenses, 2nd/3rd conditionals, modal perfect, reported-speech
 * backshifting, etc.) — see each such page's own <script> include.
 *
 * Reuses the single 213-row table already authored in
 * irregular-verbs.html (Extras) instead of keeping a second copy: the
 * first time a student opens this panel, it fetches that page, lifts
 * out just its <table data-verb-table>, and wires up the exact same
 * filtering logic irregular-verbs.js itself uses (via
 * window.RenanIrregularVerbs.initFilter — see that file), scoped to
 * this panel. Cached in the DOM after the first successful fetch, so
 * re-opening later is instant with no extra request.
 *
 * Trigger + panel markup is static HTML already on the page (same
 * approach as assets/js/ai-teacher.js / assets/js/dict-widget.js —
 * this file only wires up behaviour, matching their exact pattern for
 * positioning, focus handling, body-scroll-lock and outside-click/
 * Escape handling rather than inventing a new one).
 */
(function () {
  "use strict";

  // Captured here, at top-level synchronous execution — document.
  // currentScript is only non-null while a script is actually running,
  // so this has to be read now, not inside a later callback. Anchoring
  // the verb-list URL to *this script's own* location (always
  // assets/js/irregular-verbs-panel.js, two directories below the site
  // root, regardless of how deep the page including it lives) avoids
  // hard-coding or re-deriving the current page's own depth — this
  // keeps working unchanged even if this panel is ever added to a page
  // at a different depth than today's.
  var THIS_SCRIPT_URL = document.currentScript && document.currentScript.src;

  var trigger = document.querySelector("[data-irregular-verbs-toggle]");
  if (!trigger) return;
  var panel = document.querySelector("[data-irregular-verbs-panel]");
  if (!panel) return;
  var closeBtn = panel.querySelector("[data-irregular-verbs-close]");
  var body = panel.querySelector("[data-irregular-verbs-body]");
  var loading = panel.querySelector("[data-irregular-verbs-loading]");
  var input = panel.querySelector("[data-verb-filter]");

  function verbListUrl() {
    if (THIS_SCRIPT_URL) {
      try {
        return new URL("../../irregular-verbs.html", THIS_SCRIPT_URL).href;
      } catch (err) {
        /* fall through to the relative fallback below */
      }
    }
    // Defensive fallback only, if document.currentScript was ever
    // unavailable — every page this ships on today is two directories
    // deep, matching every other asset reference already on it.
    return "../../irregular-verbs.html";
  }

  // Identical shared-counter scroll lock to ai-teacher.js's and
  // dict-widget.js's own lockBodyScrollForPanel/unlockBodyScrollForPanel
  // (window.__rtPanelLock), so this panel and either of those never
  // fight over re-enabling page scroll if more than one is open.
  var lockedBodyScroll = false;
  function lockBodyScrollForPanel() {
    if (!(window.matchMedia && window.matchMedia("(max-width: 640px)").matches)) return;
    window.__rtPanelLock = (window.__rtPanelLock || 0) + 1;
    lockedBodyScroll = true;
    if (window.__rtPanelLock > 1) return;
    window.__rtPanelLockY = window.scrollY || window.pageYOffset || 0;
    var s = document.body.style;
    s.position = "fixed";
    s.top = "-" + window.__rtPanelLockY + "px";
    s.left = "0";
    s.right = "0";
    s.width = "100%";
  }
  function unlockBodyScrollForPanel() {
    if (!lockedBodyScroll) return;
    lockedBodyScroll = false;
    window.__rtPanelLock = Math.max(0, (window.__rtPanelLock || 1) - 1);
    if (window.__rtPanelLock > 0) return;
    var y = window.__rtPanelLockY || 0;
    var s = document.body.style;
    s.position = "";
    s.top = "";
    s.left = "";
    s.right = "";
    s.width = "";
    window.scrollTo(0, y);
  }

  var loadState = "idle"; // idle | loading | ready | error

  function loadVerbTable() {
    if (loadState === "loading" || loadState === "ready") return;
    loadState = "loading";
    fetch(verbListUrl())
      .then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status);
        return res.text();
      })
      .then(function (html) {
        var doc = new DOMParser().parseFromString(html, "text/html");
        var table = doc.querySelector("[data-verb-table]");
        if (!table) throw new Error("verb table not found in fetched page");
        // Same .table-scroll wrapper irregular-verbs.html itself uses
        // (assets/css/lessons.css) so a very narrow phone can scroll
        // the table sideways instead of it overflowing the panel.
        var scroll = document.createElement("div");
        scroll.className = "table-scroll";
        scroll.appendChild(table);
        // Replaces the "Loading…" placeholder in place, so the table
        // lands between the count notice and the empty-state notice —
        // the same order irregular-verbs.html itself uses.
        if (loading && loading.parentNode) {
          loading.parentNode.insertBefore(scroll, loading);
          loading.parentNode.removeChild(loading);
        } else {
          body.appendChild(scroll);
        }
        if (window.RenanIrregularVerbs && window.RenanIrregularVerbs.initFilter) {
          window.RenanIrregularVerbs.initFilter(panel);
        }
        loadState = "ready";
      })
      .catch(function () {
        loadState = "error";
        if (loading) {
          loading.textContent = "";
          loading.appendChild(document.createTextNode("Couldn't load the verb list right now — "));
          var link = document.createElement("a");
          link.href = verbListUrl();
          link.target = "_blank";
          link.rel = "noopener";
          link.textContent = "open it in a new tab instead";
          loading.appendChild(link);
          loading.appendChild(document.createTextNode("."));
        }
      });
  }

  function open() {
    panel.hidden = false;
    trigger.setAttribute("aria-expanded", "true");
    lockBodyScrollForPanel();
    loadVerbTable();
    // Focused immediately, exactly like the Dictionary and AI Teacher
    // panels focus their own primary field on open — even before the
    // fetch resolves, so a student can start typing right away and the
    // list is already filtered once it lands.
    if (input) input.focus();
  }

  // returnFocus: true always sends focus back to the trigger (the ×
  // button and Escape are an unambiguous "I'm done" — nothing else is
  // competing for focus). For an outside click, only do that if the
  // click didn't already hand focus to something else on the page
  // (e.g. the student clicked an exercise input) — respecting that is
  // more correct than yanking focus back to the trigger over it.
  function close(returnFocus) {
    panel.hidden = true;
    trigger.setAttribute("aria-expanded", "false");
    unlockBodyScrollForPanel();
    if (returnFocus || document.activeElement === document.body) {
      trigger.focus();
    }
  }

  trigger.addEventListener("click", function (e) {
    // Keeps this click from reaching the document-level outside-click
    // listener below in the same tick it opens the panel.
    e.stopPropagation();
    if (panel.hidden) open();
    else close(true);
  });
  closeBtn.addEventListener("click", function () { close(true); });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !panel.hidden) close(true);
  });
  // Only closes on a click that both starts and ends outside the panel
  // — identical fix to dict-widget.js's own pointerDownOutside
  // tracking, otherwise selecting text in the search input (press
  // inside, release outside while dragging) closes the panel
  // mid-selection.
  var pointerDownOutside = false;
  document.addEventListener("pointerdown", function (e) {
    if (panel.hidden) return;
    pointerDownOutside = !(panel.contains(e.target) || trigger.contains(e.target));
  });
  document.addEventListener("click", function (e) {
    if (panel.hidden) return;
    if (panel.contains(e.target) || trigger.contains(e.target)) return;
    if (!pointerDownOutside) return;
    close(false);
  });
  panel.addEventListener("click", function (e) { e.stopPropagation(); });
})();
