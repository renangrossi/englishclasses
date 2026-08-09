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
  function renderBotText(raw) {
    var safe = escapeHtml(raw);
    safe = safe.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    safe = safe.replace(/\n\s*[-*]\s+/g, "\n\u2022 ");
    safe = safe.replace(/\n/g, "<br>");
    return safe;
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
