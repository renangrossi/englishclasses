#!/usr/bin/env python3
"""
Regenerate the 9 stub "Coming soon" PDFs in cefr/b2-upper-intermediate/ for
B2 topics that were authored from scratch as curriculum/b2/*.json (no
original .docx/.txt ever existed for them, per curriculum/index.json's own
notes) but whose PDF was never generated -- the live "Open PDF" button in
the Grammar Booklets section of levels/b2.html downloaded a ~1KB stub
reading "This lesson PDF is currently being prepared."

Sibling script to regenerate_cefr_pdfs.py (which does the same job for
C1/C2 from their .txt source) -- same HTML->PDF approach via soffice, same
visual style, but reading structured content straight from the curriculum
JSON schema (curriculum/SCHEMA.md) instead of parsing .txt.

Usage:
    python3 scripts/regenerate_b2_pdfs.py [--dry-run]
"""
import html
import re
import shutil
import subprocess
import sys
import tempfile
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CURRICULUM_DIR = REPO_ROOT / "curriculum" / "b2"
OUT_DIR = REPO_ROOT / "cefr" / "b2-upper-intermediate"

TOPICS = [
    "mixed-conditionals",
    "advanced-passive-voice",
    "reported-speech-full-system",
    "modal-perfect",
    "cleft-sentences",
    "inversion-for-emphasis",
    "reduced-relative-clauses",
    "advanced-connectors",
    "wish-if-only",
]

CSS = """
body { font-family: 'Liberation Serif', Georgia, serif; max-width: 720px; margin: 2.5cm auto; line-height: 1.5; color: #1a1a1a; }
h1 { font-size: 20pt; margin-bottom: 0.1em; }
.meta { color: #555; font-size: 10pt; margin-bottom: 1.4em; }
h2 { font-size: 13pt; margin-top: 1.6em; border-bottom: 1px solid #ccc; padding-bottom: 0.2em; }
h3 { font-size: 11.5pt; margin-top: 1.1em; margin-bottom: 0.3em; }
p, li { font-size: 11pt; }
ul, ol { padding-left: 1.3em; }
.mistake { margin-bottom: 0.6em; }
.mistake .wrong { color: #8a1f1f; }
.mistake .right { color: #1f6b2f; }
footer { margin-top: 3em; font-size: 8pt; color: #888; border-top: 1px solid #ddd; padding-top: 0.5em; }
"""


def esc(s: str) -> str:
    return html.escape(s or "", quote=False)


def strip_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s or "")


def build_html(lesson: dict) -> str:
    content = lesson["content"]
    parts = [f"<p>{esc(content.get('intro', ''))}</p>"]

    parts.append("<h2>Rules</h2>")
    for rule in content.get("rules", []):
        parts.append(f"<h3>{esc(strip_tags(rule['heading']))}</h3>")
        parts.append(rule["body"])  # already-sanitized inline HTML from our own JSON

    if content.get("examples"):
        parts.append("<h2>Examples</h2><ul>")
        for ex in content["examples"]:
            parts.append(f"<li>{esc(ex)}</li>")
        parts.append("</ul>")

    if content.get("commonMistakes"):
        parts.append("<h2>Common Mistakes</h2>")
        for m in content["commonMistakes"]:
            parts.append(
                '<p class="mistake"><span class="wrong">✗ ' + esc(m["wrong"]) + "</span><br>"
                '<span class="right">✓ ' + esc(m["right"]) + "</span><br>"
                "<em>" + esc(m["why"]) + "</em></p>"
            )

    if lesson.get("summary"):
        parts.append("<h2>Summary</h2><ul>")
        for s in lesson["summary"]:
            parts.append(f"<li>{esc(s)}</li>")
        parts.append("</ul>")

    body_html = "\n".join(parts)
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{esc(lesson['title'])}</title>
<style>{CSS}</style></head>
<body>
<h1>{esc(lesson['title'])}</h1>
<p class="meta">B2 &middot; Upper-Intermediate &middot; {esc(lesson.get('subtitle', ''))}</p>
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
    regenerated = []
    for topic in TOPICS:
        json_path = CURRICULUM_DIR / f"{topic}.json"
        pdf_path = OUT_DIR / f"{topic}.pdf"
        lesson = json.loads(json_path.read_text(encoding="utf-8"))
        page_html = build_html(lesson)

        if dry_run:
            print(f"[dry-run] would regenerate: {pdf_path.relative_to(REPO_ROOT)}  ({lesson['title']})")
            continue

        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            html_path = tmp_dir / f"{topic}.html"
            html_path.write_text(page_html, encoding="utf-8")
            convert_html_to_pdf(html_path, tmp_dir)
            produced = tmp_dir / f"{topic}.pdf"
            if not produced.exists():
                print(f"FAILED to produce PDF for {topic}", file=sys.stderr)
                continue
            shutil.copyfile(produced, pdf_path)
        regenerated.append(pdf_path.relative_to(REPO_ROOT))

    print(f"\nRegenerated {len(regenerated)} PDFs:")
    for p in regenerated:
        print(f"  - {p}")


if __name__ == "__main__":
    main()
