#!/usr/bin/env python3
"""
Add a "Test Yourself" CTA section to every hand-authored A1 lesson page
(levels/a1/*.html), linking to that topic's existing, unmodified anchor in
levels/a1/test-yourself.html. A1 lesson pages already ship correct
Previous/Next navigation (built by hand before the curriculum/*.json
pipeline existed), so this script only inserts the new section -- right
after #summary ("Review") and before #related ("Keep Going") -- using the
exact same markup build_lesson.py now generates for every other level, so
the feature looks and behaves identically everywhere.

Usage:
    python3 scripts/patch_a1_test_yourself.py
"""
import html
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ARROW_SVG = '<svg class="" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></svg>'


def esc(s):
    return html.escape(s, quote=False)


def section(title, anchor):
    return f"""<section id="lesson-test-yourself" class="section section--tight" aria-labelledby="lesson-ty-heading">
        <div class="section__inner section__inner--narrow" style="text-align:center;">
            <p class="eyebrow">Test Yourself</p>
            <h2 id="lesson-ty-heading">Ready to check your knowledge?</h2>
            <p style="color:var(--color-text-muted);max-width:56ch;margin:0 auto var(--space-md);">Take the full A1 Test Yourself review for this topic &mdash; more questions, mixed together, with instant feedback.</p>
            <a class="btn btn--accent" href="test-yourself.html#{anchor}">Test Yourself: {esc(title)} {ARROW_SVG}</a>
        </div>
    </section>
"""


def main():
    nav_map = json.loads((REPO_ROOT / "scripts" / "lesson_nav_map.json").read_text(encoding="utf-8"))
    a1_lessons = {l["slug"]: l for l in nav_map["a1"]}

    patched, skipped = 0, 0
    for path in sorted((REPO_ROOT / "levels" / "a1").glob("*.html")):
        if path.stem not in a1_lessons:
            continue  # test-yourself.html itself
        lesson = a1_lessons[path.stem]
        if not lesson["ty"]:
            skipped += 1
            continue
        text = path.read_text(encoding="utf-8")
        if "lesson-test-yourself" in text:
            print(f"SKIP (already patched): {path}")
            continue
        marker = '<section id="related"'
        if marker not in text:
            print(f"WARN: no #related section found in {path}, skipping")
            continue
        new_text = text.replace(marker, section(lesson["title"], lesson["ty"]) + marker, 1)
        path.write_text(new_text, encoding="utf-8")
        patched += 1
        print(f"Patched {path.relative_to(REPO_ROOT)}")
    print(f"\n{patched} files patched, {skipped} skipped (no Test Yourself match)")


if __name__ == "__main__":
    main()
