/*!
 * Renan the Teacher — tag filter on the reading hub (exercises.html)
 *
 * Each level has its own independent filter. Clicking chips narrows that
 * level's cards; the other levels are untouched, because a student browsing B1
 * has no reason to have their A2 view changed under them.
 *
 * Chips combine as OR within a row and AND across rows: picking Travel and
 * Food shows texts that are either, while picking Travel and Passive voice
 * shows travel texts that practice the passive. That is what the two rows look
 * like they promise, and the alternative -- OR everywhere -- makes the grammar
 * row useless the moment a subject is also selected.
 *
 * Markup comes from scripts/build_exercises_hub.py; this file only wires it up.
 * With JavaScript off, every card stays visible and the chips simply do
 * nothing, which is the right failure for a page whose job is to list texts.
 */
(function () {
  "use strict";

  function setup(root) {
    var chips = Array.prototype.slice.call(root.querySelectorAll("[data-tag]"));
    if (!chips.length) return;
    var section = root.closest("section");
    if (!section) return;
    var cards = Array.prototype.slice.call(section.querySelectorAll(".lesson-card[data-tags]"));
    var status = root.querySelector("[data-tag-status]");
    var clear = root.querySelector("[data-tag-clear]");
    var total = cards.length;

    function active() {
      return chips.filter(function (c) { return c.getAttribute("aria-pressed") === "true"; })
                  .map(function (c) { return c.getAttribute("data-tag"); });
    }

    function apply() {
      var on = active();
      // Group the selection the same way the rows are grouped, so each row is
      // an OR and the rows are ANDed together.
      var topics = on.filter(function (t) { return t.indexOf("topic:") === 0; });
      var gram = on.filter(function (t) { return t.indexOf("g:") === 0; });
      var shown = 0;

      cards.forEach(function (card) {
        var tags = (card.getAttribute("data-tags") || "").split(/\s+/);
        var ok = true;
        if (topics.length) {
          ok = topics.some(function (t) { return tags.indexOf(t) !== -1; });
        }
        if (ok && gram.length) {
          ok = gram.some(function (t) { return tags.indexOf(t) !== -1; });
        }
        card.hidden = !ok;
        if (ok) shown++;
      });

      // Hide a topic heading whose whole grid has gone, so no heading is left
      // standing above an empty space.
      Array.prototype.forEach.call(section.querySelectorAll(".grid"), function (grid) {
        var any = Array.prototype.some.call(grid.querySelectorAll(".lesson-card"),
                                            function (c) { return !c.hidden; });
        grid.hidden = !any;
        var head = grid.previousElementSibling;
        if (head && head.classList.contains("topic-group")) head.hidden = !any;
      });

      if (status) {
        status.textContent = on.length
          ? (shown === 0
              ? "No text in this level matches all of those. Try removing one."
              : "Showing " + shown + " of " + total + " texts.")
          : "Showing all " + total + " texts.";
      }
      if (clear) clear.hidden = !on.length;
    }

    chips.forEach(function (chip) {
      chip.addEventListener("click", function () {
        chip.setAttribute("aria-pressed",
          chip.getAttribute("aria-pressed") === "true" ? "false" : "true");
        apply();
      });
    });

    if (clear) {
      clear.addEventListener("click", function () {
        chips.forEach(function (c) { c.setAttribute("aria-pressed", "false"); });
        apply();
        chips[0].focus();
      });
    }
  }

  function init() {
    Array.prototype.forEach.call(document.querySelectorAll("[data-tag-filter]"), setup);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
