#!/usr/bin/env python3
"""
Telegram Bot: Slash Command Handler

Handles /brief, /query, /files, /cc, /newchat, /tasks, /status, /compact commands.
The AI text handler already covers these via natural language,
but slash commands are faster for known actions.

/newchat — resets conversation context (starts fresh)
/cc — proxies a prompt to Claude Code CLI
/tasks — shows pending tasks grouped by due date
"""

import os
import sys
import asyncio
import subprocess
import logging
from telegram import Update
from telegram.ext import ContextTypes

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common import get_openai_client, call_gpt, MODEL_FAST

from task_handler import _send_outbox_files, _call_gpt, _get_openai_client, _smart_split
from bot_memory import (
    clear_history, add_to_history, get_history, get_history_count,
    get_memory_count, list_memories_with_ids, delete_memory, MAX_HISTORY,
)
from skills_menu import _get_tasks_list_with_ids, _build_task_done_buttons
from utils import run_claude_code, run_claude_code_product
from scheduler import list_pending, cancel_reminder, format_reminder_list
from tts import text_to_voice, LANG_VOICES, LANG_NAMES

logger = logging.getLogger(__name__)

import time as _time_mod
_BOT_START_TIME = _time_mod.time()

# Base directory for all scripts
BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "..")

DB_FILE = os.path.join(BASE_DIR, "data", "aios_data.db")


def _get_dashboard():
    """Returns key Product metrics from the latest snapshot — no LLM call, instant."""
    import sqlite3
    if not os.path.exists(DB_FILE):
        return "База данных не найдена."
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Check metrics table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='metrics'")
        if not cursor.fetchone():
            return "Таблица metrics не создана. Сначала нужен data_snapshot."

        # Get latest Product snapshot
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
        if not rows:
            return "Метрики Product ещё не собраны."

        d = {name: value for name, value in rows}

        # Get snapshot timestamp
        cursor.execute("""
            SELECT date FROM metrics WHERE source = 'Product'
            ORDER BY date DESC LIMIT 1
        """)
        ts_row = cursor.fetchone()
        snapshot_time = ts_row[0][:16].replace("T", " ") if ts_row else "?"

        def i(k): return int(d.get(k, 0))
        def f(k): return d.get(k, 0)

        lines = [
            f"DASHBOARD (снимок от {snapshot_time})\n",
            f"Выручка сегодня: {f('revenue_today'):,.0f} R",
            f"Выручка за месяц: {f('revenue_month'):,.0f} R",
            f"MRR: {f('mrr'):,.0f} R",
            f"Средний чек: {f('avg_check_month'):,.0f} R",
            "",
            f"Пользователей всего: {i('users_total')}",
            f"Новых за месяц: {i('users_new_month')}",
            f"Клиентов: {i('clients_total')}",
            f"Новых клиентов: {i('clients_new_month')}",
            "",
            f"Консультаций проведено: {i('funnel_month_completed')}",
            f"Заявки ожидают: {i('funnel_month_pending_specialist')}",
            f"Отмены: {i('funnel_month_cancelled')} | Неявки: {i('funnel_month_no_show')}",
            f"Skip rate: {f('skip_rate_month'):.1f}%",
            "",
            f"Диагностик завершено: {i('assessments_completed_month')}",
            f"Специалистов активных: {i('specialists_active')}",
            f"Повторных клиентов: {i('repeat_clients')}",
        ]
        return "\n".join(lines)
    except Exception as e:
        return f"Ошибка: {e}"
    finally:
        if conn:
            conn.close()


async def handle_slash_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Executes the appropriate script based on the slash command."""
    # Support commands in both text and photo captions
    raw_text = update.message.text or update.message.caption or ""
    if not raw_text:
        return
    parts = raw_text.split(" ", 1)
    command = parts[0][1:].split("@")[0]  # Remove the slash and @botname
    args_text = parts[1].strip() if len(parts) > 1 else ""
    user_id = update.effective_user.id

    if command == "brief":
        await update.message.chat.send_action("typing")
        loop = asyncio.get_running_loop()
        script = os.path.join(BASE_DIR, "execution", "daily_brief", "brief_generator.py")
        result = await loop.run_in_executor(None, _run_script, script, None)
        add_to_history(user_id, "user", "/brief")
        add_to_history(user_id, "assistant", result[:2000])
        for chunk in _smart_split(result):
            await update.message.reply_text(chunk)

    elif command == "query":
        if not args_text:
            await update.message.reply_text(
                "Использование: /query <вопрос>\nПример: /query какой MRR за прошлый месяц?"
            )
            return
        await update.message.chat.send_action("typing")
        loop = asyncio.get_running_loop()
        script = os.path.join(BASE_DIR, "execution", "data_os", "query.py")
        result = await loop.run_in_executor(None, _run_script, script, [args_text])
        add_to_history(user_id, "user", f"/query {args_text}")
        add_to_history(user_id, "assistant", result[:2000])
        for chunk in _smart_split(result):
            await update.message.reply_text(chunk)

    elif command == "files":
        await _send_outbox_files(update)

    elif command == "newchat":
        clear_history(user_id)
        await update.message.reply_text("Контекст очищен. Начинаем с чистого листа.")
        return

    elif command == "status":
        hist_count = get_history_count(user_id)
        mem_count = get_memory_count(user_id)
        import platform

        # Task stats
        task_info = ""
        try:
            import sqlite3
            db_file = os.path.join(BASE_DIR, "data", "aios_data.db")
            if os.path.exists(db_file):
                conn = sqlite3.connect(db_file)
                c = conn.cursor()
                c.execute("SELECT COUNT(*) FROM tasks WHERE status IN ('pending','reminded')")
                pending = c.fetchone()[0]
                c.execute("SELECT COUNT(*) FROM tasks WHERE status='done'")
                done = c.fetchone()[0]
                conn.close()
                task_info = f"Задачи: {pending} активных, {done} выполненных"
                # DB size
                db_size = round(os.path.getsize(db_file) / 1024, 1)
                task_info += f"\nБаза данных: {db_size} КБ"
        except Exception:
            task_info = "Задачи: н/д"

        # Uptime (process start time)
        uptime_str = ""
        try:
            import time
            uptime_sec = time.time() - _BOT_START_TIME
            hours = int(uptime_sec // 3600)
            mins = int((uptime_sec % 3600) // 60)
            if hours > 0:
                uptime_str = f"Аптайм: {hours}ч {mins}м"
            else:
                uptime_str = f"Аптайм: {mins}м"
        except Exception:
            pass

        lines = [
            "AIOS Status",
            "",
            "Модели:",
            "  Chat: GPT-5.4 (function calling)",
            "  Vision: GPT-4o",
            "  Memory: GPT-4o-mini",
            "  Voice: Whisper (OpenAI)",
            "",
            f"История: {hist_count}/{MAX_HISTORY} сообщений",
            f"Долговременная память: {mem_count} фактов",
            task_info,
            "",
            uptime_str,
            f"Python {platform.python_version()} / {platform.system()}",
        ]
        # Remove empty lines at the end
        lines = [l for l in lines if l or l == ""]
        await update.message.reply_text("\n".join(lines))
        return

    elif command == "compact":
        # Summarize long history to save context window
        history = get_history(user_id)
        if len(history) < 10:
            await update.message.reply_text(
                f"История короткая ({len(history)} сообщений), сжатие не нужно."
            )
            return
        await update.message.chat.send_action("typing")
        # Build summary prompt
        conv_text = "\n".join(
            f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content'][:300]}"
            for m in history
        )
        summary_prompt = (
            "Summarize this conversation in 5-10 bullet points in Russian. "
            "Keep key facts, decisions, and context. Drop small talk.\n\n"
            f"{conv_text[:10000]}"
        )
        try:
            client = _get_openai_client()
            loop = asyncio.get_running_loop()
            resp = await loop.run_in_executor(
                None,
                lambda: client.chat.completions.create(
                    model=MODEL_FAST,
                    max_completion_tokens=500,
                    messages=[{"role": "user", "content": summary_prompt}],
                ),
            )
            summary = (resp.choices[0].message.content or "").strip()
            # Clear history and inject summary
            clear_history(user_id)
            add_to_history(user_id, "assistant", f"[Сводка предыдущего разговора]\n{summary}")
            await update.message.reply_text(
                f"История сжата ({len(history)} -> 1 сообщение).\n\n{summary}"
            )
        except Exception as e:
            logger.error(f"/compact error: {e}")
            await update.message.reply_text(f"Ошибка сжатия: {e}")
        return

    elif command == "tasks":
        result, task_ids = _get_tasks_list_with_ids()
        for chunk in _smart_split(result):
            await update.message.reply_text(chunk)
        if task_ids:
            await update.message.reply_text(
                "Отметить выполненную:",
                reply_markup=_build_task_done_buttons(task_ids),
            )

    elif command == "memory":
        memories = list_memories_with_ids(user_id)
        if not memories:
            await update.message.reply_text(
                "Долговременная память пуста.\n\n"
                "Я автоматически запоминаю важные факты из разговоров "
                "(имена, предпочтения, контекст)."
            )
            return
        lines = [f"Долговременная память ({len(memories)} фактов):\n"]
        for m in memories:
            date_str = m["created_at"][:10] if m.get("created_at") else ""
            lines.append(f"  [{m['id']}] {m['memory']}  ({date_str})")
        lines.append(f"\nУдалить: /forget <id>")
        result = "\n".join(lines)
        for chunk in _smart_split(result):
            await update.message.reply_text(chunk)
        return

    elif command == "forget":
        if not args_text:
            await update.message.reply_text("Использование: /forget <id>\nСначала посмотри /memory")
            return
        try:
            mem_id = int(args_text.strip())
            delete_memory(user_id, mem_id)
            await update.message.reply_text(f"Память #{mem_id} удалена.")
        except ValueError:
            await update.message.reply_text("ID должен быть числом. Посмотри /memory")
        return

    elif command == "reminders":
        reminders = list_pending(user_id)
        text = format_reminder_list(reminders)
        if reminders:
            text += "\n\nОтменить: /cancel <id>"
        await update.message.reply_text(text)
        return

    elif command == "cancel":
        if not args_text:
            await update.message.reply_text("Использование: /cancel <id>\nСначала посмотри /reminders")
            return
        try:
            rid = int(args_text.strip())
            if cancel_reminder(rid, user_id):
                await update.message.reply_text(f"Напоминание #{rid} отменено.")
            else:
                await update.message.reply_text(f"Напоминание #{rid} не найдено или уже выполнено.")
        except ValueError:
            await update.message.reply_text("ID должен быть числом.")
        return

    elif command == "translate" or command == "tr":
        if not args_text:
            langs = ", ".join(sorted(LANG_VOICES.keys()))
            await update.message.reply_text(
                "Использование: /translate <язык> <текст>\n"
                "Или: /tr <язык> <текст>\n\n"
                "Примеры:\n"
                "/tr tr Здравствуйте, сколько это стоит?\n"
                "/tr en Мне нужен номер на две ночи\n"
                "/tr es Где ближайшая аптека?\n\n"
                f"Языки: {langs}"
            )
            return

        parts = args_text.split(None, 1)
        if len(parts) < 2:
            await update.message.reply_text("Укажи язык и текст: /tr en Привет!")
            return

        lang_code = parts[0].lower()
        source_text = parts[1]

        if lang_code not in LANG_VOICES:
            langs = ", ".join(sorted(LANG_VOICES.keys()))
            await update.message.reply_text(f"Язык '{lang_code}' не поддерживается.\nДоступные: {langs}")
            return

        # Translate via GPT (with retry, in executor to avoid blocking)
        target_lang = LANG_NAMES.get(lang_code, lang_code)
        messages = [{
            "role": "system",
            "content": f"Translate the following text to {target_lang}. "
                       "Return ONLY the translation, nothing else."
        }, {
            "role": "user",
            "content": source_text,
        }]

        try:
            loop = asyncio.get_running_loop()
            tr_msg = await loop.run_in_executor(
                None, lambda: call_gpt(messages, model=MODEL_FAST, max_tokens=1024)
            )
            translated = tr_msg.content.strip()
        except Exception as e:
            logger.error(f"Translation GPT error: {e}")
            await update.message.reply_text("Не удалось перевести. Попробуй ещё раз.")
            return

        # Send text translation
        await update.message.reply_text(f"🗣 {translated}")

        # Send voice message in target language
        voice_path = await text_to_voice(translated, voice=lang_code)
        if voice_path:
            try:
                with open(voice_path, "rb") as f:
                    await update.message.reply_voice(voice=f)
            finally:
                try:
                    os.remove(voice_path)
                except OSError:
                    pass
        else:
            await update.message.reply_text("(не удалось озвучить)")
        return

    elif command == "help":
        help_text = (
            "AIOS — твой персональный AI-ассистент\n\n"
            "Что я умею:\n"
            "- Отвечать на вопросы и вести беседу\n"
            "- Записывать задачи (скажи 'запиши', 'напомни', 'добавь задачу')\n"
            "- Генерировать утренний брифинг\n"
            "- Искать бизнес-метрики и данные\n"
            "- Работать с почтой через Claude Code\n"
            "- Искать и анализировать записи встреч (Fireflies)\n"
            "- Анализировать фото и скриншоты\n"
            "- Расшифровывать голосовые сообщения\n"
            "- Запоминать важные факты о тебе\n\n"
            "Команды:\n"
            "/brief — утренний брифинг\n"
            "/dashboard — ключевые метрики (мгновенно, без AI)\n"
            "/query <вопрос> — запрос данных через AI\n"
            "/search <запрос> — поиск в интернете\n"
            "/tasks — список задач\n"
            "/reminders — активные напоминания\n"
            "/cancel <id> — отменить напоминание\n"
            "/cc <запрос> — выполнить через Claude Code\n"
            "/bal <запрос> — правки в коде Product\n"
            "/files — файлы из outbox\n"
            "/skills — меню быстрых действий\n"
            "/memory — посмотреть что я помню\n"
            "/forget <id> — удалить факт из памяти\n"
            "/tr <язык> <текст> — перевести и озвучить\n"
            "/voice — вкл/выкл голосовые ответы\n"
            "/compact — сжать историю (экономит контекст)\n"
            "/status — статус бота\n"
            "/newchat — очистить контекст\n"
            "/help — эта справка"
        )
        await update.message.reply_text(help_text)
        return

    elif command == "cc":
        if not args_text:
            await update.message.reply_text(
                "Использование: /cc <запрос>\n\n"
                "Примеры:\n"
                "/cc проверь мою почту\n"
                "/cc отправь письмо на test@example.com с темой Привет\n"
                "/cc создай презентацию о продукте"
            )
            return
        # Enrich with photo analysis if present
        photo_analysis = context.user_data.pop("_photo_analysis", None)
        if photo_analysis:
            args_text = f"{args_text}\n\nСКРИНШОТ (описание):\n{photo_analysis}"
        await update.message.reply_text("⏳ Работаю...")
        await update.message.chat.send_action("typing")
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, run_claude_code, args_text)
        add_to_history(user_id, "user", f"/cc {args_text[:500]}")
        add_to_history(user_id, "assistant", result[:2000])
        for chunk in _smart_split(result):
            await update.message.reply_text(chunk)

    elif command == "bal":
        if not args_text:
            await update.message.reply_text(
                "Использование: /bal <запрос>\n\n"
                "Claude Code внесёт правки в отдельной ветке.\n"
                "Ты получишь ссылку на PR для ревью.\n\n"
                "Примеры:\n"
                "/bal исправь баг в компоненте авторизации\n"
                "/bal добавь валидацию email в форме регистрации\n"
                "/bal найди все TODO в коде и покажи список"
            )
            return
        try:
            # Enrich with photo analysis if present (screenshot of a bug etc.)
            photo_analysis = context.user_data.pop("_photo_analysis", None)
            if photo_analysis:
                args_text = f"{args_text}\n\nСКРИНШОТ (описание от GPT-4o Vision):\n{photo_analysis}"
                await update.message.reply_text("⏳ Скриншот проанализирован. Работаю над Product кодом...")
            else:
                await update.message.reply_text("⏳ Работаю над Product кодом...")
            await update.message.chat.send_action("typing")
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, run_claude_code_product, args_text)
            add_to_history(user_id, "user", f"/bal {args_text[:500]}")
            add_to_history(user_id, "assistant", result[:2000])
            for chunk in _smart_split(result):
                await update.message.reply_text(chunk)
        except Exception as e:
            logger.error(f"/bal error: {e}")
            await update.message.reply_text(f"Ошибка /bal: {e}")

    elif command == "dashboard":
        await update.message.chat.send_action("typing")
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, _get_dashboard)
        for chunk in _smart_split(result):
            await update.message.reply_text(chunk)
        return

    elif command == "voice":
        # Toggle voice mode: bot replies with audio messages
        current = context.user_data.get("voice_mode", False)
        context.user_data["voice_mode"] = not current
        # Force persistence flush so voice_mode survives bot restarts
        if context.application.persistence:
            await context.application.update_persistence()
        if not current:
            await update.message.reply_text("Голосовой режим включён. Теперь я буду отвечать аудио.")
        else:
            await update.message.reply_text("Голосовой режим выключен.")
        return

    elif command == "search":
        if not args_text:
            await update.message.reply_text("Использование: /search <запрос>")
            return
        await update.message.chat.send_action("typing")
        from utils import web_search
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, web_search, args_text, 5)
        add_to_history(user_id, "user", f"/search {args_text}")
        add_to_history(user_id, "assistant", result[:2000])
        for chunk in _smart_split(result):
            await update.message.reply_text(chunk)

    else:
        await update.message.reply_text(
            "Доступные команды:\n"
            "/brief — сгенерировать брифинг\n"
            "/query <вопрос> — запрос данных\n"
            "/dashboard — ключевые метрики (без AI)\n"
            "/search <запрос> — поиск в интернете\n"
            "/tasks — список задач\n"
            "/files — проверить outbox и получить файлы\n"
            "/cc <запрос> — выполнить через Claude Code\n"
            "/bal <запрос> — правки в Product коде\n"
            "/skills — меню быстрых действий\n"
            "/memory — что я помню о тебе\n"
            "/forget <id> — удалить факт из памяти\n"
            "/voice — вкл/выкл голосовые ответы\n"
            "/status — статус бота\n"
            "/compact — сжать историю\n"
            "/newchat — очистить контекст\n"
            "/help — полная справка"
        )


def _run_script(script_path, args=None):
    """Runs a Python script and returns its output."""
    try:
        cmd = [sys.executable, script_path] + (args or [])
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            env={**os.environ},
        )
        if result.stdout:
            return result.stdout
        if result.stderr:
            return f"Ошибка: {result.stderr[:2000]}"
        return "Скрипт выполнен, но не вернул результат."
    except subprocess.TimeoutExpired:
        return "Таймаут — скрипт работал дольше 5 минут."
    except Exception as e:
        logger.error(f"Script error: {e}")
        return f"Ошибка: {e}"
