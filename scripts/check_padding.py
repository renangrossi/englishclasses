#!/usr/bin/env python3
"""
Look for padding in the reading library.

Padding is not the same as length. A long text that keeps saying new things is
fine; a short one that restates its own opening is not. This reports the four
signals that actually catch it in this library, and prints the evidence rather
than a score, because every one of them has honest exceptions:

  FILLER     stock phrases that announce content without carrying any
  REPEAT     several sentences in a row opening the same way
  DIVERSITY  unusually repetitive vocabulary for its length
  THIN       a passage shorter than its own level's floor

Everything here is evidence for a human to judge, not a verdict. Every signal
has honest exceptions, and in the first run on this library most flags were
exceptions rather than faults:

  - "at the end of the day" was literal twice (dusk over the pampas; cleaning
    up after a shift) and idiomatic filler zero times.
  - Three sentences opening "Anything called..." in b1/beers is deliberate
    parallelism carrying a rule of thumb, and reads better than the varied
    version would.
  - A low distinct-word ratio usually means dialogue or narrative, which repeat
    names and pronouns legitimately.

So read the text before changing it. DIVERSITY in particular calibrates itself
against this library rather than against a number picked in advance -- a text
is flagged only if its ratio falls in the bottom tenth of comparable lengths
here, which keeps it meaningful as the library grows.

Usage:  python3 scripts/check_padding.py [--level b1] [--all]
"""
import argparse
import re
import sys
from collections import Counter

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import reading_common as rc

# Phrases that, in this library's register, are nearly always filler.
FILLER = [
    "it is important to note", "it's important to note", "it is worth noting",
    "when it comes to", "in today's world", "in the modern world",
    "at the end of the day", "the fact of the matter is", "needless to say",
    "it goes without saying", "last but not least", "first and foremost",
    "in conclusion", "to sum up", "as we have seen", "a wide variety of",
    "a wide range of", "plays an important role", "plays a key role",
    "there are many different", "in order to be able to", "due to the fact that",
]

# Below this, a text is thin for its level rather than merely short.
FLOOR = {"pre-a1": 60, "a1": 80, "a2": 140, "b1": 280, "b2": 340, "c1": 300, "c2": 450}


def sentences(passage):
    out = []
    for p in passage:
        out += [s.strip() for s in re.split(r"(?<=[.!?”])\s+", p) if s.strip()]
    return out


BANDS = [(120, 300), (300, 500), (500, 700), (700, 10**6)]

# A dialogue names its speakers on every line, and the first run of this flagged
# four texts for it: "receptionist" fifteen times, "clerk" fourteen, "detective"
# fourteen, "manager" ten. That is the format, not the prose, so the label is
# stripped before the ratio is taken -- same convention the page builder uses to
# recognise a speaker line.
SPEAKER_RE = re.compile(r"^[A-Z][\w .'\-]{0,24}:\s")


def narration(passage):
    """The passage with speaker labels removed, which is what DIVERSITY reads."""
    return [SPEAKER_RE.sub("", p) for p in passage]


def band_of(n):
    for lo, hi in BANDS:
        if lo <= n < hi:
            return (lo, hi)
    return None


def diversity_floors(all_rows):
    """Bottom-decile distinct-word ratio per length band, from the library
    itself. Bands with too few texts to have a meaningful tenth are skipped."""
    floors = {}
    for band in BANDS:
        rs = sorted(r for b, r in all_rows if b == band)
        if len(rs) >= 10:
            floors[band] = rs[len(rs) // 10]
    return floors


def analyse(level, slug, d, floors=None):
    passage = d["passage"]
    text = " ".join(passage)
    low = text.lower()
    words = re.findall(r"[a-z']+", low)
    n = len(words)
    spoken = re.findall(r"[a-z']+", " ".join(narration(passage)).lower())
    issues = []
    # A text may record, in its own source, a signal already read and judged to
    # be a feature. The reason is required; it is printed with the text so the
    # exception stays arguable rather than becoming invisible.
    waived = d.get("paddingNote") or {}

    for f in FILLER:
        if f in low and "FILLER" not in waived:
            issues.append(("FILLER", f'"{f}"'))

    # Three or more consecutive sentences opening on the same two words.
    sents = sentences(passage)
    opens = [" ".join(re.findall(r"[A-Za-z']+", s)[:2]).lower() for s in sents]
    run, start = 1, 0
    for i in range(1, len(opens) + 1):
        if i < len(opens) and opens[i] and opens[i] == opens[i - 1]:
            run += 1
            continue
        if run >= 3 and opens[start] and "REPEAT" not in waived:
            issues.append(("REPEAT", f'{run} sentences in a row open "{opens[start]}…"'))
        run, start = 1, i

    # Distinct-word ratio against the bottom decile of comparable texts here.
    band = band_of(len(spoken))
    ratio = len(set(spoken)) / len(spoken)
    if (band and floors and band in floors and ratio <= floors[band]
            and "DIVERSITY" not in waived):
        issues.append(("DIVERSITY", f"{ratio:.2f} distinct-word ratio — bottom tenth "
                                    f"for {band[0]}+ word texts here (floor {floors[band]:.2f}). Read it."))

    floor = FLOOR.get(level, 200)
    if n < floor:
        issues.append(("THIN", f"{n} words, below the {floor}-word floor for {level.upper()}"))
    return n, issues


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--level")
    ap.add_argument("--all", action="store_true", help="list clean texts too")
    a = ap.parse_args()

    # First pass: the library's own diversity distribution.
    measured = []
    for _, _, d in rc.all_sources():
        w = re.findall(r"[a-z']+", " ".join(narration(d["passage"])).lower())
        b = band_of(len(w))
        if b:
            measured.append((b, len(set(w)) / len(w)))
    floors = diversity_floors(measured)

    flagged = 0
    counts = Counter()
    rows = []
    for level, slug, d in rc.all_sources():
        if a.level and level != a.level:
            continue
        n, issues = analyse(level, slug, d, floors)
        if issues:
            flagged += 1
            for kind, _ in issues:
                counts[kind] += 1
        if issues or a.all:
            rows.append((level, slug, n, issues))

    rows.sort(key=lambda r: (r[0], r[1]))
    for level, slug, n, issues in rows:
        head = f"{level}/{slug}  ({n} words)"
        print(head if issues else f"{head}  clean")
        for kind, detail in issues:
            print(f"    {kind:10} {detail}")
    total = sum(1 for _ in rc.all_sources()) if not a.level else len(
        [1 for lv, _, _ in rc.all_sources() if lv == a.level])

    # DIVERSITY is a RANKING, not a defect: it flags the bottom tenth of each
    # length band, so it can never reach zero and clearing one text simply
    # promotes the next. Counting it beside FILLER and REPEAT made the summary
    # read as "20 faults" when the faults were two. They are tallied apart:
    # the first number is work, the second is a reading list.
    defects = sum(v for k, v in counts.items() if k != "DIVERSITY")
    print(f"\n{defects} defect(s) across {total} text(s)" +
          (f" — {dict((k, v) for k, v in counts.items() if k != 'DIVERSITY')}"
           if defects else ""))
    print(f"{counts['DIVERSITY']} text(s) in the bottom tenth for vocabulary "
          f"variety — by construction, not a fault; read them when you are "
          f"looking for something to improve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
