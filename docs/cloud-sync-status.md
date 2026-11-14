# Saved progress — where we stopped (13 November 2026)

Working notes for picking this up again. How the feature works and how
it was set up is in [`cloud-sync.md`](cloud-sync.md); this file is only
the current state and what is still open.

## State

Everything is pushed (`main` at `d6882f7`) and switched on.

| Piece | State |
| --- | --- |
| Site code (`assets/js/cloud-sync.js`, merge code in `progress.js` / `mastery.js`) | live |
| Supabase project `ustsqrbceviabupvaaip` | URL and publishable key are in `cloud-sync.js` |
| Table `student_progress` (`supabase/schema.sql`) | created, row level security on, exposed in the Data API |
| Google provider in Supabase | enabled |
| Google OAuth consent screen | **still in "Testing"** — only listed test users can sign in |
| `privacy.html` | live, linked from every footer, the progress page and the sign-in block |

Checked from outside with the publishable key on 13 Nov: the table
answers, a signed-out read returns no rows, a signed-out insert is
refused by row level security.

## Still to do

1. **Publish the Google app.** In Google Cloud → OAuth consent screen →
   Branding, set the privacy policy link to
   `https://renangrossi.github.io/englishclasses/privacy.html`, then
   Publish. Until then any student who is not a test user gets Google's
   "access blocked" screen.
2. **Test a real sign-in. This has never been run.** Only the sync logic
   was tested, against a fake Supabase (`node scripts/test_cloud_sync.js .`).
   - Sign in on the live site, do one exercise.
   - Supabase → Table Editor → `student_progress`: one row should appear.
   - Sign in on a second device: the XP should show up.
   - If it fails, the browser console has a line starting `[cloud-sync]`.
3. **Look at the pages in a browser.** Nothing was viewed while building:
   the Sign in with Google block in the header progress panel and on
   `progress.html`, and the layout of `privacy.html`.
4. **Read `privacy.html`.** It is published in Renan's name. It says the
   teacher can see students' progress, that there are no analytics, and
   gives `renanvg@proton.me` for deletion requests.

## Things that could go wrong on first test

- **Redirect not allowed.** After Google, the student should land back on
  the page they started from. If they land on the home page or get an
  error instead, Supabase → Authentication → URL Configuration → Redirect
  URLs needs `https://renangrossi.github.io/englishclasses/**`. This
  setting could not be checked from outside.
- **Publishable key rejected by the library.** `cloud-sync.js` loads
  supabase-js 2.45.4 from jsDelivr and passes the new-style
  `sb_publishable_…` key. Direct API calls with it work; the library with
  it is untested. If requests fail with 401, try a newer supabase-js
  (change `SDK_URL`) or the legacy anon key.
- **Stale assets.** GitHub Pages caches for 10 minutes. After any change
  under `assets/`, run `python3 scripts/stamp_asset_versions.py`.

## Decisions already made

- Signing in is optional; signed out, nothing leaves the browser.
- With sync on, the progress pill in the header is always visible (a new
  device has no progress, and the panel holds the sign-in button).
- Signing out uploads, then empties the browser.
- "Reset my progress" while signed in resets the account on every device.
- The Google client secret lives only in the Supabase dashboard — never
  in this repository.

## Ideas not started

- A teacher view of all students' progress (today: Supabase Table Editor,
  or the query in `cloud-sync.md`).
- Opt-in class leaderboard (see the end of `gamification.md`).
- Self-service "delete my account" button; today it is by email.
