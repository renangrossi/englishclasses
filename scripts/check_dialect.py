#!/usr/bin/env python3
"""
Keep the reading library in one variety of English.

The site teaches American English: the voices are en-US, the history collection
is American, and the hub calls its subjects by American names. The texts,
however, were written over a long period and drifted -- "organised" in one text
and "organized" in the next, "neighbour" in one A1 story and "neighbor" in
another. That is the kind of inconsistency that makes a library read as a pile
of separately generated pages.

This normalises SPELLING only, which is mechanical and safe. It deliberately
does not touch word choice -- rubbish/trash, flat/apartment, lift/elevator --
because those carry meaning, can be correct in a text set in Britain, and are
worth teaching as variants rather than erasing. Those are reported instead.

Rewriting a passage changes what the narrator says, so anything this touches
needs scripts/generate_reading_audio.py run over it afterwards. The script
prints the list.

Usage:
    python3 scripts/check_dialect.py             # report
    python3 scripts/check_dialect.py --fix       # rewrite the JSON sources
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reading_common as rc

# British -> American. Applied case-insensitively, preserving the case of the
# first letter. Ordered longest-first where one is a prefix of another.
SPELLING = [
    (r"\borganis(e|ed|es|ing|ation|ational|er|ers)\b", "organiz"),
    (r"\brecognis(e|ed|es|ing|able)\b", "recogniz"),
    (r"\brealis(e|ed|es|ing|ation)\b", "realiz"),
    (r"\bapologis(e|ed|es|ing)\b", "apologiz"),
    (r"\bcriticis(e|ed|es|ing|m)\b", "criticiz"),
    (r"\bemphasis(e|ed|es|ing)\b", "emphasiz"),
    (r"\bmemoris(e|ed|es|ing)\b", "memoriz"),
    (r"\bspecialis(e|ed|es|ing|ation)\b", "specializ"),
    (r"\banalys(e|ed|es|ing)\b", "analyz"),
    (r"\bcolour(s|ed|ing|ful|less)?\b", "color"),
    (r"\bfavour(s|ed|ing|able|ite|ites)?\b", "favor"),
    (r"\bbehaviour(s|al)?\b", "behavior"),
    (r"\bneighbour(s|ing|hood|hoods|ly)?\b", "neighbor"),
    (r"\blabour(s|ed|ing|er|ers)?\b", "labor"),
    (r"\bhonour(s|ed|ing|able)?\b", "honor"),
    (r"\brumour(s)?\b", "rumor"),
    (r"\bharbour(s)?\b", "harbor"),
    (r"\bcentre(s|d)?\b", "center"),
    (r"\btheatre(s)?\b", "theater"),
    (r"\bmetre(s)?\b", "meter"),
    (r"\bkilometre(s)?\b", "kilometer"),
    (r"\bcentimetre(s)?\b", "centimeter"),
    (r"\bmillimetre(s)?\b", "millimeter"),
    (r"\bdefence(s)?\b", "defense"),
    (r"\boffence(s)?\b", "offense"),
    (r"\bpractis(e|ed|es|ing)\b", "practic"),
    (r"\btravell(ed|ing|er|ers)\b", "travel"),
    (r"\bcancell(ed|ing)\b", "cancel"),
    (r"\bmodell(ed|ing)\b", "model"),
    (r"\bprogramme(s)?\b", "program"),
    (r"\bgrey(s|ish)?\b", "gray"),
    (r"\bsceptic(s|al|ism)?\b", "skeptic"),
    (r"\bjudgement(s)?\b", "judgment"),
    (r"\bfulfil\b", "fulfill"),
    (r"\benrol\b", "enroll"),
    (r"\bmarvellous\b", "marvelous"),
    (r"\bstorey(s)?\b", "story"),
    (r"\bploughed\b", "plowed"),
    (r"\bplough(s|ing)?\b", "plow"),
    (r"\bmoustache(s)?\b", "mustache"),
    (r"\bpyjamas\b", "pajamas"),
    (r"\bnappy\b", "diaper"),
    (r"\bnappies\b", "diapers"),
    (r"\baluminium\b", "aluminum"),
    (r"\bwhilst\b", "while"),
]

# Spellings that are part of a name or a term of art and must survive.
# "hawker centre" is the Singaporean institution, spelled that way officially.
PROTECTED = [
    r"hawker centres?",
    r"Labour Party",
    r"Centre for [A-Z]",
    r"Theatre Royal",
    r"Ford'?s Theatre",
]

# Word choice, not spelling: reported, never rewritten.
VARIANT_WORDS = {
    "rubbish": "trash / garbage", "lorry": "truck", "lift": "elevator",
    "flat": "apartment", "petrol": "gas", "pavement": "sidewalk",
    "queue": "line", "biscuit": "cookie", "jumper": "sweater",
    "trousers": "pants", "torch": "flashlight", "aeroplane": "airplane",
    "maths": "math", "chemist": "pharmacy / drugstore", "tap": "faucet",
    "cutlery": "silverware", "autumn": "fall", "holiday": "vacation",
    "postcode": "zip code", "timetable": "schedule", "cinema": "movie theater",
    "mum": "mom",
}

# Every string on a text that a student reads.
FIELDS = ["title", "subtitle", "description"]


def _protect(text):
    """Blank out protected spans so a rule cannot reach inside them."""
    spans = []
    for pat in PROTECTED:
        for m in re.finditer(pat, text, re.IGNORECASE):
            spans.append((m.start(), m.end()))
    if not spans:
        return text, []
    out, keep, last = [], [], 0
    for i, (s, e) in enumerate(sorted(spans)):
        if s < last:
            continue
        out.append(text[last:s])
        out.append(f"\x00{len(keep)}\x00")
        keep.append(text[s:e])
        last = e
    out.append(text[last:])
    return "".join(out), keep


def _restore(text, keep):
    for i, s in enumerate(keep):
        text = text.replace(f"\x00{i}\x00", s)
    return text


def convert(text):
    """British -> American spelling, preserving the case of the first letter."""
    masked, keep = _protect(text)

    def repl(stem):
        def f(m):
            whole = m.group(0)
            tail = m.group(1) or "" if m.lastindex else ""
            new = stem + tail
            if whole[0].isupper():
                new = new[0].upper() + new[1:]
            return new
        return f

    for pat, stem in SPELLING:
        masked = re.sub(pat, repl(stem), masked, flags=re.IGNORECASE)
    return _restore(masked, keep)


def walk(d):
    """Every reader-facing string on a text, as (path, value) pairs."""
    for f in FIELDS:
        if d.get(f):
            yield (f, d[f])
    for i, p in enumerate(d.get("passage") or []):
        yield (f"passage[{i}]", p)
    for i, v in enumerate(d.get("vocabulary") or []):
        yield (f"vocabulary[{i}].term", v["term"])
        yield (f"vocabulary[{i}].definition", v["definition"])
    for i, img in enumerate(d.get("images") or []):
        for k in ("alt", "caption"):
            if img.get(k):
                yield (f"images[{i}].{k}", img[k])
    for i, p in enumerate(d.get("discussion") or []):
        yield (f"discussion[{i}]", p)


def apply_to(d):
    """Rewrite in place; returns the number of strings changed."""
    n = 0
    for f in FIELDS:
        if d.get(f):
            new = convert(d[f])
            if new != d[f]:
                d[f] = new
                n += 1
    for key in ("passage", "discussion"):
        if d.get(key):
            new = [convert(x) for x in d[key]]
            n += sum(1 for a, b in zip(d[key], new) if a != b)
            d[key] = new
    for v in (d.get("vocabulary") or []):
        for k in ("term", "definition"):
            new = convert(v[k])
            if new != v[k]:
                v[k] = new
                n += 1
    for img in (d.get("images") or []):
        for k in ("alt", "caption"):
            if img.get(k):
                new = convert(img[k])
                if new != img[k]:
                    img[k] = new
                    n += 1
    return n


def main():
    fix = "--fix" in sys.argv
    touched, variants, total = [], {}, 0
    for level, slug, d in rc.all_sources():
        hits = []
        for path, value in walk(d):
            if convert(value) != value:
                hits.append(path)
        for w, us in VARIANT_WORDS.items():
            blob = " ".join(d.get("passage") or [])
            if re.search(r"(?<![\w-])" + w + r"(e?s)?(?![\w-])", blob, re.I):
                variants.setdefault(w, []).append(f"{level}/{slug}")
        if not hits:
            continue
        total += len(hits)
        touched.append((level, slug, hits))
        if fix:
            p = rc.src_path(level, slug)
            data = json.loads(p.read_text(encoding="utf-8"))
            apply_to(data)
            p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                         encoding="utf-8")

    verb = "normalized" if fix else "would normalize"
    print(f"{verb} {total} string(s) across {len(touched)} text(s).")
    if not fix:
        for level, slug, hits in touched:
            print(f"  {level}/{slug}: {len(hits)} string(s)")
    if variants:
        print("\nWord choice, not spelling -- left alone, worth a decision:")
        for w, where in sorted(variants.items(), key=lambda x: -len(x[1])):
            print(f"  {w} ({VARIANT_WORDS[w]}): {len(where)} text(s) "
                  f"— {', '.join(where[:4])}{' …' if len(where) > 4 else ''}")
    if fix and touched:
        print("\nThese texts now need their audio regenerated:")
        print("  python3 scripts/generate_reading_audio.py "
              + " ".join(f"{l}/{s}" for l, s, _ in touched[:6])
              + (" …" if len(touched) > 6 else "")
              + " --tts /tmp/rl-venv/bin/edge-tts")


if __name__ == "__main__":
    main()
