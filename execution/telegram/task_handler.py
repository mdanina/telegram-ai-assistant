#!/usr/bin/env python3
"""
Telegram Bot: AI Assistant Handler

Main message handler powered by GPT-5 with function calling.
Routes user messages through AI, which can call tools for tasks,
briefings, data queries, file operations, and Claude Code.
"""

import os
import sys
import glob
import json
import time
import hashlib
import shutil
import asyncio
import subprocess
import logging
from datetime import datetime, timedelta, timezone

# Add execution/ to path for common module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common import get_openai_client, call_gpt, MODEL_MAIN, MODEL_FAST

# Moscow timezone (UTC+3)
_MSK = timezone(timedelta(hours=3))

# ── Cross-message task deduplication ──────────────────────────────
# Prevents duplicate tasks when user sends same message twice quickly
_recent_tasks = {}  # {hash: timestamp}
_DEDUP_WINDOW = 60  # seconds
from telegram import Update
from telegram.ext import ContextTypes

from bot_memory import (
    get_history, add_to_history, clear_history,
    get_memories_formatted, save_memory, MEMORY_EXTRACTION_PROMPT,
    get_history_count,
)
from utils import run_claude_code, search_fireflies_meetings, analyze_fireflies_meeting, web_search, crawl_page
from tts import text_to_voice, LANG_VOICES, LANG_NAMES
from scheduler import create_reminder, parse_fire_at, parse_repeat

# Outbox directory — files placed here get sent to user via Telegram
OUTBOX_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "outbox")
DOCUMENTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "documents")

# Auto-categorize files by name keywords → subfolder
_FILE_CATEGORIES = {
    "contracts": ("договор", "контракт", "contract", "соглашени", "nda"),
    "invoices": ("счёт", "счет", "invoice", "оплат"),
    "accounting": ("акт", "бухгалтер", "accounting", "налог", "усн", "ндфл"),
    "reports": ("отчёт", "отчет", "report", "аналитик", "brief"),
}


def _categorize_file(filename: str) -> str:
    """Determine category subfolder based on filename keywords."""
    name_lower = filename.lower()
    for category, keywords in _FILE_CATEGORIES.items():
        if any(kw in name_lower for kw in keywords):
            return category
    return "other"

logger = logging.getLogger(__name__)

# ── OpenAI client — delegates to common singleton ─────────────────────
def _get_openai_client():
    """Returns the shared OpenAI client from common module."""
    return get_openai_client()


# ── OpenAI Function Calling Tools ──────────────────────────────────────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": (
                "Create a GTD task ONLY when user uses explicit task language: "
                "'запиши', 'добавь задачу', 'напомни', 'нужно сделать', "
                "'поставь задачу', 'не забудь'. "
                "NEVER call this for: questions, requests for information, "
                "greetings, follow-ups, complaints, or conversation. "
                "If uncertain — do NOT call this tool, just respond in text. "
                "IMPORTANT: pass the user's message VERBATIM as task_text."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "task_text": {
                        "type": "string",
                        "description": (
                            "The user's original message text, copied verbatim. "
                            "Do NOT rephrase or reinterpret."
                        ),
                    }
                },
                "required": ["task_text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_brief",
            "description": (
                "Generate a daily intelligence briefing/report. Use when user "
                "asks for morning brief, daily report, or summary."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_data",
            "description": (
                "Query business metrics, numbers, or statistics "
                "(MRR, users, revenue, analytics)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query_text": {
                        "type": "string",
                        "description": "The data question to look up",
                    }
                },
                "required": ["query_text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_files",
            "description": (
                "ALWAYS use when user asks to send, share, or deliver a file, document, "
                "contract, or attachment. Checks data/outbox/ and sends matching files. "
                "Triggers: 'пришли файл', 'скинь документ', 'отправь договор', 'send file'. "
                "After sending, files are auto-archived to documents/<category>/."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Optional: part of filename to filter (e.g. 'Папина', 'договор'). Empty = send all.",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_claude_code",
            "description": (
                "Delegate complex tasks to Claude Code CLI on the server: "
                "email (Gmail read/send), file generation "
                "(documents, reports, spreadsheets), document processing "
                "(translate, summarize, analyze, rewrite), code changes. "
                "Use when user needs an ACTION performed, not just information. "
                "Google Calendar is NOT available."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": (
                            "Task prompt in English, regardless of "
                            "conversation language"
                        ),
                    }
                },
                "required": ["prompt"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_meetings",
            "description": (
                "Search recent meetings in Fireflies.ai. Returns list of meetings "
                "with titles, dates, participants, summary, and action items. "
                "Use when user asks about meetings, calls, or wants to find a specific meeting."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {
                        "type": "integer",
                        "description": "How many days back to search (default 7)",
                    },
                    "keyword": {
                        "type": "string",
                        "description": (
                            "Optional keyword to filter meetings "
                            "(name, topic, participant)"
                        ),
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_meeting",
            "description": (
                "Get detailed analysis of a specific meeting transcript. "
                "Fetches full transcript from Fireflies and produces a structured "
                "analysis: topics, decisions, action items, risks. "
                "Requires meeting_id from search_meetings results."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "meeting_id": {
                        "type": "string",
                        "description": "Fireflies transcript ID from search results",
                    },
                    "question": {
                        "type": "string",
                        "description": (
                            "Optional specific question about the meeting "
                            "(e.g. 'что решили по ценообразованию?')"
                        ),
                    },
                },
                "required": ["meeting_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_reminder",
            "description": (
                "Set a reminder or recurring notification. Use when user says "
                "'напомни через...', 'remind me in...', 'через 2 часа напомни', "
                "'каждый день в 9:00'. For one-time reminders provide 'when', "
                "for recurring also provide 'every'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "What to remind about",
                    },
                    "when": {
                        "type": "string",
                        "description": (
                            "When to fire: relative (+30m, 2h, 1d), "
                            "time today (14:00), or ISO (2026-03-20T14:00)"
                        ),
                    },
                    "every": {
                        "type": "string",
                        "description": (
                            "Repeat interval (optional): 30m, 2h, 1d. "
                            "Omit for one-time reminders."
                        ),
                    },
                },
                "required": ["text", "when"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "Search the internet using Brave Search. Use when user asks to "
                "find information online, research a topic, look up current events, "
                "find articles, check facts, or needs any information from the web. "
                "Keywords: 'найди', 'поищи', 'загугли', 'что пишут', 'новости', "
                "'search', 'look up', 'find online'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query in the most effective language for the topic",
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of results (default 5, max 10)",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "translate_and_speak",
            "description": (
                "ALWAYS use this tool when user asks to translate, say something in "
                "another language, or mentions 'переведи', 'скажи по-', 'как будет на'. "
                "This tool sends both text AND audio voice message — do NOT translate "
                "in plain text, ALWAYS call this tool instead. "
                "Supported: " + ", ".join(sorted(LANG_NAMES.values()))
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to translate (in the original language)",
                    },
                    "target_language": {
                        "type": "string",
                        "enum": list(LANG_VOICES.keys()),
                        "description": "Target language code (e.g. 'tr', 'en', 'es')",
                    },
                },
                "required": ["text", "target_language"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "crawl_page",
            "description": (
                "Read and extract text content from a web page URL. Use when user "
                "sends a link and wants to read it, summarize an article, extract "
                "information from a specific page, or when you need to read a page "
                "found via web_search. Returns clean markdown text."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Full URL of the page to read",
                    },
                },
                "required": ["url"],
            },
        },
    },
]


# ── System prompt (with cached business context) ─────────────────────────

_context_cache = {"text": None, "loaded_at": 0}
_CONTEXT_TTL = 3600  # reload from disk every 1 hour


def _load_business_context():
    """Loads business context files with 1-hour in-memory cache."""
    import time

    now = time.time()
    if _context_cache["text"] and (now - _context_cache["loaded_at"]) < _CONTEXT_TTL:
        return _context_cache["text"]

    context = ""
    context_dir = os.path.join(os.path.dirname(__file__), "..", "..", "context")
    if not os.path.exists(context_dir):
        return "No business context available."
    for filename in sorted(os.listdir(context_dir)):
        if filename.endswith(".md"):
            with open(os.path.join(context_dir, filename), "r") as f:
                context += f"\n\n--- {filename} ---\n\n" + f.read()

    _context_cache["text"] = context
    _context_cache["loaded_at"] = now
    logger.info("Business context reloaded from disk")
    return context


def _get_system_prompt(user_id: int = None, user_message: str = None):
    """Returns the system prompt for the AI assistant."""
    business_context = _load_business_context()
    now = datetime.now(_MSK).replace(tzinfo=None)
    today = now.strftime("%A, %B %d, %Y")
    current_time = now.strftime("%H:%M")
    hour = now.hour

    memory_block = ""
    if user_id:
        memory_block = get_memories_formatted(user_id, context_query=user_message)
        if memory_block:
            memory_block = "\n\n" + memory_block

    # Load soul (personality) from context/soul.md
    soul = ""
    soul_path = os.path.join(os.path.dirname(__file__), "..", "..", "context", "soul.md")
    try:
        with open(soul_path, "r", encoding="utf-8") as f:
            soul = f.read().strip()
    except FileNotFoundError:
        soul = "You are Nikitka — a male AI assistant. Use masculine forms in Russian."

    return (
        f"{soul}\n\n"
        f"You communicate via Telegram. Today is {today}, current time: {current_time} (hour: {hour}).\n\n"
        f"CONTEXT ABOUT INCOMING MESSAGES:\n"
        f"- [Голосовое: ...] = transcribed voice note\n"
        f"- [Фото: ...] = analyzed photo (Vision AI)\n"
        f"- [Переслано ...] = forwarded message\n"
        f"- [Контекст: пользователь отправил файл ...] = recently uploaded file\n\n"
        f"BUSINESS CONTEXT:\n{business_context}{memory_block}\n\n"
        f"INTENT CLASSIFICATION (follow strictly):\n"
        f"Your DEFAULT mode is CONVERSATION. Only use tools when clearly needed.\n\n"
        f"create_task — ONLY when user uses explicit task words:\n"
        f"  YES: 'запиши', 'добавь задачу', 'напомни', 'нужно сделать', "
        f"'поставь задачу', 'не забудь', 'запланируй'\n"
        f"  YES: events/reminders with specific dates\n"
        f"  NO: requests for info, questions, complaints, follow-ups, greetings\n"
        f"  RULE: if in doubt — respond in text, do NOT create a task\n"
        f"  RULE: when creating a task, ALWAYS ask the user for a due date if "
        f"they didn't specify one. Say: 'Записал. Когда нужно сделать?' "
        f"This is critical — tasks without deadlines get lost.\n\n"
        f"query_data — business metrics, numbers, statistics\n"
        f"search_meetings / analyze_meeting — Fireflies.ai recordings\n"
        f"run_claude_code — email (Gmail), file processing, "
        f"document generation, translations, complex server actions\n"
        f"generate_brief — daily briefing report\n"
        f"send_files — ALWAYS use when user says 'пришли файл', 'скинь документ', "
        f"'отправь договор', 'send file'. Sends files from data/outbox/. "
        f"Do NOT use run_claude_code for sending files.\n"
        f"set_reminder — set a timed reminder ('напомни через 2 часа', "
        f"'remind me at 14:00'). Use INSTEAD of create_task when user wants "
        f"a time-based notification, not a persistent task.\n"
        f"web_search — search the internet (Brave Search). Use for any question "
        f"that needs current/external information\n"
        f"crawl_page — read and extract text from a web page URL\n"
        f"translate_and_speak — ALWAYS use when user asks to translate or say "
        f"something in another language. NEVER translate in plain text — this tool "
        f"sends both text translation AND audio voice message.\n"
    )


# ── Action executors ───────────────────────────────────────────────────────

def _format_due_date(date_str):
    """Formats YYYY-MM-DD or YYYY-MM-DD HH:MM to a human-friendly Russian string."""
    weekdays = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]
    months = [
        "янв", "фев", "мар", "апр", "мая", "июн",
        "июл", "авг", "сен", "окт", "ноя", "дек",
    ]
    try:
        if " " in date_str:
            dt = datetime.strptime(date_str.strip(), "%Y-%m-%d %H:%M")
            return f"{weekdays[dt.weekday()]}, {dt.day} {months[dt.month - 1]} в {dt.strftime('%H:%M')}"
        else:
            dt = datetime.strptime(date_str.strip(), "%Y-%m-%d")
            return f"{weekdays[dt.weekday()]}, {dt.day} {months[dt.month - 1]}"
    except (ValueError, IndexError):
        return date_str


def _run_gtd_processor(task_text):
    """Runs the GTD processor on a task and returns a formatted result."""
    try:
        script_path = os.path.join(
            os.path.dirname(__file__), "..", "task_os", "gtd_processor.py"
        )
        result = subprocess.run(
            [sys.executable, script_path, task_text],
            capture_output=True, text=True, timeout=60, env={**os.environ},
        )
        output = result.stdout.strip() if result.stdout else ""
        if not output:
            return None

        try:
            for line in output.split("\n"):
                line = line.strip()
                if line.startswith("{"):
                    task = json.loads(line)
                    # If all meaningful fields are null — not a real task
                    if not any(task.get(f) for f in (
                        "next_action", "project", "delegated_to", "due_date",
                    )):
                        return None
                    parts = []
                    # Main action — the task itself (no label needed)
                    action = (task.get("next_action") or "").strip()
                    if action:
                        parts.append(action)
                    if task.get("project"):
                        parts.append(f"Проект: {task['project']}")
                    if task.get("delegated_to"):
                        parts.append(f"Кому: {task['delegated_to']}")
                    if task.get("due_date"):
                        parts.append(f"Срок: {_format_due_date(task['due_date'])}")
                    if task.get("is_someday_maybe"):
                        parts.append("(когда-нибудь)")
                    return "\n".join(parts) if parts else None
        except (json.JSONDecodeError, KeyError):
            pass

        return output
    except Exception as e:
        logger.error(f"GTD processor error: {e}")
        return None


def _run_brief_generator():
    """Runs the daily brief generator and returns the result."""
    try:
        script_path = os.path.join(
            os.path.dirname(__file__), "..", "daily_brief", "brief_generator.py"
        )
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True, text=True, timeout=300, env={**os.environ},
        )
        if result.stdout and result.stdout.strip():
            return result.stdout
        stderr = result.stderr.strip() if result.stderr else ""
        logger.error(
            f"Brief generator no output. rc={result.returncode} stderr={stderr[:500]}"
        )
        if stderr:
            return f"Ошибка генерации брифа:\n{stderr[:1000]}"
        return "Не удалось сгенерировать бриф."
    except subprocess.TimeoutExpired:
        return "Таймаут: генерация брифа заняла больше 5 минут."
    except Exception as e:
        logger.error(f"Brief generator error: {e}")
        return f"Ошибка: {e}"


def _run_data_query(query_text):
    """Runs a natural language query against the Data OS."""
    try:
        script_path = os.path.join(
            os.path.dirname(__file__), "..", "data_os", "query.py"
        )
        result = subprocess.run(
            [sys.executable, script_path, query_text],
            capture_output=True, text=True, timeout=60, env={**os.environ},
        )
        return result.stdout if result.stdout else "Данные не найдены."
    except Exception as e:
        logger.error(f"Data query error: {e}")
        return f"Ошибка: {e}"


async def _send_outbox_files(update: Update, filename_filter: str = ""):
    """Send files from outbox, optionally filtered by name. After sending, archive to documents/."""
    os.makedirs(OUTBOX_DIR, exist_ok=True)
    files = sorted(glob.glob(os.path.join(OUTBOX_DIR, "*")))
    if not files:
        await update.message.reply_text("Outbox пуст — нет файлов для отправки.")
        return

    # Filter by filename if specified
    if filename_filter:
        filter_lower = filename_filter.lower()
        files = [f for f in files if filter_lower in os.path.basename(f).lower()]
        if not files:
            # List available files
            all_files = sorted(glob.glob(os.path.join(OUTBOX_DIR, "*")))
            names = [os.path.basename(f) for f in all_files if os.path.isfile(f)]
            if names:
                listing = "\n".join(f"- {n}" for n in names)
                await update.message.reply_text(f"Не нашёл '{filename_filter}'. Доступные файлы:\n{listing}")
            else:
                await update.message.reply_text("Outbox пуст.")
            return

    sent_count = 0
    for file_path in files:
        if not os.path.isfile(file_path):
            continue
        try:
            with open(file_path, "rb") as f:
                await update.message.reply_document(
                    document=f, filename=os.path.basename(file_path),
                )
            sent_count += 1
            # Archive: move to documents/<category>/
            basename = os.path.basename(file_path)
            category = _categorize_file(basename)
            archive_dir = os.path.join(DOCUMENTS_DIR, category)
            os.makedirs(archive_dir, exist_ok=True)
            archive_path = os.path.join(archive_dir, basename)
            # Handle duplicates
            if os.path.exists(archive_path):
                name, ext = os.path.splitext(basename)
                archive_path = os.path.join(archive_dir, f"{name}_{int(time.time())}{ext}")
            shutil.move(file_path, archive_path)
            logger.info(f"Sent and archived: {file_path} -> {archive_path}")
        except Exception as e:
            logger.error(f"Failed to send file {file_path}: {e}")
            await update.message.reply_text(f"Не удалось отправить {os.path.basename(file_path)}")

    if sent_count:
        await update.message.reply_text(f"Отправлено: {sent_count} файл(ов).")


# ── GPT call with retry (delegates to common.call_gpt) ───────────────────

def _call_gpt(client, messages, tools=None):
    """Calls GPT with retry on transient errors. Returns the message object.

    The `client` arg is kept for backward compatibility but ignored —
    uses the common singleton internally.
    """
    return call_gpt(messages, tools=tools, model=MODEL_MAIN)


# ── Typing indicator ──────────────────────────────────────────────────────

async def _keep_typing(chat, stop_event: asyncio.Event):
    """Refreshes the Telegram typing indicator every 4s until stopped."""
    try:
        while not stop_event.is_set():
            await chat.send_action("typing")
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=4.0)
            except asyncio.TimeoutError:
                pass
    except Exception:
        pass


# ── Memory extraction ─────────────────────────────────────────────────────

def _extract_and_save_memories(client, user_id, user_text, assistant_text):
    """Asks GPT to extract memorable facts. Uses cheap model."""
    prompt = MEMORY_EXTRACTION_PROMPT.format(
        user_message=user_text[:500],
        assistant_response=assistant_text[:500],
    )
    try:
        resp = client.chat.completions.create(
            model=MODEL_FAST,
            max_completion_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        result = (resp.choices[0].message.content or "").strip()
        if not result or result.upper() == "NONE":
            return
        for line in result.split("\n"):
            line = line.strip().lstrip("-•").strip()
            if line and len(line) > 3:
                save_memory(user_id, line, source_message=user_text[:200])
    except Exception as e:
        logger.warning(f"Memory extraction failed: {e}")


# ── Ack reactions (OpenClaw-style feedback) ────────────────────────────────

async def _react(message, emoji: str):
    """Set a reaction emoji on a message. Silently ignores errors."""
    try:
        from telegram import ReactionTypeEmoji
        await message.set_reaction([ReactionTypeEmoji(emoji=emoji)])
    except Exception:
        pass  # Reactions may not be supported in all chats


# ── Paragraph-aware message splitting ─────────────────────────────────────

async def _send_voice_if_enabled(update, context, text: str):
    """If voice mode is on, convert text to audio and send as voice message."""
    voice_on = context.user_data.get("voice_mode", False)
    logger.info(f"TTS check: voice_mode={voice_on}, text_len={len(text)}")
    if not voice_on:
        return
    try:
        audio_path = await text_to_voice(text)
        if audio_path:
            with open(audio_path, "rb") as af:
                await update.message.reply_voice(voice=af)
            import os as _os
            _os.remove(audio_path)
    except Exception as e:
        logger.warning(f"TTS send error: {e}")


def _smart_split(text: str, max_len: int = 4000) -> list[str]:
    """Splits text at paragraph boundaries, falling back to hard split."""
    if len(text) <= max_len:
        return [text]
    chunks = []
    while text:
        if len(text) <= max_len:
            chunks.append(text)
            break
        # Try to split at last paragraph break within limit
        cut = text.rfind("\n\n", 0, max_len)
        if cut == -1:
            cut = text.rfind("\n", 0, max_len)
        if cut == -1 or cut < max_len // 2:
            cut = max_len
        chunks.append(text[:cut].rstrip())
        text = text[cut:].lstrip("\n")
    return chunks


# ── Main handler ──────────────────────────────────────────────────────────

async def handle_text_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Main handler for all text messages. Uses GPT-5 with function calling."""
    user_id = update.effective_user.id
    # Support photo-with-caption routed from photo_handler (message.text is None)
    raw_user_text = (
        context.user_data.pop("_photo_text_override", None)
        or update.message.text
        or ""
    )
    user_text = raw_user_text              # Working copy — enriched for GPT

    # ── Forwarded message context (python-telegram-bot v20+ API) ──
    fwd_label = None
    fwd_origin = getattr(update.message, "forward_origin", None)
    if fwd_origin:
        origin_type = getattr(fwd_origin, "type", "")
        if origin_type == "user":
            u = fwd_origin.sender_user
            name = u.full_name or u.username or str(u.id)
            fwd_label = f"от {name}"
        elif origin_type == "chat":
            c = fwd_origin.sender_chat
            fwd_label = f"из чата «{c.title or c.username or c.id}»"
        elif origin_type == "channel":
            c = fwd_origin.chat
            fwd_label = f"из канала «{c.title or c.username or c.id}»"
        elif origin_type == "hidden_user":
            fwd_label = f"от {fwd_origin.sender_user_name}"
        else:
            fwd_label = "переслано"

    if fwd_label:
        user_text = f"[Переслано {fwd_label}]\n{user_text}"

    logger.info(f"Message from user {user_id}: {user_text[:100]}")

    # ── Ack reaction: show the user we're processing ──
    await _react(update.message, "👀")

    # ── Reply-to context: if user replies to a specific bot message ──
    reply_msg = update.message.reply_to_message
    if reply_msg and reply_msg.from_user and reply_msg.from_user.is_bot:
        quoted = (reply_msg.text or "")[:500]
        if quoted:
            user_text = (
                f"[Пользователь отвечает на сообщение бота: \"{quoted}\"]\n\n"
                f"{user_text}"
            )

    # ── Skill flow check ──
    from skills_menu import handle_skill_input
    if await handle_skill_input(update, context):
        return

    # ── Transcript paste check ──
    if len(raw_user_text) > 200:
        from transcript_store import is_transcript_signal, save_transcript
        if is_transcript_signal(raw_user_text[:200]):
            await update.message.chat.send_action("typing")
            first_line = raw_user_text.split("\n")[0][:80].strip()
            save_transcript(
                text=raw_user_text, title=first_line, source="telegram_text"
            )
            await update.message.reply_text(
                f"Транскрипт сохранён ({len(raw_user_text)} символов).\n"
                f"Попадёт в утренний бриф."
            )
            return

    # ── Inject file context (enrichment only, not saved to history) ──
    last_file = context.user_data.get("last_file")
    if last_file:
        user_text = (
            f"[Контекст: пользователь отправил файл "
            f"\"{last_file['name']}\" ({last_file['size_kb']} КБ), "
            f"сохранён: {last_file['path']}]\n\n{user_text}"
        )
        context.user_data.pop("last_file", None)

    # ── Save RAW user text to history (before enrichment) ──
    add_to_history(user_id, "user", raw_user_text)

    # ── Build messages for OpenAI ──
    messages = [{"role": "system", "content": _get_system_prompt(user_id, raw_user_text)}]
    history = get_history(user_id)
    # Replace last user message with enriched version for current request
    if history and history[-1]["role"] == "user":
        history[-1]["content"] = user_text
    messages.extend(history)

    # ── Start typing indicator (refreshes every 4s) ──
    stop_typing = asyncio.Event()
    typing_task = asyncio.create_task(
        _keep_typing(update.message.chat, stop_typing)
    )

    try:
        client = _get_openai_client()
        loop = asyncio.get_running_loop()

        # ── Call GPT-5 with function calling (async via executor) ──
        msg = await loop.run_in_executor(
            None, _call_gpt, client, messages, TOOLS
        )

        refusal = getattr(msg, "refusal", None)
        if refusal:
            logger.warning(f"GPT refusal: {refusal}")

        response_text = (msg.content or "").strip()
        tool_calls = msg.tool_calls or []
        _voice_parts = []  # Collect text for TTS at the end

        logger.info(
            f"GPT response: text={response_text[:200] if response_text else 'NONE'}, "
            f"tools={[t.function.name for t in tool_calls]}"
        )

        # ── Fallback: empty response with tools → retry without tools ──
        if not response_text and not tool_calls:
            logger.warning("Empty GPT response with tools, retrying without tools...")
            msg = await loop.run_in_executor(
                None, _call_gpt, client, messages, None
            )
            response_text = (msg.content or "").strip()
            tool_calls = msg.tool_calls or []
            logger.info(f"Retry response: text={response_text[:200] if response_text else 'NONE'}")

        # ── Send the text response ──
        # When create_task is the only tool, skip GPT's text ("Записал!") —
        # the task confirmation message replaces it.
        is_task_only = (
            tool_calls
            and all(tc.function.name == "create_task" for tc in tool_calls)
        )
        if response_text and not is_task_only:
            add_to_history(user_id, "assistant", response_text)
            for chunk in _smart_split(response_text):
                await update.message.reply_text(chunk)
            _voice_parts.append(response_text)
        elif response_text and is_task_only:
            # Save to history but don't send — task confirmation handles it
            add_to_history(user_id, "assistant", response_text)
        elif not tool_calls:
            # Still no text AND no tool calls — something went wrong
            await update.message.reply_text(
                "Не удалось получить ответ. Попробуй переформулировать."
            )
            return

        # ── Text-only response (no tool calls) — send voice + memory, then return ──
        if not tool_calls:
            if _voice_parts:
                await _send_voice_if_enabled(update, context, "\n".join(_voice_parts))
            # Memory extraction (non-blocking)
            if response_text and len(raw_user_text) > 10:
                try:
                    client = get_openai_client()
                    asyncio.ensure_future(loop.run_in_executor(
                        None, _extract_and_save_memories, client, user_id, raw_user_text, response_text
                    ))
                except Exception:
                    pass
            return

        # ── Execute tool calls → collect results → synthesize via GPT ──
        seen_tools = set()
        tool_results = []       # {"id", "fn", "result", "arguments"}
        direct_sends = []       # Tools sent directly (brief, translate, cc — too long for synthesis)

        for tc in tool_calls:
            fn_name = tc.function.name

            if fn_name in seen_tools and fn_name == "create_task":
                logger.info(f"Skipping duplicate create_task call")
                continue
            seen_tools.add(fn_name)

            try:
                fn_args = json.loads(tc.function.arguments) if tc.function.arguments else {}
            except json.JSONDecodeError:
                logger.error(f"Bad tool args: {tc.function.arguments}")
                tool_results.append({"id": tc.id, "fn": fn_name, "result": "Ошибка: невалидные аргументы", "arguments": tc.function.arguments or "{}"})
                continue

            result_text = ""

            if fn_name == "create_task":
                task_text = raw_user_text
                stripped = task_text.strip()
                if len(stripped) < 15 and "?" not in stripped:
                    logger.info(f"Skipping create_task for short message: {stripped}")
                    continue

                _TASK_MARKERS = (
                    "запиши", "записать", "добавь задач", "поставь задач",
                    "напомни", "напоминание", "нужно сделать", "не забудь",
                    "запланируй", "внеси в список", "создай задач",
                    "добавь в задач", "task", "remind me", "todo",
                )
                text_lower = stripped.lower()
                has_task_marker = any(m in text_lower for m in _TASK_MARKERS)
                has_date_marker = any(
                    d in text_lower for d in (
                        "января", "февраля", "марта", "апреля", "мая", "июня",
                        "июля", "августа", "сентября", "октября", "ноября",
                        "декабря", "понедельник", "вторник", "сред", "четверг",
                        "пятниц", "суббот", "воскресень", "завтра", "послезавтра",
                        "через час", "через день", "через неделю",
                    )
                )
                if not has_task_marker and not has_date_marker:
                    logger.info(f"Blocking create_task — no task markers in: {stripped[:80]}")
                    if is_task_only and not response_text:
                        fallback_msg = await loop.run_in_executor(None, _call_gpt, client, messages, None)
                        fallback_text = (fallback_msg.content or "").strip()
                        if fallback_text:
                            add_to_history(user_id, "assistant", fallback_text)
                            for chunk in _smart_split(fallback_text):
                                await update.message.reply_text(chunk)
                    continue

                task_hash = hashlib.md5(task_text.lower().strip().encode()).hexdigest()
                now = time.time()
                expired = [k for k, v in _recent_tasks.items() if now - v >= _DEDUP_WINDOW]
                for k in expired:
                    del _recent_tasks[k]
                if task_hash in _recent_tasks:
                    continue
                _recent_tasks[task_hash] = now

                gtd_result = _run_gtd_processor(task_text)
                if gtd_result:
                    await _react(update.message, "✅")
                    result_text = f"Задача создана: {gtd_result[:500]}"

            elif fn_name == "generate_brief":
                await _react(update.message, "📊")
                await update.message.reply_text("Генерирую брифинг, подожди...")
                brief = await loop.run_in_executor(None, _run_brief_generator)
                for chunk in _smart_split(brief):
                    await update.message.reply_text(chunk)
                _voice_parts.append(brief)
                direct_sends.append(fn_name)
                continue  # Skip synthesis — brief is self-contained

            elif fn_name == "query_data":
                await _react(update.message, "📈")
                query_text = fn_args.get("query_text", raw_user_text)
                result_text = await loop.run_in_executor(None, _run_data_query, query_text)

            elif fn_name == "send_files":
                file_filter = fn_args.get("filename", "")
                await _send_outbox_files(update, filename_filter=file_filter)
                direct_sends.append(fn_name)
                continue

            elif fn_name == "run_claude_code":
                await _react(update.message, "⚡")
                cc_prompt = fn_args.get("prompt", raw_user_text)
                await update.message.reply_text("Выполняю через Claude Code, это может занять до 2 минут...")
                cc_result = await loop.run_in_executor(None, run_claude_code, cc_prompt)
                for chunk in _smart_split(cc_result):
                    await update.message.reply_text(chunk)
                _voice_parts.append(cc_result)
                direct_sends.append(fn_name)
                continue  # Skip synthesis — CC output is self-contained

            elif fn_name == "search_meetings":
                await _react(update.message, "🎤")
                days = fn_args.get("days", 7)
                keyword = fn_args.get("keyword")
                result_text = await loop.run_in_executor(None, search_fireflies_meetings, days, keyword)

            elif fn_name == "analyze_meeting":
                await _react(update.message, "🎤")
                meeting_id = fn_args.get("meeting_id", "")
                question = fn_args.get("question")
                result_text = await loop.run_in_executor(None, analyze_fireflies_meeting, meeting_id, question)

            elif fn_name == "translate_and_speak":
                await _react(update.message, "🗣")
                tr_text = fn_args.get("text", "")
                tr_lang = fn_args.get("target_language", "en")
                target_name = LANG_NAMES.get(tr_lang, tr_lang)
                tr_messages = [{
                    "role": "system",
                    "content": f"Translate the following text to {target_name}. Return ONLY the translation, nothing else."
                }, {"role": "user", "content": tr_text}]
                try:
                    tr_msg = await loop.run_in_executor(
                        None, lambda m=tr_messages: call_gpt(m, model=MODEL_FAST, max_tokens=1024)
                    )
                    translated = tr_msg.content.strip()
                except Exception as e:
                    logger.error(f"Translation error: {e}")
                    await update.message.reply_text("Не удалось перевести.")
                    continue
                add_to_history(user_id, "assistant", f"[{target_name}] {translated}")
                await update.message.reply_text(f"🗣 {translated}")
                voice_path = await text_to_voice(translated, voice=tr_lang)
                if voice_path:
                    try:
                        with open(voice_path, "rb") as f:
                            await update.message.reply_voice(voice=f)
                    finally:
                        try:
                            os.remove(voice_path)
                        except OSError:
                            pass
                direct_sends.append(fn_name)
                continue

            elif fn_name == "web_search":
                await _react(update.message, "🔍")
                search_query = fn_args.get("query", raw_user_text)
                count = fn_args.get("count", 5)
                result_text = await loop.run_in_executor(None, web_search, search_query, count)

            elif fn_name == "crawl_page":
                await _react(update.message, "📄")
                page_url = fn_args.get("url", "")
                result_text = await loop.run_in_executor(None, crawl_page, page_url)

            elif fn_name == "set_reminder":
                await _react(update.message, "⏰")
                rem_text = fn_args.get("text", "Напоминание")
                when_str = fn_args.get("when", "+1h")
                every_str = fn_args.get("every", "")
                try:
                    fire_at = parse_fire_at(when_str)
                    repeat = parse_repeat(every_str)
                    rid = create_reminder(user_id, rem_text, fire_at, repeat)
                    fire_fmt = fire_at.strftime("%d.%m в %H:%M")
                    repeat_info = ""
                    if repeat:
                        if repeat >= 86400:
                            repeat_info = f" (повтор каждые {repeat // 86400} дн.)"
                        elif repeat >= 3600:
                            repeat_info = f" (повтор каждые {repeat // 3600} ч.)"
                        else:
                            repeat_info = f" (повтор каждые {repeat // 60} мин.)"
                    result_text = f"Напоминание #{rid} установлено на {fire_fmt}{repeat_info}: {rem_text}"
                except ValueError as e:
                    result_text = f"Не понял время: {e}"

            # Collect result for synthesis
            if result_text:
                tool_results.append({"id": tc.id, "fn": fn_name, "result": result_text[:3000], "arguments": tc.function.arguments or "{}"})

        # ── Synthesis: send results back to GPT for a coherent response ──
        if tool_results and not direct_sends:
            # Build tool-role messages for the second GPT call
            synth_messages = list(messages)
            # Add original assistant message with tool_calls
            synth_messages.append({
                "role": "assistant",
                "content": response_text or None,
                "tool_calls": [
                    {"id": tr["id"], "type": "function",
                     "function": {"name": tr["fn"], "arguments": tr["arguments"]}}
                    for tr in tool_results
                ],
            })
            for tr in tool_results:
                synth_messages.append({
                    "role": "tool",
                    "tool_call_id": tr["id"],
                    "content": tr["result"],
                })

            try:
                synth_msg = await loop.run_in_executor(
                    None, _call_gpt, client, synth_messages, None
                )
                synth_text = (synth_msg.content or "").strip()
                if synth_text:
                    add_to_history(user_id, "assistant", synth_text)
                    for chunk in _smart_split(synth_text):
                        await update.message.reply_text(chunk)
                    _voice_parts.append(synth_text)
                    logger.info(f"Synthesis: {synth_text[:200]}")
            except Exception as synth_err:
                logger.error(f"Synthesis call failed: {synth_err}")
                # Fallback: send raw results
                for tr in tool_results:
                    for chunk in _smart_split(tr["result"]):
                        await update.message.reply_text(chunk)
                    _voice_parts.append(tr["result"])

        elif tool_results and direct_sends:
            # Mixed: some tools were sent directly, some collected
            # Just send remaining results as-is (e.g. task created alongside brief)
            for tr in tool_results:
                for chunk in _smart_split(tr["result"]):
                    await update.message.reply_text(chunk)

        # ── Send TTS voice message if voice mode enabled ──
        has_translate = any(tc.function.name == "translate_and_speak" for tc in tool_calls)
        if _voice_parts and not has_translate:
            await _send_voice_if_enabled(update, context, "\n".join(_voice_parts))

        # ── Memory extraction (non-blocking, cheap model) ──
        final_text = response_text or " ".join(tr["result"][:500] for tr in tool_results)
        if final_text and len(raw_user_text) > 10:
            heavy = {"generate_brief", "query_data", "run_claude_code", "send_files", "analyze_meeting"}
            tool_names = {tc.function.name for tc in tool_calls}
            if not (tool_names & heavy):
                try:
                    asyncio.ensure_future(
                        loop.run_in_executor(
                            None, _extract_and_save_memories,
                            client, user_id, raw_user_text, final_text,
                        )
                    )
                except Exception:
                    pass

    except Exception as e:
        logger.error(f"Error in AI handler: {e}", exc_info=True)
        err_str = str(e).lower()
        if "rate" in err_str or "429" in err_str:
            error_msg = "Превышен лимит запросов к AI. Подожди пару минут и попробуй снова."
        elif "timeout" in err_str or "timed out" in err_str:
            error_msg = "AI не ответил вовремя — сервер перегружен. Попробуй через минуту."
        elif "api_key" in err_str or "authentication" in err_str or "401" in err_str:
            error_msg = "Проблема с ключом API. Напиши мне позже, разберусь."
        elif "500" in err_str or "502" in err_str or "503" in err_str:
            error_msg = "Сервер AI временно недоступен. Попробуй через пару минут."
        elif "context_length" in err_str or "token" in err_str:
            error_msg = (
                "Слишком длинный контекст. "
                "Попробуй /compact чтобы сжать историю, потом повтори."
            )
        else:
            error_msg = "Произошла ошибка при обработке. Попробуй ещё раз через минуту."
        await update.message.reply_text(error_msg)

    finally:
        stop_typing.set()
        typing_task.cancel()
        try:
            await typing_task
        except (asyncio.CancelledError, Exception):
            pass
