#!/usr/bin/env python3
"""
Shared definitions for the reading library (see PROJECT_STATUS.md).

Source of truth for a reading text is content/readings/{level}/{slug}.json;
scripts/build_reading_page.py renders it to reading/{level}/{slug}.html and
scripts/generate_reading_audio.py narrates it to
assets/audio/reading/{level}/{slug}.mp3. Both read the same file, which is
what keeps a page and its audio from drifting apart.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "content" / "readings"
PAGE_DIR = REPO_ROOT / "reading"
AUDIO_DIR = REPO_ROOT / "assets" / "audio" / "reading"

LEVELS = ["pre-a1", "a1", "a2", "b1", "b2", "c1", "c2"]

# Pacing already established for this site's 28 listening files (commit 7f73dc8):
# slower for beginners, natural from B2 up.
LEVEL_RATE = {
    "pre-a1": "-15%", "a1": "-15%",
    "a2": "-8%", "b1": "-8%",
    "b2": "+0%", "c1": "+0%", "c2": "+0%",
}

# The 8-voice en-US roster, 4 female / 4 male, matching commit f3da4e4's
# convention: a text with a first-person or named narrator gets a voice of
# that narrator's gender; anything impersonal rotates for variety.
VOICES_F = ["en-US-JennyNeural", "en-US-AriaNeural", "en-US-EmmaNeural", "en-US-MichelleNeural"]
VOICES_M = ["en-US-GuyNeural", "en-US-ChristopherNeural", "en-US-EricNeural", "en-US-BrianNeural"]

TOPIC_LABELS = {
    "work": "Work & Career", "interviews": "Job Interviews", "business": "Business English",
    "travel": "Travel", "everyday": "Everyday Life", "food": "Food & Dining",
    "sports": "Sports", "culture": "American Culture", "tech": "Technology",
    "society": "Society", "literature": "Stories & Literature", "review": "Review",
}

# How the page labels where a text came from, so edited and newly written
# material is never passed off as original source material (requirement 19).
PROVENANCE_LABELS = {
    "as-published": "From the original course material.",
    "edited": "Adapted from the original course material.",
    "rewritten": "Substantially rewritten from the original course material.",
    "merged": "Combined from two or more of the original course texts.",
    "new": "Newly written for this level.",
}


def src_path(level, slug):
    return SRC_DIR / level / f"{slug}.json"


def page_path(level, slug):
    return PAGE_DIR / level / f"{slug}.html"


def audio_path(level, slug):
    return AUDIO_DIR / level / f"{slug}.mp3"


def audio_href(level, slug, rel="../../"):
    return f"{rel}assets/audio/reading/{level}/{slug}.mp3"


def pick_voice(slug, narrator):
    """narrator: "male" | "female" | None. Deterministic per slug, so a
    rebuild does not silently reassign a voice (and thus invalidate audio)."""
    roster = VOICES_M if narrator == "male" else VOICES_F if narrator == "female" \
        else VOICES_F + VOICES_M
    return roster[sum(ord(c) for c in slug) % len(roster)]


def load(level, slug):
    import json
    return json.loads(src_path(level, slug).read_text(encoding="utf-8"))


def all_sources():
    """Every reading source JSON, as (level, slug, data)."""
    import json
    for lv in LEVELS:
        d = SRC_DIR / lv
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.json")):
            yield lv, f.stem, json.loads(f.read_text(encoding="utf-8"))
