# AI English Teacher — backend deployment

This folder is **not** part of the GitHub Pages site (nothing under
`worker/` is linked from any HTML page). It's the source for a
separate Cloudflare Worker that acts as a secure proxy between your
website and the Groq API — the only place your Groq API key lives.

## Why a separate deployment?

GitHub Pages only serves static files — there's no way to keep a
secret out of the browser if the AI call happened directly from your
site's JavaScript. The Worker runs on Cloudflare's servers, holds the
key there, and your site's JS only ever talks to the Worker.

## One-time setup (about 15 minutes)

### 1. Create free accounts (no credit card required for either)
- **Groq**: [console.groq.com](https://console.groq.com) → sign up → **API Keys** → Create API Key. Copy it somewhere safe.
- **Cloudflare**: [dash.cloudflare.com/sign-up](https://dash.cloudflare.com/sign-up) → sign up (email + password, or Google — either is fine, this is *your* account, not a student-facing login).

### 2. Install Wrangler (Cloudflare's deploy tool)
```bash
npm install -g wrangler
wrangler login
```
This opens a browser window to connect Wrangler to your new Cloudflare account.

### 3. Create the KV namespace (used for rate-limit counters)
```bash
cd worker
wrangler kv namespace create AI_TEACHER_KV
```
This prints something like:
```
id = "abcd1234..."
```
Copy that `id` value into `wrangler.toml`, replacing `REPLACE_WITH_YOUR_KV_NAMESPACE_ID`.

### 4. Set your Groq API key as a secret (never committed to git)
```bash
wrangler secret put GROQ_API_KEY
```
Paste your Groq key when prompted. This stores it encrypted on Cloudflare's side — it is never written to any file in this repo.

### 5. Confirm the allowed origin
Open `worker.js` and check the top of the file:
```js
const ALLOWED_ORIGIN = "https://renangrossi.github.io";
```
Update this if your GitHub Pages URL is different (e.g. a custom domain).

### 6. Deploy
```bash
wrangler deploy
```
This prints your live Worker URL, something like:
```
https://ai-teacher.your-subdomain.workers.dev
```

### 7. Point the website at your Worker
Open `build.py` in the main project (not this folder) and find:
```python
AI_TEACHER_WORKER_URL = "https://ai-teacher.YOUR-SUBDOMAIN.workers.dev"
```
Replace it with the real URL from Step 6, then rebuild the site:
```bash
python3 build.py
python3 build_lessons.py
```
Commit and push as usual — the chat widget will now reach your live Worker.

## Adjusting limits

At the top of `worker.js`:
- `DAILY_LIMIT_PER_ANON` — questions per browser per day (default 20).
- `BURST_LIMIT_PER_IP` / `BURST_WINDOW_SECONDS` — short-term abuse brake (default 8 requests/60s per IP).
- `MAX_MESSAGE_LENGTH` — longest question accepted (keep in sync with the `maxlength` on the textarea in `assets/js/ai-teacher.js` if you change it).

## Course catalog (`course-catalog.json`)

So the AI Teacher can recommend a *real* lesson link instead of guessing one, `worker.js` imports `course-catalog.json` — a small, hand-maintained list of every real course page (level index pages, A1's individual lesson pages, and the PDF/Word worksheets linked from the A2/B1/B2 level pages) with their real on-site URLs. At request time the Worker does a lightweight, deterministic keyword match between the student's message (plus recent conversation) and this catalog, and only ever hands the model URLs that come out of that match — the model is instructed to never output a URL that wasn't supplied to it that turn, so it's structurally unable to invent one.

**This file is not auto-generated — there is no `build.py` in this repo.** If you add, rename, or move a lesson/worksheet/level page, update `course-catalog.json` by hand (or regenerate the relevant section with a small script that scrapes the real `href`s out of the `levels/*.html` files, the way it was first built — see git history for the extraction approach). Each entry:
```json
{ "level": "A2", "title": "Zero and First Conditionals", "url": "cefr/a2-elementary/l-zero-and-first-conditionals.pdf", "type": "worksheet", "format": "pdf" }
```
- `url` is site-root-relative (no leading slash, no domain) — the Worker resolves it against `SITE_BASE_URL` in `worker.js`.
- `type` is `"lesson"` (A1 HTML pages), `"worksheet"` (PDF/DOCX), `"test"` (test-yourself pages), or `"page"` (top-level utility pages like Exercises/Dictionary).
- Optional `aliases`: extra search terms for topics where common student phrasing doesn't share words with the on-site title (e.g. `"To Be (Am, Is, Are)"` has alias `"be verb"`).
- C1/C2 topics currently have **no resource entries on purpose** — those pages have no linked content yet, so the tutor correctly says it doesn't have that exact page rather than linking the topic-only overview page as if it were the lesson.

After editing the catalog, redeploy with `wrangler deploy` (it's bundled into the Worker at deploy time, not fetched at runtime).

After editing, redeploy with `wrangler deploy`.

## What data is sent/stored

- The student's message and the current conversation (kept in the browser tab's memory only, lost on reload) are sent to the Worker, then to Groq, to generate a reply.
- The Worker stores nothing except two small rate-limit counters in KV: an anonymous ID (a random string generated in the browser, no personal info) plus a request count, both auto-expiring after 24 hours or 60 seconds.
- Per Groq's terms (worth re-checking at console.groq.com before relying on it long-term), free-tier requests may be logged for abuse monitoring; nothing here is guaranteed private, so the frontend also tells students not to share personal information.

## Free-tier reality check

Groq's `openai/gpt-oss-120b` free tier is roughly 1,000 requests/day
**shared across every visitor to your site**, not per-student. The
Worker automatically falls back to the `openai/gpt-oss-20b` model
(same ~1,000 requests/day, but a separate quota pool) if the primary
model's daily quota is exhausted, so the feature keeps working at
slightly lower quality rather than going down entirely. The
per-browser daily cap (`DAILY_LIMIT_PER_ANON`) exists specifically to
stop one visitor from using up the whole day's shared quota.

Note: as of this writing, `llama-3.3-70b-versatile` and
`llama-3.1-8b-instant` (the models originally used here) are on
Groq's deprecation schedule (shutdown 08/16/26) — see
[console.groq.com/docs/deprecations](https://console.groq.com/docs/deprecations)
if you need to change models again in the future.
