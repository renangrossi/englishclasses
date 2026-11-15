// Tests the account-sync logic (assets/js/cloud-sync.js + the merge code in
// progress.js / mastery.js) with two fake devices and a fake Supabase.
// No network, no browser:   node scripts/test_cloud_sync.js .
const fs = require("fs"), vm = require("vm"), assert = require("assert");
const ROOT = process.argv[2];
const src = f => fs.readFileSync(ROOT + "/assets/js/" + f, "utf8");
const cloudSrc = src("cloud-sync.js")
  .replace(/var SUPABASE_URL = "[^"]*";/, 'var SUPABASE_URL = "https://x.supabase.co";')
  .replace(/var SUPABASE_ANON_KEY = "[^"]*";/, 'var SUPABASE_ANON_KEY = "k";')
  .replace("var UPLOAD_DELAY_MS = 1500;", "var UPLOAD_DELAY_MS = 5;");
assert(cloudSrc.includes('"https://x.supabase.co"') && cloudSrc.includes("= 5;"));

const server = { rows: {}, writes: 0, fail: false, otpSent: [], otpError: null };
const sleep = ms => new Promise(r => setTimeout(r, ms));

function device(sessionUser, { mastery = true, initial = {}, search = "" } = {}) {
  const store = Object.assign({}, initial);
  const listeners = {};
  const localStorage = {
    getItem: k => (k in store ? store[k] : null),
    setItem: (k, v) => { store[k] = String(v); },
    removeItem: k => { delete store[k]; },
  };
  let session = sessionUser ? { user: sessionUser } : null;
  if (session) store.rt_auth = "x";
  const document = {
    readyState: "loading", visibilityState: "visible",
    addEventListener: (n, f) => (listeners[n] = listeners[n] || []).push(f),
    dispatchEvent: e => (listeners[e.type] || []).forEach(f => f(e)),
    querySelectorAll: () => [], querySelector: () => null, getElementById: () => null,
    createElement: () => ({ setAttribute() {}, appendChild() {}, classList: { add() {}, toggle() {}, remove() {} }, style: {} }),
    body: { appendChild() {} }, head: { appendChild() {} },
  };
  const client = {
    auth: {
      getSession: async () => ({ data: { session } }),
      onAuthStateChange() {},
      signOut: async () => { session = null; delete store.rt_auth; return {}; },
      signInWithOtp: async args => { server.otpSent.push(args); return server.otpError ? { error: server.otpError } : { data: {} }; },
      verifyOtp: async ({ email, token, type }) => {
        if (token !== "123456" || type !== "email") return { error: { message: "Token has expired or is invalid" } };
        session = { user: { id: "cara", email } }; store.rt_auth = "x";
        return { data: { session } };
      },
    },
    from: () => ({
      select: () => ({ eq: (_c, id) => ({ maybeSingle: async () => {
        if (server.fail) return { error: { message: "offline" } };
        const r = server.rows[id];
        return { data: r ? JSON.parse(JSON.stringify(r)) : null };
      } }) }),
      upsert: async p => {
        if (server.fail) return { error: { message: "offline" } };
        server.writes++;
        server.rows[p.user_id] = Object.assign({ mastery: {}, epoch: 0 }, server.rows[p.user_id], JSON.parse(JSON.stringify(p)));
        return {};
      },
    }),
  };
  const window = {
    localStorage, document, console: { warn() {} },
    location: { pathname: "/englishclasses/levels/a1/x.html", search, hash: "", origin: "https://h", href: "https://h/", assigned: null, assign(u) { this.assigned = u; } },
    addEventListener() {}, confirm: () => true, matchMedia: () => ({ matches: false }),
    supabase: { createClient: () => client },
    innerWidth: 1000,
  };
  window.window = window;
  const ctx = vm.createContext(Object.assign(window, {
    setTimeout, clearTimeout, Promise, JSON, Date, Math, Object, Array, String, URL,
    CustomEvent: function (type) { this.type = type; },
  }));
  vm.runInContext(src("progress.js"), ctx);
  document.readyState = "complete"; // progress.js skips its DOM widget; cloud-sync boots
  vm.runInContext(cloudSrc, ctx);
  if (mastery) vm.runInContext(src("mastery.js"), ctx);
  return { w: ctx, store, document,
    submit(id, correct, total, items) {
      ctx.ProgressTracker.recordExerciseResult({ level: "A1", exerciseId: id, correct, total });
      document.dispatchEvent({ type: "exercise:submitted", detail: { id, results: items || [] } });
    } };
}

(async () => {
  const ana = { id: "ana", email: "ana@example.com" }, bia = { id: "bia", email: "b@example.com" };

  // 1. Anonymous progress, then sign in: local progress reaches the account.
  let phone = device(null);
  phone.submit("ex1", 3, 3, [{ itemId: "q1", attempted: true, correct: true }]);
  phone.submit("ex2", 1, 3);
  const phoneXp = phone.w.ProgressTracker.getState().xp;
  assert(phoneXp > 0 && !server.rows.ana, "signed out must not upload");
  const phoneStore = phone.store;
  // "sign in" = reload the page with a session, same storage
  phone = device(ana, { initial: phoneStore });
  await sleep(60);
  assert(server.rows.ana, "row created");
  assert.strictEqual(server.rows.ana.progress.xp, phone.w.ProgressTracker.getState().xp);
  assert(server.rows.ana.progress.exercises.ex1 && server.rows.ana.mastery.items["ex1/q1"]);
  console.log("1 ok  first sign-in uploads local progress, xp", server.rows.ana.progress.xp);

  // 2. New device, same account: progress comes down.
  let laptop = device(ana);
  await sleep(60);
  let ls = laptop.w.ProgressTracker.getState();
  assert.strictEqual(ls.xp, server.rows.ana.progress.xp);
  assert(ls.exercises.ex2 && laptop.w.MasteryTracker.getState().items["ex1/q1"]);
  const w0 = server.writes; await sleep(40);
  assert.strictEqual(server.writes, w0, "no upload when nothing changed");
  console.log("2 ok  second device downloads it, no redundant upload");

  // 3. Both devices work, each uploads; both converge with the union.
  laptop.submit("ex3", 2, 2); await sleep(60);
  phone.submit("ex4", 2, 2); await sleep(60);          // phone hasn't seen ex3 yet
  const afterPhone = server.rows.ana.progress;
  assert(afterPhone.exercises.ex3 && afterPhone.exercises.ex4, "phone upload kept laptop's ex3");
  laptop.submit("ex5", 0, 2); await sleep(60);
  const fin = server.rows.ana.progress;
  ["ex1", "ex2", "ex3", "ex4", "ex5"].forEach(id => assert(fin.exercises[id], id));
  assert.strictEqual(laptop.w.ProgressTracker.getState().xp, fin.xp);
  // every exercise's XP is counted exactly once: 5 exercises, 3 perfect (ex1, ex3, ex4)
  const base = 5 * 10 + 3 * 5;
  const badgeXp = fin.xp - base;
  assert(badgeXp >= 0, "xp not under-counted: " + fin.xp);
  phone.w.ProgressTracker.recordDictionaryUse(); await sleep(60);
  assert.strictEqual(phone.w.ProgressTracker.getState().xp, server.rows.ana.progress.xp);
  // Reference: one device doing the same things with no sync at all.
  const solo = device(null);
  solo.submit("ex1", 3, 3); solo.submit("ex2", 1, 3); solo.submit("ex3", 2, 2); solo.submit("ex4", 2, 2); solo.submit("ex5", 0, 2);
  solo.w.ProgressTracker.recordDictionaryUse();
  solo.w.ProgressTracker.recordDictionaryUse(); // second pass lets the 100-XP badge see the dictionary badge's XP
  const ref = solo.w.ProgressTracker.getState();
  const got = phone.w.ProgressTracker.getState();
  assert.deepStrictEqual(got.badges.slice().sort(), ref.badges.slice().sort());
  assert.strictEqual(got.xp, ref.xp, "synced xp equals single-device xp");
  assert.strictEqual(got.levelStats.A1.exercisesDone, 5);
  laptop = device(ana, { initial: laptop.store }); await sleep(60);   // laptop reloads
  assert.strictEqual(laptop.w.ProgressTracker.getState().xp, got.xp, "devices agree on xp");
  console.log("   badges:", got.badges.join(","), "xp", got.xp, "solo xp", ref.xp);
  console.log("3 ok  two devices converge, xp", fin.xp, "(exercises 65 + badges", badgeXp + ")");

  // 3b. merging is idempotent
  const before = JSON.stringify(laptop.w.ProgressTracker.getState());
  laptop.w.ProgressTracker.importState(server.rows.ana.progress, false);
  laptop.w.ProgressTracker.importState(server.rows.ana.progress, false);
  const st = laptop.w.ProgressTracker.getState();
  assert.strictEqual(st.xp, JSON.parse(before).xp, "re-merging the same data adds no xp");
  console.log("3b ok merge is idempotent");

  // 4. Offline: upload fails, data stays local, goes up later.
  server.fail = true;
  laptop.submit("ex6", 1, 1); await sleep(60);
  assert(!server.rows.ana.progress.exercises.ex6);
  server.fail = false;
  laptop.w.ProgressTracker.recordDictionaryUse(); await sleep(60);
  assert(server.rows.ana.progress.exercises.ex6);
  console.log("4 ok  failed upload is retried with the next save");

  // 5. Reset on laptop reaches the account and the phone.
  laptop.w.ProgressTracker.resetProgress(); await sleep(80);
  assert.strictEqual(server.rows.ana.progress.xp, 0);
  assert.strictEqual(server.rows.ana.epoch, 1);
  assert.deepStrictEqual(server.rows.ana.mastery.items, {});
  phone.w.ProgressTracker.recordDictionaryUse(); await sleep(60); // phone still had everything
  assert.strictEqual(phone.w.ProgressTracker.getState().xp, 0, "phone dropped its old copy");
  assert.strictEqual(Object.keys(server.rows.ana.progress.exercises).length, 0, "reset not undone by the phone");
  console.log("5 ok  reset propagates and is not resurrected");

  // 6. Sign out clears the device; another student signing in does not inherit.
  laptop.submit("ex7", 1, 1); await sleep(60);
  await laptop.w.CloudSync.signOut();
  assert.strictEqual(laptop.w.ProgressTracker.getState().xp, 0);
  assert(!laptop.store.rt_sync_meta && server.rows.ana.progress.exercises.ex7);
  console.log("6 ok  sign-out saves, then empties the device");

  // 7. Device left holding ana's data (sign-out while offline), bia signs in.
  server.fail = true;
  phone.submit("ex8", 1, 1); await sleep(60);
  await phone.w.CloudSync.signOut();           // confirm() -> true, data kept
  assert(phone.w.ProgressTracker.getState().exercises.ex8);
  server.fail = false;
  const shared = device(bia, { initial: phone.store }); await sleep(60);
  assert(!server.rows.bia.progress.exercises.ex8, "bia must not get ana's exercise");
  assert(!shared.w.ProgressTracker.getState().exercises.ex8);
  console.log("7 ok  a different student does not inherit leftover progress");

  // 8. Page without mastery.js must not wipe the mastery column.
  phone = device(ana);  await sleep(60);
  phone.submit("ex9", 1, 1, [{ itemId: "q9", attempted: true, correct: false }]); await sleep(60);
  assert(server.rows.ana.mastery.items["ex9/q9"]);
  const noM = device(ana, { mastery: false }); await sleep(60);
  noM.w.ProgressTracker.recordDictionaryUse(); await sleep(60);
  assert(server.rows.ana.mastery.items["ex9/q9"], "mastery column preserved");
  console.log("8 ok  pages without mastery.js leave review data alone");

  // 9. Not configured: inert.
  const plain = vm.createContext({ document: { addEventListener() { throw new Error("should not listen"); } } });
  plain.window = plain;
  vm.runInContext(src("cloud-sync.js").replace(/var SUPABASE_URL = "[^"]*";/, 'var SUPABASE_URL = "";'), plain);
  assert.strictEqual(plain.CloudSync.enabled, false);
  console.log("9 ok  with no project URL the file is inert");

  // 10. Email sign-in: link + code. Signed-out progress goes up after the code.
  const cara = device(null);
  cara.submit("ex10", 2, 2);
  assert.strictEqual(await cara.w.CloudSync.sendEmailLink("not-an-email"), false);
  assert.strictEqual(server.otpSent.length, 0, "bad address is not sent");
  assert.strictEqual(await cara.w.CloudSync.sendEmailLink("  cara@example.com "), true);
  const sent = server.otpSent[0];
  assert.strictEqual(sent.email, "cara@example.com");
  assert.strictEqual(sent.options.emailRedirectTo, "https://h/englishclasses/levels/a1/x.html", "link comes back to this page");
  assert(JSON.parse(cara.store.rt_email_pending).email === "cara@example.com", "pending email remembered");
  assert.strictEqual(cara.w.CloudSync.isSignedIn(), false);
  assert.strictEqual(await cara.w.CloudSync.verifyEmailCode("999999"), false, "wrong code");
  assert.strictEqual(cara.w.CloudSync.isSignedIn(), false);
  assert.strictEqual(await cara.w.CloudSync.verifyEmailCode("123 456"), true, "code with a space still works");
  await sleep(60);
  assert(!cara.store.rt_email_pending, "pending email cleared after sign-in");
  assert(server.rows.cara && server.rows.cara.progress.exercises.ex10, "progress made before signing in is uploaded");
  assert(/today-review\.html$/.test(cara.w.location.assigned || ""), "a fresh sign-in opens Today's Review");
  console.log("10 ok email link/code sign-in, then sync, then Today's Review");

  // 11. Sending fails (rate limit): nothing remembered, no sign-in.
  const dan = device(null);
  server.otpError = { status: 429, message: "email rate limit exceeded" };
  assert.strictEqual(await dan.w.CloudSync.sendEmailLink("dan@example.com"), false);
  assert(!dan.store.rt_email_pending);
  server.otpError = null;
  console.log("11 ok a failed send leaves no pending code");

  // 12. Today's Review opens after a sign-in made just now (back from
  // Google / an email link), never for a session restored on page load.
  const eve = { id: "eve", email: "e@x" };
  const back = device(eve, { search: "?code=abc" }); await sleep(60);
  assert(/today-review\.html$/.test(back.w.location.assigned || ""), "back from Google opens Today's Review");
  const again = device(eve, { initial: back.store }); await sleep(60);
  assert.strictEqual(again.w.location.assigned, null, "a restored session stays on the page");
  console.log("12 ok Today's Review opens after a new sign-in only");
})().catch(e => { console.error("FAIL", e); process.exit(1); });
