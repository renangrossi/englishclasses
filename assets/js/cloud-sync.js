/*!
 * Renan the Teacher — Account sync (Supabase + Google sign-in)
 * ------------------------------------------------------------------
 * Optional layer on top of progress.js and mastery.js. Those two keep
 * working from localStorage exactly as before; this file copies what
 * they save to the student's own row in Supabase once the student has
 * signed in with Google, and brings it back on any other device.
 *
 * Signed out, nothing leaves the browser and the Supabase library is
 * not even downloaded.
 *
 * Setup (one time, see docs/cloud-sync.md): create the Supabase
 * project, run supabase/schema.sql, enable the Google provider, then
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
      var here = window.location.origin + window.location.pathname;
      return client.auth.signInWithOAuth({ provider: "google", options: { redirectTo: here } });
    }).then(function (res) {
      if (res && res.error) throw res.error;
    }).catch(function (err) {
      if (window.console) console.warn("[cloud-sync]", err && err.message ? err.message : err);
      setStatus("error");
    });
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

  function onSession(session) {
    var next = session && session.user ? session.user : null;
    var changed = (next && next.id) !== (user && user.id);
    user = next;
    if (!user) { setStatus("idle"); return; }
    if (changed) sync(); else render();
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

  function boot() {
    showCloudCopy();
    render();
    if (!hasStoredSession() && !isAuthCallback()) return; // signed out: stay offline
    var failed = /error_description=/.test(window.location.search + window.location.hash);
    getClient().then(function (client) {
      return client.auth.getSession().then(function (res) {
        cleanCallbackUrl();
        onSession(res && res.data ? res.data.session : null);
        if (failed && !user) setStatus("error");
        client.auth.onAuthStateChange(function (event, session) {
          // Token refreshes arrive here too; only a change of user matters.
          // Deferred: supabase-js must not be called back into from here.
          if (event === "SIGNED_OUT" || event === "SIGNED_IN") {
            setTimeout(function () { onSession(session); }, 0);
          }
        });
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
    var slots = document.querySelectorAll("[data-cloud-account]");
    Array.prototype.forEach.call(slots, function (slot) {
      slot.textContent = "";
      slot.classList.add("cloud-account");

      if (!user) {
        var waiting = status === "signing-in" || (status === "idle" && hasStoredSession() && !!clientPromise);
        var p = document.createElement("p");
        p.className = "cloud-account__text";
        p.textContent = status === "error"
          ? "Sign-in did not work. Please try again."
          : "Sign in to save your progress and pick it up on any phone or computer.";
        var btn = document.createElement("button");
        btn.type = "button";
        btn.className = "cloud-account__google";
        btn.innerHTML = GOOGLE_ICON + "<span>Sign in with Google</span>";
        btn.disabled = waiting;
        btn.addEventListener("click", signIn);
        var privacy = document.createElement("a");
        privacy.className = "cloud-account__privacy";
        privacy.href = SITE_ROOT + "privacy.html";
        privacy.textContent = "What is stored, and how to delete it";
        slot.appendChild(p);
        slot.appendChild(btn);
        slot.appendChild(privacy);
        return;
      }

      var who = document.createElement("p");
      who.className = "cloud-account__text";
      who.appendChild(document.createTextNode("Signed in as "));
      var strong = document.createElement("strong");
      strong.textContent = user.email || "your Google account";
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
  }

  /* ---------------- wiring ---------------- */

  window.CloudSync = {
    enabled: enabled,
    isSignedIn: function () { return !!user; },
    signIn: signIn,
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
