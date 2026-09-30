#!/usr/bin/env python3
"""
Fetch a public-domain artwork from Wikimedia Commons for a reading page.

Only accepts files whose licence metadata says public domain. Anything under
a CC licence with conditions, or with no licence metadata at all, is refused
rather than downloaded, because the site is public and the rights have to be
right. The artist and licence it reports are what belongs in the caption.

Usage:
    python3 scripts/fetch_public_domain_image.py --check "File:Foo.jpg"
    python3 scripts/fetch_public_domain_image.py "File:Foo.jpg" b2/slug/01.jpg
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "assets" / "img" / "reading"
API = "https://commons.wikimedia.org/w/api.php"
UA = "RenanTheTeacher-reading-library/1.0 (educational site; contact via github.com/renangrossi)"

# Substrings that mean "no rights reserved". Anything else is refused.
PD_OK = ("public domain", "pd-", "cc0", "no restrictions")


def _get(url, tries=4):
    """Commons rate-limits (HTTP 429) if you ask quickly. Back off and retry
    rather than hammering it; a fixed pause between calls keeps this a polite
    client even when several images are fetched in one run."""
    last = None
    for attempt in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                time.sleep(1.5)
                return r.read()
        except urllib.error.HTTPError as err:
            last = err
            if err.code not in (429, 503):
                raise
            time.sleep(5 * (attempt + 1))
    raise last


def info(title, width=1100):
    q = urllib.parse.urlencode({
        "action": "query", "format": "json", "prop": "imageinfo",
        "iiprop": "url|extmetadata|size", "iiurlwidth": str(width), "titles": title,
    })
    data = json.loads(_get(f"{API}?{q}"))
    pages = data.get("query", {}).get("pages", {})
    page = next(iter(pages.values()), {})
    if "imageinfo" not in page:
        return None
    ii = page["imageinfo"][0]
    ex = ii.get("extmetadata", {})

    def field(k):
        v = ex.get(k, {}).get("value", "")
        # strip any markup the API returns in these fields
        out, depth = [], 0
        for c in v:
            if c == "<":
                depth += 1
            elif c == ">":
                depth = max(0, depth - 1)
            elif depth == 0:
                out.append(c)
        return " ".join("".join(out).split())

    lic = field("LicenseShortName") or field("License")
    return {
        "title": title,
        "artist": field("Artist"),
        "credit": field("Credit"),
        "date": field("DateTimeOriginal"),
        "licence": lic,
        "usage": field("UsageTerms"),
        "thumb": ii.get("thumburl") or ii.get("url"),
        "descurl": ii.get("descriptionurl", ""),
    }


def is_pd(meta):
    blob = f"{meta.get('licence','')} {meta.get('usage','')}".lower()
    return any(k in blob for k in PD_OK)


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    if args[0] == "--search":
        q = urllib.parse.urlencode({
            "action": "query", "format": "json", "list": "search",
            "srsearch": f'filetype:bitmap {args[1]}', "srnamespace": "6", "srlimit": "8",
        })
        for r in json.loads(_get(f"{API}?{q}")).get("query", {}).get("search", []):
            print("  " + r["title"])
        return 0
    if args[0] == "--check":
        m = info(args[1])
        if not m:
            print("  NOT FOUND"); return 1
        print(f"  title   : {m['title']}")
        print(f"  artist  : {m['artist'][:90]}")
        print(f"  date    : {m['date'][:60]}")
        print(f"  licence : {m['licence']} | {m['usage'][:60]}")
        print(f"  PUBLIC DOMAIN: {is_pd(m)}")
        return 0
    title, dest = args[0], args[1]
    m = info(title)
    if not m:
        sys.exit(f"not found: {title}")
    if not is_pd(m):
        sys.exit(f"REFUSED (not public domain): {title} -> {m['licence']} / {m['usage'][:80]}")
    path = OUT / dest
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_get(m["thumb"]))
    print(f"  {dest}  ({path.stat().st_size//1024} KB)  [{m['licence']}]  {m['artist'][:60]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
