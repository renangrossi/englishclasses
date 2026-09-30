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
| **Current phase** | Milestones 0–3 complete → Milestone 4 (the `EDIT` texts) |
| **Overall completion** | ~30% (audit done; pipeline proven; 24 of 98 source documents converted into 26 pages; every `KEEP` text done; hub rebuilt as a CEFR progression) |

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

### Milestone 1 — Content architecture & pipeline ✅
- **Date:** 2026-09-30
- **Branch:** `content/reading-library-pipeline` → merged to `main`
- **Commit:** `6b61fe0` (merge `50cd3cb`)
- **Pushed:** yes · **Merged:** yes

**What was completed**
1. Locked the target structure (`reading/{level}/{slug}.html` + `assets/audio/reading/{level}/{slug}.mp3`)
   with `content/readings/{level}/{slug}.json` as the single source of truth for both.
2. Built the pipeline:
   - `scripts/reading_common.py` — shared paths, level pacing, voice roster, topic/provenance labels.
   - `scripts/build_reading_page.py` — renders a reading page via `site_chrome.py`.
   - `scripts/generate_reading_audio.py` — edge-tts narration with **content-based** staleness.
   - `scripts/build_search_index_readings.py` — keeps reading pages searchable.
   - `scripts/build_content_audit.py` — regenerates `docs/content-audit.md` from the map.
3. Proved the pipeline end-to-end on the pilot text `nfl` (B1): page + 4 exercise blocks
   (24 graded items) + 10-term vocabulary + 5 discussion prompts + 3:39 of narration.
4. **Zero new CSS and zero new JavaScript** — the page reuses `.reading-passage`,
   `.summary-list`, the site-wide `audio` rule and the existing exercise engine.

**Files created:** `scripts/reading_common.py`, `scripts/build_reading_page.py`,
`scripts/generate_reading_audio.py`, `scripts/build_search_index_readings.py`,
`scripts/build_content_audit.py`, `content/readings/b1/nfl.json`, `reading/b1/nfl.html`,
`assets/audio/reading/b1/nfl.mp3`, `assets/audio/reading/manifest.json`
**Files modified:** `docs/reading-library-map.json`, `docs/content-audit.md`,
`assets/data/search-index.json`, `PROJECT_STATUS.md`
**Known issues:** none; `check_site_integrity.py` reports 0 errors.

---

## Completed milestones 2 and 3

### Milestone 2 — Volume conversion: the `KEEP` texts & the hub ✅
- **Date:** 2026-09-30
- **Commit:** `7627ba4` (merge `819c85a`)
- **Branches:** `content/reading-a2-batch-1`, `content/reading-a2-batch-2`,
  `content/levelled-hub-and-deletions`, `feature/reading-print-to-pdf`,
  `feature/inline-vocabulary-tooltips`, `content/reading-b1-keep-batch` → all merged to `main`

**What was completed**
1. **17 texts converted** beyond the `nfl` pilot: 12 at A2 and 5 at B1, each with a built page,
   inline vocabulary tooltips, graded exercise blocks, discussion prompts and edge-tts narration.
2. **`exercises.html` rebuilt as a CEFR progression** (requirement 18), replacing the flat
   alphabetical "Open PDF" grid. One button per card; unconverted texts still link to their
   printable source and are labelled "Not yet converted" (decision D-7).
3. **Print / Save-as-PDF** on every reading page, replacing the generated PDF files.
4. **Inline vocabulary tooltips** (requirement 7, decision D-9): key words are bold in the
   passage and carry their definition on hover. The separate on-page Vocabulary section is gone;
   the definitions survive in a print-only glossary.
5. **The passage set as prose** rather than a tinted callout panel (decision D-8).
6. **The per-text provenance line removed from the page** (decision D-10).

**Current tally by level:** A2 12 · B1 6 · A1/B2/C1/C2 0.

### Milestone 3 — Finishing the `KEEP` texts ✅
- **Date:** 2026-09-30
- **Branches:** `content/reading-b2-keep-batch`, `content/reading-c1-keep-batch` → merged to `main`
- **Commits:** `923899e` (merge `989b408`), `98f0d0e` (merge recorded below)
- **Pushed:** yes · **Merged:** yes

**What was completed**
1. **The last 8 `KEEP` texts converted** — 5 at B2 and 3 at C1 — each with a built page,
   inline vocabulary tooltips, graded exercise blocks, discussion prompts and edge-tts narration.
   The `KEEP` action is now finished: **15 of 15 implemented**.
2. **B2:** `it-interview`, `sales-strategy`, `project-management-can-could-able-do-make`,
   `phrasal-verbs-01-bed-and-breakfast`, `phrasal-verbs-02-trip-abroad`.
3. **C1:** `attention-economy`, `technology-and-ethics`, `physiological-stressors`.
4. **`attention-economy`'s three old mp3 segments were retired**, not reused: they narrate an
   earlier wording, so the text was re-narrated as a single file and the segments were deleted
   from `cefr/texts/` (decision D-6). No `KEEP` text has ever matched its existing audio.
5. **Still zero new CSS and zero new JavaScript.** The `matching` blocks introduced in this
   batch use the engine's existing renderer.

**Current tally by level:** A2 12 · B1 6 · B2 5 · C1 3 · A1/C2 0.

**Two shape corrections found while building** (both would have failed silently in the browser,
so they are recorded in [The source JSON contract](#the-source-json-contract)):
- `matching` takes **one item holding a `pairs` array**, not one item per pair.
- `writing` blocks are ungraded textareas; the engine ignores `modelAnswer`. Extended
  written work belongs in `discussion`, which is what every other reading page does.

## Current milestone

### Milestone 4 — The `EDIT` texts (NOT STARTED)

**Goal:** work through the 27 remaining `EDIT` texts, which carry the real editorial load, then
the `MERGE`/`SPLIT` groups, then `REPLACE` and `CONVERT`.

**What remains**
1. The **27 remaining `EDIT`** texts (see the editorial rules).
2. The **15 `MERGE`** → merge targets, and the **8 remaining `SPLIT`** files.
3. The **8 remaining `REPLACE`** texts and the **11 `CONVERT`** drills.
4. The **5 `DELETE`** entries, to be confirmed and removed.
5. New A1 and C2 content for open problem P-1.

**Next exact actions:** see [NEXT SESSION](#next-session).

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
| **Audio player** | Native `<audio controls preload="metadata">` at the top of the reading section, with a download link as fallback. Gives play/pause, progress, elapsed/total time, keyboard access and the browser's own speed menu on desktop and mobile, with no JS to fail. The grammar lessons' listening blocks keep their `<details class="transcript-toggle">` pattern; a reading page shows the text itself, so it needs no transcript toggle. |
| **HTML migration** | 24 / 98 source docs converted → 26 reading pages (12 A2, 6 B1, 5 B2, 3 C1), each with narration |
| **CSS** | **No changes made.** Reading pages reuse `.reading-passage` (exercises.css), `.summary-list` (lessons.css) and the site-wide `audio` rule (components.css) |
| **JavaScript** | **No changes made.** `assets/js/exercises.js` renders the new pages unmodified |
| **Navigation** | `exercises.html` is currently a flat alphabetical grid of 117 "Open PDF" cards — to be restructured |
| **Responsive** | Inherited from existing chrome/CSS; must be re-verified per new page type |
| **Accessibility** | Inherited; keep heading order, `aria-hidden` on decorative indices, real `<audio controls>` |
| **Search index** | `scripts/build_search_index_sheets.py` + integrity check rule 3 — new pages must be added to the search index |
| **Validation** | `python3 scripts/check_site_integrity.py` — run before every commit |
| **Git** | Milestones 0 and 1 merged to `main`; working tree clean |
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
7. **Bold the key vocabulary inside the passage, with the meaning on hover.** Glossary words are
   marked with `.vocab-term` and carry `data-definition`; there is **no separate Vocabulary
   section** on the page (the definitions reappear only in the print-only glossary). The builder
   matches headwords to their inflected forms automatically — pin a `match` field on the
   vocabulary entry when auto-matching picks the wrong sense.
8. **Exercises must test meaning, not string-matching.** Do **not** write a question whose correct
   option is lifted verbatim from the passage — a student can then scan for matching words and
   answer without understanding anything. Paraphrase the question and the options, and scale how
   far by level:
   - **A1/A2** — reword with simple synonyms; one short inference at most.
   - **B1** — paraphrase throughout, plus questions that combine two facts.
   - **B2** — inference and implication; ask *why*, not just *what*.
   - **C1/C2** — interpretation: tone, attitude, what the writer implies but does not say.

   Keep the *explanation* quoting the text where that helps — the feedback after grading is
   exactly where the student should be pointed back to the wording.

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

**Progress:** 24 IMPLEMENTED · 74 NOT STARTED · 98 AUDITED — every `KEEP` text is done (15/15)

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
- **D-8 — The passage is set as prose, not as a callout box.** `.reading-passage` was a tinted
  panel with a gold rule down its left edge; a text a student reads for several minutes needs
  typography instead. It is now the serif display face at `--step-1`, line-height 1.75, in a
  62-character measure, with no background, border or panel. The print rule drops the frame too.
  No new class and no new JS — only the existing rule was rewritten, so every reading page and
  every future one inherits it.

- **D-9 — Key vocabulary is bold in the passage with the meaning on hover, and there is no
  separate Vocabulary section.** A word list sitting below the text is read once and forgotten;
  a definition attached to the word where it actually occurs is read at the moment it is needed.
  Glossary words carry `.vocab-term` + `data-definition`, and the builder matches a headword to
  its inflected forms automatically (pin `match` on the entry when auto-matching picks the wrong
  sense). Because hover does not exist on paper, the definitions come back as a **print-only
  glossary** (`.reading-glossary { display: none }` on screen, shown under `@media print`).
- **D-10 — The per-text provenance line is not printed on the page.** Pages used to end with
  "Adapted from the original course material." or similar. It is edit-history metadata, not
  something a student reading the text needs, and it undercut the material to no purpose.
  Each source JSON still records `provenance` (`as-published` / `edited` / `rewritten` /
  `merged` / `new`) and the audit still reports on it — requirement 6 is satisfied by the
  project record, not by a footnote on the page. `PROVENANCE_LABELS` was replaced by
  `VALID_PROVENANCE` in `scripts/reading_common.py`.

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

The pipeline is built and proven — **do not rebuild it.** Use it.

### The build loop (per text)

```bash
# 0. recreate the TTS venv once per machine/session
python3 -m venv /tmp/rl-venv && /tmp/rl-venv/bin/pip install edge-tts

# 1. author content/readings/{level}/{slug}.json   (the editorial work)
# 2. build the page
python3 scripts/build_reading_page.py {level}/{slug}
# 3. narrate it
python3 scripts/generate_reading_audio.py {level}/{slug} --tts /tmp/rl-venv/bin/edge-tts
# 4. make it searchable + refresh the audit view
python3 scripts/build_search_index_readings.py
python3 scripts/build_content_audit.py
# 5. validate — both must be clean before committing
python3 scripts/check_site_integrity.py          # must say "No errors."
python3 scripts/generate_reading_audio.py --check # must say "0 need audio"
```

Set each text's `status` to `IMPLEMENTED` in `docs/reading-library-map.json` as it lands, and
add a `page` field pointing at the built page (see the `nfl` entry as the worked example).

### The source JSON contract

Copy `content/readings/b1/nfl.json` as the template. Required: `id`, `level`, `slug`, `topic`,
`title`, `subtitle`, `description`, `source`, `provenance`, `passage` (array of paragraphs).
Optional: `vocabulary`, `exercises`, `discussion`, `narrator` (`"male"`/`"female"` only when the
text genuinely has a narrator of that gender), `audio.duration_label`, `audio.voice`, `audio.rate`.

**Exercise item shapes the engine actually implements** — these differ per type and getting them
wrong fails silently in the browser, so follow them exactly:

| Type | Item fields |
|---|---|
| `reading-comprehension`, `multiple-choice`, `vocabulary` | `id`, `prompt`, `options`, `answerIndex`, `explanation` |
| `true-false` | `id`, **`statement`**, `answer` (bool), `explanation` |
| `fill-blank` | `id`, `prompt` with `___` per blank, **`answers`** (one per blank), `options` (flat array for a single blank, array-of-arrays for several), `explanation` |
| `matching` | **one item** per block: `id`, **`pairs`** (an array of `{left, right}`), `explanation`. One item per pair renders nothing. |
| `true-false` explanation | begin it with "True —" or "False —" so the printed feedback stands alone |

`writing` blocks are **ungraded textareas**: the engine renders the prompt and a "Save my
answers" button, and ignores any `modelAnswer` you supply. Extended written work therefore
belongs in `discussion` — which is what every reading page does — not in a `writing` block.

### Work order

1. ~~**The `KEEP` texts**~~ — **done.** All 15 are implemented (Milestones 2 and 3).
   No `KEEP` text ever matched its existing audio: the old mp3s in `cefr/texts/` are split into
   2–4 parts narrating an earlier wording, so every one has been re-narrated as a single file
   and the superseded segments removed.
2. ~~**`exercises.html` → the levelled hub**~~ — **done** in Milestone 2. Regenerate it with
   `python3 scripts/build_exercises_hub.py` after any map change; implemented cards take their
   title and subtitle from the reading JSON, not from `card_title`/`card_desc`.
3. **The 27 remaining `EDIT` texts**, then the `MERGE`/`SPLIT` groups, then `REPLACE`, then `CONVERT`.
4. **The two `stale-on-edit` texts** (`capetown`, `physical-education`): once edited, their 4+4
   old mp3s in `cefr/texts/` must be replaced, not left behind.
5. **New A1 and C2 content** for P-1, labelled `provenance: "new"`.

**Audit the verdict as you go.** Two texts have now had their audited action changed on a close
read — `nfl` (KEEP→EDIT, factual errors) and `investigation-story` (KEEP→EDIT, a graphic and
abusive closing exchange that the audit had not flagged). The audit was written from a full read,
but a verdict is not binding: if a text turns out to need work the map does not record, change
the `action`, write the reason into the entry, and say so in the commit.

### Milestone discipline

Commit per coherent group (e.g. "the KEEP texts for A2 and B1"), not per file and not in one
giant commit. At each milestone: update `PROJECT_STATUS.md` → run both validators → commit →
push → merge → record the commit hash here.
