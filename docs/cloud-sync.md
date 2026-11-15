# Saved progress (Supabase + Google or email sign-in)

Students can sign in with Google, or with a link/code sent to their
email, and have their XP, streak, badges and
review history saved to an account, so it follows them between devices.
Signing in is optional: signed out, the site works from `localStorage`
exactly as before and sends nothing anywhere.

| Piece | Where |
| --- | --- |
| Sync + sign-in code | `assets/js/cloud-sync.js` |
| Merge rules | `mergeStates()` in `assets/js/progress.js`, `importState()` in `assets/js/mastery.js` |
| Database table and security policies | `supabase/schema.sql` |

Until the two constants at the top of `cloud-sync.js` are filled in, the
file does nothing and the site looks and behaves as it did before.

## One-time setup

### 1. Supabase project

1. <https://supabase.com/dashboard> → **New project** (the free plan is
   enough). Pick a region close to your students.
2. **SQL Editor → New query**, paste the whole of `supabase/schema.sql`,
   **Run**.
3. **Project Settings → API** (or **API Keys**): copy the **Project URL**
   and the **anon / publishable** key. Never use the `service_role` /
   secret key on the site.

### 2. Google OAuth client

1. <https://console.cloud.google.com/> → create (or pick) a project.
2. **APIs & Services → OAuth consent screen**: User type **External**,
   fill in the app name ("Renan the Teacher"), support email, and add
   `supabase.co` and `renangrossi.github.io` under authorised domains.
   The only scopes needed are the defaults (`email`, `profile`, `openid`).
   Then **Publish app** — while it is in "Testing" only the test users you
   list can sign in.
3. **APIs & Services → Credentials → Create credentials → OAuth client
   ID**, type **Web application**:
   - Authorised JavaScript origins: `https://renangrossi.github.io`
   - Authorised redirect URIs: `https://<project-ref>.supabase.co/auth/v1/callback`
     (Supabase shows the exact value on the Google provider page, next step).
4. Copy the **Client ID** and **Client secret**.

### 3. Connect the two

In Supabase:

1. **Authentication → Sign In / Providers → Google**: enable, paste the
   Client ID and Client secret, save.
2. **Authentication → URL Configuration**:
   - Site URL: `https://renangrossi.github.io/englishclasses/`
   - Redirect URLs, add: `https://renangrossi.github.io/englishclasses/**`
     and, for testing on your own machine, `http://localhost:8000/**`.

   Students return to the page they signed in from, so the `/**` matters.

### 3b. Email sign-in (link + code)

The sign-in block offers an email box under the Google button. One email
carries both a **link** (works in the browser that asked for it) and a
**6-digit code** (works anywhere -- e.g. email read on the phone while the
course is open on a computer). It needs:

1. **A custom SMTP sender.** Supabase's built-in sender only delivers to
   members of your Supabase team and allows 2 emails an hour, so students
   would get nothing. Create an account with an email service (Brevo,
   Resend, ...), verify the sender address/domain there, and enter its
   SMTP details in **Authentication → Emails → SMTP Settings**. Then raise
   the email limit in **Authentication → Rate Limits** if needed.
2. **Authentication → Sign In / Providers → Email**: enabled. "Confirm
   email" can stay on; the link/code is the confirmation.
3. **Authentication → Emails → Templates → Magic Link** must show the
   code as well as the link, or the code box is useless. For example:

   ```html
   <h2>Sign in to Renan the Teacher</h2>
   <p><a href="{{ .ConfirmationURL }}">Sign in</a></p>
   <p>Or type this code on the page where you asked for it: <strong>{{ .Token }}</strong></p>
   <p>If you did not ask for this, you can ignore this email.</p>
   ```

   Do the same in the **Confirm signup** template: a student's first email
   uses that one.
4. Name the email service in `privacy.html` ("If you sign in with your
   email").

**Current setup (Nov 2026):** Brevo free plan, sender
`renanvg@gmail.com` ("Renan the Teacher"), SMTP `smtp-relay.brevo.com:587`,
login `c35619001@smtp-brevo.com`, key generated in Brevo → SMTP & API.
Email OTP length set to 6 (Sign In / Providers → Email). Because the
sender is a Gmail address, Brevo rewrites it to `@…brevosend.com`; a
domain of your own would fix that and help deliverability.

The redirect URLs from step 3 already cover the link.

### 4. Switch it on in the site

Edit the top of `assets/js/cloud-sync.js`:

```js
var SUPABASE_URL = "https://<project-ref>.supabase.co";
var SUPABASE_ANON_KEY = "<anon / publishable key>";
```

then

```
python3 scripts/stamp_asset_versions.py
```

and commit. Both values are meant to be public; row level security in
`schema.sql` is what keeps each student to their own row.

### 5. Try it

```
python3 -m http.server 8000
```

Open <http://localhost:8000/progress.html>, sign in, do an exercise, and
look at **Table Editor → student_progress** in Supabase: one row with
your user id. Open the site in another browser, sign in with the same
Google account, and the XP should appear.

## How syncing behaves

- **When**: on every page load while signed in, and about 1.5 s after
  each save (an exercise, a dictionary lookup). Each sync reads the
  account's row, reconciles, and uploads only if something differs.
- **Merging**: exercises, badges, completed tests and topics are unioned,
  so work done on two devices, or before signing in, is all kept. XP is
  taken from the richer copy plus whatever the other copy has that it
  lacks, so nothing is counted twice.
- **Signing out** uploads first, then empties the browser, so the next
  person on a shared computer starts clean. If the upload fails the
  student is asked, and the progress stays on the device.
- **A different student signing in** on a device still holding someone
  else's progress gets their own account's copy, not a merge.
- **Reset my progress**, signed in, resets the account. The row's `epoch`
  goes up, which makes the student's other devices drop their copy
  rather than upload it back.
- **Offline**: saves stay in `localStorage` and go up on the next sync.

## Looking at students' progress

**Table Editor → student_progress** in the dashboard, or in the SQL
editor:

```sql
select u.email,
       (p.progress->>'xp')::int               as xp,
       (p.progress->'streak'->>'count')::int  as streak,
       jsonb_array_length(p.progress->'badges') as badges,
       p.updated_at
from public.student_progress p
join auth.users u on u.id = p.user_id
order by p.updated_at desc;
```

## Deleting a student's data

**Authentication → Users**, delete the user; their progress row goes with
it (`on delete cascade`).
