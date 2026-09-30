#!/usr/bin/env python3
"""
Build reading/{level}/{slug}.html from content/readings/{level}/{slug}.json.

Deliberately separate from scripts/build_lesson.py: that script builds the
grammar lessons from curriculum/*.json, and re-running it on an existing
lesson destroys enrichment those built pages hold but their JSON no longer
does. Nothing here touches levels/ or curriculum/.

Page shape (reusing the site's existing components verbatim -- no new CSS,
no new JS):

    page-header          level eyebrow + title + lede
    level-toc            jump links
    #listen-and-read     <audio controls> then the passage
    #vocabulary          optional word list
    #practice            .exercise-block JSON for assets/js/exercises.js
    #discussion          optional speaking/writing prompts

Usage:
    python3 scripts/build_reading_page.py                      # build all
    python3 scripts/build_reading_page.py b1/nfl               # build one
"""
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reading_common as rc
import site_chrome

REL = "../../"
STAR = ('<svg class="" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
        '<path d="m12 2 2.9 6.9 7.1.6-5.4 4.7 1.6 7L12 17.5 5.8 21.2l1.6-7L2 9.5l7.1-.6Z"/></svg>')
STARS_ROW = f'<div class="stars-row stars-row--onlight" aria-hidden="true">{STAR * 11}</div>'
PRINTER_SVG = ('<svg class="" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" '
               'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
               '<path d="M6 9V2h12v7"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/>'
               '<path d="M6 14h12v8H6Z"/></svg>')
# The reading page *is* the document now -- the per-text PDFs it replaced have
# been deleted -- so every page carries its own "Print / Save as PDF".
PRINT_BTN = (f'<button type="button" class="btn btn--ghost btn--small print-hidden" data-print-page>'
             f'{PRINTER_SVG}Print / Save as PDF</button>')


def esc(s):
    return html.escape(str(s), quote=False)


def _surface_patterns(term):
    """Regexes for the ways a glossary headword can appear in running text.

    A vocabulary list is written in dictionary form -- "to grind", "a bye
    week", "try something on", "check in / check out", "It's worth (doing)" --
    but the passage contains the inflected, article-less, separated thing:
    "grinding", "bye week", "try it on", "checked in", "it is worth knowing".
    So each headword becomes a set of patterns, longest-first.

    Placeholders matter most: an English phrasal verb splits around its object
    ("cheer someone up" -> "cheer you up"), which a literal search can never
    find."""
    pats = []
    for alt in re.split(r"\s*/\s*", term):
        alt = alt.strip().strip("\u2026.?!\u2019'\"")
        alt = re.sub(r"\s*\(.*?\)\s*", " ", alt).strip()
        alt = re.sub(r"^(to|a|an|the)\s+", "", alt, flags=re.I).strip()
        if len(alt) < 3:
            continue
        words = alt.split()
        head, rest = words[0], words[1:]

        # "it's" also appears written out as "it is"
        heads = {head}
        if head.lower() == "it's":
            heads |= {"it is"}

        # inflections of the first word, which is the one that changes
        forms = set()
        for h in heads:
            forms |= {h, h + "s", h + "es", h + "ed", h + "d", h + "ing",
                      h + "er", h + "est"}
            if len(h) > 3 and h.endswith("e"):
                forms |= {h[:-1] + "ing", h[:-1] + "er", h[:-1] + "est"}
            if len(h) > 3 and h.endswith("y"):
                forms |= {h[:-1] + "ies", h[:-1] + "ied", h[:-1] + "ier"}
        IRREG = {"be": ["is", "are", "was", "were", "been", "'re", "'s", "'m"],
                 "tell": ["told"], "speak": ["spoke", "spoken"],
                 "take": ["took", "taken"], "get": ["got", "gotten"],
                 "have": ["has", "had"], "make": ["made"], "go": ["went", "gone"],
                 "leave": ["left"], "hold": ["held"], "buy": ["bought"],
                 "find": ["found"], "eat": ["ate", "eaten"], "good": ["better", "best"]}
        for h in list(heads):
            forms |= set(IRREG.get(h.lower(), []))

        # the rest of the phrase, with placeholders opened up
        tail = []
        for w in rest:
            if w.lower().strip(".,") in ("something", "someone", "somebody", "sth", "sb"):
                tail.append(r"\s+\S+")          # whatever the real object is
            else:
                tail.append(r"\s+" + re.escape(w))
        tail_re = "".join(tail)

        for f in sorted(forms, key=len, reverse=True):
            pats.append((len(alt), r"(?<![\w-])(" + re.escape(f).replace(r"\ ", r"\s+") + tail_re + r")(?![\w-])"))

        # "to be out of something" carries its meaning in the tail, and the
        # copula is usually contracted onto the subject ("we're out of..."),
        # where a leading word-boundary can never match. Match the tail alone.
        if head.lower() == "be" and rest:
            core = []
            for w in rest:
                if w.lower().strip(".,") in ("something", "someone", "somebody", "sth", "sb"):
                    break
                core.append(re.escape(w))
            if core:
                pats.append((len(alt), r"(?<![\w-])(" + r"\s+".join(core) + r")(?![\w-])"))

        # In a noun phrase it is the LAST word that pluralizes, not the first:
        # "a fitting room" appears as "fitting rooms".
        if rest and not any(r"\S+" in t for t in tail):
            last = rest[-1]
            stem = r"(?<![\w-])(" + re.escape(head) + "".join(tail[:-1]) + r"\s+" + re.escape(last)
            for suf in ("s", "es"):
                pats.append((len(alt), stem + suf + r")(?![\w-])"))
    return [p for _, p in sorted(set(pats), key=lambda x: -x[0])]


def annotate(paras, vocab):
    """Bold the first occurrence of each glossary word in the passage and hang
    its definition off it, so the reader can hover (or tap, or tab to) the word
    instead of consulting a separate list. Reuses the site's existing
    .vocab-term style, which was defined in exercises.css and never used.

    Each term is marked at most once, across the whole passage -- marking every
    occurrence would turn a page into a field of underlines."""
    # A glossary entry may pin the exact surface form to highlight via "match".
    # Auto-matching cannot tell senses apart: "to exchange" (return goods)
    # happily attached itself to "exchanges" meaning conversations, so the
    # author needs a way to say which word is meant.
    todo = []
    for v in (vocab or []):
        if v.get("match"):
            pats = [r"(?<![\w-])(" + re.escape(v["match"]).replace(r"\ ", r"\s+") + r")(?![\w-])"]
        else:
            pats = _surface_patterns(v["term"])
        todo.append((v["term"], v["definition"], pats))
    out = []
    placed = set()
    slot = []  # rendered spans, substituted back after escaping

    for para in paras:
        text = para
        # An all-caps line is a section heading inside the passage, not prose.
        # Highlighting a word there produced "1. BOOKING A FLIGHT BY PHONE"
        # with the definition hanging off the heading itself.
        letters = [c for c in para if c.isalpha()]
        if letters and sum(c.isupper() for c in letters) / len(letters) > 0.6:
            out.append(text)
            continue
        # Find, for this paragraph, the earliest match of any unplaced term.
        while True:
            best = None
            for term, definition, forms in todo:
                if term in placed:
                    continue
                for pat in forms:
                    m = re.search(pat, text, re.I)
                    if m and (best is None or m.start() < best[0].start()):
                        best = (m, term, definition)
                        break
            if best is None:
                break
            m, term, definition = best
            placed.add(term)
            token = f"\x00{len(slot)}\x00"
            slot.append((m.group(1), definition))
            text = text[:m.start()] + token + text[m.end():]
        out.append(text)

    rendered = []
    for text in out:
        t = esc(text)
        for i, (word, definition) in enumerate(slot):
            t = t.replace(
                f"\x00{i}\x00",
                f'<span class="vocab-term" tabindex="0" role="note" '
                f'data-definition="{html.escape(definition, quote=True)}">{esc(word)}</span>')
        rendered.append(t)
    return rendered, placed


def page_header(d):
    topic = rc.TOPIC_LABELS.get(d.get("topic", ""), "")
    eyebrow = f'{d["level"]} &middot; {esc(topic)}' if topic else d["level"]
    return f"""<div class="page-header">
        {STARS_ROW}
        <div class="page-header__inner">
            <div class="page-header__text">
                <p class="eyebrow hero__eyebrow">{eyebrow}</p>
                <h1>{esc(d['title'])}</h1>
                <p class="page-header__lede">{esc(d['subtitle'])}</p>
                <p class="page-header__actions" style="margin-top:var(--space-md);">{PRINT_BTN}</p>
            </div>
        </div>
    </div>"""


def toc(ids):
    labels = {"listen-and-read": "Listen &amp; Read",
              "practice": "Practice", "discussion": "Discussion"}
    links = "".join(f'<a href="#{i}">{labels[i]}</a>' for i in labels if i in ids)
    return f'<div class="level-toc"><div class="level-toc__inner">{links}</div></div>'


def listen_and_read(d, level, slug):
    """Audio first, then the text. Native <audio controls> is a deliberate
    choice: it gives play/pause, a progress bar, elapsed/total time, keyboard
    access and a playback-speed menu on every modern browser, desktop and
    mobile, with no JavaScript to fail. The <p> inside it is the fallback for
    a browser that cannot play the file at all."""
    marked, placed = annotate(d["passage"], d.get("vocabulary"))
    paras = "\n            ".join(f"<p>{p}</p>" for p in marked)
    # Hovering works on screen, but a printed page has no hover, and the
    # on-page vocabulary list is gone -- so the definitions come back as a
    # glossary that only exists in print.
    gloss = "".join(
        f'<li><strong>{esc(v["term"])}</strong> &mdash; {esc(v["definition"])}</li>'
        for v in (d.get("vocabulary") or []))
    gloss_html = (f'<div class="reading-glossary"><h3>Vocabulary</h3>'
                  f'<ul class="summary-list">{gloss}</ul></div>') if gloss else ""
    mins = d.get("audio", {}).get("duration_label", "")
    meta = f' <span>{esc(mins)}</span>' if mins else ""
    return f"""<section id="listen-and-read" class="section" aria-labelledby="lr-heading">
        <div class="section__inner">
            <p class="eyebrow">Listen &amp; Read</p>
            <h2 id="lr-heading">The Text</h2>
            <p style="color:var(--color-text-muted);margin-bottom:var(--space-md);max-width:60ch;">Play the audio and follow along, then read it again on your own. Hover over a <span class="vocab-term" tabindex="0" role="note" data-definition="Like this one — the highlighted words carry a definition.">highlighted word</span> to see what it means.{meta}</p>
            <audio controls preload="metadata" src="{rc.audio_href(level, slug, REL)}">
                <p>Your browser cannot play this audio. <a href="{rc.audio_href(level, slug, REL)}">Download the MP3</a> instead.</p>
            </audio>
            <div class="reading-passage">
            {paras}
            </div>
            {gloss_html}
        </div>
    </section>"""


def practice(d):
    exs = d.get("exercises") or []
    if not exs:
        return ""
    blocks = "".join(
        '<div class="exercise-block"><script type="application/json" class="exercise-data">'
        f'{json.dumps(ex, ensure_ascii=False)}</script></div>' for ex in exs)
    return f"""<section id="practice" class="section section--surface" aria-labelledby="practice-heading">
        <div class="section__inner">
            <p class="eyebrow">Interactive Exercises</p>
            <h2 id="practice-heading">Practice</h2>
            <p style="color:var(--color-text-muted);margin-bottom:var(--space-md);max-width:60ch;">Complete each exercise, then click <strong>Submit</strong> to see your score and an explanation for every answer.</p>
            {blocks}
        </div>
    </section>"""


def discussion(d):
    prompts = d.get("discussion") or []
    if not prompts:
        return ""
    rows = "".join(f"<li>{esc(p)}</li>" for p in prompts)
    return f"""<section id="discussion" class="section section--tight" aria-labelledby="disc-heading">
        <div class="section__inner">
            <p class="eyebrow">Speaking &amp; Writing</p>
            <h2 id="disc-heading">Discussion</h2>
            <p style="color:var(--color-text-muted);margin-bottom:var(--space-md);max-width:60ch;">There are no right answers here &mdash; use these to practice speaking, or write a short answer to each.</p>
            <ul class="summary-list">{rows}</ul>
        </div>
    </section>"""


def build(level, slug, d):
    title = f"{d['title']} — {d['level']} Reading & Listening — Renan the Teacher"
    description = d.get("description") or f"{d['title']}: {d['subtitle']}"
    breadcrumb = (
        f'<li><a href="{REL}index.html">Home</a></li>'
        f'<li><a href="{REL}exercises.html">Reading</a></li>'
        f'<li><a href="{REL}levels/{level}.html">{d["level"]}</a></li>'
        f'<li aria-current="page">{esc(d["title"])}</li>'
    )
    body = [listen_and_read(d, level, slug), practice(d), discussion(d)]
    ids = [i for i, s in zip(
        ["listen-and-read", "practice", "discussion"], body) if s]

    out = [
        site_chrome.head(REL, title, description[:300],
                         page_path=f"reading/{level}/{slug}.html", og_type="article"),
        site_chrome.header(REL, d["level"], breadcrumb),
        page_header(d),
        toc(ids),
        *[s for s in body if s],
        site_chrome.footer(REL),
    ]
    p = rc.page_path(level, slug)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(out), encoding="utf-8")
    return p


def main():
    targets = sys.argv[1:]
    built = 0
    for level, slug, d in rc.all_sources():
        if targets and f"{level}/{slug}" not in targets:
            continue
        p = build(level, slug, d)
        print(f"  built {p.relative_to(rc.REPO_ROOT)}")
        built += 1
    if not built:
        print("nothing to build (no matching content/readings/*.json)")
    else:
        print(f"{built} reading page(s) built")


if __name__ == "__main__":
    main()
