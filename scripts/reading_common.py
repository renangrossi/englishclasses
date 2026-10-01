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

# The subject chip on a card, and the filter group on the hub. The key is the
# value stored in a text's JSON; the label is what a student reads.
#
# Two rules, learned the hard way. A key must mean what its label says: "culture"
# was labelled "American Culture", so a text about a Japanese dog, a Romanian
# valley and a festival in Fukushima all filed themselves under American
# Culture. And a key that names a region must say so, which is why the
# collection's own key is "american-history" rather than a bare "history" that
# the next non-American text would quietly inherit.
TOPIC_LABELS = {
    "work": "Work & Career", "interviews": "Job Interviews", "business": "Business English",
    "travel": "Travel & Places", "everyday": "Everyday Life", "food": "Food & Dining",
    "sports": "Sports", "culture": "Culture & Traditions", "tech": "Technology",
    "science": "Science", "society": "Society", "literature": "Stories & Literature",
    "review": "Review",
    "american-history": "American History", "world-history": "World History",
}

# Each source JSON still records "provenance" (as-published / edited /
# rewritten / merged / new) -- it is the project's own record of how a text
# was produced, and the audit reports on it. It is deliberately NOT printed
# on the page: a student reading the text does not need its edit history.
VALID_PROVENANCE = ("as-published", "edited", "rewritten", "merged", "new")


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
