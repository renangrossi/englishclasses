# Auth email templates

Copies of what is pasted into Supabase → Authentication → Emails → Templates
(the dashboard is the source of truth; keep these in step by hand).

- `magic-link.html` → **Magic link or OTP**, subject
  `Your sign-in link and code - Renan the Teacher's English Academy`
- `confirm-signup.html` → **Confirm sign up**, subject
  `Confirm your email - Renan the Teacher's English Academy`

Styled like the site (navy header, Old Glory stripe, parchment code box,
burgundy button) with inline styles and tables only: no images, no web
fonts, under 5 KB each. `{{ .ConfirmationURL }}` is the link, `{{ .Token }}`
the 6-digit code the sign-in form accepts.
