# Curriculum data schema (v1)

Single source of truth for lesson content, going forward. Each lesson is one
JSON file at `curriculum/{level}/{lesson-id}.json`. `curriculum/index.json`
lists every level's units and the lesson ids that belong to each, in order,
with prerequisites -- this is what lets a level page, the search index, and
`worker/course-catalog.json` all be generated instead of hand-maintained.

This schema is deliberately close to the *content* every existing A1 lesson
page already has (Objectives / Explanation / Rules / Examples / Common
Mistakes / Practice / Summary / Related) -- see `levels/a1/to-be-am-is-are.html`
for the hand-authored reference this schema was reverse-engineered from.
`exercises` items use the exact schema `assets/js/exercises.js` already reads
(see its own header comment) -- nothing about the exercise engine changes.

## Lesson JSON shape

```jsonc
{
  "id": "c1-complex-subordinate-clauses",   // matches the generated filename
  "level": "C1",
  "unit": "1",                // curriculum/index.json unit number this belongs to
  "order": 2,                 // position within the unit
  "skill": "grammar",         // grammar | vocabulary | pronunciation | reading
                               // | listening | speaking | writing | functional
  "strand": "subordination",  // free-text grouping used for prerequisite/related lookups
  "title": "Complex Subordinate Clauses",
  "subtitle": "Link ideas with precision using concessive, purpose and result clauses.",
  "prerequisites": ["b2-concessive-clauses"],   // lesson ids; [] if none
  "objectives": [
    "Use concessive, purpose and result clauses accurately",
    "..."
  ],
  "content": {
    "intro": "One short paragraph, same role as the A1 template's italic intro.",
    "explanation": "<p>...</p>",     // may contain inline HTML (strong/em), no block tags
    "rules": [ { "heading": "a) Concessive clauses", "body": "<p>...</p>" }, ... ],
    "examples": ["Even though she was exhausted, she finished the marathon.", ...],
    "commonMistakes": [
      { "wrong": "...", "right": "...", "why": "..." }
    ]
  },
  "exercises": [ /* verbatim assets/js/exercises.js exercise-data objects */ ],
  "summary": ["One-line takeaway", "..."],
  "related": [ { "lessonId": "c1-advanced-conditional-forms", "label": "Advanced Conditional Forms" } ],
  "sourceMaterial": {
    "docx": "cefr/c1-advanced/complex-subordinate-clauses.docx",
    "txt": "cefr/c1-advanced/complex-subordinate-clauses.txt",
    "pdf": "cefr/c1-advanced/complex-subordinate-clauses.pdf"
  }
}
```

## `curriculum/index.json` shape

```jsonc
{
  "levels": {
    "C1": {
      "units": [
        {
          "id": "1",
          "title": "Advanced Passive & Subordination",
          "lessons": ["c1-advanced-passive-structures", "c1-complex-subordinate-clauses"]
        }
      ]
    }
  }
}
```

`status` on a unit/lesson entry is one of `"published"` (has a generated HTML
page + is linked from its level page), `"drafted"` (JSON exists, not yet
built/published), or `"planned"` (identified in the gap analysis, no JSON
yet). This lets partial progress be tracked honestly instead of the index
silently claiming more is done than actually is.

## Build

`python3 scripts/build_lesson.py curriculum/{level}/{lesson-id}.json` renders
one lesson to `levels/{level}/{lesson-id}.html`, reusing the exact header/
footer/AI-Teacher-panel markup already on every page (via `scripts/site_chrome.py`)
so a generated page is visually identical to a hand-written one.
