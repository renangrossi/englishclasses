/*!
 * Renan the Teacher — Irregular Verbs List (irregular-verbs.html)
 * Progressive enhancement only: the full 213-row table is already in
 * the page's static HTML (works with no JS, indexable, printable).
 * This adds live client-side filtering across all three columns (base
 * form, simple past, past participle) as the student types.
 *
 * initFilter(root) is exposed on window.RenanIrregularVerbs so the
 * floating Irregular Verbs panel (assets/js/irregular-verbs-panel.js,
 * shown on exercise pages whose grammar point needs irregular-verb
 * recall) can reuse this exact filtering logic against its own,
 * separately-fetched copy of this same table instead of
 * re-implementing it — see that file for why. Passing a root narrower
 * than `document` (e.g. the panel's own container) scopes every
 * lookup to inside it, so this keeps working unchanged if a page ever
 * has more than one such table.
 */
(function () {
  "use strict";

  function initFilter(root) {
    root = root || document;
    var input = root.querySelector("[data-verb-filter]");
    var tbody = root.querySelector("[data-verb-tbody]");
    if (!input || !tbody) return null;

    var countNotice = root.querySelector("[data-verb-count]");
    var emptyNotice = root.querySelector("[data-verb-empty]");
    var emptyTerm = root.querySelector("[data-verb-empty-term]");
    var rows = Array.prototype.slice.call(tbody.querySelectorAll("tr"));
    var total = rows.length;

    function filter() {
      var q = input.value.trim().toLowerCase();
      var shown = 0;
      rows.forEach(function (row) {
        var match = !q || row.textContent.toLowerCase().indexOf(q) !== -1;
        row.hidden = !match;
        if (match) shown++;
      });

      if (emptyNotice) emptyNotice.hidden = shown !== 0;
      if (emptyTerm) emptyTerm.textContent = input.value.trim();
      if (countNotice) {
        countNotice.hidden = shown === 0;
        var text = q
          ? "Showing " + shown + " of " + total + " verbs matching “" + input.value.trim() + "”."
          : "Showing all " + total + " verbs. A few (like “burn” or “dream”) have two accepted forms — both are shown, separated by a slash.";
        // First child text node holds the message; a leading icon
        // <svg> (if any) stays untouched. A consumer that didn't
        // pre-render a text node (e.g. an empty notice element built
        // fresh, rather than authored with one) gets one added instead
        // of this silently doing nothing — irregular-verbs.html itself
        // always has one already, so this is a no-op there.
        var textNode = Array.prototype.find.call(countNotice.childNodes, function (n) { return n.nodeType === 3; });
        if (textNode) textNode.textContent = text;
        else countNotice.appendChild(document.createTextNode(text));
      }
    }

    var debounceTimer;
    input.addEventListener("input", function () {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(filter, 80);
    });

    // Populates the initial "Showing all N verbs…" state from the
    // actual row count rather than requiring it to be pre-rendered —
    // on irregular-verbs.html itself this reproduces the exact text
    // already baked into the static HTML (harmless no-op-looking
    // update); for a consumer like the floating panel, whose table
    // only exists once fetched, this is what populates the count the
    // first time.
    filter();

    return { filter: filter, total: total };
  }

  window.RenanIrregularVerbs = window.RenanIrregularVerbs || {};
  window.RenanIrregularVerbs.initFilter = initFilter;

  // Standalone page: wire up immediately, exactly as before this file
  // was refactored to also expose initFilter() for reuse.
  if (document.querySelector("[data-verb-filter]")) {
    initFilter(document);
  }
})();
