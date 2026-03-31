#!/usr/bin/env python3
"""
Intelligence Layer: Weekly Strategic Report

Runs every Sunday at 19:00 UTC via cron.
Collects data from all sources for the past 7 days:
- Business metrics trends (Data OS)
- Meetings analyzed (Fireflies)
- Tasks completed / created / overdue (GTD)
- Key decisions from meeting analyses

Synthesizes everything through LLM into a strategic weekly summary.
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
CONTEXT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'context')
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_TARGET_USER_ID = os.getenv("TELEGRAM_ALLOWED_USER_IDS", "").split(",")[0]

# Moscow timezone (UTC+3)
_MSK = timezone(timedelta(hours=3))


def _get_metrics_trends():
    """Gets key metric trends over the past 7 days."""
    if not os.path.exists(DB_FILE):
        return "Нет данных метрик."

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='metrics'")
        if not cursor.fetchone():
            conn.close()
            return "Таблица metrics не создана."

        week_ago = (datetime.now(_MSK).replace(tzinfo=None) - timedelta(days=7)).strftime("%Y-%m-%d")
        today = datetime.now(_MSK).replace(tzinfo=None).strftime("%Y-%m-%d")

        # Product key metrics — latest vs week ago
        sections = []

        # Revenue this week
        cursor.execute("""
            SELECT SUM(value) FROM metrics
            WHERE source = 'Product' AND metric_name = 'revenue_today'
              AND date(date) >= date(?) AND date(date) <= date(?)
        """, (week_ago, today))
        row = cursor.fetchone()
        weekly_revenue = row[0] if row and row[0] else 0

        # New users this week
        cursor.execute("""
            SELECT value FROM metrics
            WHERE source = 'Product' AND metric_name = 'users_new_month'
            ORDER BY date DESC LIMIT 1
        """)
        row = cursor.fetchone()
        new_users = int(row[0]) if row else 0

        # Completed consultations
        cursor.execute("""
            SELECT value FROM metrics
            WHERE source = 'Product' AND metric_name = 'funnel_month_completed'
            ORDER BY date DESC LIMIT 1
        """)
        row = cursor.fetchone()
        completed = int(row[0]) if row else 0

        # Cancelled
        cursor.execute("""
            SELECT value FROM metrics
            WHERE source = 'Product' AND metric_name = 'funnel_month_cancelled'
            ORDER BY date DESC LIMIT 1
        """)
        row = cursor.fetchone()
        cancelled = int(row[0]) if row else 0

        # MRR
        cursor.execute("""
            SELECT value FROM metrics
            WHERE source = 'Product' AND metric_name = 'mrr'
            ORDER BY date DESC LIMIT 1
        """)
        row = cursor.fetchone()
        mrr = row[0] if row else 0

        sections.append(f"Выручка за неделю: ~{weekly_revenue:,.0f} руб.")
        sections.append(f"Новых пользователей за месяц: {new_users}")
        sections.append(f"Консультаций проведено за месяц: {completed}")
        sections.append(f"Отменено за месяц: {cancelled}")
        sections.append(f"MRR: {mrr:,.0f} руб.")

        # YouTube
        cursor.execute("""
            SELECT metric_name, value FROM metrics
            WHERE source = 'YouTube'
            ORDER BY date DESC LIMIT 5
        """)
        yt = cursor.fetchall()
        if yt:
            for name, val in yt:
                sections.append(f"YouTube {name}: {val}")

        conn.close()
        return "\n".join(sections)

    except Exception as e:
        return f"Ошибка метрик: {e}"


def _get_tasks_summary():
    """Gets task stats for the past 7 days."""
    if not os.path.exists(DB_FILE):
        return "Нет данных задач."

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        week_ago = (datetime.now(_MSK).replace(tzinfo=None) - timedelta(days=7)).isoformat()

        # Tasks created this week
        cursor.execute(
            "SELECT COUNT(*) FROM tasks WHERE created_at >= ?", (week_ago,)
        )
        created = cursor.fetchone()[0]

        # Tasks completed this week (status changed to done recently — approximate)
        cursor.execute(
            "SELECT COUNT(*) FROM tasks WHERE status = 'done'"
        )
        done_total = cursor.fetchone()[0]

        # Overdue
        today = datetime.now(_MSK).replace(tzinfo=None).strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT COUNT(*) FROM tasks
            WHERE status IN ('pending', 'reminded')
              AND due_date IS NOT NULL AND date(due_date) < date(?)
        """, (today,))
        overdue = cursor.fetchone()[0]

        # Pending total
        cursor.execute(
            "SELECT COUNT(*) FROM tasks WHERE status IN ('pending', 'reminded')"
        )
        pending = cursor.fetchone()[0]

        # Overdue task details
        cursor.execute("""
            SELECT next_action, due_date FROM tasks
            WHERE status IN ('pending', 'reminded')
              AND due_date IS NOT NULL AND date(due_date) < date(?)
            ORDER BY due_date ASC LIMIT 5
        """, (today,))
        overdue_list = cursor.fetchall()

        conn.close()

        lines = [
            f"Создано за неделю: {created}",
            f"Всего выполнено: {done_total}",
            f"В работе: {pending}",
            f"Просрочено: {overdue}",
        ]

        if overdue_list:
            lines.append("\nПросроченные:")
            for action, due in overdue_list:
                lines.append(f"  - {action} (до {due})")

        return "\n".join(lines)

    except Exception as e:
        return f"Ошибка задач: {e}"


def _get_meetings_summary():
    """Gets processed meetings for the past 7 days."""
    if not os.path.exists(DB_FILE):
        return "Нет данных встреч."

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='processed_meetings'")
        if not cursor.fetchone():
            conn.close()
            return "Нет обработанных встреч."

        week_ago = (datetime.now(_MSK).replace(tzinfo=None) - timedelta(days=7)).isoformat()
        cursor.execute(
            "SELECT title, processed_at FROM processed_meetings WHERE processed_at >= ? ORDER BY processed_at",
            (week_ago,)
        )
        meetings = cursor.fetchall()
        conn.close()

        if not meetings:
            return "Нет встреч за неделю."

        lines = [f"Встреч за неделю: {len(meetings)}"]
        for title, date in meetings:
            lines.append(f"  - {title} ({date[:10]})")

        return "\n".join(lines)

    except Exception as e:
        return f"Ошибка встреч: {e}"


def _load_strategy():
    """Loads strategy.md for context."""
    path = os.path.join(CONTEXT_DIR, "strategy.md")
    if os.path.exists(path):
        with open(path, "r") as f:
            content = f.read()
        return content[:3000]
    return ""


def generate_weekly_report():
    """Generates the weekly strategic report via LLM."""
    metrics = _get_metrics_trends()
    tasks = _get_tasks_summary()
    meetings = _get_meetings_summary()
    strategy = _load_strategy()

    now = datetime.now(_MSK).replace(tzinfo=None)
    week_start = (now - timedelta(days=7)).strftime("%d.%m")
    week_end = now.strftime("%d.%m.%Y")

    prompt = f"""Ты — AIOS, AI Operating System для CEO. Сгенерируй еженедельный стратегический отчёт.

Период: {week_start} — {week_end}

МЕТРИКИ БИЗНЕСА:
{metrics}

ЗАДАЧИ (GTD):
{tasks}

ВСТРЕЧИ:
{meetings}

СТРАТЕГИЯ КОМПАНИИ:
{strategy[:2000]}

Сгенерируй краткий еженедельный отчёт на русском:

1. ИТОГИ НЕДЕЛИ (3-4 ключевых факта)
2. ПРОБЛЕМЫ И РИСКИ (что требует внимания)
3. РЕКОМЕНДАЦИИ НА СЛЕДУЮЩУЮ НЕДЕЛЮ (конкретные действия)

Формат: plain text, без markdown, без emoji. Лаконично и по делу.
"""

    try:
        response = call_gpt(
            messages=[
                {"role": "system", "content": "Ты — стратегический AI-аналитик. Пишешь только на русском. Лаконично, без воды."},
                {"role": "user", "content": prompt}
            ],
            model=MODEL_MAIN,
            max_tokens=2048,
        )
        content = response.content
        if not content:
            return "Ошибка: LLM не вернул ответ."

        header = f"ЕЖЕНЕДЕЛЬНЫЙ ОТЧЁТ\n{week_start} — {week_end}\n\n"
        return header + content

    except Exception as e:
        # Fallback: send raw data instead of empty error
        raw = f"ЕЖЕНЕДЕЛЬНЫЙ ОТЧЁТ\n{week_start} — {week_end}\n\n"
        raw += f"(LLM недоступен: {e})\n\n"
        raw += f"МЕТРИКИ:\n{metrics}\n\nЗАДАЧИ:\n{tasks}\n\nВСТРЕЧИ:\n{meetings}"
        return raw


async def send_to_telegram(text):
    """Sends report to Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_TARGET_USER_ID:
        print("Telegram credentials not set.")
        return
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    for i in range(0, len(text), 4000):
        await bot.send_message(chat_id=TELEGRAM_TARGET_USER_ID, text=text[i:i + 4000])


if __name__ == "__main__":
    send_telegram = "--send" in sys.argv

    report = generate_weekly_report()
    print(report)

    if send_telegram:
        asyncio.run(send_to_telegram(report))
        print("\n[Weekly report sent to Telegram]", file=sys.stderr)
