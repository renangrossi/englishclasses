#!/usr/bin/env python3
"""
Work out which grammar points a reading text actually practices, and write them
to its source JSON as "grammar".

These tags drive the filter on exercises.html, so a wrong tag sends a student to
a text that does not teach what they clicked. The detectors are therefore
deliberately conservative: each one looks for an unambiguous surface pattern and
a tag is only applied when the pattern occurs at least MIN times, so a single
incidental passive does not get a text tagged "Passive voice".

The detectors cannot see everything -- "past simple" in particular is not
reliably separable from past participles by surface pattern, so it is counted
only on irregular past forms that cannot be participles. Under-tagging is the
intended failure: a missing tag costs a student one text in a filter, a wrong
one costs them their trust in the filter.

Usage:
    python3 scripts/tag_grammar.py --report        # show what would be tagged
    python3 scripts/tag_grammar.py --write         # write "grammar" into the JSONs
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reading_common as rc

LABELS = {
    # Student-facing names. These are what a learner sees on the filter, so they
    # use the names a course or a coursebook would use -- not linguistic ones.
    # "Continuous aspect" was the worst offender: it is the term a syntax class
    # uses and it means nothing to somebody looking for "-ing".
    "present-simple": "Present Simple",
    "past-simple": "Past Simple",
    "present-perfect": "Present Perfect",
    "future": "Future (will / going to)",
    "present-continuous": "Present Continuous (-ing)",
    "past-continuous": "Past Continuous (was / were -ing)",
    "passive": "Passive Voice",
    "modals": "Modal Verbs",
    "conditionals": "Conditionals (if)",
    "comparatives": "Comparatives & Superlatives",
    "questions": "Question Forms",
    "phrasal-verbs": "Phrasal Verbs",
    "reported-speech": "Reported Speech",
    "relative-clauses": "Relative Clauses (who / which)",
    "connectors": "Linking Words",
    "imperatives": "Imperatives (instructions)",
}

# Irregular past forms that are not also participles, so finding one is
# unambiguous evidence of a past simple rather than a perfect or a passive.
PAST_ONLY = (r"\b(was|were|went|saw|came|took|gave|made|said|told|got|found|knew|thought|"
             r"felt|left|kept|held|brought|bought|caught|sat|stood|ran|began|drank|ate|"
             r"wrote|spoke|broke|chose|drove|rose|wore|became|put down|sent|built|met|paid)\b")

PARTICIPLE = (r"(?:\w+ed|known|made|taken|given|written|held|built|put|done|seen|found|told|"
              r"shown|kept|left|sent|brought|chosen|driven|grown|drawn|paid|sold|lost|meant|"
              r"spent|caught|begun|understood|carried)")


# ---------------------------------------------------------------------------
# Phrasal verbs
#
# This is the one item on the list that no surface rule can find. "She walked up
# the hill" is not a phrasal verb and "she picked up the pace" is, and nothing in
# the shape of the two sentences tells them apart -- only which verbs take which
# particles idiomatically does. A rule like \w+\s+(up|out|on) tags half the
# library.
#
# So this detector does not guess. It carries a list of phrasal verbs and looks
# for a verb from it beside its own particle, or separated by a pronoun, which is
# the one split that is both common and unambiguous ("turn it off", "picked them
# up"). A longer object ("turn the lights in the back room off") is missed. That
# under-reports, which is the failure this file prefers everywhere else.
PHRASAL = {
    "back": ("up", "down", "off", "out"),
    "blow": ("up", "out"),
    "break": ("down", "up", "out", "into", "off"),
    "bring": ("up", "in", "back", "about", "along", "out"),
    "build": ("up",),
    "call": ("back", "off", "up", "in", "out"),
    "calm": ("down",),
    "carry": ("on", "out"),
    "catch": ("up", "on"),
    "check": ("in", "out", "off"),
    "cheer": ("up",),
    "clean": ("up", "out"),
    "clear": ("up", "out"),
    "close": ("down", "off"),
    "come": ("back", "in", "out", "up", "across", "along", "over", "round"),
    "count": ("on",),
    "cut": ("down", "off", "out", "back"),
    "deal": ("with",),
    "drop": ("off", "out", "in"),
    "eat": ("out", "up"),
    "end": ("up",),
    "fall": ("apart", "behind", "out", "through"),
    "figure": ("out",),
    "fill": ("in", "out", "up"),
    "find": ("out",),
    "get": ("up", "on", "off", "out", "over", "through", "along", "around",
            "back", "into", "away", "by"),
    "give": ("up", "in", "away", "back", "out"),
    "go": ("on", "out", "off", "back", "through", "over", "down", "up",
           "away", "ahead"),
    "grow": ("up",),
    "hand": ("in", "out", "over"),
    "hang": ("on", "up", "out", "around"),
    "heat": ("up",),
    "hold": ("on", "up", "back", "out"),
    "hurry": ("up",),
    "keep": ("on", "up", "away", "out", "off"),
    "kick": ("off",),
    "knock": ("out", "over"),
    "lay": ("off", "out"),
    "leave": ("out", "behind"),
    "let": ("down", "in", "out", "off"),
    "lie": ("down",),
    "line": ("up",),
    "log": ("in", "out", "on", "off"),
    "look": ("up", "after", "into", "out", "around", "back"),
    "make": ("up", "out"),
    "mix": ("up",),
    "move": ("in", "out", "on"),
    "open": ("up",),
    "pass": ("out", "away", "on", "by"),
    "pay": ("back", "off"),
    "pick": ("up", "out"),
    "plug": ("in",),
    "point": ("out",),
    "print": ("out",),
    "pull": ("over", "out", "up", "off", "through"),
    "push": ("on", "through", "back"),
    "put": ("on", "off", "away", "up", "down", "back", "out"),
    "rule": ("out",),
    "run": ("out", "into", "over", "away", "through"),
    "save": ("up",),
    "screw": ("up",),
    "see": ("off", "through"),
    "sell": ("out", "off"),
    "send": ("back", "off", "out"),
    "set": ("up", "off", "out", "aside", "back"),
    "settle": ("down", "in"),
    "show": ("up", "off", "around"),
    "shut": ("down", "up", "off"),
    "sign": ("up", "in", "out", "off"),
    "sit": ("down", "up", "back"),
    "slow": ("down",),
    "sort": ("out",),
    "speak": ("up", "out"),
    "stand": ("up", "out", "by"),
    "start": ("over", "out"),
    "stay": ("up", "in", "out", "away"),
    "stick": ("out", "with", "to"),
    "sum": ("up",),
    "switch": ("on", "off"),
    "take": ("off", "up", "out", "over", "back", "in", "on"),
    "talk": ("over", "into"),
    "tear": ("up", "down"),
    "think": ("over", "through", "up"),
    "throw": ("away", "out", "up"),
    "tidy": ("up",),
    "track": ("down",),
    "try": ("on", "out"),
    "turn": ("on", "off", "up", "down", "out", "into", "around", "over"),
    "use": ("up",),
    "wake": ("up",),
    "walk": ("out",),
    "warm": ("up",),
    "wash": ("up",),
    "watch": ("out",),
    "wear": ("out",),
    "wind": ("up",),
    "wipe": ("out", "down"),
    "work": ("out",),
    "wrap": ("up",),
    "write": ("down", "up", "off"),
}

# Past and participle forms that a -ed rule would get wrong.
PHRASAL_IRREG = {
    "break": ("broke", "broken"), "bring": ("brought",), "build": ("built",),
    "come": ("came",), "cut": (), "deal": ("dealt",), "eat": ("ate", "eaten"),
    "fall": ("fell", "fallen"), "find": ("found",), "get": ("got", "gotten"),
    "give": ("gave", "given"), "go": ("went", "gone"), "grow": ("grew", "grown"),
    "hang": ("hung",), "hold": ("held",), "keep": ("kept",), "lay": ("laid",),
    "leave": ("left",), "let": (), "lie": ("lay", "lain"), "make": ("made",),
    "pay": ("paid",), "put": (), "run": ("ran",), "see": ("saw", "seen"),
    "sell": ("sold",), "send": ("sent",), "set": (), "shut": (),
    "sit": ("sat",), "speak": ("spoke", "spoken"), "stand": ("stood",),
    "stick": ("stuck",), "take": ("took", "taken"), "tear": ("tore", "torn"),
    "think": ("thought",), "throw": ("threw", "thrown"), "wake": ("woke", "woken"),
    "wear": ("wore", "worn"), "wind": ("wound",), "write": ("wrote", "written"),
}

# Objects the verb and its particle may be split around. Pronouns only: a full
# noun phrase makes the match ambiguous again.
_SPLIT = r"(?:it|them|him|her|me|us|you|this|that|these|those|one|everything|something)"


def _verb_forms(v):
    forms = {v, v + "s", v + "ing", v + "ed"}
    if v.endswith("e"):
        forms |= {v[:-1] + "ing", v + "d"}
    if v.endswith("y"):
        forms |= {v[:-1] + "ies", v[:-1] + "ied"}
    if len(v) >= 3 and v[-1] not in "aeiouwxy" and v[-2] in "aeiou" and v[-3] not in "aeiou":
        forms |= {v + v[-1] + "ed", v + v[-1] + "ing"}
    forms |= set(PHRASAL_IRREG.get(v, ()))
    return forms


def _phrasal_pattern():
    alts = []
    for verb, particles in PHRASAL.items():
        forms = "|".join(sorted(_verb_forms(verb), key=len, reverse=True))
        parts = "|".join(particles)
        alts.append(rf"\b(?:{forms})\s+(?:{_SPLIT}\s+)?(?:{parts})\b")
    return "|".join(alts)


PHRASAL_RE = _phrasal_pattern()


PATTERNS = {
    "present-perfect": rf"\b(has|have|had)\s+(?:not\s+|never\s+|already\s+|just\s+)?{PARTICIPLE}\b",
    "passive": rf"\b(is|are|was|were|been|being|be)\s+(?:not\s+|also\s+|often\s+|usually\s+)?{PARTICIPLE}\b",
    "past-simple": PAST_ONLY,
    "future": r"\b(will|won't|shall)\s+\w+|\bgoing to\s+\w+|\babout to\s+\w+",
    # One "continuous" detector could not be labelled honestly: it fired on
    # "she is walking" and "they were walking" alike, so a text tagged only on
    # past forms would have read "Present Continuous". Split per tense instead.
    "present-continuous": r"\b(am|is|are|being)\s+(?:not\s+|just\s+|still\s+|now\s+|always\s+)?\w+ing\b",
    "past-continuous": r"\b(was|were|been)\s+(?:not\s+|just\s+|still\s+|always\s+)?\w+ing\b",
    "modals": r"\b(must|should|shouldn't|might|may|can|cannot|can't|could|couldn't|would|wouldn't|ought to|have to|has to|had to)\b",
    "conditionals": r"\bif\b[^.!?]{0,80}\b(would|will|could|might|were)\b|\bunless\b",
    "comparatives": r"\b\w+er than\b|\bmore \w+ than\b|\bless \w+ than\b|\bthe (most|least|biggest|best|worst|largest) \w+",
    "questions": r"\?",
    "reported-speech": r"\b(said|told|asked|explained|replied|admitted|argued|claimed)\s+(that\b|him\b|her\b|them\b|me\b|us\b)",
    "relative-clauses": r"\b\w+,?\s+(which|who|whose|whom)\b",
    "connectors": r"\b(however|therefore|moreover|nevertheless|furthermore|whereas|although|though|despite|in spite of|on the other hand|as a result|consequently|even so)\b",
    "imperatives": r"(?:^|[.!?“]\s*)(Take|Put|Give|Look|Listen|Drink|Eat|Go|Come|Stay|Ask|Tell|Try|Keep|Make|Use|Read|Write|Check|Call|Open|Close|Don't|Do not)\s+\w+",
    "present-simple": r"\b(I|you|we|they)\s+(?!am|are|was|were|have been|will)\w+s?\b|\b(he|she|it)\s+\w+s\b",
    "phrasal-verbs": PHRASAL_RE,
}

# Hits needed before a tag is claimed, calibrated against a 500-word text and
# scaled by actual length -- otherwise a 130-word A1 passage written entirely in
# the present simple fails a threshold set for a 900-word essay, and comes out
# with no tags at all and so invisible to the filter. Density is what matters.
REFERENCE_WORDS = 500
MIN = {
    "present-simple": 12, "questions": 3, "modals": 5, "connectors": 3,
    "relative-clauses": 4, "comparatives": 2,
    "present-continuous": 3, "past-continuous": 3,
    "passive": 3, "present-perfect": 3, "past-simple": 6, "future": 3,
    "conditionals": 2, "reported-speech": 2, "imperatives": 3,
    # A narrative uses a few in passing; a text that is ABOUT them is thick with
    # them. The threshold is set to separate the two rather than to find any.
    "phrasal-verbs": 8,
}

# Density decides most tags, and the floor is scaled down for a short passage so
# that a 130-word A1 story written entirely in the present simple is not missed.
# That scaling is wrong for phrasal verbs: three of them in a 150-word story is a
# high density and still not a text that practises phrasal verbs. So this tag
# also has to clear an absolute count, which keeps the filter honest -- clicking
# it should return texts built on them, not stories containing "wake up".
ABS_MIN = {"phrasal-verbs": 6}


def tags_for(passage):
    text = " ".join(passage)
    words = max(1, len(text.split()))
    found = []
    for key, pat in PATTERNS.items():
        n = len(re.findall(pat, text, re.IGNORECASE if key != "imperatives" else 0))
        floor = max(2, round(MIN.get(key, 3) * words / REFERENCE_WORDS))
        if n >= floor and n >= ABS_MIN.get(key, 0):
            found.append((key, n))
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--level")
    a = ap.parse_args()

    per_tag = Counter()
    rows = []
    for level, slug, d in rc.all_sources():
        if a.level and level != a.level:
            continue
        found = tags_for(d["passage"])
        keys = [k for k, _ in found]
        for k in keys:
            per_tag[k] += 1
        rows.append((level, slug, found))
        if a.write:
            p = rc.src_path(level, slug)
            j = json.loads(p.read_text(encoding="utf-8"))
            out = {}
            for k, v in j.items():
                if k == "passage":
                    out["grammar"] = keys
                if k != "grammar":
                    out[k] = v
            p.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if a.report:
        for level, slug, found in rows:
            print(f"{level}/{slug}")
            print("    " + ", ".join(f"{LABELS[k]} ({n})" for k, n in found))
    print("\ntexts per tag:")
    for k, n in per_tag.most_common():
        print(f"   {LABELS[k]:20} {n}")
    print(f"\n{len(rows)} text(s); {sum(len(f) for _,_,f in rows)/max(1,len(rows)):.1f} tags each on average")
    return 0


if __name__ == "__main__":
    sys.exit(main())
