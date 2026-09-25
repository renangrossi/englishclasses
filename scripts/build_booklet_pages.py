"""
Turns the print-ready grammar booklets (cefr/english-classes-{level}.html,
built by build.js in the booklet project) into normal site pages.

The booklet content itself is never edited: its <body> markup is copied
across as-is, with only these structural changes so it can live inside a
site page:
  - headings are shifted down one level (h1 -> h2, h2 -> h3, h3 -> h4) so
    the page has a single h1 (the cover's level code and name);
  - the cover title becomes that <h1> (its two <div>s become <span>s);
  - every sheet gets an id (sheet-46, ...) and each contents entry on the
    cover links to its sheet.

The booklet's own <style> becomes assets/css/booklet-print.css, scoped
to #booklet (so it can't clash with the site's .card, .eyebrow, svg...
rules, or they with it) and otherwise unchanged -- it is still exactly
what print/PDF uses. The web layout lives in assets/css/booklet.css, and
the booklet's page-fitting script lives in assets/js/booklet.js, where it
runs only when printing.

Usage, after copying freshly built booklets into cefr/:
    python scripts/build_booklet_pages.py
Running it on pages it already converted rebuilds them from the booklet
markup they carry, so it is safe to run again.
"""

import html
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from site_chrome import LEVELS  # noqa: E402

REL = "../"
START, END = "<!-- booklet:start -->", "<!-- booklet:end -->"
STYLE_START, STYLE_END = "/* booklet-style:start */", "/* booklet-style:end */"

ARROW = ('<svg class="" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" '
         'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></svg>')
ARROW_BACK = ARROW.replace('<path d="M5 12h14"/><path d="m13 6 6 6-6 6"/>', '<path d="M19 12H5"/><path d="m11 18-6-6 6-6"/>')
PRINTER = ('<svg class="" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" '
           'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9V2h12v7"/>'
           '<path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><path d="M6 14h12v8H6z"/></svg>')


def booklet_path(slug):
    return os.path.join(ROOT, "cefr", f"english-classes-{slug}.html")


# ---------------------------------------------------------------- source

def read_source(slug):
    """Returns (style_css, body_markup) of the original booklet."""
    src = open(booklet_path(slug), encoding="utf-8").read()
    if START in src:  # already converted: rebuild from what it carries
        body = src[src.index(START) + len(START):src.index(END)]
        return None, restore_original(body)
    style = re.search(r"<style>(.*?)</style>", src, re.S).group(1)
    body = src[src.index("<body>") + len("<body>"):src.index("<script>")]
    return style, body


def restore_original(body):
    """Undoes convert_body() and the inserted top navigation, so a
    converted page can be rebuilt."""
    body = re.sub(r'\n<nav class="booklet-nav booklet-nav--top".*?</nav>', "", body, count=1, flags=re.S)
    body = re.sub(r'<a class="toc2__link" href="#sheet-\d+">(.*?)</a>', r"\1", body, flags=re.S)
    body = re.sub(r'<a class="lvl__link" href="english-classes-[a-z0-9-]+\.html">(.*?)</a>', r"\1", body, flags=re.S)
    body = re.sub(r'<section class="page" id="sheet-\d+">', '<section class="page">', body)
    body = re.sub(r'<h1 class="cover__title">(.*?)</h1>',
                  lambda m: '<div class="cover__title">' + re.sub(
                      r'<span class="(cover__code|cover__name)">(.*?)</span>', r'<div class="\1">\2</div>', m.group(1)) + "</div>",
                  body, flags=re.S)
    for a, b in (("h2", "h1"), ("h3", "h2"), ("h4", "h3")):
        body = body.replace(f"<{a}", f"<{b}").replace(f"</{a}>", f"</{b}>")
    return body


def convert_body(body):
    for a, b in (("h3", "h4"), ("h2", "h3"), ("h1", "h2")):
        body = body.replace(f"<{a}", f"<{b}").replace(f"</{a}>", f"</{b}>")
    body = re.sub(r'<div class="cover__title">(.*?)</div>\s*(?=<p class="cover__lede">)',
                  lambda m: '<h1 class="cover__title">' + re.sub(
                      r'<div class="(cover__code|cover__name)">(.*?)</div>', r'<span class="\1">\2</span>', m.group(1)) + "</h1>\n    ",
                  body, count=1, flags=re.S)

    def add_id(m):
        seal = re.search(r'<div class="seal">(\d+)</div>', m.group(2))
        return f'<section class="page" id="sheet-{seal.group(1)}">{m.group(2)}' if seal else m.group(0)
    body = re.sub(r'(<section class="page">)(.*?</section>)', add_id, body, flags=re.S)
    body = re.sub(r'<li>(<span class="n">(\d+)</span>.*?)</li>',
                  r'<li><a class="toc2__link" href="#sheet-\2">\1</a></li>', body, flags=re.S)
    # every level on the cover's CEFR scale links to its booklet, except the current one
    body = re.sub(r'<div class="(lvl (?!now)[^"]*)">(<b>([^<]+)</b>.*?)</div>',
                  lambda m: f'<div class="{m.group(1)}"><a class="lvl__link" href="english-classes-{m.group(3).lower()}.html">{m.group(2)}</a></div>',
                  body, flags=re.S)
    return body


# ------------------------------------------------------------------- css

def scope_css(css):
    """Prefixes every rule of the booklet stylesheet with #booklet and
    renames heading selectors to match convert_body()."""
    out = []
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        sel, decl = m.group(1).strip(), m.group(2).strip()
        if sel.startswith("@page"):
            out.append(f"{sel} {{ {decl} }}")
            continue
        scoped = []
        for s in sel.split(","):
            s = s.strip()
            s = re.sub(r"\bh3\b", "h4", s)
            s = re.sub(r"\bh2\b", "h3", s)
            s = re.sub(r"\bh1\b", "h2", s)
            if s in (":root", "html", "body"):
                scoped.append("#booklet")
            elif s == "*":
                scoped.append("#booklet :where(.page, .page *)")
            else:
                scoped.append("#booklet " + s)
        scoped = list(dict.fromkeys(scoped))
        out.append(f"{', '.join(scoped)} {{ {decl} }}")
    return "\n".join(out)


def write_print_css(style):
    path = os.path.join(ROOT, "assets", "css", "booklet-print.css")
    if style is not None:
        scoped = scope_css(style)
    else:  # pages already converted: keep the scoped booklet rules already there
        existing = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
        if STYLE_START not in existing:
            sys.exit("booklet-print.css is missing and no original booklet was found to build it from.")
        scoped = existing[existing.index(STYLE_START) + len(STYLE_START):existing.index(STYLE_END)].strip()
    css = f"""/* GENERATED by scripts/build_booklet_pages.py from the grammar
   booklets' own stylesheet -- edit the booklet project, not this file.
   Every rule is the original, scoped to #booklet; headings are shifted
   one level down (h1 -> h2 ...) like the booklet markup. This is the
   layout print/PDF uses; assets/css/booklet.css adapts it for screen. */

/* Isolate the sheets from the site's element and component styles
   (svg sizing, .card, .eyebrow, headings, lists...), so they render
   exactly as they did in the standalone document. :where() keeps this
   reset at the lowest specificity, below every booklet rule. */
#booklet :where(.page, .page *:not(svg, svg *)),
#booklet :where(.page *:not(svg, svg *))::before,
#booklet :where(.page *:not(svg, svg *))::after {{ all: revert; }}
/* SVGs can't take that reset (it would also undo their fill, stroke and
   path attributes), so only undo what the site sets on them. */
#booklet :where(.page svg) {{ width: auto; height: auto; flex-shrink: 1; float: none; margin: 0; }}
/* ...and from what the site's <body> passes down by inheritance. */
#booklet {{ letter-spacing: normal; text-align: left; text-rendering: auto; -webkit-font-smoothing: auto; }}

{STYLE_START}
{scoped}
{STYLE_END}

/* The cover title is now the page's <h1>; its two parts are spans. */
#booklet h1.cover__title {{ font: inherit; }}
#booklet .cover__code, #booklet .cover__name {{ display: block; }}
/* Contents entries now link to their sheet; same look as before. */
#booklet .toc2 li {{ display: block; }}
#booklet .toc2__link {{ display: grid; grid-template-columns: 2.4em 1fr; gap: .5em; color: inherit; text-decoration: none; }}
/* The other levels on the cover link to their booklet; the link covers
   the whole box without changing its layout. */
#booklet .lvl:has(.lvl__link) {{ position: relative; }}
#booklet .lvl__link {{ color: inherit; text-decoration: none; }}
#booklet .lvl__link::after {{ content: ""; position: absolute; inset: 0; border-radius: inherit; }}
"""
    open(path, "w", encoding="utf-8").write(css)


# ---------------------------------------------------------------- chrome

def site_chrome():
    """Head, header and footer of an existing root page (dictionary.html),
    with relative URLs rewritten for pages one folder deep."""
    page = open(os.path.join(ROOT, "dictionary.html"), encoding="utf-8").read()
    head = page[:page.index("</head>")]
    head = head[head.index("<link rel=\"icon\""):]
    header = page[page.index("<body"):page.index('<nav class="breadcrumbs"')]
    header = header.replace(' aria-current="page"', "")
    header = header.replace('<a href="index.html#grammar">', '<a href="index.html#grammar" aria-current="page">', 1)
    footer = page[page.index('<button type="button" class="dict-widget-toggle"'):]
    footer = re.sub(r'\s*<script src="assets/js/dictionary\.js"></script>', "", footer)
    footer = add_irregular_verbs(footer)

    def rel(s):
        return re.sub(r'((?:href|src|data-index-src)=")(?!https?:|#|data:|mailto:|/)', r"\1" + REL, s)
    return rel(head), rel(header), rel(footer)


def add_irregular_verbs(footer):
    """Adds the floating Irregular Verbs button and panel, copied from the
    Simple Past I lesson page, with the same position modifiers it uses
    for the Dictionary and back-to-top buttons."""
    lesson = open(os.path.join(ROOT, "levels", "a2", "simple-past-i.html"), encoding="utf-8").read()
    start = lesson.index('<button type="button" class="irregular-verbs-toggle"')
    end = lesson.index("</div>", lesson.index('<p class="irregular-verbs-panel__footer">')) + len("</div>")
    widget = lesson[start:end].replace('href="../../', 'href="')  # root-relative, like the rest of the footer
    footer = footer.replace('class="dict-widget-toggle"', 'class="dict-widget-toggle dict-widget-toggle--with-irregular-verbs"', 1)
    footer = footer.replace('class="dict-widget-panel"', 'class="dict-widget-panel dict-widget-panel--with-irregular-verbs"', 1)
    footer = footer.replace("back-to-top back-to-top--with-dict\"", "back-to-top back-to-top--with-dict-and-irregular\"", 1)
    scripts = footer.index("    <script src=")
    footer = footer[:scripts] + "    " + widget + "\n" + footer[scripts:]
    return footer.replace('<script src="assets/js/dict-widget.js"></script>',
                          '<script src="assets/js/dict-widget.js"></script>\n'
                          '    <script src="assets/js/irregular-verbs.js"></script>'
                          '<script src="assets/js/irregular-verbs-panel.js"></script>', 1)


def nav_button(slug, direction):
    i = [l[2] for l in LEVELS].index(slug)
    j = i + (1 if direction == "next" else -1)
    if not 0 <= j < len(LEVELS):
        return ""
    code, name, other = LEVELS[j]
    title = booklet_title(other)
    if direction == "next":
        return (f'<a class="btn btn--accent booklet-nav__next" href="english-classes-{other}.html" rel="next">'
                f'<span class="booklet-nav__text"><small>Next level</small>{title}</span> {ARROW}</a>')
    return (f'<a class="btn btn--ghost booklet-nav__prev" href="english-classes-{other}.html" rel="prev">'
            f'{ARROW_BACK} <span class="booklet-nav__text"><small>Previous level</small>{title}</span></a>')


def booklet_title(slug):
    src = open(booklet_path(slug), encoding="utf-8").read()
    code = re.search(r'class="cover__code">([^<]+)<', src).group(1)
    name = re.search(r'class="cover__name">([^<]+)<', src).group(1)
    return f"{code} {name}"


def print_button():
    return (f'<button type="button" class="btn btn--ghost booklet-print" data-booklet-print>'
            f'{PRINTER} Print / Save as PDF</button>')


def toolbar(slug, where):
    prev, nxt = nav_button(slug, "prev"), nav_button(slug, "next")
    label = "Booklet navigation" if where == "top" else "Continue studying"
    return (f'<nav class="booklet-nav booklet-nav--{where}" aria-label="{label}">'
            f'<div class="booklet-nav__side">{prev}</div>'
            f'<div class="booklet-nav__middle">{print_button()}</div>'
            f'<div class="booklet-nav__side booklet-nav__side--end">{nxt}</div></nav>')


def build(slug):
    style, body = read_source(slug)
    title = booklet_title(slug)
    overview = re.search(r'<p class="cover__overview">(.*?)</p>', body, re.S)
    desc = html.escape(html.unescape(re.sub("<[^>]+>", "", overview.group(1))), quote=True) if overview else ""
    head, header, footer = site_chrome()
    content = convert_body(body)
    # the navigation sits between the cover and the first sheet
    cover_end = content.index("</section>") + len("</section>")
    content = content[:cover_end] + "\n" + toolbar(slug, "top") + content[cover_end:]

    page_title = f"{title} Grammar Booklet — Renan the Teacher"
    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{page_title}</title>
<meta name="description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Renan the Teacher">
<meta property="og:title" content="{page_title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="https://renangrossi.github.io/englishclasses/assets/img/og-social-card.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{page_title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="https://renangrossi.github.io/englishclasses/assets/img/og-social-card.jpg">
{head.strip()}
<link rel="stylesheet" href="{REL}assets/css/lessons.css">
<link rel="stylesheet" href="{REL}assets/css/booklet-print.css">
<link rel="stylesheet" href="{REL}assets/css/booklet.css">
</head>
{header.strip()}
    <nav class="breadcrumbs" aria-label="Breadcrumb">
        <ol>
        <li><a href="{REL}index.html">Home</a></li><li><a href="{REL}index.html#grammar">Grammar</a></li><li aria-current="page">{title}</li>
        </ol>
    </nav>
    <main id="main-content" class="site-main">
<div id="booklet" class="booklet" data-level="{slug}">
{START}{content}{END}
{toolbar(slug, "bottom")}
</div>
{footer.replace('<script src="' + REL + 'assets/js/dict-widget.js"></script>', '<script src="' + REL + 'assets/js/dict-widget.js"></script>' + chr(10) + '    <script src="' + REL + 'assets/js/booklet.js"></script>')}"""
    return style, doc


def main():
    styles = {}
    docs = {}
    for _, _, slug in LEVELS:
        if not os.path.exists(booklet_path(slug)):
            sys.exit(f"missing {booklet_path(slug)}")
    for _, _, slug in LEVELS:
        style, doc = build(slug)
        docs[slug] = doc
        if style is not None:
            styles[slug] = style
    if len(set(styles.values())) > 1:
        sys.exit("The booklets' stylesheets differ; this script assumes they share one.")
    write_print_css(next(iter(styles.values())) if styles else None)
    for slug, doc in docs.items():
        open(booklet_path(slug), "w", encoding="utf-8").write(doc)
        print("built", os.path.relpath(booklet_path(slug), ROOT))


if __name__ == "__main__":
    main()
