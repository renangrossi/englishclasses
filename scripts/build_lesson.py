#!/usr/bin/env python3
"""
Render one curriculum/{level}/{lesson-id}.json into levels/{level}/{lesson-id}.html,
following the exact section structure of the hand-written A1 lessons
(Objectives -> Explanation -> Rules -> Examples -> Common Mistakes -> Practice
-> Summary -> Related), using the shared chrome from site_chrome.py so the
result is visually identical to the rest of the site.

Usage:
    python3 scripts/build_lesson.py curriculum/c1/complex-subordinate-clauses.json
"""
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import site_chrome  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
REL = "../../"  # levels/{level}/{lesson}.html -> repo root

STAR = '<svg class="stars-row__star" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 17.27 18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21Z"/></svg>'
STARS_ROW = f'<div class="stars-row stars-row--onlight" aria-hidden="true">{STAR * 11}</div>'
CHECK_SVG = '<svg class="" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12 5 5L20 7"/></svg>'
ARROW_SVG = '<svg class="" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></svg>'


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def page_header(lesson):
    return f"""<div class="page-header">
        {STARS_ROW}
        <div class="page-header__inner">
            <div class="page-header__text">
                <p class="eyebrow hero__eyebrow">{lesson['level']}</p>
                <h1>{esc(lesson['title'])}</h1>
                <p class="page-header__lede">{esc(lesson['subtitle'])}</p>
            </div>
        </div>
    </div>"""


def toc(present_ids):
    labels = {
        "objectives": "Objectives", "explanation": "Explanation", "rules": "Rules",
        "examples": "Examples", "mistakes": "Common Mistakes", "practice": "Practice",
        "summary": "Summary",
    }
    links = "".join(f'<a href="#{a}">{labels[a]}</a>' for a in labels if a in present_ids)
    return f'<div class="level-toc"><div class="level-toc__inner">{links}</div></div>'


def objectives_section(lesson):
    items = "".join(f"<li>{CHECK_SVG}<span>{esc(o)}</span></li>" for o in lesson["objectives"])
    return f"""<section id="objectives" class="section section--tight" aria-labelledby="obj-heading">
        <div class="section__inner split">
            <div>
                <p class="eyebrow">Introduction</p>
                <p style="font-size:var(--step-0);color:var(--color-text-muted);max-width:56ch;">{esc(lesson['content']['intro'])}</p>
            </div>
            <div class="card card--feature">
                <h2 id="obj-heading" style="font-size:var(--step-0);">By the end of this lesson you can&hellip;</h2>
                <ul class="objectives-list">{items}</ul>
            </div>
        </div>
    </section>"""


def explanation_section(lesson):
    c = lesson["content"]
    explanation = c.get("explanation")
    register = f'<div class="notice mt-lg"><strong>Register</strong><p>{esc(c["registerNote"])}</p></div>' if c.get("registerNote") else ""
    if not explanation and not register:
        return ""
    # `explanation` may be plain text (pilot lesson) or pre-built inline
    # HTML (<p>/<strong>/<ul> from the batch txt parser) -- only escape
    # plain text; content already containing tags is trusted, same as
    # `rules[].body` below.
    if explanation:
        inner = explanation if "<" in explanation else f"<p>{esc(explanation)}</p>"
        body = f'<div class="prose">{inner}</div>'
    else:
        body = ""
    return f"""<section id="explanation" class="section section--surface" aria-labelledby="exp-heading">
        <div class="section__inner section__inner--narrow">
            <p class="eyebrow">Explanation</p>
            <h2 id="exp-heading" class="visually-hidden">Explanation</h2>
            {body}
            {register}
        </div>
    </section>"""


def rules_section(lesson):
    rules = lesson["content"].get("rules") or []
    if not rules:
        return ""
    blocks = "".join(f'<div class="card" style="margin-bottom:var(--space-md);"><h3>{esc(r["heading"])}</h3>{r["body"]}</div>' for r in rules)
    return f"""<section id="rules" class="section section--tight" aria-labelledby="rules-heading">
        <div class="section__inner">
            <p class="eyebrow">Grammar Rules</p>
            <h2 id="rules-heading">The Rules</h2>
            {blocks}
        </div>
    </section>"""


def examples_section(lesson):
    items = "".join(
        f'<li><svg class="examples-list__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12 5 5L20 7"/></svg><span>{esc(e)}</span></li>'
        for e in lesson["content"]["examples"]
    )
    return f"""<section id="examples" class="section section--surface" aria-labelledby="ex-heading">
        <div class="section__inner">
            <p class="eyebrow">Examples</p>
            <h2 id="ex-heading">See It in Action</h2>
            <ul class="examples-list">{items}</ul>
        </div>
    </section>"""


def mistakes_section(lesson):
    cards = "".join(
        f"""<div class="mistake-card">
            <p class="mistake-card__wrong"><span class="badge badge--pdf" style="margin-right:.5em;">Avoid</span>{esc(m['wrong'])}</p>
            <p class="mistake-card__right"><span class="badge badge--doc" style="margin-right:.5em;">Use instead</span>{esc(m['right'])}</p>
            <p class="mistake-card__why">{esc(m['why'])}</p>
        </div>"""
        for m in lesson["content"]["commonMistakes"]
    )
    return f"""<section id="mistakes" class="section section--tight" aria-labelledby="mist-heading">
        <div class="section__inner">
            <p class="eyebrow">Common Mistakes</p>
            <h2 id="mist-heading">Watch Out For</h2>
            <div class="mistakes-grid">{cards}</div>
        </div>
    </section>"""


def practice_section(lesson):
    blocks = "".join(
        f'<div class="exercise-block"><script type="application/json" class="exercise-data">{json.dumps(ex, ensure_ascii=False)}</script></div>'
        for ex in lesson["exercises"]
    )
    return f"""<section id="practice" class="section section--surface" aria-labelledby="practice-heading">
        <div class="section__inner">
            <p class="eyebrow">Interactive Exercises</p>
            <h2 id="practice-heading">Practice</h2>
            <p style="color:var(--color-text-muted);margin-bottom:var(--space-md);max-width:60ch;">Complete each exercise, then click <strong>Submit</strong> to see your score and an explanation for every answer.</p>
            {blocks}
        </div>
    </section>"""


def summary_section(lesson):
    items = "".join(f"<li>{esc(s)}</li>" for s in lesson["summary"])
    return f"""<section id="summary" class="section section--tight" aria-labelledby="sum-heading">
        <div class="section__inner section__inner--narrow">
            <p class="eyebrow">Summary</p>
            <h2 id="sum-heading">Review</h2>
            <ul class="summary-list">{items}</ul>
        </div>
    </section>"""


def related_section(lesson, level_slug):
    return f"""<section id="related" class="section section--surface" aria-labelledby="rel-heading">
        <div class="section__inner">
            <p class="eyebrow">Source Material</p>
            <h2 id="rel-heading">Keep Going</h2>
            <div class="lesson-nav">
                <a class="btn btn--ghost" href="../{level_slug}.html">Back to {lesson['level']}</a>
                <a class="btn btn--ghost btn--small" href="../../{lesson['sourceMaterial']['pdf']}" target="_blank" rel="noopener">Open PDF</a>
            </div>
        </div>
    </section>"""


def build(lesson_path: Path):
    lesson = json.loads(lesson_path.read_text(encoding="utf-8"))
    level_slug = lesson["level"].lower()
    lesson_slug = lesson["id"].split("-", 1)[1] if lesson["id"].startswith(level_slug + "-") else lesson["id"]

    title = f"{lesson['title']} — {lesson['level']} English Grammar — Renan the Teacher"
    description = f"{lesson['title']}: {lesson['subtitle']}"[:300]
    breadcrumb = (
        f'<li><a href="{REL}index.html">Home</a></li>'
        f'<li aria-current="page">Levels</li>'
        f'<li><a href="../{level_slug}.html">{lesson["level"]}</a></li>'
        f'<li aria-current="page">{esc(lesson["title"])}</li>'
    )

    sections = {
        "objectives": objectives_section(lesson),
        "explanation": explanation_section(lesson),
        "rules": rules_section(lesson),
        "examples": examples_section(lesson),
        "mistakes": mistakes_section(lesson),
        "practice": practice_section(lesson),
        "summary": summary_section(lesson),
    }
    present_ids = [k for k, v in sections.items() if v]

    out = []
    out.append(site_chrome.head(REL, title, description))
    out.append(site_chrome.header(REL, lesson["level"], breadcrumb))
    out.append(page_header(lesson))
    out.append(toc(present_ids))
    for k in present_ids:
        out.append(sections[k])
    out.append(related_section(lesson, level_slug))
    out.append(site_chrome.footer(REL))

    out_dir = REPO_ROOT / "levels" / level_slug
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{lesson_slug}.html"
    out_path.write_text("\n".join(out), encoding="utf-8")
    print(f"Built {out_path.relative_to(REPO_ROOT)}")
    return out_path


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        build(Path(arg))
