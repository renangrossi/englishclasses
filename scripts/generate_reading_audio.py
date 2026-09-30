#!/usr/bin/env python3
"""
Narrate content/readings/{level}/{slug}.json to
assets/audio/reading/{level}/{slug}.mp3 with edge-tts.

edge-tts is the tool this site already uses -- the 28 existing listening
files in assets/audio/{level}/ were made with it (commits 7f73dc8, f3da4e4)
-- so the voices and pacing here deliberately match that convention rather
than introducing a second-sounding narrator.

It narrates the same "passage" the page renders, so the audio cannot drift
from the text. --check reports any page whose audio is missing or older than
its source JSON, which is how requirement 8's "no stale audio" rule is kept
honest.

This machine has no pip, so edge-tts lives in a venv:

    python3 -m venv /tmp/rl-venv && /tmp/rl-venv/bin/pip install edge-tts
    python3 scripts/generate_reading_audio.py --tts /tmp/rl-venv/bin/edge-tts

Usage:
    python3 scripts/generate_reading_audio.py --check            # report only
    python3 scripts/generate_reading_audio.py b1/nfl [--force]
    python3 scripts/generate_reading_audio.py                    # all stale/missing
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reading_common as rc


def narration_text(d):
    """What the narrator reads: the title, then the passage. Paragraphs are
    joined with blank lines so the voice takes a real pause between them."""
    return "\n\n".join([d["title"].rstrip(".") + "."] + list(d["passage"]))


# Staleness is decided by the narration text, not by file timestamps. Editing
# a title, an exercise or a duration label does not change what the narrator
# says, and an mtime comparison would report those edits as stale and burn a
# regeneration on every one of them. Hashing the exact string sent to edge-tts
# (plus the voice and rate) means audio is rebuilt when, and only when, it no
# longer matches the text -- which is the actual requirement.
MANIFEST = rc.AUDIO_DIR / "manifest.json"


def load_manifest():
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {}


def save_manifest(m):
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(m, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def fingerprint(d, voice, rate):
    h = hashlib.sha256()
    h.update(narration_text(d).encode("utf-8"))
    h.update(f"|{voice}|{rate}".encode("utf-8"))
    return h.hexdigest()[:16]


def voice_and_rate(level, slug, d):
    voice = d.get("audio", {}).get("voice") or rc.pick_voice(slug, d.get("narrator"))
    rate = d.get("audio", {}).get("rate") or rc.LEVEL_RATE[level]
    return voice, rate


def is_stale(level, slug, d=None, manifest=None):
    a = rc.audio_path(level, slug)
    if not a.exists():
        return "missing"
    if d is None:
        return None
    manifest = load_manifest() if manifest is None else manifest
    voice, rate = voice_and_rate(level, slug, d)
    if manifest.get(f"{level}/{slug}", {}).get("fingerprint") != fingerprint(d, voice, rate):
        return "stale"
    return None


def find_tts(explicit):
    if explicit:
        return explicit
    for c in ("edge-tts", "/tmp/rl-venv/bin/edge-tts"):
        p = shutil.which(c) or (c if Path(c).is_file() else None)
        if p:
            return p
    return None


def generate(level, slug, d, tts):
    voice, rate = voice_and_rate(level, slug, d)
    out = rc.audio_path(level, slug)
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [tts, "--voice", voice, "--rate", rate,
           "--write-media", str(out), "--text", narration_text(d)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if r.returncode != 0 or not out.exists() or out.stat().st_size < 2000:
        raise RuntimeError(f"edge-tts failed for {level}/{slug}: {r.stderr.strip()[:300]}")

    # edge-tts can return 0 and still write a file that stops part-way
    # through the text -- it happened once to b1/cachacas, which came out at
    # 1:56 for a passage that needs 3:31, and nothing caught it because the
    # old guard only rejected files under 2 KB. Narration is reliably around
    # 2.0-2.4 KB per word at A2/B1 pacing and 1.7-1.9 at natural speed, so a
    # file under 1.4 KB per word has lost a large part of the text. The
    # threshold is deliberately loose: it is here to catch gross truncation,
    # not to police normal variation between voices.
    words = sum(len(p.split()) for p in d["passage"]) or 1
    kb_per_word = (out.stat().st_size / 1024) / words
    if kb_per_word < 1.4:
        raise RuntimeError(
            f"{level}/{slug}: narration looks truncated -- {out.stat().st_size // 1024} KB "
            f"for {words} words ({kb_per_word:.2f} KB/word, expected >= 1.4). "
            f"Delete the file and run again; this is usually a transient edge-tts failure.")
    return out, voice, rate


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("targets", nargs="*", help="level/slug, e.g. b1/nfl")
    ap.add_argument("--check", action="store_true", help="report missing/stale audio, generate nothing")
    ap.add_argument("--force", action="store_true", help="regenerate even if up to date")
    ap.add_argument("--tts", help="path to the edge-tts executable")
    args = ap.parse_args()

    items = [(lv, sl, d) for lv, sl, d in rc.all_sources()
             if not args.targets or f"{lv}/{sl}" in args.targets]
    if not items:
        print("no matching content/readings/*.json")
        return 0

    if args.check:
        man = load_manifest()
        bad = [(lv, sl, why) for lv, sl, d in items if (why := is_stale(lv, sl, d, man))]
        for lv, sl, why in bad:
            print(f"  {why.upper():8} {lv}/{sl}")
        print(f"{len(items)} reading(s); {len(bad)} need audio")
        return 1 if bad else 0

    tts = find_tts(args.tts)
    if not tts:
        print("error: edge-tts not found. Create the venv shown in this file's docstring,\n"
              "       then pass --tts /tmp/rl-venv/bin/edge-tts", file=sys.stderr)
        return 2

    man = load_manifest()
    done = 0
    for lv, sl, d in items:
        if not args.force and not is_stale(lv, sl, d, man):
            print(f"  up to date {lv}/{sl}")
            continue
        out, voice, rate = generate(lv, sl, d, tts)
        kb = out.stat().st_size // 1024
        man[f"{lv}/{sl}"] = {"fingerprint": fingerprint(d, voice, rate),
                             "voice": voice, "rate": rate, "bytes": out.stat().st_size}
        save_manifest(man)
        print(f"  narrated {out.relative_to(rc.REPO_ROOT)}  ({voice}, rate {rate}, {kb} KB)")
        done += 1
    print(f"{done} audio file(s) written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
