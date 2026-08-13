/*!
 * Renan the Teacher — AI English Teacher chat widget
 * -----------------------------------------------------------------
 * No login, no account, no data stored beyond the current browser
 * session. Sends the student's message (plus a short in-memory
 * conversation history, cleared when the tab/window closes) to a
 * Cloudflare Worker, which holds the real API key server-side and
 * forwards the request to Groq. This file never sees or stores an
 * API key.
 * -----------------------------------------------------------------
 */
(function () {
  "use strict";

  var scriptTag = document.querySelector("script[data-ai-endpoint]");
  var toggle = document.querySelector("[data-ai-teacher-toggle]");
  if (!scriptTag || !toggle) return;

  var ENDPOINT = scriptTag.getAttribute("data-ai-endpoint");
  var panel = document.querySelector("[data-ai-teacher-panel]");
  var closeBtn = document.querySelector("[data-ai-teacher-close]");
  var messagesBox = document.querySelector("[data-ai-teacher-messages]");
  var form = document.querySelector("[data-ai-teacher-form]");
  var input = document.querySelector("[data-ai-teacher-input]");
  var sendBtn = document.querySelector("[data-ai-teacher-send]");
  var hint = document.querySelector("[data-ai-teacher-hint]");

  // Conversation history lives only in memory for this page view —
  // never written to localStorage/sessionStorage, and lost on reload
  // or tab close. Capped so a long chat can't blow up the request size.
  var history = [];
  var MAX_HISTORY_TURNS = 6;

  // Anonymous rate-limiting identity: a random ID with no personal
  // information, stored locally only so the same browser can be
  // recognized for a fair per-day quota. Not sent anywhere except as
  // an opaque token to our own Worker.
  function getAnonId() {
    try {
      var id = localStorage.getItem("aiTeacherAnonId");
      if (!id) {
        id = "anon-" + Math.random().toString(36).slice(2) + Date.now().toString(36);
        localStorage.setItem("aiTeacherAnonId", id);
      }
      return id;
    } catch (e) {
      return "anon-session-" + Date.now();
    }
  }

  // Cheap, page-derived context so the Worker can ground answers in
  // the real course structure — no page markup changes needed. The
  // level comes from the URL (levels/a1/..., levels/a2.html, ...);
  // the "lesson" name is just the first segment of <title> (e.g.
  // "Adjectives — A1 English Grammar — Renan the Teacher" -> "Adjectives").
  // The Worker re-validates all of this against its own course
  // catalog before ever using it — nothing here is trusted as-is.
  var courseContext = (function () {
    var path = window.location.pathname;
    var levelMatch = path.match(/\/levels\/(a1|a2|b1|b2|c1|c2)(?:[\/.]|$)/i);
    var titleParts = (document.title || "").split("—"); // split on em dash "—"
    return {
      currentLevel: levelMatch ? levelMatch[1].toUpperCase() : "",
      currentLesson: titleParts[0] ? titleParts[0].trim() : "",
      currentLessonUrl: path,
    };
  })();

  function toggleOpen(open) {
    var willOpen = open !== undefined ? open : panel.hidden;
    panel.hidden = !willOpen;
    toggle.setAttribute("aria-expanded", String(willOpen));
    if (willOpen) {
      input.focus();
      messagesBox.scrollTop = messagesBox.scrollHeight;
    }
  }

  toggle.addEventListener("click", function () { toggleOpen(); });
  closeBtn.addEventListener("click", function () { toggleOpen(false); });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !panel.hidden) toggleOpen(false);
  });
  document.addEventListener("click", function (e) {
    if (panel.hidden) return;
    if (panel.contains(e.target) || toggle.contains(e.target)) return;
    toggleOpen(false);
  });
  panel.addEventListener("click", function (e) { e.stopPropagation(); });

  function escapeHtml(s) {
    var d = document.createElement("div");
    d.textContent = String(s || "");
    return d.innerHTML;
  }

  // Very small, safe subset of markdown-ish formatting the model
  // tends to use (bold, line breaks, simple numbered/bulleted lists)
  // rendered without any HTML injection risk, since we escape first.
  //
  // Markdown tables get special handling: the system prompt discourages
  // them, but if the model produces one anyway (well-formed, malformed,
  // or truncated), a raw "| a | b |" row is unreadable in a narrow chat
  // bubble. Rather than trying to render an actual <table> (which isn't
  // valid inside the <p> these messages live in), every pipe-delimited
  // row is converted into a short bullet line instead \u2014 this guarantees
  // the student never sees broken/raw Markdown syntax.
  function isTableSeparatorRow(line) {
    return /^\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?$/.test(line.trim());
  }

  function splitTableRow(line) {
    var t = line.trim().replace(/^\|/, "").replace(/\|$/, "");
    return t.split("|").map(function (c) { return c.trim(); }).filter(function (c) { return c.length > 0; });
  }

  function inlineBold(s) {
    return s.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  }

  // Base the site's own relative paths (as sent to the model in the
  // Worker's "Course context") resolve against — used only by the bare
  // relative-path safety net below.
  var SITE_BASE_URL = "https://renangrossi.github.io/englishclasses/";

  // Turns Markdown links [Label](url) into real, clickable <a> elements.
  // Two safety nets, for on the rare chance the model doesn't follow
  // the system prompt's "always use [Label](url)" instruction:
  //   1. A bare absolute http(s) URL still becomes a clickable link
  //      (using the raw URL itself as the label, since there's no
  //      label to reuse).
  //   2. A bare *relative* site path (e.g. "levels/a1/to-be-am-is-are.html"
  //      or "levels/b1.html#revision", missing the "https://…" origin
  //      entirely) is resolved against SITE_BASE_URL and linked too —
  //      this is the case that otherwise shows up as inert, unclickable
  //      plain text in the chat.
  // A single regex/replace pass avoids double-wrapping a URL that was
  // already turned into an <a> by an earlier branch in the same pass.
  var RELATIVE_PATH_PATTERN = "(?:levels|cefr)\\/[A-Za-z0-9\\-\\/.]+\\.(?:html|pdf|docx)(?:#[A-Za-z0-9\\-]+)?" +
    "|(?:dictionary|exercises|placement-test|simulated-exams|extras|progress)\\.html(?:#[A-Za-z0-9\\-]+)?";
  var LINK_PATTERN = new RegExp(
    "\\[([^\\[\\]]+)\\]\\((https?:\\/\\/[^\\s()]+)\\)" + // 1 label, 2 mdUrl
    "|(https?:\\/\\/[^\\s<>\"']+)" + // 3 bareUrl
    "|\\b(" + RELATIVE_PATH_PATTERN + ")\\b", // 4 relPath
    "g"
  );
  function inlineLinks(s) {
    return s.replace(LINK_PATTERN, function (match, label, mdUrl, bareUrl, relPath) {
      if (label && mdUrl) {
        return '<a href="' + mdUrl + '" target="_blank" rel="noopener noreferrer">' + label + "</a>";
      }
      if (relPath) {
        return '<a href="' + SITE_BASE_URL + relPath + '" target="_blank" rel="noopener noreferrer">' + relPath + "</a>";
      }
      // Trim trailing punctuation (., , ; : ! ? ) ]) that's almost
      // always sentence punctuation, not part of the URL itself.
      var trimmed = bareUrl.replace(/[.,;:!?)\]]+$/, "");
      var trailing = bareUrl.slice(trimmed.length);
      return '<a href="' + trimmed + '" target="_blank" rel="noopener noreferrer">' + trimmed + "</a>" + trailing;
    });
  }

  // The system prompt asks the model to avoid "#" heading syntax, but
  // as a safety net (same reasoning as the table handling above): if
  // it slips one in anyway, never show the raw "### Heading" text —
  // render it as a bold line instead, since <p> can't hold real
  // heading elements and a literal "###" reads as broken Markdown.
  function formatLine(line) {
    var heading = line.match(/^#{1,6}\s+(.*)$/);
    if (heading) return "<strong>" + inlineLinks(inlineBold(heading[1])) + "</strong>";
    return inlineLinks(inlineBold(line));
  }

  function renderBotText(raw) {
    var safe = escapeHtml(raw);
    var lines = safe.split("\n");
    var out = [];
    var i = 0;
    while (i < lines.length) {
      var line = lines[i];
      if (/^-{3,}$/.test(line.trim())) {
        // Bare "---" horizontal-rule Markdown — drop it rather than
        // showing literal dashes; surrounding blank lines already
        // give enough visual separation in a chat bubble.
        i++;
        continue;
      }
      if (line.indexOf("|") !== -1 && line.trim() !== "") {
        var block = [];
        var j = i;
        while (j < lines.length && lines[j].indexOf("|") !== -1 && lines[j].trim() !== "") {
          block.push(lines[j]);
          j++;
        }
        block.forEach(function (rowLine, idx) {
          if (idx === 1 && isTableSeparatorRow(rowLine)) return; // drop the "---|---" row
          var cells = splitTableRow(rowLine);
          if (cells.length === 0) return;
          var label = inlineLinks(cells[0].replace(/\*\*/g, ""));
          var rest = cells.slice(1).map(function (c) { return inlineLinks(inlineBold(c)); });
          out.push("\u2022 <strong>" + label + "</strong>" + (rest.length ? " \u2014 " + rest.join(" \u2014 ") : ""));
        });
        i = j;
        continue;
      }
      out.push(formatLine(line));
      i++;
    }
    var html = out.join("\n");
    html = html.replace(/\n\s*[-*]\s+/g, "\n\u2022 ");
    html = html.replace(/\n/g, "<br>");
    return html;
  }

  function addMessage(role, text) {
    var msg = document.createElement("div");
    msg.className = "ai-teacher-msg ai-teacher-msg--" + (role === "user" ? "user" : "bot");
    var p = document.createElement("p");
    if (role === "user") {
      p.textContent = text;
    } else {
      p.innerHTML = renderBotText(text);
    }
    msg.appendChild(p);
    messagesBox.appendChild(msg);
    messagesBox.scrollTop = messagesBox.scrollHeight;
    return msg;
  }

  function addTypingIndicator() {
    var msg = document.createElement("div");
    msg.className = "ai-teacher-msg ai-teacher-msg--bot ai-teacher-msg--typing";
    msg.innerHTML = "<p><span></span><span></span><span></span></p>";
    messagesBox.appendChild(msg);
    messagesBox.scrollTop = messagesBox.scrollHeight;
    return msg;
  }

  function setBusy(busy) {
    input.disabled = busy;
    sendBtn.disabled = busy;
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var text = input.value.trim();
    if (!text) return;

    addMessage("user", text);
    history.push({ role: "user", content: text });
    if (history.length > MAX_HISTORY_TURNS * 2) {
      history = history.slice(-MAX_HISTORY_TURNS * 2);
    }
    input.value = "";
    input.style.height = "auto";
    setBusy(true);
    var typing = addTypingIndicator();

    fetch(ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        history: history.slice(0, -1),
        anonId: getAnonId(),
        page: window.location.pathname,
        currentLevel: courseContext.currentLevel,
        currentLesson: courseContext.currentLesson,
        currentLessonUrl: courseContext.currentLessonUrl,
      }),
    })
      .then(function (res) {
        if (res.status === 429) {
          throw new Error("RATE_LIMIT");
        }
        if (!res.ok) throw new Error("SERVER_ERROR");
        return res.json();
      })
      .then(function (data) {
        typing.remove();
        var reply = data && data.reply ? data.reply : "Sorry, I didn't get a response. Please try again.";
        addMessage("bot", reply);
        history.push({ role: "assistant", content: reply });
      })
      .catch(function (err) {
        typing.remove();
        if (err && err.message === "RATE_LIMIT") {
          addMessage("bot", "You've reached today's question limit for the AI Teacher. Please come back tomorrow, or keep practicing with the course's own exercises in the meantime!");
        } else {
          addMessage("bot", "Sorry, I couldn't reach the AI Teacher right now. Please check your connection and try again in a moment.");
        }
      })
      .finally(function () {
        setBusy(false);
        input.focus();
      });
  });

  // Auto-grow the textarea up to a reasonable max height.
  input.addEventListener("input", function () {
    input.style.height = "auto";
    input.style.height = Math.min(input.scrollHeight, 120) + "px";
  });
  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      form.requestSubmit();
    }
  });
})();
