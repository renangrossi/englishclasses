#!/usr/bin/env python3
"""
Semi-automated converter: cefr/{level}/{topic}.txt (the structured
LEVEL/TOPIC + 5-section format confirmed identical across all C1 and C2
source files) -> curriculum/{level}/{lesson-id}.json (the schema in
curriculum/SCHEMA.md).

This is the "AI-assisted first draft" half of the agreed hybrid workflow
(source material -> pedagogical analysis -> gap detection -> curriculum
decision -> lesson creation). It reliably parses structure (rules,
examples, common mistakes, exercise items, answer keys) because that
structure is verified consistent across files. It does NOT invent
per-item pedagogical explanations for the batch-converted exercise items
(A/B/C sub-exercises get a rule-pointer explanation, not a bespoke one
like the hand-authored pilot lesson) -- that enrichment is flagged as
follow-up work, not silently faked.

Usage:
    python3 scripts/parse_cefr_txt_to_lesson.py cefr/c1-advanced/advanced-verb-patterns.txt
    (writes curriculum/c1/advanced-verb-patterns.json)
"""
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

SECTION_HEAD_RE = re.compile(r"^\d+\.\s+(BRIEF EXPLANATION|EXAMPLES|COMMON MISTAKES|EXERCISES|ANSWER KEY)\s*$")
LETTER_HEAD_RE = re.compile(r"^([a-z])\)\s+(.*)$")
BULLET_RE = re.compile(r"^-\s+(.*)$")
NUM_ITEM_RE = re.compile(r"^(\d+)\.\s+(.*)$")
SUBEX_RE = re.compile(r"^([A-D])\.\s+(.*)$")


def split_sections(body_lines):
    sections = {}
    current = None
    buf = []
    for line in body_lines:
        m = SECTION_HEAD_RE.match(line.strip())
        if m:
            if current:
                sections[current] = buf
            current = m.group(1)
            buf = []
        else:
            buf.append(line)
    if current:
        sections[current] = buf
    return sections


def parse_explanation(lines):
    """Returns (intro_text, rules[], register_note, explanation_html or None).

    Most C1/C2 source files break section 1 into lettered a)/b)/c) blocks --
    those become `rules` (rendered as separate cards). A few (e.g.
    inversion-for-emphasis.txt) instead use a flowing structure with
    "Label:" sub-headers and "- " bullets and no lettered breakdown; for
    those, nothing is silently dropped -- the whole section is preserved
    as `explanation_html` (rendered as one prose block) instead of being
    truncated into just the short intro snippet.
    """
    intro_parts = []
    rules = []
    register_note = None
    current_rule = None
    explanation_blocks = []  # used only when there are no lettered rules

    def flush_bullets(bullets):
        if not bullets:
            return ""
        return "<ul>" + "".join(f"<li>{b}</li>" for b in bullets) + "</ul>"

    bullets = []
    fallback_bullets = []

    def flush_fallback():
        if fallback_bullets:
            explanation_blocks.append(flush_bullets(fallback_bullets))
            fallback_bullets.clear()

    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if line.lower().startswith("register note:"):
            register_note = line.split(":", 1)[1].strip()
            continue
        m = LETTER_HEAD_RE.match(line)
        if m:
            if current_rule is not None:
                current_rule["body"] += flush_bullets(bullets)
                rules.append(current_rule)
            bullets = []
            current_rule = {"heading": f"{m.group(1)}) {m.group(2)}", "body": ""}
            continue
        mb = BULLET_RE.match(line)
        if mb and current_rule is not None:
            bullets.append(mb.group(1))
            continue
        if mb and current_rule is None:
            fallback_bullets.append(mb.group(1))
            continue
        if current_rule is not None:
            if bullets:
                bullets[-1] += " " + line
            else:
                current_rule["body"] += f"<p>{line}</p>"
            continue
        # no lettered rule active: goes to both the short intro accumulator
        # and, verbatim, to the fallback explanation blocks so nothing is lost
        flush_fallback()
        intro_parts.append(line)
        if re.match(r"^[A-Z][a-z ]+:$|^[A-Z][a-z ]+:\s", line) and len(line) < 60:
            explanation_blocks.append(f"<p><strong>{line}</strong></p>")
        else:
            explanation_blocks.append(f"<p>{line}</p>")
    flush_fallback()
    if current_rule is not None:
        current_rule["body"] += flush_bullets(bullets)
        rules.append(current_rule)

    explanation_html = "".join(explanation_blocks) if (explanation_blocks and not rules) else None
    return " ".join(intro_parts), rules, register_note, explanation_html


def parse_examples(lines):
    out = []
    for raw in lines:
        m = NUM_ITEM_RE.match(raw.strip())
        if m:
            out.append(m.group(2))
    return out


def parse_common_mistakes(lines):
    text = "\n".join(lines)
    # Each item: "N. Incorrect: ...\n   Correct: ...\n   Why: ..."
    # "Incorrect:"/"Correct:" sometimes carry a parenthetical register/context
    # note before the colon, e.g. "Incorrect (journalistic): ..." -- match
    # any such qualifier (kept as a "[Label]" prefix, since mastery-of-register
    # specifically organizes its mistakes by register) rather than requiring
    # the bare label.
    pattern = re.compile(
        r"\d+\.\s*Incorrect\s*(?:\(([^)]*)\))?:\s*(.*?)\s*\n\s*Correct\s*(?:\(([^)]*)\))?:\s*(.*?)\s*\n\s*Why:\s*(.*?)(?=\n\s*\n|\n\d+\.\s*Incorrect|\Z)",
        re.S,
    )
    out = []
    for m in pattern.finditer(text):
        wrong_label, wrong, right_label, right, why = (g.strip() if g else g for g in m.groups())
        why = why.replace("\n", " ")
        wrong = (f"[{wrong_label}] " if wrong_label else "") + wrong.replace("\n", " ")
        right = (f"[{right_label}] " if right_label else "") + right.replace("\n", " ")
        out.append({"wrong": wrong, "right": right, "why": why})
    return out


def split_subexercises(lines):
    """Returns dict letter -> {title, items: [(num, text)]}"""
    subs = {}
    current = None
    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped:
            continue
        m = SUBEX_RE.match(stripped)
        if m:
            current = m.group(1)
            subs[current] = {"title": m.group(2), "items": []}
            continue
        mi = NUM_ITEM_RE.match(stripped)
        if mi and current:
            subs[current]["items"].append((int(mi.group(1)), mi.group(2)))
    return subs


def build_exercises(ex_lines, key_lines, topic_slug):
    ex_subs = split_subexercises(ex_lines)
    key_subs = split_subexercises(key_lines)
    exercises = []

    # A. Gap-fill -> fill-blank
    if "A" in ex_subs:
        items = []
        answers_by_num = {n: t for n, t in key_subs.get("A", {}).get("items", [])}
        for n, prompt in ex_subs["A"]["items"]:
            ans = answers_by_num.get(n, "")
            items.append({
                "id": f"{topic_slug}-a{n}", "prompt": prompt,
                "answers": [[a.strip() for a in re.split(r"\s*/\s*", ans)]] if ans else [[]],
                "explanation": "See the rule above for this form.",
            })
        exercises.append({"id": f"{topic_slug}-gapfill", "type": "fill-blank",
                           "title": "Gap-fill", "instructions": ex_subs["A"]["title"], "items": items})

    # B. Rewrite / Transformation -> typing (graded)
    if "B" in ex_subs:
        items = []
        answers_by_num = {n: t for n, t in key_subs.get("B", {}).get("items", [])}
        for n, prompt in ex_subs["B"]["items"]:
            ans = answers_by_num.get(n, "")
            items.append({
                "id": f"{topic_slug}-b{n}", "prompt": prompt,
                "answer": [ans] if ans else [],
                "explanation": "Compare your sentence to the model above once you submit.",
            })
        exercises.append({"id": f"{topic_slug}-transform", "type": "typing",
                           "title": "Rewrite / Transformation", "instructions": ex_subs["B"]["title"], "items": items})

    # C. Error Correction -> correction
    if "C" in ex_subs:
        items = []
        answers_by_num = {n: t for n, t in key_subs.get("C", {}).get("items", [])}
        for n, incorrect in ex_subs["C"]["items"]:
            ans = answers_by_num.get(n, incorrect)
            note = ""
            m = re.search(r"\(([^()]*correct as written[^()]*)\)", ans, re.I)
            if m:
                note = " (already correct)"
                ans = ans[: m.start()].strip()
            items.append({
                "id": f"{topic_slug}-c{n}", "incorrect": incorrect,
                "answer": [a.strip() for a in re.split(r"\s*/\s*", ans)],
                "explanation": "Check the rule above for this structure." + note,
            })
        exercises.append({"id": f"{topic_slug}-correction", "type": "correction",
                           "title": "Error Correction", "items": items})

    # D. Guided Production -> typing (self-check, modelAnswer)
    if "D" in ex_subs:
        items = []
        answers_by_num = {n: t for n, t in key_subs.get("D", {}).get("items", [])}
        for n, prompt in ex_subs["D"]["items"]:
            model = answers_by_num.get(n)
            item = {"id": f"{topic_slug}-d{n}", "prompt": prompt}
            if model:
                item["modelAnswer"] = model
            items.append(item)
        exercises.append({"id": f"{topic_slug}-guided", "type": "typing",
                           "title": "Guided Production",
                           "instructions": "Write your own sentence. There's no single correct answer — a model answer is shown for comparison after you submit.",
                           "items": items})

    return exercises


def convert(txt_path: Path):
    txt_path = txt_path.resolve()
    lines = txt_path.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines) and not lines[i].startswith("LEVEL:"):
        i += 1
    level = lines[i].split("LEVEL:", 1)[1].strip()
    i += 1
    topic = lines[i].split("TOPIC:", 1)[1].strip()
    i += 1
    while i < len(lines) and not re.match(r"^-{5,}$", lines[i].strip()):
        i += 1
    i += 1
    body = lines[i:]

    sections = split_sections(body)
    intro, rules, register_note, explanation_html = parse_explanation(sections.get("BRIEF EXPLANATION", []))
    examples = parse_examples(sections.get("EXAMPLES", []))
    mistakes = parse_common_mistakes(sections.get("COMMON MISTAKES", []))
    topic_slug = txt_path.stem
    exercises = build_exercises(sections.get("EXERCISES", []), sections.get("ANSWER KEY", []), topic_slug)

    lesson_id = f"{level.lower()}-{topic_slug}"
    # When there's no lettered a)/b)/c) breakdown, use just the first
    # sentence as the short intro (next to the objectives box) and keep
    # the full flowing explanation as its own prose block -- otherwise
    # the long "Common triggers" style content would only ever appear
    # truncated to ~160 characters.
    short_intro = intro
    if explanation_html:
        first_sentence = re.split(r"(?<=[.!?])\s+", intro.strip(), maxsplit=1)[0]
        short_intro = first_sentence
    content = {"intro": short_intro, "rules": rules, "examples": examples, "commonMistakes": mistakes}
    if explanation_html:
        content["explanation"] = explanation_html
    if register_note:
        content["registerNote"] = register_note

    lesson = {
        "id": lesson_id, "level": level, "unit": "1", "order": None,
        "skill": "grammar", "strand": topic_slug, "title": topic,
        "subtitle": short_intro[:160] + ("…" if len(short_intro) > 160 else ""),
        "prerequisites": [],
        "objectives": [f"Understand and use: {r['heading'].split(') ', 1)[-1]}" for r in rules] or [f"Understand and use {topic}"],
        "content": content,
        "exercises": exercises,
        "summary": [r["heading"] for r in rules] or [f"Review the explanation above for {topic}."],
        "related": [],
        "sourceMaterial": {
            "docx": str(txt_path.with_suffix(".docx").relative_to(REPO_ROOT)),
            "txt": str(txt_path.relative_to(REPO_ROOT)),
            "pdf": str(txt_path.with_suffix(".pdf").relative_to(REPO_ROOT)),
        },
    }

    out_dir = REPO_ROOT / "curriculum" / level.lower()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{topic_slug}.json"
    out_path.write_text(json.dumps(lesson, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path, lesson


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        p, lesson = convert(Path(arg))
        n_items = sum(len(e["items"]) for e in lesson["exercises"])
        print(f"{p.relative_to(REPO_ROOT)}  ({len(lesson['exercises'])} blocks, {n_items} items, {len(lesson['content']['rules'])} rules, {len(lesson['content']['examples'])} examples, {len(lesson['content']['commonMistakes'])} mistakes)")
