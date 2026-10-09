"""
Shared page chrome (head/header/nav/search-overlay/footer/AI-Teacher-panel)
for generated lesson pages -- extracted verbatim from an existing hand-written
page (levels/a1/to-be-am-is-are.html) so a generated page is byte-for-byte
consistent with the rest of the site's chrome. Only the lesson-specific
<main> content differs page to page; see build_lesson.py.

REL is the relative path prefix from the generated file back to the repo
root, e.g. "../../" for levels/{level}/{lesson}.html (two levels deep,
matching every existing levels/a1/*.html page).
"""

import html as _html

# The site is served from a project subpath, not a domain root -- every
# absolute URL below has to keep the /englishclasses/ segment or the link
# previews point at a 404.
SITE_ORIGIN = "https://renangrossi.github.io/englishclasses/"
SITE_NAME = "Renan the Teacher"
OG_IMAGE = SITE_ORIGIN + "assets/img/og-social-card.jpg"
OG_IMAGE_ALT = "Renan the Teacher \u2014 English Language Academy"
OG_IMAGE_W, OG_IMAGE_H = "1200", "630"

LEVELS = [
    ("Pre-A1", "Survival English", "pre-a1"),
    ("A1", "Beginner", "a1"),
    ("A2", "Elementary", "a2"),
    ("B1", "Intermediate", "b1"),
    ("B2", "Upper Intermediate", "b2"),
    ("C1", "Advanced", "c1"),
    ("C2", "Proficient", "c2"),
]


def nav_levels_html(rel, active_level_code):
    items = []
    for code, name, slug in LEVELS:
        current = ' aria-current="page"' if code.upper() == (active_level_code or "").upper() else ""
        items.append(
            f'<li><a href="{rel}levels/{slug}.html"{current}><span>{name}</span>'
            f'<span class="level-code">{code}</span></a></li>'
        )
    return "".join(items)


def page_url(page_path):
    """Absolute https URL for a repo-relative page path ("levels/b2/x.html")."""
    page_path = str(page_path).replace("\\", "/").lstrip("/")
    if page_path == "index.html":          # the home page canonicalises to the site root
        return SITE_ORIGIN
    return SITE_ORIGIN + page_path


def _esc(s):
    """Escape for an HTML attribute. Everything that reaches a meta tag goes
    through this -- an unescaped & or " in a title silently truncates the
    attribute and can cost a crawler the whole tag."""
    return _html.escape(str(s or ""), quote=True)


def preview_text(description, limit=200):
    """Trim a description to something that reads as a finished sentence.

    36 of the site's meta descriptions were truncated at a fixed character
    count when they were authored and stop mid-word ("...a handful of very
    common o"), which is exactly what a WhatsApp card puts under the title.
    Prefer the last complete sentence; fall back to the last whole word.
    """
    s = " ".join(str(description or "").split())
    if not s:
        return s
    if len(s) <= limit and s[-1] in ".!?\u2019\u201d)":
        return s
    window = s[:limit]
    cut = max(window.rfind(". "), window.rfind("! "), window.rfind("? "))
    if cut >= 60:                       # a sentence break worth keeping
        return window[:cut + 1]
    if s[-1] in ".!?\u2019\u201d)" and len(s) <= limit:
        return s
    word = window.rfind(" ")
    trimmed = (window[:word] if word > 0 else window).rstrip(" ,;:-\u2014")
    return trimmed + "\u2026"


def social_meta(page_path, title, description, og_type="website",
                image=OG_IMAGE, image_alt=OG_IMAGE_ALT):
    """The canonical link plus the Open Graph and Twitter block for one page.

    Single source of truth: head() below, build_booklet_pages.py and
    build_social_meta.py all render their tags from here, so the site
    cannot drift into three slightly different versions of this block.

    `title` is the page's own <title>; the trailing site name is dropped for
    og:title because og:site_name already carries the brand and link
    previews truncate hard -- "Paired Expressions - B2 English Grammar"
    survives where "... - Renan the Teacher" would be cut off.
    """
    url = page_url(page_path)
    og_title = title
    for suffix in (" \u2014 " + SITE_NAME, " - " + SITE_NAME, " | " + SITE_NAME):
        if og_title.endswith(suffix):
            og_title = og_title[: -len(suffix)]
            break
    # Lesson descriptions are authored as "Topic: what it teaches"; next to
    # og:title that prefix just repeats itself in the preview card.
    og_desc = description
    # the topic is the part before the first em-dash separator
    # ("Paired Expressions - B2 English Grammar" -> "Paired Expressions")
    topic = og_title.split(" \u2014 ")[0].strip()
    for prefix in (topic + ": ", og_title + ": "):
        if og_desc.startswith(prefix):
            og_desc = og_desc[len(prefix):]
            break
    og_desc = preview_text(og_desc)
    return "\n".join([
        f'<link rel="canonical" href="{_esc(url)}">',
        f'<meta property="og:type" content="{_esc(og_type)}">',
        f'<meta property="og:site_name" content="{_esc(SITE_NAME)}">',
        f'<meta property="og:url" content="{_esc(url)}">',
        f'<meta property="og:title" content="{_esc(og_title)}">',
        f'<meta property="og:description" content="{_esc(og_desc)}">',
        f'<meta property="og:image" content="{_esc(image)}">',
        f'<meta property="og:image:secure_url" content="{_esc(image)}">',
        f'<meta property="og:image:type" content="image/jpeg">',
        f'<meta property="og:image:width" content="{OG_IMAGE_W}">',
        f'<meta property="og:image:height" content="{OG_IMAGE_H}">',
        f'<meta property="og:image:alt" content="{_esc(image_alt)}">',
        f'<meta property="og:locale" content="en_US">',
        f'<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{_esc(og_title)}">',
        f'<meta name="twitter:description" content="{_esc(og_desc)}">',
        f'<meta name="twitter:image" content="{_esc(image)}">',
        f'<meta name="twitter:image:alt" content="{_esc(image_alt)}">',
    ])


def head(rel, title, description, page_path=None, og_type="website"):
    """`page_path` is the page's repo-relative path ("levels/b2/x.html"); it is
    what og:url and the canonical link are built from, so it must be passed for
    a page to be shareable. Without it the social block is omitted rather than
    emitted with a wrong URL."""
    social = social_meta(page_path, title, description, og_type) if page_path else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{_esc(title)}</title>
<meta name="description" content="{_esc(description)}">
{social}
<link rel="icon" href="{rel}assets/img/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="{rel}assets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,500&family=Source+Sans+3:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{rel}assets/css/tokens.css">
<link rel="stylesheet" href="{rel}assets/css/base.css">
<link rel="stylesheet" href="{rel}assets/css/components.css">
<link rel="stylesheet" href="{rel}assets/css/layout.css">
<link rel="stylesheet" href="{rel}assets/css/dark-mode.css">
<link rel="stylesheet" href="{rel}assets/css/ai-teacher.css">
<link rel="stylesheet" href="{rel}assets/css/search.css">
<link rel="stylesheet" href="{rel}assets/css/exercises.css"><link rel="stylesheet" href="{rel}assets/css/lessons.css">
<link rel="stylesheet" href="{rel}assets/css/reading-print.css">
<script>
(function(){{try{{var t=localStorage.getItem('theme');if(!t){{t=window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';}}document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}}})();
</script>
</head>"""


def header(rel, active_level_code, breadcrumb_html, body_class=""):
    """body_class marks what kind of page this is, so a stylesheet can scope
    rules to it. Reading pages pass "reading-page", which is what the print
    layout in assets/css/exercises.css keys off: a grammar lesson prints
    through assets/css/booklet-print.css and must not inherit any of it."""
    return f"""<body class="{body_class}" data-level-code="{active_level_code}">
    <a class="skip-link" href="#main-content">Skip to content</a>
    <header class="site-header">
        <div class="site-header__bar">
            <a class="brand" href="{rel}index.html">
                <img class="brand__mark" src="{rel}assets/img/logo-1776.webp" alt="" width="38" height="38" loading="lazy">
                <span class="brand__text">
                    <span class="brand__name">Renan the Teacher</span>
                    <span class="brand__tagline">English Language Academy</span>
                </span>
            </a>
            <nav class="primary-nav" id="primary-nav" role="navigation" aria-label="Main navigation">
                <ul class="primary-nav__list">
                <li><a href="{rel}index.html">Home</a></li>
                <li><a href="{rel}index.html#grammar">Grammar</a></li>
                <li class="nav-drop">
                    <button type="button" class="nav-drop__toggle" aria-haspopup="true" aria-expanded="false">
                        Levels <span class="nav-drop__caret" aria-hidden="true"></span>
                    </button>
                    <ul class="nav-drop__menu" role="menu">
                    {nav_levels_html(rel, active_level_code)}
                    </ul>
                </li>
                <li><a href="{rel}exercises.html">Exercises</a></li>
                <li><a href="{rel}simulated-exams.html">Simulated Exams</a></li>
                <li><a href="{rel}extras.html">Extras</a></li>
                <li><a href="{rel}dictionary.html">Dictionary</a></li>
                </ul>
            </nav>
            <div class="nav-utility">
                <button type="button" class="theme-toggle" data-search-toggle aria-label="Search the site" aria-haspopup="dialog">
                    <svg class="" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>
                </button>
                <button type="button" class="theme-toggle" data-theme-toggle aria-label="Switch to dark mode">
                    <svg class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
                    <svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 14.5A8.5 8.5 0 1 1 9.5 4a7 7 0 0 0 10.5 10.5Z"/></svg>
                </button>
                <button type="button" class="nav-toggle" data-nav-toggle aria-label="Open menu" aria-expanded="false" aria-controls="primary-nav">
                    <span class="nav-toggle__icon"></span>
                </button>
            </div>
        </div>
    </header>
    <div class="search-overlay" data-search-overlay hidden>
        <div class="search-modal" role="dialog" aria-modal="true" aria-label="Site search" data-index-src="{rel}assets/data/search-index.json">
            <div class="search-modal__bar">
                <svg class="search-modal__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>
                <input type="search" class="search-modal__input" data-search-input placeholder="Search lessons, grammar, vocabulary, exercises&hellip;" aria-label="Search">
                <button type="button" class="search-modal__close" data-search-close aria-label="Close search"><svg class="" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 6 6 18"/><path d="M6 6l12 12"/></svg></button>
            </div>
            <div class="search-modal__results" data-search-results>
                <p class="search-modal__hint">Type at least 2 characters to search across every level, lesson, grammar topic, exercise and mock exam.</p>
            </div>
        </div>
    </div>
    <nav class="breadcrumbs" aria-label="Breadcrumb">
        <ol>
        {breadcrumb_html}
        </ol>
    </nav>
    <main id="main-content" class="site-main">"""


IRREGULAR_VERBS_WIDGET = """<button type="button" class="irregular-verbs-toggle" data-irregular-verbs-toggle aria-label="Open the irregular verbs list" aria-expanded="false" aria-haspopup="dialog">
        <svg class="" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 6h13"/><path d="M8 12h13"/><path d="M8 18h13"/><path d="M3 6h.01"/><path d="M3 12h.01"/><path d="M3 18h.01"/></svg>
        <span class="irregular-verbs-toggle__label">Irregular Verbs</span>
    </button>
    <div class="irregular-verbs-panel" data-irregular-verbs-panel hidden role="dialog" aria-label="Irregular verbs list" aria-modal="false">
        <div class="irregular-verbs-panel__bar">
            <input type="text" data-verb-filter placeholder="Type any form, e.g. “went” or “go”" aria-label="Search irregular verbs" autocomplete="off">
            <button type="button" class="irregular-verbs-panel__close" data-irregular-verbs-close aria-label="Close irregular verbs list"><svg class="" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 6 6 18"/><path d="M6 6l12 12"/></svg></button>
        </div>
        <div class="irregular-verbs-panel__body" data-irregular-verbs-body>
            <p class="notice" data-verb-count hidden></p>
            <p class="irregular-verbs-panel__loading" data-irregular-verbs-loading>Loading the verb list…</p>
            <p class="notice" data-verb-empty hidden>No verb matches “<span data-verb-empty-term></span>.” Try a different spelling.</p>
        </div>
        <p class="irregular-verbs-panel__footer"><a href="{rel}irregular-verbs.html" target="_blank" rel="noopener">Open the full page ↗</a></p>
    </div>"""

def footer(rel):
    return f"""<button type="button" class="dict-widget-toggle" data-dict-widget-toggle aria-label="Open quick dictionary" aria-expanded="false" aria-haspopup="dialog">
        <svg class="" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2Z"/></svg>
    </button>
    <div class="dict-widget-panel" data-dict-widget-panel hidden>
        <div class="dict-widget__bar">
            <input type="text" data-dict-widget-input placeholder="Look up a word…" aria-label="Look up a word">
            <button type="button" class="dict-widget__close" data-dict-widget-close aria-label="Close dictionary"><svg class="" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 6 6 18"/><path d="M6 6l12 12"/></svg></button>
        </div>
        <div class="dict-widget__result" data-dict-widget-result>
            <p class="dict-widget__hint">Type a word to see its definition without leaving this page.</p>
        </div>
        <div class="dict-widget__links" data-dict-widget-links></div>
    </div>
    </main>
    <footer class="site-footer">
        <div class="site-footer__inner">
            <div>
                <a class="brand" href="{rel}index.html">
                    <img class="brand__mark" src="{rel}assets/img/logo-1776.webp" alt="" width="38" height="38" loading="lazy">
                    <span class="brand__text">
                        <span class="brand__name">Renan the Teacher</span>
                        <span class="brand__tagline">English Language Academy</span>
                    </span>
                </a>
                <p class="site-footer__blurb">A CEFR-aligned English course built one honest, carefully-checked lesson at a time &mdash; from first greetings to proficiency.</p>
            </div>
            <div class="footer-col">
                <h4>Levels</h4>
                <ul>
                    <li><a href="{rel}levels/a1.html">A1 &mdash; Beginner</a></li>
                    <li><a href="{rel}levels/a2.html">A2 &mdash; Elementary</a></li>
                    <li><a href="{rel}levels/b1.html">B1 &mdash; Intermediate</a></li>
                    <li><a href="{rel}levels/b2.html">B2 &mdash; Upper Intermediate</a></li>
                    <li><a href="{rel}levels/c1.html">C1 &mdash; Advanced</a></li>
                    <li><a href="{rel}levels/c2.html">C2 &mdash; Proficient</a></li>
                </ul>
            </div>
            <div class="footer-col">
                <h4>Practice</h4>
                <ul>
                    <li><a href="{rel}index.html#grammar">Grammar Booklets</a></li>
                    <li><a href="{rel}exercises.html">Reading &amp; Exercises</a></li>
                    <li><a href="{rel}simulated-exams.html">Simulated Exams</a></li>
                    <li><a href="{rel}dictionary.html">Dictionary &amp; Reference</a></li>
                    <li><a href="{rel}extras.html">Extras</a></li>
                </ul>
            </div>
            <div class="footer-col">
                <h4>About CEFR</h4>
                <ul>
                    <li><a href="{rel}index.html#about-cefr">What is the CEFR?</a></li>
                    <li><a href="{rel}index.html#why-us">Why learn with us</a></li>
                    <li><a href="{rel}index.html#mission">Our mission</a></li>
                </ul>
            </div>
        </div>
        <div class="site-footer__bottom">
            <p>&copy; 1776 Renan the Teacher English Course. All rights reserved.</p>
        </div>
    </footer>
    <button type="button" class="back-to-top back-to-top--with-dict" data-back-to-top aria-label="Back to top">
        <svg class="" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 19V5"/><path d="m5 12 7-7 7 7"/></svg>
    </button>
    <button type="button" class="ai-teacher-toggle" data-ai-teacher-toggle aria-label="Ask the AI English Teacher" aria-expanded="false" aria-haspopup="dialog">
        <svg class="" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m22 10-10-5L2 10l10 5 10-5Z"/><path d="M6 12v5c0 1.5 2.5 3 6 3s6-1.5 6-3v-5"/><path d="M22 10v6"/></svg>
        <span class="ai-teacher-toggle__label">AI Teacher</span>
    </button>
    <div class="ai-teacher-panel" data-ai-teacher-panel hidden role="dialog" aria-label="AI English Teacher chat" aria-modal="false">
        <div class="ai-teacher-panel__bar">
            <div class="ai-teacher-panel__brand">
                <svg class="ai-teacher-panel__brand-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m22 10-10-5L2 10l10 5 10-5Z"/><path d="M6 12v5c0 1.5 2.5 3 6 3s6-1.5 6-3v-5"/><path d="M22 10v6"/></svg>
                <div>
                    <strong>AI English Teacher</strong>
                    <span>Ask a grammar, vocabulary or exercise question</span>
                </div>
            </div>
            <button type="button" class="ai-teacher-panel__close" data-ai-teacher-close aria-label="Close AI Teacher"><svg class="" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 6 6 18"/><path d="M6 6l12 12"/></svg></button>
        </div>
        <div class="ai-teacher-panel__messages" data-ai-teacher-messages role="log" aria-live="polite">
            <div class="ai-teacher-msg ai-teacher-msg--bot">
                <p>Hi! I can help you with English. Ask me about grammar, words, or exercises.<br>Example: <em>&ldquo;Explain present perfect&rdquo;</em> or <em>&ldquo;Give me an exercise about conditionals.&rdquo;</em></p>
            </div>
        </div>
        <form class="ai-teacher-panel__form" data-ai-teacher-form>
            <label for="ai-teacher-input" class="visually-hidden">Your question</label>
            <textarea id="ai-teacher-input" data-ai-teacher-input rows="1" maxlength="600" placeholder="Type your question&hellip;" required></textarea>
            <button type="submit" class="ai-teacher-panel__send" data-ai-teacher-send aria-label="Send question"><svg class="" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg></button>
        </form>
        <p class="ai-teacher-panel__hint" data-ai-teacher-hint>Answers come from an AI model and may occasionally be wrong &mdash; always double-check against your lesson material. Nothing you type is stored after you close this window.</p>
    </div>
    <script src="{rel}assets/js/main.js"></script>
    <script src="{rel}assets/js/search.js"></script>
    <script src="{rel}assets/js/ai-teacher.js" data-ai-endpoint="https://ai-teacher.englishclasses.workers.dev"></script>
    <script src="{rel}assets/js/dict-widget.js"></script>
    <script src="{rel}assets/js/progress.js"></script><script src="{rel}assets/js/exercises.js"></script>
</body>
</html>
"""


def with_irregular_verbs(footer_html, rel=""):
    """Adds the floating Irregular Verbs list under the Dictionary button.

    The grammar lessons that need irregular-verb recall carry this widget, and
    the three position modifiers below are what stack the buttons: the verbs
    toggle takes the bottom slot, the dictionary moves up one step and
    back-to-top up two. Behaviour comes from the two scripts, which lift the
    213-row table out of irregular-verbs.html and anchor that URL to their own
    location, so this works at any page depth.

    Markup is held here rather than scraped from a built page: the booklet
    generator scrapes, and its regexes stopped matching once the pages were
    asset-stamped, which silently dropped these very scripts.
    """
    out = footer_html.replace(
        'class="dict-widget-toggle"',
        'class="dict-widget-toggle dict-widget-toggle--with-irregular-verbs"', 1)
    out = out.replace(
        'class="dict-widget-panel"',
        'class="dict-widget-panel dict-widget-panel--with-irregular-verbs"', 1)
    out = out.replace(
        'class="back-to-top back-to-top--with-dict"',
        'class="back-to-top back-to-top--with-dict-and-irregular"', 1)
    widget = IRREGULAR_VERBS_WIDGET.format(rel=rel)
    anchor = out.index("    <script src=")
    out = out[:anchor] + "    " + widget + "\n" + out[anchor:]
    return out.replace(
        f'<script src="{rel}assets/js/dict-widget.js"></script>',
        f'<script src="{rel}assets/js/dict-widget.js"></script>\n'
        f'    <script src="{rel}assets/js/irregular-verbs.js"></script>'
        f'<script src="{rel}assets/js/irregular-verbs-panel.js"></script>', 1)
