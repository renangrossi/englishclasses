#!/usr/bin/env python3
"""
Validate every reading source against the schema the builders assume.

scripts/check_site_integrity.py checks the built site: links resolve, files
exist. This checks the thing the site is built FROM, so a fault is caught
before it is rendered into a page, an audio file and a search entry.

What it looks for is what has actually gone wrong in this repo, not a generic
list: a vocabulary headword that never appears in its own passage (so the word
is defined and never highlighted), an image whose caption is missing or whose
file is not on disk, a topic key with no label (which prints as a raw slug on
the hub), a duplicated glossary entry, an "after" index pointing past the end
of the passage, a level that disagrees with the folder it sits in.

Usage:
    python3 scripts/check_content.py              # report; exit 1 on an error
    python3 scripts/check_content.py --warnings   # also list the warnings
    python3 scripts/check_content.py b1/nfl       # one text
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reading_common as rc
import build_reading_page as brp

IMG_ROOT = rc.REPO_ROOT / "assets" / "img" / "reading"

REQUIRED = ["id", "level", "slug", "topic", "title", "subtitle", "passage"]

# A caption that is only "*Title* -- Artist, year." tells a reader what the
# picture IS but not why it is here. That is fine over a generic scene and
# misleading over a named subject, which is how a painting of Dordrecht came to
# illustrate a text about Denver. Pictures that depict their subject need no
# such sentence; pictures that stand in for it do.
BARE_CAPTION_RE = re.compile(r"^\*[^*]+\*\s*[—-]\s*[^.]{0,60}\.\s*$")

VALID_RELATION = ("depicts", "analogue")


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def err(self, where, msg):
        self.errors.append(f"{where}: {msg}")

    def warn(self, where, msg):
        self.warnings.append(f"{where}: {msg}")


def check_text(level, slug, d, rep):
    where = f"{level}/{slug}"

    for key in REQUIRED:
        if not d.get(key):
            rep.err(where, f"missing required field '{key}'")
    if not d.get("passage"):
        return

    if d.get("level", "").lower() != level:
        rep.err(where, f"level '{d.get('level')}' disagrees with its folder")
    if d.get("slug") != slug:
        rep.err(where, f"slug '{d.get('slug')}' disagrees with its filename")

    topic = d.get("topic", "")
    if topic and topic not in rc.TOPIC_LABELS:
        rep.err(where, f"topic '{topic}' has no label in reading_common.TOPIC_LABELS")

    if d.get("provenance") and d["provenance"] not in rc.VALID_PROVENANCE:
        rep.err(where, f"provenance '{d['provenance']}' is not one of {rc.VALID_PROVENANCE}")

    # ---- vocabulary -------------------------------------------------------
    vocab = d.get("vocabulary") or []
    seen = {}
    for v in vocab:
        if not v.get("term") or not v.get("definition"):
            rep.err(where, f"vocabulary entry missing term or definition: {v}")
            continue
        key = v["term"].strip().lower()
        if key in seen:
            rep.err(where, f"duplicate vocabulary headword '{v['term']}'")
        seen[key] = True

    # The builder decides what to highlight; asking it is the only way to know
    # whether a headword will actually land on the page.
    if vocab:
        _, placed, _ = brp.annotate(d["passage"], vocab)
        for v in vocab:
            if v["term"] not in placed:
                rep.warn(where, f"vocabulary '{v['term']}' never matches its own passage "
                                f"(defined but never highlighted)")
        for v in vocab:
            if v.get("match") and v["match"] not in "\n".join(d["passage"]):
                rep.err(where, f"vocabulary '{v['term']}' pins match='{v['match']}', "
                               f"which is not in the passage")

    # ---- images -----------------------------------------------------------
    for img in (d.get("images") or []):
        tag = f"{where} image {img.get('src', '?')}"
        if not img.get("src"):
            rep.err(where, "image with no src")
            continue
        rel = img["src"] if "/" in img["src"] else f"{level}/{slug}/{img['src']}"
        if not (IMG_ROOT / rel).is_file():
            rep.err(tag, f"file not found: assets/img/reading/{rel}")
        if not (img.get("alt") or "").strip():
            rep.err(tag, "no alt text")
        elif len(img["alt"].strip()) < 15:
            rep.warn(tag, f"alt text is very short: {img['alt']!r}")
        if not (img.get("caption") or "").strip():
            rep.warn(tag, "no caption")
        after = img.get("after")
        if not isinstance(after, int) or not 0 <= after < len(d["passage"]):
            rep.err(tag, f"'after' is {after!r}, outside the {len(d['passage'])}-paragraph passage")

        relation = img.get("relation", "analogue" if not str(
            img.get("source", "")).startswith("commons:") else "depicts")
        if relation not in VALID_RELATION:
            rep.err(tag, f"relation '{relation}' is not one of {VALID_RELATION}")
        elif relation == "analogue" and img.get("caption") \
                and BARE_CAPTION_RE.match(img["caption"].strip()):
            rep.warn(tag, "an analogue with a bare caption: it names the work but never "
                          "says why it is here, so it reads as a picture of the subject")

    # ---- exercises --------------------------------------------------------
    ex_ids = set()
    for ex in (d.get("exercises") or []):
        if not ex.get("id") or not ex.get("type"):
            rep.err(where, f"exercise missing id or type: {ex.get('title', ex)}")
        if ex.get("id") in ex_ids:
            rep.err(where, f"duplicate exercise id '{ex['id']}'")
        ex_ids.add(ex.get("id"))
        item_ids = set()
        for item in (ex.get("items") or []):
            if item.get("id") in item_ids:
                rep.err(where, f"duplicate item id '{item['id']}' in exercise '{ex.get('id')}'")
            item_ids.add(item.get("id"))
            opts = item.get("options")
            # Some item types (matching, ordering) use a list of lists here,
            # which is a different shape and not what this check is about.
            if isinstance(opts, list) and all(isinstance(o, str) for o in opts):
                if len(set(opts)) != len(opts):
                    rep.err(where, f"repeated option in item '{item.get('id')}'")
                idx = item.get("answerIndex")
                if idx is not None and not 0 <= idx < len(opts):
                    rep.err(where, f"answerIndex {idx} out of range in item '{item.get('id')}'")

    # ---- audio ------------------------------------------------------------
    if not rc.audio_path(level, slug).is_file():
        rep.warn(where, "no audio file yet")


def main():
    targets = [a for a in sys.argv[1:] if not a.startswith("-")]
    show_warnings = "--warnings" in sys.argv
    rep = Report()
    n = 0
    for level, slug, d in rc.all_sources():
        if targets and f"{level}/{slug}" not in targets:
            continue
        check_text(level, slug, d, rep)
        n += 1

    print(f"Checked {n} reading source(s).")
    if rep.warnings:
        print(f"{len(rep.warnings)} warning(s)"
              f"{'' if show_warnings else ' (pass --warnings to list them)'}.")
        if show_warnings:
            for w in rep.warnings:
                print(f"  ! {w}")
    if rep.errors:
        print(f"\n{len(rep.errors)} error(s):")
        for e in rep.errors:
            print(f"  x {e}")
        return 1
    print("No errors.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
