#!/usr/bin/env python3
"""
Intelligence Layer: Fireflies.ai Client

Fetches recent meeting transcripts from the Fireflies.ai GraphQL API.
"""

import os
import requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

API_KEY = os.getenv("FIREFLIES_API_KEY")
GRAPHQL_ENDPOINT = "https://api.fireflies.ai/graphql"


def get_recent_transcripts(days=1):
    """Fetches transcripts from the last N days."""
    if not API_KEY:
        print("FIREFLIES_API_KEY not set. Skipping Fireflies.")
        return []

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    from_date = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S.000Z")

    query = """
        query RecentTranscripts($fromDate: DateTime, $limit: Int, $mine: Boolean) {
            transcripts(fromDate: $fromDate, limit: $limit, mine: $mine) {
                id
                title
                date
                duration
                transcript_url
                participants
                summary {
                    overview
                    action_items
                    keywords
                }
                sentences {
                    text
                    speaker_name
                }
            }
        }
    """

    variables = {
        "fromDate": from_date,
        "limit": 20,
        "mine": True
    }

    try:
        response = requests.post(
            GRAPHQL_ENDPOINT,
            headers=headers,
            json={"query": query, "variables": variables},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        if 'errors' in data:
            print(f"Fireflies GraphQL errors: {data['errors']}")
            return []

        transcripts = data.get("data", {}).get("transcripts", []) or []
        print(f"Fireflies: fetched {len(transcripts)} transcripts since {from_date}")
        return transcripts

    except requests.exceptions.RequestException as e:
        print(f"Fireflies API error: {e}")
        return []


def format_transcript_for_analysis(transcript):
    """Formats a single transcript into text for GPT analysis."""
    lines = []
    title = transcript.get("title", "Untitled")
    duration = transcript.get("duration", 0)
    duration_min = round(duration / 60) if duration else 0
    participants = transcript.get("participants", []) or []

    lines.append(f"## Встреча: {title}")
    if duration_min:
        lines.append(f"Длительность: {duration_min} мин")
    if participants:
        lines.append(f"Участники: {', '.join(participants)}")

    # Summary from Fireflies AI
    summary = transcript.get("summary") or {}
    if summary.get("overview"):
        lines.append(f"\nОбзор: {summary['overview']}")
    if summary.get("action_items"):
        lines.append(f"\nЗадачи: {summary['action_items']}")
    if summary.get("keywords"):
        lines.append(f"Ключевые слова: {summary['keywords']}")

    # Full transcript text (truncated for brief)
    sentences = transcript.get("sentences") or []
    if sentences:
        full_text = " ".join(s.get("text", "") for s in sentences[:200])
        if len(full_text) > 3000:
            full_text = full_text[:3000] + "..."
        lines.append(f"\nТранскрипт (фрагмент):\n{full_text}")

    return "\n".join(lines)


if __name__ == "__main__":
    transcripts = get_recent_transcripts(days=7)
    if transcripts:
        print(f"\nНайдено {len(transcripts)} транскриптов:")
        for t in transcripts:
            title = t.get("title", "?")
            summary = t.get("summary") or {}
            overview = summary.get("overview", "нет саммари")
            print(f"  - {title}")
            if overview != "нет саммари":
                print(f"    Обзор: {overview[:150]}...")
    else:
        print("Нет транскриптов (или ещё не было созвонов).")
