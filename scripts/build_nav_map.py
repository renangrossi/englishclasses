#!/usr/bin/env python3
"""
Build scripts/lesson_nav_map.json: for every level, the ordered list of its
own lessons (slug, title, and -- if a matching topic exists in that level's
*unmodified* test-yourself.html -- the anchor id to deep-link to), used by
build_lesson.py to render Previous/Next navigation and a "Test Yourself"
button on every generated lesson page, and by patch_a1_nav.py to do the
same for the hand-authored A1 pages.

This script only reads existing files (curriculum/*.json, curriculum/
index.json, levels/{level}/test-yourself.html, levels/a1.html) -- it never
invents lesson names or test-yourself topics. A lesson with no matching
test-yourself topic gets "ty": null, and no Test Yourself button is added
for it (the existing Test Yourself pages are never modified or extended).

Usage:
    python3 scripts/build_nav_map.py
"""
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Slug overrides where a lesson's own slug doesn't literally match its
# test-yourself.html anchor id, discovered by manual inspection.
TY_ANCHOR_OVERRIDE = {
    ("B1", "second-and-third-conditionals"): "2nd-and-3rd-conditionals",
}


def ty_anchors(level_slug: str) -> dict:
    """id -> heading text, for every ty-topic section in that level's
    existing, untouched test-yourself.html (empty dict if none exists)."""
    path = REPO_ROOT / "levels" / level_slug / "test-yourself.html"
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(
        r'<section id="([^"]+)"[^>]*ty-topic[^>]*aria-labelledby="([^"]+)"[^>]*>.*?<h2 id="\2">([^<]+)</h2>',
        re.S,
    )
    return {sid: heading for sid, _hid, heading in pattern.findall(text)}


def build_curriculum_level(level_key: str, level_slug: str) -> list:
    idx = json.loads((REPO_ROOT / "curriculum" / "index.json").read_text(encoding="utf-8"))
    lessons = idx["levels"][level_key]["units"][0]["lessons"] if idx["levels"][level_key]["units"] else []
    anchors = ty_anchors(level_slug)
    out = []
    for entry in lessons:
        lesson_id = entry["id"]
        prefix = level_slug + "-"
        slug = lesson_id[len(prefix):] if lesson_id.startswith(prefix) else lesson_id
        lesson_json_path = REPO_ROOT / "curriculum" / level_slug / f"{slug}.json"
        title = json.loads(lesson_json_path.read_text(encoding="utf-8"))["title"]
        ty = TY_ANCHOR_OVERRIDE.get((level_key, slug))
        if ty is None:
            ty = slug if slug in anchors else None
        out.append({"slug": slug, "title": title, "ty": ty})
    return out


def build_a1() -> list:
    # A1 predates the curriculum/*.json pipeline (hand-authored HTML) and
    # already ships correct Previous/Next navigation -- only the ordered
    # (slug, title) list and the test-yourself anchor mapping are needed
    # here, both read directly from the existing pages.
    html = (REPO_ROOT / "levels" / "a1.html").read_text(encoding="utf-8")
    hrefs = re.findall(r'lesson-card__title-link" href="a1/([^"]+)\.html">([^<]+)</a>', html)
    anchors = ty_anchors("a1")
    out = []
    for slug, title in hrefs:
        ty = slug if slug in anchors else None
        out.append({"slug": slug, "title": title, "ty": ty})
    return out


def build_pre_a1() -> list:
    idx = json.loads((REPO_ROOT / "curriculum" / "index.json").read_text(encoding="utf-8"))
    lessons = idx["levels"]["PRE-A1"]["units"][0]["lessons"]
    out = []
    for entry in lessons:
        lesson_id = entry["id"]
        slug = lesson_id[len("pre-a1-"):]
        lesson_json_path = REPO_ROOT / "curriculum" / "pre-a1" / f"{slug}.json"
        title = json.loads(lesson_json_path.read_text(encoding="utf-8"))["title"]
        out.append({"slug": slug, "title": title, "ty": None})  # Pre-A1 has no test-yourself.html
    return out


def main():
    nav_map = {
        "pre-a1": build_pre_a1(),
        "a1": build_a1(),
        "a2": build_curriculum_level("A2", "a2"),
        "b1": build_curriculum_level("B1", "b1"),
        "b2": build_curriculum_level("B2", "b2"),
        "c1": build_curriculum_level("C1", "c1"),
        "c2": build_curriculum_level("C2", "c2"),
    }
    out_path = REPO_ROOT / "scripts" / "lesson_nav_map.json"
    out_path.write_text(json.dumps(nav_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for lvl, lessons in nav_map.items():
        with_ty = sum(1 for l in lessons if l["ty"])
        print(f"{lvl}: {len(lessons)} lessons, {with_ty} with a Test Yourself match")


if __name__ == "__main__":
    main()
