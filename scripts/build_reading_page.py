#!/usr/bin/env python3
"""
Build reading/{level}/{slug}.html from content/readings/{level}/{slug}.json.

Deliberately separate from scripts/build_lesson.py: that script builds the
grammar lessons from curriculum/*.json, and re-running it on an existing
lesson destroys enrichment those built pages hold but their JSON no longer
does. Nothing here touches levels/ or curriculum/.

Page shape (reusing the site's existing components verbatim -- no new CSS,
no new JS):

    page-header          level eyebrow + title + lede
    level-toc            jump links
    #listen-and-read     <audio controls> then the passage
    #vocabulary          optional word list
    #practice            .exercise-block JSON for assets/js/exercises.js
    #discussion          optional speaking/writing prompts

Usage:
    python3 scripts/build_reading_page.py                      # build all
    python3 scripts/build_reading_page.py b1/nfl               # build one
"""
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reading_common as rc
import site_chrome

REL = "../../"
STAR = ('<svg class="" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
        '<path d="m12 2 2.9 6.9 7.1.6-5.4 4.7 1.6 7L12 17.5 5.8 21.2l1.6-7L2 9.5l7.1-.6Z"/></svg>')
STARS_ROW = f'<div class="stars-row stars-row--onlight" aria-hidden="true">{STAR * 11}</div>'
PRINTER_SVG = ('<svg class="" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" '
               'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
               '<path d="M6 9V2h12v7"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/>'
               '<path d="M6 14h12v8H6Z"/></svg>')
# The reading page *is* the document now -- the per-text PDFs it replaced have
# been deleted -- so every page carries its own "Print / Save as PDF".
PRINT_BTN = (f'<button type="button" class="btn btn--ghost btn--small print-hidden" data-print-page>'
             f'{PRINTER_SVG}Print / Save as PDF</button>')


def esc(s):
    return html.escape(str(s), quote=False)


# A title set between asterisks, the way anyone writing plain text marks one.
# The JSON is hand-written, so this is the only markup it is allowed to carry.
EMPHASIS_RE = re.compile(r"\*([^*\n]+)\*")


def _emphasis(escaped):
    """Turn *...* into <em>...</em> in text that has ALREADY been escaped."""
    return EMPHASIS_RE.sub(r"<em>\1</em>", escaped)


def _caption(text):
    """Escape, then turn *...* into italics. Captions carry a work's title, and
    a title is set in italics -- but the JSON is written by hand, so it uses
    asterisks rather than HTML."""
    return _emphasis(esc(text))


def _surface_patterns(term):
    """Regexes for the ways a glossary headword can appear in running text.

    A vocabulary list is written in dictionary form -- "to grind", "a bye
    week", "try something on", "check in / check out", "It's worth (doing)" --
    but the passage contains the inflected, article-less, separated thing:
    "grinding", "bye week", "try it on", "checked in", "it is worth knowing".
    So each headword becomes a set of patterns, longest-first.

    Placeholders matter most: an English phrasal verb splits around its object
    ("cheer someone up" -> "cheer you up"), which a literal search can never
    find."""
    pats = []
    for alt in re.split(r"\s*/\s*", term):
        alt = alt.strip().strip("\u2026.?!\u2019'\"")
        alt = re.sub(r"\s*\(.*?\)\s*", " ", alt).strip()
        alt = re.sub(r"^(to|a|an|the)\s+", "", alt, flags=re.I).strip()
        # Two letters is a real headword ("an ox"); the word boundaries in the
        # pattern are what stop it claiming the inside of a longer word.
        if len(alt) < 2:
            continue
        words = alt.split()
        head, rest = words[0], words[1:]

        # "it's" also appears written out as "it is"
        heads = {head}
        if head.lower() == "it's":
            heads |= {"it is"}

        # Inflections of the first word, which is the one that changes.
        #
        # Being generous here is cheap and being stingy is not. A form that
        # exists in no English text ("buildd") simply never matches and costs
        # nothing; a form that is missing means a word is defined in the
        # glossary and then never highlighted in the passage that defines it,
        # which is what scripts/check_content.py reports. So the rules below
        # over-generate on purpose. The only thing that must stay tight is the
        # word boundary in the pattern itself, which is what stops a short
        # headword from claiming the inside of a longer word.
        forms = set()
        for h in heads:
            forms |= {h, h + "s", h + "es", h + "ed", h + "d", h + "ing",
                      h + "er", h + "est"}
            if len(h) > 3 and h.endswith("e"):
                forms |= {h[:-1] + "ing", h[:-1] + "er", h[:-1] + "est"}
            if len(h) > 3 and h.endswith("y"):
                forms |= {h[:-1] + "ies", h[:-1] + "ied", h[:-1] + "ier"}
            # -able/-ible/-le adverbs: formidable -> formidably, simple ->
            # simply, terrible -> terribly.
            if len(h) > 3 and h.endswith("le"):
                forms |= {h[:-1] + "y"}
            # Consonant doubling: flag -> flagged, plan -> planned, stop ->
            # stopped. The old rule required the third-last letter to be a
            # consonant, which rejected "acquit" (the u of qu reads as a vowel
            # to a letter test) and "court-martial" (British -ll-). Since a
            # spurious form is harmless, every consonant-final headword now
            # gets the doubled set.
            if len(h) >= 3 and h[-1].isalpha() and h[-1] not in "aeiouwxy":
                d2 = h + h[-1]
                forms |= {d2 + "ed", d2 + "ing", d2 + "er", d2 + "est"}
        # Irregular verbs, and the irregular plurals that a glossary headword
        # is written in the singular of: "an ox" has to find "oxen".
        IRREG = {"be": ["is", "are", "was", "were", "been", "'re", "'s", "'m"],
                 "tell": ["told"], "speak": ["spoke", "spoken"],
                 "take": ["took", "taken"], "get": ["got", "gotten"],
                 "have": ["has", "had"], "make": ["made"], "go": ["went", "gone"],
                 "leave": ["left"], "hold": ["held"], "buy": ["bought"],
                 "find": ["found"], "eat": ["ate", "eaten"], "good": ["better", "best"],
                 "build": ["built"], "shoot": ["shot"], "bring": ["brought"],
                 "think": ["thought"], "catch": ["caught"], "teach": ["taught"],
                 "seek": ["sought"], "fight": ["fought"], "lead": ["led"],
                 "feed": ["fed"], "meet": ["met"], "keep": ["kept"],
                 "sleep": ["slept"], "sweep": ["swept"], "lose": ["lost"],
                 "send": ["sent"], "spend": ["spent"], "lend": ["lent"],
                 "strike": ["struck", "stricken"],
                 "bend": ["bent"], "stand": ["stood"], "understand": ["understood"],
                 "win": ["won"], "run": ["ran"], "begin": ["began", "begun"],
                 "drink": ["drank", "drunk"], "sing": ["sang", "sung"],
                 "swim": ["swam", "swum"], "ring": ["rang", "rung"],
                 "write": ["wrote", "written"], "drive": ["drove", "driven"],
                 "ride": ["rode", "ridden"], "rise": ["rose", "risen"],
                 "give": ["gave", "given"], "forgive": ["forgave", "forgiven"],
                 "break": ["broke", "broken"], "choose": ["chose", "chosen"],
                 "freeze": ["froze", "frozen"], "steal": ["stole", "stolen"],
                 "wear": ["wore", "worn"], "tear": ["tore", "torn"],
                 "bear": ["bore", "borne"], "swear": ["swore", "sworn"],
                 "fly": ["flew", "flown"], "grow": ["grew", "grown"],
                 "know": ["knew", "known"], "throw": ["threw", "thrown"],
                 "blow": ["blew", "blown"], "draw": ["drew", "drawn"],
                 "show": ["shown"], "see": ["saw", "seen"],
                 "fall": ["fell", "fallen"], "sell": ["sold"], "feel": ["felt"],
                 "deal": ["dealt"], "mean": ["meant"], "sit": ["sat"],
                 "pay": ["paid"], "say": ["said"], "lay": ["laid"],
                 "lie": ["lay", "lain"], "do": ["did", "done", "does"],
                 "come": ["came"], "become": ["became"], "light": ["lit"],
                 "hear": ["heard"], "hide": ["hid", "hidden"],
                 "ox": ["oxen"], "bureau": ["bureaux", "bureaus"],
                 "child": ["children"], "man": ["men"], "woman": ["women"],
                 "foot": ["feet"], "tooth": ["teeth"], "mouse": ["mice"],
                 "goose": ["geese"], "person": ["people"], "datum": ["data"],
                 "criterion": ["criteria"], "phenomenon": ["phenomena"],
                 "index": ["indices", "indexes"], "appendix": ["appendices"],
                 "analysis": ["analyses"], "crisis": ["crises"],
                 "thesis": ["theses"], "basis": ["bases"], "medium": ["media"]}
        for h in list(heads):
            forms |= set(IRREG.get(h.lower(), []))

        # the rest of the phrase, with placeholders opened up
        tail = []
        for w in rest:
            if w.lower().strip(".,") in ("something", "someone", "somebody", "sth", "sb"):
                tail.append(r"\s+\S+")          # whatever the real object is
            else:
                tail.append(r"\s+" + re.escape(w))
        tail_re = "".join(tail)

        # Longest first so "checked in" wins over "check", then alphabetically:
        # forms is a set, and sorting on length alone leaves equal-length forms
        # in hash order, which changes per process. The first pattern that
        # matches is the one that claims the word, so that made the build
        # non-reproducible -- rebuilding a page moved highlights between
        # occurrences ("the agent" vs "agents") with no source change.
        for f in sorted(forms, key=lambda w: (-len(w), w)):
            pats.append((len(alt), r"(?<![\w-])(" + re.escape(f).replace(r"\ ", r"\s+") + tail_re + r")(?![\w-])"))

        # "to be out of something" carries its meaning in the tail, and the
        # copula is usually contracted onto the subject ("we're out of..."),
        # where a leading word-boundary can never match. Match the tail alone.
        if head.lower() == "be" and rest:
            core = []
            for w in rest:
                if w.lower().strip(".,") in ("something", "someone", "somebody", "sth", "sb"):
                    break
                core.append(re.escape(w))
            if core:
                pats.append((len(alt), r"(?<![\w-])(" + r"\s+".join(core) + r")(?![\w-])"))

        # In a noun phrase it is the LAST word that pluralizes, not the first:
        # "a fitting room" appears as "fitting rooms".
        if rest and not any(r"\S+" in t for t in tail):
            last = rest[-1]
            stem = r"(?<![\w-])(" + re.escape(head) + "".join(tail[:-1]) + r"\s+" + re.escape(last)
            for suf in ("s", "es"):
                pats.append((len(alt), stem + suf + r")(?![\w-])"))
    # Dedupe without losing insertion order, then sort stably. set(pats) here
    # discarded the order the patterns were built in, and the sort key only
    # compares the phrase length, so every pattern from the same headword tied
    # and fell back on the set's hash order -- which differs per process. The
    # first matching pattern is the one that claims the word, so two builds of
    # an unchanged page could highlight different occurrences of it.
    seen = set()
    uniq = [p for p in pats if not (p in seen or seen.add(p))]
    return [p for _, p in sorted(uniq, key=lambda x: -x[0])]


# "Receptionist:", "You:", "Emma:" -- a dialogue turn, as opposed to prose
# that merely contains a colon. The label is short, starts capitalised and is
# followed by the speaker's line.
SPEAKER_RE = re.compile(r"^[A-Z][\w .'\-]{0,24}:\s")


# A numbered section heading inside a passage -- "1. Booking a room" --
# as opposed to a sentence that merely starts with a figure. It is short,
# it does not end in sentence punctuation, and it opens with "N.".
NUMBERED_HEADING_RE = re.compile(r"^\d+\.\s+\S")


def is_heading(para):
    t = para.strip()
    if not t:
        return False
    # "1. Booking a room" -- a numbered section heading.
    if NUMBERED_HEADING_RE.match(t) and len(t) <= 70 and t[-1] not in ".!?:;":
        return True
    # "The Fox and the Grapes" -- a short titled heading with no number. It has
    # to be short, end without sentence punctuation, and not be a line of
    # dialogue, which is also short and unpunctuated at the end.
    if (len(t) <= 60 and t[-1] not in ".!?:;,\u201d\u2019\"'"
            and not SPEAKER_RE.match(t) and len(t.split()) <= 9):
        return True
    letters = [c for c in t if c.isalpha()]
    return bool(letters) and sum(c.isupper() for c in letters) / len(letters) > 0.6


def annotate(paras, vocab):
    """Bold the first occurrence of each glossary word in the passage and hang
    its definition off it, so the reader can hover (or tap, or tab to) the word
    instead of consulting a separate list. Reuses the site's existing
    .vocab-term style, which was defined in exercises.css and never used.

    Each term is marked at most once, across the whole passage -- marking every
    occurrence would turn a page into a field of underlines."""
    # A glossary entry may pin the exact surface form to highlight via "match".
    # Auto-matching cannot tell senses apart: "to exchange" (return goods)
    # happily attached itself to "exchanges" meaning conversations, so the
    # author needs a way to say which word is meant.
    todo = []
    for i, v in enumerate(vocab or []):
        if v.get("match"):
            pats = [r"(?<![\w-])(" + re.escape(v["match"]).replace(r"\ ", r"\s+") + r")(?![\w-])"]
        else:
            pats = _surface_patterns(v["term"])
        todo.append((v["term"], (v["definition"], i), pats))
    out = []
    placed = set()
    headings = set()  # indices of all-caps section headings inside the passage
    slot = []  # rendered spans, substituted back after escaping

    for idx, para in enumerate(paras):
        text = para
        # A section heading inside the passage is not prose, and highlighting
        # a word in one produced "1. Booking a flight by phone" with the
        # definition hanging off the heading itself. Two shapes count: a
        # short numbered line with no sentence-ending punctuation, which is
        # how these texts number their sections, and a line in capitals,
        # kept because the sources originally wrote them that way.
        if is_heading(para):
            headings.add(idx)
            out.append(text)
            continue
        # Find, for this paragraph, the earliest match of any unplaced term.
        while True:
            best = None
            for term, definition, forms in todo:
                if term in placed:
                    continue
                for pat in forms:
                    m = re.search(pat, text, re.I)
                    if m and (best is None or m.start() < best[0].start()):
                        best = (m, term, definition)
                        break
            if best is None:
                break
            m, term, definition = best
            placed.add(term)
            token = f"\x00{len(slot)}\x00"
            slot.append((m.group(1), definition))
            text = text[:m.start()] + token + text[m.end():]
        out.append(text)

    rendered = []
    for text in out:
        t = esc(text)
        # A case name, a newspaper, a book title: the passage marks these with
        # asterisks exactly as a caption does, and they used to print as
        # literal asterisks because only captions were converted. Run it on the
        # escaped text BEFORE the spans go in, so nothing scans generated HTML.
        t = _emphasis(t)
        for i, (word, (definition, vi)) in enumerate(slot):
            # data-definition drives the CSS tooltip, which only a sighted
            # reader gets; aria-describedby points at the same words in the Key
            # Vocabulary list below, which is what a screen reader reads out.
            t = t.replace(
                f"\x00{i}\x00",
                f'<span class="vocab-term" tabindex="0" role="note" '
                f'aria-describedby="vocab-{vi}" '
                f'data-definition="{html.escape(definition, quote=True)}">{esc(word)}</span>')
        rendered.append(t)
    return rendered, placed, headings


# Sits with the audio, where it is actually true: it is about this player and
# these highlighted words, not about the page in general. It is marked
# print-hidden because neither playing nor hovering is possible on paper.
READING_INTRO = ('Play the audio and follow along, then read it again on your own. '
                 'Tap or hover over a <span class="vocab-term" tabindex="0" role="note" '
                 'data-definition="Like this one \u2014 the highlighted words carry a '
                 'definition.">highlighted word</span> to see what it means.')


def page_header(d):
    """A thin band: where you are, and the one action the page offers.

    The text's own title belongs immediately above the text, not up here -- a
    title separated from its prose by a navigation bar is a title for the page
    rather than for the reading. So the banner carries the level and topic and
    the Print button, and nothing else. It used to carry a generic "The Text"
    in display type, which was a heading that named nothing.
    """
    topic = rc.TOPIC_LABELS.get(d.get("topic", ""), "")
    eyebrow = f'{d["level"]} &middot; {esc(topic)}' if topic else d["level"]
    return f"""<div class="page-header page-header--slim">
        {STARS_ROW}
        <div class="page-header__inner">
            <div class="page-header__text">
                <p class="eyebrow hero__eyebrow">{eyebrow}</p>
                <p class="page-header__actions print-hidden">{PRINT_BTN}</p>
            </div>
        </div>
    </div>"""


def toc(ids):
    labels = {"listen-and-read": "Reading",
              "practice": "Practice", "discussion": "Discussion"}
    links = "".join(f'<a href="#{i}">{labels[i]}</a>' for i in labels if i in ids)
    return f'<div class="level-toc"><div class="level-toc__inner">{links}</div></div>'


# Commons' short names for the two attribution licences that are not Creative
# Commons. "Attribution" on its own reads as a word rather than a licence, and
# "OGL 3" means nothing to somebody who has not met it; spell both out.
LICENCE_LABEL = {
    "Attribution": "free licence with attribution",
    "OGL 3": "Open Government Licence v3.0",
}


def listen_and_read(d, level, slug):
    """Audio first, then the text. Native <audio controls> is a deliberate
    choice: it gives play/pause, a progress bar, elapsed/total time, keyboard
    access and a playback-speed menu on every modern browser, desktop and
    mobile, with no JavaScript to fail. The <p> inside it is the fallback for
    a browser that cannot play the file at all."""
    marked, placed, headings = annotate(d["passage"], d.get("vocabulary"))
    # Classify each paragraph so the stylesheet can set it correctly. Only
    # running prose takes the first-line indent: an all-caps section heading
    # does not, the paragraph that opens a section does not (it begins the
    # section rather than marking a break inside it), and a dialogue turn
    # does not -- the speaker's name already marks where the turn starts, and
    # indenting turns makes a conversation look like a misprint. Texts that
    # mix the two, such as a prose introduction wrapped around a dialogue,
    # therefore come out right without anyone tagging them by hand.
    def _ptag(i):
        if i in headings:
            return '<p class="reading-passage__heading">'
        if SPEAKER_RE.match(d["passage"][i]):
            return '<p class="reading-passage__turn">'
        if i == 0:
            # The drop cap hangs on this paragraph, so it has to be long
            # enough to sit beside. Under about 200 characters there is not
            # enough text for a three-line cap and it would overhang into
            # whatever follows, so those texts get the two-line version.
            short = " reading-passage__lead--short" if len(d["passage"][0]) < 200 else ""
            return f'<p class="reading-passage__lead{short}">'
        if (i - 1) in headings:
            return '<p class="reading-passage__opener">'
        return "<p>"
    # Images belong to the page but not to the passage: they are listed
    # separately in the source JSON and slotted in after the paragraph each
    # one names. Keeping them out of "passage" means adding a picture never
    # changes the narration fingerprint, so it never forces a re-record.
    figures = {}
    for img in (d.get("images") or []):
        # A plain filename lives in this page's own folder. A path with a
        # slash is relative to assets/img/reading/, so several pages split
        # out of one source document can share its image set -- the three
        # Aesop pages all draw on b2/aesop/.
        rel = img["src"] if "/" in img["src"] else f"{level}/{slug}/{img['src']}"
        src = f"{REL}assets/img/reading/{rel}"
        # A caption names the work: *Title* -- Artist, year. The asterisks are
        # written in the source JSON the way anyone would type an italic title,
        # and become <em> here; nothing else in a caption is markup.
        # A picture used under an attribution licence -- CC BY, CC BY-SA, OGL,
        # Commons' {{Attribution}} -- is free only on condition of a
        # credit, so the credit is part of the figure rather than something kept
        # in a file somebody has to go and find. Public-domain pictures carry no
        # licence field and print nothing here.
        credit = ""
        if img.get("licence"):
            who = esc(img["author"]) if img.get("author") else "unknown"
            lic = esc(LICENCE_LABEL.get(img["licence"], img["licence"]))
            if img.get("source_url"):
                lic = f'<a href="{esc(img["source_url"])}" rel="license nofollow">{lic}</a>'
            # "Photo" unless the image says otherwise: a satellite composite is
            # not a photograph, and its provider asks for its own wording.
            kind = esc(img.get("credit_prefix") or "Photo")
            credit = f'<span class="reading-figure__credit">{kind}: {who}, {lic}</span>'
        cap_text = _caption(img["caption"]) if img.get("caption") else ""
        cap = (f'<figcaption>{cap_text}{credit}</figcaption>'
               if (cap_text or credit) else "")
        # Most illustrations are an aside and sit at about half the measure.
        # Some are the subject: a student comparing one flag with the next has
        # to see the stars. Those are marked "wide" in the source JSON.
        cls = "reading-figure reading-figure--wide" if img.get("wide") else "reading-figure"
        figures.setdefault(int(img.get("after", 0)), []).append(
            f'<figure class="{cls}">'
            f'<img src="{src}" alt="{html.escape(img.get("alt", ""), quote=True)}" loading="lazy">'
            f'{cap}</figure>')
    blocks = []
    for i, p in enumerate(marked):
        blocks.append(f"{_ptag(i)}{p}</p>")
        blocks.extend(figures.get(i, []))
    paras = "\n            ".join(blocks)
    # Hovering works on screen, but a printed page has no hover, and the
    # on-page vocabulary list is gone -- so the definitions come back as a
    # glossary that only exists in print.
    # The same list serves three readers: somebody skimming before they start,
    # somebody using a screen reader (the hover tooltip is invisible to one),
    # and somebody holding a printout, where there is nothing to hover over.
    gloss = "".join(
        f'<li id="vocab-{i}"><strong>{esc(v["term"])}</strong> '
        f'<span class="reading-glossary__def">{esc(v["definition"])}</span></li>'
        for i, v in enumerate(d.get("vocabulary") or []))
    gloss_html = (f'<div class="reading-glossary">'
                  f'<h2 class="reading-glossary__heading">Key Vocabulary</h2>'
                  f'<ul class="reading-glossary__list">{gloss}</ul></div>') if gloss else ""
    source_html = print_source(d, level, slug)
    # The running time is deliberately not printed here: the audio element
    # already shows it (0:00 / 2:44) as soon as the metadata loads, so a
    # second copy in the prose was duplicate furniture. duration_label is
    # still recorded in the source JSON and still checked by the batch script.
    # The title opens the section it names, directly above the audio and the
    # prose, and is the page's only <h1>.
    return f"""<section id="listen-and-read" class="section" aria-labelledby="lr-heading">
        <div class="section__inner">
            <h1 id="lr-heading" class="reading-title">{esc(d['title'])}</h1>
            <p class="reading-subtitle">{esc(d['subtitle'])}</p>
            <p class="reading-intro print-hidden">{READING_INTRO}</p>
            <audio controls preload="metadata" src="{rc.audio_href(level, slug, REL)}">
                <p>Your browser cannot play this audio. <a href="{rc.audio_href(level, slug, REL)}">Download the MP3</a> instead.</p>
            </audio>
            <div class="reading-passage">
            {paras}
            </div>
            {gloss_html}
            {source_html}
        </div>
    </section>"""


def practice(d):
    exs = d.get("exercises") or []
    if not exs:
        return ""
    blocks = "".join(
        '<div class="exercise-block"><script type="application/json" class="exercise-data">'
        f'{json.dumps(ex, ensure_ascii=False)}</script></div>' for ex in exs)
    return f"""<section id="practice" class="section section--surface" aria-labelledby="practice-heading">
        <div class="section__inner">
            <p class="eyebrow">Interactive Exercises</p>
            <h2 id="practice-heading">Practice</h2>
            <p style="color:var(--color-text-muted);margin-bottom:var(--space-md);max-width:60ch;">Complete each exercise, then click <strong>Submit</strong> to see your score and an explanation for every answer.</p>
            {blocks}
        </div>
    </section>"""


def discussion(d):
    prompts = d.get("discussion") or []
    if not prompts:
        return ""
    rows = "".join(f"<li>{esc(p)}</li>" for p in prompts)
    return f"""<section id="discussion" class="section section--tight" aria-labelledby="disc-heading">
        <div class="section__inner">
            <p class="eyebrow">Speaking &amp; Writing</p>
            <h2 id="disc-heading">Discussion</h2>
            <p style="color:var(--color-text-muted);margin-bottom:var(--space-md);max-width:60ch;">There are no right answers here &mdash; use these to practice speaking, or write a short answer to each.</p>
            <ul class="summary-list">{rows}</ul>
        </div>
    </section>"""


SITE_URL = "https://renangrossi.github.io/englishclasses"


def print_source(d, level, slug):
    """Printed once at the foot of the handout. A photocopy that has lost its
    first page should still say where it came from and what level it is."""
    topic = rc.TOPIC_LABELS.get(d.get("topic", ""), "")
    where = f"{d['level']} &middot; {esc(topic)}" if topic else d["level"]
    url = f"{SITE_URL}/reading/{level}/{slug}.html"
    return (f'<p class="print-source">{esc(d["title"])} &mdash; {where} &middot; '
            f'Renan the Teacher, English Language Academy &middot; '
            f'<a href="{url}">{url}</a></p>')


def build(level, slug, d):
    title = f"{d['title']} — {d['level']} Reading & Listening — Renan the Teacher"
    description = d.get("description") or f"{d['title']}: {d['subtitle']}"
    breadcrumb = (
        f'<li><a href="{REL}index.html">Home</a></li>'
        f'<li><a href="{REL}exercises.html">Reading</a></li>'
        f'<li><a href="{REL}levels/{level}.html">{d["level"]}</a></li>'
        f'<li aria-current="page">{esc(d["title"])}</li>'
    )
    body = [listen_and_read(d, level, slug), practice(d), discussion(d)]
    ids = [i for i, s in zip(
        ["listen-and-read", "practice", "discussion"], body) if s]

    out = [
        site_chrome.head(REL, title, description[:300],
                         page_path=f"reading/{level}/{slug}.html", og_type="article"),
        site_chrome.header(REL, d["level"], breadcrumb, body_class="reading-page"),
        page_header(d),
        toc(ids),
        *[s for s in body if s],
        site_chrome.footer(REL),
    ]
    p = rc.page_path(level, slug)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(out), encoding="utf-8")
    return p


def main():
    targets = sys.argv[1:]
    built = 0
    for level, slug, d in rc.all_sources():
        if targets and f"{level}/{slug}" not in targets:
            continue
        p = build(level, slug, d)
        print(f"  built {p.relative_to(rc.REPO_ROOT)}")
        built += 1
    if not built:
        print("nothing to build (no matching content/readings/*.json)")
    else:
        print(f"{built} reading page(s) built")


if __name__ == "__main__":
    main()
