#!/usr/bin/env python3
"""
Print each reading's title, subtitle and the opening of every paragraph.

This is the view you need to place an illustration: a picture belongs at a turn
in the text, and the turns are visible from the paragraph openings without
reading all 70,000 words again.

    python3 scripts/show_passages.py b1/          # a level
    python3 scripts/show_passages.py b1/nfl       # one text
    python3 scripts/show_passages.py              # everything not yet illustrated
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reading_common as rc

def main():
    sel = sys.argv[1:]
    for level, slug, d in rc.all_sources():
        key = f"{level}/{slug}"
        if sel and not any(s in key for s in sel):
            continue
        if not sel and d.get("images"):
            continue
        print(f"\n### {key} — {d['title']} | {d.get('subtitle', '')}")
        for i, p in enumerate(d["passage"]):
            print(f"  [{i}] {re.sub('<[^>]+>', '', p)[:110]}")

if __name__ == "__main__":
    main()
