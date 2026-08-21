#!/usr/bin/env python3
"""
Regenerate stub "Coming soon" PDFs in cefr/{c1-advanced,c2-proficient}/
from the real, structured, PII-free .txt source files sitting next to
them (same content as the matching .docx, minus the personal contact
header).

This is a $0, local, one-off content-delivery fix -- NOT part of the
curriculum/lesson build pipeline. It exists only because the live PDF
links currently 404-equivalent ("Coming soon... see the website" where
the website doesn't have the content either). See the audit that
found this: every C1/C2 PDF and 10 of 13 B2 PDFs were placeholder
stubs, while C1/C2's .txt files already had full, structured content
(Brief Explanation, Examples, Common Mistakes, Exercises, Answer Key).

B2's 10 missing topics are NOT regenerated here -- they have no
source content at all (confirmed: no matching .docx/.txt exists), so
there is nothing to regenerate from. Those are real authoring work,
tracked separately in the curriculum backlog, not a quick win.

Usage:
    python3 scripts/regenerate_cefr_pdfs.py [--dry-run]
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET_DIRS = [REPO_ROOT / "cefr" / "c1-advanced", REPO_ROOT / "cefr" / "c2-proficient"]

SECTION_RE = re.compile(r"^\d+\.\s+[A-Z][A-Z ()/\-]+$")
HEADER_RULE_RE = re.compile(r"^-{5,}$")

CSS = """
body { font-family: 'Liberation Serif', Georgia, serif; max-width: 720px; margin: 2.5cm auto; line-height: 1.5; color: #1a1a1a; }
h1 { font-size: 20pt; margin-bottom: 0.1em; }
.meta { color: #555; font-size: 10pt; margin-bottom: 1.4em; }
h2 { font-size: 13pt; margin-top: 1.6em; border-bottom: 1px solid #ccc; padding-bottom: 0.2em; }
p, li { font-size: 11pt; }
ul { padding-left: 1.3em; }
footer { margin-top: 3em; font-size: 8pt; color: #888; border-top: 1px solid #ddd; padding-top: 0.5em; }
"""


def parse_txt(path: Path):
    lines = path.read_text(encoding="utf-8").splitlines()
    level, topic = None, None
    body_lines = []
    i = 0
    # Header block: ---- / LEVEL: X / TOPIC: Y / ----
    while i < len(lines) and not (lines[i].startswith("LEVEL:")):
        i += 1
    if i < len(lines):
        level = lines[i].split("LEVEL:", 1)[1].strip()
        i += 1
    if i < len(lines) and lines[i].startswith("TOPIC:"):
        topic = lines[i].split("TOPIC:", 1)[1].strip()
        i += 1
    # skip to end of header rule
    while i < len(lines) and not HEADER_RULE_RE.match(lines[i].strip()):
        i += 1
    i += 1
    body_lines = lines[i:]
    if not level or not topic:
        raise ValueError(f"Could not parse LEVEL/TOPIC header in {path}")
    return level, topic, body_lines


def lines_to_html(body_lines):
    html_parts = []
    in_list = False

    def close_list():
        nonlocal in_list
        if in_list:
            html_parts.append("</ul>")
            in_list = False

    for raw in body_lines:
        line = raw.strip()
        if not line:
            continue
        if SECTION_RE.match(line):
            close_list()
            html_parts.append(f"<h2>{escape(line)}</h2>")
            continue
        # bullet-ish lines: "- ...", "a) ...", "A. ...", "1. ..." (but not
        # section headers, already handled above)
        if re.match(r"^([-•]|[a-zA-Z]\)|[A-Z]\.|\d+\.)\s+", line):
            if not in_list:
                html_parts.append("<ul>")
                in_list = True
            html_parts.append(f"<li>{escape(line)}</li>")
        else:
            close_list()
            html_parts.append(f"<p>{escape(line)}</p>")
    close_list()
    return "\n".join(html_parts)


def escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def build_html(level, topic, body_lines) -> str:
    body_html = lines_to_html(body_lines)
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{escape(topic)}</title>
<style>{CSS}</style></head>
<body>
<h1>{escape(topic)}</h1>
<p class="meta">{escape(level)} &middot; Renan the Teacher &mdash; English Language Academy</p>
{body_html}
<footer>Renan the Teacher &mdash; English Language Academy &middot; renangrossi.github.io/englishclasses</footer>
</body></html>"""


def convert_html_to_pdf(html_path: Path, out_dir: Path):
    subprocess.run(
        ["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(out_dir), str(html_path)],
        check=True, capture_output=True, timeout=60,
    )


def main():
    dry_run = "--dry-run" in sys.argv
    regenerated, skipped = [], []

    for d in TARGET_DIRS:
        for txt_path in sorted(d.glob("*.txt")):
            if txt_path.name == "should-be-here.txt":
                continue
            pdf_path = txt_path.with_suffix(".pdf")
            level, topic, body = parse_txt(txt_path)
            html = build_html(level, topic, body)

            if dry_run:
                print(f"[dry-run] would regenerate: {pdf_path.relative_to(REPO_ROOT)}  ({topic})")
                continue

            with tempfile.TemporaryDirectory() as tmp:
                tmp_dir = Path(tmp)
                html_path = tmp_dir / (txt_path.stem + ".html")
                html_path.write_text(html, encoding="utf-8")
                convert_html_to_pdf(html_path, tmp_dir)
                produced = tmp_dir / (txt_path.stem + ".pdf")
                if not produced.exists():
                    print(f"FAILED to produce PDF for {txt_path}", file=sys.stderr)
                    continue
                shutil.copyfile(produced, pdf_path)
            regenerated.append(pdf_path.relative_to(REPO_ROOT))

    print(f"\nRegenerated {len(regenerated)} PDFs:")
    for p in regenerated:
        print(f"  - {p}")


if __name__ == "__main__":
    main()
