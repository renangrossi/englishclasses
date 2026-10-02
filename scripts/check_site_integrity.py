#!/usr/bin/env python3
"""
Static consistency checks for the whole site. Read-only -- it never edits
anything, so it is safe to run at any time.

Checks
------
1. internal links      every href/src resolves to a file that exists, and
                       every #fragment resolves to an id on the target page
2. search index        every entry's url (and #fragment) resolves
3. booklet sheets      every `<section id="sheet-N">` has its own search
                       entry pointing at `...#sheet-N` -- the check that
                       would have caught the bug where searching a sheet
                       title ("Paired Expressions") landed on the top of
                       the booklet instead of the sheet, because sheet
                       titles only existed inside the parent booklet
                       entry's "keywords"
4. curriculum <-> site every curriculum/{level}/*.json has a built page,
                       is listed in curriculum/index.json, and appears in
                       worker/course-catalog.json
5. exercise data       every `<script class="exercise-data">` block (and
                       its curriculum source) matches the contract
                       assets/js/exercises.js actually implements, and
                       item ids are unique per lesson

Usage:
    python3 scripts/check_site_integrity.py            # report, exit 1 on error
    python3 scripts/check_site_integrity.py --warnings # also list warnings
"""
import glob
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_ORIGIN = "https://renangrossi.github.io/englishclasses/"
SKIP_DIRS = (".git/", ".claude/", "old/", "students/", "node_modules/", ".wrangler/")

# Types assets/js/exercises.js has a renderer for.
EXERCISE_TYPES = {
    "multiple-choice", "true-false", "fill-blank", "matching", "ordering",
    "correction", "typing", "reading-comprehension", "vocabulary", "writing",
}

errors: list[str] = []
warnings: list[str] = []


def html_pages():
    for path in sorted(REPO_ROOT.rglob("*.html")):
        rel = path.relative_to(REPO_ROOT).as_posix()
        if rel.startswith(SKIP_DIRS):
            continue
        yield rel, path


def load_pages():
    pages, anchors = {}, {}
    for rel, path in html_pages():
        text = path.read_text(encoding="utf-8", errors="replace")
        pages[rel] = text
        ids = set(re.findall(r'\sid="([^"]+)"', text))
        ids |= set(re.findall(r'\sname="([^"]+)"', text))
        anchors[rel] = ids
    return pages, anchors


# ------------------------------------------------------------------ 1 links
def check_links(pages, anchors):
    link_re = re.compile(r'(?:href|src)="([^"]+)"')
    for rel, text in pages.items():
        base = os.path.dirname(rel)
        for raw in link_re.findall(text):
            url = raw.strip()
            if url.startswith(SITE_ORIGIN):       # absolute self-link
                url, target_base = url[len(SITE_ORIGIN):], ""
            else:
                target_base = base
            if not url or url.startswith(("#", "mailto:", "tel:", "data:", "javascript:")):
                continue
            if re.match(r"^[a-z][a-z0-9+.-]*:", url):   # external scheme
                continue
            path, _, frag = url.partition("#")
            # scripts/stamp_asset_versions.py appends ?v=<hash> to css and js
            # references for cache-busting; the query is not part of the path
            # on disk, so strip it before resolving.
            path, _, _query = path.partition("?")
            path = unquote(path)
            if path:
                target = os.path.normpath(os.path.join(target_base, path)).replace("\\", "/")
                if not (REPO_ROOT / target).exists():
                    errors.append(f"broken link: {rel} -> {raw}")
                    continue
            else:
                target = rel
            if frag and target in anchors and frag not in anchors[target]:
                errors.append(f"broken anchor: {rel} -> {raw} (no id={frag!r} on {target})")


# ----------------------------------------------------------- 2+3 search index
def check_search_index(anchors):
    index = json.loads((REPO_ROOT / "assets/data/search-index.json").read_text(encoding="utf-8"))
    for entry in index:
        path, _, frag = entry["url"].partition("#")
        if not (REPO_ROOT / unquote(path)).exists():
            errors.append(f"search entry {entry['title']!r} -> missing file {entry['url']}")
            continue
        if frag and path in anchors and frag not in anchors[path]:
            errors.append(f"search entry {entry['title']!r} -> dead anchor {entry['url']}")

    # every booklet sheet must be directly reachable from search
    indexed = {e["url"] for e in index}
    for booklet in sorted(REPO_ROOT.glob("cefr/english-classes-*.html")):
        rel = booklet.relative_to(REPO_ROOT).as_posix()
        text = booklet.read_text(encoding="utf-8")
        for sheet_id in re.findall(r'<section class="page" id="(sheet-\d+)">', text):
            want = f"{rel}#{sheet_id}"
            if want not in indexed:
                errors.append(
                    f"booklet sheet not searchable: {want} has no search-index entry "
                    f"(run scripts/build_search_index_sheets.py)")


# --------------------------------------------------------- 4 curriculum <-> site
def check_curriculum():
    index = json.loads((REPO_ROOT / "curriculum/index.json").read_text(encoding="utf-8"))
    listed = set()
    for level in index["levels"].values():
        for unit in level["units"]:
            for entry in unit["lessons"]:
                listed.add(entry["id"] if isinstance(entry, dict) else entry)

    catalog = json.loads((REPO_ROOT / "worker/course-catalog.json").read_text(encoding="utf-8"))
    catalog_urls = {r["url"] for r in catalog["resources"]}
    for resource in catalog["resources"]:
        if not (REPO_ROOT / unquote(resource["url"].partition("#")[0])).exists():
            errors.append(f"course-catalog entry {resource['title']!r} -> missing {resource['url']}")

    for fpath in sorted(glob.glob(str(REPO_ROOT / "curriculum/*/*.json"))):
        if Path(fpath).name == "index.json":
            continue
        lesson = json.loads(Path(fpath).read_text(encoding="utf-8"))
        lesson_id, level = lesson["id"], lesson["level"].lower()
        slug = lesson_id[len(level) + 1:] if lesson_id.startswith(level + "-") else lesson_id
        page = f"levels/{level}/{slug}.html"
        rel = Path(fpath).relative_to(REPO_ROOT).as_posix()
        if not (REPO_ROOT / page).exists():
            errors.append(f"{rel}: no built page at {page} (run scripts/build_lesson.py)")
        if lesson_id not in listed:
            errors.append(f"{rel}: {lesson_id} is not listed in curriculum/index.json")
        if page not in catalog_urls:
            warnings.append(f"{rel}: {page} is not in worker/course-catalog.json "
                            f"(the AI teacher won't know about it)")


# ------------------------------------------------------------ 5 exercise data
def check_exercise_block(where, block, seen_ids):
    eid = block.get("id", "?")
    etype = block.get("type")
    if etype not in EXERCISE_TYPES:
        errors.append(f"{where} {eid}: type {etype!r} has no renderer in exercises.js")
        return
    items = block.get("items") or []
    if not items:
        errors.append(f"{where} {eid}: no items")
    for item in items:
        iid = item.get("id")
        if not iid:
            errors.append(f"{where} {eid}: an item has no id")
            continue
        if iid in seen_ids:
            errors.append(f"{where}: duplicate item id {iid!r} (also in {seen_ids[iid]})")
        seen_ids[iid] = eid

        if etype == "fill-blank":
            blanks = str(item.get("prompt", "")).count("___")
            answers = item.get("answers")
            if not isinstance(answers, list):
                errors.append(f"{where} {iid}: fill-blank needs an 'answers' list")
            elif blanks != len(answers):
                errors.append(f"{where} {iid}: {blanks} blank(s) but {len(answers)} answer group(s)")
            options = item.get("options")
            # A flat options list is only applied when the item has one
            # blank (see renderFillBlank); on a multi-blank item it would
            # silently render free-text inputs instead of dropdowns.
            if options and not isinstance(options[0], list) and blanks != 1:
                errors.append(f"{where} {iid}: flat 'options' on a {blanks}-blank item")
            if options and isinstance(options[0], list) and len(options) != blanks:
                errors.append(f"{where} {iid}: {len(options)} option group(s) for {blanks} blank(s)")
        elif etype in ("multiple-choice", "vocabulary", "reading-comprehension"):
            options = item.get("options") or []
            answer_index = item.get("answerIndex")
            if len(options) < 2:
                errors.append(f"{where} {iid}: needs at least 2 options")
            elif not isinstance(answer_index, int) or not 0 <= answer_index < len(options):
                errors.append(f"{where} {iid}: answerIndex {answer_index!r} out of range")
            if len(set(options)) != len(options):
                errors.append(f"{where} {iid}: duplicate options")
        elif etype == "correction":
            if not item.get("incorrect"):
                errors.append(f"{where} {iid}: correction needs 'incorrect'")
            if not item.get("answer"):
                errors.append(f"{where} {iid}: correction needs 'answer'")
        elif etype == "ordering":
            if not isinstance(item.get("words"), list) or len(item["words"]) < 2:
                errors.append(f"{where} {iid}: ordering needs a 'words' list")
        elif etype == "matching":
            pairs = item.get("pairs")
            if not isinstance(pairs, list) or not pairs:
                errors.append(f"{where} {iid}: matching needs 'pairs'")
            else:
                rights = [p.get("right") for p in pairs]
                if len(set(rights)) != len(rights):
                    warnings.append(f"{where} {iid}: repeated 'right' values make the dropdown ambiguous")
        elif etype == "typing":
            if not item.get("answer") and not item.get("modelAnswer"):
                warnings.append(f"{where} {iid}: typing item with neither 'answer' nor 'modelAnswer'")


def check_exercises(pages):
    block_re = re.compile(r'<script type="application/json" class="exercise-data">(.*?)</script>', re.S)
    for rel, text in pages.items():
        seen: dict[str, str] = {}
        for raw in block_re.findall(text):
            try:
                block = json.loads(raw)
            except json.JSONDecodeError as exc:
                errors.append(f"{rel}: unparseable exercise-data ({exc})")
                continue
            check_exercise_block(rel, block, seen)
    for fpath in sorted(glob.glob(str(REPO_ROOT / "curriculum/*/*.json"))):
        if Path(fpath).name == "index.json":
            continue
        lesson = json.loads(Path(fpath).read_text(encoding="utf-8"))
        rel = Path(fpath).relative_to(REPO_ROOT).as_posix()
        seen = {}
        for block in lesson.get("exercises", []):
            check_exercise_block(rel, block, seen)


def main():
    pages, anchors = load_pages()
    check_links(pages, anchors)
    check_search_index(anchors)
    check_curriculum()
    check_exercises(pages)

    print(f"Checked {len(pages)} pages, "
          f"{len(glob.glob(str(REPO_ROOT / 'curriculum/*/*.json'))) - 1} curriculum lessons.")
    if "--warnings" in sys.argv and warnings:
        print(f"\n{len(warnings)} warning(s):")
        for w in warnings:
            print(f"  ! {w}")
    elif warnings:
        print(f"{len(warnings)} warning(s) (pass --warnings to list them).")
    if errors:
        print(f"\n{len(errors)} error(s):")
        for e in errors:
            print(f"  x {e}")
        sys.exit(1)
    print("No errors.")


if __name__ == "__main__":
    main()
