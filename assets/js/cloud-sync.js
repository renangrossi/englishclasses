/*!
 * Renan the Teacher — Account sync (Supabase + Google or email sign-in)
 * ------------------------------------------------------------------
 * Optional layer on top of progress.js and mastery.js. Those two keep
 * working from localStorage exactly as before; this file copies what
 * they save to the student's own row in Supabase once the student has
 * signed in -- with Google, or with a link/code sent by email -- and
 * brings it back on any other device.
 *
 * Signed out, nothing leaves the browser and the Supabase library is
 * not even downloaded.
 *
 * Setup (one time, see docs/cloud-sync.md): create the Supabase
 * project, run supabase/schema.sql, enable the Google provider (and,
 * for email sign-in, the Email provider plus a custom SMTP sender), then
 * fill in the two constants below. While either is empty this whole
 * file is inert and the site behaves as it did before it existed.
 *
 * Both values are public by design -- the anon key only lets a signed-in
 * student reach their own row (row level security in schema.sql). The
 * service_role key must never be put here.
 *
 * Public API (window.CloudSync):
 *   enabled        // true once the two constants are filled in
 *   isSignedIn()
 *   signIn()       // redirects to Google and back to the same page
 *   sendEmailLink(email)   // emails a sign-in link + code
 *   verifyEmailCode(code)  // signs in with the code from that email
 *   signOut()
 *   render()       // (re)draws every [data-cloud-account] element
 * ------------------------------------------------------------------ */
(function () {
  "use strict";

  var SUPABASE_URL = "https://ustsqrbceviabupvaaip.supabase.co";      // e.g. "https://abcdefghijklmnop.supabase.co"
  var SUPABASE_ANON_KEY = "sb_publishable_44AffZ_J0Z2kwbmFgvea_w_rsMibqFF"; // Project Settings -> API -> anon / publishable key

  var SDK_URL = "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.45.4/dist/umd/supabase.min.js";
  var TABLE = "student_progress";
  var AUTH_STORAGE_KEY = "rt_auth";   // where supabase-js keeps the session
  var META_KEY = "rt_sync_meta";      // { userId, epoch, pendingReset }
  var MASTERY_STORAGE_KEY = "rt_mastery";
  var PENDING_EMAIL_KEY = "rt_email_pending"; // { email, at } while a code is awaited
  var EMAIL_CODE_TTL_MS = 60 * 60 * 1000;     // Supabase's default OTP lifetime
  var UPLOAD_DELAY_MS = 1500;         // quiet time after a save before uploading

  var enabled = !!(SUPABASE_URL && SUPABASE_ANON_KEY);

  // The site's root, worked out from this script's own address
  // (".../assets/js/cloud-sync.js"), so links work at any page depth.
  var SITE_ROOT = (function () {
    var me = document.currentScript && document.currentScript.src;
    return me ? me.replace(/assets\/js\/cloud-sync\.js.*$/, "") : "";
  })();

  var clientPromise = null;
  var user = null;
  var status = "idle";   // idle | signing-in | syncing | synced | error
  var syncing = false;
  var syncAgain = false;
  var currentSync = null; // the round trip in flight, if any
  var applying = false;  // true while we write the account's copy locally
  var uploadTimer = null;
  var watching = false;  // onAuthStateChange registered
  // Email sign-in form state. Kept here, not in the DOM, because render()
  // redraws the form (the panel and progress.html can both show it).
  var emailDraft = "";
  var codeDraft = "";
  var emailBusy = false;
  var emailError = "";
  var focusRequest = null; // { slot, selector } to focus after the next render

  /* ---------------- small helpers ---------------- */

  function readJson(key) {
    try { return JSON.parse(window.localStorage.getItem(key) || "null"); } catch (e) { return null; }
  }
  function writeJson(key, value) {
    try { window.localStorage.setItem(key, JSON.stringify(value)); } catch (e) { /* ignore */ }
  }
  function loadMeta() {
    return readJson(META_KEY) || { userId: null, epoch: 0, pendingReset: false };
  }

  // Postgres returns jsonb with its keys reordered, so two equal states
  // only compare equal once their keys are written in one fixed order.
  function stable(value) {
    if (Array.isArray(value)) return "[" + value.map(stable).join(",") + "]";
    if (value && typeof value === "object") {
      return "{" + Object.keys(value).sort().map(function (k) {
        return JSON.stringify(k) + ":" + stable(value[k]);
      }).join(",") + "}";
    }
    return JSON.stringify(value === undefined ? null : value);
  }

  function loadPendingEmail() {
    var p = readJson(PENDING_EMAIL_KEY);
    if (!p || !p.email || !(Date.now() - (p.at || 0) < EMAIL_CODE_TTL_MS)) return null;
    return p;
  }
  function savePendingEmail(email) { writeJson(PENDING_EMAIL_KEY, { email: email, at: Date.now() }); }
  function clearPendingEmail() {
    try { window.localStorage.removeItem(PENDING_EMAIL_KEY); } catch (e) { /* ignore */ }
  }

  function warn(err) {
    if (window.console) console.warn("[cloud-sync]", err && err.message ? err.message : err);
  }

  // The page the student is on, so every sign-in route brings them back here.
  function herePage() {
    return window.location.origin + window.location.pathname;
  }

  function hasStoredSession() {
    try { return !!window.localStorage.getItem(AUTH_STORAGE_KEY); } catch (e) { return false; }
  }

  // True on the page load that Google/Supabase has just redirected back to.
  function isAuthCallback() {
    var loc = window.location;
    return /[?&](code|error_description)=/.test(loc.search) || /access_token=|error_description=/.test(loc.hash);
  }

  function loadSdk() {
    if (window.supabase && window.supabase.createClient) return Promise.resolve();
    return new Promise(function (resolve, reject) {
      var s = document.createElement("script");
      s.src = SDK_URL;
      s.async = true;
      s.onload = function () { resolve(); };
      s.onerror = function () { reject(new Error("Could not load the sign-in library")); };
      document.head.appendChild(s);
    });
  }

  function getClient() {
    if (!clientPromise) {
      clientPromise = loadSdk().then(function () {
        return window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
          auth: {
            storageKey: AUTH_STORAGE_KEY,
            flowType: "pkce",
            persistSession: true,
            autoRefreshToken: true,
            detectSessionInUrl: true,
          },
        });
      });
      // A failed download must not be remembered, or one offline moment
      // would disable sign-in until the next page load.
      clientPromise.catch(function () { clientPromise = null; });
    }
    return clientPromise;
  }

  /* ---------------- sync ---------------- */

  function localMastery() {
    return window.MasteryTracker ? window.MasteryTracker.getState() : null;
  }

  // mastery.js is not on every page. Where it is missing, a merge of the
  // review data simply waits for a page that has it; a full replacement
  // cannot wait (it would leave another student's data behind), so it is
  // written straight to storage.
  function applyMastery(remote, replace) {
    if (window.MasteryTracker) return window.MasteryTracker.importState(remote, replace);
    if (replace) {
      if (remote && remote.items) writeJson(MASTERY_STORAGE_KEY, remote);
      else { try { window.localStorage.removeItem(MASTERY_STORAGE_KEY); } catch (e) { /* ignore */ } }
    }
    return null;
  }

  function setStatus(next) {
    status = next;
    render();
  }

  // One round trip: read the account's row, reconcile it with this
  // browser, upload the result if the account does not already have it.
  // Resolves true when the account is known to be up to date.
  function sync() {
    if (!enabled || !user || !window.ProgressTracker) return Promise.resolve(false);
    // Already talking to the server: run once more when that finishes,
    // and hand the caller the same promise so it learns the final result.
    if (syncing) { syncAgain = true; return currentSync; }
    syncing = true;
    clearTimeout(uploadTimer);
    uploadTimer = null;
    setStatus("syncing");

    var uid = user.id;
    var client;
    currentSync = getClient().then(function (c) {
      client = c;
      return client.from(TABLE).select("progress, mastery, epoch").eq("user_id", uid).maybeSingle();
    }).then(function (res) {
      if (res.error) throw res.error;
      var row = res.data;
      var meta = loadMeta();
      var sameUser = meta.userId === uid;
      var anonymous = !meta.userId; // progress made before anyone signed in here
      var epoch = row ? row.epoch || 0 : 0;
      var progress, mastery;

      if (sameUser && meta.pendingReset) {
        // "Reset my progress" was pressed here: the emptied local state
        // wins, and the higher epoch tells the other devices to drop theirs.
        epoch += 1;
        progress = window.ProgressTracker.getState();
        mastery = localMastery();
      } else {
        // Take the account's copy as it is when this browser holds another
        // student's progress, or when a reset happened on another device.
        // Otherwise merge, so nothing done offline or before signing in is lost.
        var replace = (!anonymous && !sameUser) || (sameUser && epoch > (meta.epoch || 0));
        applying = true;
        try {
          if (row || replace) {
            progress = window.ProgressTracker.importState(row ? row.progress : null, replace);
            mastery = applyMastery(row ? row.mastery : null, replace);
          } else {
            progress = window.ProgressTracker.getState();
            mastery = localMastery();
          }
        } finally {
          applying = false;
        }
      }

      writeJson(META_KEY, { userId: uid, epoch: epoch, pendingReset: false });

      var upToDate = row && (row.epoch || 0) === epoch &&
        stable(row.progress) === stable(progress) &&
        (!mastery || stable(row.mastery) === stable(mastery));
      if (upToDate) return true;

      var payload = { user_id: uid, progress: progress, epoch: epoch };
      if (mastery) payload.mastery = mastery; // left out, the column keeps its value
      return client.from(TABLE).upsert(payload, { onConflict: "user_id" }).then(function (up) {
        if (up.error) throw up.error;
        return true;
      });
    }).then(function () {
      syncing = false;
      setStatus("synced");
      if (syncAgain) { syncAgain = false; return sync(); }
      return true;
    }).catch(function (err) {
      syncing = false;
      syncAgain = false;
      if (window.console) console.warn("[cloud-sync]", err && err.message ? err.message : err);
      setStatus("error");
      return false;
    });
    return currentSync;
  }

  function scheduleUpload() {
    if (!user || applying) return;
    clearTimeout(uploadTimer);
    uploadTimer = setTimeout(sync, UPLOAD_DELAY_MS);
  }

  /* ---------------- auth ---------------- */

  function signIn() {
    if (!enabled) return Promise.resolve();
    setStatus("signing-in");
    return getClient().then(function (client) {
      // Come back to the page the student was on.
      return client.auth.signInWithOAuth({ provider: "google", options: { redirectTo: herePage() } });
    }).then(function (res) {
      if (res && res.error) throw res.error;
    }).catch(function (err) {
      if (window.console) console.warn("[cloud-sync]", err && err.message ? err.message : err);
      setStatus("error");
    });
  }

  /* Email sign-in. One email carries both a link and a code: the link
     signs in when it is opened in this same browser (PKCE keeps a secret
     here); the code works anywhere, e.g. email read on the phone while
     the course is open on a computer. */

  function sendErrorText(err) {
    var msg = (err && err.message) || "";
    if ((err && err.status === 429) || /rate limit|security purposes|seconds/i.test(msg)) {
      return "Too many emails just now. Please wait a minute and try again.";
    }
    if (/not authorized|signups not allowed|provider is not enabled|disabled/i.test(msg)) {
      return "Email sign-in is not available right now. Please sign in with Google.";
    }
    return "The email could not be sent. Check the address and try again.";
  }

  function sendEmailLink(address, slot) {
    if (!enabled || emailBusy) return Promise.resolve(false);
    var email = String(address || "").trim();
    emailDraft = email;
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      emailError = "Please type your full email address, like name@gmail.com.";
      focusRequest = { slot: slot, selector: ".cloud-account__input" };
      render();
      return Promise.resolve(false);
    }
    emailBusy = true;
    emailError = "";
    render();
    var client;
    return getClient().then(function (c) {
      client = c;
      return client.auth.signInWithOtp({
        email: email,
        options: { emailRedirectTo: herePage(), shouldCreateUser: true },
      });
    }).then(function (res) {
      if (res && res.error) throw res.error;
      emailBusy = false;
      codeDraft = "";
      savePendingEmail(email);
      // If the link is opened in another tab of this browser, supabase-js
      // tells this tab too, and the form here turns into "Signed in as".
      watchAuth(client);
      focusRequest = { slot: slot, selector: ".cloud-account__code" };
      render();
      return true;
    }).catch(function (err) {
      emailBusy = false;
      warn(err);
      emailError = sendErrorText(err);
      focusRequest = { slot: slot, selector: ".cloud-account__input" };
      render();
      return false;
    });
  }

  function verifyEmailCode(code, slot) {
    if (!enabled || emailBusy) return Promise.resolve(false);
    var pending = loadPendingEmail();
    if (!pending) { emailError = ""; render(); return Promise.resolve(false); }
    var token = String(code || "").replace(/\s+/g, "");
    codeDraft = token;
    if (!/^[0-9]{6,10}$/.test(token)) {
      emailError = "Type the number from the email (6 digits).";
      focusRequest = { slot: slot, selector: ".cloud-account__code" };
      render();
      return Promise.resolve(false);
    }
    emailBusy = true;
    emailError = "";
    render();
    return getClient().then(function (client) {
      return client.auth.verifyOtp({ email: pending.email, token: token, type: "email" }).then(function (res) {
        if (res && res.error) throw res.error;
        emailBusy = false;
        watchAuth(client);
        onSession(res && res.data ? res.data.session : null, true);
        return !!user;
      });
    }).catch(function (err) {
      emailBusy = false;
      warn(err);
      emailError = /expired|invalid|not found/i.test((err && err.message) || "")
        ? "That code is wrong or has expired. Use the newest email, or send a new one."
        : "That did not work. Please try again.";
      focusRequest = { slot: slot, selector: ".cloud-account__code" };
      render();
      return false;
    });
  }

  function cancelEmail() {
    clearPendingEmail();
    emailError = "";
    codeDraft = "";
    render();
  }

  function signOut() {
    if (!user) return Promise.resolve();
    return sync().then(function (saved) {
      if (!saved && !window.confirm(
        "Your latest progress could not be saved to your account (are you offline?).\n\n" +
        "Sign out anyway? It will stay on this device and be saved the next time you sign in here.")) {
        return;
      }
      return getClient().then(function (client) {
        return client.auth.signOut({ scope: "local" });
      }).then(function () {
        user = null;
        if (saved) {
          // Everything is in the account, so this browser goes back to
          // empty -- the next person to use it does not inherit it.
          applying = true;
          try {
            window.ProgressTracker.importState(null, true);
            applyMastery(null, true);
          } finally {
            applying = false;
          }
          try { window.localStorage.removeItem(META_KEY); } catch (e) { /* ignore */ }
        }
        setStatus("idle");
      });
    });
  }

  // After a sign-in the student just made (back from Google, an email
  // link, or a typed code) -- not a session restored on a normal page
  // load -- take them to Today's Review once their progress is merged.
  function goToReview() {
    var target = SITE_ROOT + "today-review.html";
    if (/\/today-review\.html$/.test(window.location.pathname)) return;
    window.location.assign(target);
  }

  function onSession(session, fresh) {
    var next = session && session.user ? session.user : null;
    var changed = (next && next.id) !== (user && user.id);
    user = next;
    if (!user) { setStatus("idle"); return; }
    clearPendingEmail();
    emailError = "";
    emailDraft = "";
    codeDraft = "";
    if (changed && fresh) sync().then(goToReview, goToReview);
    else if (changed) sync();
    else render();
  }

  // Supabase leaves ?code=... (or an error) in the address after the
  // redirect back; remove it so a reload or a shared link is clean.
  function cleanCallbackUrl() {
    if (!isAuthCallback() || !window.history || !window.history.replaceState) return;
    var url = new URL(window.location.href);
    ["code", "error", "error_code", "error_description"].forEach(function (k) { url.searchParams.delete(k); });
    if (/access_token=|error_description=/.test(url.hash)) url.hash = "";
    window.history.replaceState(null, "", url.pathname + url.search + url.hash);
  }

  // Pages can word things two ways: [data-offline-only] is what ships
  // in the HTML, [data-cloud-only] replaces it once sync is configured.
  function showCloudCopy() {
    Array.prototype.forEach.call(document.querySelectorAll("[data-offline-only]"), function (n) { n.hidden = true; });
    Array.prototype.forEach.call(document.querySelectorAll("[data-cloud-only]"), function (n) { n.hidden = false; });
  }

  function watchAuth(client) {
    if (watching) return;
    watching = true;
    client.auth.onAuthStateChange(function (event, session) {
      // Token refreshes arrive here too; only a change of user matters.
      // Deferred: supabase-js must not be called back into from here.
      if (event === "SIGNED_OUT" || event === "SIGNED_IN") {
        setTimeout(function () { onSession(session); }, 0);
      }
    });
  }

  /* ---------------- "Log in" welcome overlay ----------------
   * Signed out, once per browser session: dim the page, ring the LOG IN
   * pill (or the menu button on phones, where the pill lives inside the
   * menu), and say why to log in. It closes by itself after a short
   * countdown -- paused while the pointer or focus is on the card -- or
   * on "Not now", Escape, or a click outside. "Log in" opens the
   * progress panel, where the sign-in buttons are.
   * ---------------------------------------------------------------- */
  var NUDGE_KEY = "rt_login_nudge_shown";   // sessionStorage: once per browser session
  var NUDGE_SECONDS = 5;
  var STAR_PATH = "M12 17.27 18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21Z";

  function star(cls, style) {
    return '<svg class="' + cls + '" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"' +
      (style ? ' style="' + style + '"' : "") + '><path d="' + STAR_PATH + '"/></svg>';
  }

  function visibleRect(node) {
    if (!node || node.hidden) return null;
    var r = node.getBoundingClientRect();
    return r.width > 0 && r.height > 0 ? r : null;
  }

  // What to point at, and what "Log in" should click.
  function nudgeTarget() {
    var pill = document.querySelector(".progress-toggle--pill");
    if (visibleRect(pill)) return { el: pill, opener: pill, round: true, phone: false };
    var burger = document.querySelector("[data-nav-toggle]");
    var row = document.querySelector(".progress-menu-toggle");
    if (visibleRect(burger)) return { el: burger, opener: row || burger, round: false, phone: true };
    return { el: null, opener: pill || row, round: false, phone: false };
  }

  function maybeShowLoginNudge() {
    if (!enabled || user || hasStoredSession() || isAuthCallback() || loadPendingEmail()) return;
    if (/\/privacy\.html$/.test(window.location.pathname)) return;
    try {
      if (window.sessionStorage.getItem(NUDGE_KEY)) return;
      window.sessionStorage.setItem(NUDGE_KEY, "1");
    } catch (e) {
      return; // no session storage: it could not stay at once per session
    }
    // Let the header (and the pill progress.js builds) settle first.
    setTimeout(showLoginNudge, 500);
  }

  function showLoginNudge() {
    if (user || hasStoredSession() || document.querySelector(".login-nudge")) return;
    var target = nudgeTarget();
    var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var before = document.activeElement;

    var root = document.createElement("div");
    root.className = "login-nudge" + (target.el ? "" : " login-nudge--plain") + (reduce ? " login-nudge--still" : "");
    root.setAttribute("role", "dialog");
    root.setAttribute("aria-modal", "false");
    root.setAttribute("aria-labelledby", "login-nudge-title");
    root.setAttribute("aria-describedby", "login-nudge-text");

    // Scattered twinkling stars across the dimmed page.
    var sky = "";
    var spots = [[8, 22], [17, 70], [26, 40], [35, 88], [44, 12], [58, 64], [66, 30], [74, 82], [83, 18], [90, 52], [12, 48], [52, 92]];
    spots.forEach(function (xy, i) {
      sky += star("login-nudge__sky-star", "top:" + xy[0] + "%;left:" + xy[1] + "%;--d:" + (i % 5) * 0.45 + "s;--s:" + (10 + (i % 4) * 4) + "px");
    });

    var where = target.phone
      ? "Open the menu <b>☰</b>, then <b>Progress</b>, to log in any time."
      : "The <b>LOG IN</b> button is up here, at the top of every page.";
    root.innerHTML =
      '<div class="login-nudge__sky" aria-hidden="true">' + sky + "</div>" +
      (target.el ? '<div class="login-nudge__spot' + (target.round ? " login-nudge__spot--round" : "") + '" aria-hidden="true"></div>' : "") +
      '<div class="login-nudge__card" tabindex="-1">' +
        '<div class="login-nudge__stars" aria-hidden="true">' + star("") + star("") + star("") + star("") + star("") + "</div>" +
        '<p class="login-nudge__eyebrow">Save your progress</p>' +
        '<h2 class="login-nudge__title" id="login-nudge-title">Log in and never lose a star</h2>' +
        '<p class="login-nudge__text" id="login-nudge-text">Your XP, streak, badges and reviews are kept in your account, so you can pick up on any phone or computer. ' + where + "</p>" +
        '<div class="login-nudge__actions">' +
          '<button type="button" class="btn btn--accent" data-nudge-login>Log in</button>' +
          '<button type="button" class="btn btn--ghost-inverse" data-nudge-close>Not now</button>' +
        "</div>" +
        '<div class="login-nudge__timer"><span class="login-nudge__bar"><span></span></span>' +
          '<span class="login-nudge__count">Closing in <b>' + NUDGE_SECONDS + "</b>s</span></div>" +
      "</div>";
    document.body.appendChild(root);

    var card = root.querySelector(".login-nudge__card");
    var spot = root.querySelector(".login-nudge__spot");
    var bar = root.querySelector(".login-nudge__bar span");
    var count = root.querySelector(".login-nudge__count b");

    function place() {
      var r = target.el && visibleRect(target.el);
      var vw = window.innerWidth, gutter = 16;
      var cardW = Math.min(380, vw - 2 * gutter);
      card.style.width = cardW + "px";
      if (!r || !spot) {
        card.style.left = Math.round((vw - cardW) / 2) + "px";
        card.style.top = "18vh";
        return;
      }
      var pad = 6;
      spot.style.left = r.left - pad + "px";
      spot.style.top = r.top - pad + "px";
      spot.style.width = r.width + 2 * pad + "px";
      spot.style.height = r.height + 2 * pad + "px";
      var centerX = r.left + r.width / 2;
      var left = Math.min(Math.max(gutter, centerX - cardW + 40), vw - cardW - gutter);
      card.style.left = Math.round(left) + "px";
      card.style.top = Math.round(r.bottom + pad + 18) + "px";
      card.style.setProperty("--arrow-x", Math.round(Math.min(Math.max(centerX - left, 24), cardW - 24)) + "px");
    }
    place();
    window.addEventListener("resize", place);

    // Countdown, paused while the student is reading or using the card.
    var total = NUDGE_SECONDS * 1000, left = total, paused = false, last = Date.now();
    var timer = setInterval(function () {
      var now = Date.now();
      if (!paused) left -= now - last;
      last = now;
      if (left <= 0) { close(); return; }
      bar.style.width = (left / total) * 100 + "%";
      count.textContent = String(Math.ceil(left / 1000));
    }, 100);
    function pause() { paused = true; root.classList.add("is-paused"); }
    function resume() {
      if (card.matches(":hover") || card.contains(document.activeElement)) return;
      paused = false; root.classList.remove("is-paused");
    }
    card.addEventListener("mouseenter", pause);
    card.addEventListener("mouseleave", resume);
    card.addEventListener("focusin", pause);
    card.addEventListener("focusout", function () { setTimeout(resume, 0); });

    var closed = false;
    function close(thenOpen) {
      if (closed) return;
      closed = true;
      clearInterval(timer);
      window.removeEventListener("resize", place);
      document.removeEventListener("keydown", onKey, true);
      root.classList.add("is-leaving");
      setTimeout(function () { if (root.parentNode) root.parentNode.removeChild(root); }, reduce ? 0 : 250);
      if (thenOpen && target.opener) {
        target.opener.click();
      } else if (before && before.focus && document.contains(before)) {
        try { before.focus({ preventScroll: true }); } catch (e) { /* ignore */ }
      }
    }
    function onKey(e) { if (e.key === "Escape") { e.preventDefault(); close(); } }
    document.addEventListener("keydown", onKey, true);

    root.addEventListener("click", function (e) {
      if (e.target.closest("[data-nudge-login]")) { close(true); return; }
      if (e.target.closest("[data-nudge-close]")) { close(); return; }
      if (card.contains(e.target)) return;
      // A click on the ringed button itself counts as "Log in".
      var r = target.el && visibleRect(target.el);
      var onTarget = r && e.clientX >= r.left && e.clientX <= r.right && e.clientY >= r.top && e.clientY <= r.bottom;
      close(onTarget);
    });

    // Focus the card itself (not the button), so the countdown keeps
    // running until the student actually engages with it.
    setTimeout(function () {
      if (closed) return;
      try { card.focus({ preventScroll: true }); } catch (e) { /* ignore */ }
      paused = false; root.classList.remove("is-paused");
    }, 0);
  }

  function boot() {
    showCloudCopy();
    render();
    if (!hasStoredSession() && !isAuthCallback()) { maybeShowLoginNudge(); return; } // signed out: stay offline
    // Back from Google or an email link but no session: the link expired,
    // was already used, or was opened in another browser than the one
    // that asked for it.
    var returning = isAuthCallback();
    getClient().then(function (client) {
      return client.auth.getSession().then(function (res) {
        cleanCallbackUrl();
        onSession(res && res.data ? res.data.session : null, returning);
        if (returning && !user) setStatus("error");
        watchAuth(client);
      });
    }).catch(function (err) {
      if (window.console) console.warn("[cloud-sync]", err && err.message ? err.message : err);
      setStatus(hasStoredSession() ? "error" : "idle");
    });
  }

  /* ---------------- UI ---------------- */

  var GOOGLE_ICON =
    '<svg class="cloud-account__g" viewBox="0 0 48 48" aria-hidden="true">' +
    '<path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>' +
    '<path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>' +
    '<path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>' +
    '<path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>' +
    "</svg>";

  var STATUS_TEXT = {
    syncing: "Saving…",
    synced: "Saved to your account",
    error: "Not saved yet — will try again",
    idle: "",
  };

  function render() {
    if (!enabled) return;
    // Lets the header pill (progress.js) switch between "LOG IN" and
    // the XP display whenever the account state may have changed.
    try { document.dispatchEvent(new CustomEvent("rt:account")); } catch (e) { /* old browser */ }
    var slots = document.querySelectorAll("[data-cloud-account]");
    Array.prototype.forEach.call(slots, function (slot, i) {
      slot.textContent = "";
      slot.classList.add("cloud-account");

      if (!user) {
        renderSignedOut(slot, i);
        return;
      }

      var who = document.createElement("p");
      who.className = "cloud-account__text";
      who.appendChild(document.createTextNode("Signed in as "));
      var strong = document.createElement("strong");
      strong.textContent = user.email || "your account";
      who.appendChild(strong);

      var row = document.createElement("p");
      row.className = "cloud-account__row";
      var state = document.createElement("span");
      state.className = "cloud-account__status cloud-account__status--" + status;
      state.setAttribute("role", "status");
      state.textContent = STATUS_TEXT[status] || "";
      var out = document.createElement("button");
      out.type = "button";
      out.className = "cloud-account__signout";
      out.textContent = "Sign out";
      out.addEventListener("click", signOut);
      row.appendChild(state);
      row.appendChild(out);

      slot.appendChild(who);
      slot.appendChild(row);
    });
    if (focusRequest) {
      var req = focusRequest;
      focusRequest = null;
      var target = req.slot && req.slot.querySelector ? req.slot.querySelector(req.selector) : null;
      if (target && target.focus) target.focus();
    }
  }

  function el(tag, className, text) {
    var n = document.createElement(tag);
    if (className) n.className = className;
    if (text) n.textContent = text;
    return n;
  }

  function errorLine() {
    var e = el("p", "cloud-account__status cloud-account__status--error cloud-account__msg", emailError);
    e.setAttribute("role", "alert");
    return e;
  }

  // Signed out: Google button, then "or" an email address. Once an email
  // has gone out, the same spot asks for the code from it instead.
  function renderSignedOut(slot, i) {
    var waiting = status === "signing-in" || (status === "idle" && hasStoredSession() && !!clientPromise);
    var pending = loadPendingEmail();

    if (pending) {
      var sent = el("p", "cloud-account__text");
      sent.appendChild(document.createTextNode("We sent a sign-in link to "));
      var to = el("strong", "", pending.email);
      sent.appendChild(to);
      sent.appendChild(document.createTextNode(
        ". Open it on this device, or type the code from the email here. Not there? Check your spam folder."));
      slot.appendChild(sent);

      var codeForm = el("form", "cloud-account__email");
      codeForm.noValidate = true;
      var codeLabel = el("label", "cloud-account__label", "Code from the email");
      codeLabel.htmlFor = "cloud-code-" + i;
      var codeRow = el("div", "cloud-account__field");
      var code = el("input", "cloud-account__input cloud-account__code");
      code.id = "cloud-code-" + i;
      code.type = "text";
      code.name = "code";
      code.inputMode = "numeric";
      code.autocomplete = "one-time-code";
      code.maxLength = 12;
      code.placeholder = "123456";
      code.value = codeDraft;
      code.disabled = emailBusy;
      code.addEventListener("input", function () { codeDraft = code.value; });
      var go = el("button", "cloud-account__send", emailBusy ? "Checking…" : "Sign in");
      go.type = "submit";
      go.disabled = emailBusy;
      codeForm.addEventListener("submit", function (e) {
        e.preventDefault();
        verifyEmailCode(code.value, slot);
      });
      codeRow.appendChild(code);
      codeRow.appendChild(go);
      codeForm.appendChild(codeLabel);
      codeForm.appendChild(codeRow);
      slot.appendChild(codeForm);
      if (emailError) slot.appendChild(errorLine());

      var links = el("p", "cloud-account__row cloud-account__links");
      var again = el("button", "cloud-account__signout", "Send a new email");
      again.type = "button";
      again.disabled = emailBusy;
      again.addEventListener("click", function () { sendEmailLink(pending.email, slot); });
      var other = el("button", "cloud-account__signout", "Use another email or Google");
      other.type = "button";
      other.disabled = emailBusy;
      other.addEventListener("click", function () {
        emailDraft = pending.email;
        focusRequest = { slot: slot, selector: ".cloud-account__input" };
        cancelEmail();
      });
      links.appendChild(again);
      links.appendChild(other);
      slot.appendChild(links);
    } else {
      var p = el("p", "cloud-account__text", status === "error"
        ? "Sign-in did not work. Please try again. An email link only works in the browser where you asked for it; anywhere else, type the code from the email."
        : "Sign in to save your progress and pick it up on any phone or computer.");
      slot.appendChild(p);

      var btn = el("button", "cloud-account__google");
      btn.type = "button";
      btn.innerHTML = GOOGLE_ICON + "<span>Sign in with Google</span>";
      btn.disabled = waiting || emailBusy;
      btn.addEventListener("click", signIn);
      slot.appendChild(btn);

      slot.appendChild(el("p", "cloud-account__or", "or"));

      var form = el("form", "cloud-account__email");
      form.noValidate = true;
      var label = el("label", "cloud-account__label", "Get a sign-in link by email");
      label.htmlFor = "cloud-email-" + i;
      var fieldRow = el("div", "cloud-account__field");
      var input = el("input", "cloud-account__input");
      input.id = "cloud-email-" + i;
      input.type = "email";
      input.name = "email";
      input.autocomplete = "email";
      input.inputMode = "email";
      input.placeholder = "you@example.com";
      input.value = emailDraft;
      input.disabled = emailBusy || waiting;
      input.addEventListener("input", function () { emailDraft = input.value; });
      var send = el("button", "cloud-account__send", emailBusy ? "Sending…" : "Send link");
      send.type = "submit";
      send.disabled = emailBusy || waiting;
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        sendEmailLink(input.value, slot);
      });
      fieldRow.appendChild(input);
      fieldRow.appendChild(send);
      form.appendChild(label);
      form.appendChild(fieldRow);
      slot.appendChild(form);
      if (emailError) slot.appendChild(errorLine());
    }

    var privacy = el("a", "cloud-account__privacy", "What is stored, and how to delete it");
    privacy.href = SITE_ROOT + "privacy.html";
    slot.appendChild(privacy);
  }

  /* ---------------- wiring ---------------- */

  window.CloudSync = {
    enabled: enabled,
    isSignedIn: function () { return !!user; },
    // Signed in, or a stored session that has not been checked yet
    // (signed out, the library is never downloaded). Used on first
    // render so the header pill does not flash the wrong label. Back
    // from Google (?code=... still in the address) also counts until
    // boot() has exchanged the code and cleaned the address.
    hasSession: function () { return !!user || hasStoredSession() || isAuthCallback(); },
    signIn: signIn,
    sendEmailLink: function (email) { return sendEmailLink(email, null); },
    verifyEmailCode: function (code) { return verifyEmailCode(code, null); },
    signOut: signOut,
    render: render,
  };

  if (!enabled) return;

  document.addEventListener("rt:saved", scheduleUpload);

  document.addEventListener("rt:reset", function () {
    if (!user) return;
    var meta = loadMeta();
    meta.userId = user.id;
    meta.pendingReset = true; // survives a reload if the upload does not get out
    writeJson(META_KEY, meta);
    sync();
  });

  // Leaving the page with an upload still waiting: send it now. If it
  // does not get out, the next page load syncs anyway -- the data is
  // still in localStorage.
  document.addEventListener("visibilitychange", function () {
    if (document.visibilityState === "hidden" && uploadTimer) sync();
  });

  // Back online after a failed upload.
  window.addEventListener("online", function () {
    if (user && status === "error") sync();
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
