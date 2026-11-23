#!/usr/bin/env python3
"""
Keep the grammar lessons in American spelling, as check_dialect.py does for
the reading library.

The lessons were written over a long period and mixed the two: "cancelled"
beside "canceled", "colour" beside "color". This rewrites spelling only, in
the text a student reads -- text nodes and the exercise JSON of levels/ and
the root pages, the strings of curriculum/*.json, and every prose string of
content/readings/*.json (check_dialect.py covers a reading's passage and
glossary but not its questions). Markup, attributes, scripts and styles are
left alone. Reading pages are built from their JSON, so run
scripts/build_reading_page.py afterwards.

Anything that talks about the difference ("British English: colour") is
skipped and reported, because there the British spelling is the content.

Usage:
    python3 scripts/normalize_lesson_spelling.py          # report
    python3 scripts/normalize_lesson_spelling.py --fix    # rewrite
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_dialect as cd

ROOT = Path(__file__).resolve().parent.parent

# Spellings the reading library never needed. (pattern, American stem); the
# captured tail is kept, as in check_dialect.SPELLING.
EXTRA = [
    (r"\b(author|character|minim|maxim|optim|stabil|social|summar|final|general|"
     r"industrial|commercial|crystall|synchron|hypothes|agon|prioritis|modern|"
     r"categor|symbol|util|civil|national|natural|normal|standard|familiar|"
     r"custom|special|recogn|organ|real|apolog|critic|emphas|memor)"
     r"is(e|ed|es|ing|ation|ations|er|ers|ably)\b", r"\1iz"),
    (r"\b(dis|re|un)organis(ed|ation)\b", r"\1organiz"),
    (r"\bunrecognis(ed)\b", "unrecogniz"),
    (r"\bunauthoris(ed)\b", "unauthoriz"),
    (r"\b(flavo|humo|armo|vapo|misdemeano)ur(s|ed|ing|less)?\b", r"\1r"),
    (r"\b(fib|lit)re(s)?\b", r"\1er"),
    (r"\btyre(s)?\b", "tire"),
    (r"\b(label|level|signal|fuel|quarrel|initial|chisel|snorkel|counsel|marvel)l(ed|ing|er|ers)\b", r"\1"),
    (r"\bjewellery\b", "jewelry"),
    (r"\bageing\b", "aging"),
    (r"\bskilful\b", "skillful"),
    (r"\bdistil\b", "distill"),
    (r"\bmould(s|y)?\b", "mold"),
    (r"\bsulphur\b", "sulfur"),
    (r"\bhaemorrhage(s)?\b", "hemorrhage"),
    (r"\banaesthetist(s)?\b", "anesthetist"),
    (r"\bchilli\b", "chili"),
    (r"\bspecialit(y|ies)\b", "specialt"),
    (r"\backnowledgement(s)?\b", "acknowledgment"),
]
# Word choice rather than spelling: not this script's business.
NOT_SPELLING = {"nappy", "nappies", "whilst", "pyjamas", "storey"}

ABOUT_DIALECT = re.compile(r"\b(British|American) (English|spelling)|\b(BrE|AmE)\b|\bin (the UK|Britain)\b")


def convert(text):
    text = cd.convert(text)
    for pat, stem in EXTRA:
        def f(m, stem=stem):
            new = m.expand(stem) + (m.group(m.lastindex) or "" if m.lastindex and m.lastindex > stem.count("\\") else "")
            return new[0].upper() + new[1:] if m.group(0)[0].isupper() else new
        text = re.sub(pat, f, text, flags=re.IGNORECASE)
    return text


def rewrite_html(s, report):
    """Rewrite text between tags; skip <script> (except exercise JSON) and <style>."""
    out, pos = [], 0
    skip_until = None
    for m in re.finditer(r"<[^>]+>", s):
        chunk = s[pos:m.start()]
        tag = m.group(0)
        if skip_until is None:
            out.append(fix_chunk(chunk, report))
        else:
            out.append(chunk)
        out.append(tag)
        pos = m.end()
        low = tag.lower()
        if skip_until and low.startswith(skip_until):
            skip_until = None
        elif low.startswith("<style") or (low.startswith("<script") and "application/json" not in low):
            skip_until = "</style" if low.startswith("<style") else "</script"
    out.append(s[pos:])
    return "".join(out)


def fix_chunk(chunk, report):
    if not chunk.strip():
        return chunk
    # Exercise JSON: decide item by item, so one item about dialect does not
    # exempt the whole block.
    parts = re.split(r'(\{"id": )', chunk) if chunk.lstrip().startswith("{") else [chunk]
    res = []
    for part in parts:
        new = convert(part)
        if new != part and ABOUT_DIALECT.search(part):
            report["skipped"].append(re.sub(r"\s+", " ", part)[:160])
            new = part
        elif new != part:
            report["changed"] += 1
        res.append(new)
    return "".join(res)


# Keys of a reading's source JSON that are not prose.
NOT_PROSE = {"id", "type", "slug", "level", "src", "source", "file", "url", "href",
             "license", "credit", "voice", "topic", "status", "audio"}


def rewrite_reading(node, report, key=None):
    """Every prose string of a content/readings/*.json, exercises included --
    check_dialect.py covers the passage and glossary but not the questions."""
    if isinstance(node, dict):
        return {k: (v if k in NOT_PROSE else rewrite_reading(v, report, k)) for k, v in node.items()}
    if isinstance(node, list):
        return [rewrite_reading(v, report, key) for v in node]
    if isinstance(node, str):
        new = convert(node)
        if new != node and ABOUT_DIALECT.search(node):
            report["skipped"].append(node[:160])
            return node
        if new != node:
            report["changed"] += 1
            if key == "passage":
                report["passages"] += 1
        return new
    return node


def main():
    fix = "--fix" in sys.argv
    cd.SPELLING[:] = [(p, st) for p, st in cd.SPELLING
                      if not any(w in p for w in NOT_SPELLING)]
    report = {"changed": 0, "skipped": [], "passages": 0}
    # cefr/*.html are the grammar booklets: their text was never normalized.
    files = sorted(ROOT.glob("levels/**/*.html")) + sorted(ROOT.glob("*.html")) \
        + sorted(ROOT.glob("cefr/*.html")) \
        + sorted(ROOT.glob("curriculum/**/*.json"))
    touched = 0
    for f in files:
        s = f.read_text(encoding="utf-8")
        if f.suffix == ".json":
            new = "\n".join(fix_chunk(line, report) for line in s.split("\n"))
        else:
            new = rewrite_html(s, report)
        if new != s:
            touched += 1
            if fix:
                f.write_text(new, encoding="utf-8")
    import json
    renarrate = []
    for f in sorted(ROOT.glob("content/readings/*/*.json")):
        raw = f.read_text(encoding="utf-8")
        before = report["passages"]
        new = json.dumps(rewrite_reading(json.loads(raw), report), ensure_ascii=False, indent=2)
        new += "\n" if raw.endswith("\n") else ""
        if new != raw:
            touched += 1
            if report["passages"] > before:
                renarrate.append(f"{f.parent.name}/{f.stem}")
            if fix:
                f.write_text(new, encoding="utf-8")
    verb = "rewrote" if fix else "would rewrite"
    print(f"{verb} {report['changed']} passage(s) in {touched} file(s).")
    if renarrate:
        print(f"\n{len(renarrate)} passage(s) changed; the narration manifest will call them stale "
              f"until scripts/generate_reading_audio.py is run, then scripts/build_reading_page.py:")
        print("  ", " ".join(renarrate))
    if report["skipped"]:
        print(f"\nLeft alone -- {len(report['skipped'])} passage(s) that discuss the difference:")
        for x in report["skipped"]:
            print("  ", x)


if __name__ == "__main__":
    main()
