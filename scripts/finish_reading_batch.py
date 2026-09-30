#!/usr/bin/env python3
"""
Finish a conversion batch: correct durations, rebuild everything generated,
delete superseded source PDFs, and validate.

Run after authoring content/readings/*.json and marking them with
scripts/mark_reading_status.py. Everything here is idempotent.

    python3 scripts/finish_reading_batch.py                 # rebuild + validate
    python3 scripts/finish_reading_batch.py --drop-pdfs      # also delete the
                                                             # PDFs of converted texts

Duration labels are measured from the generated mp3 rather than guessed. That
only rewrites metadata, and because audio staleness is fingerprinted on the
narration text (not the file's mtime), it never triggers a re-narration.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reading_common as rc

MAP = rc.REPO_ROOT / "docs" / "reading-library-map.json"


def run(*cmd):
    r = subprocess.run([sys.executable, str(rc.REPO_ROOT / "scripts" / cmd[0]), *cmd[1:]],
                       cwd=rc.REPO_ROOT, capture_output=True, text=True)
    sys.stdout.write(r.stdout)
    if r.returncode != 0:
        sys.stderr.write(r.stderr)
    return r.returncode


def fix_durations():
    changed = 0
    for lv, slug, d in rc.all_sources():
        mp3 = rc.audio_path(lv, slug)
        if not mp3.exists():
            continue
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                              "-of", "default=nw=1:nk=1", str(mp3)],
                             capture_output=True, text=True).stdout.strip()
        if not out:
            continue
        secs = int(float(out))
        label = f"{secs // 60}:{secs % 60:02d}"
        p = rc.src_path(lv, slug)
        j = json.loads(p.read_text(encoding="utf-8"))
        if j.get("audio", {}).get("duration_label") != label:
            j.setdefault("audio", {})["duration_label"] = label
            p.write_text(json.dumps(j, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            changed += 1
    print(f"duration labels corrected: {changed}")


def drop_pdfs():
    """Delete the source PDF of every text that now has a page of its own. The
    page plus its Print / Save as PDF button replaces the file."""
    d = json.loads(MAP.read_text(encoding="utf-8"))
    removed = []
    for t in d["texts"]:
        if t.get("status") not in ("IMPLEMENTED", "MERGED"):
            continue
        for f in t.get("source_files", []):
            p = rc.REPO_ROOT / f
            if f.endswith(".pdf") and p.exists():
                subprocess.run(["git", "rm", "-q", f], cwd=rc.REPO_ROOT, check=True)
                removed.append(f)
    print(f"source PDFs deleted: {len(removed)}")
    for f in removed:
        print(f"  {f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--drop-pdfs", action="store_true",
                    help="delete the source PDF of every converted text")
    args = ap.parse_args()

    fix_durations()
    rc_ = 0
    rc_ |= run("build_reading_page.py")
    if args.drop_pdfs:
        drop_pdfs()
    rc_ |= run("build_exercises_hub.py")
    rc_ |= run("build_search_index_readings.py")
    rc_ |= run("build_content_audit.py")

    print("--- validation ---")
    bad = run("check_site_integrity.py")
    audio = run("generate_reading_audio.py", "--check")
    if bad or audio:
        print("VALIDATION FAILED", file=sys.stderr)
        return 1
    print("validation clean")
    return rc_


if __name__ == "__main__":
    sys.exit(main())
