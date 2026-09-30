# Content audit — reading & exercise library

Generated from `docs/reading-library-map.json`, which is the authoritative machine-readable map.
Every one of the **98 source documents** in `cefr/texts/` was extracted and read in full before
being classified here; nothing in this table was inferred from a filename.

Extraction used the `.docx` wherever one exists (the `.pdf` is an export of the same document).

See `PROJECT_STATUS.md` for the target architecture, the editorial rules and the next actions.

## Totals

| Action | Count | Meaning |
|---|---:|---|
| DELETE | 5 | Nothing worth migrating. |
| REPLACE | 8 | The slot is worth keeping, but authoring a new text beats repairing this one. |
| MERGE | 16 | Two or more files teach essentially the same language in essentially the same context. |
| SPLIT | 8 | Several unrelated materials share one file; each deserves its own page, exercises and audio. |
| EDIT | 33 | Useful material that needs correction before it goes on the site. |
| CONVERT | 11 | Not a reading text -- a drill, answer key or discussion bank. |
| KEEP | 17 | Already good; convert as-is. |
| **Total** | **98** | |

### Recommended level

| Level | Docs |
|---|---:|
| A1 | 1 |
| A2 | 20 |
| B1 | 38 |
| B2 | 22 |
| C1 | 15 |
| C2 | 0 |
| n/a | 2 |

**A1 has 1 document and C2 has none.** The library's centre of gravity is B1. A coherent
A1→C2 progression therefore needs newly authored A1 material and a small, genuinely justified
C2 set -- flagged as P-1 in `PROJECT_STATUS.md` and to be labelled as new content, never as pre-existing.

### Audio requirement

| Audio | Docs | |
|---|---:|---|
| `required` | 64 | must be generated |
| `exists` | 4 | mp3 already present, text unchanged |
| `stale-on-edit` | 2 | mp3 present but text is being edited -- **must be regenerated** |
| `n/a` | 28 | drill / answer key / discussion bank -- not a reading text |

---

## DELETE (5)

Nothing worth migrating. Each reason is given -- no existing material is dropped silently.

| Source | Words | Genre | Level | Topic | Audio | Reason |
|---|---:|---|---|---|---|---|
| `el-niño-2027` | 432 | reading | B2 | society | `n/a` | Dated to a specific forecast year and written for one Brazilian city ('what does it mean for someone who lives in porto alegre'). Stale and off-brief; nothing here is worth migrating. |
| `irregular-verbs-list` | 497 | reference | A2 | reference | `n/a` | Duplicates the existing irregular-verbs.html page, and this copy is defective: lists regular verbs as irregular ('Clap/Clapped'), invents 'Abidden', and drops the participle column for many entries. |
| `it-ptbr` | 844 | reference | n/a | n/a | `n/a` | Written entirely in Portuguese — a translation of it-management, not an English exercise. The English original is kept. |
| `market-sumup` | 759 | reading | C1 | business | `n/a` | Single-day market report ('The S&P 500 fell about 0.7%... third straight weekly loss') tied to a specific Fed nomination. Already stale and cannot be kept current. |
| `mind-games` | — | reference | n/a | n/a | `n/a` | PDF-only and image-based — the only extractable text is 'ACTIVITY 1/2/3', so there is no content to migrate. Deletion confirmed by the user. |

## REPLACE (8)

The slot is worth keeping, but authoring a new text beats repairing this one.

| Source | Words | Genre | Level | Topic | Audio | Reason |
|---|---:|---|---|---|---|---|
| `animal-solutions` | 271 | reading | B1 | work | `required` | Reads as marketing copy for a named vendor (Gallagher), not a teaching text. Replace with a neutral do/make farm-work reading. |
| `cybersecurity` | 898 | reading | B1 | tech | `required` | Whole text written in the past tense for a simple-past drill, which makes it factually wrong: 'Cybersecurity protected computers...', 'Today, we used the internet'. Rewrite in present tense and move the past-tense practice to a separate drill. |
| `egypt` | 413 | reading | B2 | society | `required` | Presents a UFO sighting as documented history and invites the student to research it 'as a doctoral student'. Misinformation framed as scholarship; replace with a real Thutmose III / Karnak reading. |
| `formal-informal` | 535 | reading | B2 | society | `required` | The register contrast is worth teaching, but the informal sample argues developing nations are poor because 'they suck at running their countries'. Keep the formal/informal exercise shape, replace the topic with a neutral one. |
| `haiti` | 564 | reading | C1 | society | `required` | Blog-register news brief with an emoji mid-text, and graphic content (gang rape, torture, starvation) unsuitable for a general adult English class. Replace with a current-affairs reading that teaches the same analytical language. |
| `maringá` | 387 | reading | B1 | travel | `required` | City-attractions list for a Brazilian city; list format and off-brief. Replace with a US city reading serving the same 'describing a city' language. |
| `milan-restaurants` | 608 | reading | B1 | food | `required` | Annotated restaurant list for Milan — no connected prose, no American context. Replace with a US dining-out reading. |
| `santa-catarina` | 340 | reading | B1 | travel | `required` | A wholesome family-travel text in which the father 'decided to change careers and become a michê' — Brazilian slang for a male prostitute. Unusable as written; keep the present-perfect-continuous travel premise and rewrite. |

## MERGE (16)

Two or more files teach essentially the same language in essentially the same context.

| Source | Words | Genre | Level | Topic | Audio | Reason |
|---|---:|---|---|---|---|---|
| `coffee-and-it-answers`<br>→ `coffee-and-it` | 295 | reference | B1 | work | `n/a` | Answer key for coffee-and-it; becomes that block's answers/explanations. |
| `common-chores`<br>→ `household-chores` | 340 | reading | B1 | everyday | `required` | Phrasal-verb chores text. Unnatural line to fix: 'you hang up or toss into the dryer the clothes'. Merges with common-chores-ii. |
| `common-chores-ii`<br>→ `household-chores` | 337 | reading | A2 | everyday | `required` | Same teaching goal as common-chores, narrative form (Mike, Austin TX). Keep the American setting as the merged version's frame. |
| `daily-activities`<br>→ `routines-and-prepositions-drill` | 442 | drill | B1 | work | `n/a` | Identical '_____ (to verb) ___ (in/on/at)' template to navigating-finance and unfortunate-events; three copies of one exercise. |
| `formula-1-exercises-answers`<br>→ `formula-1` | — | reference | B2 | sports | `n/a` | Answer key for formula-1. |
| `kitchen-chaos-i`<br>→ `kitchen-phrasal-verbs` | 228 | reading | B1 | everyday | `required` | Same premise and teaching goal as kitchen-chaos-ii (IT worker cooking, phrasal verbs). Two texts teaching one thing. |
| `kitchen-chaos-ii`<br>→ `kitchen-phrasal-verbs` | 310 | reading | B1 | everyday | `required` | Merges with kitchen-chaos-i into one stronger phrasal-verb text. |
| `navigating-finance`<br>→ `routines-and-prepositions-drill` | 734 | drill | B2 | business | `n/a` | Third copy of the same gap-fill template as daily-activities and unfortunate-events. |
| `say-speak-talk-tell`<br>→ `the-day-at-the-market` | 330 | reading | A2 | everyday | `required` | This is the same text as the-day-at-the-market ('A Day at the Market') with say/tell verbs foregrounded. One text, two files. |
| `simple-past-+-present-continuous-+-future-1`<br>→ `tense-contrast-drill` | 1009 | drill | A2 | review | `n/a` | Parts 1 and 2 of one exercise split across two files. |
| `simple-past-+-present-continuous-+-future-2`<br>→ `tense-contrast-drill` | 1018 | drill | A2 | review | `n/a` | Second half of the same exercise. |
| `trials`<br>→ `american-courtroom-cases` | 671 | reading | C1 | society | `required` | Both 'Court Trials' files cover famous US cases; merge into one curated reading and even out the register ('some crazy courthouse cases'). |
| `trials-mayors`<br>→ `american-courtroom-cases` | 1007 | reading | C1 | society | `required` | Same title and theme as trials, focused on mayoral corruption cases. |
| `two-texts-sp-to-pp`<br>→ `past-to-present-perfect-drill` | 700 | drill | B1 | review | `n/a` | Paired with its -ii file as one exercise. |
| `two-texts-sp-to-pp-ii`<br>→ `past-to-present-perfect-drill` | — | drill | B1 | review | `n/a` | Second half of the same exercise. |
| `unfortunate-events`<br>→ `routines-and-prepositions-drill` | 570 | drill | B1 | everyday | `n/a` | Same gap-fill template as daily-activities and navigating-finance. |

## SPLIT (8)

Several unrelated materials share one file; each deserves its own page, exercises and audio.

| Source | Words | Genre | Level | Topic | Audio | Reason |
|---|---:|---|---|---|---|---|
| `a1-review-and-a1-review-2` | 2036 | drill | A1 | review | `n/a` | Two concatenated A1 review sheets, 2036w. Split into themed A1 review blocks. |
| `american-culture` | 1072 | reading | B2 | culture | `required` | Three unrelated things in one file: a culture overview, a corndog/state-fair food piece, and passive-voice grammar drills. Split into a B2 culture reading, a B1 food reading, and a drill block. |
| `interrogative-exercises` | 1656 | drill | A2 | review | `n/a` | Long question-formation drill across several tenses; split by tense into separate blocks. |
| `shadows-in-the-server-room` | 2407 | reading | C1 | work | `required` | Strong long-form workplace mystery (2407w) — too long for one page and one audio file. Split into chapters, per requirement 8's guidance against huge audio files. |
| `soothing-texts` | 2225 | reading | C1 | everyday | `required` | Several unrelated descriptive scenes (kitchen, etc.) in one 2225w file. Split into short descriptive readings — excellent sensory-vocabulary material once separated. |
| `text-interpretation` | 1039 | reading | B2 | society | `required` | Several unrelated short articles ('Robot Birds' and others) in one file; split so each gets its own page, questions and audio. |
| `text-interpretation-aesops-fables` | 1921 | reading | B2 | literature | `required` | Multiple fables in one file. Split per fable; keep the literary register but gloss the archaic phrasing. |
| `verb-tense-review` | 5091 | drill | B1 | review | `n/a` | Largest file in the library (5091w) — many separate gap-fill texts, several with good American settings (hotel near Times Square). Split into per-scenario drill blocks. |

## EDIT (33)

Useful material that needs correction before it goes on the site.

| Source | Words | Genre | Level | Topic | Audio | Reason |
|---|---:|---|---|---|---|---|
| `america-in-1776` | 1154 | reading | C1 | culture | `required` | Strong, genuinely C1 essay on the founding. Dense academic register; trim and break into sections for readability. |
| `arriving-in-johannesburg` | 1306 | dialogue | B1 | travel | `required` | Excellent airport-arrival functional dialogue. Traveler renamed to an English name; trim repetition in the shuttle exchange. |
| `australia-and-thailand` | 954 | reading | A2 | travel | `required` | Bulleted travel-tips list, not connected prose. Rewrite the Sydney half as a short A2 reading; drop or fold the Thailand half. |
| `beers` | 694 | reading | B1 | food | `required` | Factual slip: 'Pilsner: Pilsen is a type of lager'. Fix, tighten the style list. |
| `business-war-it` | 689 | reading | B2 | tech | `required` | Useful tech-history angle but list-like and abrupt; convert to connected prose. |
| `cachaças` | 672 | reading | B1 | food | `required` | Sound process text. Slug de-accented for safe hosting; retitle from the odd 'Distilled Spirit Visitation'. |
| `capetown` | 770 | reading | B2 | travel | `stale-on-edit` | Perfect/perfect-continuous forms crammed in unnaturally ('had begun... had been... has been pulling'). Rewrite naturally, then regenerate the 4 existing mp3s. |
| `cars-and-their-parts` | 436 | reading | B1 | tech | `required` | Good vocabulary load; over-casual asides ('this beast drives the whole operation') to even out. |
| `christmas-krampus-grinch` | 261 | reading | B1 | culture | `required` | Text points at images that do not survive conversion ('Here is a chilling traditional image of Krampus'). Rewrite those references out. |
| `detective-story` | 526 | reading | B1 | society | `required` | Good whodunnit with inline vocabulary glosses that become a real vocabulary component. Retitle (the 'Cachaca Case' name is unrelated to the plot). |
| `do-make-livestock-farming` | 406 | reading | B1 | work | `required` | do/make contrast is forced into unnatural English ('Do the feeding of the cattle'). Rewrite with collocations people actually use. |
| `dream-bistro` | 430 | reading | A2 | work | `required` | Good present/past A2 narrative. Relocate to a US setting and use an English name, per the project's American-context brief. |
| `egypt-a-journey-through-history-and-culture` | 1086 | reading | B2 | culture | `required` | The legitimate Egypt text; keep as the single Egypt reading and trim. |
| `golden-gate-bridge-present-perfect` | 274 | reading | B1 | culture | `required` | Idioms crammed in at an unnatural density, one of them crude for a classroom ('crews have busted their butts'). Keep the present-perfect focus, rewrite the register. |
| `it-and-jiu-jitsu` | 356 | reading | B2 | work | `required` | Likeable text; remove the gratuitous aside about breaking an opponent's 'defense (or face)'. |
| `it-management` | 432 | reading | C1 | business | `required` | Dense, authentic exec-meeting register. Rename the cast to English names per instruction; the source's hyphens (risk-adjusted, per-transaction) must survive extraction. |
| `my-day-in-vienna-to-by-for` | 319 | reading | B1 | travel | `required` | Passives exist only to demo the form and read badly ('The tickets were bought by her', 'I gave a big hug to her'). Rewrite naturally. |
| `north-sentinel-island` | 270 | reading | B2 | society | `required` | Genuinely interesting factual text; check the framing of the islanders stays respectful and drop the 'Stone Age' comparison. |
| `ny-visitation` | 789 | reading | B1 | travel | `required` | Good hotel/recommendation narrative. Overlaps restaurant-dialogue (same Joe's Pizza scene) — keep this as the narrative, that as the dialogue, and cross-reference. |
| `physical-education` | 392 | reading | B1 | sports | `stale-on-edit` | Present perfect and past perfect are misused ('Last month, she had organized a relay race' with no later anchor). Fix the tenses, then regenerate the 4 existing mp3s. |
| `real-estate` | 634 | reading | C1 | business | `required` | Strong market-analysis register, but wholly about Porto Alegre neighborhoods. Re-set in a US market to match the brief. |
| `recent-advancements-in-it` | 367 | reading | B2 | tech | `required` | Pegged to 'What's new in 2026'; rewrite so it does not date, and tone down 'insane'/'revolutionary'. |
| `restaurant-dialogue` | 345 | dialogue | A2 | food | `required` | Useful ordering dialogue. Rename the family to English names per instruction; keep as the dialogue counterpart to ny-visitation. |
| `romania` | 575 | reading | B2 | culture | `required` | Competent country overview; slightly encyclopedic, tighten into themed paragraphs. |
| `rs-japan` | 945 | reading | C1 | culture | `required` | Overwritten ('neon-veined precision', 'cultural whiplash'); the cultural-contrast idea is good but the prose needs heavy pruning to read as natural C1. |
| `say-speak-talk-tell-02` | 353 | reading | B1 | tech | `required` | Present perfect applied where it is wrong: 'I've known there are some exciting purchases', 'The salesperson has told me...'. Rewrite the tense scheme. |
| `soma-nomaoi` | 446 | reading | B2 | culture | `required` | Good festival text; strip the raw x.com link and keep the Japanese terms glossed. |
| `southeast-asia-adventure` | 572 | reading | B1 | travel | `required` | Good present-perfect travel narrative; rename the cast to English names per instruction. |
| `st.-patricks-day` | 371 | reading | A2 | culture | `required` | Charming short story, English names already. Fix the letter-spacing artifacts inherited from the source layout. |
| `travel-dialogues` | 935 | dialogue | A2 | travel | `required` | Strong functional dialogues (airline booking, etc.) but student lines are blank, prices are in euros and times are 24-hour. Supply model answers and convert to US conventions ($, 4:45 PM) per requirement 16. |
| `travel-dialogues-02` | 905 | dialogue | B1 | travel | `required` | Hotel-reception training dialogue; same treatment, good workplace-English value. |
| `trip-through-rs` | 785 | reading | A2 | travel | `required` | Good there is/there are practice in dialogue. Re-set in a US road-trip frame with English names to match the brief. |
| `usa-restaurants` | 1318 | reading | B1 | travel | `required` | Titled 'U.S.A. Restaurants' but the body is a bulleted list of Florida attractions — title and content do not match, and it is a list rather than a reading. Rewrite as a Florida travel reading, and let the dining material live in the food thread. |

## CONVERT (11)

Not a reading text -- a drill, answer key or discussion bank. Becomes an HTML exercise component (audio not applicable).

| Source | Words | Genre | Level | Topic | Audio | Reason |
|---|---:|---|---|---|---|---|
| `a-freelance-accounting-assignment` | 655 | drill | B1 | work | `n/a` | Pure simple-past gap-fill on accounting tasks; no prose passage. Becomes a fill-blank block. |
| `a2-review` | 1158 | drill | A2 | review | `n/a` | Well-formed A2 mixed-grammar drill set; converts cleanly to fill-blank/multiple-choice. |
| `coffee-and-it` | 285 | drill | B1 | work | `n/a` | Word-bank gap-fill; its answer key is a separate file to fold in. |
| `formula-1` | 808 | drill | B2 | sports | `n/a` | Technical word-bank gap-fill; answer key is a separate file. |
| `grammar-practice-i` | 1050 | drill | A2 | review | `n/a` | Multiple-choice-in-brackets dialogue drill; maps directly to fill-blank with options. |
| `grocery-shopping` | 160 | drill | A2 | everyday | `n/a` | A writing worksheet whose body is blank rules for handwriting. Becomes guided writing prompts, not a reading. |
| `questionnaire-company-management` | 568 | discussion | C1 | business | `n/a` | A bank of executive discussion prompts; becomes a speaking/discussion component, not a reading. |
| `questionnaire-company-tech-leader` | 216 | discussion | C1 | interviews | `n/a` | Same — senior-interview speaking prompts. |
| `review-prepositions-some-any-no-tenses-comparatives` | 707 | drill | A2 | review | `n/a` | Clean multiple-choice mixed review; converts directly. |
| `rio-de-janeiro-exercises` | 342 | drill | B1 | travel | `n/a` | Word-bank gap-fill about hiking in Rio; keep as a drill. |
| `say-talk-speak-tell-exercises` | — | drill | A2 | everyday | `n/a` | The drill half of the say/speak/talk/tell set; attach to the merged reading. |

## KEEP (17)

Already good; convert as-is.

| Source | Words | Genre | Level | Topic | Audio | Reason |
|---|---:|---|---|---|---|---|
| `attention-economy` | 327 | reading | C1 | society | `exists` | Clean, well-pitched C1 argument text. Already has 3 mp3 segments. |
| `cars` | 967 | reading | B1 | society | `exists` | Clear, well-levelled text on income and car choice. Has 4 mp3 segments. |
| `climbing` | 494 | reading | B1 | sports | `required` | Clean informational sports text with a natural vocabulary set. |
| `coffee-brewing` | 321 | reading | A2 | food | `required` | Well-formed procedural text; good imperative/sequencing practice. |
| `glamping` | 520 | reading | B1 | travel | `required` | Natural, well-levelled travel-trend text. |
| `hiking-in-the-mountains` | 292 | reading | A2 | everyday | `exists` | Simple, natural past-tense narrative. Has 2 mp3 segments. |
| `investigation-story` | 408 | dialogue | B1 | society | `required` | Tight interrogation dialogue, natural past continuous, English names already. |
| `it-interview` | 447 | dialogue | B2 | interviews | `required` | Realistic technical job interview; directly serves the job-interview brief. |
| `nfl` | 566 | reading | B1 | sports | `required` | Clear explainer on an American sport; squarely on brief. |
| `phrasal-verbs-01-bed-and-breakfast` | 1153 | reading | B2 | everyday | `required` | Dense but natural phrasal-verb narrative; among the strongest material in the library. |
| `phrasal-verbs-02-trip-abroad` | 1019 | reading | B2 | travel | `required` | Same strength, US travel setting, English names already. |
| `physiological-stressors` | 832 | reading | C1 | sports | `required` | Authentically C1 technical prose; good for advanced learners who read in their field. |
| `project-management-can-could-able-do-make` | 597 | reading | B2 | work | `required` | Solid workplace-modality text with an English-named cast. |
| `sales-strategy` | 701 | reading | B2 | business | `required` | Natural business-English text with genuinely useful collocations and acronyms. |
| `snowy-days` | 473 | reading | B1 | everyday | `exists` | Authentic conversational register, a genuinely useful model of informal opinion writing. Light polish only. Has 2 mp3 segments. |
| `technology-and-ethics` | 648 | reading | C1 | tech | `required` | Genuinely C1, professionally relevant, natural register. |
| `the-day-at-the-market` | 269 | reading | A2 | everyday | `required` | Simple, natural, well-levelled. Serves as the merge target for say-speak-talk-tell. |

---

## Merge targets

The 16 MERGE entries collapse into these pages:

| Merge target | Sources |
|---|---|
| `american-courtroom-cases` | `trials`, `trials-mayors` |
| `coffee-and-it` | `coffee-and-it-answers` |
| `formula-1` | `formula-1-exercises-answers` |
| `household-chores` | `common-chores`, `common-chores-ii` |
| `kitchen-phrasal-verbs` | `kitchen-chaos-i`, `kitchen-chaos-ii` |
| `past-to-present-perfect-drill` | `two-texts-sp-to-pp`, `two-texts-sp-to-pp-ii` |
| `routines-and-prepositions-drill` | `daily-activities`, `navigating-finance`, `unfortunate-events` |
| `tense-contrast-drill` | `simple-past-+-present-continuous-+-future-1`, `simple-past-+-present-continuous-+-future-2` |
| `the-day-at-the-market` | `say-speak-talk-tell` |
