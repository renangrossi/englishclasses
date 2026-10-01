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
    "present-simple": "Present simple",
    "past-simple": "Past simple",
    "present-perfect": "Present perfect",
    "future": "Future forms",
    "continuous": "Continuous aspect",
    "passive": "Passive voice",
    "modals": "Modal verbs",
    "conditionals": "Conditionals",
    "comparatives": "Comparatives",
    "questions": "Questions",
    "phrasal-verbs": "Phrasal verbs",
    "reported-speech": "Reported speech",
    "relative-clauses": "Relative clauses",
    "connectors": "Connectors",
    "imperatives": "Imperatives",
}

# Irregular past forms that are not also participles, so finding one is
# unambiguous evidence of a past simple rather than a perfect or a passive.
PAST_ONLY = (r"\b(was|were|went|saw|came|took|gave|made|said|told|got|found|knew|thought|"
             r"felt|left|kept|held|brought|bought|caught|sat|stood|ran|began|drank|ate|"
             r"wrote|spoke|broke|chose|drove|rose|wore|became|put down|sent|built|met|paid)\b")

PARTICIPLE = (r"(?:\w+ed|known|made|taken|given|written|held|built|put|done|seen|found|told|"
              r"shown|kept|left|sent|brought|chosen|driven|grown|drawn|paid|sold|lost|meant|"
              r"spent|caught|begun|understood|carried)")

PATTERNS = {
    "present-perfect": rf"\b(has|have|had)\s+(?:not\s+|never\s+|already\s+|just\s+)?{PARTICIPLE}\b",
    "passive": rf"\b(is|are|was|were|been|being|be)\s+(?:not\s+|also\s+|often\s+|usually\s+)?{PARTICIPLE}\b",
    "past-simple": PAST_ONLY,
    "future": r"\b(will|won't|shall)\s+\w+|\bgoing to\s+\w+|\babout to\s+\w+",
    "continuous": r"\b(am|is|are|was|were|been|being)\s+\w+ing\b",
    "modals": r"\b(must|should|shouldn't|might|may|can|cannot|can't|could|couldn't|would|wouldn't|ought to|have to|has to|had to)\b",
    "conditionals": r"\bif\b[^.!?]{0,80}\b(would|will|could|might|were)\b|\bunless\b",
    "comparatives": r"\b\w+er than\b|\bmore \w+ than\b|\bless \w+ than\b|\bthe (most|least|biggest|best|worst|largest) \w+",
    "questions": r"\?",
    "reported-speech": r"\b(said|told|asked|explained|replied|admitted|argued|claimed)\s+(that\b|him\b|her\b|them\b|me\b|us\b)",
    "relative-clauses": r"\b\w+,?\s+(which|who|whose|whom)\b",
    "connectors": r"\b(however|therefore|moreover|nevertheless|furthermore|whereas|although|though|despite|in spite of|on the other hand|as a result|consequently|even so)\b",
    "imperatives": r"(?:^|[.!?“]\s*)(Take|Put|Give|Look|Listen|Drink|Eat|Go|Come|Stay|Ask|Tell|Try|Keep|Make|Use|Read|Write|Check|Call|Open|Close|Don't|Do not)\s+\w+",
    "present-simple": r"\b(I|you|we|they)\s+(?!am|are|was|were|have been|will)\w+s?\b|\b(he|she|it)\s+\w+s\b",
}

# Hits needed before a tag is claimed, calibrated against a 500-word text and
# scaled by actual length -- otherwise a 130-word A1 passage written entirely in
# the present simple fails a threshold set for a 900-word essay, and comes out
# with no tags at all and so invisible to the filter. Density is what matters.
REFERENCE_WORDS = 500
MIN = {
    "present-simple": 12, "questions": 3, "modals": 5, "connectors": 3,
    "relative-clauses": 4, "comparatives": 2, "continuous": 3,
    "passive": 3, "present-perfect": 3, "past-simple": 6, "future": 3,
    "conditionals": 2, "reported-speech": 2, "imperatives": 3,
}


def tags_for(passage):
    text = " ".join(passage)
    words = max(1, len(text.split()))
    found = []
    for key, pat in PATTERNS.items():
        n = len(re.findall(pat, text, re.IGNORECASE if key != "imperatives" else 0))
        floor = max(2, round(MIN.get(key, 3) * words / REFERENCE_WORDS))
        if n >= floor:
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
