#!/usr/bin/env python3
"""
Telegram Bot: In-Chat Scheduler

Allows users to set reminders and recurring notifications via chat.
GPT calls set_reminder tool → stored in SQLite → background loop fires them.

Supports:
- Relative: "через 2 часа", "in 30 minutes"
- Absolute: ISO datetime "2026-03-20T14:00"
- Recurring: "every_hours=2" or cron-style (future)
"""

import os
import re
import sqlite3
import asyncio
import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

DB_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'aios_data.db')
_MSK = timezone(timedelta(hours=3))


# ── Database ──────────────────────────────────────────────────────────

def _ensure_table():
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                fire_at TEXT NOT NULL,
                repeat_seconds INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending',
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()


def create_reminder(user_id: int, text: str, fire_at: datetime,
                    repeat_seconds: int = 0) -> int:
    """Creates a reminder. Returns its ID."""
    _ensure_table()
    conn = sqlite3.connect(DB_FILE)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO reminders (user_id, text, fire_at, repeat_seconds, status, created_at)
               VALUES (?, ?, ?, ?, 'pending', ?)""",
            (user_id, text, fire_at.isoformat(), repeat_seconds,
             datetime.now(_MSK).isoformat())
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_due_reminders() -> list:
    """Returns all pending reminders whose fire_at <= now."""
    _ensure_table()
    now = datetime.now(_MSK).isoformat()
    conn = sqlite3.connect(DB_FILE)
    try:
        rows = conn.execute(
            """SELECT id, user_id, text, fire_at, repeat_seconds
               FROM reminders
               WHERE status = 'pending' AND fire_at <= ?""",
            (now,)
        ).fetchall()
        return [
            {"id": r[0], "user_id": r[1], "text": r[2],
             "fire_at": r[3], "repeat_seconds": r[4]}
            for r in rows
        ]
    finally:
        conn.close()


def mark_fired(reminder_id: int, repeat_seconds: int = 0):
    """Marks reminder as fired. If recurring, reschedules."""
    conn = sqlite3.connect(DB_FILE)
    try:
        if repeat_seconds > 0:
            # Reschedule
            next_fire = datetime.now(_MSK) + timedelta(seconds=repeat_seconds)
            conn.execute(
                "UPDATE reminders SET fire_at = ? WHERE id = ?",
                (next_fire.isoformat(), reminder_id)
            )
        else:
            conn.execute(
                "UPDATE reminders SET status = 'fired' WHERE id = ?",
                (reminder_id,)
            )
        conn.commit()
    finally:
        conn.close()


def cancel_reminder(reminder_id: int, user_id: int) -> bool:
    """Cancels a reminder. Returns True if found and cancelled."""
    conn = sqlite3.connect(DB_FILE)
    try:
        cursor = conn.execute(
            "UPDATE reminders SET status = 'cancelled' WHERE id = ? AND user_id = ? AND status = 'pending'",
            (reminder_id, user_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def list_pending(user_id: int) -> list:
    """Lists all pending reminders for a user."""
    _ensure_table()
    conn = sqlite3.connect(DB_FILE)
    try:
        rows = conn.execute(
            """SELECT id, text, fire_at, repeat_seconds
               FROM reminders
               WHERE user_id = ? AND status = 'pending'
               ORDER BY fire_at ASC""",
            (user_id,)
        ).fetchall()
        return [
            {"id": r[0], "text": r[1], "fire_at": r[2], "repeat_seconds": r[3]}
            for r in rows
        ]
    finally:
        conn.close()


# ── Time parsing ──────────────────────────────────────────────────────

def parse_fire_at(when: str) -> datetime:
    """Parses various time formats into a datetime.

    Accepts:
    - ISO: "2026-03-20T14:00", "2026-03-20 14:00"
    - Relative: "+30m", "+2h", "+1d", "30m", "2h"
    - Time today: "14:00", "18:30"
    """
    when = when.strip()

    # Relative: +30m, 2h, +1d, 30m, 90min, 2hours
    rel = re.match(r'^\+?(\d+)\s*(m|min|minutes?|h|hours?|d|days?)$', when, re.IGNORECASE)
    if rel:
        amount = int(rel.group(1))
        unit = rel.group(2)[0].lower()
        if unit == 'm':
            delta = timedelta(minutes=amount)
        elif unit == 'h':
            delta = timedelta(hours=amount)
        elif unit == 'd':
            delta = timedelta(days=amount)
        else:
            delta = timedelta(minutes=amount)
        return datetime.now(_MSK) + delta

    # Time today: "14:00" or "18:30"
    time_match = re.match(r'^(\d{1,2}):(\d{2})$', when)
    if time_match:
        h, m = int(time_match.group(1)), int(time_match.group(2))
        now = datetime.now(_MSK)
        target = now.replace(hour=h, minute=m, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)  # tomorrow if time already passed
        return target

    # ISO datetime
    for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt = datetime.strptime(when, fmt)
            return dt.replace(tzinfo=_MSK)
        except ValueError:
            continue

    raise ValueError(f"Cannot parse time: '{when}'")


def parse_repeat(every: str) -> int:
    """Parses repeat interval to seconds. E.g. '2h' -> 7200, '30m' -> 1800."""
    if not every:
        return 0
    rel = re.match(r'^(\d+)\s*(m|min|h|hours?|d|days?)$', every.strip(), re.IGNORECASE)
    if not rel:
        return 0
    amount = int(rel.group(1))
    unit = rel.group(2)[0].lower()
    if unit == 'm':
        return amount * 60
    elif unit == 'h':
        return amount * 3600
    elif unit == 'd':
        return amount * 86400
    return 0


# ── Format helpers ────────────────────────────────────────────────────

def format_reminder_list(reminders: list) -> str:
    """Formats pending reminders for display."""
    if not reminders:
        return "Нет активных напоминаний."

    lines = [f"Напоминания ({len(reminders)}):\n"]
    for r in reminders:
        fire = r["fire_at"][:16].replace("T", " ")
        repeat = ""
        if r["repeat_seconds"]:
            secs = r["repeat_seconds"]
            if secs >= 86400:
                repeat = f" (каждые {secs // 86400} дн.)"
            elif secs >= 3600:
                repeat = f" (каждые {secs // 3600} ч.)"
            else:
                repeat = f" (каждые {secs // 60} мин.)"
        lines.append(f"  #{r['id']} — {fire}{repeat}\n  {r['text']}")
    return "\n".join(lines)
