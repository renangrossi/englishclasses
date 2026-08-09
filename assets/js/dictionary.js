/*!
 * Renan the Teacher — Dictionary word lookup
 * Rewrites every dictionary/thesaurus/pronunciation link on the page
 * to point at whatever word the user has typed, entirely client-side.
 */
(function () {
  "use strict";

  var input = document.querySelector("[data-dict-word]");
  if (!input) return;
  var cards = document.querySelectorAll(".dict-card[data-url-template]");

  function update() {
    var raw = input.value.trim();
    var word = raw || "hello";
    var encoded = encodeURIComponent(word.toLowerCase());
    cards.forEach(function (card) {
      var tmpl = card.getAttribute("data-url-template");
      var link = card.querySelector("[data-dict-link]");
      if (!link) return;
      link.href = tmpl.replace("{word}", encoded);
      link.textContent = "";
      var icon = link.querySelector("svg");
      if (icon) link.appendChild(icon);
      link.appendChild(document.createTextNode(raw ? "Look up \u201c" + raw + "\u201d" : "Look up"));
    });
  }

  input.addEventListener("input", update);
  update();

  // Enter key opens a random one of the four core dictionaries
  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
      var primaryLinks = document.querySelectorAll(".card--feature.dict-card [data-dict-link]");
      if (!primaryLinks.length) return;
      var pick = primaryLinks[Math.floor(Math.random() * primaryLinks.length)];
      window.open(pick.href, "_blank", "noopener");
    }
  });
})();
