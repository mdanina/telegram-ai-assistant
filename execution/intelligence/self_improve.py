#!/usr/bin/env python3
"""
Intelligence Layer: Self-Improvement v2

Daily job with two alternating modes:
  - Code Review (even days): Claude Code reads the entire AIOS codebase and
    proposes fixes, new features, and UX improvements grounded in real code.
  - Feature Scout (odd days): Claude Code searches the web for new AI agent
    patterns and proposes improvements tied to specific AIOS files.

All analysis runs through Claude Code CLI — no direct GPT calls.

Cron: 0 8 * * * (8:00 UTC = 11:00 Moscow)
"""

import os
import subprocess
import sqlite3
import asyncio
import logging
from datetime import datetime
from telegram import Bot
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

BASE_DIR = os.path.join(os.path.dirname(__file__), '..', '..')
DB_FILE = os.path.join(BASE_DIR, 'data', 'aios_data.db')
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_TARGET_USER_ID = os.getenv("TELEGRAM_ALLOWED_USER_IDS", "").split(",")[0]

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# Rotate search topics daily (used in feature_scout mode)
SEARCH_QUERIES = [
    "OpenClaw AI agent new features 2026",
    "personal AI assistant automation use cases 2026",
    "Telegram bot AI agent capabilities 2026",
    "AI agent self-improvement autonomous workflows",
    "Claude Code automation best practices 2026",
    "AI agent cron jobs background automation",
    "AI personal assistant productivity features 2026",
]


# ── Database ──────────────────────────────────────────────────────────

def _ensure_log_table():
    """Create self_improve_log table if it doesn't exist."""
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS self_improve_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            mode TEXT,
            content TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def _get_previous_findings():
    """Get recent findings to avoid repeating the same suggestions."""
    try:
        conn = sqlite3.connect(DB_FILE)
        rows = conn.execute(
            "SELECT content FROM self_improve_log ORDER BY created_at DESC LIMIT 3"
        ).fetchall()
        conn.close()
        if rows:
            return "\n---\n".join(r[0][:1500] for r in rows)
    except Exception:
        pass
    return ""


def _save_to_log(mode, content):
    """Save findings to the log table."""
    conn = sqlite3.connect(DB_FILE)
    conn.execute(
        "INSERT INTO self_improve_log (date, mode, content, created_at) VALUES (?, ?, ?, ?)",
        (datetime.now().strftime("%Y-%m-%d"), mode, content, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


# ── Claude Code CLI ──────────────────────────────────────────────────

def _call_claude(prompt, timeout=900):
    """Call Claude Code CLI and return stdout."""
    try:
        cmd = [
            "claude",
            "--allowedTools", "Bash,Read,Glob,Grep,WebFetch,WebSearch",
            "-p", prompt,
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=BASE_DIR,
            env={**os.environ},
        )
        output = result.stdout.strip()
        if not output:
            log.error("Claude returned empty output. stderr: %s", result.stderr[:500])
            return None
        return output
    except subprocess.TimeoutExpired:
        log.error("Claude timed out (%ds)", timeout)
        return None
    except FileNotFoundError:
        log.error("Claude Code CLI not found")
        return None
    except Exception as e:
        log.error("Claude error: %s", e)
        return None


# ── Modes ────────────────────────────────────────────────────────────

def _get_today_mode():
    """Even day of year → code_review, odd → feature_scout."""
    day = datetime.now().timetuple().tm_yday
    return "code_review" if day % 2 == 0 else "feature_scout"


def _get_today_query():
    """Pick a search query based on the day of the year."""
    day = datetime.now().timetuple().tm_yday
    return SEARCH_QUERIES[day % len(SEARCH_QUERIES)]


def _run_code_review():
    """Full codebase review via Claude Code."""
    previous = _get_previous_findings()
    dedup_block = ""
    if previous:
        dedup_block = (
            "\n\nПРЕДЫДУЩИЕ ПРЕДЛОЖЕНИЯ (НЕ повторяй их, ищи НОВОЕ):\n"
            f"{previous}\n"
        )

    prompt = f"""Прочитай ВСЕ Python-файлы проекта AIOS:
- execution/telegram/ (bot.py, task_handler.py, slash_commands.py, skills_menu.py, email_handler.py, voice_handler.py, photo_handler.py, document_handler.py, meeting_handler.py, bot_memory.py, transcript_store.py, utils.py)
- execution/daily_brief/ (brief_generator.py)
- execution/intelligence/ (intelligence_orchestrator.py, meeting_analyzer.py, meeting_autoprocess.py, article_finder.py, weekly_report.py, voice_processor.py, fireflies_client.py)
- execution/task_os/ (gtd_processor.py, reminder.py)
- execution/data_os/ (query.py, snapshot.py, db_setup.py, db_router.py + collectors/)

Также прочитай context/strategy.md — учитывай бизнес-стратегию при предложении фич.

Проведи комплексный анализ с фокусом на ТРИ направления:

1. НАДЁЖНОСТЬ И БЕЗОПАСНОСТЬ
   - Необработанные edge cases, отсутствие retry/fallback
   - Утечки ресурсов (SQLite соединения, subprocess, память)
   - Потенциальные инъекции (SQL, prompt injection через user input)
   - Захардкоженные значения которые стоит вынести в конфиг
   - Дублирование кода между модулями

2. ФУНКЦИОНАЛЬНОСТЬ — ЧТО ДОБАВИТЬ
   - Какие возможности системы недоиспользуются или могут быть расширены
   - Какие данные уже собираются но не анализируются
   - Какие связи между модулями можно создать (например: данные из meeting_analyzer могут обогащать weekly_report)
   - Какие новые автоматизации просятся на базе существующей инфраструктуры
   - Что можно автоматизировать из того что сейчас делается вручную

3. ПОЛЬЗОВАТЕЛЬСКИЙ ОПЫТ
   - Как улучшить взаимодействие через Telegram бот (новые команды, улучшение существующих)
   - Что в текущих ответах бота можно сделать полезнее, информативнее, удобнее
   - Какие сценарии использования не покрыты (частые запросы CEO которые бот не умеет)
   - Как улучшить брифинги, отчёты, напоминания

Для КАЖДОГО предложения укажи:
- Файл(ы) и строку где менять
- Что не так / чего не хватает
- Как исправить / что добавить (конкретно)
- Категория: баг / надёжность / новая фича / UX
- Приоритет: критичный / высокий / средний / низкий
{dedup_block}
Не выдумывай проблем. Приоритизируй: сначала то что ломается или мешает, потом то что добавит ценность.
Формат: plain text, без markdown. На русском языке."""

    log.info("Running full code review via Claude Code...")
    return _call_claude(prompt, timeout=3600)


def _run_feature_scout(query):
    """Search the web for new ideas and tie them to AIOS code."""
    previous = _get_previous_findings()
    dedup_block = ""
    if previous:
        dedup_block = (
            "\n\nПРЕДЫДУЩИЕ ПРЕДЛОЖЕНИЯ (НЕ повторяй их, ищи НОВОЕ):\n"
            f"{previous}\n"
        )

    prompt = f"""Выполни два шага:

1. Прочитай ключевые файлы AIOS чтобы понять текущие возможности:
   - execution/telegram/task_handler.py
   - execution/daily_brief/brief_generator.py
   - execution/intelligence/article_finder.py
   - execution/task_os/gtd_processor.py
   - execution/data_os/query.py
   - context/strategy.md

2. Найди в интернете (используй WebSearch): {query}
   Прочитай 2-3 самых релевантных результата через WebFetch.

3. На основе найденного предложи 2-3 улучшения для AIOS.

Для каждого предложения:
- Что: одно предложение
- Зачем: какую бизнес-проблему решает для CEO платформы детского ментального здоровья
- Где в коде: конкретный файл и функция, что в них менять
- Как: конкретные шаги реализации
- Сложность: легко (1 час) / средне (полдня) / сложно (день+)

ПРАВИЛА:
- Только то, чего реально нет в прочитанном коде
- Привязывай к конкретным файлам и функциям
- VPS 2CPU/2GB RAM — учитывай ограничения
- Если ничего полезного не нашлось — так и скажи, не выдумывай
{dedup_block}
Формат: plain text, без markdown. На русском языке.
Начни с краткого заголовка: "Скаут улучшений: [тема дня]"."""

    log.info("Running feature scout: %s", query)
    return _call_claude(prompt, timeout=3600)


# ── Telegram ─────────────────────────────────────────────────────────

async def _send_to_telegram(text):
    """Send text to Telegram, splitting if needed."""
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    for i in range(0, len(text), 4096):
        await bot.send_message(chat_id=TELEGRAM_TARGET_USER_ID, text=text[i:i + 4096])


# ── Main ─────────────────────────────────────────────────────────────

def main():
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_TARGET_USER_ID:
        log.error("Telegram credentials not set.")
        return

    _ensure_log_table()

    # Support --mode override for testing
    import sys
    mode = None
    for arg in sys.argv[1:]:
        if arg.startswith("--mode"):
            # Handle --mode=X and --mode X
            if "=" in arg:
                mode = arg.split("=", 1)[1]
            else:
                idx = sys.argv.index(arg)
                if idx + 1 < len(sys.argv):
                    mode = sys.argv[idx + 1]
    if not mode:
        mode = _get_today_mode()

    log.info("Mode: %s", mode)

    if mode == "code_review":
        result = _run_code_review()
    else:
        query = _get_today_query()
        result = _run_feature_scout(query)

    if not result or len(result) < 100:
        log.warning("Claude returned no useful analysis (%d chars).",
                    len(result) if result else 0)
        return

    header = "CODE REVIEW" if mode == "code_review" else "FEATURE SCOUT"
    text = f"{header} ({datetime.now().strftime('%d.%m.%Y')})\n\n{result}"

    log.info("Analysis ready (%d chars). Sending to Telegram...", len(text))
    asyncio.run(_send_to_telegram(text))

    _save_to_log(mode, text)
    log.info("Done! Saved to log.")


if __name__ == "__main__":
    main()
