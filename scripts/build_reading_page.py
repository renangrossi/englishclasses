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
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reading_common as rc
import site_chrome

REL = "../../"
STAR = ('<svg class="" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
        '<path d="m12 2 2.9 6.9 7.1.6-5.4 4.7 1.6 7L12 17.5 5.8 21.2l1.6-7L2 9.5l7.1-.6Z"/></svg>')
STARS_ROW = f'<div class="stars-row stars-row--onlight" aria-hidden="true">{STAR * 11}</div>'


def esc(s):
    return html.escape(str(s), quote=False)


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
            </div>
        </div>
    </div>"""


def toc(ids):
    labels = {"listen-and-read": "Listen &amp; Read", "vocabulary": "Vocabulary",
              "practice": "Practice", "discussion": "Discussion"}
    links = "".join(f'<a href="#{i}">{labels[i]}</a>' for i in labels if i in ids)
    return f'<div class="level-toc"><div class="level-toc__inner">{links}</div></div>'


def listen_and_read(d, level, slug):
    """Audio first, then the text. Native <audio controls> is a deliberate
    choice: it gives play/pause, a progress bar, elapsed/total time, keyboard
    access and a playback-speed menu on every modern browser, desktop and
    mobile, with no JavaScript to fail. The <p> inside it is the fallback for
    a browser that cannot play the file at all."""
    paras = "\n            ".join(f"<p>{esc(p)}</p>" for p in d["passage"])
    mins = d.get("audio", {}).get("duration_label", "")
    meta = f' <span>{esc(mins)}</span>' if mins else ""
    note = rc.PROVENANCE_LABELS.get(d.get("provenance", ""), "")
    note_html = (f'<p style="color:var(--color-text-muted);'
                 f'font-size:0.9rem;margin-top:var(--space-md);">{esc(note)}</p>') if note else ""
    return f"""<section id="listen-and-read" class="section" aria-labelledby="lr-heading">
        <div class="section__inner">
            <p class="eyebrow">Listen &amp; Read</p>
            <h2 id="lr-heading">The Text</h2>
            <p style="color:var(--color-text-muted);margin-bottom:var(--space-md);max-width:60ch;">Play the audio and follow along, then read it again on your own.{meta}</p>
            <audio controls preload="metadata" src="{rc.audio_href(level, slug, REL)}">
                <p>Your browser cannot play this audio. <a href="{rc.audio_href(level, slug, REL)}">Download the MP3</a> instead.</p>
            </audio>
            <div class="reading-passage">
            {paras}
            </div>
            {note_html}
        </div>
    </section>"""


def vocabulary(d):
    items = d.get("vocabulary") or []
    if not items:
        return ""
    rows = "".join(
        f'<li><strong>{esc(v["term"])}</strong> &mdash; {esc(v["definition"])}</li>'
        for v in items)
    return f"""<section id="vocabulary" class="section section--tight" aria-labelledby="vocab-heading">
        <div class="section__inner">
            <p class="eyebrow">Useful Language</p>
            <h2 id="vocab-heading">Vocabulary</h2>
            <ul class="summary-list">{rows}</ul>
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
    body = [listen_and_read(d, level, slug), vocabulary(d), practice(d), discussion(d)]
    ids = [i for i, s in zip(
        ["listen-and-read", "vocabulary", "practice", "discussion"], body) if s]

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
