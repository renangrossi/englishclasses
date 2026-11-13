#!/usr/bin/env python3
"""
Build assets/data/exercise-items-index.json: a flat lookup of every
gradeable exercise item on the grammar lesson pages, keyed by
"<exercise block id>/<item id>".

This is what makes a spaced-repetition "Today's Review" page possible
without a backend: assets/js/mastery.js tracks *which* items are due
for review (in localStorage, using only the key + correctness history),
but has no way to know what an item actually says. This index is the
other half -- a static, generated lookup from that key to the item's
full definition (prompt/options/answer/etc.), its exercise type, and
which lesson it came from, so a review page can reconstruct real,
gradeable exercise-data blocks for whatever's due, using the exact same
schema assets/js/exercises.js already renders.

The source is the exercise JSON embedded in levels/{level}/*.html --
the pages students actually answer on. It used to be curriculum/*.json,
but the lesson pages were expanded after those files were written (the
pages hold about seven times as many items) and A1 never had any, so
nearly everything a student answered was missing from the index and
never came back for review.

The key includes the block id because item ids alone repeat across
lessons. A lesson and its level's Test Yourself page share block ids
for the questions they share; the lesson's copy is the one indexed.

Usage:
    python3 scripts/build_exercise_index.py
"""
import html
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = REPO_ROOT / "assets" / "data" / "exercise-items-index.json"
BLOCK = re.compile(r'<script type="application/json" class="exercise-data">(.*?)</script>', re.S)
TITLE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.S)
GRADED_TYPES = {"fill-blank", "multiple-choice", "vocabulary", "true-false",
                "correction", "typing", "matching", "ordering"}


def checkable(ex_type, item):
    """Self-check typing items (a model answer, no answer key) and
    free writing have nothing to be right or wrong about."""
    if ex_type == "typing":
        return bool(item.get("answer"))
    return ex_type in GRADED_TYPES


def main():
    index = {}
    skipped = 0
    pages = sorted((REPO_ROOT / "levels").glob("*/*.html"),
                   key=lambda p: (p.name == "test-yourself.html", str(p)))
    for page in pages:
        text = page.read_text(encoding="utf-8")
        level = page.parent.name.upper().replace("PRE-A1", "Pre-A1")
        m = TITLE.search(text)
        title = html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else page.stem
        url = page.relative_to(REPO_ROOT).as_posix()
        for block in BLOCK.finditer(text):
            ex = json.loads(block.group(1))
            ex_type = ex.get("type")
            for item in ex.get("items", []):
                if not item.get("id") or not ex.get("id"):
                    continue
                if not checkable(ex_type, item):
                    skipped += 1
                    continue
                key = f"{ex['id']}/{item['id']}"
                if key in index:
                    continue
                entry = dict(item)
                entry["exerciseType"] = ex_type
                entry["exerciseId"] = ex["id"]
                entry["exerciseTitle"] = ex.get("title")
                entry["exerciseInstructions"] = ex.get("instructions")
                entry["lessonId"] = page.stem
                entry["lessonTitle"] = title
                entry["level"] = level
                entry["lessonUrl"] = url
                index[key] = entry

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(index, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Indexed {len(index)} reviewable items from {len(pages)} pages "
          f"({skipped} self-check items excluded) -> {OUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
