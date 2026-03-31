#!/usr/bin/env python3
"""
Transcript Store

Saves and reads manual text transcripts (from Kontur.Talk, Yandex.Telemost, etc.)
to data/intelligence_reports/transcripts/ for inclusion in the daily brief.

Format: JSON files with title, date, source, text.
"""

import os
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

TRANSCRIPTS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "intelligence_reports", "transcripts"
)

# Keywords that indicate a transcript (Russian + English)
TRANSCRIPT_KEYWORDS = {
    "транскрипт", "транскрипция", "расшифровка", "протокол",
    "встреча", "созвон", "совещание", "transcript", "meeting",
}


def is_transcript_signal(text: str) -> bool:
    """Check if text contains keywords indicating it's a transcript."""
    if not text:
        return False
    lower = text.lower()
    return any(kw in lower for kw in TRANSCRIPT_KEYWORDS)


def save_transcript(text: str, title: str = None, source: str = "manual",
                    file_name: str = None) -> str:
    """Save a text transcript to the transcripts directory.

    Returns the saved file path.
    """
    os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if not title:
        # Use first 50 chars of text as title
        title = text[:50].replace("\n", " ").strip()
        if len(text) > 50:
            title += "..."

    data = {
        "title": title,
        "date": datetime.now().isoformat(),
        "source": source,
        "file_name": file_name,
        "text": text,
    }

    save_path = os.path.join(TRANSCRIPTS_DIR, f"transcript_{timestamp}.json")
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info(f"Transcript saved: {save_path} ({len(text)} chars)")
    return save_path


def get_today_transcripts() -> list:
    """Get all transcripts saved today (for the daily brief)."""
    if not os.path.exists(TRANSCRIPTS_DIR):
        return []

    today = datetime.now().strftime("%Y%m%d")
    yesterday = (datetime.now().replace(hour=0, minute=0) -
                 timedelta(days=1)).strftime("%Y%m%d")

    results = []
    for fname in sorted(os.listdir(TRANSCRIPTS_DIR)):
        if not fname.endswith(".json"):
            continue
        # Match today or yesterday's files
        if today not in fname and yesterday not in fname:
            continue
        try:
            fpath = os.path.join(TRANSCRIPTS_DIR, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            results.append(data)
        except Exception as e:
            logger.error(f"Error reading transcript {fname}: {e}")

    return results


def format_transcript_for_brief(transcript: dict) -> str:
    """Format a stored transcript for inclusion in the daily brief."""
    lines = []
    title = transcript.get("title", "Без названия")
    source = transcript.get("source", "manual")
    text = transcript.get("text", "")

    lines.append(f"--- {title} (источник: {source}) ---")

    # Truncate long transcripts for the brief prompt
    if len(text) > 3000:
        text = text[:3000] + "\n[...транскрипт обрезан, всего символов: " + str(len(text)) + "]"

    lines.append(text)
    return "\n".join(lines)
