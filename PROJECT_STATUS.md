# PROJECT STATUS — Reading & Exercise Library Overhaul

> **Living recovery document.** If a session is interrupted, start a new one and say
> **"resume the project."** Read this file top to bottom, then run the checks in
> [Session recovery protocol](#session-recovery-protocol) before changing anything.

---

## Project overview

| | |
|---|---|
| **Objective** | Audit, re-level, edit, de-duplicate and convert the whole reading/exercise library from PDF/DOCX into native HTML pages with audio, organized by CEFR level and topic. |
| **Site** | https://renangrossi.github.io/englishclasses/ |
| **Repo** | `/media/valusia/Documents/curso-ingles` (GitHub Pages, served from `/englishclasses/`) |
| **Entry point** | `exercises.html` → to become the levelled library hub |
| **Current phase** | Milestone 0 complete → Milestone 1 (content architecture) |
| **Overall completion** | ~8% (audit done; 0 of 98 source documents converted) |

### What this project is *not*
It is not a redesign of the grammar-lesson system. `levels/{level}/*.html` + `curriculum/{level}/*.json`
(71 lessons) are a **separate, mature, working system** and are out of scope except for
navigation links. See [Decisions](#decisions) D-2.

---

## Session recovery protocol

Run these before making changes:

```bash
cd /media/valusia/Documents/curso-ingles
git status --short && git branch --show-current
git log --oneline -8
python3 scripts/check_site_integrity.py        # must print "No errors."
```

Baseline at Milestone 0: **131 pages, 71 curriculum lessons, 0 errors, 51 warnings.**
Those 51 warnings are **pre-existing** in the grammar lessons (`repeated 'right' values`,
`typing item with neither 'answer' nor 'modelAnswer'`) and are *not* caused by this project.
Do not "fix" them as part of this work; log them and move on.

---

## Completed milestones

### Milestone 0 — Audit & inventory ✅
- **Date:** 2026-09-29
- **Branch:** `content/reading-library-audit` → merged to `main`
- **Commit:** `6e72706` (merge `593c1bd`)
- **Pushed:** yes · **Merged:** yes

**What was completed**
1. Inspected the repo and the deployed site's structure, design system, JS engine and audio system.
2. Established that the reading library (`cefr/texts/`, 117 files) is **PDF/DOCX only — zero HTML**.
3. Built a stdlib-only DOCX extractor and extracted **all 98 source documents (~70k words)**, then
   **read every one of them** and classified it. `.docx` is the extraction source of truth; `.pdf`
   is used only where no `.docx` exists (which was 1 file, `mind-games`, now deleted).
4. Produced the content map: `docs/reading-library-map.json` (98 entries, per-text decision + reason).
5. Produced the human-readable audit: `docs/content-audit.md`.
6. Confirmed audio is technically achievable end-to-end (see [Audio](#audio-architecture)).
7. Deleted `mind-games` (image-only PDF, no extractable content) per user instruction.

**Files created:** `PROJECT_STATUS.md`, `docs/reading-library-map.json`, `docs/content-audit.md`,
`scripts/extract_source_docs.py`
**Files modified:** `exercises.html` (removed the deleted `mind-games` card)
**Files deleted:** `cefr/texts/mind-games.pdf`
**Known issues:** none introduced; integrity check still clean.

---

## Current milestone

### Milestone 1 — Content architecture (IN PROGRESS)

**Goal:** lock the target structure and the page/audio pipeline, then prove it end-to-end on a
pilot text before converting at volume.

**Already completed**
- CEFR + topic taxonomy defined (below).
- Per-text level and topic recommendations recorded in `docs/reading-library-map.json`.
- Duplicate/overlap groups identified (16 MERGE entries across 8 merge targets).

**What remains**
- [ ] Write `scripts/build_reading_page.py` (reuses `scripts/site_chrome.py`).
- [ ] Write `scripts/generate_reading_audio.py` (edge-tts wrapper).
- [ ] Convert **one pilot text** end-to-end (HTML + exercises + audio) and validate.
- [ ] Restructure `exercises.html` into the levelled hub.

**Files being modified:** none yet in this milestone.

**Next exact actions:** see [NEXT SESSION](#next-session).

---

## Target architecture

### Content structure
```
reading/                              (new — the reading & listening library)
  index.html                          optional; exercises.html is the hub
  a1/<slug>.html   a2/…   b1/…   b2/…   c1/…   c2/…
assets/audio/reading/<level>/<slug>.mp3
```

`reading/{level}/{slug}.html` mirrors the existing `levels/{level}/{lesson}.html` convention.
Audio goes under `assets/audio/reading/` so it cannot collide with the 28 existing
`assets/audio/{level}/*.mp3` listening files belonging to the grammar lessons.

Each reading page pairs 1:1 with its audio file:
`reading/b1/nfl.html` ↔ `assets/audio/reading/b1/nfl.mp3`

### Topic taxonomy
`work` · `interviews` · `business` · `travel` · `everyday` · `food` · `sports` ·
`culture` · `tech` · `society` · `literature` · `review`

### Level distribution found by the audit

| Level | Source docs | Verdict |
|---|---|---|
| A1 | 1 | **Gap** — essentially no true-beginner reading material exists |
| A2 | 20 | adequate |
| B1 | 38 | over-represented; the library's centre of gravity |
| B2 | 22 | adequate |
| C1 | 15 | adequate |
| C2 | **0** | **Gap** — no C2 material; create only where genuinely justified |

Filling A1 (and a small, honest C2 set) requires **new authored content**, which must be
labelled as new — never presented as pre-existing. See requirement 19.

---

## Audio architecture

**Confirmed working this session.** The site's established tool is **edge-tts** (free, neural,
`en-US` voices), used for the existing 28 listening files — see commits `7f73dc8` and `f3da4e4`.

- No `pip`/`pipx` on this machine, but `python3 -m venv` works and bundles pip.
- `edge-tts 7.2.8` installed into a scratch venv; a synthesis test produced a valid
  MPEG layer III, 24 kHz mono mp3 — the same format as the existing files.
- `ffmpeg` is available for any concatenation/normalisation.
- **Per-level pacing convention already in use:** Pre-A1/A1 `-15%`, A2/B1 `-8%`, B2–C2 natural.
- **Voice convention already in use:** a roster of 8 `en-US` voices, 4 male / 4 female, with the
  voice's gender matched to a first-person or named narrator's gender.

**Conclusion: audio is achievable, so requirement 8 must be met, not deferred.**
The venv is in a scratch dir and is *not* committed; recreate it with the snippet in
[Reproducing the toolchain](#reproducing-the-toolchain).

### Audio applicability
Audio is required for **reading texts and dialogues only**. Pure grammar drills, answer keys
and discussion-prompt banks are not reading texts, so audio is `n/a` for them.

| Audio status | Count |
|---|---|
| `required` (must be generated) | 64 |
| `exists` (already has mp3, text unchanged) | 4 |
| `stale-on-edit` (has mp3, but text is being edited → **must regenerate**) | 2 |
| `n/a` (drill / answer key / discussion bank) | 28 |

The 2 `stale-on-edit` texts are `capetown` (4 mp3s) and `physical-education` (4 mp3s). Requirement
8.6/8.7 forbids leaving audio that no longer matches its text.

---

## Technical status

| Area | State |
|---|---|
| **Design system** | Understood, reuse as-is: `.lesson-card`, `.lesson-card__index`, `.lesson-card__actions`, `.btn--ghost`, `.btn--small`, `.grid`, `.card`, `.exercise-block` |
| **Page chrome** | `scripts/site_chrome.py` provides head/header/nav/search/footer verbatim; `REL` sets the path prefix |
| **Exercise engine** | `assets/js/exercises.js` (1841 lines). **No JS changes needed.** |
| **Exercise types available** | `multiple-choice`, `true-false`, `fill-blank`, `matching`, `ordering`, `correction`, `typing`, `reading-comprehension`, `vocabulary`, `writing` |
| **Audio player** | Existing pattern: `<audio controls preload="metadata">` inside a `reading-comprehension` block's `passage`, followed by `<details class="transcript-toggle">`. No JS. Degrades gracefully. |
| **HTML migration** | 0 / 98 source docs converted |
| **CSS** | No changes made or expected; reuse existing tokens |
| **JavaScript** | No changes made or expected |
| **Navigation** | `exercises.html` is currently a flat alphabetical grid of 117 "Open PDF" cards — to be restructured |
| **Responsive** | Inherited from existing chrome/CSS; must be re-verified per new page type |
| **Accessibility** | Inherited; keep heading order, `aria-hidden` on decorative indices, real `<audio controls>` |
| **Search index** | `scripts/build_search_index_sheets.py` + integrity check rule 3 — new pages must be added to the search index |
| **Validation** | `python3 scripts/check_site_integrity.py` — run before every commit |
| **Git** | Milestone 0 merged to `main`; working tree clean |
| **Deployment** | GitHub Pages from `main`. Absolute URLs must keep the `/englishclasses/` segment |

### Reproducing the toolchain
```bash
python3 -m venv /tmp/rl-venv && /tmp/rl-venv/bin/pip install edge-tts
/tmp/rl-venv/bin/edge-tts --voice en-US-JennyNeural --text "test" --write-media /tmp/t.mp3
python3 scripts/extract_source_docs.py /tmp/extracted   # re-extract all source docs
```

---

## Editorial rules (user-specified — apply to every conversion)

1. **DOCX over PDF.** Where a text has both, extract from the `.docx` and ignore the `.pdf`.
   *(The extractor must preserve `<w:noBreakHyphen/>`, or "risk-adjusted" silently becomes
   "riskadjusted" — this bug was found and fixed in Milestone 0.)*
2. **English character names.** All character names should be English names. Where the context
   genuinely demands otherwise (a named local figure in a text about a specific country),
   pick a randomized proper name appropriate to that context rather than keeping the original.
3. **American English throughout** (spelling, vocabulary, currency, dates, 12-hour clock),
   unless a British/other form is the actual teaching point.
4. **"Many Americans…", never "Americans always…"** — cultural tendencies, not stereotypes.
5. **Quality over quantity.** Merging or replacing a weak text beats preserving it for volume.
6. **Never present new content as pre-existing.** New texts are labelled as newly authored.

---

## Content status

The authoritative, per-text table is **`docs/reading-library-map.json`** (98 entries, each with
level, topic, genre, action, reason, audio requirement and status). It is machine-readable so
progress can be tracked and resumed. `docs/content-audit.md` is the human-readable view.

**Decision totals from the audit:**

| Action | Count | Meaning |
|---|---|---|
| KEEP | 17 | already good; convert as-is |
| EDIT | 33 | useful but needs correction |
| MERGE | 16 | overlaps another text (→ 8 merge targets) |
| CONVERT | 11 | drill/discussion → HTML exercise components |
| SPLIT | 8 | several unrelated materials in one file |
| REPLACE | 8 | new text more useful than repairing this one |
| DELETE | 5 | nothing worth migrating |
| **Total** | **98** | |

**Progress:** 0 IMPLEMENTED · 0 CONVERTED · 98 AUDITED

---

## Problems / decisions

### Decisions

- **D-1 — The reading library gets its own tree (`reading/{level}/`)**, rather than being folded
  into `levels/{level}/`. `levels/` is the grammar-lesson system driven by `curriculum/*.json`
  and its own builder; mixing reading pages into it would entangle two unrelated pipelines.
- **D-2 — `levels/` and `curriculum/` are out of scope.** 71 grammar lessons already work.
  Only their navigation links may change.
- **D-3 — Do not re-run `scripts/build_lesson.py` on an existing lesson.** The built pages contain
  enrichment their source JSON no longer holds, so rebuilding silently destroys content.
  A new builder (`build_reading_page.py`) will be written for reading pages instead.
- **D-4 — Reuse the existing audio+transcript pattern** (`<audio controls>` + `<details>` inside a
  `reading-comprehension` passage) rather than inventing a player. It needs no JS, works on
  mobile, and is already proven on 28 pages. Playback-speed controls are **not** added: requirement
  8 warns against over-engineering, and the browser's native audio UI already offers speed.
- **D-5 — Audio applies to reading texts and dialogues, not drills.** A gap-fill worksheet with no
  prose has nothing to narrate. Recorded as `audio: "n/a"` (28 documents).
- **D-6 — Edited texts with existing audio must have that audio regenerated** (`stale-on-edit`),
  never left mismatched.
- **D-7 — Keep the PDFs in the repo** as downloadable/printable companions, and stop treating them
  as the *only* way to reach the content. Requirement 13 forbids embedding PDFs as the
  experience; it does not require deleting printable worksheets a teacher may still use in class.
  Exception: files deleted outright by the audit.

### Open problems

- **P-1 — A1 and C2 gaps.** 1 A1 and 0 C2 source texts. A coherent progression needs new authored
  A1 material and a small, genuinely justified C2 set. Must be labelled as new content.
- **P-2 — Heavy non-American concentration.** A large share of the library is set in Brazil,
  or in South Africa / Romania / Thailand / Italy / Japan / Austria / Egypt, while the brief asks
  for an American-English, American-culture centre of gravity. Resolution: keep the genuinely
  good international texts as a *Travel & World* thread, and re-set the weak or list-shaped ones
  in US contexts — rather than deleting good material merely for being non-American.
- **P-3 — Two non-ASCII source filenames** (`cachaças`, `maringá`) and one with a literal `+`
  (`simple-past-+-present-continuous-+-future-*`). New slugs must be ASCII and hyphen-only.
- **P-4 — Several texts exist only to drill a tense** and read unnaturally as a result
  (`capetown`, `physical-education`, `say-speak-talk-tell-02`, `my-day-in-vienna-to-by-for`,
  `cybersecurity`). These need real editing, not relabelling — see requirement 6.
- **P-5 — Content defects requiring removal/replacement**, recorded with reasons in the audit:
  inappropriate slang in a family text (`santa-catarina`), a derogatory passage about developing
  nations (`formal-informal`), pseudo-history presented as scholarship (`egypt`), graphic content
  and blog register (`haiti`), vendor marketing copy (`animal-solutions`), a Portuguese-only file
  (`it-ptbr`), a defective duplicate verb list (`irregular-verbs-list`), and ephemeral news
  (`market-sumup`, `el-niño-2027`).
- **P-6 — The 51 pre-existing integrity warnings** in the grammar lessons are logged and
  deliberately untouched.

---

## NEXT SESSION

Do these in order. Commit, push and merge at the end of each numbered group.

1. **Write `scripts/build_reading_page.py`.**
   Import `scripts/site_chrome.py` for chrome; emit `reading/{level}/{slug}.html` with a
   `reading-comprehension` exercise-data block whose `passage` holds
   `<audio controls preload="metadata" src="../../assets/audio/reading/{level}/{slug}.mp3">`
   plus a `<details class="transcript-toggle">` transcript. `REL = "../../"`.
   Do **not** touch `scripts/build_lesson.py` (see D-3).

2. **Write `scripts/generate_reading_audio.py`.**
   edge-tts wrapper: input text → `assets/audio/reading/{level}/{slug}.mp3`, applying the
   established per-level rate (`-15%` Pre-A1/A1, `-8%` A2/B1, natural B2–C2) and the 8-voice
   `en-US` roster with narrator-gender matching. Split long texts into parts rather than
   producing one huge file.

3. **Pilot one text end-to-end and validate before scaling.**
   Use **`nfl`** (B1, 566w, `action: KEEP`, American sports/culture, needs no rewriting) so the
   pipeline is tested without editorial confounds. Produce the page, real comprehension/vocabulary
   exercises, and the audio. Then run:
   ```bash
   python3 scripts/check_site_integrity.py     # must stay at 0 errors
   ```
   Open the page and confirm the audio plays and the transcript toggles.
   **Commit + push + merge as Milestone 2a, and update this file.**

4. **Restructure `exercises.html` into the levelled hub** (requirement 18): A1 → A2 → B1 → B2 → C1 → C2,
   each level with a short description, the English it practices, its main topics, and links.
   Replace the flat 117-card alphabetical grid. Add new pages to the search index
   (`scripts/build_search_index_sheets.py`) so integrity-check rule 3 passes.

5. **Then convert at volume, level by level**, in this order: the 17 `KEEP` texts first (fastest,
   no editorial work), then `EDIT`, then `MERGE`/`SPLIT`, then `REPLACE`, and finally the
   new A1/C2 content for P-1. Update each entry's `status` in
   `docs/reading-library-map.json` as it lands, and commit per level.

6. **Always finish a milestone with:** update `PROJECT_STATUS.md` → run
   `check_site_integrity.py` → commit → push → merge → record the commit hash here.
