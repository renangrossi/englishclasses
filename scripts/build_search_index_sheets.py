#!/usr/bin/env python3
"""
Refresh the booklet-sheet entries in assets/data/search-index.json, one per
`<section class="page" id="sheet-N">` in cefr/english-classes-{level}.html.

Why this exists
---------------
Every sheet of the printed grammar booklets is a real, separately
addressable topic on the site (cefr/english-classes-b2.html#sheet-74 is
"Paired Expressions"), but the search index had no entry for any of them --
97 sheets, 0 entries. Instead, each booklet's sheet titles were dumped into
the *parent* booklet entry's "keywords" array, whose url is the bare page:

    {"title": "B2 Upper Intermediate", "url": "cefr/english-classes-b2.html",
     "keywords": [..., "paired expressions", ...]}

assets/js/search.js renders a result as `root + entry.url`, so searching a
sheet title matched only that parent entry and navigated to the *top* of a
17-sheet page, silently dropping the #sheet-N the topic actually lives at.
65 of the 93 booklet keywords behaved that way. Generating a real entry per
sheet fixes the whole class at its source instead of special-casing one
topic, and keeps the anchor in the data rather than in search.js.

Ranking note: these entries are inserted immediately after their parent
booklet entry, which puts every one of them ahead of the hand-curated
"lesson" entries further down the file. Where a sheet and an interactive
lesson share a title (e.g. "Paired Expressions"), both score 100 on an
exact title match, and Array.prototype.sort is stable (ES2019), so the
sheet -- the topic's canonical reading location -- is listed first, with
the interactive lesson right behind it. Keep this ordering if the file is
ever regenerated.

Idempotent: re-running replaces the previously generated sheet entries
rather than duplicating them, so it is safe after every booklet rebuild
(scripts/build_booklet_pages.py).

Usage:
    python3 scripts/build_search_index_sheets.py [--check]
"""
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = REPO_ROOT / "assets" / "data" / "search-index.json"

# (booklet file slug, level code as it appears on the parent booklet entry)
LEVELS = [
    ("pre-a1", "Pre-A1"),
    ("a1", "A1"),
    ("a2", "A2"),
    ("b1", "B1"),
    ("b2", "B2"),
    ("c1", "C1"),
    ("c2", "C2"),
]

SHEET_RE = re.compile(r'<section class="page" id="(sheet-\d+)">(.*?)</section>', re.S)
TAG_RE = re.compile(r"<[^>]+>")


def text(html: str) -> str:
    """Visible text of a fragment, with entities and whitespace normalised."""
    s = TAG_RE.sub("", html)
    for ent, ch in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
                    ("&quot;", '"'), ("&#39;", "'"), ("&mdash;", "—"),
                    ("&ndash;", "–"), ("&nbsp;", " ")):
        s = s.replace(ent, ch)
    return re.sub(r"\s+", " ", s).strip()


def strip_extra(name: str) -> str:
    """Drops the trailing "· Extra" marker some booklet sheets carry in their
    footer -- it flags a bonus sheet, it is not part of the topic name."""
    return re.sub(r"\s*·\s*Extra$", "", name, flags=re.I).strip()


def sheets_for(slug: str):
    """(sheet id, h2 heading, lede, footer topic name) per sheet."""
    html = (REPO_ROOT / "cefr" / f"english-classes-{slug}.html").read_text(encoding="utf-8")
    out = []
    for sheet_id, body in SHEET_RE.findall(html):
        h2 = re.search(r"<h2[^>]*>(.*?)</h2>", body, re.S)
        lede = re.search(r'<p class="lede">(.*?)</p>', body, re.S)
        foot = re.search(r'<footer class="foot">.*?<b>(.*?)</b>', body, re.S)
        out.append((
            sheet_id,
            text(h2.group(1)) if h2 else "",
            text(lede.group(1)) if lede else "",
            text(foot.group(1)) if foot else "",
        ))
    return out


def build_entries():
    """{level code: [entry, ...]} in sheet order."""
    by_level = {}
    for slug, level in LEVELS:
        rows = sheets_for(slug)
        # A heading like "Simple Past" is used by two different A2 sheets;
        # the footer topic name ("Simple Past II - Mixing With the Present")
        # is the authoritative, unique name, so fall back to it rather than
        # publishing two identically-titled results.
        headings = [h for _, h, _, _ in rows]
        entries = []
        for sheet_id, heading, lede, topic in rows:
            unique = headings.count(heading) == 1
            title = heading if (heading and unique) else (topic or heading)
            desc_parts = []
            if lede:
                desc_parts.append(lede)
            # "Paired Expressions · Extra" is the same topic as the heading
            # "Paired Expressions" -- that suffix only marks a bonus sheet, so
            # repeating it back as "Booklet sheet: ..." tells the reader nothing.
            if topic and strip_extra(topic).lower() != title.lower():
                desc_parts.append(f"Booklet sheet: {topic}.")
            keywords = []
            for kw in (heading, topic):
                kw = strip_extra(kw or "").lower()
                if kw and kw != title.lower() and kw not in keywords:
                    keywords.append(kw)
            entry = {
                "title": title,
                "url": f"cefr/english-classes-{slug}.html#{sheet_id}",
                "level": level,
                "type": "sheet",
                "desc": " ".join(desc_parts),
            }
            if keywords:
                entry["keywords"] = keywords
            entries.append(entry)
        by_level[level] = entries
    return by_level


def main():
    check = "--check" in sys.argv
    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    generated = build_entries()

    # Drop any previously generated sheet entries, then re-insert each
    # level's set directly after that level's parent booklet entry.
    kept = [e for e in index if "#sheet-" not in e.get("url", "")]
    out = []
    placed = set()
    for entry in kept:
        out.append(entry)
        if entry.get("type") == "booklet":
            level = entry.get("level")
            if level in generated:
                out.extend(generated[level])
                placed.add(level)
    missing = sorted(set(generated) - placed)
    if missing:
        sys.exit(f"no parent booklet entry found for: {', '.join(missing)}")

    payload = json.dumps(out, ensure_ascii=False, separators=(",", ":"))
    total = sum(len(v) for v in generated.values())
    if check:
        current = INDEX_PATH.read_text(encoding="utf-8").rstrip("\n")
        if current != payload:
            sys.exit(f"search-index.json is stale: {total} sheet entries would change")
        print(f"search-index.json is up to date ({total} sheet entries)")
        return
    INDEX_PATH.write_text(payload, encoding="utf-8")
    print(f"Wrote {total} booklet-sheet entries across {len(generated)} levels "
          f"-> {INDEX_PATH.relative_to(REPO_ROOT)} ({len(out)} entries total)")


if __name__ == "__main__":
    main()
