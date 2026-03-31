#!/usr/bin/env python3
"""
Task OS: Reminder

Time-based reminders for tasks with due dates/times.
- Date-only tasks (YYYY-MM-DD): one reminder on the due date
- Datetime tasks (YYYY-MM-DD HH:MM): reminders at 24h, 3h, and 1h before

Called by cron every 15 minutes.
"""

import os
import sqlite3
import asyncio
from datetime import datetime, timedelta, timezone
from telegram import Bot
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

DB_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'aios_data.db')
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_TARGET_USER_ID = os.getenv("TELEGRAM_ALLOWED_USER_IDS", "").split(",")[0]

# Moscow timezone (UTC+3) — server runs UTC, but user & due dates are in Moscow time
_MSK = timezone(timedelta(hours=3))

# Reminder stages for datetime tasks (hours before due)
STAGES = [
    ("24h", 24),
    ("3h", 3),
    ("1h", 1),
]


def _ensure_reminder_stage_column():
    """Add reminder_stage column if it doesn't exist (migration)."""
    if not os.path.exists(DB_FILE):
        return
    conn = sqlite3.connect(DB_FILE)
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(tasks)")
        columns = [row[1] for row in cursor.fetchall()]
        if "reminder_stage" not in columns:
            cursor.execute("ALTER TABLE tasks ADD COLUMN reminder_stage TEXT")
            conn.commit()
    finally:
        conn.close()


def _parse_due(due_date_str):
    """Parse due_date string. Returns (datetime, has_time)."""
    if not due_date_str:
        return None, False
    due_date_str = due_date_str.strip()
    # Try datetime first (YYYY-MM-DD HH:MM)
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M"):
        try:
            return datetime.strptime(due_date_str, fmt), True
        except ValueError:
            pass
    # Fall back to date only
    try:
        return datetime.strptime(due_date_str, "%Y-%m-%d"), False
    except ValueError:
        return None, False


def get_tasks_to_remind():
    """Returns tasks needing a reminder right now.

    Returns list of (task_dict, stage_label, time_remaining_text).
    """
    if not os.path.exists(DB_FILE):
        return []

    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, raw_text, next_action, project, context, delegated_to,
                   due_date, reminder_stage
            FROM tasks
            WHERE status = 'pending' AND due_date IS NOT NULL
        """)
        rows = cursor.fetchall()
    finally:
        conn.close()

    now = datetime.now(_MSK).replace(tzinfo=None)
    result = []

    for row in rows:
        task = dict(row)
        due_dt, has_time = _parse_due(task["due_date"])
        if not due_dt:
            continue

        current_stage = task.get("reminder_stage") or ""

        if has_time:
            # Datetime task: check 24h, 3h, 1h stages
            hours_left = (due_dt - now).total_seconds() / 3600

            # Skip if already past due (will be caught by overdue check)
            if hours_left < 0:
                # If never reminded at all, send one "overdue" reminder
                if not current_stage:
                    result.append((task, "overdue", "просрочено"))
                continue

            # Find the next stage to send
            for stage_label, stage_hours in STAGES:
                if current_stage == stage_label:
                    continue  # Already sent this stage
                # Skip stages we've already passed through
                if _stage_order(stage_label) <= _stage_order(current_stage):
                    continue
                if hours_left <= stage_hours:
                    # Time to send this stage
                    if hours_left >= 1:
                        time_text = f"через {int(hours_left)} ч."
                    else:
                        mins = int(hours_left * 60)
                        time_text = f"через {mins} мин."
                    result.append((task, stage_label, time_text))
                    break  # Only one stage per check
        else:
            # Date-only task: remind once on the due date
            if current_stage:
                continue  # Already reminded
            if due_dt.date() <= now.date():
                if due_dt.date() == now.date():
                    time_text = "сегодня"
                else:
                    time_text = "просрочено"
                result.append((task, "date", time_text))

    return result


def _stage_order(stage):
    """Returns numeric order for stage comparison."""
    order = {"": 0, "24h": 1, "3h": 2, "1h": 3, "date": 4, "overdue": 4}
    return order.get(stage, 0)


def update_reminder_stage(task_id, stage):
    """Updates the reminder_stage for a task. Marks 'reminded' on final stage."""
    conn = sqlite3.connect(DB_FILE)
    try:
        cursor = conn.cursor()
        now = datetime.now(_MSK).replace(tzinfo=None).isoformat()

        if stage in ("1h", "date", "overdue"):
            cursor.execute(
                "UPDATE tasks SET reminder_stage = ?, reminded_at = ?, status = 'reminded' WHERE id = ?",
                (stage, now, task_id),
            )
        else:
            cursor.execute(
                "UPDATE tasks SET reminder_stage = ?, reminded_at = ? WHERE id = ?",
                (stage, now, task_id),
            )
        conn.commit()
    finally:
        conn.close()


def format_reminder(task, stage, time_text):
    """Formats a reminder message."""
    parts = []

    # Header with urgency
    if stage == "1h":
        parts.append("\u26a0\ufe0f Напоминание ({})".format(time_text))
    elif stage == "3h":
        parts.append("\u23f0 Напоминание ({})".format(time_text))
    elif stage == "24h":
        parts.append("\U0001f4c5 Напоминание на завтра ({})".format(time_text))
    elif stage == "overdue":
        parts.append("\U0001f534 Просроченная задача!")
    else:
        parts.append("\u23f0 Напоминание ({})".format(time_text))

    if task.get("next_action"):
        parts.append(task["next_action"])
    elif task.get("raw_text"):
        parts.append(task["raw_text"])

    if task.get("project"):
        parts.append(f"Проект: {task['project']}")
    if task.get("delegated_to"):
        parts.append(f"Кому: {task['delegated_to']}")
    if task.get("due_date"):
        parts.append(f"Срок: {task['due_date']}")

    return "\n".join(parts)


def get_pending_summary():
    """Returns a summary of pending tasks for proactive push.

    Checks:
    - Tasks without due_date (need prioritization)
    - Overdue tasks (due_date < today, still pending)
    - Tasks due today
    Returns None if nothing to report.
    """
    if not os.path.exists(DB_FILE):
        return None

    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        now = datetime.now(_MSK).replace(tzinfo=None)
        today_str = now.strftime("%Y-%m-%d")

        # Pending tasks without due_date
        no_date = conn.execute(
            "SELECT id, raw_text, next_action FROM tasks WHERE status = 'pending' AND due_date IS NULL"
        ).fetchall()

        # Overdue tasks (due_date < today, still pending)
        overdue = conn.execute(
            "SELECT id, raw_text, next_action, due_date FROM tasks "
            "WHERE status = 'pending' AND due_date IS NOT NULL AND due_date < ?",
            (today_str,)
        ).fetchall()

        # Tasks due today
        due_today = conn.execute(
            "SELECT id, raw_text, next_action, due_date FROM tasks "
            "WHERE status = 'pending' AND due_date IS NOT NULL AND due_date LIKE ?",
            (today_str + "%",)
        ).fetchall()

        if not no_date and not overdue and not due_today:
            return None

        parts = []

        if overdue:
            parts.append(f"🔴 Просрочено ({len(overdue)}):")
            for t in overdue:
                text = t["next_action"] or t["raw_text"]
                parts.append(f"  • {text[:80]} (срок: {t['due_date'][:10]})")

        if due_today:
            parts.append(f"📅 Сегодня ({len(due_today)}):")
            for t in due_today:
                text = t["next_action"] or t["raw_text"]
                time_part = t["due_date"][11:16] if len(t["due_date"]) > 10 else ""
                if time_part:
                    parts.append(f"  • {text[:80]} ({time_part})")
                else:
                    parts.append(f"  • {text[:80]}")

        if no_date:
            parts.append(f"⚪ Без срока ({len(no_date)}):")
            for t in no_date[:5]:  # Show max 5
                text = t["next_action"] or t["raw_text"]
                parts.append(f"  • {text[:80]}")
            if len(no_date) > 5:
                parts.append(f"  ... и ещё {len(no_date) - 5}")

        return "\n".join(parts)
    finally:
        conn.close()


async def send_reminders():
    """Main entry point: check tasks and send reminders."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_TARGET_USER_ID:
        print("Telegram credentials not set.")
        return

    _ensure_reminder_stage_column()
    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    # 1. Due-date reminders (existing logic)
    tasks_to_remind = get_tasks_to_remind()
    for task, stage, time_text in tasks_to_remind:
        msg = format_reminder(task, stage, time_text)
        # Update stage FIRST to prevent duplicate sends on retry
        update_reminder_stage(task["id"], stage)
        try:
            await bot.send_message(chat_id=TELEGRAM_TARGET_USER_ID, text=msg[:4096])
            print(f"Reminder sent: task #{task['id']} stage={stage}")
        except Exception as e:
            print(f"Error sending reminder for task #{task['id']}: {e}")

    # 2. Morning summary push (only at 7:00-7:15 MSK window)
    now_msk = datetime.now(_MSK).replace(tzinfo=None)
    if 7 <= now_msk.hour <= 7 and now_msk.minute < 15:
        summary = get_pending_summary()
        if summary:
            msg = f"📋 Задачи на сегодня:\n\n{summary}"
            try:
                await bot.send_message(chat_id=TELEGRAM_TARGET_USER_ID, text=msg[:4096])
                print("Morning task summary sent.")
            except Exception as e:
                print(f"Error sending morning summary: {e}")
    else:
        # Outside morning window — still check for overdue-only alerts
        # Push overdue alerts once a day (afternoon check at 14:00-14:15)
        if now_msk.hour == 14 and now_msk.minute < 15:
            summary = get_pending_summary()
            if summary and "🔴 Просрочено" in summary:
                # Only send if there are overdue tasks
                overdue_part = []
                for line in summary.split("\n"):
                    if line.startswith("🔴") or line.startswith("  •"):
                        overdue_part.append(line)
                    elif overdue_part and not line.startswith("  "):
                        break
                if overdue_part:
                    msg = f"⚠️ Напоминание:\n\n" + "\n".join(overdue_part)
                    try:
                        await bot.send_message(chat_id=TELEGRAM_TARGET_USER_ID, text=msg[:4096])
                        print("Afternoon overdue reminder sent.")
                    except Exception as e:
                        print(f"Error sending overdue reminder: {e}")

    if not tasks_to_remind:
        print("No tasks to remind.")


if __name__ == "__main__":
    asyncio.run(send_reminders())
