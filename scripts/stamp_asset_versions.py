#!/usr/bin/env python3
"""Stamp a content hash onto every CSS and JS link in the built pages.

GitHub Pages serves assets with `cache-control: max-age=600`, so for ten
minutes after a deploy a returning visitor keeps the stylesheet they already
have. A fix to the layout therefore looks like it did not land -- which is
exactly how a corrected button stack came back as "still broken" on a phone
that was holding the old search.css.

The fix is the usual one: the URL changes when the file changes. Each
`assets/**/*.css` and `assets/**/*.js` reference gets `?v=<first 8 of the
file's sha1>` appended, so a byte-identical file keeps its URL and the cache
keeps working, and an edited one gets a new URL that no cache has.

Run it after changing anything under assets/ and before pushing:

    python3 scripts/stamp_asset_versions.py

It is idempotent -- an existing ?v= is replaced, not stacked -- so running it
twice is harmless, and running it with nothing changed writes nothing.
"""
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# href="...css" / src="...js", with an optional ?v= already on it.
REF = re.compile(r'((?:href|src)=")([^"?]*?assets/[^"?]+\.(?:css|js))(\?v=[0-9a-f]+)?(")')

_digest_cache = {}


def digest(asset_rel):
    """First 8 hex of the file's sha1, or None if the path does not resolve."""
    if asset_rel in _digest_cache:
        return _digest_cache[asset_rel]
    path = ROOT / asset_rel
    out = None
    if path.is_file():
        out = hashlib.sha1(path.read_bytes()).hexdigest()[:8]
    _digest_cache[asset_rel] = out
    return out


def stamp(html_path):
    text = html_path.read_text(encoding="utf-8")

    def sub(m):
        prefix, url, _old, quote = m.groups()
        # The href is relative to the page; resolve it to a repo path so the
        # same file hashes identically however deep the page sits.
        rel = (html_path.parent / url).resolve()
        try:
            asset_rel = rel.relative_to(ROOT).as_posix()
        except ValueError:
            return m.group(0)
        d = digest(asset_rel)
        if not d:
            return m.group(0)
        return f"{prefix}{url}?v={d}{quote}"

    new = REF.sub(sub, text)
    if new == text:
        return False
    html_path.write_text(new, encoding="utf-8")
    return True


def main():
    pages = [p for p in ROOT.rglob("*.html") if ".git" not in p.parts]
    changed = sum(stamp(p) for p in pages)
    missing = sorted(k for k, v in _digest_cache.items() if v is None)
    print(f"{changed} of {len(pages)} page(s) restamped")
    if missing:
        print("referenced but not found on disk:")
        for m in missing:
            print("   ", m)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
