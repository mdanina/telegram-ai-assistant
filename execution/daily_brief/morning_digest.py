#!/usr/bin/env python3
"""
Morning Digest: Tasks + Meetings

Sends a separate Telegram message with:
- Overdue and today's tasks from GTD
- Pending tasks without due date
- Yesterday's meetings from Fireflies (titles + action items)

Runs via cron at 7:05 UTC, right after the daily brief.
No LLM calls — just structured data.
"""

import os
import sys
import sqlite3
import asyncio
from datetime import datetime, timedelta, timezone
from telegram import Bot
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'intelligence'))

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

DB_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'aios_data.db')
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_TARGET_USER_ID = os.getenv("TELEGRAM_ALLOWED_USER_IDS", "").split(",")[0]

# Moscow timezone (UTC+3)
_MSK = timezone(timedelta(hours=3))


def get_tasks_digest():
    """Returns formatted task digest: overdue, today, upcoming, no-date."""
    if not os.path.exists(DB_FILE):
        return None

    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Check if tasks table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
        if not cursor.fetchone():
            conn.close()
            return None

        today = datetime.now(_MSK).replace(tzinfo=None).strftime("%Y-%m-%d")

        # Overdue tasks (due_date < today)
        cursor.execute("""
            SELECT next_action, project, due_date FROM tasks
            WHERE status IN ('pending', 'reminded')
              AND due_date IS NOT NULL
              AND date(due_date) < date(?)
            ORDER BY due_date ASC
        """, (today,))
        overdue = cursor.fetchall()

        # Due today
        cursor.execute("""
            SELECT next_action, project, due_date FROM tasks
            WHERE status IN ('pending', 'reminded')
              AND due_date IS NOT NULL
              AND date(due_date) = date(?)
            ORDER BY due_date ASC
        """, (today,))
        due_today = cursor.fetchall()

        # Upcoming (next 3 days)
        future = (datetime.now(_MSK).replace(tzinfo=None) + timedelta(days=3)).strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT next_action, project, due_date FROM tasks
            WHERE status IN ('pending', 'reminded')
              AND due_date IS NOT NULL
              AND date(due_date) > date(?)
              AND date(due_date) <= date(?)
            ORDER BY due_date ASC
        """, (today, future))
        upcoming = cursor.fetchall()

        # No due date
        cursor.execute("""
            SELECT next_action, project FROM tasks
            WHERE status IN ('pending', 'reminded')
              AND (due_date IS NULL OR due_date = '')
            ORDER BY created_at DESC
        """)
        no_date = cursor.fetchall()

        conn.close()

        if not overdue and not due_today and not upcoming and not no_date:
            return None

        lines = []

        if overdue:
            lines.append(f"ПРОСРОЧЕНО ({len(overdue)})")
            for t in overdue:
                action = t['next_action'] or '(без описания)'
                days_late = (datetime.now(_MSK).replace(tzinfo=None) - datetime.strptime(t['due_date'][:10], "%Y-%m-%d")).days
                proj = f" [{t['project']}]" if t['project'] else ""
                lines.append(f"  ! {action}{proj} (просрочено на {days_late} дн.)")
            lines.append("")

        if due_today:
            lines.append(f"СЕГОДНЯ ({len(due_today)})")
            for t in due_today:
                action = t['next_action'] or '(без описания)'
                time_part = ""
                if len(t['due_date']) > 10:
                    time_part = f" к {t['due_date'][11:16]}"
                proj = f" [{t['project']}]" if t['project'] else ""
                lines.append(f"  - {action}{proj}{time_part}")
            lines.append("")

        if upcoming:
            lines.append(f"БЛИЖАЙШИЕ 3 ДНЯ ({len(upcoming)})")
            for t in upcoming:
                action = t['next_action'] or '(без описания)'
                date_str = t['due_date'][:10]
                proj = f" [{t['project']}]" if t['project'] else ""
                lines.append(f"  - {action}{proj} ({date_str})")
            lines.append("")

        if no_date:
            lines.append(f"БЕЗ СРОКА ({len(no_date)})")
            for t in no_date[:10]:  # limit to 10
                action = t['next_action'] or '(без описания)'
                proj = f" [{t['project']}]" if t['project'] else ""
                lines.append(f"  - {action}{proj}")
            if len(no_date) > 10:
                lines.append(f"  ... и ещё {len(no_date) - 10}")

        return "\n".join(lines)

    except Exception as e:
        return f"Ошибка чтения задач: {e}"


def get_meetings_digest():
    """Returns formatted meetings digest from Fireflies (last 24h)."""
    try:
        from fireflies_client import get_recent_transcripts
        transcripts = get_recent_transcripts(days=1)

        if not transcripts:
            return None

        lines = [f"ВСТРЕЧИ ЗА СУТКИ ({len(transcripts)})"]

        for t in transcripts:
            title = t.get("title", "Без названия")
            duration = t.get("duration", 0)
            duration_min = round(duration / 60) if duration else 0
            participants = t.get("participants") or []

            lines.append(f"\n  {title}")
            meta = []
            if duration_min:
                meta.append(f"{duration_min} мин")
            if participants:
                meta.append(f"{len(participants)} участников")
            if meta:
                lines.append(f"    {', '.join(meta)}")

            summary = t.get("summary") or {}
            if summary.get("action_items"):
                items = summary["action_items"]
                # Trim to reasonable length
                if len(items) > 500:
                    items = items[:500] + "..."
                lines.append(f"    Задачи: {items}")

        return "\n".join(lines)

    except Exception as e:
        return f"Ошибка Fireflies: {e}"


def build_digest():
    """Builds the full morning digest message."""
    tasks = get_tasks_digest()
    meetings = get_meetings_digest()

    if not tasks and not meetings:
        return None  # Nothing to send

    parts = []
    today_str = datetime.now(_MSK).replace(tzinfo=None).strftime("%d.%m.%Y")
    parts.append(f"ДАЙДЖЕСТ — {today_str}")
    parts.append("")

    if tasks:
        parts.append(tasks)

    if meetings:
        if tasks:
            parts.append("")  # separator
        parts.append(meetings)

    return "\n".join(parts)


async def send_digest(text):
    """Sends digest to Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_TARGET_USER_ID:
        print("Telegram credentials not set.")
        return

    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    for i in range(0, len(text), 4000):
        await bot.send_message(chat_id=TELEGRAM_TARGET_USER_ID, text=text[i:i + 4000])


if __name__ == "__main__":
    send_telegram = "--send" in sys.argv

    digest = build_digest()

    if digest:
        print(digest)
        if send_telegram:
            asyncio.run(send_digest(digest))
            print("\n[Digest sent to Telegram]", file=sys.stderr)
    else:
        print("Нет задач и встреч — дайджест не нужен.")
