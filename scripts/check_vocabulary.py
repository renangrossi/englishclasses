#!/usr/bin/env python3
"""
Review a reading text's glossary the way a Portuguese speaker would read it.

The students this library is written for speak Portuguese. That changes which
English words are worth a definition and which are not, and the glossaries were
not built with it in mind. Three things fall out of it:

1. A TRANSPARENT COGNATE costs a line and teaches nothing. "information",
   "traditional", "professional", "communication", "cultural" -- a Brazilian
   reader decodes all of these on sight. Latinate English is the part of the
   language they already own, and glossing it crowds out the part they do not.

2. A FALSE FRIEND is worth more than almost anything else on the page, and is
   exactly what an automatic "hard-looking word" rule will never select,
   because these words are short and familiar. "eventually" is not
   eventualmente; "actually" is not atualmente; "pretend" is not pretender;
   "parents" is not parentes. Left unmarked, the reader does not misunderstand
   the word -- they misunderstand the sentence, confidently.

3. Germanic everyday English and phrasal verbs are where the real difficulty
   is: "to put up with", "a chore", "to shrink", "wary", "to brace". These are
   opaque to a Portuguese speaker in a way that "constitutional" is not.

This script reports, per text, the cognates that could come out, the false
friends present in the passage that are not glossed, and the glossary size
against the level's target. It changes nothing: what to keep is a judgement,
and a word may earn its place for a reason no rule can see.

Usage:
    python3 scripts/check_vocabulary.py                  # whole library
    python3 scripts/check_vocabulary.py c1/rosa-parks    # one text
    python3 scripts/check_vocabulary.py --missing        # only the false friends
    python3 scripts/check_vocabulary.py --counts         # only the size report
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reading_common as rc

# Glossary size a level can carry before the list stops being a list and starts
# being a page. Guidance, not a rule -- a text with an unusually technical
# subject legitimately runs long.
LEVEL_TARGET = {"A1": (5, 8), "A2": (6, 10), "B1": (8, 12),
                "B2": (10, 15), "C1": (10, 16), "C2": (10, 18)}

# The band above is absolute, and that was wrong on the two ends of the
# library. A 1,075-word C1 text with 17 entries is a SPARSE glossary -- one
# word in sixty -- and it was flagged, while a 120-word A1 text with 13 was
# flagged by the same rule for something entirely different. What a student
# actually carries is the density: how often the reading stops to explain a
# word. So the ceiling grows with the passage, never below the level's own
# figure and never past 2.5x it, because a list of forty is unreadable however
# long the text.
DENSITY_PER_100 = 3.0
MAX_OVER_LEVEL = 2.5


def size_band(level, words):
    """(lo, hi) for a passage of this level and length."""
    lo, hi = LEVEL_TARGET.get(level, (8, 16))
    import math
    allowed = int(math.ceil(words / 100 * DENSITY_PER_100))
    return lo, max(hi, min(allowed, int(round(hi * MAX_OVER_LEVEL))))

# English ending -> the Portuguese ending it maps onto almost mechanically.
# A word built on one of these, on a stem of any length, is readable on sight
# by a Portuguese speaker.
COGNATE_SUFFIXES = [
    ("ation", "ação"), ("ition", "ição"), ("tion", "ção"), ("sion", "são"),
    ("ity", "idade"), ("ment", "mento"), ("ous", "oso"), ("ical", "ico"),
    ("ance", "ância"), ("ence", "ência"), ("ary", "ário"), ("ism", "ismo"),
    ("ist", "ista"), ("ive", "ivo"), ("able", "ável"), ("ible", "ível"),
    ("ize", "izar"), ("ise", "izar"),
]

# Words whose cognate really is transparent and which keep turning up in these
# glossaries. Listed explicitly because a suffix rule alone misses some of them.
TRANSPARENT = {
    "information", "traditional", "tradition", "professional", "profession",
    "communication", "organization", "organisation", "cultural", "culture",
    "national", "international", "natural", "normal", "total", "central",
    "special", "social", "personal", "positive", "negative", "possible",
    "impossible", "necessary", "important", "different", "difficult",
    "famous", "nervous", "serious", "curious", "generous", "religious",
    "public", "private", "automatic", "electric", "economic", "historic",
    "classic", "basic", "specific", "pacific", "atlantic", "romantic",
    "dramatic", "fantastic", "democratic", "politics", "political",
    "president", "presidential", "constitution", "constitutional",
    "federal", "capital", "territory", "colony", "immigrant", "emigrant",
    "population", "revolution", "declaration", "independence", "liberty",
    "monument", "document", "element", "moment", "instrument",
    "activity", "quantity", "quality", "university", "community", "security",
    "society", "majority", "minority", "authority", "capacity", "velocity",
    "to continue", "to permit", "to admit", "to invent", "to prepare",
    "to decide", "to respect", "to resist", "to insist", "to persist",
    "to transport", "to transform", "to describe", "to observe", "to confirm",
    # Verified by hand against Brazilian Portuguese while clearing the first
    # cognate backlog. Each one has an everyday Portuguese cognate carrying the
    # same sense, so the entry taught the reader a word they already had.
    "bombardment", "constellation", "convention", "falsification", "formality",
    "fugitive", "proposition", "refutation", "resolution", "temperament",
    "accusation", "adaptation", "assertion", "expedition", "inevitability",
    "inference", "anaesthetist", "anesthetist", "association", "autonomous",
    "capability", "circulation", "circumlocution", "compensation",
    "comprehension", "compression", "concession", "condescension",
    "conservative", "consolation", "constitutive", "consumption", "contrary",
    "convenience", "correlation", "counter-intuitive", "credibility",
    "cynicism", "decorative", "deliberation", "denotation", "dependence",
    "desegregation", "disillusionment", "dispossession", "disruption",
    "documentation", "emancipation", "equitable", "euphemism", "exclusion",
    "exhortation", "fragility", "glamorous", "impeachment", "improbable",
    "incentive", "indistinguishable", "inseparable", "intelligible",
    "intimidation", "intransitive", "intuition", "legislation", "mechanism",
    "migration", "nationalist", "naturalisation", "naturalization",
    "non-negotiable", "non-renewable", "obscurity", "parliament", "posthumous",
    "precision", "prescription", "providence", "reflexive", "registration",
    "representation", "reunification", "reverence", "reversible",
    "segregation", "selection", "self-description", "separable", "skepticism",
    "scepticism", "spontaneous", "synchronous", "government", "transformative",
    "transmission", "unanimous", "visibility",
    "to authorise", "to authorize", "to capitalize", "to crystallise",
    "to crystallize", "to democratize", "to industrialise", "to industrialize",
    "to metabolise", "to metabolize", "to minimise", "to minimize",
    "to mobilize", "to optimize", "to prioritize", "to recognize",
    "to romanticize", "to scrutinize", "to stabilise", "to stabilize",
    "agreeable",
    # Found by hand while trimming the oversized glossaries: the same class of
    # word, caught by neither the suffix rule nor the list above.
    "various", "inverted", "to exceed", "telemetry", "to circulate",
    "inconsistent", "to diminish", "to qualify", "subtle", "anomaly",
    "to tolerate", "elite", "carbohydrate", "margin", "contingency",
    "tedious", "agenda", "recurring", "to expire", "hypothesis",
    "apparatus", "perceptual", "catastrophe", "epidemic", "asymmetry",
    "bureaucracy",
}

# The suffix rule reads the ENDING, and an English word can wear a Latinate
# ending over a core a Portuguese speaker cannot see through: "unbearable" is
# insuportável, "a constable" is a policial, "a timetable" is a grade horária.
# Worse, three of these are false friends -- "relative" is parente not
# relativo, "tentative" is hesitant not uma tentativa, "formidable" is
# fearsome where formidável is wonderful, "authoritative" is not autoritário --
# so the rule was telling the editor to delete the most valuable entries on the
# page. Checked before the suffix rule; the explicit TRANSPARENT list still wins.
NOT_TRANSPARENT = {
    "allegiance", "amendment", "endowment", "appointment", "authoritative",
    "burglary", "depletion", "discretion", "disfranchisement", "enforcement",
    "expensive", "formidable", "implement", "indirection", "inequality",
    "inheritance", "life-size", "peaceable", "predictable", "prospective",
    "reenactment", "relative", "reliability", "self-invention", "self-reliance",
    "serviceable", "settlement", "surveillance", "survivability", "tentative",
    "timetable", "to enfranchise", "to overpromise", "unassimilable",
    "unbearable", "unemployment", "unfalsifiable", "unglamorous",
    "unresolvable", "untenable", "untranslatable", "enlightenment",
    "constable", "accountable",
}

# The ones that matter most, because nothing about them looks difficult.
# term -> (what a Portuguese speaker expects, what it actually means)
#
# FALSE_FRIENDS holds the words that mislead whatever sense they are used in:
# "eventually" never means eventualmente. CONTEXT_FRIENDS below holds the ones
# that mislead in only one of their senses -- "a plant" is a trap when it means
# a factory and perfectly transparent when it means a growing thing -- so they
# are reported only with --all, where a human decides whether this passage uses
# the difficult sense.
FALSE_FRIENDS = {
    "eventually": ("eventualmente (occasionally)", "in the end, finally"),
    "actually": ("atualmente (currently)", "in fact, really"),
    "actual": ("atual (current)", "real, genuine"),
    "to pretend": ("pretender (to intend)", "to act as if something is true when it is not"),
    "to realize": ("realizar (to carry out)", "to become aware of"),
    "to realise": ("realizar (to carry out)", "to become aware of"),
    "parents": ("parentes (relatives)", "your mother and father"),
    "a library": ("livraria (bookshop)", "a place you borrow books from"),
    "to push": ("puxar (to pull)", "to press forward — the opposite"),
    "a costume": ("costume (habit)", "clothes worn to look like somebody else"),
    "fabric": ("fábrica (factory)", "cloth, material"),
    "to assist": ("assistir (to watch)", "to help"),
    "to attend": ("atender (to answer, to serve)", "to go to, to be present at"),
    "to support": ("suportar (to endure)", "to back, to help, to hold up"),
    "an exit": ("êxito (success)", "the way out"),
    "college": ("colégio (secondary school)", "university, in American English"),
    "a lecture": ("leitura (reading)", "a talk given to students"),
    "a novel": ("novela (soap opera)", "a long work of fiction"),
    "comprehensive": ("compreensivo (understanding)", "complete, covering everything"),
    "sensible": ("sensível (sensitive)", "showing good judgement"),
    "a journal": ("jornal (newspaper)", "an academic periodical, or a diary"),
    "a policy": ("polícia (police)", "a course of action adopted by an institution"),
    "a resume": ("resumo (summary)", "a CV, in American English"),
    "a legend": ("legenda (subtitle, caption)", "a traditional story"),
    "an estate": ("estado (state)", "a large area of land, or property"),
    "an idiom": ("idioma (language)", "a fixed expression whose meaning is not literal"),
    "an injury": ("injúria (insult)", "physical harm"),
    "a mayor": ("maior (bigger)", "the head of a city government"),
    "a physician": ("físico (physicist)", "a doctor"),
    "prejudice": ("prejuízo (financial loss)", "an unfair opinion formed in advance"),
    "a scholar": ("escolar (relating to school)", "a person who studies a subject deeply"),
    "terrific": ("terrível (terrible)", "excellent"),
    "ultimately": ("ultimamente (lately)", "in the end"),
    "vicious": ("vicioso (addicted)", "cruel, violent"),
    "to anticipate": ("antecipar (to bring forward)", "to expect and prepare for"),
    "a compromise": ("compromisso (commitment)", "a settlement where each side gives something up"),
    "convenient": ("conveniente (suitable)", "easy, giving little trouble"),
    "a deception": ("decepção (disappointment)", "a trick, a lie"),
    "to intend": ("entender (to understand)", "to plan to do"),
    "ordinary": ("ordinário (vulgar, low quality)", "normal, usual"),
    "to procure": ("procurar (to look for)", "to obtain"),
    "to quit": ("quitar (to pay off)", "to leave, to stop doing"),
    "to resume": ("resumir (to summarise)", "to begin again after a pause"),
    "a stranger": ("estrangeiro (foreigner)", "somebody you do not know"),
    "a tenant": ("tenente (lieutenant)", "a person renting a property"),
    "to traduce": ("traduzir (to translate)", "to speak badly of"),
}

# Sense-dependent: a trap in one meaning, transparent in another. Reported only
# under --all, because only a reader of the passage can tell which is in play.
CONTEXT_FRIENDS = {
    "large": ("largo (wide)", "big"),
    "a local": ("local (place)", "a person who lives there"),
    "a notice": ("notícia (news item)", "a written announcement"),
    "a record": ("recordar (to remember)", "a written account, or a best performance"),
    "a tax": ("taxa (rate, fee)", "money paid to a government"),
    "an argument": ("argumento (a reason given)", "a disagreement, a quarrel"),
    "to apply": ("aplicar (to apply a thing)", "to make a formal request for a job or place"),
    "to balance": ("balança (scales)", "to keep steady, to weigh against"),
    "a cafeteria": ("cafeteria (coffee shop)", "a self-service canteen"),
    "a camera": ("câmara (chamber, council)", "a device for taking photographs"),
    "to cite": ("citar (to quote) — close, but", "to name a source formally"),
    "to contest": ("contestar (to answer back)", "to dispute, to challenge"),
    "to demand": ("demandar (to sue)", "to ask for forcefully"),
    "an editor": ("editor (publisher)", "a person who edits text"),
    "to educate": ("educar (to bring up well)", "to teach formally"),
    "an engine": ("engenho (ingenuity, mill)", "a motor"),
    "to expect": ("espectar", "to think something will happen"),
    "a fathom": ("", "a unit of depth"),
    "a grade": ("grade (railing, grid)", "a mark for work, or a school year"),
    "a lunch": ("lanche (snack)", "the midday meal"),
    "a motorist": ("motorista (driver, incl. professional)", "a private car driver"),
    "an officer": ("oficial (official)", "a person holding a position of authority"),
    "to pass": ("passar (many senses)", "to succeed in an exam; to hand over"),
    "a plant": ("planta (plant, plan)", "a factory, as well as a growing thing"),
    "to retain": ("reter", "to keep"),
    "a senior": ("senhor (mister)", "an older or higher-ranking person"),
    "to stranger": ("", ""),
}

# Written the way a glossary headword is, so the surface form has to be built
# to search a passage with.
_ARTICLE = re.compile(r"^(to|a|an|the)\s+", re.I)


def _stem(term):
    return _ARTICLE.sub("", term.strip().lower())


def is_transparent_cognate(term):
    """Would a Portuguese speaker read this without being told?"""
    t = term.strip().lower()
    s = _stem(t)
    if t in TRANSPARENT or s in TRANSPARENT:
        return True
    if t in NOT_TRANSPARENT or s in NOT_TRANSPARENT:
        return False
    if " " in s:                      # a phrase is not a single cognate
        return False
    # A known false friend LOOKS like a cognate and is the opposite of one.
    if any(k in FALSE_FRIENDS or k in CONTEXT_FRIENDS
           for k in (t, f"a {s}", f"an {s}", f"to {s}")):
        return False
    for suf, _pt in COGNATE_SUFFIXES:
        if s.endswith(suf) and len(s) - len(suf) >= 5:
            return True
    return False


def false_friends_in(passage, include_context=False):
    """False friends the passage actually uses, as headword -> matched form."""
    text = "\n".join(passage)
    table = dict(FALSE_FRIENDS)
    if include_context:
        table.update(CONTEXT_FRIENDS)
    found = {}
    for head, (looks, means) in table.items():
        if not means:
            continue
        s = _stem(head)
        # the inflections worth searching for; the pattern's own boundaries
        # keep a short stem from matching inside a longer word
        forms = {s, s + "s", s + "es", s + "ed", s + "d", s + "ing"}
        if s.endswith("e"):
            forms.add(s[:-1] + "ing")
        if s.endswith("y"):
            forms |= {s[:-1] + "ies", s[:-1] + "ied"}
        for f in sorted(forms, key=len, reverse=True):
            m = re.search(r"(?<![\w-])(" + re.escape(f) + r")(?![\w-])", text, re.I)
            if m:
                found[head] = m.group(1)
                break
    return found


def review(level, slug, d, include_context=False):
    vocab = d.get("vocabulary") or []
    terms = [v["term"] for v in vocab]
    lowered = {_stem(t) for t in terms}

    cognates = [t for t in terms if is_transparent_cognate(t)]
    ff = false_friends_in(d["passage"], include_context)
    missing_ff = {k: v for k, v in ff.items() if _stem(k) not in lowered}

    words = len(" ".join(d["passage"]).split())
    lo, hi = size_band(d["level"], words)
    size_note = ""
    if len(vocab) > hi:
        # A text whose whole purpose is the word list -- the A1 naming texts,
        # the phrasal-verb lessons -- says so in its own source, with the
        # reason, and is held to the declaration rather than to the band.
        if d.get("lexicalSet"):
            size_note = ""
        else:
            size_note = (f"{len(vocab)} entries, above the {hi} a "
                         f"{d['level']} passage of {words} words carries")
    elif len(vocab) < lo:
        size_note = f"only {len(vocab)} entries, below the {lo}-{hi} the level suggests"
    return cognates, missing_ff, size_note


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    only_missing = "--missing" in sys.argv
    only_counts = "--counts" in sys.argv

    tot_cog = tot_ff = tot_size = 0
    for level, slug, d in rc.all_sources():
        if args and f"{level}/{slug}" not in args:
            continue
        cognates, missing_ff, size_note = review(level, slug, d, "--all" in sys.argv)
        tot_cog += len(cognates)
        tot_ff += len(missing_ff)
        tot_size += 1 if size_note else 0

        if only_counts:
            if size_note:
                print(f"{level}/{slug}: {size_note}")
            continue
        if only_missing:
            if missing_ff:
                print(f"{level}/{slug}:")
                for k, form in missing_ff.items():
                    looks, means = {**FALSE_FRIENDS, **CONTEXT_FRIENDS}[k]
                    print(f"    + {k}  (text has {form!r}) "
                          f"— looks like {looks}; means {means}")
            continue

        if cognates or missing_ff or size_note:
            print(f"\n{level}/{slug} — {d['title']}")
            if size_note:
                print(f"    size: {size_note}")
            if cognates:
                print(f"    transparent for a Portuguese reader, "
                      f"candidates to drop: {', '.join(cognates)}")
            for k, form in missing_ff.items():
                looks, means = {**FALSE_FRIENDS, **CONTEXT_FRIENDS}[k]
                print(f"    false friend not glossed: {k} (text has {form!r}) "
                      f"— looks like {looks}; means {means}")

    print(f"\n{tot_cog} transparent cognate(s) glossed, "
          f"{tot_ff} unglossed false friend(s), "
          f"{tot_size} glossary(ies) outside the level's size guidance.")


if __name__ == "__main__":
    main()
