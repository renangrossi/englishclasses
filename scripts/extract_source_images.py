#!/usr/bin/env python3
"""
Pull the content images out of a source .docx into assets/img/reading/.

A .docx is a zip, and its pictures sit in word/media/. Two of them are
boilerplate rather than content: a 36 KB logo that appears in 72 of the
source documents, and a 1.2 MB decorative header that appears in 12. Both
are skipped by hash, so what comes out is the artwork that actually belongs
to the text -- the Krampus engraving, the Aesop illustrations, and so on.

Images are written to assets/img/reading/{level}/{slug}/ and referenced from
the source JSON's "images" array; see build_reading_page.py. They are NOT
part of the passage, so adding one never changes the narration fingerprint
and never forces a re-record.

Usage:
    python3 scripts/extract_source_images.py <docx-stem> <level>/<slug>
    python3 scripts/extract_source_images.py --list <docx-stem>
"""
import hashlib
import shutil
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "cefr" / "texts"
OUT = REPO / "assets" / "img" / "reading"

# The two images that are furniture, not content, identified by counting how
# many documents each distinct image appears in (72 and 12 respectively).
BOILERPLATE = {"f2fb4b1e4373", "96f59a670204"}

EXT = {".jpeg": ".jpg", ".jpg": ".jpg", ".png": ".png", ".gif": ".gif", ".webp": ".webp"}


def media(stem):
    """Every content image in the document, as (name, suffix, bytes)."""
    path = SRC / f"{stem}.docx"
    if not path.exists():
        sys.exit(f"no such source: {path}")
    z = zipfile.ZipFile(path)
    found = []
    for n in sorted(z.namelist()):
        if not n.startswith("word/media/"):
            continue
        suffix = EXT.get(Path(n).suffix.lower())
        if not suffix:
            continue
        data = z.read(n)
        if hashlib.sha256(data).hexdigest()[:12] in BOILERPLATE:
            continue
        found.append((Path(n).stem, suffix, data))
    return found


def main():
    args = [a for a in sys.argv[1:]]
    if not args:
        sys.exit(__doc__)
    if args[0] == "--list":
        for name, suffix, data in media(args[1]):
            print(f"  {name}{suffix}  {len(data)//1024} KB")
        return 0
    stem, target = args[0], args[1]
    level, slug = target.split("/")
    dest = OUT / level / slug
    dest.mkdir(parents=True, exist_ok=True)
    written = []
    for i, (name, suffix, data) in enumerate(media(stem), 1):
        f = dest / f"{i:02d}{suffix}"
        f.write_bytes(data)
        written.append(f"{f.relative_to(REPO)}  ({len(data)//1024} KB)")
    for w in written:
        print("  wrote", w)
    print(f"{len(written)} image(s) -> {dest.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
