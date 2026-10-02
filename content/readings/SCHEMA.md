# Reading library data schema (v1)

Single source of truth for a reading text: one JSON file at
`content/readings/{level}/{slug}.json`. Everything a student sees is generated
from it and nothing is maintained by hand:

| Generated | By |
|---|---|
| `reading/{level}/{slug}.html` | `scripts/build_reading_page.py` |
| `assets/audio/reading/{level}/{slug}.mp3` | `scripts/generate_reading_audio.py` |
| `exercises.html` (cards, counts, filters) | `scripts/build_exercises_hub.py` |
| `assets/data/search-index.json` | `scripts/build_search_index_readings.py` |
| `docs/image-credits.md` | `scripts/build_image_credits.py` |
| `docs/content-audit.md` | `scripts/build_content_audit.py` |

`scripts/finish_reading_batch.py` runs the lot. **It does not run
`tag_grammar.py` or `build_image_credits.py`** — run those too, or a batch
ships without grammar filter tags and without image credits.

## Checks

```bash
python3 scripts/check_content.py --warnings   # this schema
python3 scripts/check_vocabulary.py           # glossary, for a Portuguese reader
python3 scripts/check_dialect.py              # American/British spelling drift
python3 scripts/check_site_integrity.py       # the built site: links, files
```

## Shape

```jsonc
{
  "id": "c1-reading-rosa-parks",     // unique; conventionally {level}-reading-{slug}
  "level": "C1",                     // must match the folder it sits in
  "slug": "rosa-parks",              // must match the filename
  "order": 100,                      // optional; sorts within a topic group
  "topic": "american-history",       // a key of reading_common.TOPIC_LABELS
  "title": "Rosa Parks and the Montgomery Bus Boycott",
  "subtitle": "One sentence. It is the page's standfirst and the card's blurb.",
  "description": "Used for <meta name=description> and the search index.",
  "source": "authored for this site; no source document",
  "provenance": "new",               // as-published | edited | rewritten | merged | new
  "narrator": "female",              // female | male | omitted (rotates by slug)

  "passage": [                       // one string per paragraph; the only markup
    "A paragraph.",                  // allowed is *italics*, for a title or a
    "*Browder v. Gayle* decided it." // case name. Asterisks are stripped before
  ],                                 // narration and become <em> on the page.

  "images": [ /* see below */ ],
  "vocabulary": [ /* see below */ ],
  "exercises": [ /* schema: see assets/js/exercises.js */ ],
  "discussion": ["Open questions. No right answers."],
  "grammar": ["past-simple"],        // written by scripts/tag_grammar.py --write
  "audio": { "duration_label": "4:17" }  // measured by finish_reading_batch.py
}
```

## Images

```jsonc
{
  "src": "01.jpg",            // in assets/img/reading/{level}/{slug}/, or
                              // "b2/aesop/03.png" to share another text's set
  "after": 3,                 // 0-based index of the paragraph it follows
  "wide": true,               // optional; full measure instead of half. For a
                              // map, a flag, a document — anything read for detail
  "alt": "What is in the frame, for somebody who cannot see it",
  "caption": "*Title* — Artist, year. Then a sentence, if it is an analogue.",
  "source": "commons:File:Foo.jpg",   // or a local gallery filename
  "relation": "depicts",              // depicts | analogue — see below

  // Written only when the licence requires a credit. add_commons_image.py sets
  // these; build_reading_page.py prints them under the picture.
  "licence": "CC BY-SA 4.0",
  "author": "Infrogmation of New Orleans",
  "source_url": "https://commons.wikimedia.org/wiki/File:...",
  "credit_prefix": "Image"            // optional; the word before the credit.
                                      // "Photo" unless set -- a satellite
                                      // composite is not a photograph
}
```

**`relation` is the field that keeps the library honest.** This library
illustrates with period artwork, and a painting can be doing one of two quite
different jobs:

- `depicts` — the picture is of the thing. Rosa Parks being fingerprinted;
  Trumbull's *Declaration of Independence*; the Chinese Exclusion Act.
- `analogue` — a period work standing in for something it is not. A siege
  painting over a text about online security; Tower Bridge over a text about
  the Golden Gate.

An analogue is a good illustration and a bad photograph, and the caption is
what decides which the reader takes it for. A caption that reads only
*"\*Dordrecht\* — Elias Pieter van Bommel, 1871."* over a text about Denver
tells a reader they are looking at Denver. So an analogue's caption must carry
a sentence saying what it is doing there, and `check_content.py` warns when one
does not.

If `relation` is absent it is inferred: a `commons:` source is a `depicts`, a
local gallery file is an `analogue`. Set it explicitly wherever that is wrong —
a gallery painting often does depict its subject.

Rights are not a judgement call. `scripts/add_commons_image.py` reads the Commons
licence metadata and sorts it into three tiers: public domain and CC0 are used as
they are; CC BY, CC BY-SA, the UK Open Government Licence and Commons'
{{Attribution}} licence are used with the licence and author recorded on the
image and printed under it; anything carrying NC or ND is refused, because ND
forbids the resize every image goes through and NC puts a condition on the whole
site. See `docs/image-credits.md`.

## Vocabulary

```jsonc
{
  "term": "to indict",        // dictionary form, with its article or "to"
  "definition": "to charge somebody formally with a crime",
  "match": "held public office"   // optional: pin the exact surface form
}
```

The builder highlights the first occurrence of each headword in the passage and
hangs the definition off it, and the same list prints as **Key Vocabulary**,
which is also what a screen reader reads (each highlight carries
`aria-describedby` pointing at its entry). A headword that never matches its own
passage is defined and never shown — `check_content.py` reports it. Use `match`
when the passage uses a form the inflection rules cannot reach, or when a word
has two senses and the wrong one is being claimed.

### Choosing the words

The students are Portuguese speakers, which changes what is worth a line:

- **Skip transparent cognates.** `information`, `traditional`, `communication`,
  `cultural` are free to a Brazilian reader. Glossing them spends a line and
  teaches nothing.
- **Prefer false friends.** `eventually` is not *eventualmente*; `ordinary` is
  not *ordinário*; `to support` is not *suportar*. These look easy, so no
  difficulty heuristic will ever select them, and they are where a reader
  misunderstands a sentence while feeling certain they understood it. House
  style marks them: `"normal, usual — careful: it is not an insult"`.
- **Prefer the Germanic and the idiomatic** — phrasal verbs, collocations,
  everyday concrete words — over Latinate abstractions.

`scripts/check_vocabulary.py` reports all three for every text.

### How many

| Level | A1 | A2 | B1 | B2 | C1 | C2 |
|---|---|---|---|---|---|---|
| Entries | 5–8 | 6–10 | 8–12 | 10–15 | 10–16 | 10–18 |

Guidance, not a rule. A text with a genuinely technical subject earns more; no
text should be padded to reach a number.

## English variety

American English is the house variety: the voices are en-US and the collection
is American. `scripts/check_dialect.py` normalises spelling (`organise` →
`organize`, `centre` → `center`, `metre` → `meter`) and deliberately leaves word
choice alone — `rubbish`/`trash`, `flat`/`apartment`, `lift`/`elevator` carry
meaning and are worth teaching as variants. It prints those for a decision.

Anything that rewrites a passage changes what the narrator says, so
`generate_reading_audio.py` has to run afterwards. Staleness is fingerprinted on
the narration text, so it re-records exactly the files that changed.
