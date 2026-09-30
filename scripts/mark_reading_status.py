#!/usr/bin/env python3
"""
Record conversion progress in docs/reading-library-map.json.

Called after a batch is built, so the map (and therefore exercises.html and
docs/content-audit.md, which are both generated from it) reflects what is
actually on the site.

    # a source is now live at its own reading page
    python3 scripts/mark_reading_status.py done a2/the-day-at-the-market

    # a source was folded into another page and is represented by it
    python3 scripts/mark_reading_status.py merged common-chores=a2/household-chores

Usage forms:
    done   <level>/<slug> ...            (slug must match the map entry)
    done   <source-slug>=<level>/<slug>  (when the page slug was renamed)
    merged <source-slug>=<level>/<slug>
"""
import json
import sys
from pathlib import Path

MAP = Path(__file__).resolve().parent.parent / "docs" / "reading-library-map.json"


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    mode, args = sys.argv[1], sys.argv[2:]
    if mode not in ("done", "merged"):
        print(f"unknown mode {mode!r}"); return 1

    d = json.loads(MAP.read_text(encoding="utf-8"))
    by_slug = {}
    for t in d["texts"]:
        by_slug.setdefault(t["slug"], t)
        by_slug.setdefault(t.get("source_slug", t["slug"]), t)

    missing = []
    for a in args:
        if "=" in a:
            src, target = a.split("=", 1)
        else:
            target = a
            src = a.split("/", 1)[1]
        t = by_slug.get(src)
        if t is None:
            missing.append(src); continue
        t["status"] = "IMPLEMENTED" if mode == "done" else "MERGED"
        t["page"] = f"reading/{target}.html"
        if mode == "done" and t["audio"] in ("required", "stale-on-edit"):
            t["audio"] = "exists"
        print(f"  {t['slug']:34} -> {t['status']:12} {t['page']}")

    d["_progress"] = {
        "implemented": sum(1 for t in d["texts"] if t.get("status") == "IMPLEMENTED"),
        "merged_away": sum(1 for t in d["texts"] if t.get("status") == "MERGED"),
        "total": len(d["texts"]),
    }
    MAP.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    if missing:
        print(f"error: no map entry for {missing}", file=sys.stderr); return 1
    print(f"progress: {d['_progress']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
