#!/usr/bin/env python3
"""
Put a public-domain image from Wikimedia Commons into a reading page.

The local gallery (scripts/import_local_artwork.py) is always the first place to
look. This is for what the gallery cannot answer: flags, maps, photographs,
portraits of particular people -- the things an American history collection
needs and a shelf of European landscape painting does not have.

Rights are not a judgement call here. The Commons licence metadata is read
first. Public domain and CC0 are used as they are; CC BY and CC BY-SA are used
too, but the licence and the author are recorded on the image and printed under
it, because that is the condition those licences attach. Anything carrying NC or
ND is refused outright -- ND forbids the resize this script performs, and NC puts
a condition on the whole site that nobody should have to reason about later.

Usage:
    python3 scripts/add_commons_image.py --plan plan.json
    python3 scripts/add_commons_image.py a1/george-washington \
        --file "File:Foo.jpg" --after 5 --alt "..." --caption "*Title* — Artist, 1796." [--wide]

Plan entries: {text, file, after, alt, caption, wide}
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reading_common as rc
import fetch_public_domain_image as pd

IMG_ROOT = rc.REPO_ROOT / "assets" / "img" / "reading"
MAX_W, MAX_H, QUALITY = 1200, 1200, 85


def add(text, title, after, alt, caption, wide=False, check=False):
    level, slug = text.split("/", 1)
    p = rc.src_path(level, slug)
    if not p.is_file():
        raise SystemExit(f"no such text: {text}")
    meta = pd.info(title, width=1600)
    if not meta:
        raise SystemExit(f"not found on Commons: {title}")
    if not pd.is_usable(meta):
        raise SystemExit(f"REFUSED (not free to use): {title} -> {meta['licence']}")
    if check:
        tier = "PD" if pd.is_pd(meta) else "needs credit"
        print(f"  ok {text} <- {title}  [{meta['licence']} / {tier}]  {meta['artist'][:46]}")
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    if not 0 <= after < len(d["passage"]):
        raise SystemExit(f"{text}: --after {after} is outside the passage")
    imgs = list(d.get("images") or [])
    # Next FREE number, not len+1. Removing an image from the middle of a text's
    # set leaves a shorter list whose highest number is still taken, and len+1
    # then silently overwrote the file already sitting there -- losing the old
    # picture while two JSON entries claimed the same filename.
    taken = {i["src"] for i in imgs} | {f.name for f in (IMG_ROOT / level / slug).glob("*")}
    n = 1
    while f"{n:02d}.jpg" in taken:
        n += 1
    name = f"{n:02d}.jpg"
    dest = IMG_ROOT / level / slug / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    raw = dest.with_suffix(".download")
    raw.write_bytes(pd._get(meta["thumb"]))
    # Flags and maps come back as PNG renders of an SVG; everything is
    # normalised to one web-sized JPEG so the page is predictable. A flag is
    # flattened onto white rather than losing its transparency to black.
    subprocess.run(["magick", str(raw), "-auto-orient", "-background", "white",
                    "-alpha", "remove", "-alpha", "off",
                    "-resize", f"{MAX_W}x{MAX_H}>", "-strip",
                    "-interlace", "Plane", "-quality", str(QUALITY), str(dest)], check=True)
    raw.unlink()
    entry = {"src": name, "after": after, "alt": alt, "source": f"commons:{title}"}
    # A public-domain file owes nobody anything and carries no licence fields.
    # Anything else is free only on condition of a credit, so the condition is
    # recorded here and printed under the picture by build_reading_page.py.
    if pd.needs_credit(meta):
        entry["licence"] = meta["licence"]
        entry["author"] = meta["artist"] or meta["credit"] or "unknown"
        entry["source_url"] = meta.get("descurl", "")
    if caption:
        entry["caption"] = caption
    if wide:
        entry["wide"] = True
    imgs.append(entry)
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
    print(f"  {text} <- {title} as {name} (after {after}, {dest.stat().st_size//1024} KB)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("text", nargs="?")
    ap.add_argument("--file")
    ap.add_argument("--after", type=int, default=0)
    ap.add_argument("--alt", default="")
    ap.add_argument("--caption", default="")
    ap.add_argument("--wide", action="store_true")
    ap.add_argument("--plan")
    ap.add_argument("--check-only", action="store_true")
    a = ap.parse_args()
    jobs = json.loads(Path(a.plan).read_text(encoding="utf-8")) if a.plan else [
        {"text": a.text, "file": a.file, "after": a.after, "alt": a.alt,
         "caption": a.caption, "wide": a.wide}]
    for j in jobs:
        add(j["text"], j["file"], int(j["after"]), j["alt"], j.get("caption", ""),
            bool(j.get("wide")), check=a.check_only)
    print(f"{len(jobs)} image(s)")


if __name__ == "__main__":
    main()
