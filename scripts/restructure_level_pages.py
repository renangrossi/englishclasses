#!/usr/bin/env python3
"""
Restructure levels/{a1,a2,b1,b2,c1,c2}.html so the interactive-lesson grid
(currently named "Exercises") becomes the primary "Lessons" section (same
#exercises id, matching the existing levels/pre-a1.html convention of
id="exercises" + heading "Lessons"), and the original grid is preserved,
renamed "Extra Exercises", stripped of duplicate "open the lesson" links
(since that navigation now lives in Lessons), and moved to right after
Speaking and right before Revision.

Nothing under #test-yourself, #vocabulary, #reading, #listening, #writing,
#speaking or #revision is touched -- this only splits and repositions the
one "Exercises" section. Does NOT touch levels/pre-a1.html (already in the
target shape) or any levels/{level}/test-yourself.html page.

Usage:
    python3 scripts/restructure_level_pages.py
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CARD_RE = re.compile(r'<article class="lesson-card">.*?</article>', re.S)
TITLE_LINK_RE = re.compile(r'<h3><a class="lesson-card__title-link"[^>]*>([^<]+)</a></h3>')
ACTIONS_RE = re.compile(r'<div class="lesson-card__actions">.*?</div>', re.S)
INDEX_SPAN_RE = re.compile(r'(<span class="lesson-card__index" aria-hidden="true">)[^<]+(</span>)')

ROMAN = [(1000,"M"),(900,"CM"),(500,"D"),(400,"CD"),(100,"C"),(90,"XC"),(50,"L"),
         (40,"XL"),(10,"X"),(9,"IX"),(5,"V"),(4,"IV"),(1,"I")]


def to_roman(n):
    out = []
    for val, sym in ROMAN:
        while n >= val:
            out.append(sym)
            n -= val
    return "".join(out)


def restructure(level_slug, level_code):
    path = REPO_ROOT / "levels" / f"{level_slug}.html"
    text = path.read_text(encoding="utf-8")

    m = re.search(r'<section id="exercises".*?</section>', text, re.S)
    assert m, f"no #exercises section in {path}"
    old_section = m.group(0)

    cards = CARD_RE.findall(old_section)
    lesson_cards = []
    extra_cards = []
    for card in cards:
        title_match = TITLE_LINK_RE.search(card)
        if title_match:
            lessons_card = ACTIONS_RE.sub("", card)
            lesson_cards.append(lessons_card)
            extra_cards.append(card)  # unchanged: kept fully, incl. its own PDF link
        else:
            extra_cards.append(card)  # PDF-only card (e.g. B2 mixed reviews): Extra only

    # Renumber the Lessons cards I, II, III... (Extra Exercises keeps its
    # original, still-contiguous numbering, since no cards are removed
    # from it).
    renumbered = []
    for i, card in enumerate(lesson_cards, start=1):
        renumbered.append(INDEX_SPAN_RE.sub(rf'\g<1>{to_roman(i)}\g<2>', card, count=1))
    lesson_cards = renumbered

    # Extra Exercises: strip the duplicate "open the lesson" title-link,
    # leaving a plain heading (the PDF/Word download button is still the
    # section's own link).
    extra_cards = [TITLE_LINK_RE.sub(r'<h3>\1</h3>', card) for card in extra_cards]

    n_lessons = len(lesson_cards)
    lessons_section = f"""<section id="exercises" class="section section--surface" aria-labelledby="grammar-heading">
        <div class="section__inner">
            <div class="section__head">
                <p class="eyebrow">{level_code}</p>
                <h2 id="grammar-heading">Lessons</h2>
                <p>{n_lessons} lesson{'s' if n_lessons != 1 else ''}, in order &mdash; each one builds on the one before it.</p>
            </div>
            <div class="grid">{''.join(lesson_cards)}</div>
        </div>
    </section>"""

    extra_section = f"""<section id="extra-exercises" class="section section--surface" aria-labelledby="extra-exercises-heading">
        <div class="section__inner">
            <div class="section__head">
                <p class="eyebrow">{level_code}</p>
                <h2 id="extra-exercises-heading">Extra Exercises</h2>
                <p>Supplementary worksheets from the original course material, for extra practice beyond the interactive lessons above.</p>
            </div>
            <div class="grid">{''.join(extra_cards)}</div>
        </div>
    </section>"""

    # 1) Replace the old #exercises section with just the new Lessons section.
    text = text.replace(old_section, lessons_section, 1)

    # 2) Insert Extra Exercises right after #speaking, right before #revision.
    speaking_m = re.search(r'<section id="speaking".*?</section>', text, re.S)
    assert speaking_m, f"no #speaking section in {path}"
    insert_at = speaking_m.end()
    text = text[:insert_at] + "\n" + extra_section + text[insert_at:]

    # 3) Update the quick-nav TOC: "Exercises" -> "Lessons", add "Extra
    # Exercises" between Speaking and Revision.
    text = text.replace('<a href="#exercises">Exercises</a>', '<a href="#exercises">Lessons</a>', 1)
    text = text.replace(
        '<a href="#speaking">Speaking</a><a href="#revision">Revision</a>',
        '<a href="#speaking">Speaking</a><a href="#extra-exercises">Extra Exercises</a><a href="#revision">Revision</a>',
        1,
    )

    path.write_text(text, encoding="utf-8")
    print(f"Restructured {path.relative_to(REPO_ROOT)}: {n_lessons} lessons, {len(extra_cards)} extra-exercise cards")


def main():
    for slug, code in [("a1", "A1"), ("a2", "A2"), ("b1", "B1"), ("b2", "B2"), ("c1", "C1"), ("c2", "C2")]:
        restructure(slug, code)


if __name__ == "__main__":
    main()
