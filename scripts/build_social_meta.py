#!/usr/bin/env python3
"""
Normalise the link-preview metadata (canonical + Open Graph + Twitter) in the
<head> of every page on the site.

Why this exists
---------------
Most pages here are static HTML that no generator owns: the hand-written A1
lessons, the level hubs, index.html and the root utility pages. Only
levels/{level}/*.html (build_lesson.py) and cefr/*.html (build_booklet_pages.py)
come from a template. So fixing the template alone cannot fix the site -- this
script is the part that reaches every page, and both generators render the same
block from the same builder (site_chrome.social_meta), so all three stay in step.

What it fixes
-------------
* og:url and rel=canonical were missing from every page, so WhatsApp, Facebook
  and Twitter had no absolute URL to key a preview on. The site is served from
  the /englishclasses/ subpath, so these have to be absolute and keep that
  segment -- a root-relative "/assets/..." would 404.
* og:image:alt was missing everywhere.
* Titles and descriptions were interpolated into meta tags unescaped, so a
  topic like "Nouns & Plurals" emitted a bare & in an attribute -- invalid
  markup that a strict crawler can stop reading at.
* og:type was "website" even on lesson pages.

Skipped on purpose
------------------
* redirect stubs (<meta http-equiv="refresh">) -- they already carry a
  canonical pointing at the page they forward to, and should never own a
  preview of their own.
* noindex pages (manoelito.html) -- deliberately unlisted, so giving them a
  share card would work against that.

Idempotent: re-running replaces the block it wrote last time. Safe after every
build_lesson.py / build_booklet_pages.py run.

Usage:
    python3 scripts/build_social_meta.py            # rewrite
    python3 scripts/build_social_meta.py --check    # exit 1 if anything is stale
"""
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import site_chrome  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = (".git/", ".claude/", "old/", "students/", "node_modules/", ".wrangler/")

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S)
DESC_RE = re.compile(r'<meta\s+name="description"\s+content="([^"]*)"\s*/?>')
# every tag this script owns, so a rerun replaces rather than duplicates
SOCIAL_TAG_RE = re.compile(
    r'[ \t]*<meta\s+(?:property|name)="(?:og:[^"]*|twitter:[^"]*)"[^>]*>\n?'
    r'|[ \t]*<link[^>]+rel="canonical"[^>]*>\n?',
    re.I,
)
REFRESH_RE = re.compile(r'<meta[^>]+http-equiv="refresh"', re.I)
NOINDEX_RE = re.compile(r'<meta[^>]+name="robots"[^>]+content="[^"]*noindex', re.I)
RAW_AMP_RE = re.compile(r"&(?!#?\w+;)")


def unescape_text(s):
    return html.unescape(s)


def og_type_for(rel):
    """A lesson or booklet page is an article; hubs and utility pages are not."""
    if re.match(r"^levels/[a-z0-9-]+/[^/]+\.html$", rel) or rel.startswith("cefr/"):
        return "article"
    return "website"


def pages():
    for path in sorted(REPO_ROOT.rglob("*.html")):
        rel = path.relative_to(REPO_ROOT).as_posix()
        if rel.startswith(SKIP_DIRS):
            continue
        yield rel, path


def rewrite(rel, text):
    """Returns the page with a correct, single social block, or None to skip."""
    end = text.find("</head>")
    if end == -1:
        return None
    head, rest = text[:end], text[end:]

    # A redirect stub or a noindex page must not own a share card, but its
    # markup still has to be valid -- it gets the escaping below and nothing
    # else.
    shareable = not (REFRESH_RE.search(head) or NOINDEX_RE.search(head))

    tm = TITLE_RE.search(head)
    if not tm:
        return None
    title = unescape_text(tm.group(1)).strip()
    dm = DESC_RE.search(head)
    description = unescape_text(dm.group(1)).strip() if dm else ""

    # 1. drop whatever social tags are already there
    if shareable:
        head = SOCIAL_TAG_RE.sub("", head)

    # 2. re-escape the title and description in place -- these were written
    #    unescaped by the generators, so "Nouns & Plurals" sat in the markup
    #    as a bare ampersand
    head = TITLE_RE.sub(lambda m: f"<title>{html.escape(title, quote=False)}</title>", head, count=1)
    if dm:
        head = DESC_RE.sub(
            lambda m: f'<meta name="description" content="{html.escape(description, quote=True)}">',
            head, count=1)

    # 3. insert the block right after the description (or the title)
    if shareable:
        block = site_chrome.social_meta(rel, title, description, og_type_for(rel))
        anchor = DESC_RE.search(head) or TITLE_RE.search(head)
        at = anchor.end()
        if head[at:at + 1] == "\n":
            at += 1
        head = head[:at] + block + "\n" + head[at:]

    return head + rest


def main():
    check = "--check" in sys.argv
    changed, skipped, stale = [], [], []
    for rel, path in pages():
        text = path.read_text(encoding="utf-8")
        new = rewrite(rel, text)
        if new is None:
            skipped.append(rel)
            continue
        if new == text:
            continue
        if check:
            stale.append(rel)
        else:
            path.write_text(new, encoding="utf-8")
            changed.append(rel)

    if check:
        if stale:
            print(f"{len(stale)} page(s) have stale social metadata:")
            for rel in stale[:20]:
                print(f"  {rel}")
            if len(stale) > 20:
                print(f"  ... +{len(stale) - 20} more")
            sys.exit(1)
        print(f"Social metadata is up to date ({len(list(pages())) - len(skipped)} pages).")
        return

    print(f"Updated {len(changed)} page(s); {len(skipped)} without a parseable head.")
    # a raw & left anywhere in a head means the escaping above missed a case
    for rel, path in pages():
        head = path.read_text(encoding="utf-8").split("</head>")[0]
        for m in re.finditer(r'<(?:title>|meta[^>]*content=")([^"<]*)', head):
            if RAW_AMP_RE.search(m.group(1)):
                print(f"  ! raw & remains in {rel}: {m.group(1)[:60]}")


if __name__ == "__main__":
    main()
