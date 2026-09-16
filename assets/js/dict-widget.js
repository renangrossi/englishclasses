/*!
 * Renan the Teacher — Floating Dictionary Widget
 * A small floating lookup tool (styled like the back-to-top button),
 * available on every page, so a student can check a word without
 * losing their place. Tries to show the definition inline using the
 * free, keyless dictionaryapi.dev API first (including pronunciation
 * audio when the API provides it), falling back to Wiktionary's REST
 * API for words dictionaryapi.dev doesn't index (e.g. demonyms like
 * "Brazilian"). Pronunciation always has a second line of defense too:
 * if every audio clip URL fails to load (dictionaryapi.dev's own media
 * hosting has outages), the browser's built-in speechSynthesis reads
 * the word aloud instead, so the audio button never goes silent. The
 * outbound dictionary links below the result are always shown too, in
 * the same fixed order as the main Dictionary page, as a second way to
 * check the word.
 */
(function () {
  "use strict";

  var trigger = document.querySelector("[data-dict-widget-toggle]");
  if (!trigger) return;
  var panel = document.querySelector("[data-dict-widget-panel]");
  var input = panel.querySelector("[data-dict-widget-input]");
  var resultBox = panel.querySelector("[data-dict-widget-result]");
  var closeBtn = panel.querySelector("[data-dict-widget-close]");
  var linksBox = panel.querySelector("[data-dict-widget-links]");

  /* ---------------------------------------------------------------
   * Attention hint — "Dictionary" appears next to the button on
   * load, then drifts up and fades away letter by letter after a
   * few seconds, just to point out the button exists.
   * --------------------------------------------------------------- */
  function showHint() {
    var word = "Dictionary";
    var hint = document.createElement("div");
    hint.className = "dict-widget-hint";
    hint.setAttribute("aria-hidden", "true");
    word.split("").forEach(function (ch) {
      var span = document.createElement("span");
      span.textContent = ch;
      hint.appendChild(span);
    });
    trigger.insertAdjacentElement("beforebegin", hint);

    setTimeout(function () {
      var spans = hint.querySelectorAll("span");
      spans.forEach(function (span, i) {
        setTimeout(function () {
          span.classList.add("is-leaving");
        }, i * 40);
      });
      setTimeout(function () {
        if (hint.parentNode) hint.parentNode.removeChild(hint);
      }, spans.length * 40 + 500);
    }, 2600);
  }
  showHint();

  // Locks the page behind the widget on small phones while it's open —
  // see the identical helper (and the full explanation) on
  // ai-teacher.js's lockBodyScrollForPanel(). window.__rtPanelLock is a
  // shared counter so the two widgets never unlock a page the other is
  // still holding the lock on.
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

  function toggle(open) {
    var willOpen = open !== undefined ? open : panel.hidden;
    panel.hidden = !willOpen;
    trigger.setAttribute("aria-expanded", String(willOpen));
    if (willOpen) {
      lockBodyScrollForPanel();
      input.focus();
    } else {
      unlockBodyScrollForPanel();
    }
  }

  trigger.addEventListener("click", function (e) {
    e.stopPropagation();
    toggle();
  });
  closeBtn.addEventListener("click", function () { toggle(false); });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !panel.hidden) toggle(false);
  });
  // Only closes on a click that both starts and ends outside the panel.
  // Selecting text inside the input (mouse/finger down inside, dragged
  // past the panel edge before releasing) fires a "click" whose target
  // is wherever the release happened — outside the panel — which used
  // to close it mid-selection; tracking the press separately fixes that.
  var pointerDownOutside = false;
  document.addEventListener("pointerdown", function (e) {
    if (panel.hidden) return;
    pointerDownOutside = !(panel.contains(e.target) || trigger.contains(e.target));
  });
  document.addEventListener("click", function (e) {
    if (panel.hidden) return;
    if (panel.contains(e.target) || trigger.contains(e.target)) return;
    if (!pointerDownOutside) return;
    toggle(false);
  });
  panel.addEventListener("click", function (e) { e.stopPropagation(); });

  function escapeHtml(s) {
    var d = document.createElement("div");
    d.textContent = String(s || "");
    return d.innerHTML;
  }

  function renderOutboundLinks(word) {
    var encoded = encodeURIComponent(word || "hello");
    // Same fixed order as the Dictionary page's core cards.
    var sites = [
      ["Merriam-Webster", "https://www.merriam-webster.com/dictionary/" + encoded],
      ["Cambridge", "https://dictionary.cambridge.org/dictionary/english/" + encoded],
      ["Oxford Learner's", "https://www.oxfordlearnersdictionaries.com/definition/english/" + encoded],
      ["Longman", "https://www.ldoceonline.com/dictionary/" + encoded],
    ];
    linksBox.innerHTML = sites
      .map(function (s) {
        return '<a class="btn btn--ghost btn--small" target="_blank" rel="noopener" href="' + s[1] + '">' + s[0] + "</a>";
      })
      .join("");
  }

  /* ---------------------------------------------------------------
   * Word lookup — tries several capitalization variants in order,
   * since the API is case-sensitive and indexes some words (mostly
   * ordinary vocabulary) lowercase and others (many nationalities,
   * proper nouns) capitalized. Only shows the "ready to look up"
   * fallback after every variant has genuinely failed.
   * --------------------------------------------------------------- */
  function titleCase(s) {
    return s.replace(/\w\S*/g, function (t) {
      return t.charAt(0).toUpperCase() + t.slice(1).toLowerCase();
    });
  }

  function candidateWords(word) {
    var seen = {};
    var out = [];
    [word, word.charAt(0).toUpperCase() + word.slice(1), word.toLowerCase(), titleCase(word)].forEach(function (w) {
      if (w && !seen[w]) {
        seen[w] = true;
        out.push(w);
      }
    });
    return out;
  }

  /* ---------------------------------------------------------------
   * Performance: request timeout + parallel candidates + persistent
   * cache. Previously every lookup fired its capitalization candidates
   * one at a time (up to 4) against dictionaryapi.dev, then up to 4
   * more against Wiktionary, with no timeout at all -- if the first
   * candidate's connection ever stalled (dictionaryapi.dev is a free,
   * best-effort API with no SLA, and its origin does intermittently
   * stop responding after the TLS handshake completes), the browser's
   * own default timeout could leave the widget "Looking up..." for
   * a very long time before ever reaching the working Wiktionary
   * fallback. Two independent fixes:
   *   1. Every fetch gets a hard REQUEST_TIMEOUT_MS ceiling via
   *      AbortController, so a stalled origin fails fast instead of
   *      hanging the whole lookup.
   *   2. A word's candidates are tried in PARALLEL (firstSuccess)
   *      instead of sequentially, so the cost of one bad candidate is
   *      no longer paid serially before trying the next.
   * On top of that, a persistent (localStorage) + in-memory cache
   * means any word looked up before -- successfully or confirmed
   * not-found -- renders instantly with zero network requests, and
   * concurrent lookups for the same in-flight word share one request
   * instead of duplicating it. See lookup() below for the cache path.
   * --------------------------------------------------------------- */
  var REQUEST_TIMEOUT_MS = 5000;
  var CACHE_STORAGE_KEY = "rt_dict_cache_v1";
  var CACHE_MAX_ENTRIES = 500;

  // Object.create(null) rather than {} -- cache keys come from
  // whatever a student types, and a plain object literal treats a key
  // literally named "__proto__" as a request to change the object's
  // prototype instead of an ordinary property, which would corrupt
  // every other cache entry's lookups. A null-prototype object has no
  // such special key and no inherited members to collide with either.
  function blankMap() { return Object.create(null); }

  var memoryCache = blankMap(); // word(lowercase) -> {data:[...]} | {notFound:true}
  var inFlight = blankMap();    // word(lowercase) -> Promise

  (function loadPersistentCache() {
    try {
      var raw = window.localStorage.getItem(CACHE_STORAGE_KEY);
      if (!raw) return;
      var parsed = JSON.parse(raw);
      Object.keys(parsed).forEach(function (k) { memoryCache[k] = parsed[k]; });
    } catch (e) {
      // Corrupt JSON, storage disabled, or a private-browsing quota --
      // an empty in-memory cache is a safe fallback either way.
    }
  })();

  var persistTimer = null;
  function schedulePersist() {
    if (persistTimer) return;
    persistTimer = setTimeout(function () {
      persistTimer = null;
      try {
        var keys = Object.keys(memoryCache);
        if (keys.length > CACHE_MAX_ENTRIES) {
          // Trim oldest-inserted entries first (insertion order is
          // preserved for string keys) rather than let the cache --
          // and the localStorage write on every lookup -- grow forever.
          keys.slice(0, keys.length - CACHE_MAX_ENTRIES).forEach(function (k) { delete memoryCache[k]; });
        }
        window.localStorage.setItem(CACHE_STORAGE_KEY, JSON.stringify(memoryCache));
      } catch (e) {
        // Storage full or unavailable -- the in-memory cache still
        // serves the rest of this page session.
      }
    }, 300);
  }

  function normalizeCacheKey(word) {
    return word.trim().toLowerCase();
  }

  function fetchWithTimeout(url, ms) {
    var hasAbort = typeof AbortController !== "undefined";
    var controller = hasAbort ? new AbortController() : null;
    var timer = hasAbort ? setTimeout(function () { controller.abort(); }, ms) : null;
    return fetch(url, hasAbort ? { signal: controller.signal } : {}).then(
      function (res) { if (timer) clearTimeout(timer); return res; },
      function (err) { if (timer) clearTimeout(timer); throw err; }
    );
  }

  // Fires every candidate's request immediately in parallel (so one
  // candidate's full latency is never paid before the next even starts
  // -- the actual latency fix), but still resolves with the EARLIEST-
  // INDEX candidate that succeeds, never merely whichever happened to
  // respond fastest. candidateWords() orders candidates deliberately
  // (the word exactly as typed first, a capitalized variant after) --
  // e.g. Wiktionary's "oyster" (the mollusk: noun/adjective/verb) and
  // "Oyster" (only a rare surname) are unrelated entries, and racing
  // them by raw response time can surface the wrong one depending on
  // which server answers first. Waiting for index 0 to settle before
  // considering index 1 (while both requests are already in flight)
  // keeps the result deterministic without giving up the parallel
  // dispatch's speed.
  //
  // The rejection this settles with carries .reachedServer = true when
  // at least one candidate got a real (if negative) answer from its
  // server -- e.g. a 404 -- rather than every candidate failing at the
  // network/timeout level. lookup() below uses that to decide whether
  // "not found" is definitive enough to cache, versus a connectivity
  // blip worth retrying fresh next time.
  function firstSuccess(factories) {
    return new Promise(function (resolve, reject) {
      var n = factories.length;
      if (!n) { reject(new Error("no candidates")); return; }
      var results = new Array(n);
      var nextNeeded = 0;
      var settledCount = 0;
      var anyReachedServer = false;

      function tryAdvance() {
        while (nextNeeded < n && results[nextNeeded] !== undefined) {
          var r = results[nextNeeded];
          if (r.ok) { resolve(r.value); return; }
          if (r.err && r.err.reachedServer) anyReachedServer = true;
          nextNeeded += 1;
        }
        if (settledCount === n && nextNeeded === n) {
          var finalErr = new Error("all candidates failed");
          finalErr.reachedServer = anyReachedServer;
          reject(finalErr);
        }
      }

      factories.forEach(function (factory, i) {
        factory().then(
          function (value) { results[i] = { ok: true, value: value }; settledCount += 1; tryAdvance(); },
          function (err) { results[i] = { ok: false, err: err }; settledCount += 1; tryAdvance(); }
        );
      });
    });
  }

  function fetchDefinition(word) {
    return fetchWithTimeout("https://api.dictionaryapi.dev/api/v2/entries/en/" + encodeURIComponent(word), REQUEST_TIMEOUT_MS).then(function (res) {
      if (!res.ok) {
        // A real response from the server (even a 404) is a definitive
        // "this word isn't indexed" answer -- worth caching. A timed-out
        // or network-failed request never reaches here at all (the
        // fetch promise itself rejects instead), so it can't be
        // mistaken for one; see the notFound-caching logic in lookup().
        var err = new Error("not found: " + word);
        err.reachedServer = true;
        throw err;
      }
      return res.json();
    });
  }

  // Try every candidate word in parallel; resolve with the first
  // successful response, or reject once every candidate has failed.
  function tryCandidates(candidates) {
    return firstSuccess(candidates.map(function (c) { return function () { return fetchDefinition(c); }; }));
  }

  /* ---------------------------------------------------------------
   * Wiktionary fallback — dictionaryapi.dev has real gaps in its word
   * list (e.g. demonyms like "Brazilian" return "No Definitions
   * Found" in every capitalization). Wiktionary's REST API is free,
   * keyless and CORS-enabled, so it's tried next, only after every
   * dictionaryapi.dev candidate has failed. Its response shape is
   * normalized into the same {word, phonetic, phonetics, meanings}
   * shape dictionaryapi.dev returns, so renderDefinition() below
   * needs no changes to render either source.
   * --------------------------------------------------------------- */
  function stripHtml(s) {
    return String(s || "")
      .replace(/<[^>]+>/g, "")
      .replace(/\s+/g, " ")
      .trim();
  }

  function normalizeWiktionary(groups, word) {
    return [
      {
        word: word,
        phonetic: "",
        phonetics: [],
        meanings: groups.map(function (g) {
          return {
            partOfSpeech: (g.partOfSpeech || "").toLowerCase(),
            definitions: (g.definitions || []).slice(0, 4).map(function (d) {
              return { definition: stripHtml(d.definition) };
            }),
          };
        }),
      },
    ];
  }

  function fetchWiktionaryDefinition(word) {
    return fetchWithTimeout("https://en.wiktionary.org/api/rest_v1/page/definition/" + encodeURIComponent(word), REQUEST_TIMEOUT_MS)
      .then(function (res) {
        if (!res.ok) {
          var err = new Error("not found: " + word);
          err.reachedServer = true;
          throw err;
        }
        return res.json();
      })
      .then(function (data) {
        // The "en" key groups every entry *written* in English, which
        // also catches Translingual/symbol entries (e.g. "pit" is also
        // the ISO 639-3 code for a language) — keep only entries that
        // are actually about the English word itself.
        var groups = ((data && data.en) || []).filter(function (g) {
          return g.language === "English";
        });
        if (!groups.length) {
          // A real (200) response came back, it just has no English
          // entry -- still a definitive, cacheable "not found", not a
          // network failure.
          var err = new Error("no English entry: " + word);
          err.reachedServer = true;
          throw err;
        }
        return normalizeWiktionary(groups, word);
      });
  }

  // Try every candidate word in parallel; resolve with the first
  // successful response, or reject once every candidate has failed.
  function tryCandidatesWiktionary(candidates) {
    return firstSuccess(candidates.map(function (c) { return function () { return fetchWiktionaryDefinition(c); }; }));
  }

  var lookupTimer;
  var lastQuery = "";

  // Runs the real dictionaryapi.dev -> Wiktionary chain for a word that
  // isn't already cached, sharing one in-flight request across
  // overlapping calls (e.g. the debounced "input" handler firing right
  // as Enter is pressed for the same word) instead of duplicating the
  // network work.
  function lookupNetwork(word, key) {
    if (inFlight[key]) return inFlight[key];

    var promise = tryCandidates(candidateWords(word))
      .catch(function (err1) {
        // dictionaryapi.dev has no entry for this word in any
        // capitalization — try Wiktionary before giving up.
        return tryCandidatesWiktionary(candidateWords(word)).catch(function (err2) {
          var finalErr = new Error("not found anywhere: " + word);
          finalErr.reachedServer = !!(err1 && err1.reachedServer) || !!(err2 && err2.reachedServer);
          throw finalErr;
        });
      })
      .then(
        function (data) {
          memoryCache[key] = { data: data };
          schedulePersist();
          return data;
        },
        function (err) {
          // Only cache "not found" once at least one server actually
          // answered (a real 404 / no entry) — never for a pure
          // connectivity or timeout failure, which deserves a fresh
          // retry next time rather than being poisoned as permanently
          // missing just because the network hiccuped once.
          if (err && err.reachedServer) {
            memoryCache[key] = { notFound: true };
            schedulePersist();
          }
          throw err;
        }
      );

    inFlight[key] = promise.then(
      function (data) { delete inFlight[key]; return data; },
      function (err) { delete inFlight[key]; throw err; }
    );
    return inFlight[key];
  }

  function lookup(word) {
    word = word.trim();
    if (!word) {
      resultBox.innerHTML = '<p class="dict-widget__hint">Type a word and press Enter, or wait a moment after typing.</p>';
      linksBox.innerHTML = "";
      return;
    }
    // A real lookup attempt for a genuinely new word (not a repeat call
    // for the word already in flight, e.g. Enter right after typing
    // finishes) — see docs/gamification.md "sherlock" /
    // "dictionary_power_user" badges.
    if (word !== lastQuery && window.ProgressTracker && typeof window.ProgressTracker.recordDictionaryUse === "function") {
      window.ProgressTracker.recordDictionaryUse();
    }
    renderOutboundLinks(word);
    lastQuery = word;

    // Cache hit (this session, or carried over from localStorage from a
    // previous visit) — render immediately with zero network requests,
    // for a definition or a confirmed "not found" alike.
    var key = normalizeCacheKey(word);
    var cached = memoryCache[key];
    if (cached) {
      if (cached.notFound) {
        resultBox.innerHTML =
          '<p class="dict-widget__hint">Ready to look up &ldquo;' + escapeHtml(word) + '&rdquo;! Pick a dictionary below:</p>';
      } else {
        renderDefinition(cached.data);
      }
      return;
    }

    resultBox.innerHTML = '<p class="dict-widget__hint">Looking up &ldquo;' + escapeHtml(word) + '&rdquo;&hellip;</p>';
    lookupNetwork(word, key)
      .then(function (data) {
        if (lastQuery !== word) return; // a newer query has since started
        renderDefinition(data);
      })
      .catch(function () {
        if (lastQuery !== word) return;
        resultBox.innerHTML =
          '<p class="dict-widget__hint">Ready to look up &ldquo;' + escapeHtml(word) + '&rdquo;! Pick a dictionary below:</p>';
      });
  }

  /* ---------------------------------------------------------------
   * Pronunciation audio — collects every usable audio URL from the
   * entry (not just the first), and if one fails to play, the next
   * one is tried automatically before giving up and showing an
   * error state on the button.
   * --------------------------------------------------------------- */
  function findAudioUrls(entry) {
    var phonetics = entry.phonetics || [];
    var urls = [];
    phonetics.forEach(function (p) {
      var url = p.audio;
      if (url && url.trim()) {
        if (url.indexOf("//") === 0) url = "https:" + url;
        urls.push(url);
      }
    });
    return urls;
  }

  var currentAudio = null;

  // Last-resort pronunciation: the browser's own text-to-speech voice,
  // used when every dictionary-provided audio clip URL has failed (or
  // the entry had none at all — Wiktionary results never do). This is
  // what keeps the audio button working even during a dictionaryapi.dev
  // media-hosting outage, with no backend or paid service involved.
  function speakWord(word, btn) {
    if (!window.speechSynthesis || typeof window.SpeechSynthesisUtterance !== "function") return false;
    try {
      var synth = window.speechSynthesis;
      var utter = new window.SpeechSynthesisUtterance(word);
      utter.lang = "en-US";
      utter.rate = 0.9;
      if (btn) {
        utter.addEventListener("end", function () { btn.classList.remove("is-playing"); });
        utter.addEventListener("error", function () { btn.classList.remove("is-playing"); });
      }
      if (synth.speaking || synth.pending) {
        // Calling cancel() and speak() in the same tick can silently
        // drop the new utterance in some Chrome versions — give the
        // cancel a beat to actually take effect before queuing ours.
        synth.cancel();
        setTimeout(function () { synth.speak(utter); }, 50);
      } else {
        synth.speak(utter);
      }
      return true;
    } catch (e) {
      return false;
    }
  }

  function playAudioUrls(urls, index, btn, word) {
    index = index || 0;
    if (index >= urls.length) {
      btn.classList.remove("has-error");
      btn.removeAttribute("title");
      if (speakWord(word, btn)) {
        btn.classList.add("is-playing");
        return;
      }
      btn.classList.remove("is-playing");
      btn.classList.add("has-error");
      btn.setAttribute("title", "This pronunciation clip didn't load — try a dictionary link below instead.");
      return;
    }
    if (currentAudio) {
      currentAudio.pause();
      currentAudio = null;
    }
    btn.classList.remove("has-error");
    btn.removeAttribute("title");
    var audio = new Audio(urls[index]);
    currentAudio = audio;
    var triedNext = false;
    function tryNext() {
      if (triedNext) return;
      triedNext = true;
      playAudioUrls(urls, index + 1, btn, word);
    }
    audio.addEventListener("ended", function () { btn.classList.remove("is-playing"); });
    audio.addEventListener("error", tryNext);
    btn.classList.add("is-playing");
    var playPromise = audio.play();
    if (playPromise && playPromise.catch) {
      playPromise.catch(tryNext);
    }
  }

  function renderDefinition(data) {
    if (!Array.isArray(data) || !data.length) {
      resultBox.innerHTML = '<p class="dict-widget__hint">No definition found. Try a dictionary below.</p>';
      return;
    }
    var entry = data[0];
    var phonetic = entry.phonetic || (entry.phonetics && entry.phonetics.find(function (p) { return p.text; }) || {}).text || "";
    var audioUrls = findAudioUrls(entry);

    resultBox.innerHTML = "";
    var wordRow = document.createElement("div");
    wordRow.className = "dict-widget__word-row";
    var wordEl = document.createElement("span");
    wordEl.className = "dict-widget__word";
    wordEl.textContent = entry.word;
    wordRow.appendChild(wordEl);
    if (phonetic) {
      var ph = document.createElement("span");
      ph.className = "dict-widget__phonetic";
      ph.textContent = phonetic;
      wordRow.appendChild(ph);
    }
    // Always offered, even when the entry has no audio clip of its own
    // (e.g. every Wiktionary-sourced result) — playAudioUrls() falls
    // back to the browser's speech synthesis in that case.
    var audioBtn = document.createElement("button");
    audioBtn.type = "button";
    audioBtn.className = "dict-widget__audio";
    audioBtn.setAttribute("aria-label", "Play pronunciation");
    audioBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M11 5 6 9H3v6h3l5 4V5Z"/><path d="M15.5 8.5a5 5 0 0 1 0 7"/><path d="M18 6a9 9 0 0 1 0 12"/></svg>';
    audioBtn.addEventListener("click", function () { playAudioUrls(audioUrls, 0, audioBtn, entry.word); });
    wordRow.appendChild(audioBtn);
    resultBox.appendChild(wordRow);

    (entry.meanings || []).slice(0, 3).forEach(function (m) {
      var pos = document.createElement("div");
      pos.className = "dict-widget__pos";
      pos.textContent = m.partOfSpeech;
      resultBox.appendChild(pos);
      var list = document.createElement("ol");
      list.className = "dict-widget__defs";
      (m.definitions || []).slice(0, 2).forEach(function (d) {
        var li = document.createElement("li");
        li.textContent = d.definition;
        if (d.example) {
          var ex = document.createElement("em");
          ex.className = "dict-widget__example";
          ex.innerHTML = "<br>&ldquo;" + escapeHtml(d.example) + "&rdquo;";
          li.appendChild(ex);
        }
        list.appendChild(li);
      });
      resultBox.appendChild(list);
    });
  }

  input.addEventListener("input", function () {
    clearTimeout(lookupTimer);
    lookupTimer = setTimeout(function () {
      lookup(input.value);
    }, 500);
  });
  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
      e.preventDefault();
      clearTimeout(lookupTimer);
      lookup(input.value);
    }
  });
})();
