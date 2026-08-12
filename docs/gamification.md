# Gamification (XP, streaks, badges)

Phase 1 is implemented and live: `assets/js/progress.js`. It is fully
offline — everything is read from and written to the browser's own
`localStorage`, nothing is sent to a server, and it works identically
on GitHub Pages with no backend at all.

## What the student sees

- A compact pill in the header (top right, next to the search and
  dark-mode buttons) showing the current streak and total XP. Clicking
  it opens a small panel with per-level progress bars and a badge grid.
- A short "+10 XP" toast in the top-right corner right after submitting
  an exercise, and a bigger "Badge unlocked" toast when one is earned.
- `progress.html` — a full page with the same information at a larger
  size, plus a "Reset my progress on this device" button.

The widget appears on every page that already has interactive
exercises (level pages, individual A1 lesson pages, every level's
Test Yourself page, and the Placement Test) — the same 33 pages that
already load `assets/js/exercises.js`. It's intentionally left off
purely informational pages (Dictionary, Extras, the homepage) to avoid
clutter where it wouldn't do anything.

## Where data is stored

`localStorage["rt_progress"]`, as JSON:

```json
{
  "version": 1,
  "xp": 0,
  "streak": { "count": 0, "lastActiveDate": "YYYY-MM-DD" },
  "badges": [],
  "exercises": {
    "exercise-id": { "bestCorrect": 0, "total": 0, "xpAwarded": true, "perfect": false }
  },
  "levelStats": { "A1": { "xp": 0, "exercisesDone": 0 }, "A2": {...}, ... },
  "pagesCompleted": { "test-yourself:A1": true, "placement": true }
}
```

- `exercises` is the anti-farming ledger: XP for a given exercise
  block `id` is only ever awarded the first time that id is submitted
  (in this browser). Retrying updates `bestCorrect`/`perfect` for
  accurate stats and badges, but never re-awards XP.
- `pagesCompleted` tracks the one-off "finished the whole page" bonus
  for Test Yourself (`test-yourself:<LEVEL>`) and the Placement Test
  (`placement`) — see "How page-completion is detected" below.
- If the stored `version` doesn't match `SCHEMA_VERSION` in
  `progress.js`, the state resets rather than crashing on an
  incompatible shape. Bump `SCHEMA_VERSION` if you ever change the
  shape of this object in a way older saves can't be merged into.

Clearing site data/cookies for the domain, using a different browser,
or a different device all start fresh — that's expected for Phase 1
(see "Phase 2" below for the plan to change this).

## How to change XP values

Edit the `XP` object near the top of `assets/js/progress.js`:

```js
var XP = {
  exercise: 10,       // submitting an exercise block, first time (any score)
  perfectBonus: 5,    // extra, only if that first submission was 100%
  testYourself: 25,   // completing every exercise block on a Test Yourself page
  placement: 40,      // completing the Placement Test
  dailyBonus: 5,       // first activity of a new calendar day (on top of streak +1)
};
```

Change a number, save, redeploy — no other file needs to change.
Setting `dailyBonus` to `0` disables the daily-login bonus entirely
while streak counting keeps working exactly as before.

## How to add a badge

Add one object to the `BADGES` array in `assets/js/progress.js`:

```js
{
  id: "unique_id",           // stable — this is what's stored once earned
  icon: "🏅",                 // any emoji, shown when earned (locked shows 🔒)
  name: "Display Name",
  desc: "One sentence a student can read to know what to do.",
  check: function (state) {
    // Return true once this badge should be unlocked. `state` is the
    // same shape as getState() below — read whatever you need from
    // state.xp / state.streak / state.exercises / state.levelStats /
    // state.pagesCompleted.
    return state.xp >= 500;
  },
}
```

Badges are checked after every XP-earning action; a badge is only
ever added to `state.badges` once `check()` first returns true, and
never removed automatically. There's no separate "badge config file"
to keep in sync — this array is the single source of truth, and
`progress.html` renders directly from it.

The six `<level>_explorer` badges are generated automatically from the
`LEVELS` array and `LEVEL_EXERCISE_COUNTS`, scaled to ~30% of that
level's real exercise count (see `explorerThreshold()`) — update
`LEVEL_EXERCISE_COUNTS` if you add or remove a significant number of
exercises at a level, so the badge keeps meaning roughly the same
amount of effort everywhere.

## How page-completion is detected (Test Yourself / Placement)

There is no manual wiring per Test Yourself page. On load,
`progress.js` scans the current page for every
`.exercise-block script.exercise-data` and collects their `id`s (its
"page inventory"). It also looks at the URL: pages ending in
`test-yourself.html` or `placement-test.html` are treated as
completable pages; everything else is a normal lesson page and this
logic is skipped entirely.

After every exercise submission, if the page is completable, it
checks whether every id in the inventory now has an entry in
`state.exercises` (regardless of when each one was actually earned —
a Test Yourself block whose id was already completed earlier from its
own lesson page still counts). Once the whole inventory is covered, it
awards the page bonus exactly once (guarded by `pagesCompleted`) and
checks `placement_done`.

Adding a new Test Yourself page or growing an existing one needs
zero changes here — it Just Works from the exercise blocks already on
the page.

## Public API (`window.ProgressTracker`)

```js
recordExerciseResult({ level, exerciseId, correct, total, perfect })
recordTestProgress({ type: "test-yourself" | "placement", level })
getState()          // deep-cloned snapshot, safe to read/log
resetProgress()      // wipes localStorage["rt_progress"]
XP, BADGES, LEVELS   // read-only config, used by progress.html
```

`assets/js/exercises.js` calls `recordExerciseResult` once, right
after grading, at the very end of the Submit button's click handler —
guarded by `if (window.ProgressTracker && ...)` so a page that (for
whatever reason) doesn't load `progress.js` still grades exercises
exactly as before. Nothing in `exercises.js`'s grading logic itself
was changed.

## How to test

1. Open any level page with exercises, e.g. `levels/a1/to-be-am-is-are.html`.
2. Complete an exercise block and click **Submit**. You should see a
   "+10 XP" (or "+15 XP" on a perfect score) toast, and the header
   pill's XP number update.
3. Click the header pill (flame + XP) to open the panel — check the
   A1 progress bar moved and **First Steps** (and **Perfectionist**,
   if that attempt was 100%) show as unlocked in the badge grid.
4. Reload the page and confirm the XP/streak/badges are unchanged
   (persistence) — then retry the *same* exercise and confirm the XP
   total does **not** increase again (anti-farming).
5. Open `levels/a1/test-yourself.html`, complete every exercise block
   on the page, and confirm a "+25 XP" toast appears once the last
   block is submitted (this can take a while on A1 — for a quicker
   check, use a shorter Test Yourself page like `levels/b2/test-yourself.html`).
6. Open `placement-test.html`, submit the test, and confirm "+40 XP"
   plus the **Know Your Level** badge.
7. Open `progress.html` directly and confirm the full-page view matches
   the header panel, then use **Reset my progress on this device** and
   confirm everything goes back to zero.
8. To test the streak deliberately: open DevTools → Application →
   Local Storage → find `rt_progress` → edit `streak.lastActiveDate`
   to yesterday's date → reload and complete one exercise → streak
   count should go up by 1.

## Phase 2 (optional — not implemented yet)

Phase 1 intentionally has **no** login and **no** server, so it stays
free and fully functional on GitHub Pages alone. Optional
cross-device sync would need a small backend; Supabase's free tier
(Postgres + built-in auth) fits this project well because the rest of
the site is also free-tier-only (Cloudflare Workers for the AI
Teacher). Sketch, to implement later:

1. **Create a Supabase project** (free tier) and note the project URL
   + anon public key.
2. **Auth**: use Supabase's magic-link (passwordless email) auth —
   no password storage/reset flow to build. Add a small "Save my
   progress" button to the progress panel that opens an email-only
   sign-in form.
3. **Table** `progress` (one row per user):
   ```sql
   create table progress (
     user_id uuid references auth.users primary key,
     state jsonb not null,
     updated_at timestamptz not null default now()
   );
   alter table progress enable row level security;
   create policy "own row only" on progress
     for all using (auth.uid() = user_id);
   ```
   Store the exact same JSON shape `getState()` already returns —
   no separate schema to design.
4. **Sync logic** (new file, e.g. `assets/js/progress-sync.js`, only
   loaded once auth is wired up):
   - On sign-in: fetch the row for `auth.uid()`; if it exists and is
     newer, merge it into local storage (simplest correct merge: take
     the higher `xp`, the union of `badges`, the newer `streak`, and
     per-key `exercises`/`pagesCompleted` union) rather than a naive
     overwrite, so progress made offline before signing in isn't lost.
   - After every local write (`saveState` in `progress.js`), if
     signed in, `upsert` the same JSON to Supabase (debounce a couple
     of seconds so rapid exercise submissions don't spam requests).
   - Add a `supabase-js` `<script>` tag (CDN, ~30kb) only on pages
     where this matters, or lazy-load it on first click of "Save my
     progress" so it costs nothing for students who never opt in.
5. **Never required**: keep `progress.js`'s public API and behavior
   unchanged when signed out — Phase 1 must keep working exactly as it
   does today for every student who never creates an account.
6. **Class / weekly leaderboard** (later still, genuinely optional):
   a read-only Supabase view aggregating opted-in students' XP for a
   given week, shown on a new page — only meaningful once sync exists,
   and only for students who explicitly opt in (a boolean column on
   the `progress` row, default `false`).
