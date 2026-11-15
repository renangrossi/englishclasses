/*!
 * Renan the Teacher — Today's Review (today-review.html)
 * ------------------------------------------------------------------
 * The student's study coach: one page that says what to do next, in
 * what order, and what went wrong before. Everything shown comes from
 * the student's own records -- nothing is estimated or made up:
 *
 *   - assets/js/mastery.js  (window.MasteryTracker): one record per
 *     answered item -- attempts, misses, due date, mastery status and
 *     the latest wrong answer.
 *   - assets/js/progress.js (window.ProgressTracker): which exercise
 *     blocks were submitted and their best score, streak, tests done.
 *   - assets/data/exercise-items-index.json: what each item says (its
 *     prompt, answer, explanation and lesson) -- see
 *     scripts/build_exercise_index.py.
 *   - assets/data/lesson-order.json: each level's lessons in course
 *     order with their exercise block ids -- see
 *     scripts/build_lesson_order.py.
 *
 * Study order (the plan at the top of the page):
 *   1. overdue reviews   2. reviews due today
 *   3. exercises scored below IMPROVE_BELOW   4. the next new lesson
 * The first unfinished step is "Your next step".
 *
 * The review session is built from due items not yet practiced today,
 * most overdue first, capped at MAX_ITEMS_PER_SESSION, and graded by
 * the same engine as every lesson page (window.ExerciseEngine) --
 * nothing here re-implements grading. After each submission the plan,
 * stats and mistakes redraw from the updated records.
 * ------------------------------------------------------------------ */
(function () {
  "use strict";

  var MAX_ITEMS_PER_SESSION = 20;
  var IMPROVE_BELOW = 0.8;      // best score under 80% = "needs improvement"
  var MISTAKES_FIRST = 6;       // mistakes shown at first...
  var MISTAKES_MORE = 12;       // ...and how many each "Show more" adds
  var TYPE_LABELS = {
    "fill-blank": "Fill in the Blanks",
    "multiple-choice": "Multiple Choice",
    "correction": "Error Correction",
    "typing": "Rewrite / Short Answer",
    "matching": "Matching",
    "ordering": "Word Order",
    "true-false": "True or False",
    "vocabulary": "Vocabulary",
  };
  var INDEX_ONLY_FIELDS = ["exerciseType", "exerciseId", "exerciseTitle", "exerciseInstructions",
    "lessonId", "lessonTitle", "level", "lessonUrl"];

  var index = null;          // item key -> item
  var order = null;          // lesson-order.json
  var exerciseInfo = {};     // exercise block id -> { lesson, level, title }
  var session = null;        // { keys: [...], blockIds: [...] } built once per page load
  var sessionRound = 0;

  /* ---------------- helpers ---------------- */

  function todayStr(offsetDays) {
    var d = new Date();
    if (offsetDays) d.setDate(d.getDate() + offsetDays);
    return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
  }

  function daysBetween(a, b) {
    return Math.round((new Date(b + "T00:00:00") - new Date(a + "T00:00:00")) / 86400000);
  }

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function plural(n, word, many) {
    return n + " " + (n === 1 ? word : (many || word + "s"));
  }

  function first(a) { return Array.isArray(a) ? a[0] : a; }

  // The question as the student saw it, in one line.
  function promptText(item) {
    switch (item.exerciseType) {
      case "correction": return item.incorrect || item.prompt || "";
      case "matching": return item.prompt || "Match the pairs";
      case "true-false": return item.statement || "";
      default: return item.prompt || item.statement || "";
    }
  }

  // The right answer, in one line.
  function answerText(item) {
    switch (item.exerciseType) {
      case "multiple-choice":
      case "vocabulary":
        return (item.options || [])[item.answerIndex];
      case "true-false": return item.answer ? "True" : "False";
      case "fill-blank": return (item.answers || []).map(first).join(" · ");
      case "ordering": return (item.words || []).join(" ");
      case "matching": return (item.pairs || []).map(function (p) { return p.left + " → " + p.right; }).join("; ");
      default: return first(item.answer);
    }
  }

  // "Exercise VI: Fill in the Blanks (Part 1 of 3)" -- the number the
  // lesson page shows above the exercise (assets/js/exercises.js).
  function exerciseName(info) {
    return "Exercise " + toRoman(info.num) + ": " + info.title;
  }
  function toRoman(n) {
    return window.RomanNumeral ? window.RomanNumeral(n) : String(n);
  }

  function weakHref(w) {
    return w.info.url + "#ex-" + encodeURIComponent(w.id);
  }

  function lessonLink(item) {
    return item.lessonUrl + "#ex-" + encodeURIComponent(item.exerciseId);
  }

  /* ---------------- reading the records ---------------- */

  function readRecords() {
    var mastery = window.MasteryTracker ? window.MasteryTracker.getState().items || {} : {};
    var progress = window.ProgressTracker ? window.ProgressTracker.getState() : null;
    return { items: mastery, progress: progress };
  }

  function analyse() {
    var rec = readRecords();
    var today = todayStr();
    var a = {
      today: today,
      overdue: [], dueToday: [], reviewedToday: [], missedToday: [],
      tracked: 0, mastered: 0, attempts: 0, correct: 0,
      mistakes: [],
      progress: rec.progress,
    };
    Object.keys(rec.items).forEach(function (key) {
      var m = rec.items[key];
      if (!index[key]) return; // an item that was edited or removed since
      a.tracked++;
      a.attempts += m.attempts || 0;
      a.correct += m.correctCount || 0;
      if (m.masteryStatus === "mastered") a.mastered++;
      if (m.lastAttemptAt === today) {
        a.reviewedToday.push(key);
        if (m.lastCorrect === false) a.missedToday.push(key);
      }
      if (m.masteryStatus !== "mastered" && m.dueAt <= today && m.lastAttemptAt !== today) {
        (m.dueAt < today ? a.overdue : a.dueToday).push(key);
      }
      if ((m.incorrectCount || 0) > 0 && m.masteryStatus !== "mastered") {
        a.mistakes.push({ key: key, m: m, item: index[key] });
      }
    });
    function byDue(x, y) {
      var dx = rec.items[x].dueAt, dy = rec.items[y].dueAt;
      return dx < dy ? -1 : dx > dy ? 1 : 0;
    }
    a.overdue.sort(byDue);
    a.oldestDue = a.overdue.length ? rec.items[a.overdue[0]].dueAt : null;
    // Recurring first (missed more than once), then the most recent miss.
    a.mistakes.sort(function (x, y) {
      var rx = x.m.incorrectCount >= 2 ? 1 : 0, ry = y.m.incorrectCount >= 2 ? 1 : 0;
      if (rx !== ry) return ry - rx;
      if (x.m.incorrectCount !== y.m.incorrectCount) return y.m.incorrectCount - x.m.incorrectCount;
      var lx = x.m.lastWrongAt || x.m.lastAttemptAt || "", ly = y.m.lastWrongAt || y.m.lastAttemptAt || "";
      return lx < ly ? 1 : lx > ly ? -1 : 0;
    });

    // Exercise blocks whose best score is below the bar, worst first.
    var ex = (rec.progress && rec.progress.exercises) || {};
    a.weak = Object.keys(ex).filter(function (id) {
      var r = ex[id];
      return exerciseInfo[id] && r.total > 0 && r.bestCorrect / r.total < IMPROVE_BELOW;
    }).map(function (id) {
      return { id: id, best: ex[id].bestCorrect, total: ex[id].total, info: exerciseInfo[id] };
    }).sort(function (x, y) { return x.best / x.total - y.best / y.total; });

    // Weak areas: lessons with the most items missed and not yet mastered.
    var byLesson = {};
    a.mistakes.forEach(function (x) {
      var k = x.item.lessonUrl;
      if (!byLesson[k]) byLesson[k] = { url: k, title: x.item.lessonTitle, level: x.item.level, items: 0, recurring: 0, exerciseId: x.item.exerciseId };
      byLesson[k].items++;
      if (x.m.incorrectCount >= 2) byLesson[k].recurring++;
    });
    a.weakLessons = Object.keys(byLesson).map(function (k) { return byLesson[k]; })
      .sort(function (x, y) { return (y.recurring - x.recurring) || (y.items - x.items); });

    a.exercisesDone = Object.keys(ex).filter(function (id) { return !!exerciseInfo[id]; }).length;
    a.next = nextLesson(ex, rec.progress);
    a.after = lessonsAfter(a.next, ex, 2);
    a.lessonsTotal = 0; a.lessonsStarted = 0;
    order.levels.forEach(function (l) {
      l.lessons.forEach(function (lesson) {
        a.lessonsTotal++;
        if (lesson.exercises.some(function (id) { return !!ex[id]; })) a.lessonsStarted++;
      });
    });
    return a;
  }

  // The `n` lessons not started yet that follow `next` in course order.
  function lessonsAfter(next, ex, n) {
    var out = [], seen = false;
    if (next.kind !== "lesson") return out;
    order.levels.forEach(function (l) {
      l.lessons.forEach(function (lesson) {
        if (out.length >= n) return;
        if (lesson.url === next.url) { seen = true; return; }
        if (seen && !lesson.exercises.some(function (id) { return !!ex[id]; })) out.push({ url: lesson.url, title: lesson.title, level: l.code });
      });
    });
    return out;
  }

  // The next new step in course order: the first lesson with no
  // submitted exercise, in the highest level the student has worked in;
  // that level's Test Yourself once every lesson in it is started.
  function nextLesson(ex, progress) {
    var started = function (lesson) { return lesson.exercises.some(function (id) { return !!ex[id]; }); };
    var pages = (progress && progress.pagesCompleted) || {};
    var current = -1;
    order.levels.forEach(function (l, i) { if (l.lessons.some(started)) current = i; });
    if (current === -1) {
      var firstLevel = order.levels[0], firstLesson = firstLevel.lessons[0];
      if (!pages.placement) {
        return { kind: "placement", title: "Placement Test", url: "placement-test.html",
          why: "You haven't done any exercises yet. The placement test shows which level to start at." };
      }
      return { kind: "lesson", title: firstLesson.title, level: firstLevel.code, url: firstLesson.url,
        why: "The first lesson of the course. Start at the level your placement test suggested if it's higher." };
    }
    for (var i = current; i < order.levels.length; i++) {
      var level = order.levels[i];
      var todo = level.lessons.filter(function (l) { return !started(l); })[0];
      if (todo) {
        return { kind: "lesson", title: todo.title, level: level.code, url: todo.url,
          why: i === current ? "The next lesson in " + level.code + " you haven't started." : "You've started every lesson in " + order.levels[current].code + ". This is the first lesson of " + level.code + "." };
      }
      if (level.test && !pages["test-yourself:" + level.code]) {
        return { kind: "test", title: level.code + " Test Yourself", level: level.code, url: level.test,
          why: "You've started every " + level.code + " lesson. The test checks the whole level." };
      }
    }
    return { kind: "exam", title: "Simulated Exams", url: "simulated-exams.html",
      why: "You've started every lesson in the course. Practice for an exam." };
  }

  /* ---------------- next step + plan ---------------- */

  function sessionLeft() {
    if (!session) return 0;
    return session.blockIds.filter(function (id) {
      var b = document.getElementById(id);
      return b && !b.hasAttribute("data-submitted");
    }).length;
  }

  function steps(a) {
    var remaining = a.overdue.length + a.dueToday.length;
    return [
      { id: "overdue", label: "Overdue reviews",
        detail: a.overdue.length ? plural(a.overdue.length, "item") + ", oldest " + plural(daysBetween(a.oldestDue, a.today), "day") + " late" : "None",
        done: a.overdue.length === 0, href: "#review-queue" },
      { id: "due", label: "Reviews due today",
        detail: a.dueToday.length ? plural(a.dueToday.length, "item") : (a.reviewedToday.length ? plural(a.reviewedToday.length, "item") + " reviewed today" : "None"),
        done: a.dueToday.length === 0, href: "#review-queue" },
      { id: "improve", label: "Exercises to improve",
        detail: a.weak.length ? plural(a.weak.length, "exercise") + " under " + Math.round(IMPROVE_BELOW * 100) + "%" : "None",
        done: a.weak.length === 0, href: "#coach-improve" },
      // Informational only: mistakes stay open until mastered, days later,
      // so this step is never the "next" one and never blocks step 5.
      { id: "mistakes", label: "Your mistakes", info: true,
        detail: a.mistakes.length ? plural(a.mistakes.length, "open mistake") : "None open",
        done: a.mistakes.length === 0, href: "#coach-mistakes" },
      { id: "new", label: a.next.kind === "lesson" ? "New lesson" : "Next step",
        detail: a.next.title + (a.next.level ? " (" + a.next.level + ")" : ""),
        done: false, href: "#coach-recs", remaining: remaining },
    ];
  }

  function renderNext(a) {
    var box = document.getElementById("coach-next");
    var plan = document.getElementById("coach-plan");
    var list = steps(a);
    var current = list.filter(function (s) { return !s.done && !s.info; })[0];

    plan.innerHTML = list.map(function (s, i) {
      var state = s.done ? "is-done" : s === current ? "is-current" : "";
      return '<li class="coach-plan__step ' + state + '">' +
        '<a href="' + esc(s.href) + '">' +
        '<span class="coach-plan__num" aria-hidden="true">' + (s.done ? "✓" : i + 1) + "</span>" +
        '<span class="coach-plan__text"><strong>' + esc(s.label) + "</strong><span>" + esc(s.detail) + "</span></span>" +
        (s.done ? '<span class="visually-hidden"> (done)</span>' : s === current ? '<span class="visually-hidden"> (next)</span>' : "") +
        "</a></li>";
    }).join("");

    var title, why, action, href, isReview = false;
    if (current.id === "overdue" || current.id === "due") {
      var n = a.overdue.length + a.dueToday.length;
      var left = sessionLeft();
      title = "Review " + plural(Math.min(n, MAX_ITEMS_PER_SESSION), "item") + " you're about to forget";
      why = (a.overdue.length ? plural(a.overdue.length, "item") + " overdue" : "") +
        (a.overdue.length && a.dueToday.length ? " and " : "") +
        (a.dueToday.length ? plural(a.dueToday.length, "item") + " due today" : "") +
        ". Most overdue first." +
        (n > MAX_ITEMS_PER_SESSION ? " Today's session is capped at " + MAX_ITEMS_PER_SESSION + "; the rest come back next time." : "");
      action = left && left < (session ? session.blockIds.length : 0) ? "Continue review" : "Start review";
      href = "#review-queue";
      isReview = true;
    } else if (current.id === "improve") {
      var w = a.weak[0];
      title = "Improve " + w.info.lesson + ", " + exerciseName(w.info);
      why = "Your best score is " + w.best + " of " + w.total + " in " + w.info.lesson + " (" + w.info.level + "). " +
        (a.weak.length > 1 ? plural(a.weak.length - 1, "more exercise") + " also scored under " + Math.round(IMPROVE_BELOW * 100) + "%." : "Get it to " + Math.round(IMPROVE_BELOW * 100) + "% or more.");
      action = "Practice this exercise";
      href = weakHref(w);
    } else {
      title = (a.next.kind === "lesson" ? "Start “" + a.next.title + "”" : a.next.title) + (a.next.level && a.next.kind === "lesson" ? " (" + a.next.level + ")" : "");
      why = (a.reviewedToday.length ? "Today's review is done. " : "") + a.next.why;
      action = a.next.kind === "lesson" ? "Open the lesson" : a.next.kind === "test" ? "Take the test" : "Go";
      href = a.next.url;
    }
    box.innerHTML =
      '<p class="eyebrow">Your next step</p>' +
      '<h2 id="next-heading" class="coach-next__title">' + esc(title) + "</h2>" +
      '<p class="coach-next__why">' + esc(why) + "</p>" +
      '<a class="btn btn--accent coach-next__go" href="' + esc(href) + '"' + (isReview ? " data-start-review" : "") + ">" + esc(action) + "</a>";
  }

  /* ---------------- progress overview ---------------- */

  // The summary at the top. Each box is a button that opens its details
  // right below the boxes (one at a time; clicking it again closes it).
  var openTile = null;

  function renderStats(a) {
    var p = a.progress || { streak: { count: 0 } };
    var streak = p.streak || { count: 0 };
    // A streak whose last active day is before yesterday has lapsed.
    var streakNow = streak.lastActiveDate && streak.lastActiveDate >= todayStr(-1) ? streak.count : 0;
    var accuracy = a.attempts ? Math.round((a.correct / a.attempts) * 100) + "%" : "—";
    var masteredPct = a.tracked ? Math.round((a.mastered / a.tracked) * 100) : 0;
    var todayRight = a.reviewedToday.length - a.missedToday.length;
    var tiles = [
      { id: "streak", value: streakNow, label: "Day streak" },
      { id: "today", value: a.reviewedToday.length, label: "Items practiced today" + (a.reviewedToday.length ? " · " + todayRight + " right" : "") },
      { id: "left", value: a.overdue.length + a.dueToday.length, label: "Reviews left today" },
      { id: "accuracy", value: accuracy, label: "Accuracy, all answers" + (a.attempts ? " (" + a.attempts + ")" : "") },
      { id: "exercises", value: a.exercisesDone, label: "Exercises completed" },
      { id: "lessons", value: a.lessonsStarted + " / " + a.lessonsTotal, label: "Lessons started" },
    ];
    var html = tiles.map(function (t) {
      var open = openTile === t.id;
      return '<button type="button" class="progress-stat coach-tile' + (open ? " is-open" : "") + '" data-tile="' + t.id + '" aria-expanded="' + open + '" aria-controls="coach-detail">' +
        "<strong>" + esc(t.value) + "</strong><span>" + esc(t.label) + "</span></button>";
    }).join("");
    var mOpen = openTile === "mastery";
    html += '<button type="button" class="coach-mastery coach-tile' + (mOpen ? " is-open" : "") + '" data-tile="mastery" aria-expanded="' + mOpen + '" aria-controls="coach-detail">' +
        '<span class="progress-label"><span>Mastered items</span><span>' + a.mastered + " of " + a.tracked + " practiced (" + masteredPct + "%)</span></span>" +
        '<span class="progress-track" role="presentation"><span class="progress-track__fill" style="width:' + masteredPct + '%"></span></span>' +
        '<span class="coach-mastery__hint">An item is mastered when you get it right twice, on different days.</span>' +
      "</button>";
    document.getElementById("coach-stats").innerHTML = html;
    renderDetail(a, { streakNow: streakNow, streak: streak });
  }

  function levelOrder(code) {
    for (var i = 0; i < order.levels.length; i++) if (order.levels[i].code === code) return i;
    return 99;
  }

  function renderDetail(a, ctx) {
    var box = document.getElementById("coach-detail");
    if (!openTile) { box.hidden = true; box.innerHTML = ""; return; }
    var items = window.MasteryTracker.getState().items || {};
    var ex = (a.progress && a.progress.exercises) || {};
    var html = "";
    var empty = function (t) { return '<p class="coach-empty">' + t + "</p>"; };

    if (openTile === "streak") {
      html = "<h3 class=\"coach-h3\">Day streak</h3>" +
        (ctx.streakNow
          ? "<p>You've studied " + plural(ctx.streakNow, "day") + " in a row. Last active: " + (ctx.streak.lastActiveDate === a.today ? "today" : "yesterday") + "." +
            (ctx.streak.lastActiveDate === a.today ? "" : " Submit one exercise today to keep it going.") + "</p>"
          : "<p>No streak right now" + (ctx.streak.lastActiveDate ? " (last active " + esc(ctx.streak.lastActiveDate) + ")" : "") + ". Submit an exercise today to start one, and come back tomorrow to grow it.</p>");
    } else if (openTile === "today") {
      html = "<h3 class=\"coach-h3\">Items practiced today</h3>";
      html += a.reviewedToday.length
        ? '<ul class="coach-items">' + a.reviewedToday.map(function (k) {
            var it = index[k], ok = items[k].lastCorrect !== false;
            return '<li class="' + (ok ? "is-right" : "is-wrong") + '"><span class="coach-items__mark" aria-label="' + (ok ? "right" : "wrong") + '">' + (ok ? "✓" : "✗") + "</span>" +
              '<span><span class="coach-items__prompt">' + esc(promptText(it)) + '</span><span class="coach-items__meta">' + esc(it.level) + " · " + esc(it.lessonTitle) + "</span></span></li>";
          }).join("") + "</ul>"
        : empty("Nothing yet today. Answers you submit in lessons or in the review below are counted here.");
    } else if (openTile === "left") {
      var n = a.overdue.length + a.dueToday.length;
      html = "<h3 class=\"coach-h3\">Reviews left today</h3>" + (n
        ? "<p>" + (a.overdue.length ? plural(a.overdue.length, "item") + " overdue" : "") + (a.overdue.length && a.dueToday.length ? " and " : "") + (a.dueToday.length ? plural(a.dueToday.length, "item") + " due today" : "") + ".</p>" +
          '<p><a class="btn btn--accent btn--small" href="#review-queue" data-start-review>Start review</a></p>'
        : empty(a.reviewedToday.length ? "None. Today's review is done." : "None. Items come back here on the day you're about to forget them."));
    } else if (openTile === "accuracy" || openTile === "mastery") {
      var by = {};
      Object.keys(items).forEach(function (k) {
        if (!index[k]) return;
        var l = index[k].level, r = items[k];
        if (!by[l]) by[l] = { attempts: 0, correct: 0, tracked: 0, mastered: 0 };
        by[l].attempts += r.attempts || 0; by[l].correct += r.correctCount || 0;
        by[l].tracked++; if (r.masteryStatus === "mastered") by[l].mastered++;
      });
      var levels = Object.keys(by).sort(function (x, y) { return levelOrder(x) - levelOrder(y); });
      var isAcc = openTile === "accuracy";
      html = "<h3 class=\"coach-h3\">" + (isAcc ? "Accuracy by level" : "Mastered items by level") + "</h3>";
      html += levels.length ? '<div class="coach-bars">' + levels.map(function (l) {
        var b = by[l];
        var pct = isAcc ? Math.round((b.correct / b.attempts) * 100) : Math.round((b.mastered / b.tracked) * 100);
        var label = isAcc ? b.correct + " of " + plural(b.attempts, "answer") + " right (" + pct + "%)" : b.mastered + " of " + b.tracked + " mastered (" + pct + "%)";
        return '<div class="progress-panel__level-row"><div class="progress-label"><span>' + esc(l) + "</span><span>" + label + "</span></div>" +
          '<div class="progress-track"><div class="progress-track__fill" style="width:' + pct + '%"></div></div></div>';
      }).join("") + "</div>" : empty("No answers recorded yet. Submit an exercise in any lesson.");
      if (isAcc && a.mistakes.length) html += '<p><a href="#coach-mistakes">See your ' + plural(a.mistakes.length, "open mistake") + " →</a></p>";
    } else if (openTile === "exercises") {
      var done = Object.keys(ex).filter(function (id) { return exerciseInfo[id]; });
      var byLesson = {};
      done.forEach(function (id) {
        var info = exerciseInfo[id];
        (byLesson[info.url] = byLesson[info.url] || { info: info, list: [] }).list.push(id);
      });
      var urls = Object.keys(byLesson).sort(function (x, y) {
        return (levelOrder(byLesson[x].info.level) - levelOrder(byLesson[y].info.level)) || (x < y ? -1 : 1);
      });
      html = "<h3 class=\"coach-h3\">Exercises completed</h3>";
      html += urls.length ? urls.map(function (u) {
        var g = byLesson[u];
        return '<div class="coach-group"><p class="coach-group__title"><a href="' + esc(u) + '">' + esc(g.info.lesson) + "</a> (" + g.info.level + ")</p>" +
          '<ul class="coach-items">' + g.list.map(function (id) {
            var r = ex[id], pct = r.total ? Math.round((r.bestCorrect / r.total) * 100) : null;
            var weak = pct !== null && pct < IMPROVE_BELOW * 100;
            return '<li class="' + (weak ? "is-wrong" : "is-right") + '"><span class="coach-items__mark" aria-hidden="true">' + (weak ? "!" : "✓") + "</span>" +
              '<a href="' + esc(u + "#ex-" + encodeURIComponent(id)) + '">' + esc(exerciseName(exerciseInfo[id])) + "</a>" +
              '<span class="coach-items__score">' + (pct === null ? "done" : "best " + r.bestCorrect + " of " + r.total + " (" + pct + "%)") + "</span></li>";
          }).join("") + "</ul></div>";
      }).join("") : empty("None yet. Submit any exercise on a lesson page.");
    } else if (openTile === "lessons") {
      html = "<h3 class=\"coach-h3\">Lessons started</h3>";
      var any = false;
      html += order.levels.map(function (l) {
        var started = l.lessons.filter(function (lesson) { return lesson.exercises.some(function (id) { return !!ex[id]; }); });
        if (!started.length) return "";
        any = true;
        return '<div class="coach-group"><p class="coach-group__title">' + esc(l.code) + " · " + started.length + " of " + l.lessons.length + " started</p>" +
          '<ul class="coach-items">' + started.map(function (lesson) {
            var n = lesson.exercises.filter(function (id) { return !!ex[id]; }).length;
            return '<li class="is-right"><span class="coach-items__mark" aria-hidden="true">✓</span><a href="' + esc(lesson.url) + '">' + esc(lesson.title) + "</a>" +
              '<span class="coach-items__score">' + n + " of " + lesson.exercises.length + " exercises</span></li>";
          }).join("") + "</ul></div>";
      }).join("");
      if (!any) html += empty("None yet.");
      html += '<p>Next: <a href="' + esc(a.next.url) + '">' + esc(a.next.title) + "</a>" + (a.next.level ? " (" + a.next.level + ")" : "") + "</p>";
    }
    box.innerHTML = html;
    box.hidden = false;
  }

  /* ---------------- mistakes ---------------- */

  // A compact card: lesson + how often, the prompt, then the wrong and
  // right answers on one line each.
  function mistakeCard(x) {
    var item = x.item, m = x.m;
    var recurring = m.incorrectCount >= 2;
    var fixed = m.lastCorrect === true;
    return '<li class="mistake' + (recurring ? " mistake--recurring" : "") + '">' +
      '<div class="mistake__meta">' +
        '<span class="mistake__lesson">' + esc(item.level) + " · " + esc(item.lessonTitle) + "</span>" +
        (recurring ? '<span class="mistake__tag mistake__tag--recurring">×' + m.incorrectCount + "</span>" : "") +
        (fixed ? '<span class="mistake__tag mistake__tag--fixed">Right last time</span>' : "") +
      "</div>" +
      '<p class="mistake__prompt">' + esc(promptText(item)) + "</p>" +
      (m.lastWrongAnswer ? '<p class="mistake__ans mistake__ans--wrong"><span aria-label="Your answer">✗</span> <s>' + esc(m.lastWrongAnswer) + "</s></p>" : "") +
      '<p class="mistake__ans mistake__ans--right"><span aria-label="Correct answer">✓</span> ' + esc(answerText(item)) + "</p>" +
      (item.explanation ? '<p class="mistake__why">' + esc(item.explanation) + "</p>" : "") +
      '<a class="mistake__link" href="' + esc(lessonLink(item)) + '">Revisit in the lesson →</a>' +
      "</li>";
  }

  // Bounded however many mistakes there are: the first MISTAKES_FIRST,
  // then MISTAKES_MORE per click, and buttons to show one lesson only.
  var mistakeFilter = null;     // lesson url, or null for all
  var mistakeLimit = MISTAKES_FIRST;

  function renderMistakes(a) {
    var body = document.getElementById("mistakes-body");
    if (!a.mistakes.length) {
      body.innerHTML = '<p class="coach-empty">' + (a.tracked
        ? "No open mistakes. Everything you've missed has since been mastered."
        : "Nothing yet. Answers you get wrong in lesson exercises will show up here, with the correct answer and why.") + "</p>";
      return;
    }
    if (mistakeFilter && !a.weakLessons.some(function (l) { return l.url === mistakeFilter; })) mistakeFilter = null;
    var recurring = a.mistakes.filter(function (x) { return x.m.incorrectCount >= 2; }).length;
    var html = '<p class="coach-lede">' + plural(a.mistakes.length, "item") + " missed and not yet mastered" +
      (recurring ? ", " + recurring + " of them more than once (×)" : "") +
      ". They come back in your review until you get them right twice, on different days.</p>";
    if (a.weakLessons.length > 1) {
      html += '<div class="mistake-filter" role="group" aria-label="Show mistakes from one lesson">' +
        '<button type="button" class="tag-chip" data-mistake-filter="" aria-pressed="' + !mistakeFilter + '">All (' + a.mistakes.length + ")</button>" +
        a.weakLessons.slice(0, 8).map(function (l) {
          return '<button type="button" class="tag-chip" data-mistake-filter="' + esc(l.url) + '" aria-pressed="' + (mistakeFilter === l.url) + '">' +
            esc(l.title) + " (" + l.items + ")</button>";
        }).join("") + "</div>";
    }
    var list = mistakeFilter ? a.mistakes.filter(function (x) { return x.item.lessonUrl === mistakeFilter; }) : a.mistakes;
    var shown = list.slice(0, mistakeLimit);
    html += '<ul class="mistake-list">' + shown.map(mistakeCard).join("") + "</ul>";
    var rest = list.length - shown.length;
    html += '<p class="mistake-count">Showing ' + shown.length + " of " + list.length +
      (rest ? ' <button type="button" class="btn btn--ghost btn--small" data-mistakes-more>Show ' + Math.min(rest, MISTAKES_MORE) + " more</button>" : "") +
      (mistakeLimit > MISTAKES_FIRST ? ' <button type="button" class="btn btn--ghost btn--small" data-mistakes-less>Show fewer</button>' : "") + "</p>";
    body.innerHTML = html;
  }

  /* ---------------- recommendations ---------------- */

  // Every exercise under the bar, right under the plan, so the student
  // can pick which one to do. Worst first; each link opens the exercise.
  // Step 3's own section: every exercise under the bar, worst first,
  // each opening its exercise, so the student can pick one.
  function renderImprove(a) {
    var box = document.getElementById("improve-body");
    if (!a.weak.length) {
      box.innerHTML = '<p class="coach-empty">' + (a.exercisesDone
        ? "None. Every exercise you've done has a best score of " + Math.round(IMPROVE_BELOW * 100) + "% or more."
        : "Nothing yet. Exercises you score under " + Math.round(IMPROVE_BELOW * 100) + "% on will be listed here.") + "</p>";
      return;
    }
    box.innerHTML = '<p class="coach-lede">Your best score on ' + (a.weak.length === 1 ? "this exercise is" : "these " + a.weak.length + " exercises is") +
      " under " + Math.round(IMPROVE_BELOW * 100) + "%. Worst first. Pick any one to open it.</p>" +
      '<ul class="rec-list">' + a.weak.map(function (w) {
        var pct = Math.round((w.best / w.total) * 100);
        return '<li class="rec"><a href="' + esc(weakHref(w)) + '">' +
          '<span class="rec__title">' + esc(w.info.lesson) + " · " + esc(exerciseName(w.info)) + "</span>" +
          '<span class="rec__meta">' + w.info.level + " · best " + w.best + " of " + w.total + " (" + pct + "%)</span></a></li>";
      }).join("") + "</ul>";
  }

  // Step 5: new material only -- the next lesson, then the two after it
  // in course order (lessons not started yet).
  function renderRecs(a) {
    var body = document.getElementById("recs-body");
    var html = '<p class="coach-lede">New material, in course order. Start with the first.</p>' +
      '<ol class="rec-list"><li class="rec rec--next"><a href="' + esc(a.next.url) + '">' +
      '<span class="rec__title">' + esc(a.next.title) + (a.next.level ? " (" + a.next.level + ")" : "") + "</span>" +
      '<span class="rec__meta">Next · ' + esc(a.next.why) + "</span></a></li>" +
      a.after.map(function (l) {
        return '<li class="rec"><a href="' + esc(l.url) + '"><span class="rec__title">' + esc(l.title) + " (" + l.level + ")</span>" +
          '<span class="rec__meta">After that</span></a></li>';
      }).join("") + "</ol>";
    body.innerHTML = html;
  }

  /* ---------------- review session ---------------- */

  function cleanItem(item, key) {
    var clean = {};
    Object.keys(item).forEach(function (k) { if (INDEX_ONLY_FIELDS.indexOf(k) === -1) clean[k] = item[k]; });
    // The full key (block id + item id) goes in as the id, so the result
    // is recorded against the same history as the lesson it came from.
    clean.id = key;
    return clean;
  }

  function buildSession(keys, label) {
    var wrap = document.getElementById("review-blocks");
    sessionRound++;
    var groups = {}, groupOrder = [];
    keys.forEach(function (key) {
      var item = index[key];
      var g = item.level + "::" + item.exerciseType;
      if (!groups[g]) { groups[g] = []; groupOrder.push(g); }
      groups[g].push(cleanItem(item, key));
    });
    var ids = [];
    groupOrder.forEach(function (g, i) {
      var parts = g.split("::"), level = parts[0], type = parts[1];
      var id = "review-" + sessionRound + "-" + i + "-" + g.replace(/[^a-z0-9]/gi, "-");
      var data = {
        id: id, type: type,
        title: (TYPE_LABELS[type] || type) + " — " + level + " " + label,
        instructions: "Mixed review from " + level + " lessons you've already studied.",
        items: groups[g],
      };
      var container = document.createElement("div");
      container.className = "exercise-block";
      container.id = id;
      var script = document.createElement("script");
      script.type = "application/json";
      script.className = "exercise-data";
      script.textContent = JSON.stringify(data);
      container.appendChild(script);
      wrap.appendChild(container);
      ids.push(id);
    });
    if (window.ExerciseEngine && typeof window.ExerciseEngine.init === "function") window.ExerciseEngine.init();
    session = { keys: keys, blockIds: (session ? session.blockIds : []).concat(ids) };
    return ids;
  }

  function renderStatus(a) {
    var box = document.getElementById("review-status-box");
    var done = document.getElementById("review-done");
    var left = sessionLeft();
    var total = session ? session.blockIds.length : 0;

    if (total && left) {
      box.hidden = false;
      box.innerHTML = "<p><strong>" + plural(session.keys.length, "item") + " in today's session</strong>, in " +
        plural(total, "exercise") + ". " + (left < total ? plural(total - left, "exercise") + " submitted, " + left + " to go." : "Submit each exercise to record your answers.") + "</p>";
      done.hidden = true;
      return;
    }

    if (!total && !a.reviewedToday.length) {
      box.hidden = false;
      box.innerHTML = a.tracked
        ? "<p><strong>Nothing is due today.</strong> Items come back here on the day you're about to forget them.</p>"
        : "<p><strong>No reviews yet.</strong> Do the exercises in any lesson, and the items you answer will come back here for review.</p>";
      done.hidden = true;
      return;
    }

    // Finished: the session is all submitted, or everything due was
    // already practiced earlier today.
    box.hidden = true;
    var right = a.reviewedToday.length - a.missedToday.length;
    var remaining = a.overdue.length + a.dueToday.length;
    var html = '<p class="coach-done__title">✓ Today\'s review is done</p>' +
      "<p>You practiced " + plural(a.reviewedToday.length, "item") + " today and got " + right + " right." +
      (a.missedToday.length ? " The " + (a.missedToday.length === 1 ? "one" : a.missedToday.length + " items") + " you missed will come back tomorrow, and " + (a.missedToday.length === 1 ? "is" : "are") + " listed under Your mistakes below." : "") +
      (remaining ? " " + plural(remaining, "more item") + " are due; they'll be in your next session." : "") + "</p>";
    html += '<p class="coach-done__actions">' +
      '<a class="btn btn--accent" href="' + esc(a.weak.length ? weakHref(a.weak[0]) : a.next.url) + '">' +
      esc(!a.weak.length ? "Next: " + a.next.title : "Next: improve " + a.weak[0].info.lesson + ", Exercise " + toRoman(a.weak[0].info.num)) + "</a>";
    if (a.missedToday.length) html += ' <button type="button" class="btn btn--ghost" data-retry-missed>Practice today\'s ' + plural(a.missedToday.length, "mistake") + " again</button>";
    if (remaining) html += ' <button type="button" class="btn btn--ghost" data-more-review>Review ' + Math.min(remaining, MAX_ITEMS_PER_SESSION) + " more</button>";
    html += "</p>";
    var wasHidden = done.hidden;
    done.innerHTML = html;
    done.hidden = false;
    if (wasHidden && total) done.focus();
  }

  /* ---------------- wiring ---------------- */

  function refresh() {
    var a = analyse();
    renderNext(a);
    renderStats(a);
    renderStatus(a);
    renderMistakes(a);
    renderImprove(a);
    renderRecs(a);
    return a;
  }

  function startReview() {
    var target = null;
    if (session) {
      session.blockIds.some(function (id) {
        var b = document.getElementById(id);
        if (b && !b.hasAttribute("data-submitted")) { target = b; return true; }
        return false;
      });
    }
    target = target || document.getElementById("review-queue");
    target.scrollIntoView({ behavior: "smooth", block: "start" });
    var focusable = target.querySelector("input, select, textarea, button");
    if (focusable) setTimeout(function () { focusable.focus({ preventScroll: true }); }, 400);
  }

  function sessionKeys(a) {
    return a.overdue.concat(a.dueToday).slice(0, MAX_ITEMS_PER_SESSION);
  }

  var started = false;
  function main() {
    var statusBox = document.getElementById("review-status-box");
    if (!statusBox || started) return;
    started = true;
    if (!window.MasteryTracker) {
      statusBox.innerHTML = "<p>Review tracking isn't available right now.</p>";
      return;
    }

    Promise.all([
      fetch("assets/data/exercise-items-index.json").then(function (r) { return r.json(); }),
      fetch("assets/data/lesson-order.json").then(function (r) { return r.json(); }),
    ]).then(function (res) {
      index = res[0];
      order = res[1];
      order.levels.forEach(function (l) {
        l.lessons.forEach(function (lesson) {
          lesson.exercises.forEach(function (id, i) {
            exerciseInfo[id] = { lesson: lesson.title, level: l.code, url: lesson.url, title: id, num: i + 1 };
          });
        });
      });
      Object.keys(index).forEach(function (k) {
        var it = index[k];
        if (exerciseInfo[it.exerciseId]) exerciseInfo[it.exerciseId].title = it.exerciseTitle || it.exerciseId;
      });

      var a = analyse();
      var keys = sessionKeys(a);
      if (keys.length) buildSession(keys, "Review");
      refresh();

      // Each submitted block: mark it, then redraw from the updated
      // records (mastery.js records the answers in its own listener,
      // so wait a tick for it).
      document.addEventListener("exercise:submitted", function (e) {
        var block = e.target && e.target.closest ? e.target.closest(".exercise-block") : null;
        if (block) block.setAttribute("data-submitted", "");
        setTimeout(refresh, 0);
      });
      // "Retry" in a block makes it answerable again.
      document.addEventListener("click", function (e) {
        var t = e.target;
        if (!t || !t.closest) return;
        if (t.closest("[data-start-review]")) { e.preventDefault(); startReview(); return; }
        var mf = t.closest("[data-mistake-filter]");
        if (mf) { mistakeFilter = mf.getAttribute("data-mistake-filter") || null; mistakeLimit = MISTAKES_FIRST; renderMistakes(analyse()); return; }
        if (t.closest("[data-mistakes-more]")) { mistakeLimit += MISTAKES_MORE; renderMistakes(analyse()); return; }
        if (t.closest("[data-mistakes-less]")) {
          mistakeLimit = MISTAKES_FIRST; renderMistakes(analyse());
          document.getElementById("coach-mistakes").scrollIntoView({ block: "start" });
          return;
        }
        var tile = t.closest("[data-tile]");
        if (tile) {
          var id = tile.getAttribute("data-tile");
          openTile = openTile === id ? null : id;
          refresh();
          return;
        }
        if (t.closest("[data-retry-missed]")) {
          var now = analyse();
          buildSession(now.missedToday.slice(0, MAX_ITEMS_PER_SESSION), "Mistakes Again");
          refresh(); startReview(); return;
        }
        if (t.closest("[data-more-review]")) {
          buildSession(sessionKeys(analyse()), "Review");
          refresh(); startReview(); return;
        }
        var retry = t.closest(".exercise-block .btn");
        if (retry && /retry|try again/i.test(retry.textContent)) {
          var b = retry.closest(".exercise-block");
          if (b && b.hasAttribute("data-submitted")) { b.removeAttribute("data-submitted"); setTimeout(refresh, 0); }
        }
      });
      // Progress synced down from the account (cloud-sync.js) changes the picture.
      document.addEventListener("rt:account", function () { setTimeout(refresh, 0); });
    }).catch(function (err) {
      if (window.console) console.warn("[today-review]", err);
      statusBox.innerHTML = "<p>Couldn't load your study plan right now. Check your connection and reload the page.</p>";
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", main);
  } else {
    main();
  }
})();
