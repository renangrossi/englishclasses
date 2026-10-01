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
import tag_grammar
import site_chrome

REL = ""
OUT = rc.REPO_ROOT / "exercises.html"
MAP = rc.REPO_ROOT / "docs" / "reading-library-map.json"

DOC_SVG = ('<svg class="" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" '
           'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
           '<path d="M6 2h9l5 5v13a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2Z"/><path d="M15 2v5h5"/></svg>')
WORD_SVG = DOC_SVG.replace('<path d="M15 2v5h5"/>', '<path d="M15 2v5h5"/><path d="M8 15h8"/>')
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


# Within a level the cards are grouped by topic, in the order a student would
# most likely want them: the everyday situations first, then the things you do
# with other people, then work, then the wider subjects. Anything not listed
# here sorts to the end alphabetically rather than disappearing.
TOPIC_ORDER = ["everyday", "food", "travel", "sports", "culture", "society",
               "work", "interviews", "business", "tech", "literature", "review"]


def topic_rank(topic):
    return TOPIC_ORDER.index(topic) if topic in TOPIC_ORDER else len(TOPIC_ORDER)


def tag_list(d):
    """Every tag a card can be filtered by: its subject topic, then the grammar
    points detected in its passage (see scripts/tag_grammar.py)."""
    return [f"topic:{d.get('topic','')}"] + [f"g:{g}" for g in (d.get("grammar") or [])]


def built_card(level, slug, d, n):
    """A converted text. Its own source JSON is the truth about what exists --
    which is what makes splits (one source -> several pages) and merges
    (several sources -> one page) list correctly."""
    page = f"reading/{level}/{slug}.html"
    # One button and nothing else. The genre, the running time and an "Audio"
    # badge used to sit under it on their own line, which crowded the card for
    # information the reading page itself states the moment you open it.
    return (f'<article class="lesson-card" id="ex-{esc(slug)}" '
            f'data-tags="{esc(" ".join(tag_list(d)))}">'
            f'<span class="lesson-card__index" aria-hidden="true">{roman(n)}</span>'
            f"<h3>{esc(d['title'])}</h3><p>{esc(d['subtitle'])}</p>"
            f'<div class="lesson-card__actions">'
            f'<a class="btn btn--accent btn--small" href="{page}">{READ_SVG}Read &amp; Listen</a></div>'
            f"</article>")


def pending_card(t, n):
    """A text still waiting to be converted. It keeps a link to the document it
    currently lives in, so nothing is unreachable mid-migration."""
    slug = t["slug"]
    title = t.get("card_title") or slug.replace("-", " ").title()
    desc = t.get("card_desc", "")
    cid = t.get("card_id") or t.get("source_slug") or slug
    actions = []
    for f in t.get("source_files", []):
        if f.endswith(".pdf"):
            actions.append(f'<a class="btn btn--ghost btn--small" href="{f}" target="_blank" rel="noopener">{DOC_SVG}Open PDF</a>')
        elif f.endswith(".docx"):
            actions.append(f'<a class="btn btn--ghost btn--small" href="{f}" target="_blank" rel="noopener">{WORD_SVG}Open Word</a>')
    desc_html = f"<p>{esc(desc)}</p>" if desc else ""
    return (f'<article class="lesson-card" id="ex-{esc(cid)}">'
            f'<span class="lesson-card__index" aria-hidden="true">{roman(n)}</span>'
            f"<h3>{esc(title)}</h3>{desc_html}"
            f'<div class="lesson-card__actions">{"".join(actions)}</div>'
            f'<p class="lesson-card__meta" style="color:var(--color-text-muted);font-size:var(--step--1);margin-top:auto;">Not yet converted</p>'
            f"</article>")


def filter_bar(code, built):
    """The tags a student can click, in place of the three lines of prose this
    replaced. A tag is only offered if at least two texts in this level carry
    it: a filter that returns a single card is a worse answer than not being
    offered the question, and it makes the level look thinner than it is.
    Subject topics come first because that is what most people browse by."""
    from collections import Counter
    counts = Counter(t for _, _, d in built for t in tag_list(d))
    topics = [(t, n) for t, n in counts.items() if t.startswith("topic:") and n >= 2]
    gram = [(t, n) for t, n in counts.items() if t.startswith("g:") and n >= 2]
    topics.sort(key=lambda x: (topic_rank(x[0].split(":", 1)[1]), x[0]))
    gram.sort(key=lambda x: (-x[1], x[0]))
    if not topics and not gram:
        return ""

    def chip(tag, n, label):
        return (f'<button type="button" class="tag-chip" data-tag="{esc(tag)}" '
                f'aria-pressed="false">{esc(label)}'
                f'<span class="tag-chip__n">{n}</span></button>')

    groups = ""
    if topics:
        groups += ('<div class="tag-row"><span class="tag-row__label">Subject</span>'
                   + "".join(chip(t, n, rc.TOPIC_LABELS.get(t.split(":", 1)[1], t.split(":", 1)[1].title()))
                             for t, n in topics) + "</div>")
    if gram:
        groups += ('<div class="tag-row"><span class="tag-row__label">Grammar</span>'
                   + "".join(chip(t, n, tag_grammar.LABELS.get(t.split(":", 1)[1], t.split(":", 1)[1]))
                             for t, n in gram) + "</div>")
    return (f'<div class="tag-filter" data-tag-filter="{esc(code)}">{groups}'
            f'<p class="tag-filter__status" data-tag-status role="status">'
            f'Showing all {len(built)} texts.</p>'
            f'<button type="button" class="tag-filter__clear" data-tag-clear hidden>Clear filters</button>'
            f"</div>")


def level_section(code, built, pending, n_start):
    info = LEVEL_INFO[code]
    n = n_start
    # One grid per topic, under its own heading. "built" is already sorted by
    # topic, so walking it in order is enough to group it.
    groups, blocks = [], []
    for level, slug, d in built:
        t = d.get("topic", "")
        if not groups or groups[-1][0] != t:
            groups.append((t, []))
        groups[-1][1].append((level, slug, d))
    for topic, rows in groups:
        cards = []
        for level, slug, d in rows:
            cards.append(built_card(level, slug, d, n)); n += 1
        label = rc.TOPIC_LABELS.get(topic, topic.title() or "Other")
        blocks.append(f'<h3 class="topic-group">{esc(label)}</h3>'
                      f'<div class="grid">{"".join(cards)}</div>')
    if pending:
        cards = []
        for t in pending:
            cards.append(pending_card(t, n)); n += 1
        blocks.append('<h3 class="topic-group">Not yet converted</h3>'
                      f'<div class="grid">{"".join(cards)}</div>')
    done, texts = len(built), built + pending
    return n, f"""<section class="section" id="level-{code}" aria-labelledby="h-{code}">
        <div class="section__inner">
            <p class="eyebrow">{code.upper()} &middot; {info['name']}</p>
            <h2 id="h-{code}">{info['name']} &mdash; {len(texts)} text{'s' if len(texts) != 1 else ''}</h2>
            <p class="section__head" style="max-width:66ch;">{info['blurb']}</p>
            {filter_bar(code, built)}
            {''.join(blocks)}
        </div>
    </section>"""


def main():
    # What exists on the site: every built reading page, from its own source.
    built = {c: [] for c in LEVEL_INFO}
    for level, slug, d in rc.all_sources():
        built.setdefault(level, []).append((level, slug, d))
    for c in built:
        # Level, then topic, then the text's own "order" if it declares one.
        # A1 is a deliberate sequence -- "A Tuesday" recycles the other five and
        # has to come last -- so alphabetical would actively mislead there.
        # Anything without "order" keeps sorting by title, as it always did.
        built[c].sort(key=lambda x: (topic_rank(x[2].get("topic", "")),
                                     x[2].get("order", 10**6),
                                     x[2]["title"].lower()))

    # What is still waiting: map entries not yet converted or merged away.
    T = [t for t in json.loads(MAP.read_text(encoding="utf-8"))["texts"]
         if t["action"] != "DELETE" and t["level"] != "n/a"
         and t.get("status") not in ("IMPLEMENTED", "MERGED")]
    pending = {c: [] for c in LEVEL_INFO}
    for t in sorted(T, key=lambda t: (t.get("card_title") or t["slug"]).lower()):
        pending.setdefault(t["level"].lower(), []).append(t)

    done = sum(len(v) for v in built.values())
    pending_note = ""  # only shown while a conversion backlog actually exists
    total = done + sum(len(v) for v in pending.values())
    by_level = {c: built.get(c, []) + pending.get(c, []) for c in LEVEL_INFO}
    if total > done:
        pending_note = (f"{done} are ready to read now; the rest are still in their "
                        f"original documents while they are converted. ")

    title = "Reading & Listening Library — Renan the Teacher"
    description = ("A CEFR-levelled library of reading and listening texts for English learners — "
                   "A1 to C2, each with audio, vocabulary and interactive exercises.")
    breadcrumb = ('<li><a href="index.html">Home</a></li>'
                  '<li aria-current="page">Reading Library</li>')

    # The code alone ("B2") says nothing to a student who does not already know
    # the CEFR ladder, which is exactly the student most likely to be using this.
    jump = "".join(f'<a href="#level-{c}"><strong>{c.upper()}</strong> {esc(LEVEL_INFO[c]["name"])}</a>'
                   for c in by_level if by_level[c])

    sections = []
    n = 1
    for c in ["a1", "a2", "b1", "b2", "c1", "c2"]:
        if by_level[c]:
            n, sec = level_section(c, built.get(c, []), pending.get(c, []), n)
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
                <p class="page-header__lede">{total} texts, ordered the way you would actually learn them &mdash; A1 through C2. Every reading has a recording, vocabulary and exercises you can check yourself, and a Print / Save as PDF button. {pending_note}Use the tags under each level to find texts by subject or by the grammar they practice.</p>
            </div>
            <img class="page-header__badge" src="assets/img/badges/badge-single-star.webp" alt="" width="88" height="88" loading="lazy">
        </div>
    </div>
<div class="level-toc"><div class="level-toc__inner">{jump}</div></div>
<div class="section section--tight" style="padding-bottom:0;"><div class="section__inner"><img class="section-banner" src="assets/img/the-boxers-(1954),-by-william-george.jpg" alt="" loading="lazy"></div></div>""",
        *sections,
        # Only this page has the filter, so the script is injected here rather
        # than added to the chrome every page on the site shares.
        site_chrome.footer(REL).replace(
            "</body>", f'    <script src="{REL}assets/js/tag-filter.js"></script>\n</body>'),
    ]
    OUT.write_text("\n".join(out), encoding="utf-8")
    print(f"exercises.html: {total} texts across {sum(1 for v in by_level.values() if v)} levels, "
          f"{done} implemented")
    for c in ["a1", "a2", "b1", "b2", "c1", "c2"]:
        if by_level[c]:
            print(f"  {c.upper():5} {len(by_level[c]):3}  ({len(built.get(c, []))} ready)")


STAR = ('<svg class="stars-row__star" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
        '<path d="M12 17.27 18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21Z"/></svg>')
STARS = STAR * 13

if __name__ == "__main__":
    main()
