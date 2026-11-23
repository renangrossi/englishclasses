# Language audit — 2026-11-23

A grammar and language pass over the whole site: what a student reads, and what it
teaches. Branch `audit/language-pass`, merged to `main`.

## What was checked, and how

| Area | How |
|---|---|
| Every lesson page (98), its rules, examples, mistake cards, tips and summary | Read in full |
| The six Test Yourself pages and seven level overview pages | Read in full, and compared with the lessons they summarize |
| Root pages (home, Extras, privacy, progress, placement, exams, dictionary, hub) | Read in full |
| The seven grammar booklets (`cefr/english-classes-*.html`) | Read in full |
| All 2,246 reading-glossary definitions | Read in full |
| Interface strings in `assets/js` | Read in full |
| Everything above plus 10,774 lesson exercise items and all 152 readings (623k unique words) | Spell-checked against en_US (hunspell, 20,362 distinct words; every unknown word looked up in context) |
| Every multiple-choice and gap-fill item | Checked that its explanation does not name a different option than its key (36 flags, all intended) |
| Every keyed exercise sentence | Grammar heuristics: a/an, doubled words, agreement |

Reading passages and the bulk of the exercise items were covered by the automated checks
and by reading their glossaries, not line by line; both had their own audits in October
and November.

## What was wrong, and is fixed

**Rules that taught the wrong thing.** "I remembered to lock the door" was glossed *(I did
it, then remembered)* — the reverse. The A2 spelling rule doubled the consonant after any
vowel + consonant. B2 Test Yourself said never to mix the past simple with *would have*,
one topic before teaching mixed conditionals. *If it wasn't for* was called a present form;
*that* in defining clauses was called informal; *if it hadn't been for* "always" takes the
past perfect.

**Correct English marked as a mistake.** *Have you finished already?*, *It snowed all day
yesterday*, *It is said he is rich*, *She admitted to lying*, *She really liked it, in fact*,
*I have two sisters who live in London* — and two that are standard American English, *She
called me already* and *Did you ever visit Egypt?* Each card now shows a real error.

**Mistake cards that showed the same sentence twice** (*Who is coming?*, *Hurry up!*, *Wake
up early tomorrow*, *between* "is already correct"), and corrections that were wrong or
unnatural themselves: *She has finished her homework for 2 hours*, *I am the second in the
line*, *I like tea or coffee*, *By this time next year, she retires*.

**Examples that contradicted their own lesson** — adjective order (*a tall, friendly man*), a
Simple Past II example its own mistake card corrected, a *while/when* pattern that matched
none of its examples — and the A2 Test Yourself prepositions cards, which still taught what
the 2026-11-13 rewrite of that lesson had removed.

**Cut-off text.** 17 C1/C2 subtitles stopped mid-word (*hypothetical situat…*); six of them
also broke their meta description with an unescaped quote, leaving the link preview empty.
Objectives and summaries that ended at a colon, and one placeholder summary, are written out.

**Spelling the checker could not see, and damage it had done.** The dialect tools missed
*-ically*, most *-isation* words, compounds like *watercolour*, the *-ll-* forms of *spiral,
panel, martial*, and the booklets entirely. They had also turned the show title *GREY'S
ANATOMY* into *Gray'S ANATOMY* and a glossary note into *(British spelling: harbor)*. Both
are restored and protected; 26 strings were normalized.

**Booklets.** British IPA on an American course (/əʊ/, /ɑː/), *I* glossed as *me, myself*, a
comma rule contradicted on its own sheet, *between either … or*, and calques from Portuguese
(*Summing up, …*; reflexives as "when the same person creates and suffers the action").

**Extras page.** A dangling opener, *is diagnosed* for a condition someone has, *between
2025-2027*, *Radio-stations*, *a competitor English teacher*, a day-first date, and names:
Viking, Airbnb, Laszlo, Elisabeth Kübler-Ross, U.S. Customs and Border Protection.

**Worksheets.** The C1/C2 download PDFs are generated from `.txt` sources that carried the
same errors as their lessons; the eight affected ones are corrected and regenerated.

Smaller: *God save the King*, *well-being*, *coins and bills*, *Yours faithfully* marked as
British, *Italian* capitalized in a word-order prompt, a circular glossary entry (*to wait in
line: to wait in a line*), a credit that printed Commons' footnote marker, *November 15,
2026*.

## Left for a decision

These are real, but each is a choice about content, branding or cost rather than a slip,
so they were not changed.

1. **Homepage copy.** "Welcome to *teacher Renan's* English Course" uses *teacher* as a title,
   a Portuguese pattern (*professor Renan*); "Est. *in* 1776" is usually "Est. 1776". The
   Exercises card says "dozens of … exercises, independent of level" — the library is 152
   texts, graded A1–C2. Mock Exams promises "answer keys"; the exams page says to ask the
   instructor where a key is not included.
2. **The signed-in progress text contradicts the privacy page.** It says only XP, streak,
   badges and results are stored "next to your email address — nobody else can see them";
   the privacy page says Google sign-in also stores name and picture, and that the teacher
   can see progress.
3. **A1 Test Yourself, topic 20** still holds the old version of *Imperatives (Review and
   Expand)*: past simple and *will* in a story, where the lesson is now present simple,
   present continuous and imperatives. Its broken card is fixed; the topic itself needs
   regenerating from the lesson, including its exercises.
4. **Test Yourself structure.** A2 lists 15 topics for 14 lessons (topics 7 and 8 are the
   same); B2 has three overlapping future-continuous/perfect topics.
5. **Tense names.** The lessons say *simple past* 262 times and *past simple* 208 times,
   *present simple* 141 and *simple present* 136, sometimes on one page and in lesson titles.
   American textbooks use *simple present / simple past*.
6. **British words in texts set nowhere in particular**, which the site's own rule says
   should be American: *fortnight*, *lay the table*, *cooker*, *a load of washing*
   (`b1/a-day-in-the-house`), *till* (`b1/coffee-and-it`, `b2/describing-a-place`), *revise*
   for study (`b2/intelligence-pills`), *bin* (`b1/robot-birds`). They are in narrated
   passages, so each change needs re-narration. `c1/apollo-11` also dates the landing
   "20 July 1969".
7. **Narration.** 38 readings are listed as stale: 33 from the 2026-11-13 spelling pass and
   5 from this one. All changed by spelling only and sound the same; regenerate with
   `scripts/generate_reading_audio.py` when convenient.
8. **Booklet source.** The booklets are built by an external project; the fixes here need
   the same edits there, or a rebuild will bring the errors back. A1's sheet also teaches
   *at Easter / at Christmas*, where American English mostly says *on Easter*.
9. **Portuguese inside English pages** ("Eu tenho 25 anos", "O café é popular no Brasil") is
   not marked `lang="pt-BR"`, so screen readers pronounce it as English.
10. **Unverified.** The Extras card "Lion King with real actors" describes "Red the lion" and
    "Disney's live-action adaptation" — worth a look at the video. C2 Discourse Devices
    teaches sentence-initial *On which point, …*, which is rare; *On this point* is the
    usual form.
11. **Asset stamps.** `ai-teacher.js` changed in 5efb785 but the 280 pages that load it still
    carry its old `?v=`; `scripts/stamp_asset_versions.py` fixes it (pre-existing, not part
    of this pass).

## Tooling

- `scripts/check_dialect.py` — new rules for the spellings above, and protection for titles
  (*Grey's Anatomy*), *Open Government Licence* and any parenthetical note that names the
  British form.
- `scripts/normalize_lesson_spelling.py` — now covers the booklets.
- `scripts/regenerate_cefr_pdfs.py` — names the serif face for headings, which the current
  LibreOffice otherwise sets in sans.

`check_site_integrity.py`: 289 pages, 71 curriculum lessons, 0 errors, 45 warnings (the
baseline). `check_content.py`: 157 sources, no errors. `check_dialect.py` and
`normalize_lesson_spelling.py`: nothing outstanding.
