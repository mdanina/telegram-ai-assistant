#!/usr/bin/env python3
"""
Daily Brief: Brief Generator

This script generates the daily intelligence brief by pulling data from the
Data OS and Intelligence Layer, synthesizing it with an LLM, and sending it
to Telegram.
"""

import os
import sys
import json
import sqlite3
import logging
from datetime import datetime, timedelta, timezone
from telegram import Bot
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'intelligence'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'data_os'))

from common import call_gpt, MODEL_MAIN

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

# Ensure DB tables exist (creates metrics table if missing)
try:
    from db_setup import create_database
    create_database()
except Exception:
    pass

DB_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'aios_data.db')
REPORTS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'intelligence_reports')
PROMPT_FILE = os.path.join(os.path.dirname(__file__), 'brief_prompt.md')

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_TARGET_USER_ID = os.getenv("TELEGRAM_ALLOWED_USER_IDS", "").split(",")[0]

# Moscow timezone (UTC+3)
_MSK = timezone(timedelta(hours=3))

def get_data_summary():
    """Retrieves a summary of key metrics from the Data OS (non-Product sources)."""
    if not os.path.exists(DB_FILE):
        return "База Data OS не найдена."

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Check if metrics table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='metrics'")
        if not cursor.fetchone():
            conn.close()
            return "- Таблица metrics ещё не создана. Запустите data_snapshot."

        # Get latest metrics from non-Product sources
        lines = []

        # YouTube
        yesterday = (datetime.now(_MSK).replace(tzinfo=None) - timedelta(days=1)).strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT metric_name, value FROM metrics
            WHERE source = 'YouTube' AND date(date) = ?
        """, (yesterday,))
        yt_rows = cursor.fetchall()
        if yt_rows:
            for name, val in yt_rows:
                lines.append(f"- YouTube {name}: {val}")

        # Google Analytics
        cursor.execute("""
            SELECT metric_name, value FROM metrics
            WHERE source = 'Google Analytics' AND date(date) = ?
        """, (yesterday,))
        ga_rows = cursor.fetchall()
        if ga_rows:
            for name, val in ga_rows:
                lines.append(f"- GA {name}: {val}")

        # Yandex Metrika
        cursor.execute("""
            SELECT metric_name, value FROM metrics
            WHERE source = 'YandexMetrika'
            AND snapshot_id = (
                SELECT snapshot_id FROM metrics
                WHERE source = 'YandexMetrika'
                ORDER BY date DESC LIMIT 1
            )
        """)
        ym_rows = cursor.fetchall()
        if ym_rows:
            lines.append("")
            lines.append("🌐 ЯНДЕКС МЕТРИКА")
            for name, val in ym_rows:
                # Format numbers nicely
                if isinstance(val, float) and val == int(val):
                    lines.append(f"  {name}: {int(val)}")
                elif isinstance(val, float):
                    lines.append(f"  {name}: {val:.1f}")
                else:
                    lines.append(f"  {name}: {val}")

        conn.close()

        if not lines:
            lines.append("- Данные из внешних источников (YouTube, GA, Метрика) пока не собраны.")

        return "\n".join(lines)
    except Exception as e:
        return f"- Ошибка чтения внешних метрик: {e}"

def get_product_summary():
    """Retrieves Product business metrics from the Data OS.

    Mirrors the admin dashboard metric groups:
      1. Users & Clients
      2. Consultation funnel
      3. Revenue
      4. Assessments
      5. Specialists
      6. Sessions & Retention
      7. Packages
    """
    if not os.path.exists(DB_FILE):
        return "Product data not available."

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Check if metrics table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='metrics'")
        if not cursor.fetchone():
            conn.close()
            return "Таблица metrics ещё не создана. Данные Product недоступны."

        # Get the latest snapshot's Product metrics
        cursor.execute("""
            SELECT metric_name, value FROM metrics
            WHERE source = 'Product'
            AND snapshot_id = (
                SELECT snapshot_id FROM metrics
                WHERE source = 'Product'
                ORDER BY date DESC LIMIT 1
            )
        """)
        rows = cursor.fetchall()
        conn.close()
    except Exception as e:
        return f"Ошибка чтения метрик Product: {e}"

    if not rows:
        return "No Product metrics collected yet."

    d = {name: value for name, value in rows}

    def i(key):
        return int(d.get(key, 0))

    def f(key):
        return d.get(key, 0)

    sections = []

    # ── 1. Пользователи и клиенты ──
    sec = ["📊 ПОЛЬЗОВАТЕЛИ И КЛИЕНТЫ"]
    sec.append(f"  Всего пользователей: {i('users_total')}")
    sec.append(f"  Новых сегодня: {i('users_new_today')} | за месяц: {i('users_new_month')}")
    sec.append(f"  Активных за месяц: {i('users_active_month')}")
    sec.append(f"  Клиентов всего: {i('clients_total')} (с ≥1 проведённой консультацией)")
    sec.append(f"  Новых клиентов за месяц: {i('clients_new_month')}")
    sections.append("\n".join(sec))

    # ── 2. Воронка консультаций ──
    sec = ["📋 ВОРОНКА КОНСУЛЬТАЦИЙ (за месяц)"]
    sec.append(f"  Заявки (ожидают специалиста): {i('funnel_month_pending_specialist')}")
    sec.append(f"  Ожидают оплаты: {i('funnel_month_payment_pending')}")
    sec.append(f"  Запланированы: {i('funnel_month_scheduled')}")
    sec.append(f"  Проведены: {i('funnel_month_completed')}")
    sec.append(f"  Отменены: {i('funnel_month_cancelled')} | Неявки: {i('funnel_month_no_show')}")
    sec.append(f"  Skip rate: {f('skip_rate_month'):.1f}%")

    # Today's funnel snapshot
    today_new = i('funnel_today_pending_specialist')
    today_completed = i('funnel_today_completed')
    if today_new or today_completed:
        sec.append(f"  → Сегодня: новых заявок {today_new}, проведено {today_completed}")
    sections.append("\n".join(sec))

    # ── 3. Выручка ──
    sec = ["💰 ВЫРУЧКА"]
    sec.append(f"  Сегодня: {f('revenue_today'):,.0f} ₽")
    sec.append(f"  Вчера: {f('revenue_yesterday'):,.0f} ₽")
    sec.append(f"  За месяц: {f('revenue_month'):,.0f} ₽ ({i('payments_count_month')} платежей)")
    sec.append(f"  Средний чек: {f('avg_check_month'):,.0f} ₽")
    sec.append(f"  LTV (на платящего клиента): {f('ltv'):,.0f} ₽")
    sec.append(f"  MRR (за 30 дней): {f('mrr'):,.0f} ₽")
    sec.append(f"  Refund rate: {f('refund_rate'):.1f}%")
    sections.append("\n".join(sec))

    # ── 4. Диагностики ──
    sec = ["🧪 ДИАГНОСТИКИ (за месяц)"]
    sec.append(f"  Всего начато: {i('assessments_total_month')}")
    sec.append(f"  Завершено: {i('assessments_completed_month')}")
    sec.append(f"  Брошено: {i('assessments_abandoned_month')}")
    sec.append(f"  Оплачено: {i('assessments_paid_month')}")
    sec.append(f"  Конверсия (завершение): {f('assessments_conversion'):.1f}%")
    sections.append("\n".join(sec))

    # ── 5. Специалисты ──
    sec = ["👩‍⚕️ СПЕЦИАЛИСТЫ"]
    sec.append(f"  Активных: {i('specialists_active')}")
    rating = f('specialists_avg_rating')
    count = i('specialists_rating_count')
    if count > 0:
        sec.append(f"  Средний рейтинг: {rating:.2f} ({count} отзывов)")
    sections.append("\n".join(sec))

    # ── 6. Сессии и удержание ──
    sec = ["🔄 СЕССИИ И УДЕРЖАНИЕ"]
    sec.append(f"  Повторных клиентов (≥2 сессии): {i('repeat_clients')}")
    sec.append(f"  Среднее кол-во сессий на клиента: {f('avg_sessions_per_client'):.1f}")
    sections.append("\n".join(sec))

    # ── 7. Пакеты ──
    sec = ["📦 ПАКЕТЫ"]
    sec.append(f"  Продано за месяц: {i('packages_sold_month')}")
    sec.append(f"  Сессий использовано/всего: {i('pkg_sessions_used')}/{i('pkg_sessions_total')}")
    sec.append(f"  Осталось сессий: {i('pkg_sessions_remaining')}")
    sections.append("\n".join(sec))

    return "\n\n".join(sections)


def get_intelligence_summary():
    """Retrieves intelligence: Fireflies transcripts + manual transcripts + stored reports."""
    sections = []

    # ── Fireflies meetings (last 24h) ──
    try:
        from fireflies_client import get_recent_transcripts, format_transcript_for_analysis
        transcripts = get_recent_transcripts(days=1)
        if transcripts:
            sections.append(f"🎙 ВСТРЕЧИ (Fireflies): {len(transcripts)} за сутки")
            for t in transcripts:
                sections.append(format_transcript_for_analysis(t))
        else:
            sections.append("🎙 ВСТРЕЧИ: нет записанных созвонов за сутки")
    except Exception as e:
        sections.append(f"🎙 ВСТРЕЧИ: ошибка Fireflies — {e}")

    # ── Manual transcripts (Kontur.Talk, Yandex.Telemost, etc.) ──
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'telegram'))
        from transcript_store import get_today_transcripts, format_transcript_for_brief
        manual = get_today_transcripts()
        if manual:
            sections.append(f"📝 ТРАНСКРИПТЫ (ручные): {len(manual)} за сутки")
            for t in manual:
                sections.append(format_transcript_for_brief(t))
    except Exception as e:
        logger.warning(f"Manual transcripts error: {e}")

    # ── Stored intelligence report (voice notes) ──
    today_str = datetime.now(_MSK).replace(tzinfo=None).strftime("%Y-%m-%d")
    report_path = os.path.join(REPORTS_DIR, f"{today_str}.json")
    if not os.path.exists(report_path):
        yesterday_str = (datetime.now(_MSK).replace(tzinfo=None) - timedelta(days=1)).strftime("%Y-%m-%d")
        report_path = os.path.join(REPORTS_DIR, f"{yesterday_str}.json")

    if os.path.exists(report_path):
        with open(report_path, "r") as f:
            report = json.load(f)
        voice_count = len(report.get('voice_notes', []))
        if voice_count:
            sections.append(f"🎤 Голосовые заметки: {voice_count} обработано")

    if not sections:
        return "Нет данных из Intelligence Layer."

    return "\n\n".join(sections)

def get_tasks_summary():
    """Returns today's tasks, overdue tasks, and delegated tasks for the brief."""
    if not os.path.exists(DB_FILE):
        return ""

    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        now = datetime.now(_MSK).replace(tzinfo=None)
        today_str = now.strftime("%Y-%m-%d")

        # Overdue tasks
        cursor.execute("""
            SELECT next_action, due_date, delegated_to, project
            FROM tasks
            WHERE status IN ('pending', 'reminded')
            AND due_date IS NOT NULL AND date(due_date) < date(?)
            ORDER BY due_date ASC
        """, (today_str,))
        overdue = cursor.fetchall()

        # Today's tasks
        cursor.execute("""
            SELECT next_action, due_date, delegated_to, project
            FROM tasks
            WHERE status IN ('pending', 'reminded')
            AND date(due_date) = date(?)
            ORDER BY due_date ASC
        """, (today_str,))
        today_tasks = cursor.fetchall()

        # Delegated tasks (not yet done)
        cursor.execute("""
            SELECT next_action, due_date, delegated_to, project
            FROM tasks
            WHERE status IN ('pending', 'reminded')
            AND delegated_to IS NOT NULL
            ORDER BY due_date ASC
        """)
        delegated = cursor.fetchall()

        lines = []

        if overdue:
            lines.append(f"ПРОСРОЧЕННЫЕ ({len(overdue)}):")
            for action, due, delegate, project in overdue:
                extra = f" [{project}]" if project else ""
                extra += f" -> {delegate}" if delegate else ""
                lines.append(f"  - {action or '?'} (до {due}){extra}")

        if today_tasks:
            lines.append(f"\nНА СЕГОДНЯ ({len(today_tasks)}):")
            for action, due, delegate, project in today_tasks:
                extra = f" [{project}]" if project else ""
                time_part = f" в {due.split(' ')[1]}" if due and " " in due else ""
                lines.append(f"  - {action or '?'}{time_part}{extra}")

        if delegated:
            lines.append(f"\nДЕЛЕГИРОВАНО ({len(delegated)}):")
            for action, due, delegate, project in delegated:
                due_str = f" (до {due})" if due else ""
                lines.append(f"  - {action or '?'} -> {delegate}{due_str}")

        if not lines:
            lines.append("Нет задач на сегодня и просроченных.")

        return "\n".join(lines)

    except Exception as e:
        return f"Ошибка чтения задач: {e}"
    finally:
        if conn:
            conn.close()


def get_wow_metrics():
    """Returns comparison with previous snapshot for key Product metrics."""
    if not os.path.exists(DB_FILE):
        return ""

    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Get the two most recent Product snapshots
        cursor.execute("""
            SELECT DISTINCT snapshot_id, date FROM metrics
            WHERE source = 'Product'
            ORDER BY date DESC
            LIMIT 2
        """)
        snapshots = cursor.fetchall()
        if len(snapshots) < 2:
            return ""

        latest_id = snapshots[0][0]
        prev_id = snapshots[1][0]

        key_metrics = [
            ("revenue_month", "Выручка за месяц"),
            ("clients_new_month", "Новых клиентов"),
            ("funnel_month_completed", "Проведено консультаций"),
            ("assessments_completed_month", "Завершено диагностик"),
            ("users_new_month", "Новых пользователей"),
        ]

        lines = ["ДИНАМИКА (vs предыдущий снимок):"]
        for metric, label in key_metrics:
            cursor.execute(
                "SELECT value FROM metrics WHERE source='Product' AND snapshot_id=? AND metric_name=?",
                (latest_id, metric)
            )
            row_new = cursor.fetchone()
            cursor.execute(
                "SELECT value FROM metrics WHERE source='Product' AND snapshot_id=? AND metric_name=?",
                (prev_id, metric)
            )
            row_old = cursor.fetchone()

            if row_new and row_old and row_old[0]:
                new_val, old_val = row_new[0], row_old[0]
                diff = new_val - old_val
                pct = (diff / old_val) * 100 if old_val != 0 else 0
                arrow = "+" if diff >= 0 else ""
                if "revenue" in metric:
                    lines.append(f"  {label}: {new_val:,.0f} ({arrow}{pct:.1f}%)")
                else:
                    lines.append(f"  {label}: {int(new_val)} ({arrow}{pct:.1f}%)")

        return "\n".join(lines) if len(lines) > 1 else ""

    except Exception as e:
        return f"Ошибка WoW: {e}"
    finally:
        if conn:
            conn.close()


def generate_brief():
    """Generates the full daily brief. Always returns a string, never crashes."""
    # Init variables before try so fallback can reference them even if
    # the exception happens before all of them are assigned.
    data_summary = ""
    product_summary = ""
    tasks_summary = ""
    wow_metrics = ""
    try:
        if not os.path.exists(PROMPT_FILE):
            return f"Ошибка: файл brief_prompt.md не найден ({PROMPT_FILE})"

        with open(PROMPT_FILE, "r") as f:
            prompt_template = f.read()

        data_summary = get_data_summary()
        product_summary = get_product_summary()
        intelligence_summary = get_intelligence_summary()
        tasks_summary = get_tasks_summary()
        wow_metrics = get_wow_metrics()

        # Enrich data section with tasks and dynamics
        enrichments = []
        if tasks_summary:
            enrichments.append(f"\n\nЗАДАЧИ:\n{tasks_summary}")
        if wow_metrics:
            enrichments.append(f"\n\n{wow_metrics}")

        final_prompt = prompt_template.format(
            date=datetime.now(_MSK).replace(tzinfo=None).strftime("%A, %B %d, %Y"),
            data_os_summary=data_summary + "".join(enrichments),
            product_summary=product_summary,
            intelligence_os_summary=intelligence_summary
        )

        msg = call_gpt(
            messages=[
                {"role": "system", "content": "Ты — AI Operating System (AIOS). Генерируй ежедневный бриф для CEO. Весь ответ ТОЛЬКО на русском языке. Никакого английского."},
                {"role": "user", "content": final_prompt}
            ],
            model=MODEL_MAIN,
            max_tokens=4096,
        )
        content = msg.content or "[Ошибка: GPT не вернул ответ]"
        return content
    except Exception as e:
        # Fallback: send raw collected data instead of empty error
        raw_parts = [f"ЕЖЕДНЕВНЫЙ БРИФ (LLM недоступен: {e})\n"]
        if product_summary:
            raw_parts.append(f"PRODUCT:\n{product_summary}\n")
        if tasks_summary:
            raw_parts.append(f"ЗАДАЧИ:\n{tasks_summary}\n")
        if wow_metrics:
            raw_parts.append(f"ДИНАМИКА:\n{wow_metrics}\n")
        if data_summary:
            raw_parts.append(f"ДАННЫЕ:\n{data_summary}\n")
        return "\n".join(raw_parts)

async def send_brief_to_telegram(brief_content):
    """Sends the generated brief to the specified Telegram user."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_TARGET_USER_ID:
        print("Telegram credentials not set. Cannot send brief.")
        return

    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    # Telegram messages have a 4096 character limit — send in chunks
    for i in range(0, len(brief_content), 4000):
        await bot.send_message(chat_id=TELEGRAM_TARGET_USER_ID, text=brief_content[i:i + 4000])

if __name__ == "__main__":
    import asyncio

    send_telegram = "--send" in sys.argv

    try:
        brief = generate_brief()
        print(brief)
    except Exception as e:
        print(f"Критическая ошибка генерации брифа: {e}")
        sys.exit(1)

    if send_telegram:
        asyncio.run(send_brief_to_telegram(brief))
        print("\n[Brief sent to Telegram]", file=sys.stderr)
