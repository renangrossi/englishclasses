/*!
 * Renan the Teacher — Interactive Exercise Engine
 * ------------------------------------------------------------------
 * A small, dependency-free, data-driven engine for classroom-style
 * exercises. New exercises are added by editing a JSON block, not by
 * writing JavaScript — see any lesson page's
 * <script type="application/json" class="exercise-data"> block for
 * a live example of the format.
 *
 * Supported "type" values:
 *   multiple-choice, true-false, fill-blank, matching, ordering,
 *   correction, typing, reading-comprehension, vocabulary
 *
 * Contract
 * --------
 * Each `.exercise-block` element carries a child
 * <script type="application/json" class="exercise-data"> with a
 * single exercise definition (see SCHEMA below). On DOMContentLoaded
 * the engine finds every such pair, renders the questions, and wires
 * up Submit / Retry-incorrect behaviour. Nothing here talks to a
 * server — everything is graded in the browser, which is what keeps
 * this deployable as a static GitHub Pages site.
 *
 * SCHEMA (informal):
 * {
 *   "id": "unique-id",
 *   "type": "multiple-choice" | "true-false" | "fill-blank" | "matching"
 *         | "ordering" | "correction" | "typing" | "reading-comprehension"
 *         | "vocabulary",
 *   "title": "Exercise title",
 *   "instructions": "One line of instructions shown under the title.",
 *   "passage": "Optional HTML passage, used by reading-comprehension.",
 *   "items": [ ...type-specific items, see renderers below... ]
 * }
 *
 * Every item's "explanation" is shown after grading regardless of whether
 * the answer was correct — write it as a short rule/reason a student can
 * learn from, not just "Correct answer."
 *
 * fill-blank items render a <select> dropdown per blank when "options" is
 * given (see renderFillBlank below for the exact shape), and fall back to
 * a free-text <input> for any blank without options.
 */
(function () {
  "use strict";

  /* ------------------------------------------------------------- *
   * Utilities
   * ------------------------------------------------------------- */
  function norm(s) {
    return String(s || "")
      .trim()
      .toLowerCase()
      .replace(/\s+/g, " ")
      .replace(/[.!?]+$/g, "");
  }

  function matchesAny(value, accepted) {
    var list = Array.isArray(accepted) ? accepted : [accepted];
    var v = norm(value);
    return list.some(function (a) {
      return norm(a) === v;
    });
  }

  function shuffled(arr) {
    var a = arr.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var tmp = a[i]; a[i] = a[j]; a[j] = tmp;
    }
    return a;
  }

  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    attrs = attrs || {};
    Object.keys(attrs).forEach(function (k) {
      if (k === "class") node.className = attrs[k];
      else if (k === "html") node.innerHTML = attrs[k];
      else if (k === "text") node.textContent = attrs[k];
      else node.setAttribute(k, attrs[k]);
    });
    (children || []).forEach(function (c) {
      if (c) node.appendChild(c);
    });
    return node;
  }

  function iconSpan(kind) {
    var d = kind === "check" ? '<path d="m5 12 5 5L20 7"/>' : '<path d="M18 6 6 18M6 6l12 12"/>';
    var wrap = el("span");
    wrap.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + d + "</svg>";
    return wrap.firstChild;
  }

  /* ------------------------------------------------------------- *
   * Shared save/print system — used by every "Save my answers" /
   * "Print / save my answers" button on the site (both graded
   * exercise blocks and free-text writing blocks), so a fix here
   * applies everywhere at once rather than per exercise type.
   *
   * Responsibilities:
   *   1. Preserve the learner's scroll position across the print
   *      dialog (hiding the rest of the page for printing changes
   *      document height, which otherwise resets scroll to 0).
   *   2. Give the generated PDF a meaningful, deterministic filename
   *      built from the page's level/section context plus the
   *      exercise's own type/title — never a generic "answers.pdf".
   * ------------------------------------------------------------- */
  var SECTION_LABELS = {
    exercises: "Exercises",
    vocabulary: "Vocabulary",
    reading: "Reading",
    listening: "Listening",
    writing: "Writing",
    speaking: "Speaking",
    revision: "Revision",
    "mock-tests": "Mock Tests",
  };
  var TYPE_LABELS = {
    "fill-blank": "fill in the blanks",
    "multiple-choice": "multiple choice",
    vocabulary: "vocabulary",
    "true-false": "true or false",
    matching: "matching",
    ordering: "ordering",
    correction: "correction",
    typing: "typing",
    "reading-comprehension": "reading comprehension",
  };

  function sanitizeFilename(name) {
    return name
      .replace(/[\\/:*?"<>|]/g, "")
      .replace(/\s+/g, " ")
      .trim();
  }

  function buildSaveFilename(container, data) {
    var levelCode = (document.body.getAttribute("data-level-code") || "").trim();
    var parts = [];
    if (levelCode) parts.push(levelCode);

    var sectionEl = container.closest("section[id]");
    if (sectionEl) {
      var id = sectionEl.id;
      if (SECTION_LABELS[id]) {
        parts.push(SECTION_LABELS[id]);
      } else {
        // On Test Yourself pages each grammar topic is its own
        // <section id="topic-slug">, so identify it by its own
        // heading text under the overarching "Test Yourself" label.
        var heading = sectionEl.querySelector("h2, h3");
        var topicTitle = heading ? heading.textContent.trim() : "";
        parts.push("Test Yourself");
        if (topicTitle) parts.push(topicTitle);
      }
    }

    var last = "";
    if (data.type && data.type !== "writing" && TYPE_LABELS[data.type]) {
      last += TYPE_LABELS[data.type] + " ";
    }
    last += data.title || "Exercise";
    parts.push(last.trim());

    return sanitizeFilename(parts.join(" - "));
  }

  function performSaveAnswers(container, data, buildOverlayContent) {
    var scrollX = window.scrollX;
    var scrollY = window.scrollY;
    var originalTitle = document.title;
    var restored = false;

    var overlay = document.getElementById("print-overlay");
    if (!overlay) {
      overlay = el("div", { id: "print-overlay" });
      document.body.appendChild(overlay);
    }
    overlay.innerHTML = "";
    overlay.appendChild(buildOverlayContent());

    document.title = buildSaveFilename(container, data) || originalTitle;
    document.body.classList.add("is-printing-block");

    function restore() {
      if (restored) return;
      restored = true;
      document.body.classList.remove("is-printing-block");
      overlay.innerHTML = "";
      document.title = originalTitle;
      // Something on the page (focus handling, the toc scrollspy, or
      // the browser's own scroll-position clamping while most of the
      // page was hidden for printing) can re-adjust the scroll
      // position slightly after we restore it once. Re-assert the
      // saved position a few times over a short window so the final,
      // settled state is reliably correct rather than a race.
      var root = document.documentElement;
      var prevBehavior = root.style.scrollBehavior;
      function jump() {
        root.style.scrollBehavior = "auto";
        window.scrollTo(scrollX, scrollY);
      }
      [0, 30, 80, 150, 300, 500].forEach(function (delay) {
        setTimeout(jump, delay);
      });
      setTimeout(function () {
        root.style.scrollBehavior = prevBehavior;
      }, 520);
      window.removeEventListener("afterprint", restore);
    }

    window.addEventListener("afterprint", restore);
    window.print();
    // Fallback in case `afterprint` doesn't fire (seen in some
    // browsers' print-to-PDF flows) — doesn't fire early because
    // `restored` guards against a double-restore.
    setTimeout(restore, 1000);
  }

  /* ------------------------------------------------------------- *
   * Item renderers — one per exercise type.
   * Each renderer returns { node, reset(), grade() }. grade() locks
   * the item, reveals correct/incorrect state + explanation, and
   * returns { correct, attempted }.
   * ------------------------------------------------------------- */
  var renderers = {};

  function itemShell(index, promptHtml) {
    var wrap = el("div", { class: "exercise-item", "data-item-index": index });
    var num = el("span", { class: "exercise-item__number", "aria-hidden": "true", text: String(index + 1) });
    if (promptHtml !== null) {
      var p = el("p", { class: "exercise-item__prompt" });
      p.appendChild(num);
      var span = el("span");
      span.innerHTML = promptHtml;
      p.appendChild(span);
      wrap.appendChild(p);
    }
    return wrap;
  }

  function feedbackNode(explanation) {
    var fb = el("div", { class: "item-feedback", role: "status" });
    var body = el("div", { class: "item-feedback__body" });
    var strong = el("strong");
    body.appendChild(strong);
    if (explanation) body.appendChild(el("span", { text: explanation }));
    fb.appendChild(body);
    return { node: fb, strongEl: strong, body: body };
  }

  function setFeedback(fbRef, correct, correctAnswerText, iconWrap) {
    fbRef.node.classList.add("is-visible");
    fbRef.node.classList.toggle("is-correct", correct);
    fbRef.node.classList.toggle("is-incorrect", !correct);
    iconWrap.innerHTML = "";
    iconWrap.appendChild(iconSpan(correct ? "check" : "cross"));
    fbRef.strongEl.textContent = correct ? "Correct." : "Not quite.";
    if (!correct && correctAnswerText) {
      var existing = fbRef.body.querySelector(".correct-answer");
      if (!existing) {
        fbRef.body.appendChild(el("div", { class: "correct-answer", html: "<em>Correct answer:</em> " + correctAnswerText }));
      }
    }
  }

  // ---- multiple-choice / vocabulary / reading-comprehension question ----
  function renderChoice(item, index) {
    var wrap = itemShell(index, item.prompt);
    var fieldset = el("fieldset");
    fieldset.appendChild(el("legend", { class: "visually-hidden", text: "Choose one answer" }));
    var list = el("div", { class: "option-list" });
    var name = "q_" + item.id;
    var optionEls = [];

    (item.options || []).forEach(function (opt, i) {
      var inputId = name + "_" + i;
      var input = el("input", { type: "radio", name: name, id: inputId, value: String(i) });
      var label = el("label", { class: "option", for: inputId }, [
        input,
        el("span", { class: "option__label", text: opt }),
      ]);
      optionEls.push({ input: input, label: label });
      list.appendChild(label);
    });

    fieldset.appendChild(list);
    wrap.appendChild(fieldset);

    var iconWrap = el("span");
    var fb = feedbackNode(item.explanation || "");
    fb.node.insertBefore(iconWrap, fb.node.firstChild);
    wrap.appendChild(fb.node);

    return {
      node: wrap,
      reset: function () {
        optionEls.forEach(function (o) {
          o.input.checked = false;
          o.input.disabled = false;
          o.label.classList.remove("is-correct", "is-incorrect");
          var tag = o.label.querySelector(".option__tag");
          if (tag) tag.remove();
        });
        fb.node.classList.remove("is-visible", "is-correct", "is-incorrect");
        var ca = fb.body.querySelector(".correct-answer");
        if (ca) ca.remove();
        wrap.classList.remove("is-locked");
      },
      grade: function () {
        var chosen = optionEls.findIndex(function (o) { return o.input.checked; });
        var correct = chosen === item.answerIndex;
        optionEls.forEach(function (o, i) {
          o.input.disabled = true;
          if (i === item.answerIndex) {
            o.label.classList.add("is-correct");
            o.label.appendChild(el("span", { class: "option__tag", "aria-hidden": "true", text: "\u2713 correct" }));
          } else if (i === chosen) {
            o.label.classList.add("is-incorrect");
            o.label.appendChild(el("span", { class: "option__tag", "aria-hidden": "true", text: "\u2717 your answer" }));
          }
        });
        wrap.classList.add("is-locked");
        setFeedback(fb, correct, null, iconWrap);
        return { correct: correct, attempted: chosen !== -1 };
      },
    };
  }
  renderers["multiple-choice"] = renderChoice;
  renderers["vocabulary"] = renderChoice;
  renderers["reading-comprehension"] = renderChoice;

  // ---- true-false ----
  function renderTrueFalse(item, index) {
    var wrap = itemShell(index, item.statement);
    var fieldset = el("fieldset");
    fieldset.appendChild(el("legend", { class: "visually-hidden", text: "True or false" }));
    var list = el("div", { class: "option-list tf-options" });
    var name = "q_" + item.id;
    var trueId = name + "_t", falseId = name + "_f";
    var trueInput = el("input", { type: "radio", name: name, id: trueId, value: "true" });
    var falseInput = el("input", { type: "radio", name: name, id: falseId, value: "false" });
    var trueLabel = el("label", { class: "option", for: trueId }, [trueInput, el("span", { class: "option__label", text: "True" })]);
    var falseLabel = el("label", { class: "option", for: falseId }, [falseInput, el("span", { class: "option__label", text: "False" })]);
    list.appendChild(trueLabel);
    list.appendChild(falseLabel);
    fieldset.appendChild(list);
    wrap.appendChild(fieldset);

    var iconWrap = el("span");
    var fb = feedbackNode(item.explanation || "");
    fb.node.insertBefore(iconWrap, fb.node.firstChild);
    wrap.appendChild(fb.node);

    return {
      node: wrap,
      reset: function () {
        trueInput.checked = false; falseInput.checked = false;
        trueInput.disabled = false; falseInput.disabled = false;
        trueLabel.classList.remove("is-correct", "is-incorrect");
        falseLabel.classList.remove("is-correct", "is-incorrect");
        var t1 = trueLabel.querySelector(".option__tag"); if (t1) t1.remove();
        var t2 = falseLabel.querySelector(".option__tag"); if (t2) t2.remove();
        fb.node.classList.remove("is-visible", "is-correct", "is-incorrect");
        wrap.classList.remove("is-locked");
      },
      grade: function () {
        var chosen = trueInput.checked ? true : falseInput.checked ? false : null;
        var correct = chosen === item.answer;
        trueInput.disabled = true; falseInput.disabled = true;
        var correctLabel = item.answer ? trueLabel : falseLabel;
        correctLabel.classList.add("is-correct");
        correctLabel.appendChild(el("span", { class: "option__tag", "aria-hidden": "true", text: "\u2713 correct" }));
        if (chosen !== null && chosen !== item.answer) {
          var wrongLabel = chosen ? trueLabel : falseLabel;
          wrongLabel.classList.add("is-incorrect");
          wrongLabel.appendChild(el("span", { class: "option__tag", "aria-hidden": "true", text: "\u2717 your answer" }));
        }
        wrap.classList.add("is-locked");
        setFeedback(fb, correct, null, iconWrap);
        return { correct: correct, attempted: chosen !== null };
      },
    };
  }
  renderers["true-false"] = renderTrueFalse;

  // ---- fill-blank ----
  // item.prompt uses "___" to mark each blank. item.answers is an array
  // (one entry per blank), each entry a string or array of accepted strings.
  //
  // Each blank renders as a <select> when the item supplies options for it,
  // and falls back to a free-text <input> otherwise (kept for any item that
  // hasn't been migrated to a dropdown yet). Options can be given two ways:
  //   - "options": ["friend", "friends", "friendly"]   (single blank)
  //   - "options": [["is","are"], ["have","has"]]       (one array per blank)
  // The correct answer's position is shuffled per render so it isn't always
  // first. Grading is unchanged — it still matches the control's value
  // against item.answers[i], which works identically for <input> and
  // <select> since both expose a plain .value.
  function renderFillBlank(item, index) {
    var wrap = itemShell(index, null);
    var sentence = el("p", { class: "blank-sentence exercise-item__prompt" });
    var num = el("span", { class: "exercise-item__number", "aria-hidden": "true", text: String(index + 1) });
    sentence.appendChild(num);

    var parts = String(item.prompt).split("___");
    var numBlanks = parts.length - 1;

    function optionsForBlank(i) {
      if (!item.options || !item.options.length) return null;
      // Per-blank arrays: "options": [["a","b"], ["c","d"]]
      if (Array.isArray(item.options[0])) return item.options[i] || null;
      // Flat array applies to a single-blank item: "options": ["a","b","c"]
      return numBlanks === 1 ? item.options : null;
    }

    var inputs = [];
    parts.forEach(function (part, i) {
      sentence.appendChild(document.createTextNode(part));
      if (i < numBlanks) {
        var blankOptions = optionsForBlank(i);
        var control;
        if (blankOptions && blankOptions.length) {
          control = el("select", {
            class: "blank-input",
            "aria-label": "Blank " + (i + 1) + " of " + numBlanks,
          });
          control.appendChild(el("option", { value: "", text: "Choose…" }));
          shuffled(blankOptions).forEach(function (opt) {
            control.appendChild(el("option", { value: opt, text: opt }));
          });
        } else {
          control = el("input", {
            type: "text",
            class: "blank-input",
            "aria-label": "Blank " + (i + 1) + " of " + numBlanks,
            autocomplete: "off",
            autocapitalize: "off",
            spellcheck: "false",
          });
        }
        inputs.push(control);
        sentence.appendChild(control);
      }
    });
    wrap.appendChild(sentence);

    var fb = feedbackNode(item.explanation || "");
    var iconWrap = el("span");
    fb.node.insertBefore(iconWrap, fb.node.firstChild);
    wrap.appendChild(fb.node);

    return {
      node: wrap,
      reset: function () {
        inputs.forEach(function (inp) {
          inp.value = "";
          inp.disabled = false;
          inp.classList.remove("is-correct", "is-incorrect");
        });
        fb.node.classList.remove("is-visible", "is-correct", "is-incorrect");
        var ca = fb.body.querySelector(".correct-answer");
        if (ca) ca.remove();
        wrap.classList.remove("is-locked");
      },
      grade: function () {
        var allCorrect = true;
        var attempted = false;
        var answers = item.answers || [];
        inputs.forEach(function (inp, i) {
          if (inp.value.trim()) attempted = true;
          var ok = matchesAny(inp.value, answers[i]);
          inp.classList.add(ok ? "is-correct" : "is-incorrect");
          inp.disabled = true;
          if (!ok) allCorrect = false;
        });
        wrap.classList.add("is-locked");
        var correctText = (item.answers || []).map(function (a) { return Array.isArray(a) ? a[0] : a; }).join(" &middot; ");
        setFeedback(fb, allCorrect, allCorrect ? null : correctText, iconWrap);
        return { correct: allCorrect, attempted: attempted };
      },
    };
  }
  renderers["fill-blank"] = renderFillBlank;

  // ---- correction (grammar correction) ----
  function renderCorrection(item, index) {
    var wrap = itemShell(index, null);
    wrap.appendChild(el("p", { class: "exercise-item__source", html: "&ldquo;" + item.incorrect + "&rdquo;" }));
    var label = el("label", { class: "exercise-item__prompt", for: "q_" + item.id });
    label.appendChild(el("span", { class: "exercise-item__number", "aria-hidden": "true", text: String(index + 1) }));
    label.appendChild(document.createTextNode("Write the correct sentence:"));
    wrap.appendChild(label);
    var input = el("input", { type: "text", id: "q_" + item.id, class: "answer-input", autocomplete: "off", spellcheck: "false" });
    wrap.appendChild(input);

    var fb = feedbackNode(item.explanation || "");
    var iconWrap = el("span");
    fb.node.insertBefore(iconWrap, fb.node.firstChild);
    wrap.appendChild(fb.node);

    return {
      node: wrap,
      reset: function () {
        input.value = ""; input.disabled = false;
        input.classList.remove("is-correct", "is-incorrect");
        fb.node.classList.remove("is-visible", "is-correct", "is-incorrect");
        var ca = fb.body.querySelector(".correct-answer");
        if (ca) ca.remove();
        wrap.classList.remove("is-locked");
      },
      grade: function () {
        var ok = matchesAny(input.value, item.answer);
        input.classList.add(ok ? "is-correct" : "is-incorrect");
        input.disabled = true;
        wrap.classList.add("is-locked");
        var correctText = Array.isArray(item.answer) ? item.answer[0] : item.answer;
        setFeedback(fb, ok, ok ? null : correctText, iconWrap);
        return { correct: ok, attempted: input.value.trim().length > 0 };
      },
    };
  }
  renderers["correction"] = renderCorrection;

  // ---- typing (short-answer; graded if item.answer given, else self-check) ----
  function renderTyping(item, index) {
    var wrap = itemShell(index, item.prompt);
    var input = el("input", { type: "text", class: "answer-input", autocomplete: "off", spellcheck: "false", "aria-label": item.prompt || "Your answer" });
    wrap.appendChild(input);

    var selfCheck = !item.answer;
    var fb = feedbackNode(selfCheck ? "" : item.explanation || "");
    var iconWrap = el("span");
    if (!selfCheck) fb.node.insertBefore(iconWrap, fb.node.firstChild);
    wrap.appendChild(fb.node);

    return {
      node: wrap,
      reset: function () {
        input.value = ""; input.disabled = false;
        input.classList.remove("is-correct", "is-incorrect");
        fb.node.classList.remove("is-visible", "is-correct", "is-incorrect");
        var ma = fb.body.querySelector(".model-answer");
        if (ma) ma.remove();
        var ca = fb.body.querySelector(".correct-answer");
        if (ca) ca.remove();
        wrap.classList.remove("is-locked");
      },
      grade: function () {
        input.disabled = true;
        wrap.classList.add("is-locked");
        if (selfCheck) {
          fb.node.classList.add("is-visible");
          fb.strongEl.textContent = item.modelAnswer ? "Model answer:" : "Saved for your own review.";
          if (item.modelAnswer && !fb.body.querySelector(".model-answer")) {
            fb.body.appendChild(el("div", { class: "model-answer", text: item.modelAnswer }));
          }
          return { correct: true, attempted: input.value.trim().length > 0, selfCheck: true };
        }
        var ok = matchesAny(input.value, item.answer);
        input.classList.add(ok ? "is-correct" : "is-incorrect");
        var correctText = Array.isArray(item.answer) ? item.answer[0] : item.answer;
        setFeedback(fb, ok, ok ? null : correctText, iconWrap);
        return { correct: ok, attempted: input.value.trim().length > 0 };
      },
    };
  }
  renderers["typing"] = renderTyping;

  // ---- matching (dropdown-based: accessible & mobile-friendly) ----
  function renderMatching(item, index) {
    var wrap = itemShell(index, null);
    var table = el("div", { class: "match-table" });
    var rightOptions = shuffled(item.pairs.map(function (p) { return p.right; }));
    var selects = [];

    item.pairs.forEach(function (pair, i) {
      var row = el("div", { class: "match-row" });
      row.appendChild(el("span", { class: "match-row__left" }, [
        el("span", { class: "exercise-item__number", "aria-hidden": "true", text: String(i + 1) }),
        el("span", { text: pair.left }),
      ]));
      row.appendChild(el("span", { class: "match-row__arrow", "aria-hidden": "true", text: "\u2192" }));
      var select = el("select", { class: "answer-input", "aria-label": "Match for " + pair.left });
      select.appendChild(el("option", { value: "", text: "Choose\u2026" }));
      rightOptions.forEach(function (opt) {
        select.appendChild(el("option", { value: opt, text: opt }));
      });
      selects.push(select);
      row.appendChild(select);
      table.appendChild(row);
    });
    wrap.appendChild(table);

    var fb = feedbackNode(item.explanation || "");
    var iconWrap = el("span");
    fb.node.insertBefore(iconWrap, fb.node.firstChild);
    wrap.appendChild(fb.node);

    return {
      node: wrap,
      reset: function () {
        selects.forEach(function (s) { s.value = ""; s.disabled = false; s.classList.remove("is-correct", "is-incorrect"); });
        fb.node.classList.remove("is-visible", "is-correct", "is-incorrect");
        wrap.classList.remove("is-locked");
      },
      grade: function () {
        var allCorrect = true, attempted = false;
        selects.forEach(function (s, i) {
          if (s.value) attempted = true;
          var ok = norm(s.value) === norm(item.pairs[i].right);
          s.classList.add(ok ? "is-correct" : "is-incorrect");
          s.disabled = true;
          if (!ok) allCorrect = false;
        });
        wrap.classList.add("is-locked");
        setFeedback(fb, allCorrect, null, iconWrap);
        return { correct: allCorrect, attempted: attempted };
      },
    };
  }
  renderers["matching"] = renderMatching;

  // ---- ordering (sentence ordering via word chips) ----
  function renderOrdering(item, index) {
    var wrap = itemShell(index, item.prompt || "Put the words in the correct order.");
    var buildArea = el("div", { class: "order-build", role: "list", "aria-label": "Your sentence" });
    var pool = el("div", { class: "order-pool", role: "list", "aria-label": "Available words" });
    var words = item.words;
    var chips = shuffled(words.map(function (w, i) { return { word: w, key: i, placed: false }; }));
    var built = [];

    function renderPool() {
      pool.innerHTML = "";
      chips.forEach(function (c) {
        var chip = el("button", { type: "button", class: "word-chip" + (c.placed ? " is-placed" : ""), text: c.word });
        chip.disabled = !!c.placed;
        chip.addEventListener("click", function () {
          c.placed = true;
          built.push(c);
          renderPool();
          renderBuild();
        });
        pool.appendChild(chip);
      });
    }
    function renderBuild() {
      buildArea.innerHTML = "";
      built.forEach(function (c) {
        var chip = el("button", { type: "button", class: "word-chip", text: c.word, "aria-label": "Remove " + c.word });
        chip.addEventListener("click", function () {
          c.placed = false;
          built = built.filter(function (b) { return b !== c; });
          renderPool();
          renderBuild();
        });
        buildArea.appendChild(chip);
      });
    }
    renderPool();
    renderBuild();

    var resetBtn = el("button", { type: "button", class: "btn btn--ghost btn--small order-reset", text: "Clear" });
    resetBtn.addEventListener("click", function () {
      built.forEach(function (c) { c.placed = false; });
      built = [];
      renderPool();
      renderBuild();
    });

    wrap.appendChild(buildArea);
    wrap.appendChild(pool);
    wrap.appendChild(resetBtn);

    var fb = feedbackNode(item.explanation || "");
    var iconWrap = el("span");
    fb.node.insertBefore(iconWrap, fb.node.firstChild);
    wrap.appendChild(fb.node);

    return {
      node: wrap,
      reset: function () {
        chips.forEach(function (c) { c.placed = false; });
        built = [];
        renderPool();
        renderBuild();
        fb.node.classList.remove("is-visible", "is-correct", "is-incorrect");
        var ca = fb.body.querySelector(".correct-answer");
        if (ca) ca.remove();
        wrap.classList.remove("is-locked");
        resetBtn.disabled = false;
      },
      grade: function () {
        var userOrder = built.map(function (c) { return c.word; });
        var correct = userOrder.length === words.length && userOrder.every(function (w, i) { return w === words[i]; });
        buildArea.querySelectorAll(".word-chip").forEach(function (b) { b.disabled = true; });
        pool.querySelectorAll(".word-chip").forEach(function (b) { b.disabled = true; });
        resetBtn.disabled = true;
        wrap.classList.add("is-locked");
        var correctText = words.join(" ");
        setFeedback(fb, correct, correct ? null : correctText, iconWrap);
        return { correct: correct, attempted: userOrder.length > 0 };
      },
    };
  }
  renderers["ordering"] = renderOrdering;

  /* ------------------------------------------------------------- *
   * Block controller — wires items + submit/retry/score for one
   * .exercise-block
   * ------------------------------------------------------------- */
  function scorePanelNode() {
    var panel = el("div", { class: "score-panel", role: "status", "aria-live": "polite" });
    var ring = el("div", { class: "score-panel__ring", text: "" });
    var textWrap = el("div", { class: "score-panel__text" });
    panel.appendChild(ring);
    panel.appendChild(textWrap);
    return { node: panel, ring: ring, textWrap: textWrap };
  }

  function buildBlock(container, data) {
    var head = el("div", { class: "exercise-block__head" });
    head.appendChild(el("span", { class: "exercise-block__type", text: data.type.replace(/-/g, " ") }));
    head.appendChild(el("h3", { class: "exercise-block__title", text: data.title || "Exercise" }));
    if (data.instructions) head.appendChild(el("p", { class: "exercise-block__instructions", text: data.instructions }));
    container.appendChild(head);

    if (data.passage) {
      container.appendChild(el("div", { class: "reading-passage", html: data.passage }));
    }

    var scoreTop = scorePanelNode();
    container.appendChild(scoreTop.node);

    var itemsWrap = el("div", { class: "exercise-block__items" });
    container.appendChild(itemsWrap);

    var renderFn = renderers[data.type];
    if (!renderFn) {
      itemsWrap.appendChild(el("p", { text: "Unsupported exercise type: " + data.type }));
      return;
    }

    var built = (data.items || []).map(function (item, i) {
      var r = renderFn(item, i);
      itemsWrap.appendChild(r.node);
      return r;
    });

    var scoreBottom = scorePanelNode();
    container.appendChild(scoreBottom.node);
    var scorePanels = [scoreTop, scoreBottom];

    var actions = el("div", { class: "exercise-actions" });
    var submitBtn = el("button", { type: "button", class: "btn btn--accent", text: "Submit" });
    var retryBtn = el("button", { type: "button", class: "btn btn--ghost", text: "Retry incorrect only" });
    var retryAllBtn = el("button", { type: "button", class: "btn btn--ghost", text: "Retry all" });
    var printBtn = el("button", { type: "button", class: "btn btn--ghost print-hidden", text: "Save my answers" });
    retryBtn.style.display = "none";
    retryAllBtn.style.display = "none";
    printBtn.style.display = "none";
    actions.appendChild(submitBtn);
    actions.appendChild(retryBtn);
    actions.appendChild(retryAllBtn);
    actions.appendChild(printBtn);
    container.appendChild(actions);

    var lastResults = null;

    function showScore(results) {
      var correctCount = results.filter(function (r) { return r.correct; }).length;
      var total = results.length;
      var pct = total ? Math.round((correctCount / total) * 100) : 0;
      var ringClass = pct < 50 ? "is-low" : pct < 80 ? "is-mid" : "";
      var headingText = pct === 100 ? "Excellent — perfect score!" : pct >= 80 ? "Well done." : pct >= 50 ? "Good progress." : "Keep practicing.";
      var subText = correctCount + " of " + total + " correct (" + pct + "%).";
      scorePanels.forEach(function (sp) {
        sp.ring.textContent = correctCount + "/" + total;
        sp.ring.classList.remove("is-low", "is-mid");
        if (ringClass) sp.ring.classList.add(ringClass);
        sp.textWrap.innerHTML = "";
        sp.textWrap.appendChild(el("h4", { text: headingText }));
        sp.textWrap.appendChild(el("p", { text: subText }));
        sp.node.classList.add("is-visible");
      });
    }

    submitBtn.addEventListener("click", function () {
      lastResults = built.map(function (r) { return r.grade(); });
      showScore(lastResults);
      submitBtn.style.display = "none";
      var anyIncorrect = lastResults.some(function (r) { return !r.correct; });
      retryBtn.style.display = anyIncorrect ? "" : "none";
      retryAllBtn.style.display = "";
      printBtn.style.display = "";
      container.dispatchEvent(new CustomEvent("exercise:submitted", {
        bubbles: true,
        detail: { id: data.id, results: lastResults },
      }));

      // Gamification (assets/js/progress.js) — optional by design: if
      // that script hasn't loaded on a given page, grading above still
      // works exactly the same, nothing here is required for it.
      if (window.ProgressTracker && typeof window.ProgressTracker.recordExerciseResult === "function") {
        var correctCount = lastResults.filter(function (r) { return r.correct; }).length;
        var total = lastResults.length;
        window.ProgressTracker.recordExerciseResult({
          exerciseId: data.id,
          level: document.body.getAttribute("data-level-code") || "",
          correct: correctCount,
          total: total,
          perfect: total > 0 && correctCount === total,
        });
      }
    });

    printBtn.addEventListener("click", function () {
      performSaveAnswers(container, data, function () {
        return container.cloneNode(true);
      });
    });

    retryBtn.addEventListener("click", function () {
      built.forEach(function (r, i) {
        if (!lastResults[i].correct) r.reset();
      });
      scorePanels.forEach(function (sp) { sp.node.classList.remove("is-visible"); });
      submitBtn.style.display = "";
      retryBtn.style.display = "none";
      retryAllBtn.style.display = "none";
      printBtn.style.display = "none";
      var firstOpen = itemsWrap.querySelector(".exercise-item:not(.is-locked)");
      if (firstOpen) firstOpen.scrollIntoView({ behavior: "smooth", block: "center" });
    });

    retryAllBtn.addEventListener("click", function () {
      built.forEach(function (r) { r.reset(); });
      scorePanels.forEach(function (sp) { sp.node.classList.remove("is-visible"); });
      submitBtn.style.display = "";
      retryBtn.style.display = "none";
      retryAllBtn.style.display = "none";
      printBtn.style.display = "none";
    });
  }

  /* ---------------------------------------------------------------
     Writing prompts — free-text, ungraded. No submit/check button;
     the only action is saving/printing the prompt(s) together with
     whatever the student has written, exactly as-is.
     --------------------------------------------------------------- */
  function buildWritingBlock(container, data) {
    var head = el("div", { class: "exercise-block__head" });
    head.appendChild(el("span", { class: "exercise-block__type", text: "writing" }));
    head.appendChild(el("h3", { class: "exercise-block__title", text: data.title || "Writing" }));
    if (data.instructions) head.appendChild(el("p", { class: "exercise-block__instructions", text: data.instructions }));
    container.appendChild(head);

    var itemsWrap = el("div", { class: "exercise-block__items" });
    container.appendChild(itemsWrap);

    var textareas = [];
    (data.items || []).forEach(function (item, i) {
      var wrap = el("div", { class: "exercise-item writing-item" });
      wrap.appendChild(el("span", { class: "exercise-item__number", "aria-hidden": "true", text: String(i + 1) }));
      var promptEl = el("p", { class: "exercise-item__prompt writing-item__prompt", text: item.prompt || "" });
      wrap.appendChild(promptEl);
      var textarea = el("textarea", {
        class: "writing-item__textarea",
        rows: "6",
        placeholder: "Write your answer here\u2026",
        "aria-label": item.prompt || "Your answer",
      });
      textarea.dataset.prompt = item.prompt || "";
      textareas.push(textarea);
      wrap.appendChild(textarea);
      itemsWrap.appendChild(wrap);
    });

    var actions = el("div", { class: "exercise-actions" });
    var saveBtn = el("button", { type: "button", class: "btn btn--ghost print-hidden", text: "Save my answers" });
    actions.appendChild(saveBtn);
    container.appendChild(actions);

    saveBtn.addEventListener("click", function () {
      performSaveAnswers(container, data, function () {
        var printWrap = el("div", { class: "exercise-block" });
        printWrap.appendChild(el("h3", { class: "exercise-block__title", text: data.title || "Writing" }));
        textareas.forEach(function (ta, i) {
          var block = el("div", { class: "writing-item" });
          block.appendChild(el("p", { class: "writing-item__prompt", text: "" + (i + 1) + ". " + (ta.dataset.prompt || "") }));
          var answerP = el("p", { class: "writing-item__saved-answer" });
          answerP.textContent = ta.value.trim() || "(No answer written yet.)";
          block.appendChild(answerP);
          printWrap.appendChild(block);
        });
        return printWrap;
      });
    });
  }

  function init() {
    document.querySelectorAll(".exercise-block").forEach(function (container) {
      var dataScript = container.querySelector("script.exercise-data");
      if (!dataScript) return;
      try {
        var data = JSON.parse(dataScript.textContent);
        if (data.type === "writing") {
          buildWritingBlock(container, data);
        } else {
          buildBlock(container, data);
        }
      } catch (e) {
        container.innerHTML = "<p>This exercise could not be loaded.</p>";
        if (window.console) console.error("Exercise parse error", e);
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
