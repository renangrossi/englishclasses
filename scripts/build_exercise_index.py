#!/usr/bin/env python3
"""
Build assets/data/exercise-items-index.json: a flat lookup of every
exercise item across every curriculum/{level}/*.json lesson, keyed by
item id.

This is what makes a spaced-repetition "Today's Review" page possible
without a backend: assets/js/mastery.js tracks *which* item ids are due
for review (in localStorage, using only the id + correctness history),
but has no way to know what an item actually says. This index is the
other half -- a static, generated lookup from item id to the item's full
original definition (prompt/options/answer/etc.), its exercise type, and
which lesson it came from, so a review page can reconstruct real,
gradeable exercise-data blocks for whatever's due, using the exact same
schema assets/js/exercises.js already renders.

Usage:
    python3 scripts/build_exercise_index.py
"""
import json
import glob
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = REPO_ROOT / "assets" / "data" / "exercise-items-index.json"


def lesson_url(level: str, lesson_id: str) -> str:
    slug = level.lower()
    prefix = slug + "-"
    file_slug = lesson_id[len(prefix):] if lesson_id.startswith(prefix) else lesson_id
    return f"levels/{slug}/{file_slug}.html"


def main():
    index = {}
    skipped_no_answer = 0
    files = sorted(glob.glob(str(REPO_ROOT / "curriculum" / "*" / "*.json")))
    for fpath in files:
        lesson = json.loads(Path(fpath).read_text(encoding="utf-8"))
        level = lesson.get("level", "")
        lesson_id = lesson.get("id", "")
        title = lesson.get("title", "")
        url = lesson_url(level, lesson_id)
        for ex in lesson.get("exercises", []):
            ex_type = ex.get("type")
            for item in ex.get("items", []):
                item_id = item.get("id")
                if not item_id:
                    continue
                # Only index items with a real, checkable answer -- open
                # self-check "typing" items with no `answer` (guided
                # production, modelAnswer only) aren't meaningfully
                # "correct/incorrect" for spaced repetition, so they're
                # left out of the review queue on purpose.
                has_checkable_answer = (
                    "answers" in item or "answer" in item
                    or (ex_type == "matching" and "pairs" in item)
                    or (ex_type == "ordering" and "words" in item)
                    or (ex_type == "multiple-choice" and "answerIndex" in item)
                )
                if not has_checkable_answer:
                    skipped_no_answer += 1
                    continue
                entry = dict(item)
                entry["exerciseType"] = ex_type
                entry["exerciseId"] = ex.get("id")
                entry["exerciseTitle"] = ex.get("title")
                entry["exerciseInstructions"] = ex.get("instructions")
                entry["lessonId"] = lesson_id
                entry["lessonTitle"] = title
                entry["level"] = level
                entry["lessonUrl"] = url
                index[item_id] = entry

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(index, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Indexed {len(index)} reviewable items from {len(files)} lessons "
          f"({skipped_no_answer} self-check-only items excluded) -> {OUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
