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
| **Repo** | `/media/valusia/Documents/course-english` (GitHub Pages, served from `/englishclasses/`) |
| **Entry point** | `exercises.html` → to become the levelled library hub |
| **Current phase** | 152 texts; the American History collection is complete, and the library has had a full audit pass (print, hierarchy, taxonomy, images, vocabulary, dialect) |
| **Overall completion** | Conversion **done**: all 98 source entries resolved — 87 built as pages, 11 deleted. **152 reading pages** (19 A1 / 24 A2 / 44 B1 / 30 B2 / 21 C1 / 14 C2), every one narrated and illustrated. Every level is populated; A1 and C2 were authored from scratch in milestones 7 and 8. |

### What this project is *not*
It is not a redesign of the grammar-lesson system. `levels/{level}/*.html` + `curriculum/{level}/*.json`
(71 lessons) are a **separate, mature, working system** and are out of scope except for
navigation links. See [Decisions](#decisions) D-2.

---

## Session recovery protocol

Run these before making changes:

```bash
cd /media/valusia/Documents/course-english
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
- **Commits:** `923899e` (merge `989b408`), `98f0d0e` (merge `a04e021`)
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

### Milestone 5 — Conversion complete ✅
- **Date:** 2026-09-30 · **Pushed:** yes · **Merged:** yes

Every `CONVERT`, `MERGE` and `SPLIT` entry is done, and the library is finished as a conversion
project. 86 pages, all narrated, no stale audio, `check_site_integrity.py` clean.

Three verdicts were changed during this milestone, each recorded in the map entry:
- `shadows-in-the-server-room` — the audit said split into chapters; the user asked for one
  story, so the length was solved by editing (2,407 words down to 1,362) instead.
- `text-interpretation-aesops-fables` — split into three themed pages rather than seven, since
  a fable is a 200-word form and a page holding one cannot carry a reading, audio and exercises.
- `soothing-texts` — split by level rather than theme, because its scenes were not written at
  one level.

The grammar drills were removed rather than converted, on the user's instruction that this area
is for reading texts: the grammar system already lives in `levels/` + `curriculum/` (D-2).

### Milestone 6 — A1 ✅ (C2 still open)
- **Date:** 2026-09-30 · **Pushed:** yes · **Merged:** yes

Six authored A1 readings, `provenance: "new"` — the first material on the site that was not
converted from a source document. They are built as one small curriculum rather than six
separate texts: the same cast (Emma, her husband Jack, her family in Ohio, the new neighbor
Sam) runs through all six, and each text deliberately recycles vocabulary from the ones before
it, so a beginner meets *get up*, *leave*, *still*, *busy*, *quiet*, *tired* and *together*
several times in different situations. One pinned voice (`audio.voice`) across all six, since
they share a narrator.

Editorial rules applied on top of the existing ones:

- **Frequency first.** Prefer the commoner word unless the topic needs the rarer one.
- **No cognate highlights** (rule 8), which bites hardest at A1: *apartment*, *coffee*, *park*,
  *restaurant*, *minute* are left plain. The highlights go to non-cognates (*tired*, *shelf*,
  *stove*, *store*, *nurse*, *upstairs*) and to fixed expressions (*Here you go*, *It's on me*,
  *that's all*, *Anything else?*, *my turn*, *that's okay*).
- **One real false friend**, taught deliberately: *parents* ≠ *parentes*. Its definition says so.
- **Americanisms where a student will actually meet them**: *server*, *the check*, *fries*,
  and the tip left on the table.
- **Exercise language is also A1.** Questions reword the passage instead of letting a student
  match a string: "What is Emma's job?" with "She makes and sells coffee", not "Where does she
  work?" with "coffee shop".

Texts run 120–152 words and 1:03–1:14 at the A1 rate of -15% (105–142 wpm, against ~158 at B2).

### Milestone 7 — A1 built out, and the library reordered ✅
- **Date:** 2026-09-30 · **Pushed:** yes · **Merged:** yes

Six more A1 texts, taking the level to twelve: shopping and money, getting around by train,
the weather through the year, being sick, the job itself, and a free Saturday. Same cast
throughout, and the recycling discipline holds — *busy*, *quiet*, *tired*, *near*, *early*,
*to get up*, *to leave*, *to stay*, *to wait* and *together* now recur across a dozen contexts.

**Ordering.** The hub used to sort alphabetically by title inside each level, which told a
student nothing. It now goes **level, then topic**, with a visible `.topic-group` heading above
each group, and inside a topic by an optional **`order`** field on the source JSON, falling back
to title. Only A1 declares `order` so far, because only A1 is a deliberate sequence — "A Tuesday"
recycles the five before it and has to follow them. Everything else is unchanged.

Note the consequence: topic grouping outranks the sequence, so "Lunch on Saturday" (food) and
"Taking the Train" (travel) sit in their own groups rather than at positions 4 and 8. That is
the intended trade — a student browsing by subject is better served than one reading straight
down the page.

### Milestone 8 — C2 opened, library grown, padding audited ✅
- **Date:** 2026-09-30 · **Pushed:** yes · **Merged:** yes

**C2 exists.** Six texts, each turning on implication, register or argument rather than on hard
vocabulary: professional indirectness, four registers of one redundancy announcement, what
survives translation, an argument that concedes more than it wins, how personality shifts
between languages, and how to read a scientific claim.

**Grown** to 108: A2 +2 (complaining politely, renting), C1 +2 (meetings, the night shift).

**Padding audited.** `scripts/check_padding.py` is new. It reports FILLER, REPEAT, DIVERSITY and
THIN, and DIVERSITY calibrates itself against this library's own bottom decile per length band
rather than against a number picked in advance. 15 of 108 flagged; two were real
(`b1/glamping`'s "a wide variety of", `b1/physical-education`'s three sentences opening "She
has"), and the rest were honest exceptions now documented in the script: "at the end of the
day" was literal both times, and the repetition in `b1/beers` is deliberate parallelism.

**Two faults of my own, found by widening the checks:**
1. **British spellings in nine files I authored**, against the American-English rule — apologise,
   behaviour, colour, organisation, judgement, scepticism, defence, programme, centre, cancelled,
   randomised, travelling. Corrected and re-recorded. "Specialist" is correct in both and was
   left alone.
2. **Adjacent vocabulary highlights** on 13 pages read as one long highlight, because the space
   between two spans sits outside both and the dotted rules stop and restart invisibly. Fixed in
   CSS (`.vocab-term + .vocab-term`) rather than by rewriting a dozen passages and re-recording
   them for a styling problem.

### Milestone 9 — Tag filter, and no topic left alone ✅
- **Date:** 2026-09-30 · **Pushed:** yes · **Merged:** yes

**The level jump strip reads the full name** — "A1 Beginner", not "A1". The code alone says
nothing to the student most likely to need it.

**Each level now carries a tag filter** in place of the three lines of prose that used to sit
there ("English you practice", "Topics", "Ready to read now"). Those lines described the level
but gave nobody a way to act on it. The chips combine **OR within a row and AND across rows**:
Travel + Food shows either, Travel + Passive voice shows travel texts practising the passive.
Each level filters independently, and with JavaScript off every card stays visible.

- **Subject tags** come from each text's `topic`.
- **Grammar tags** come from `scripts/tag_grammar.py`, which is new. It detects fourteen
  grammar points from unambiguous surface patterns and writes them to each source JSON as
  `grammar`. Thresholds scale with passage length, because a 130-word A1 text written entirely
  in the present simple otherwise fails a threshold set for a 900-word essay and ends up with no
  tags at all. Under-tagging is the intended failure: a missing tag costs a student one text, a
  wrong one costs them their trust in the filter. 3.8 tags per text; one text (`b1/cars-and-
  their-parts`, a parts list) legitimately has none.
- **A tag is only offered where at least two texts in that level carry it.** A filter that
  returns a single card is a worse answer than not being asked the question.

**No subject topic is left with one text**, which the rule above would otherwise have hidden.
Twelve singletons were resolved two ways:

- **Six retagged**, only where the new topic is at least as accurate: `detective-story` to
  literature (it is a crime story, like `investigation-story`), `robot-birds` to tech,
  `it-interview` and `sales-strategy` to work, `physiological-stressors` to society,
  `the-same-news-four-ways` to business.
- **Seven partner texts written**, where the topic genuinely deserved to exist at that level:
  A1 work / food / travel, A2 culture (Thanksgiving), B2 sports (the marathon wall), C1 tech
  (the cost of convenience), C2 culture (the accent you keep).

115 texts: 15 A1 / 18 A2 / 37 B1 / 24 B2 / 14 C1 / 7 C2.

Two incidental fixes: the hub lede still promised texts "still in their original documents",
which stopped being true when the backlog closed, so that sentence now only prints while a
backlog exists; and the truncation guard in `generate_reading_audio.py` caught a real partial
file (296 KB for 599 words) rather than letting it ship.

### Milestone 10 — The filter a student can read ✅
- **Date:** 2026-10-01 · **Branch:** `feat/filter-naming-and-grouping` → merged · **Pushed:** yes

**Grammar tags now carry the names a learner would recognise.** `Continuous aspect` was the
term a syntax class uses, and it was also dishonest: the detector fired on *she is walking* and
*they were walking* alike, so a text tagged only on past forms sat under a label that said
nothing about the past. It is now two detectors — **Present Continuous (-ing)** and **Past
Continuous (was / were -ing)** — and every other label reads the way a coursebook prints it:
Future (will / going to), Comparatives & Superlatives, Relative Clauses (who / which), Linking
Words, Question Forms, Conditionals (if). `scripts/tag_grammar.py --write` retagged all 115
texts; `grammar` keys in the source JSONs changed with it.

**Subject and Grammar are visibly two groups.** The label sits on its own line above its chips,
with space and one faint hairline between the groups (`.tag-row + .tag-row` in
`components.css`), because the two rows ask different questions and combine differently —
OR inside a group, AND between them. Chips are **alphabetical by label** within each group;
they had been ordered by an editorial topic sequence and by hit count, a ranking only the
person who built it can see.

The subject spread per level was audited and left alone: everyday / food / travel / work at
A1–A2, society from B2, business at C1–C2 — it already climbs the way it should.

### Milestone 11 — Illustrating the library ✅
- **Date:** 2026-10-01 · **Branches:** `content/illustrate-the-library`,
  `content/illustrate-b1`, `content/illustrate-b2-c1-c2` → all merged to `main` · **Pushed:** yes

**Where the pictures come from.** `/media/amaterasu/Wallpapers` — a local gallery of about
1,100 museum-grade scans of paintings and prints, with two curation notes in it
(`01a painting-taste-analysis.md`, `01b painters-by-region-and-subject.md`). **The gallery is
the first place to look**; Wikimedia Commons (`scripts/fetch_public_domain_image.py`) is only
for what it cannot answer. `scripts/import_local_artwork.py` is new and does the whole job:
resizes to a web size, writes `assets/img/reading/{level}/{slug}/NN.jpg`, and adds the entry to
the text's `images` array with the gallery filename recorded as `source`.
`scripts/build_image_credits.py` regenerates the credits table in `docs/image-credits.md` from
those `source` fields, between the `<!-- gallery:start -->` markers.

**Rules being followed:**
- A picture goes **inside** the text, at a turn in it — a change of scene, subject or
  argument — never as a cover at the top. One image for a short text, two for 8–20 paragraphs,
  three for the long dialogue pages.
- It has to **say something about the passage**. The most beautiful painting in the gallery is
  the wrong one if the text is about something else.
- **Only work old enough to be out of copyright.** The gallery also holds living and recent
  artists (Terpning, Rutkowski, Gurney, Künstler, Cuneo, Stobart, Maggiori, the Stuart Brown
  military set, the LOTR and game illustration) — none of that may be published.
- Every image gets an `alt` that describes the picture, and a caption in the form
  `*Title* — Artist, year.` (`build_reading_page.py` turns the asterisks into `<em>`; a year is
  only printed when it is actually known, never guessed.)
- **Verify before committing a choice.** A filename is not a picture: build a contact sheet
  (`magick montage -label '%f' … -tile 4x -geometry 300x300+6+6`) of the candidates and look at
  it. Several first choices were wrong — `peder-mork-monsted-going-to-market-1911` is a quiet
  river, not a market.

**Done: 144 images across all six levels — 111 of the 115 texts now carry artwork** (A1 16,
A2 29, B1 53, B2 24, C1 14, C2 8, plus the 12 images already on the pages illustrated earlier).

**Four texts are deliberately bare**, because the gallery holds nothing that genuinely speaks to
them and a decorative picture would only push the reading down the screen:
`b1/cars-and-their-parts` (a parts list, no narrative), `b1/coffee-and-it`,
`b2/phrasal-verbs-01-bed-and-breakfast` (a phrasal-verb drill) and `c1/physiological-stressors`.
If they are ever illustrated it should be from Commons, not by forcing a painting to fit.

Two subjects were refused on grounds other than fit: classical nudes (Poynter's
*A Visit to Aesculapius*, Siemiradzki's *Conversation by the Spring*) — the site is used by
children, and there are plenty of other pictures.

**The loop per batch:**
```bash
python3 scripts/show_passages.py b1/            # title, subtitle and each paragraph opening
# choose images, check them on a contact sheet, write a plan JSON
python3 scripts/import_local_artwork.py --plan plan-b1.json
for f in content/readings/b1/*.json; do python3 scripts/build_reading_page.py b1/$(basename $f .json); done
python3 scripts/build_image_credits.py && python3 scripts/check_site_integrity.py
```

### Milestone 12 — American History collection ✅
- **Date:** 2026-10-01
- **Branches:** `content/american-history` (A1, A2, B1), `content/american-history-b2`,
  `content/american-history-c1`, `content/american-history-c2` — each merged to `main` as it was finished.
- **Pushed:** yes · **Merged:** yes

A new collection of readings on the history of the United States, A1 to C2, authored for this
site. It is English practice told through history, not a history course: every text opens on a
scene rather than a birth date, and the language is held to its CEFR level while the subject is
allowed to be serious.

**All 37 texts:**
- **A1 (4):** `george-washington`, `abraham-lincoln`, `statue-of-liberty`, `the-american-flag`
- **A2 (6):** `declaration-of-independence`, `boston-tea-party`, `lewis-and-clark-west`,
  `sacagawea`, `california-gold-rush`, `oregon-trail`
- **B1 (7):** `louisiana-purchase`, `lewis-and-clark-unknown`, `harriet-tubman`,
  `frederick-douglass`, `lincoln-and-the-civil-war`, `transcontinental-railroad`,
  **`american-flag-symbols`** (the visual centrepiece: nine full-width flag plates inside the text)
- **B2 (6):** `trail-of-tears`, `civil-war-nation-divided`, `reconstruction`,
  `great-depression`, `fdr-new-deal`, `jackie-robinson`
- **C1 (7):** `rosa-parks`, `martin-luther-king`, `malcolm-x`, `women-win-the-vote`,
  `the-space-race`, `apollo-11`, `watergate`
- **C2 (7):** `manifest-destiny`, `the-west-was-not-empty`, `slavery-and-the-american-economy`,
  `reconstruction-revolution`, `the-american-dream`, `immigration-and-modern-america`,
  **`what-makes-an-american-hero`** (the closing text: it turns on the collection itself and
  asks what the hero template leaves out)

**What C2 does differently.** The lower levels narrate; C2 argues. Each text follows the house
C2 shape already set by `the-case-against-plain-english`: 8–9 paragraphs, a claim, two or three
qualifications, a concession that costs something, and a close that narrows the claim rather
than widening it. The exercise set is the C2 one — reading-comprehension, a `matching` item that
maps the *shape* of the argument, and vocabulary — with a 300-word writing task last in the
discussion. Where scholars genuinely disagree (the economics of slavery), the text says so and
sets out the best objection rather than picking a side.

**How these are built** (same pipeline, nothing new to invent):
```bash
python3 -m venv /tmp/rl-venv && /tmp/rl-venv/bin/pip install edge-tts   # once per machine
# 1. author content/readings/{level}/{slug}.json  — topic: "history", order: 100+
# 2. images: local gallery first, Commons only for what it cannot answer
python3 scripts/import_local_artwork.py --plan plan.json
python3 scripts/add_commons_image.py --plan plan.json     # PD as-is, CC BY/BY-SA with a credit, NC/ND refused
# 3. build + narrate + finish
python3 scripts/build_reading_page.py {level}/{slug}
python3 scripts/generate_reading_audio.py {level}/{slug} --tts /tmp/rl-venv/bin/edge-tts
python3 scripts/finish_reading_batch.py     # durations, indexes, hub, audit, validation
python3 scripts/tag_grammar.py --write     # grammar filter tags (NOT run by finish_reading_batch)
python3 scripts/build_image_credits.py     # image credits   (NOT run by finish_reading_batch)
python3 scripts/stamp_asset_versions.py    # cache-bust css/js (run after ANY change under assets/)
```
Those last three are easy to forget: `finish_reading_batch.py` does not call any of them, so a batch
that skips them ships texts missing from the grammar filter and images missing from the credits
file. Both are idempotent and derived from the JSON, so running them is always safe.
`scripts/show_passages.py {level}/` prints paragraph openings when placing images.

**Rules this collection follows, and the next session must keep:**
- `topic: "history"` → the Subject chip reads **American History** (`reading_common.TOPIC_LABELS`),
  sorted after Culture on the hub. No new filter system, no counters, no Text Type.
- `order: 100+` keeps the collection after the existing texts inside its topic group.
- Images go **inside** the text at a turn in it. `"wide": true` on an image gives it the full
  measure — for flags, maps and anything read for detail.
- Captions are `*Title* — Artist, year.`; every image has a real `alt`.
- **Facts are checked before they are written**, and where the popular story is wrong the text
  says so: Sacagawea was not a guide; attacks on the Oregon Trail were rare and cholera was not;
  Join or Die was a newspaper woodcut, not a flag; the Betsy Ross attribution is family tradition
  from 1870; the surviving Bennington flag is probably nineteenth-century. Nothing is invented —
  no dates, quotations, attributions or causal claims.
- The uncomfortable parts stay in: Washington's three hundred enslaved people, Jefferson writing
  that all men are equal while owning people, the eighty per cent fall in the Native Californian
  population, the Chinese workers missing from the Promontory photograph.
- Each level batch is committed, pushed and merged on its own.

### Milestone 13 — Site-wide audit and overhaul pass ✅
- **Date:** 2026-10-01
- **Branch:** `chore/library-overhaul-pass` → merged to `main`

A full audit-and-fix pass over the library, driven by a brief that asked for root-cause fixes
rather than per-page patches. Everything below was fixed in the generator, the shared CSS or the
source data, never in a built page.

**Print / Save as PDF — rebuilt.** New `assets/css/reading-print.css`, scoped to
`body.reading-page` (set via `site_chrome.header(body_class=…)`) so grammar lessons, which print
through `booklet-print.css`, inherit none of it. It gives A4 with 18/17/20mm margins, turns the
dark banner into a title block (level · topic, title, subtitle, rule), drops every piece of
interactive furniture *and* the exercises and discussion, binds each figure to its caption with
`break-inside: avoid`, caps plate heights in millimetres, sets the glossary in two columns and
prints a source line with the page URL. The exercises are not lost: each block already prints
itself through the overlay in `exercises.js`, with its own document header, which is a better
worksheet than appending them to the handout ever was. Verified by rendering real PDFs at A1,
A2, B1 (the nine-plate flag text), B2 and C2.

**Page hierarchy.** The banner said "The Text" in display type and the real title arrived a
screen later. The title and subtitle are now the banner's content and the page's only `<h1>`;
the reading section opens on the audio and the prose under a `Reading` label that is a real
`<h2>` set as an eyebrow.

**Key Vocabulary is visible again.** It had been hidden on screen on the argument that the hover
tooltip replaced it — which is true only for a reader using a mouse. Every highlight now carries
`aria-describedby` pointing at its entry, so a screen reader can reach the definitions at all.

**Taxonomy.** `culture` was labelled "American Culture", so a Japanese dog, a Romanian valley and
a festival in Fukushima all filed themselves under American Culture. Labels fixed; the key
`history` renamed to `american-history` so a key that names a region says so; `world-history` and
`science` added; seven texts refiled.

**Images.** Three were replaced because they contradicted their own text — grapes over a text
about sugarcane, Dordrecht over a text about Denver, an Edo temple over a 1930s Tokyo station —
and four analogues were re-captioned so they stop reading as photographs of their subject. The
schema gained `relation` (`depicts` | `analogue`), and `check_content.py` warns when an analogue
carries a bare caption.

**Two real bugs found and fixed in the tooling.**
`add_commons_image.py` and `import_local_artwork.py` both named new files `len(images)+1`, which
silently overwrote an existing picture whenever one had been removed from a text's set. Both now
take the next free number. And `*italics*` were converted in captions but not in passages, so six
texts printed literal asterisks around case names; the conversion now runs on passages too, and
the narrator no longer reads the asterisks.

**Three new checkers**, because the gap was that nothing validated the source data:
`check_content.py` (schema, vocabulary that never matches its own passage, image files, alt text,
exercise ids), `check_vocabulary.py` (Portuguese-aware: transparent cognates, unglossed false
friends, size against the level) and `check_dialect.py` (American/British spelling, with `--fix`).
`content/readings/SCHEMA.md` documents the data and the editorial rules.

**Vocabulary.** The matcher's inflection table was too thin — `built`, `oxen`, `acquitted`,
`court-martialled`, `formidably`, `bureaux` all failed to match their own passages. Fixed, plus
six semantic mismatches corrected in the content: 17 unmatched headwords down to 4. Nine verified
false friends added in house style (`"normal, usual — careful: it is not an insult"`).

**Dialect.** The library was roughly half British: 255 strings across 93 texts normalised to
American spelling, with `hawker centre` and `Labour Party` protected. Word choice
(`rubbish`/`trash`, `flat`/`apartment`) was deliberately left alone and reported.

**Narration pacing — a correction.** An attempt was made to lengthen the pause between
paragraphs. It does not work, and the finding is worth keeping so nobody tries it again.

edge-tts takes plain text and builds its own SSML, so there is no `<break>` to ask for. Seven
separators were measured against a real three-paragraph passage — a line holding a full stop,
three such lines, an ellipsis, an em dash, a row of commas, four blank lines, and the plain
paragraph break. **All seven produced identical timing**: the same gaps to the hundredth of a
second and the same total duration (71.8s). The service discards punctuation-only lines. Writing
`(pause)` does change it, by reading the word out loud.

A short artificial sample *does* respond — two one-sentence paragraphs gave 0.43s plain and 1.03s
with dot lines — which is exactly how this was got wrong the first time. Real paragraphs do not
behave that way: the service already inserts about **0.97s** at a paragraph boundary in long-form
text, measured across every level, and nothing in the text moves it.

So the library already has a one-second pause between paragraphs, and always did. `PARAGRAPH_BREAK`
is back to a plain blank line, with the measurements recorded next to it. Going beyond ~1s means
editing the audio after the fact: ask edge-tts for `--write-subtitles`, locate the paragraph
boundaries in the word timings, and splice silence in with ffmpeg. That is a real feature, not a
separator.

The 46 files re-recorded in this pass were rendered from text differing only by characters the
service discards, so they are byte-for-byte what the reverted text produces; only the manifest
needed correcting. The library has one pause length, not two.

### Milestone 14 — What was left after that

1. **P-2, the geography balance** — travel was the largest topic in B1. Superseded by the
   American History collection, which overshot: see P-7 below.
2. **Depth at C1 and C2.** The American History collection answered this: C1 went from 14 to 21
   and C2 from 7 to 14, against B1's 44. The top of the library is no longer thin.
3. ~~102 analogue images with a bare caption.~~ CLOSED by the caption pass (`9f2d368`): every
   gallery caption now says something about its picture. `check_content.py --warnings` reports
   nothing across all 152 sources, so the number this item was tracking is zero.
4. ~~Glossary sizes and transparent cognates.~~ CLOSED by milestone 15.
5. ~~Headwords taught in exercises but absent from their passage.~~ CLOSED by milestone 15: four
   of the five were inflections an exact-match search had missed.

### Milestone 15 — The vocabulary, dialect and padding backlog ✅

Three of the four items above were editorial backlogs the tools had reported in bulk and nobody
had worked through. Working through them showed that most of each number was the tool's, not the
library's, so the tools were corrected in the same pass. **Where a count was real it was fixed;
where the measure was wrong the measure was fixed; where a flag was a feature the text now says
so, with the reason, in its own source.**

**Dialect — one variety of English, finally.** `check_dialect.py --fix` had never been run over
the image captions and alt text added in the illustration pass: 34 strings across 30 texts
(*colour*, *centre*, *metres*, *grey*, *organising*). None was in a passage, so no narration
changed. The word-choice list the script only ever reports was mostly false positives — it
matches `tap` inside *tapes*, `lift` the verb, `flat` the adjective, `queue` meaning a backlog —
so the 23 genuine Britishisms were fixed by hand (*petrol*→gasoline, *rubbish*→trash,
*pavement*→sidewalk, *lift*→elevator, *timetable*→schedule, *flat*→apartment, *queue*→line,
*autumn*→fall, *holiday*→vacation, *trousers*→pants, *primary school*→elementary school) under a
stated rule: American where the text is set in the US or nowhere in particular; the British word
kept where the text is set in Britain or the Commonwealth (`arriving-in-johannesburg`,
`capetown`), where the word **is** the subject (the queueing joke in `what-doesnt-translate`, the
explicit "American X / British Y" glossary pairs), and where American English uses it too
(*autumn*, and *holiday* of a public holiday — `bank holiday` is the historical term and stays).

**Orphan headwords — one of five was real.** `soma-nomaoi`'s matching exercise asked for
*horagai* and the passage said "conch shells" without ever naming them; the passage now names
them. The other four were inflections an exact-match search could not see: "struck down" for
*strikes down*, "earning its keep" for *earns its keep*, "seceding" for *to secede*, "held public
office" for *to hold office*. The original note's four were the same mistake.

**Glossaries — 193 cognates, 153 false friends, 87 oversized, all resolved.**

- *The cognate rule was over-firing.* It read the ENDING, so a Latinate suffix over an opaque core
  passed as transparent: *unbearable*, *a constable*, *timetable*, *reliability*, *unemployment*.
  Worse, four of its own suggestions were false friends — *relative* is parente not relativo,
  *tentative* is hesitant, *formidable* is fearsome where formidável is wonderful,
  *authoritative* is not autoritário — so the tool was recommending the deletion of the most
  valuable entries on the page. `NOT_TRANSPARENT` is now consulted first, 100-odd words verified
  by hand against Brazilian Portuguese were added to `TRANSPARENT`, and every remaining flag comes
  from a checked list rather than a suffix. **140 entries dropped; 0 left.**
- *The false friends were real and are now glossed.* 152 added in the house style — the meaning,
  then `careful:` and the trap. Four were declined with reasons: "considerably stranger" is the
  comparative of *strange*, and three were already covered by a better entry (`housing policy`,
  `to push back`) or occur only in a section heading the builder does not highlight.
- *The size band was absolute, and that was wrong at both ends.* A 1,075-word C1 text with 17
  entries is a **sparse** glossary — one word in sixty — and was flagged, while a 120-word A1 text
  with 13 was flagged by the same rule for something entirely different. The ceiling now grows
  with the passage (3 entries per 100 words, never below the level's own figure, never past 2.5×
  it, because a list of forty is unreadable however long the text). That cleared 40 of the 87.
  26 texts whose glossary **is** the lesson — the A1 naming set, the phrasal-verb lessons,
  `a-day-in-the-house` ("the vocabulary of every room", says its own subtitle) — now declare
  `lexicalSet` with the reason. The remaining 25 were trimmed by hand, keeping false friends,
  phrasal verbs and the terms a text turns on, and cutting the level-obvious and the incidental.
  Five texts that would have dropped below their level's floor got words that earn the line
  instead — *to drift into*, *on the grounds that*, *a wing* of a movement, *to carry* of a vote —
  rather than keeping a cognate to make up the number.

**Padding — the count was 20, the defects were two.** Reading all 20 settled it:

- *DIVERSITY flags the bottom tenth of each length band.* It is a ranking, not a defect count: it
  can never reach zero, and clearing one text only promotes the next. Measured and confirmed —
  after the fix below, the flag count stayed at 17 with different texts in it. The summary now
  tallies defects and this reading list separately, because "20 flagged" read as twenty faults.
- *It was measuring the format, not the prose.* Four of the 17 were dialogues flagged for naming
  their speakers on every line: *receptionist* ×15, *clerk* ×14, *detective* ×14, *manager* ×10.
  Speaker labels are now stripped before the ratio is taken, using the same convention the page
  builder uses, so the signal reads the writing. The rest were a text's own unavoidable subject
  word — *flag* ×14, *beer* ×13, *coffee* ×10, *English* ×10 — or character names in a narrative.
- *One real defect, fixed.* `martin-luther-king` had three sentences in a row opening "He was",
  which is a tic rather than a rhythm; the third is now "At thirty-nine he had been…".
- *Three flags were features and now say so.* `dream-bistro` and `rs-japan` use "at the end of the
  day" literally — cleaning up after a shift, and the low gold light across the pampas — and
  `beers`'s three "Anything called…" sentences are deliberate parallelism carrying a rule of
  thumb. Each records a `paddingNote` with its reason, so the exception stays arguable instead of
  being re-reported forever or silently dropped from the rule.

Every validator is clean: `check_content` 152 sources, `check_site_integrity` 283 pages and 71
curriculum lessons, 0 stale audio, 0 cognates, 0 oversized glossaries, 0 padding defects,
0 dialect normalisations outstanding. 18 texts were re-narrated.

### Milestone 16 — The hub reaches the verb list, and the sources are retired ✅
- **Date:** 2026-10-09
- **Branches:** `feat/hub-irregular-verbs-button` (merge `1b23c80`), `chore/retire-converted-sources`
  → merged to `main`

**An Irregular Verbs button on the library hub.** The irregular verb list was reachable from
`extras.html` and `manoelito.html` but not from `exercises.html`, which is where a student
looking for drills lands. The button went into `scripts/build_exercises_hub.py`, not into the
page: `exercises.html` is generated, so a hand-edit would have been wiped by the next hub
rebuild. The untouched generator was run and diffed against the committed page first, to prove
the rebuild would sweep nothing else in; the resulting change to `exercises.html` is one line.
Zero new CSS. The wrapper borrows `.hero__actions` — the flex row `index.html` and `progress.html`
already use for buttons under a dark banner — because the only `.page-header__actions` margin
rule is scoped to `.page-header--slim` and this banner is the full one, so the button would
otherwise have sat flush under the lede. Inside `.page-header` a plain `.btn--ghost` is already
corrected for the dark background, and the list icon is the one `manoelito.html` and the `cefr`
pages use.

**The converted source documents are gone — 90 MB.** All 156 `.docx` and `.pdf` files in
`cefr/texts/` were deleted. Conversion and illustration are both finished, so nothing read them
any more, and that was checked rather than assumed: no page hyperlinks one, no `url` in
`worker/course-catalog.json` points inside the folder, and `build_content_audit.py` only names
the path in the prose it generates — it builds from `docs/reading-library-map.json` and still
regenerates byte-identically. The six `.mp3` source recordings went in the same pass — the
readings they belonged to carry their own edge-tts narration under `assets/audio/reading/`, and
nothing served the originals — so `cefr/texts/` is gone entirely.
`docs/reading-library-map.json` keeps every source filename as provenance, which is now the only
record outside git history that those documents existed.

**Four orphans and a worksheet the AI teacher was offering twice.** Beyond `cefr/texts/`, six
files in the grammar-lesson folders were dead. `b-present-perfect-continuous-copy.docx` is
referenced nowhere. `future-perfect-and-future-continuous.pdf` looked referenced but was not —
the only match is a section anchor of the same name in `levels/b2/test-yourself.html`. The other
four are the two A2 worksheets `curriculum/index.json` already records as resolved duplicates:
`r-can-could-may` merged into `g-can-could-may`, and `f-past-simple-and-continuous` into
`p-simple-past-vs.-past-continuous`. Both merge targets are on disk and in the catalog, but the
superseded pair was still being served — the catalog listed "Can, Could, May" twice with
identical titles and aliases — so those two `resources` entries went with the files.

**What was deliberately kept.** 159 documents remain, 122 MB, and every one earns its place: 90
are live downloads linked from `levels/*.html` and `simulated-exams.html`, and the other 69 are
the editable `.docx` masters beside those linked PDFs. The grammar-lesson system is out of scope
(D-2) and a teacher needs its sources, so none of it was touched. Deleting a master whose PDF is
a live download is a separate decision and was left to the user.

**Housekeeping in the same pass.** 118 local branches, every one already merged into `main`,
were deleted — the merge commits still name each branch, so nothing is lost — leaving `main`
alone. `.claude/worktrees/` held 17 orphaned agent worktrees, 6.0 GB of full repo copies that
`git worktree list` no longer knew about; all 17 were clean, with nothing uncommitted and no
commits outside `main`, and were removed. Roughly 180 branches still exist on `origin`; deleting
those is a separate, outward-facing call and was left to the user.

Both gates clean afterwards — `check_site_integrity` 283 pages and 71 curriculum lessons,
`check_content` 152 sources — plus a sweep of every `href`/`src` ending in `.docx` or `.pdf`
across every page and every `url` in the worker catalog: 0 broken references.

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
| **HTML migration** | **Complete.** 98 / 98 source entries resolved → 86 reading pages (15 A2, 37 B1, 23 B2, 11 C1), each with narration. Fewer pages than entries because merges combine sources and splits divide them |
| **CSS** | Reading pages reuse `.summary-list` (lessons.css) and the site-wide `audio` rule (components.css). `.reading-passage` in exercises.css has been rewritten twice on purpose — see decisions D-8 and D-11. No other CSS has been touched |
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
`extract_source_docs.py` and `extract_source_images.py` are kept for the record and no longer
have inputs: the `.docx` and `.pdf` in `cefr/texts/` were deleted in milestone 16. Recover them
from git history before `6f1e2bb` if either tool is ever needed again.

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
8. **Do not highlight what a Portuguese speaker already reads for free.** The students are
   Brazilian, and English is full of Latinate words whose Portuguese cousin is obvious on sight
   — *attribution/atribuição*, *constitutional/constitucional*, *irony/ironia*,
   *extortion/extorsão*, *inscription/inscrição*. A highlight spent on one of those teaches
   nothing and trains the student to ignore the highlighting. Spend them instead on:
   - **idioms and fixed expressions** — *the right call*, *beside the point*, *urgency is the tell*;
   - **phrasal verbs**, which are the hardest thing in English for a Romance-language speaker
     and have no cognate to fall back on — *to run out*, *to catch someone out*, *to put off*;
   - **short Germanic words** with no Latin cousin — *grip*, *stiff*, *till*, *shore*, *tell*;
   - **false friends**, which are worth a highlight precisely because the cognate misleads:
     *to appreciate* (to rise in value, not *apreciar*), *prefecture* (a region, not a
     *prefeitura*), *authoritative* (not *autoritário*), an *implement* (a tool, not
     *implementar*), *liable*, *to insure*.

   The suffix families that almost always signal a free ride: `-tion`, `-sion`, `-ity`, `-ous`,
   `-ive`, `-ance`, `-ence`, `-ent`, `-ant`, `-able`, `-ible`, `-ic`, `-al`, `-ate`, `-ure`,
   `-ism`, `-ist`, `-or`. A single word ending that way is transparent unless it is a false
   friend. A *multi-word* entry is never excluded by this rule — an idiom built from easy words
   is still opaque.

9. **Exercises must test meaning, not string-matching.** Do **not** write a question whose correct
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

**Progress:** 87 IMPLEMENTED · 11 COMPLETE (deleted) · 0 NOT STARTED · 98 AUDITED

Every action is finished: **KEEP** 15, **EDIT** 31, **REPLACE** 12, **MERGE** 15, **CONVERT** 8,
**SPLIT** 6, **DELETE** 11. Nothing in `cefr/texts/` was awaiting conversion, and as of
milestone 16 the folder is gone: its 156 source documents and six `.mp3` recordings are deleted.

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

- **D-11 — The passage is set as book typography: indented paragraphs and a drop cap.**
  Requested by the user. Each new paragraph of running prose takes a 1.5em first-line indent;
  the first paragraph of the text, the first paragraph of a section, and every dialogue turn
  stay flush, because a speaker's name already marks where a turn begins and indenting turns
  makes a conversation look like a misprint. The opening paragraph carries a drop cap over
  three lines with its first line in small capitals — the newspaper convention. Two supporting
  details matter and are easy to lose:
  - **The builder classifies each paragraph**, so a text that mixes prose and dialogue (such as
    `project-management-can-could-able-do-make`, a prose frame around a dialogue) comes out
    right with nothing tagged by hand. The classes are `reading-passage__lead`,
    `__lead--short`, `__heading`, `__opener` and `__turn`; `SPEAKER_RE` in
    `build_reading_page.py` is what detects a turn.
  - **A short opening paragraph gets a two-line cap** (`__lead--short`, under 200 characters).
    A three-line cap on a two-line paragraph overhangs whatever follows it. Section headings
    and dialogue turns also carry `clear: left` as a second guard.

  Also added, as classic text settings that cost nothing where unsupported: common ligatures,
  old-style figures (numerals that sit on the baseline rather than standing at cap height),
  and `text-wrap: pretty` for orphan control. Justified text with automatic hyphenation was
  **considered and not applied** — at a 62-character measure it opens rivers of white space,
  and ragged-right reads better on a phone.

- **D-12 — The text's title sits above the text, not in the banner.** Requested by the user.
  The banner used to carry the title and subtitle, which put them a navigation bar and a
  section heading away from the passage they name. The banner now holds the generic heading
  (“The Text”, as `.page-header__label`) and the instruction line; the reading section opens
  with the text's own title and subtitle, immediately above the audio and the prose. The title
  is still the page's only `<h1>` — it moved down to the content it names, which is a better
  document outline than a banner heading followed by an unrelated section heading. Nothing
  downstream broke: `<title>` is passed separately to `site_chrome.head()`, the breadcrumb is
  built from the title, and the search index reads the source JSON rather than the HTML.

  The **running time was removed** from the instruction line at the same time. It is not lost:
  the `<audio>` element shows it (`0:00 / 2:44`) as soon as metadata loads, so the printed copy
  was duplicate furniture. `audio.duration_label` is still recorded in every source JSON and
  still verified by `finish_reading_batch.py`.

  Two things that had to be handled and would be easy to reintroduce:
  - The instruction line demonstrates a highlighted word, and it now does that on the **dark**
    banner. The accent red used on white is far too dark there, so `.page-header__lede
    .vocab-term` overrides the colour.
  - In print the instruction line is hidden (it is about audio and hover, neither of which
    exists on paper) but the generic heading is **kept**, otherwise the banner prints as an
    empty navy block. The rule is scoped with `.page-header__label + .page-header__lede` so
    that other pages, where the lede is the page's real description, still print theirs.

### Open problems

- ~~**P-1** — A1 and C2 gaps.~~ CLOSED. Every CEFR level now has texts:
  12 A1 / 17 A2 / 37 B1 / 23 B2 / 13 C1 / 6 C2 = **108 pages**, all narrated.

- **P-2 — Non-American concentration.** OPEN. Travel is still the largest topic at 17 of 86, and
  much of the library is set in Brazil, South Africa, Romania, Thailand, Italy, Japan, Austria
  and Egypt. The agreed resolution stands: keep the good international texts as a *Travel &
  World* thread and re-set weak ones in US contexts — do not delete good material for being
  non-American.
- **P-6 — The 51 pre-existing integrity warnings** in the grammar lessons are logged and
  deliberately untouched.
- **P-7 — American History is now the largest topic.** OPEN, and the successor to P-2. The
  collection took `american-history` to 38 of 152, against `everyday` 21 and `travel` 20, while
  `world-history` has exactly one text. P-2's travel concentration is resolved; the imbalance has
  simply moved. The next collection should go anywhere but the nineteenth-century United States.

**Resolved since the original audit:**

- ~~P-3 — non-ASCII source filenames.~~ Moot: the source files are no longer read by anything,
  and every slug shipped is ASCII and hyphen-only.
- ~~P-4 — texts existing only to drill a tense.~~ All five rewritten: `capetown`,
  `physical-education`, `say-speak-talk-tell-02`, `my-day-in-vienna-to-by-for` edited,
  `cybersecurity` replaced.
- ~~P-5 — content defects.~~ All resolved: `santa-catarina`, `formal-informal`, `egypt`, `haiti`
  and `animal-solutions` replaced; `it-ptbr`, `irregular-verbs-list`, `market-sumup` and
  `el-nino-2027` deleted.

### Smaller work outstanding

- **Illustration.** Every one of the 152 texts is illustrated: 317 pictures, at one per ~300
  words (one under 300 words, two to 600, three to 900, capped at five), and no text below that.
  Pictures are placed after the paragraph they belong to. The local gallery comes first
  (`scripts/import_local_artwork.py`); Commons fills what it cannot (`scripts/add_commons_image.py`),
  which takes public domain as it is, CC BY, CC BY-SA, OGL and Commons' {{Attribution}} with the
  credit printed under the picture, and refuses anything carrying NC or ND. `docs/image-credits.md`
  is regenerated from the JSON by `scripts/build_image_credits.py`. Captions name the work and add
  one fact about it; they never refer to the reading or argue for the picture's place on the page.
  A gallery painting stands in for a scene only when the text is not about a named place that
  could be photographed instead.

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

**Images.** A text's own artwork lives in a top-level `images` array, never inside `passage`:

```json
"images": [
  {"src": "01.png", "after": 1, "alt": "...", "caption": "..."}
]
```

`after` is the index of the paragraph the figure follows, and the file is read from
`assets/img/reading/{level}/{slug}/`. Keeping images out of `passage` is deliberate: the
narration fingerprint covers the passage only, so adding or changing a picture never marks the
audio stale and never forces a re-record.

Extract them with `python3 scripts/extract_source_images.py <docx-stem> <level>/<slug>`
(`--list` to look first). It skips the two boilerplate images by hash — a 36 KB logo present in
72 of the source documents and a 1.2 MB decorative header present in 12 — so only the artwork
belonging to the text comes out. 84 source documents contain images and 55 of them are genuine
content. Nothing is left to convert, and the source documents were deleted in milestone 16, so
this records how the artwork got here rather than a step still to run.

**Check the rights before publishing one.** Most of these are old engravings, frescoes and
period postcards, which are fine. Some are not: the Grinch still in `christmas-krampus-grinch`
is a frame from the 1966 television special and was deliberately left out.

**Exercise item shapes the engine actually implements** — these differ per type and getting them
wrong fails silently in the browser, so follow them exactly:

| Type | Item fields |
|---|---|
| `reading-comprehension`, `multiple-choice`, `vocabulary` | `id`, `prompt`, `options`, `answerIndex`, `explanation` |
| `true-false` | `id`, **`statement`**, `answer` (bool), `explanation` |
| `fill-blank` | `id`, `prompt` with `___` per blank, **`answers`** (one per blank), `options` (flat array for a single blank, array-of-arrays for several), `explanation` |
| `matching` | **one item** per block: `id`, **`pairs`** (an array of `{left, right}`), `explanation`. One item per pair renders nothing. |
| `correction` | `id`, **`incorrect`** (the wrong sentence), **`answer`** (an array of accepted rewrites), `explanation`. It is `incorrect`, not `prompt`. |
| `true-false` explanation | begin it with "True —" or "False —" so the printed feedback stands alone |

`writing` blocks are **ungraded textareas**: the engine renders the prompt and a "Save my
answers" button, and ignores any `modelAnswer` you supply. Extended written work therefore
belongs in `discussion` — which is what every reading page does — not in a `writing` block.

### Work order

Conversion is finished; there is no queue left in `cefr/texts/`. A1, C2 and the illustration
of every text are all done — milestones 7, 8 and 11 — and this section's old queue is kept only
in the history above. What remains:

1. **A collection that is not American history** (P-7). The library's largest topic is now
   `american-history` at 38 of 152, and `world-history` has one text. Anywhere else.
2. **The vocabulary-variety reading list.** `check_padding.py` names the bottom tenth of each
   length band. It is a ranking and will never be empty — read it when you want something to
   improve, not as a list of faults.

**Audit the verdict as you go.** Two texts have now had their audited action changed on a close
read — `nfl` (KEEP→EDIT, factual errors) and `investigation-story` (KEEP→EDIT, a graphic and
abusive closing exchange that the audit had not flagged). The audit was written from a full read,
but a verdict is not binding: if a text turns out to need work the map does not record, change
the `action`, write the reason into the entry, and say so in the commit.

### Milestone discipline

Commit per coherent group (e.g. "the KEEP texts for A2 and B1"), not per file and not in one
giant commit. At each milestone: update `PROJECT_STATUS.md` → run both validators → commit →
push → merge → record the commit hash here.
