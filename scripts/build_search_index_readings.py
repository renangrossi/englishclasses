#!/usr/bin/env python3
"""
Refresh the reading-library entries in assets/data/search-index.json, one per
content/readings/{level}/{slug}.json.

Same idea as scripts/build_search_index_sheets.py: a reading page that is not
in the index is unreachable from the site's search, so the index is generated
from the content rather than hand-maintained and left to drift.

Entries are typed "reading" and are fully owned by this script -- it removes
every existing "reading" entry and rebuilds them, so it is safe to re-run and
never touches the hand-curated entries of any other type. New entries are
appended after the existing ones, which keeps the curated entries ranking
first (see the ranking note in build_search_index_sheets.py).

Usage:
    python3 scripts/build_search_index_readings.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reading_common as rc

INDEX = rc.REPO_ROOT / "assets" / "data" / "search-index.json"


def main():
    entries = json.loads(INDEX.read_text(encoding="utf-8"))
    kept = [e for e in entries if e.get("type") != "reading"]
    removed = len(entries) - len(kept)

    added = []
    for level, slug, d in rc.all_sources():
        topic = rc.TOPIC_LABELS.get(d.get("topic", ""), "")
        keywords = [k for k in [d.get("topic", ""), topic.lower(), "reading", "listening", "audio"] if k]
        keywords += [v["term"] for v in (d.get("vocabulary") or [])][:8]
        added.append({
            "title": d["title"],
            "url": f"reading/{level}/{slug}.html",
            "level": d["level"],
            "type": "reading",
            "desc": d["subtitle"],
            "keywords": sorted(set(keywords)),
        })

    out = kept + added
    INDEX.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"search index: removed {removed} reading entr{'y' if removed == 1 else 'ies'}, "
          f"added {len(added)} -> {len(out)} total")


if __name__ == "__main__":
    main()
