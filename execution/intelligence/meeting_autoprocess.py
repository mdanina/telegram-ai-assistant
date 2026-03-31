#!/usr/bin/env python3
"""
Intelligence Layer: Meeting Auto-Processor

Runs every 2 hours via cron. Checks Fireflies for new meetings,
analyzes each with LLM, creates GTD tasks from action items,
and sends a summary to Telegram.

Tracks processed meeting IDs in SQLite to avoid duplicates.
"""

import os
import sys
import json
import sqlite3
import asyncio
from datetime import datetime, timedelta, timezone
from telegram import Bot
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common import call_gpt, MODEL_MAIN

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

DB_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'aios_data.db')
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_TARGET_USER_ID = os.getenv("TELEGRAM_ALLOWED_USER_IDS", "").split(",")[0]

# Moscow timezone (UTC+3)
_MSK = timezone(timedelta(hours=3))


def _ensure_table():
    """Creates the processed_meetings tracking table if needed."""
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS processed_meetings (
                meeting_id TEXT PRIMARY KEY,
                title TEXT,
                processed_at TEXT NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()


def _is_processed(meeting_id):
    """Checks if a meeting was already processed."""
    conn = sqlite3.connect(DB_FILE)
    try:
        row = conn.execute(
            "SELECT 1 FROM processed_meetings WHERE meeting_id = ?", (meeting_id,)
        ).fetchone()
        return row is not None
    finally:
        conn.close()


def _mark_processed(meeting_id, title):
    """Marks a meeting as processed."""
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute(
            "INSERT OR IGNORE INTO processed_meetings (meeting_id, title, processed_at) VALUES (?, ?, ?)",
            (meeting_id, title, datetime.now(_MSK).replace(tzinfo=None).isoformat())
        )
        conn.commit()
    finally:
        conn.close()


def _load_context():
    """Loads business context for LLM analysis."""
    context_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'context')
    parts = []
    if os.path.exists(context_dir):
        for f in sorted(os.listdir(context_dir)):
            if f.endswith(".md"):
                with open(os.path.join(context_dir, f), "r") as fh:
                    parts.append(fh.read())
    return "\n\n".join(parts[:3])  # limit context size


def _analyze_meeting(transcript):
    """Analyzes a meeting transcript with LLM. Returns structured dict."""
    title = transcript.get("title", "Без названия")
    duration = transcript.get("duration", 0)
    duration_min = round(duration / 60) if duration else 0
    participants = transcript.get("participants") or []

    sentences = transcript.get("sentences") or []
    full_text = " ".join(s.get("text", "") for s in sentences[:300])
    if len(full_text) > 5000:
        full_text = full_text[:5000] + "..."

    # Fireflies summary as extra context
    ff_summary = transcript.get("summary") or {}
    ff_overview = ff_summary.get("overview", "")
    ff_actions = ff_summary.get("action_items", "")

    business_context = _load_context()

    prompt = f"""Проанализируй встречу и извлеки ключевую информацию.

ВСТРЕЧА: {title}
Длительность: {duration_min} мин
Участники: {', '.join(participants) if participants else 'не указаны'}

Обзор от Fireflies: {ff_overview}
Action items от Fireflies: {ff_actions}

Транскрипт:
{full_text}

Бизнес-контекст:
{business_context[:2000]}

Верни JSON:
{{
  "summary": "краткое резюме встречи (2-3 предложения, на русском)",
  "decisions": ["список принятых решений"],
  "action_items": [
    {{"task": "конкретная задача", "owner": "кто делает или null", "due_date": "YYYY-MM-DD или null"}}
  ],
  "important_notes": "важные заметки, которые не являются задачами (или null)"
}}

Возвращай ТОЛЬКО валидный JSON, без markdown.
"""

    try:
        response = call_gpt(
            messages=[
                {"role": "system", "content": "Ты — AI-аналитик встреч. Отвечай только на русском. Возвращай только валидный JSON."},
                {"role": "user", "content": prompt}
            ],
            model=MODEL_MAIN,
            max_tokens=2048,
        )
        content = (response.content or "").strip()

        # Strip markdown fences
        if content.startswith("```"):
            lines = content.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            content = "\n".join(lines).strip()

        return json.loads(content)

    except Exception as e:
        print(f"LLM analysis error for '{title}': {e}")
        return None


def _create_task(raw_text, next_action, project=None, due_date=None, domain="work"):
    """Creates a task in GTD database."""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO tasks (raw_text, next_action, project, due_date, status, created_at, domain)
               VALUES (?, ?, ?, ?, 'pending', ?, ?)""",
            (raw_text, next_action, project, due_date, datetime.now(_MSK).replace(tzinfo=None).isoformat(), domain)
        )
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Error creating task: {e}")
        return None
    finally:
        if conn:
            conn.close()


def process_new_meetings():
    """Main function: fetch new meetings, analyze, create tasks, return summary."""
    _ensure_table()

    try:
        from fireflies_client import get_recent_transcripts
        transcripts = get_recent_transcripts(days=1)
    except Exception as e:
        print(f"Fireflies fetch error: {e}")
        return None

    if not transcripts:
        print("No new meetings found.")
        return None

    results = []

    for t in transcripts:
        meeting_id = t.get("id", "")
        title = t.get("title", "Без названия")

        if _is_processed(meeting_id):
            print(f"  Skipping (already processed): {title}")
            continue

        print(f"  Analyzing: {title}")
        analysis = _analyze_meeting(t)

        if not analysis:
            _mark_processed(meeting_id, title)
            continue

        # Create GTD tasks from action items
        tasks_created = []
        for item in analysis.get("action_items", []):
            task_text = item.get("task", "").strip()
            if not task_text:
                continue

            owner = item.get("owner")
            due = item.get("due_date")
            project = f"Встреча: {title}"

            raw = f"[Из встречи '{title}'] {task_text}"
            if owner:
                raw += f" (ответственный: {owner})"

            task_id = _create_task(raw, task_text, project=project, due_date=due)
            if task_id:
                tasks_created.append(task_text)

        _mark_processed(meeting_id, title)

        results.append({
            "title": title,
            "summary": analysis.get("summary", ""),
            "decisions": analysis.get("decisions", []),
            "tasks_created": tasks_created,
            "notes": analysis.get("important_notes"),
        })

    if not results:
        print("All meetings already processed.")
        return None

    return results


def format_telegram_message(results):
    """Formats analysis results for Telegram."""
    lines = [f"АНАЛИЗ ВСТРЕЧ ({len(results)})"]

    for r in results:
        lines.append(f"\n--- {r['title']} ---")
        if r["summary"]:
            lines.append(r["summary"])

        if r["decisions"]:
            lines.append("\nРешения:")
            for d in r["decisions"]:
                lines.append(f"  - {d}")

        if r["tasks_created"]:
            lines.append(f"\nЗадачи создано: {len(r['tasks_created'])}")
            for task in r["tasks_created"]:
                lines.append(f"  + {task}")

        if r.get("notes"):
            lines.append(f"\nЗаметки: {r['notes']}")

    return "\n".join(lines)


async def send_to_telegram(text):
    """Sends message to Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_TARGET_USER_ID:
        print("Telegram credentials not set.")
        return
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    for i in range(0, len(text), 4000):
        await bot.send_message(chat_id=TELEGRAM_TARGET_USER_ID, text=text[i:i + 4000])


if __name__ == "__main__":
    send_telegram = "--send" in sys.argv

    results = process_new_meetings()

    if results:
        message = format_telegram_message(results)
        print(message)
        if send_telegram:
            asyncio.run(send_to_telegram(message))
            print("\n[Meeting analysis sent to Telegram]", file=sys.stderr)
    else:
        print("Nothing to process.")
