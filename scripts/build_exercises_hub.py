#!/usr/bin/env python3
"""
Generate exercises.html: the reading & listening library hub.

Replaces what was a flat alphabetical grid of 97 "Open PDF" cards -- which
told a student nothing about difficulty or order -- with the CEFR progression
A1 -> A2 -> B1 -> B2 -> C1 -> C2, each level carrying a short description, the
English it practices, its topics, and its texts.

Data comes from docs/reading-library-map.json, so the hub cannot drift from
the audit: a text whose status is IMPLEMENTED links to its reading page, and
one that is not yet converted still links to its source document. Re-run this
after every conversion batch.

Usage:
    python3 scripts/build_exercises_hub.py
"""
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reading_common as rc
import site_chrome

REL = ""
OUT = rc.REPO_ROOT / "exercises.html"
MAP = rc.REPO_ROOT / "docs" / "reading-library-map.json"

DOC_SVG = ('<svg class="" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" '
           'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
           '<path d="M6 2h9l5 5v13a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2Z"/><path d="M15 2v5h5"/></svg>')
WORD_SVG = DOC_SVG.replace('<path d="M15 2v5h5"/>', '<path d="M15 2v5h5"/><path d="M8 15h8"/>')
AUDIO_SVG = ('<svg class="" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" '
             'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
             '<path d="M3 12h2v2H3zM7 8h2v10H7zM11 5h2v16h-2zM15 9h2v8h-2zM19 11h2v4h-2z"/></svg>')
READ_SVG = ('<svg class="" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>'
            '<path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2Z"/></svg>')

# Requirement 18: each level says what it is, what English it practices and
# what it covers -- without burying the student in detail.
LEVEL_INFO = {
    "a1": {
        "name": "Beginner",
        "blurb": "Short, slow texts about everyday life, built from the few hundred words a beginner "
                 "actually has. Every sentence is one idea.",
        "practices": "Present simple, <em>to be</em>, basic questions, numbers and times",
        "topics": "Daily routines, family, food and shopping, getting around",
    },
    "a2": {
        "name": "Elementary",
        "blurb": "Everyday situations you can now tell a story about &mdash; what happened yesterday, "
                 "what you are doing next week &mdash; in short, natural paragraphs.",
        "practices": "Simple past, present continuous, comparatives, plans with <em>going to</em>",
        "topics": "Markets and stores, travel and hotels, restaurants, chores, festivals",
    },
    "b1": {
        "name": "Intermediate",
        "blurb": "The working core of the library. Real situations at work and abroad, with the "
                 "phrasal verbs and collocations that make English sound less like a textbook.",
        "practices": "Present perfect, past continuous, conditionals, phrasal verbs, reported speech",
        "topics": "Business travel, workplace English, American sports and culture, food, technology",
    },
    "b2": {
        "name": "Upper Intermediate",
        "blurb": "Longer texts that argue a point or follow a situation through to its consequences, "
                 "and the professional register that goes with them.",
        "practices": "Passive voice, perfect aspects, modality, register and connectors",
        "topics": "International business, job interviews, negotiation, media, cultural difference",
    },
    "c1": {
        "name": "Advanced",
        "blurb": "Dense, genuinely adult prose &mdash; analysis, narrative and technical writing that "
                 "does not slow down for the reader.",
        "practices": "Nuanced modality, complex subordination, inference, tone and implication",
        "topics": "Executive communication, markets and strategy, society, long-form narrative",
    },
    "c2": {
        "name": "Proficient",
        "blurb": "Only what genuinely belongs here: texts that turn on irony, implication or "
                 "register rather than on difficult vocabulary.",
        "practices": "Idiom, irony, register shift, argument built across paragraphs",
        "topics": "Nuanced professional and cultural writing",
    },
}

GENRE_NOTE = {
    "drill": "Grammar practice",
    "discussion": "Speaking prompts",
    "reference": "Reference",
    "dialogue": "Dialogue",
    "reading": "Reading",
}


def esc(s):
    return html.escape(str(s), quote=False)


def roman(n):
    vals = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
            (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
    out = ""
    for v, r in vals:
        while n >= v:
            out += r
            n -= v
    return out


def card(t, n):
    """One text. Links to its reading page once converted; until then, to the
    source document it still lives in."""
    slug = t["slug"]
    level = t["level"].lower()
    title = t.get("card_title") or slug.replace("-", " ").title()
    desc = t.get("card_desc", "")
    cid = t.get("card_id") or t.get("source_slug") or slug
    actions = []

    if t.get("status") == "IMPLEMENTED" and t.get("page"):
        actions.append(f'<a class="btn btn--accent btn--small" href="{t["page"]}">{READ_SVG}Read &amp; Listen</a>')
        note = GENRE_NOTE.get(t.get("genre", ""), "")
        badge = f'<span class="badge badge--audio">{AUDIO_SVG}Audio</span>' if t["audio"] != "n/a" else ""
    else:
        for f in t.get("source_files", []):
            if f.endswith(".pdf"):
                actions.append(f'<a class="btn btn--ghost btn--small" href="{f}" target="_blank" rel="noopener">{DOC_SVG}Open PDF</a>')
            elif f.endswith(".docx"):
                actions.append(f'<a class="btn btn--ghost btn--small" href="{f}" target="_blank" rel="noopener">{WORD_SVG}Open Word</a>')
        badge = ""
        note = "Not yet converted"

    note_html = f'<p class="lesson-card__meta" style="color:var(--color-text-muted);font-size:var(--step--1);margin-top:auto;">{esc(note)}{badge}</p>' if note else ""
    desc_html = f"<p>{esc(desc)}</p>" if desc else ""
    return (f'<article class="lesson-card" id="ex-{esc(cid)}">'
            f'<span class="lesson-card__index" aria-hidden="true">{roman(n)}</span>'
            f"<h3>{esc(title)}</h3>{desc_html}"
            f'<div class="lesson-card__actions">{"".join(actions)}</div>{note_html}'
            f"</article>")


def level_section(code, texts, n_start):
    info = LEVEL_INFO[code]
    cards = []
    n = n_start
    for t in texts:
        cards.append(card(t, n))
        n += 1
    done = sum(1 for t in texts if t.get("status") == "IMPLEMENTED")
    return n, f"""<section class="section" id="level-{code}" aria-labelledby="h-{code}">
        <div class="section__inner">
            <p class="eyebrow">{code.upper()} &middot; {info['name']}</p>
            <h2 id="h-{code}">{info['name']} &mdash; {len(texts)} text{'s' if len(texts) != 1 else ''}</h2>
            <p class="section__head" style="max-width:66ch;">{info['blurb']}</p>
            <ul class="summary-list" style="max-width:66ch;margin-bottom:var(--space-lg);">
                <li><strong>English you practice:</strong> {info['practices']}</li>
                <li><strong>Topics:</strong> {info['topics']}</li>
                <li><strong>Ready to read now:</strong> {done} of {len(texts)}</li>
            </ul>
            <div class="grid">{''.join(cards)}</div>
        </div>
    </section>"""


def main():
    T = [t for t in json.loads(MAP.read_text(encoding="utf-8"))["texts"]
         if t["action"] != "DELETE" and t["level"] != "n/a"]
    # A merge source stays listed (and reachable) until its merge target is
    # actually built; at that point the source's status becomes MERGED and the
    # target's own entry represents it. Filtering on merge_into alone would
    # have hidden 16 not-yet-converted texts behind a page that does not exist.
    T = [t for t in T if t.get("status") != "MERGED"]

    by_level = {c: [] for c in ["a1", "a2", "b1", "b2", "c1", "c2"]}
    for t in sorted(T, key=lambda t: (t.get("card_title") or t["slug"]).lower()):
        by_level.setdefault(t["level"].lower(), []).append(t)

    total = sum(len(v) for v in by_level.values())
    done = sum(1 for t in T if t.get("status") == "IMPLEMENTED")

    title = "Reading & Listening Library — Renan the Teacher"
    description = ("A CEFR-levelled library of reading and listening texts for English learners — "
                   "A1 to C2, each with audio, vocabulary and interactive exercises.")
    breadcrumb = ('<li><a href="index.html">Home</a></li>'
                  '<li aria-current="page">Reading Library</li>')

    jump = "".join(f'<a href="#level-{c}">{c.upper()}</a>' for c in by_level if by_level[c])

    sections = []
    n = 1
    for c in ["a1", "a2", "b1", "b2", "c1", "c2"]:
        if by_level[c]:
            n, sec = level_section(c, by_level[c], n)
            sections.append(sec)

    out = [
        site_chrome.head(REL, title, description, page_path="exercises.html"),
        site_chrome.header(REL, "", breadcrumb),
        f"""<div class="page-header">
        <div class="stars-row stars-row--onlight" aria-hidden="true">{STARS}</div>
        <div class="page-header__inner">
            <div class="page-header__text">
                <p class="eyebrow hero__eyebrow">Practice Library</p>
                <h1>Reading &amp; Listening Library</h1>
                <p class="page-header__lede">{total} texts, ordered the way you would actually learn them &mdash; A1 through C2. Every reading has a recording, vocabulary and exercises you can check yourself, and a Print / Save as PDF button. {done} are ready to read now; the rest are still in their original documents while they are converted.</p>
            </div>
            <img class="page-header__badge" src="assets/img/badges/badge-single-star.webp" alt="" width="88" height="88" loading="lazy">
        </div>
    </div>
<div class="level-toc"><div class="level-toc__inner">{jump}</div></div>
<div class="section section--tight" style="padding-bottom:0;"><div class="section__inner"><img class="section-banner" src="assets/img/the-boxers-(1954),-by-william-george.jpg" alt="" loading="lazy"></div></div>""",
        *sections,
        site_chrome.footer(REL),
    ]
    OUT.write_text("\n".join(out), encoding="utf-8")
    print(f"exercises.html: {total} texts across {sum(1 for v in by_level.values() if v)} levels, "
          f"{done} implemented")
    for c, v in by_level.items():
        if v:
            print(f"  {c.upper():5} {len(v):3}  ({sum(1 for t in v if t.get('status')=='IMPLEMENTED')} ready)")


STAR = ('<svg class="stars-row__star" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
        '<path d="M12 17.27 18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21Z"/></svg>')
STARS = STAR * 13

if __name__ == "__main__":
    main()
