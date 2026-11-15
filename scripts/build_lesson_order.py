#!/usr/bin/env python3
"""
Build assets/data/lesson-order.json: every level's grammar lessons in
the order the level page lists them, with the exercise block ids on
each lesson page.

Today's Review (assets/js/today-review.js) uses it to recommend the
next lesson: the first one, in course order, where the student has not
submitted any exercise yet (progress.js records each submitted block
under its id). exercise-items-index.json can't answer this -- it is
keyed by item and lists lessons alphabetically.

The order comes from the links on levels/<level>.html, the same list
students see. Lessons with no exercise blocks are left out: nothing
records whether they were studied, so they can't be recommended or
ticked off honestly.

Usage:
    python3 scripts/build_lesson_order.py
"""
import html
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = REPO_ROOT / "assets" / "data" / "lesson-order.json"
LEVELS = [("Pre-A1", "pre-a1"), ("A1", "a1"), ("A2", "a2"), ("B1", "b1"),
          ("B2", "b2"), ("C1", "c1"), ("C2", "c2")]
BLOCK = re.compile(r'<script type="application/json" class="exercise-data">(.*?)</script>', re.S)
TITLE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.S)


def text(fragment):
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def main():
    out = []
    for code, slug in LEVELS:
        level_page = REPO_ROOT / "levels" / f"{slug}.html"
        links = []
        for href in re.findall(rf'href="{re.escape(slug)}/([^"#?]+\.html)"', level_page.read_text(encoding="utf-8")):
            if href not in links:
                links.append(href)
        lessons, test = [], None
        for name in links:
            page = REPO_ROOT / "levels" / slug / name
            if not page.is_file():
                continue
            url = f"levels/{slug}/{name}"
            if name == "test-yourself.html":
                test = url
                continue
            source = page.read_text(encoding="utf-8")
            ids = []
            for raw in BLOCK.findall(source):
                try:
                    block_id = json.loads(raw).get("id")
                except ValueError:
                    continue
                if block_id and block_id not in ids:
                    ids.append(block_id)
            if not ids:
                continue
            title = TITLE.search(source)
            lessons.append({"url": url, "title": text(title.group(1)) if title else name, "exercises": ids})
        out.append({"code": code, "url": f"levels/{slug}.html", "test": test, "lessons": lessons})
    OUT_PATH.write_text(json.dumps({"levels": out}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Wrote {OUT_PATH.relative_to(REPO_ROOT)}: "
          + ", ".join(f"{l['code']} {len(l['lessons'])}" for l in out))


if __name__ == "__main__":
    main()
