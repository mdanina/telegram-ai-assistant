#!/usr/bin/env python3
"""
Telegram Bot: Skills Menu (Inline Keyboard)

Provides /skills command with quick-tap buttons for Claude Code skills.
One-tap buttons execute immediately; two-step buttons ask for details first.
"""

import os
import sqlite3
import logging
from datetime import datetime, timedelta, timezone
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

# Moscow timezone (UTC+3)
_MSK = timezone(timedelta(hours=3))
from telegram.ext import ContextTypes

from utils import run_claude_code
from task_handler import _smart_split

logger = logging.getLogger(__name__)

ALLOWED_USER_IDS = [int(uid) for uid in os.getenv("TELEGRAM_ALLOWED_USER_IDS", "").split(",") if uid]

# ── Skill definitions ──────────────────────────────────────────────
# Each skill: (label, prompt_or_template, needs_input, input_question)
SKILLS = {
    "mail_check": {
        "label": "\U0001f4e7 Почта",
        "prompt": "__mail_check__",  # Special: native IMAP via email_handler
        "needs_input": False,
    },
    "brief": {
        "label": "\U0001f4ca Брифинг",
        "prompt": "__brief__",  # Special: runs brief_generator.py instead of Claude Code
        "needs_input": False,
    },
    "mail_send": {
        "label": "\u2709\ufe0f Письмо",
        "prompt": "__mail_send__",  # Special: native SMTP via email_handler
        "needs_input": True,
        "question": "Кому и о чём? Формат:\nадрес@почты.ru\nТема письма\nТекст письма",
    },
    "mail_read": {
        "label": "\U0001f4e9 Читать",
        "prompt": "__mail_read__",  # Special: reads Nth unread email
        "needs_input": True,
        "question": "Какое письмо прочитать? (номер из списка, напр. 1)",
    },
    "tasks": {
        "label": "\U0001f4cb Задачи",
        "prompt": "__tasks__",  # Special: queries SQLite directly
        "needs_input": False,
    },
    "document": {
        "label": "\U0001f4c4 Документ",
        "prompt": "Use the file-factory skill to create a document: {details}. Save the file to data/outbox/ so the Telegram bot can deliver it.",
        "needs_input": True,
        "question": "Какой документ создать? (тип, тема, содержание)",
    },
}

# Button layout: list of rows, each row is a list of skill keys
LAYOUT = [
    ["mail_check", "mail_read"],
    ["mail_send", "brief"],
    ["tasks", "document"],
]


def _build_keyboard() -> InlineKeyboardMarkup:
    """Builds the inline keyboard from LAYOUT and SKILLS."""
    keyboard = []
    for row_keys in LAYOUT:
        row = []
        for key in row_keys:
            skill = SKILLS[key]
            row.append(InlineKeyboardButton(skill["label"], callback_data=f"skill:{key}"))
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)


async def handle_skills_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends the skills menu as an inline keyboard."""
    await update.message.reply_text(
        "Выбери действие:",
        reply_markup=_build_keyboard(),
    )


async def handle_skill_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles inline button press (with user whitelist check)."""
    query = update.callback_query

    # Security: reject callbacks from non-allowed users
    if ALLOWED_USER_IDS and query.from_user.id not in ALLOWED_USER_IDS:
        await query.answer("Доступ запрещён.", show_alert=True)
        return

    await query.answer()  # Acknowledge the button press

    data = query.data or ""
    if not data.startswith("skill:"):
        return

    skill_key = data.split(":", 1)[1]
    skill = SKILLS.get(skill_key)
    if not skill:
        await query.edit_message_text("Неизвестный скилл.")
        return

    if skill["needs_input"]:
        # Two-step: save pending skill and ask for details
        context.user_data["pending_skill"] = skill_key
        await query.edit_message_text(skill["question"])
        return

    # One-tap: execute immediately
    await query.edit_message_text(f"{skill['label']} — выполняю...")

    if skill["prompt"] == "__brief__":
        # Special case: run brief generator directly
        from task_handler import _run_brief_generator
        result = _run_brief_generator()
    elif skill["prompt"] == "__tasks__":
        result, task_ids = _get_tasks_list_with_ids()
        # Send text, then show ✅ buttons if tasks exist
        for chunk in _smart_split(result):
            await update.effective_chat.send_message(chunk)
        if task_ids:
            await update.effective_chat.send_message(
                "Отметить выполненную:",
                reply_markup=_build_task_done_buttons(task_ids),
            )
        return
    elif skill["prompt"] == "__mail_check__":
        from email_handler import check_inbox
        result = check_inbox(count=10, unread_only=True)
    else:
        await update.effective_chat.send_action("typing")
        result = run_claude_code(skill["prompt"])

    for chunk in _smart_split(result):
        await update.effective_chat.send_message(chunk)


async def handle_email_action_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles post-read email action buttons (reply, mark read, summary)."""
    query = update.callback_query

    if ALLOWED_USER_IDS and query.from_user.id not in ALLOWED_USER_IDS:
        await query.answer("Доступ запрещён.", show_alert=True)
        return

    await query.answer()

    data = query.data or ""
    last_email = context.user_data.get("last_read_email")

    if not last_email:
        await query.edit_message_text("Нет данных о письме. Прочитай письмо заново через /skills.")
        return

    if data == "email:mark_read":
        from email_handler import mark_as_read
        msg_uid = last_email.get("msg_uid")
        result = mark_as_read(msg_uid)
        await update.effective_chat.send_message(f"✅ {result}")

    elif data == "email:summary":
        await update.effective_chat.send_message("📝 Генерирую саммари...")
        await update.effective_chat.send_action("typing")
        from email_handler import summarize_email
        result = summarize_email(
            body=last_email.get("body", ""),
            subject=last_email.get("subject", ""),
            from_name=last_email.get("from_name", ""),
        )
        for chunk in _smart_split(result):
            await update.effective_chat.send_message(chunk)

    elif data == "email:reply":
        # Ask user for reply text
        context.user_data["pending_skill"] = "email_reply"
        await update.effective_chat.send_message("Напиши текст ответа:")


def _build_email_action_buttons() -> InlineKeyboardMarkup:
    """Builds inline buttons for post-read email actions."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("↩️ Ответить", callback_data="email:reply"),
            InlineKeyboardButton("✅ Прочитано", callback_data="email:mark_read"),
            InlineKeyboardButton("📝 Саммари", callback_data="email:summary"),
        ]
    ])


async def handle_skill_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Checks for pending two-step skill and executes it. Returns True if handled."""
    skill_key = context.user_data.pop("pending_skill", None)
    if not skill_key:
        return False

    details = update.message.text.strip()

    # ── Special handlers (not in SKILLS dict) ──

    # Mail send confirmation flow
    if skill_key == "mail_send_confirm":
        if details.lower() in ("да", "yes", "ок", "ok", "отправь", "send"):
            pending = context.user_data.pop("pending_email", None)
            if pending:
                from email_handler import send_email
                result = send_email(**pending)
            else:
                result = "Нет письма для отправки. Попробуй заново через /skills."
        else:
            context.user_data.pop("pending_email", None)
            result = "Отправка отменена."

        for chunk in _smart_split(result):
            await update.message.reply_text(chunk)
        return True

    # Email reply handler
    if skill_key == "email_reply":
        last_email = context.user_data.get("last_read_email")
        if not last_email:
            await update.message.reply_text("Нет данных о письме. Прочитай письмо заново.")
            return True
        from email_handler import reply_to_email
        result = reply_to_email(
            to=last_email["from_email"],
            subject=last_email["subject"],
            body=details,
            original_body=last_email.get("body", ""),
        )
        for chunk in _smart_split(result):
            await update.message.reply_text(chunk)
        return True

    # ── Standard skills from SKILLS dict ──
    skill = SKILLS.get(skill_key)
    if not skill:
        return False

    # ── Native email handlers ──
    if skill["prompt"] == "__mail_send__":
        result = _handle_mail_send(details, context)
        for chunk in _smart_split(result):
            await update.message.reply_text(chunk)
        return True
    elif skill["prompt"] == "__mail_read__":
        from email_handler import read_email_full
        try:
            idx = int(details.strip())
        except ValueError:
            idx = 1
        email_data = read_email_full(index=idx)
        result = email_data.get("text", "Ошибка чтения письма.")

        # Store metadata for follow-up actions (reply, mark read, summary)
        if not email_data.get("error"):
            context.user_data["last_read_email"] = {
                "from_email": email_data.get("from_email", ""),
                "from_name": email_data.get("from_name", ""),
                "subject": email_data.get("subject", ""),
                "body": email_data.get("body", ""),
                "msg_uid": email_data.get("msg_uid"),
            }

        # Send email text
        for chunk in _smart_split(result):
            await update.message.reply_text(chunk)

        # Show action buttons if email was read successfully
        if not email_data.get("error"):
            await update.message.reply_text(
                "Что сделать с письмом?",
                reply_markup=_build_email_action_buttons(),
            )
        return True
    else:
        prompt = skill["prompt"].format(details=details)
        await update.message.chat.send_action("typing")
        await update.message.reply_text("Выполняю, это может занять до 2 минут...")
        result = run_claude_code(prompt)

    for chunk in _smart_split(result):
        await update.message.reply_text(chunk)

    return True


def _handle_mail_send(details: str, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Parses user input, shows preview, and asks for confirmation.

    Expected format:
    address@email.com
    Subject line
    Body text (can be multiline)
    """
    lines = details.strip().split("\n")
    if len(lines) < 3:
        return (
            "Формат отправки:\n"
            "адрес@почты.ru\n"
            "Тема письма\n"
            "Текст письма"
        )

    to_addr = lines[0].strip()
    subject = lines[1].strip()
    body = "\n".join(lines[2:]).strip()

    if "@" not in to_addr:
        return f"'{to_addr}' не похоже на email-адрес. Проверь формат."

    # Save draft and ask for confirmation
    context.user_data["pending_email"] = {
        "to": to_addr,
        "subject": subject,
        "body": body,
    }
    context.user_data["pending_skill"] = "mail_send_confirm"

    preview = (
        f"Кому: {to_addr}\n"
        f"Тема: {subject}\n"
        f"{'─' * 25}\n"
        f"{body[:500]}\n"
        f"{'─' * 25}\n\n"
        f"Отправить? (да/нет)"
    )
    return preview


# ── Task list query ───────────────────────────────────────────────

DB_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'aios_data.db')


def _get_tasks_list():
    """Queries SQLite for pending tasks and returns a formatted list."""
    result, _ = _get_tasks_list_with_ids()
    return result


def _get_tasks_list_with_ids():
    """Queries SQLite for pending tasks. Returns (formatted_text, ordered_task_ids).

    Task IDs are in display order (matching numbered list) so buttons can reference them.
    """
    if not os.path.exists(DB_FILE):
        return "Нет активных задач.", []

    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, raw_text, next_action, project, delegated_to, due_date, domain
            FROM tasks
            WHERE status IN ('pending', 'reminded')
            ORDER BY
                CASE WHEN due_date IS NOT NULL THEN 0 ELSE 1 END,
                due_date ASC
        """)
        rows = [dict(r) for r in cursor.fetchall()]
    except Exception as e:
        return f"Ошибка чтения задач: {e}", []
    finally:
        if conn:
            conn.close()

    if not rows:
        return "Нет активных задач.", []

    now = datetime.now(_MSK).replace(tzinfo=None)
    today = now.date()
    tomorrow = today + timedelta(days=1)

    overdue = []
    today_tasks = []
    tomorrow_tasks = []
    later = []
    no_date = []

    for task in rows:
        due_str = task.get("due_date")
        if not due_str:
            no_date.append(task)
            continue

        # Parse date/datetime
        due_dt = None
        for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M", "%Y-%m-%d"):
            try:
                due_dt = datetime.strptime(due_str.strip(), fmt)
                break
            except ValueError:
                pass

        if not due_dt:
            no_date.append(task)
            continue

        due_date = due_dt.date()
        if due_date < today:
            overdue.append(task)
        elif due_date == today:
            today_tasks.append(task)
        elif due_date == tomorrow:
            tomorrow_tasks.append(task)
        else:
            later.append(task)

    lines = []
    # Collect task IDs in display order for button mapping
    all_tasks_ordered = []

    _DOMAIN_LABELS = {"product": "БАЛ", "secondary_product": "SP"}

    def _fmt(task):
        text = task.get("next_action") or task.get("raw_text") or "???"
        parts = [text]
        if task.get("due_date") and " " in (task.get("due_date") or ""):
            # Has time component — show it
            parts.append(f"({task['due_date'].split(' ')[1]})")
        if task.get("project"):
            parts.append(f"[{task['project']}]")
        if task.get("delegated_to"):
            parts.append(f"→ {task['delegated_to']}")
        domain = task.get("domain", "personal")
        if domain in _DOMAIN_LABELS:
            parts.append(f"({_DOMAIN_LABELS[domain]})")
        return " ".join(parts)

    # Global counter across all sections
    counter = 0

    if overdue:
        lines.append("Просроченные:")
        for t in overdue:
            counter += 1
            lines.append(f"  {counter}. {_fmt(t)}")
            all_tasks_ordered.append(t)

    if today_tasks:
        lines.append("\nНа сегодня:")
        for t in today_tasks:
            counter += 1
            lines.append(f"  {counter}. {_fmt(t)}")
            all_tasks_ordered.append(t)

    if tomorrow_tasks:
        lines.append("\nНа завтра:")
        for t in tomorrow_tasks:
            counter += 1
            lines.append(f"  {counter}. {_fmt(t)}")
            all_tasks_ordered.append(t)

    if later:
        lines.append("\nПозже:")
        for t in later:
            counter += 1
            due = t.get("due_date", "").split(" ")[0]
            lines.append(f"  {counter}. {_fmt(t)} — {due}")
            all_tasks_ordered.append(t)

    if no_date:
        lines.append("\nБез даты:")
        for t in no_date:
            counter += 1
            lines.append(f"  {counter}. {_fmt(t)}")
            all_tasks_ordered.append(t)

    task_ids = [t["id"] for t in all_tasks_ordered]
    text = "\n".join(lines) if lines else "Нет активных задач."
    return text, task_ids


def _build_task_done_buttons(task_ids: list) -> InlineKeyboardMarkup:
    """Builds inline ✅ buttons for marking tasks as done.

    Shows up to 10 buttons in rows of 5.
    """
    buttons = []
    for i, tid in enumerate(task_ids[:10], 1):
        buttons.append(InlineKeyboardButton(f"✅ {i}", callback_data=f"task:done:{tid}"))

    # Layout: rows of 5
    keyboard = []
    for j in range(0, len(buttons), 5):
        keyboard.append(buttons[j:j + 5])
    return InlineKeyboardMarkup(keyboard)


def _mark_task_done(task_id: int) -> str:
    """Marks a task as done in SQLite. Returns result message."""
    if not os.path.exists(DB_FILE):
        return "База данных не найдена."

    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Get task info for confirmation
        cursor.execute("SELECT next_action, raw_text FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        if not row:
            return "Задача не найдена."

        task_name = row[0] or row[1] or "???"

        cursor.execute(
            "UPDATE tasks SET status = 'done' WHERE id = ?",
            (task_id,),
        )
        conn.commit()

        return f"✅ Выполнено: {task_name[:100]}"

    except Exception as e:
        logger.error(f"mark_task_done error: {e}")
        return f"Ошибка: {e}"
    finally:
        if conn:
            conn.close()


async def handle_task_action_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles task action buttons (mark done)."""
    query = update.callback_query

    if ALLOWED_USER_IDS and query.from_user.id not in ALLOWED_USER_IDS:
        await query.answer("Доступ запрещён.", show_alert=True)
        return

    await query.answer()

    data = query.data or ""

    if data.startswith("task:done:"):
        try:
            task_id = int(data.split(":")[2])
        except (IndexError, ValueError):
            await query.edit_message_text("Ошибка: неверный ID задачи.")
            return

        result = _mark_task_done(task_id)
        await update.effective_chat.send_message(result)

        # Refresh the task list with updated buttons
        new_text, new_ids = _get_tasks_list_with_ids()
        if new_ids:
            await update.effective_chat.send_message(new_text)
            await update.effective_chat.send_message(
                "Отметить выполненную:",
                reply_markup=_build_task_done_buttons(new_ids),
            )
        else:
            await update.effective_chat.send_message(new_text)
