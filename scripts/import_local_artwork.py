#!/usr/bin/env python3
"""
Put a picture from the local art gallery into a reading page.

The gallery is a folder of museum-grade scans of paintings, engravings and
prints -- /media/amaterasu/Wallpapers by default, overridden with --gallery.
**It is the first place to look.** Only if nothing there fits the text is it
worth going to Wikimedia Commons with scripts/fetch_public_domain_image.py: a
picture already in the gallery has been chosen by somebody with an eye, and the
library reads as one illustrated edition rather than as a search-results page.

What this does, per image: copies the file into
assets/img/reading/{level}/{slug}/NN.jpg at a web size, and adds an entry to the
text's "images" array in content/readings/{level}/{slug}.json -- which is what
scripts/build_reading_page.py reads. The source filename is recorded as
"source" so docs/image-credits.md can be regenerated from the JSON.

"after" is the index of the paragraph the picture follows (0-based), so a
picture lands at a turn in the text rather than on top of it as a cover.

Rights: everything used is a work whose author has been dead long enough for it
to be public domain. The gallery also holds work by living and recent artists --
film and game illustration, modern military and western painting -- and none of
that may be published. --check-only prints what would happen without writing.

Usage:
    python3 scripts/import_local_artwork.py a1/rain-and-snow \\
        --image ivan-shishkin-first-snow.jpeg --after 3 \\
        --alt "A first fall of snow lying over a birch wood" \\
        --caption "*First Snow* — Ivan Shishkin"
    python3 scripts/import_local_artwork.py --plan plan.json
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reading_common as rc

GALLERY = Path("/media/amaterasu/Wallpapers")
IMG_ROOT = rc.REPO_ROOT / "assets" / "img" / "reading"
MAX_W, MAX_H, QUALITY = 1000, 1100, 82


def find(gallery, name):
    """Accept a filename with or without its extension."""
    p = gallery / name
    if p.is_file():
        return p
    hits = sorted(gallery.glob(name + ".*"))
    if not hits:
        hits = sorted(gallery.glob(name))
    if not hits:
        raise SystemExit(f"not in the gallery: {name}")
    return hits[0]


def convert(src, dest):
    """Down to a web size, re-encoded as JPEG, metadata stripped. The gallery
    files are wallpapers -- 2-8 MP and several megabytes each -- and the page
    shows a picture at about 400 px wide."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["magick", str(src), "-auto-orient",
                    "-resize", f"{MAX_W}x{MAX_H}>", "-strip",
                    "-interlace", "Plane", "-quality", str(QUALITY), str(dest)],
                   check=True)


def add(level, slug, image, after, alt, caption, gallery=GALLERY, check=False):
    src = find(gallery, image)
    p = rc.src_path(level, slug)
    if not p.is_file():
        raise SystemExit(f"no such text: {level}/{slug}")
    d = json.loads(p.read_text(encoding="utf-8"))
    n_paras = len(d["passage"])
    if not 0 <= after < n_paras:
        raise SystemExit(f"{level}/{slug}: --after {after} is outside the "
                         f"{n_paras} paragraphs of the passage")
    imgs = list(d.get("images") or [])
    # Next FREE number, not len+1 -- see the matching note in
    # scripts/add_commons_image.py. After an image is removed from a text's set,
    # len+1 points back at a filename that is still on disk and overwrites it.
    taken = {i["src"] for i in imgs} | {f.name for f in (IMG_ROOT / level / slug).glob("*")}
    n = 1
    while f"{n:02d}.jpg" in taken:
        n += 1
    nxt = f"{n:02d}.jpg"
    entry = {"src": nxt, "after": after, "alt": alt, "source": src.name}
    if caption:
        entry["caption"] = caption
    if check:
        print(f"  would add {level}/{slug} <- {src.name} as {nxt} after para {after}")
        return
    convert(src, IMG_ROOT / level / slug / nxt)
    imgs.append(entry)
    # Keep the array in reading order, and keep "images" next to "passage" --
    # the field order in these files is read by people, not just by scripts.
    imgs.sort(key=lambda i: (i["after"], i["src"]))
    out = {}
    for k, v in d.items():
        if k == "images":
            continue
        out[k] = v
        if k == "passage":
            out["images"] = imgs
    if "images" not in out:
        out["images"] = imgs
    p.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  {level}/{slug} <- {src.name} as {nxt} (after para {after})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("text", nargs="?", help="level/slug")
    ap.add_argument("--image")
    ap.add_argument("--after", type=int, default=0)
    ap.add_argument("--alt", default="")
    ap.add_argument("--caption", default="")
    ap.add_argument("--plan", help="JSON file: [{text, image, after, alt, caption}, ...]")
    ap.add_argument("--gallery", default=str(GALLERY))
    ap.add_argument("--check-only", action="store_true")
    a = ap.parse_args()
    gallery = Path(a.gallery)
    if not gallery.is_dir():
        raise SystemExit(f"gallery not found: {gallery}")

    jobs = []
    if a.plan:
        jobs = json.loads(Path(a.plan).read_text(encoding="utf-8"))
    elif a.text and a.image:
        jobs = [{"text": a.text, "image": a.image, "after": a.after,
                 "alt": a.alt, "caption": a.caption}]
    else:
        raise SystemExit("give a text and --image, or --plan")

    for j in jobs:
        level, slug = j["text"].split("/", 1)
        add(level, slug, j["image"], int(j["after"]), j["alt"],
            j.get("caption", ""), gallery=gallery, check=a.check_only)
    print(f"{len(jobs)} image(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
