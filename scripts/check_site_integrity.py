#!/usr/bin/env python3
"""
Static consistency checks for the whole site. Read-only -- it never edits
anything, so it is safe to run at any time.

Checks
------
1. internal links      every href/src resolves to a file that exists, and
                       every #fragment resolves to an id on the target page
2. search index        every entry's url (and #fragment) resolves
3. booklet sheets      every `<section id="sheet-N">` has its own search
                       entry pointing at `...#sheet-N` -- the check that
                       would have caught the bug where searching a sheet
                       title ("Paired Expressions") landed on the top of
                       the booklet instead of the sheet, because sheet
                       titles only existed inside the parent booklet
                       entry's "keywords"
4. curriculum <-> site every curriculum/{level}/*.json has a built page,
                       is listed in curriculum/index.json, and appears in
                       worker/course-catalog.json
5. exercise data       every `<script class="exercise-data">` block (and
                       its curriculum source) matches the contract
                       assets/js/exercises.js actually implements, and
                       item ids are unique per lesson. Also that a block
                       renders as ONE kind of question and that every
                       question can actually be answered -- the checks
                       that would have caught the bug where "Fill in the
                       Blanks (Part 1 of 3)" on the A2 quantifiers
                       lesson showed four dropdowns and then six text
                       boxes, because the six items added later were
                       never given `options`; and the one where the B2
                       articles lesson asked students to "choose the, a,
                       or (no article)" in a free-text box that only
                       accepted the literal string "(no article)".
                       In a self-check block (writing, or typing with no
                       answer key) two items count as the same question
                       when their prompts read the same, ignoring curly
                       vs straight quotes -- the check that would have
                       caught the 97 prompts that repeated word for word
                       inside their own block, 14 of them hidden behind
                       nothing but a change of quote character. A typing
                       block must also be all graded or all self-check --
                       the check that would have caught prea1-abc-type
                       scoring "6 of 6 correct (100%)" over a block of ten
                       questions, four of which ask the student to spell
                       their own name
6. built-page assets   every css/js reference carries the ?v= stamp
                       stamp_asset_versions.py adds, and each booklet
                       page carries the script set the booklet builder
                       is meant to give it -- the check that would have
                       caught the bug where that builder's rewrites,
                       which all match an unstamped <script> tag,
                       quietly stopped matching once the pages were
                       stamped, and dropped booklet.js and both
                       irregular-verbs scripts from all seven pages
                       while leaving dictionary.js behind

Usage:
    python3 scripts/check_site_integrity.py            # report, exit 1 on error
    python3 scripts/check_site_integrity.py --warnings # also list warnings
    python3 scripts/check_site_integrity.py --selftest # check the checks fire
"""
import glob
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_ORIGIN = "https://renangrossi.github.io/englishclasses/"
SKIP_DIRS = (".git/", ".claude/", "old/", "students/", "node_modules/", ".wrangler/")

# Types assets/js/exercises.js has a renderer for.
EXERCISE_TYPES = {
    "multiple-choice", "true-false", "fill-blank", "matching", "ordering",
    "correction", "typing", "reading-comprehension", "vocabulary", "writing",
}

# Answer strings a student has no way to type into a free-text blank.
UNTYPEABLE = {"-", "--", "–", "—"}

errors: list[str] = []
warnings: list[str] = []


def norm(value) -> str:
    """Compare answers the way assets/js/exercises.js's norm() does."""
    return re.sub(r"[.!?]+$", "", re.sub(r"\s+", " ", str(value or "").strip().lower()))


# Typography a student never notices: two prompts that differ only in curly
# vs straight quotes are the same prompt. Fourteen of the repeats this check
# found were hidden behind exactly that difference.
TYPOGRAPHY = str.maketrans({"\u201c": '"', "\u201d": '"', "\u2018": "'",
                            "\u2019": "'", "\u2013": "-", "\u2014": "-",
                            "\u2026": "..."})


def prompt_key(value) -> str:
    """Compare two prompts the way a student reading the page would."""
    return re.sub(r"\s+", " ", str(value or "").translate(TYPOGRAPHY).strip().lower())


def html_pages():
    for path in sorted(REPO_ROOT.rglob("*.html")):
        rel = path.relative_to(REPO_ROOT).as_posix()
        if rel.startswith(SKIP_DIRS):
            continue
        yield rel, path


def load_pages():
    pages, anchors = {}, {}
    for rel, path in html_pages():
        text = path.read_text(encoding="utf-8", errors="replace")
        pages[rel] = text
        ids = set(re.findall(r'\sid="([^"]+)"', text))
        ids |= set(re.findall(r'\sname="([^"]+)"', text))
        anchors[rel] = ids
    return pages, anchors


# ------------------------------------------------------------------ 1 links
def check_links(pages, anchors):
    link_re = re.compile(r'(?:href|src)="([^"]+)"')
    for rel, text in pages.items():
        base = os.path.dirname(rel)
        for raw in link_re.findall(text):
            url = raw.strip()
            if url.startswith(SITE_ORIGIN):       # absolute self-link
                url, target_base = url[len(SITE_ORIGIN):], ""
            else:
                target_base = base
            if not url or url.startswith(("#", "mailto:", "tel:", "data:", "javascript:")):
                continue
            if re.match(r"^[a-z][a-z0-9+.-]*:", url):   # external scheme
                continue
            path, _, frag = url.partition("#")
            # scripts/stamp_asset_versions.py appends ?v=<hash> to css and js
            # references for cache-busting; the query is not part of the path
            # on disk, so strip it before resolving.
            path, _, _query = path.partition("?")
            path = unquote(path)
            if path:
                target = os.path.normpath(os.path.join(target_base, path)).replace("\\", "/")
                if not (REPO_ROOT / target).exists():
                    errors.append(f"broken link: {rel} -> {raw}")
                    continue
            else:
                target = rel
            if frag and target in anchors and frag not in anchors[target]:
                errors.append(f"broken anchor: {rel} -> {raw} (no id={frag!r} on {target})")


# ----------------------------------------------------------- 2+3 search index
def check_search_index(anchors):
    index = json.loads((REPO_ROOT / "assets/data/search-index.json").read_text(encoding="utf-8"))
    for entry in index:
        path, _, frag = entry["url"].partition("#")
        if not (REPO_ROOT / unquote(path)).exists():
            errors.append(f"search entry {entry['title']!r} -> missing file {entry['url']}")
            continue
        if frag and path in anchors and frag not in anchors[path]:
            errors.append(f"search entry {entry['title']!r} -> dead anchor {entry['url']}")

    # every booklet sheet must be directly reachable from search
    indexed = {e["url"] for e in index}
    for booklet in sorted(REPO_ROOT.glob("cefr/english-classes-*.html")):
        rel = booklet.relative_to(REPO_ROOT).as_posix()
        text = booklet.read_text(encoding="utf-8")
        for sheet_id in re.findall(r'<section class="page" id="(sheet-\d+)">', text):
            want = f"{rel}#{sheet_id}"
            if want not in indexed:
                errors.append(
                    f"booklet sheet not searchable: {want} has no search-index entry "
                    f"(run scripts/build_search_index_sheets.py)")


# --------------------------------------------------------- 4 curriculum <-> site
def check_curriculum():
    index = json.loads((REPO_ROOT / "curriculum/index.json").read_text(encoding="utf-8"))
    listed = set()
    for level in index["levels"].values():
        for unit in level["units"]:
            for entry in unit["lessons"]:
                listed.add(entry["id"] if isinstance(entry, dict) else entry)

    catalog = json.loads((REPO_ROOT / "worker/course-catalog.json").read_text(encoding="utf-8"))
    catalog_urls = {r["url"] for r in catalog["resources"]}
    for resource in catalog["resources"]:
        if not (REPO_ROOT / unquote(resource["url"].partition("#")[0])).exists():
            errors.append(f"course-catalog entry {resource['title']!r} -> missing {resource['url']}")

    for fpath in sorted(glob.glob(str(REPO_ROOT / "curriculum/*/*.json"))):
        if Path(fpath).name == "index.json":
            continue
        lesson = json.loads(Path(fpath).read_text(encoding="utf-8"))
        lesson_id, level = lesson["id"], lesson["level"].lower()
        slug = lesson_id[len(level) + 1:] if lesson_id.startswith(level + "-") else lesson_id
        page = f"levels/{level}/{slug}.html"
        rel = Path(fpath).relative_to(REPO_ROOT).as_posix()
        if not (REPO_ROOT / page).exists():
            errors.append(f"{rel}: no built page at {page} (run scripts/build_lesson.py)")
        if lesson_id not in listed:
            errors.append(f"{rel}: {lesson_id} is not listed in curriculum/index.json")
        if page not in catalog_urls:
            warnings.append(f"{rel}: {page} is not in worker/course-catalog.json "
                            f"(the AI teacher won't know about it)")


# ------------------------------------------------------------ 5 exercise data
def check_exercise_block(where, block, seen_ids):
    eid = block.get("id", "?")
    etype = block.get("type")
    if etype not in EXERCISE_TYPES:
        errors.append(f"{where} {eid}: type {etype!r} has no renderer in exercises.js")
        return
    items = block.get("items") or []
    if not items:
        errors.append(f"{where} {eid}: no items")

    # One section, one kind of question. renderFillBlank gives a blank a
    # <select> when the item supplies "options" and a free-text <input>
    # when it doesn't, so a block whose items disagree renders as two
    # different exercises under one title and one instruction -- which is
    # exactly what "Fill in the Blanks (Part 1 of 3)" on the A2
    # quantifiers lesson did: four dropdowns followed by six text boxes.
    # It happened when a block authored with dropdowns was later padded
    # out with extra items that nobody gave options to.
    if etype == "fill-blank":
        with_options = [i.get("id") for i in items if i.get("options")]
        without = [i.get("id") for i in items if not i.get("options")]
        if with_options and without:
            errors.append(
                f"{where} {eid}: mixes {len(with_options)} dropdown item(s) with "
                f"{len(without)} free-text item(s) in one block "
                f"(no options on: {', '.join(str(i) for i in without[:4])}"
                f"{'...' if len(without) > 4 else ''})")

    # One block, one mode. A `typing` item is graded when it carries an
    # "answer" and self-check when it only carries a "modelAnswer", so a
    # block holding both grades half its items under one title and one
    # instruction, and the score panel reports a percentage that covers
    # only that half. prea1-abc-type reached 6 of 10 that way, because a
    # padding commit dropped gradeable word-spelling items into a block
    # whose question is "Spell your first name" -- which has no key and
    # never can. Those belong in two blocks, not one.
    if etype == "typing":
        keyed = [i.get("id") for i in items if i.get("answer")]
        unkeyed = [i.get("id") for i in items if not i.get("answer")]
        if keyed and unkeyed:
            errors.append(
                f"{where} {eid}: mixes {len(keyed)} graded item(s) with "
                f"{len(unkeyed)} self-check item(s) in one block "
                f"(no answer on: {', '.join(str(i) for i in unkeyed[:4])}"
                f"{'...' if len(unkeyed) > 4 else ''})")

    # The same graded question twice in one block: the student answers it
    # again and the score counts it twice.
    #
    # A self-check block (writing, and typing with no answer key) is judged
    # on the prompt alone, because that is all the student reads. These
    # blocks drill a skill in rounds on purpose, so a repeat is a warning
    # rather than an error -- but a round that repeats word for word gives
    # no hint that a new example is wanted, which is how 97 prompts across
    # 36 blocks came to read as copy-paste. The fix is per-block: either an
    # inline anchor ("of this second topic") where a round has a scenario,
    # or a "Second attempt, with a new example:" prefix where it doesn't.
    graded = etype not in ("writing",) and not (
        etype == "typing" and not any(i.get("answer") for i in items))
    signatures: dict[str, str] = {}
    for item in items:
        if graded:
            sig = json.dumps({k: item.get(k) for k in
                              ("prompt", "statement", "incorrect", "words", "options",
                               "answers", "answer", "answerIndex", "pairs", "modelAnswer")},
                             sort_keys=True, ensure_ascii=False)
        else:
            sig = prompt_key(item.get("prompt"))
            if not sig:
                continue
        if sig in signatures:
            msg = (f"{where} {eid}: item {item.get('id')!r} "
                   f"{'is identical to' if graded else 'asks the same thing as'} "
                   f"{signatures[sig]!r} -- the same question twice in one block")
            (errors if graded else warnings).append(msg)
        else:
            signatures[sig] = item.get("id")

    for item in items:
        iid = item.get("id")
        if not iid:
            errors.append(f"{where} {eid}: an item has no id")
            continue
        if iid in seen_ids:
            errors.append(f"{where}: duplicate item id {iid!r} (also in {seen_ids[iid]})")
        seen_ids[iid] = eid

        if etype == "fill-blank":
            blanks = str(item.get("prompt", "")).count("___")
            answers = item.get("answers")
            if not isinstance(answers, list):
                errors.append(f"{where} {iid}: fill-blank needs an 'answers' list")
            elif blanks != len(answers):
                errors.append(f"{where} {iid}: {blanks} blank(s) but {len(answers)} answer group(s)")
            options = item.get("options")
            # A flat options list is only applied when the item has one
            # blank (see renderFillBlank); on a multi-blank item it would
            # silently render free-text inputs instead of dropdowns.
            if options and not isinstance(options[0], list) and blanks != 1:
                errors.append(f"{where} {iid}: flat 'options' on a {blanks}-blank item")
            if options and isinstance(options[0], list) and len(options) != blanks:
                errors.append(f"{where} {iid}: {len(options)} option group(s) for {blanks} blank(s)")
            # A dropdown whose list doesn't contain any accepted answer
            # cannot be answered correctly at all, and the same option
            # listed twice is a copy-paste that shows up verbatim in the
            # rendered <select>.
            if options and isinstance(answers, list):
                groups = (options if isinstance(options[0], list)
                          else ([options] if blanks == 1 else []))
                for i, group in enumerate(groups):
                    accepted = answers[i] if i < len(answers) else []
                    accepted = accepted if isinstance(accepted, list) else [accepted]
                    if not ({norm(a) for a in accepted} & {norm(o) for o in group}):
                        errors.append(f"{where} {iid}: blank {i + 1} offers {group} but "
                                      f"accepts {accepted} -- no option is a correct answer")
                    if len({norm(o) for o in group}) != len(group):
                        errors.append(f"{where} {iid}: blank {i + 1} lists the same "
                                      f"option twice: {group}")
            # Without a dropdown the student has to type the answer, so
            # an answer nobody would type -- "(no article)" was the real
            # one -- cannot be entered at all. Leaving the blank empty is
            # a deliberate answer only when "" is itself accepted.
            if not options and isinstance(answers, list):
                for i, accepted in enumerate(answers):
                    accepted = accepted if isinstance(accepted, list) else [accepted]
                    if any(norm(a) == "" for a in accepted):
                        continue
                    untypeable = [a for a in accepted
                                  if re.search(r"[()\[\]]", str(a)) or str(a).strip() in UNTYPEABLE]
                    if untypeable and len(untypeable) == len(accepted):
                        errors.append(f"{where} {iid}: blank {i + 1} is free-text but only "
                                      f"accepts {untypeable} -- a student cannot type that")
        elif etype in ("multiple-choice", "vocabulary", "reading-comprehension"):
            options = item.get("options") or []
            answer_index = item.get("answerIndex")
            if len(options) < 2:
                errors.append(f"{where} {iid}: needs at least 2 options")
            elif not isinstance(answer_index, int) or not 0 <= answer_index < len(options):
                errors.append(f"{where} {iid}: answerIndex {answer_index!r} out of range")
            if len(set(options)) != len(options):
                errors.append(f"{where} {iid}: duplicate options")
        elif etype == "correction":
            if not item.get("incorrect"):
                errors.append(f"{where} {iid}: correction needs 'incorrect'")
            if not item.get("answer"):
                errors.append(f"{where} {iid}: correction needs 'answer'")
        elif etype == "ordering":
            if not isinstance(item.get("words"), list) or len(item["words"]) < 2:
                errors.append(f"{where} {iid}: ordering needs a 'words' list")
        elif etype == "matching":
            pairs = item.get("pairs")
            if not isinstance(pairs, list) or not pairs:
                errors.append(f"{where} {iid}: matching needs 'pairs'")
            else:
                # Several rows sharing an answer is a legitimate design --
                # nouns sorted into a/an, subjects into have/has -- and the
                # renderer lists each distinct answer once. What is a
                # mistake is the same row twice: the student is asked the
                # identical question again, usually from a copy-paste.
                rows = [(p.get("left"), p.get("right")) for p in pairs]
                repeated = sorted({r for r in rows if rows.count(r) > 1}, key=str)
                if repeated:
                    shown = ", ".join(f"{l!s} -> {r!s}" for l, r in repeated[:3])
                    warnings.append(f"{where} {iid}: the same row appears more than once ({shown})")
        elif etype == "typing":
            if not item.get("answer") and not item.get("modelAnswer"):
                warnings.append(f"{where} {iid}: typing item with neither 'answer' nor 'modelAnswer'")


def check_exercises(pages):
    block_re = re.compile(r'<script type="application/json" class="exercise-data">(.*?)</script>', re.S)
    for rel, text in pages.items():
        seen: dict[str, str] = {}
        for raw in block_re.findall(text):
            try:
                block = json.loads(raw)
            except json.JSONDecodeError as exc:
                errors.append(f"{rel}: unparseable exercise-data ({exc})")
                continue
            check_exercise_block(rel, block, seen)
    for fpath in sorted(glob.glob(str(REPO_ROOT / "curriculum/*/*.json"))):
        if Path(fpath).name == "index.json":
            continue
        lesson = json.loads(Path(fpath).read_text(encoding="utf-8"))
        rel = Path(fpath).relative_to(REPO_ROOT).as_posix()
        seen = {}
        for block in lesson.get("exercises", []):
            check_exercise_block(rel, block, seen)


# ------------------------------------------------------- 6 built-page assets
# href/src pointing at a css or js file under assets/, with the cache-busting
# stamp captured separately so a missing one is visible.
ASSET_REF = re.compile(r'(?:href|src)="([^"]*assets/[^"]+\.(?:css|js))(\?v=[0-9a-f]+)?"')
BOOKLETS = "cefr/english-classes-"


def check_assets(pages):
    for rel, text in pages.items():
        for asset, stamp in ASSET_REF.findall(text):
            if not stamp:
                errors.append(f"{rel}: {asset} carries no ?v= stamp "
                              f"-- run scripts/stamp_asset_versions.py")
        # The floating verbs button is inert without both of its scripts,
        # and it fails silently: the button renders and does nothing.
        if "data-irregular-verbs-toggle" in text:
            for js in ("irregular-verbs.js", "irregular-verbs-panel.js"):
                if f"assets/js/{js}" not in text:
                    errors.append(f"{rel}: shows the irregular-verbs widget "
                                  f"but never loads {js}")
        if rel.startswith(BOOKLETS):
            if "assets/js/booklet.js" not in text:
                errors.append(f"{rel}: a booklet page must load booklet.js, "
                              f"which fits the sheets to the page for print")
            if "assets/js/dictionary.js" in text:
                errors.append(f"{rel}: loads dictionary.js, which belongs to "
                              f"dictionary.html and not to a booklet")

# ------------------------------------------------------------------ selftest
# Each case is a block that once existed in this repo (or a near-enough
# minimal version of it), so a rule that stops firing is caught here
# rather than the next time a lesson is padded out.
SELFTEST = [
    ("a block that mixes dropdown and free-text items", 1, 0,
     {"id": "b", "type": "fill-blank", "items": [
         {"id": "i1", "prompt": "a ___ b", "answers": [["x"]], "options": ["x", "y"]},
         {"id": "i2", "prompt": "c ___ d", "answers": [["z"]]}]}),
    ("a dropdown offering no correct answer", 1, 0,
     {"id": "b", "type": "fill-blank", "items": [
         {"id": "i1", "prompt": "a ___ b", "answers": [["x"]], "options": ["p", "q"]}]}),
    ("the same option listed twice", 1, 0,
     {"id": "b", "type": "fill-blank", "items": [
         {"id": "i1", "prompt": "a ___ b", "answers": [["x"]], "options": ["x", "y", "x"]}]}),
    ("a free-text blank that only accepts '(no article)'", 1, 0,
     {"id": "b", "type": "fill-blank", "items": [
         {"id": "i1", "prompt": "___ Books are nice.", "answers": [["(no article)"]]}]}),
    ("the same graded question twice", 1, 0,
     {"id": "b", "type": "multiple-choice", "items": [
         {"id": "i1", "prompt": "Which?", "options": ["a", "b"], "answerIndex": 0},
         {"id": "i2", "prompt": "Which?", "options": ["a", "b"], "answerIndex": 0}]}),
    ("the same writing prompt twice (a warning, not an error)", 0, 1,
     {"id": "b", "type": "writing", "items": [
         {"id": "i1", "prompt": "Write about your week."},
         {"id": "i2", "prompt": "Write about your week."}]}),
    ("a self-check prompt repeated with a different model answer", 0, 1,
     {"id": "b", "type": "typing", "items": [
         {"id": "i1", "prompt": "Rewrite it in legal register.",
          "modelAnswer": "The Tenant shall vacate the Premises."},
         {"id": "i2", "prompt": "Rewrite it in legal register.",
          "modelAnswer": "The Buyer shall remit the deposit."}]}),
    ("a self-check prompt repeated with different quote characters", 0, 1,
     {"id": "b", "type": "typing", "items": [
         {"id": "i1", "prompt": "Write one sentence using \u201cdo so.\u201d",
          "modelAnswer": "She offered to help, and did so at once."},
         {"id": "i2", "prompt": 'Write one sentence using "do so."',
          "modelAnswer": "He promised to call, and did so that evening."}]}),
    ("a self-check block whose rounds are told apart", 0, 0,
     {"id": "b", "type": "typing", "items": [
         {"id": "i1", "prompt": "Rewrite it in legal register.",
          "modelAnswer": "The Tenant shall vacate the Premises."},
         {"id": "i2", "prompt": "Second attempt, with a new example: "
                                "Rewrite it in legal register.",
          "modelAnswer": "The Buyer shall remit the deposit."}]}),
    ("a typing block that grades half its items", 1, 0,
     {"id": "b", "type": "typing", "items": [
         {"id": "i1", "prompt": "Spell \"cat\".", "answer": ["C-A-T"]},
         {"id": "i2", "prompt": "Spell your first name.",
          "modelAnswer": "M-A-R-I-A (if your name is Maria)"}]}),
    ("a blank whose answer is to leave it empty", 0, 0,
     {"id": "b", "type": "fill-blank", "items": [
         {"id": "i1", "prompt": "The book ___ you read", "answers": [["—", ""]]}]}),
    ("a clean block", 0, 0,
     {"id": "b", "type": "fill-blank", "items": [
         {"id": "i1", "prompt": "a ___ b", "answers": [["x"]], "options": ["x", "y"]},
         {"id": "i2", "prompt": "c ___ d", "answers": [["z"]], "options": ["z", "w"]}]}),
]


def selftest():
    failed = 0
    for name, want_errors, want_warnings, block in SELFTEST:
        errors.clear()
        warnings.clear()
        check_exercise_block("selftest", block, {})
        got = (len(errors), len(warnings))
        ok = got == (want_errors, want_warnings)
        if not ok:
            failed += 1
        print(f"  {'ok  ' if ok else 'FAIL'} {name} "
              f"-> {got[0]} error(s), {got[1]} warning(s)")
        if not ok:
            for e in errors:
                print(f"         x {e}")
            for w in warnings:
                print(f"         ! {w}")
    errors.clear()
    warnings.clear()
    print(f"{len(SELFTEST) - failed}/{len(SELFTEST)} self-test case(s) passed.")
    return failed


def main():
    if "--selftest" in sys.argv:
        sys.exit(1 if selftest() else 0)
    pages, anchors = load_pages()
    check_links(pages, anchors)
    check_search_index(anchors)
    check_curriculum()
    check_exercises(pages)
    check_assets(pages)

    print(f"Checked {len(pages)} pages, "
          f"{len(glob.glob(str(REPO_ROOT / 'curriculum/*/*.json'))) - 1} curriculum lessons.")
    if "--warnings" in sys.argv and warnings:
        print(f"\n{len(warnings)} warning(s):")
        for w in warnings:
            print(f"  ! {w}")
    elif warnings:
        print(f"{len(warnings)} warning(s) (pass --warnings to list them).")
    if errors:
        print(f"\n{len(errors)} error(s):")
        for e in errors:
            print(f"  x {e}")
        sys.exit(1)
    print("No errors.")


if __name__ == "__main__":
    main()
