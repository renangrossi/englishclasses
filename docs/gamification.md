# Gamification (XP, streaks, badges)

Phase 1 is implemented and live: `assets/js/progress.js`. It is fully
offline — everything is read from and written to the browser's own
`localStorage`, nothing is sent to a server, and it works identically
on GitHub Pages with no backend at all.

## What the student sees

- A compact pill in the header (top right, next to the search and
  dark-mode buttons) showing the current streak and total XP. Clicking
  it opens a small panel with per-level progress bars and a badge grid.
- A "+10 XP" toast in the top-right corner right after submitting an
  exercise, and a bigger "Badge unlocked" toast when one is earned —
  each stays up for `TOAST_VISIBLE_MS` (~7.2s, 3x the original ~2.4s)
  before fading out over `TOAST_EXIT_MS` (350ms), both defined near the
  top of `progress.js`. Clicking/tapping a toast dismisses it early.
  Unless the browser has `prefers-reduced-motion: reduce` set, a short
  gold/amber sparkle burst (`.xp-burst`, styled in `components.css`)
  plays behind/around the toast — bigger for a badge unlock than a
  plain XP gain. Under reduced motion, the burst is skipped entirely
  but the longer toast duration still applies.
- `progress.html` — a full page with the same information at a larger
  size, plus a "Reset my progress on this device" button.

`assets/js/progress.js` is now loaded on every page that shares the
site's standard header (all 39 HTML pages, including previously-omitted
informational pages like the homepage, Dictionary, Extras, Exercises
and Simulated Exams) so the header pill can never "disappear" just by
navigating to one of them. The pill itself, though, stays hidden
(`hidden` attribute, see `hasProgress()`/`renderToggle()` in
`progress.js`) until the student has real progress on this device —
`state.xp > 0` or at least one recorded exercise — at which point it
shows on every one of those pages and stays visible across navigation
and reloads. It only goes back to hidden if progress is wiped, via
`progress.html`'s reset button or the browser's storage being cleared.

## Where data is stored

`localStorage["rt_progress"]`, as JSON:

```json
{
  "version": 1,
  "xp": 0,
  "streak": { "count": 0, "lastActiveDate": "YYYY-MM-DD", "brokenOnce": false },
  "badges": [],
  "exercises": {
    "exercise-id": { "bestCorrect": 0, "total": 0, "xpAwarded": true, "perfect": false }
  },
  "levelStats": { "A1": { "xp": 0, "exercisesDone": 0 }, "A2": {...}, ... },
  "pagesCompleted": { "test-yourself:A1": true, "placement": true },
  "dictionaryUses": 0,
  "topicsCompleted": { "A1:simple-present-i": { "name": "A1 · Simple Present I", "level": "A1", "awardedAt": "YYYY-MM-DD" } },
  "timeFlags": { "nightOwl": true, "earlyBird": true }
}
```

- `exercises` is the anti-farming ledger: XP for a given exercise
  block `id` is only ever awarded the first time that id is submitted
  (in this browser). Retrying updates `bestCorrect`/`perfect` for
  accurate stats and badges, but never re-awards XP.
- `pagesCompleted` tracks the one-off "finished the whole page" bonus
  for Test Yourself (`test-yourself:<LEVEL>`) and the Placement Test
  (`placement`) — see "How page-completion is detected" below.
- `streak.brokenOnce` is set the first time a real gap (more than one
  calendar day, and not the student's very first-ever activity) is
  detected between sessions — see `touchStreak()`. It's never cleared
  back to `false`, so the "comeback" badge (below) can fire the moment
  the student does one more exercise after returning, any time after
  the break.
- `dictionaryUses` counts every real word lookup — see
  `recordDictionaryUse()` under "Progress events" below.
- `topicsCompleted` is a second, open-ended badge list — one entry per
  fully-completed single-topic lesson page (see "Topic badges" below).
  Kept separate from the fixed `BADGES` catalog on purpose, since new
  lesson pages add new topics without any code change.
- `timeFlags` records which time-of-day windows the student has ever
  submitted a graded exercise in, set opportunistically in
  `recordExerciseResult()` so the "night_owl"/"early_bird" badge
  `check()` functions can stay pure functions of `state` (see
  `touchTimeOfDayFlags()`) instead of reaching for `Date.now()`
  themselves.
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

### Current badge catalog (`BADGES` in `progress.js`)

| id | Name | Unlocks when |
|---|---|---|
| `first_steps` | First Steps | Complete 1 exercise |
| `perfectionist` | Perfectionist | Score 100% on 1 exercise |
| `streak_3` / `streak_7` / `streak_14` / `streak_30` | N-Day Streak | Streak count reaches 3 / 7 / 14 / 30 |
| `placement_done` | Know Your Level | Placement Test completed |
| `comeback` | Comeback | `streak.brokenOnce` is true (a real gap happened, then another exercise was completed) |
| `first_test_yourself` | Test Yourself, Tested | Any level's Test Yourself page fully completed, first time |
| `xp_100` / `xp_250` / `xp_500` / `xp_1000` | N XP | Total XP reaches that milestone |
| `no_hints_needed` | No Hints Needed | 5 different exercises scored 100% |
| `sherlock` | Sherlock | First dictionary lookup (`dictionaryUses >= 1`) |
| `dictionary_power_user` | Dictionary Power User | 10th dictionary lookup |
| `polyglot` | Polyglot Path | At least 1 completed exercise at 3 different levels |
| `night_owl` / `early_bird` | Night Owl / Early Bird | An exercise graded between 00:00–05:00 / 05:00–07:00 on the device's own clock |
| `a1_explorer` … `c2_explorer` | `<LEVEL>` Explorer | ~30% of that level's exercises done (see `explorerThreshold()`) |

Plus the open-ended **topic badges** (`state.topicsCompleted`), documented separately below — they aren't part of the `BADGES` array or the table above.

## Topic badges (single-lesson completion)

Separate from the fixed `BADGES` catalog: the first time a student
completes *every* exercise on a single-topic lesson page — currently
A1's 21 individual lesson pages (e.g. `levels/a1/simple-present-i.html`)
are the only pages of this shape — `progress.js` records an entry in
`state.topicsCompleted` and shows a "Topic complete: A1 · Simple
Present I" toast, exactly like a regular badge unlock (longer duration,
sparkle burst, all the same).

This is deliberately **not** hand-maintained. `detectPageKind()` treats
any URL matching `/levels/<code>/<slug>.html` (one nested segment) as a
"topic" page — as opposed to a level overview page (`levels/a1.html`,
no nested segment, which legitimately bundles many different topics on
one page) or a Test Yourself / Placement page (matched first, before
the topic check). When every `.exercise-block` on a topic page has been
graded, `maybeCompleteTopic()`:

1. Builds a stable id: `"<LEVEL>:<slug>"`, e.g. `"A1:simple-present-i"`
   — `<LEVEL>` comes from the page's own `data-level-code` attribute
   (the same one `exercises.js` already reads), `<slug>` is the
   filename without `.html`.
2. Skips if that id is already in `state.topicsCompleted` (never
   awarded twice, same guard style as `pagesCompleted`).
3. Turns the slug into a readable name via `slugToTitle()`
   (`"simple-present-i"` → `"Simple Present I"`), prefixed with the
   level (`"A1 · Simple Present I"`).

**Adding a new lesson page that should earn a topic badge needs zero
changes to `progress.js`** — as soon as it exists at
`levels/<code>/<new-slug>.html` with its own `.exercise-block`s, this
logic picks it up automatically. This is the `topic:A2:past-continuous`
pattern the badge system is built around, in case a level other than
A1 gets its own individual lesson pages later.

Topic badges show as a compact "📘 N topics completed" line in the
header panel, and as a full list on `progress.html`'s "Topics
Completed" section (`#progress-topics`, rendered by `topicListHtml()`)
— there's no fixed catalog to check them against, so unlike `BADGES`
there's no "locked" placeholder state to render, only earned ones.

## Progress events (public API calls other scripts make)

Besides grading exercises, two other student actions feed the badge
system:

- **`recordDictionaryUse()`** — called from `assets/js/dictionary.js`
  (every click on an outbound "Look up" link, and the Enter-key
  shortcut) and `assets/js/dict-widget.js` (every real lookup attempt,
  i.e. a non-empty query that's different from the one already in
  flight — see the `word !== lastQuery` guard there). Increments
  `state.dictionaryUses`, no XP or streak/daily-bonus touch — browsing
  the dictionary isn't itself a graded practice activity, it just
  feeds the `sherlock` / `dictionary_power_user` badges.
- Time-of-day and level-count signals (`night_owl`/`early_bird`,
  `polyglot`) don't need their own event — they're derived
  opportunistically inside the existing `recordExerciseResult()` /
  `levelStats` bookkeeping, see `touchTimeOfDayFlags()` and
  `countLevelsWithActivity()`.

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
recordDictionaryUse()  // dictionary.js / dict-widget.js — see "Progress events" above
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

1. On a fresh device/profile (no `rt_progress` in localStorage), open
   the homepage or Dictionary — the header pill should not be visible.
2. Open any level page with exercises, e.g. `levels/a1/to-be-am-is-are.html`.
3. Complete an exercise block and click **Submit**. You should see a
   "+10 XP" (or "+15 XP" on a perfect score) toast with a gold sparkle
   burst behind it, staying up for a few seconds (~7s) before fading —
   click it to confirm it dismisses early — and the header pill appears
   (or updates) with the new XP number.
4. Navigate to the homepage, Dictionary, Extras, Exercises or Simulated
   Exams and confirm the header pill is now visible there too, then
   reload each — it should stay visible (persistence, not just an
   in-memory state).
5. Click the header pill (flame + XP) to open the panel — check the
   A1 progress bar moved and **First Steps** (and **Perfectionist**,
   if that attempt was 100%) show as unlocked in the badge grid.
6. Retry the *same* exercise and confirm the XP total does **not**
   increase again (anti-farming).
7. Open `levels/a1/test-yourself.html`, complete every exercise block
   on the page, and confirm a "+25 XP" toast appears once the last
   block is submitted (this can take a while on A1 — for a quicker
   check, use a shorter Test Yourself page like `levels/b2/test-yourself.html`).
8. Open `placement-test.html`, submit the test, and confirm "+40 XP"
   plus the **Know Your Level** badge — the badge toast's sparkle burst
   should be noticeably bigger than a plain XP toast's.
9. In OS/browser settings, enable "reduce motion", submit another
   exercise, and confirm the toast still appears for the same ~7s
   duration but with no sparkle burst.
10. Open `progress.html` directly and confirm the full-page view matches
    the header panel, then use **Reset my progress on this device** and
    confirm everything goes back to zero — including the header pill
    disappearing again on every page.
11. To test the streak deliberately: open DevTools → Application →
    Local Storage → find `rt_progress` → edit `streak.lastActiveDate`
    to yesterday's date → reload and complete one exercise → streak
    count should go up by 1.
12. Open `dictionary.html`, type a word and click any "Look up" button
    (or the floating dictionary widget on a level page and let it look
    a word up) — confirm the **Sherlock** badge toast appears, and only
    once (repeat lookups of the same word shouldn't re-trigger it, and
    it should never be awarded twice even after 10+ different lookups).
13. Open an A1 lesson page you haven't fully completed yet (e.g.
    `levels/a1/have-has.html`) and submit every exercise block on it —
    confirm a "Topic complete: A1 · Have / Has" toast appears once, and
    `progress.html`'s "Topics Completed" section lists it. Retrying an
    already-completed block afterwards must not re-award it.
14. To test the streak-break/`brokenOnce`-driven badges: set
    `streak.lastActiveDate` to 3+ days ago in DevTools, reload, and
    complete one exercise — confirm the **Comeback** badge unlocks.
15. Edit `xp` directly in DevTools to 100/250/500/1000 and reload (or
    just keep completing exercises) to confirm each XP-milestone badge
    fires at the right threshold, not before.

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
