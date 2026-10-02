#!/usr/bin/env python3
"""
Regenerate the "From the local art gallery" table in docs/image-credits.md.

Every image imported by scripts/import_local_artwork.py records the gallery file
it came from as "source" in the text's JSON, so the credits list is derived
rather than maintained by hand. The hand-written sections of the file (Wikimedia
Commons, carried over from the source documents, deliberately not used) are left
alone: only the block between the markers is rewritten.

Usage: python3 scripts/build_image_credits.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reading_common as rc

DOC = rc.REPO_ROOT / "docs" / "image-credits.md"
START = "<!-- gallery:start -->"
END = "<!-- gallery:end -->"


def main():
    rows, commons, licensed = [], [], []
    for level, slug, d in rc.all_sources():
        for img in (d.get("images") or []):
            src = img.get("source")
            if not src:
                continue
            work = (img.get("caption") or "").split(" — ")[0].strip("*")
            if img.get("licence"):
                # Free only on condition of a credit; the condition is listed in
                # full here as well as printed under the picture on the page.
                licensed.append((f"`{level}/{slug}`", img["src"],
                                 img.get("author", "unknown"), img["licence"],
                                 img.get("source_url", ""), work))
                continue
            row = (f"`{level}/{slug}`", img["src"], src, work)
            (commons if src.startswith("commons:") else rows).append(row)
    body = [START,
            "",
            f"{len(rows)} images, imported with `scripts/import_local_artwork.py` from the local",
            "gallery of painting and print scans. Each one is a work old enough to be free of",
            "rights; the gallery also holds living and recent artists, and none of that is used.",
            "",
            "| Page | File | Work | Gallery source |",
            "|---|---|---|---|"]
    for page, src, source, work in sorted(rows):
        body.append(f"| {page} | `{src}` | {work} | `{source}` |")
    body += ["",
             "### From Wikimedia Commons (public domain)",
             "",
             f"{len(commons)} images the gallery could not answer -- flags, maps, photographs and",
             "portraits of particular people. Fetched with `scripts/add_commons_image.py`, which",
             "reads the Commons licence metadata and refuses anything carrying NC or ND. The",
             "few used under a licence that requires a credit are listed separately below.",
             "",
             "| Page | File | Work | Commons file |",
             "|---|---|---|---|"]
    for page, src, source, work in sorted(commons):
        body.append(f"| {page} | `{src}` | {work} | `{source[8:]}` |")

    body += ["",
             "### Used under a licence that requires credit",
             "",
             f"{len(licensed)} image(s). The credit is also printed under the picture on",
             "the page itself, which is where the licence requires it to be.",
             "",
             "| Page | File | Author | Licence | Source |",
             "|---|---|---|---|---|"]
    for page, src, author, lic, url, work in sorted(licensed):
        link = f"[Commons]({url})" if url else "Commons"
        body.append(f"| {page} | `{src}` | {author} | {lic} | {link} |")
    body += ["", END]

    text = DOC.read_text(encoding="utf-8")
    block = "\n".join(body)
    if START in text:
        head, rest = text.split(START, 1)
        _, tail = rest.split(END, 1)
        text = head + block + tail
    else:
        text = text.rstrip("\n") + "\n\n## From the local art gallery\n\n" + block + "\n"
    DOC.write_text(text, encoding="utf-8")
    print(f"docs/image-credits.md: {len(rows)} gallery images")


if __name__ == "__main__":
    main()
