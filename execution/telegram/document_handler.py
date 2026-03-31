#!/usr/bin/env python3
"""
Telegram Bot: Document Handler

Receives documents (PDF, DOCX, XLSX, TXT, etc.), saves them to data/inbox/,
and confirms receipt. Stores file context so follow-up messages can reference it.

Special routing:
- Audio/video files -> Fireflies for meeting transcription
- Text files with transcript signal (caption/filename) -> transcript store for daily brief
- Captions with action words -> Claude Code for processing (translate, summarize, etc.)
"""

import os
import asyncio
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from task_handler import _react, _smart_split

logger = logging.getLogger(__name__)

INBOX_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "inbox")

# Extensions that can contain text transcripts
TEXT_EXTENSIONS = {".txt", ".md", ".text", ".log", ".csv"}

# Keywords that suggest the user wants the file processed (not just stored)
_ACTION_KEYWORDS = [
    "перевед", "перевест", "переведи", "translate",
    "проанализир", "анализ", "analyze", "analyse",
    "резюмир", "суммир", "summarize", "summary",
    "извлеки", "extract",
    "прочитай", "прочти", "read",
    "обработай", "process",
]


def _caption_wants_processing(caption: str) -> bool:
    """Check if caption implies the user wants the file processed."""
    lower = caption.lower()
    return any(kw in lower for kw in _ACTION_KEYWORDS)


def _extract_text_from_file(file_path: str):
    """Try to read text content from a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except (UnicodeDecodeError, OSError):
        try:
            with open(file_path, "r", encoding="cp1251") as f:
                return f.read()
        except Exception:
            return None


async def handle_document_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Downloads a document, saves it to inbox, and confirms receipt."""
    doc = update.message.document

    # Route audio/video documents to meeting handler (Fireflies)
    try:
        from meeting_handler import _is_meeting_file, handle_meeting_upload
        if _is_meeting_file(doc.file_name):
            await handle_meeting_upload(update, context)
            return
    except ImportError:
        pass

    # Ack: show we received the file
    await _react(update.message, "📎")
    await update.message.chat.send_action("typing")

    file_name = doc.file_name or "unknown_file"
    file_size_kb = round((doc.file_size or 0) / 1024, 1)

    # Download to inbox first
    doc_file = await doc.get_file()

    os.makedirs(INBOX_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    name, ext = os.path.splitext(file_name)
    saved_name = f"{name}_{timestamp}{ext}"
    file_path = os.path.join(INBOX_DIR, saved_name)

    await doc_file.download_to_drive(file_path)
    logger.info(f"Document saved: {file_path} ({file_size_kb} KB)")

    # ── Store file context for follow-up messages ──
    context.user_data["last_file"] = {
        "name": file_name,
        "path": file_path,
        "size_kb": file_size_kb,
        "ext": ext.lower(),
        "timestamp": timestamp,
    }

    # ── Add to conversation history so GPT knows about the file ──
    from bot_memory import add_to_history
    user_id = update.effective_user.id
    file_note = f"[Пользователь отправил файл: {file_name} ({file_size_kb} КБ). Сохранён: {file_path}]"
    add_to_history(user_id, "user", file_note)

    # Check if this is a transcript file
    caption = update.message.caption or ""
    from transcript_store import is_transcript_signal, save_transcript

    is_transcript = False
    if ext.lower() in TEXT_EXTENSIONS:
        if is_transcript_signal(caption) or is_transcript_signal(file_name):
            is_transcript = True

    if is_transcript:
        text_content = _extract_text_from_file(file_path)
        if text_content and len(text_content.strip()) > 50:
            title = caption.strip() if caption.strip() else name
            save_transcript(
                text=text_content,
                title=title,
                source="telegram_file",
                file_name=file_name,
            )
            await update.message.reply_text(
                f"Транскрипт сохранен: {file_name} ({file_size_kb} КБ)\n"
                f"Попадёт в утренний бриф."
            )
            return

    # ── If caption wants processing → delegate to Claude Code ──
    if caption and caption.strip() and _caption_wants_processing(caption):
        await update.message.reply_text(
            f"Документ получен: {file_name} ({file_size_kb} КБ)\n"
            f"Обрабатываю через Claude Code..."
        )
        from utils import run_claude_code
        await update.message.chat.send_action("typing")
        cc_prompt = (
            f"The user sent a file: {file_path}\n"
            f"User request: {caption}\n"
            f"Process the file and respond in Russian."
        )
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, run_claude_code, cc_prompt)
        for chunk in _smart_split(result):
            await update.message.reply_text(chunk)
        add_to_history(user_id, "assistant", result[:500])
        return

    await update.message.reply_text(
        f"Документ сохранен: {file_name} ({file_size_kb} КБ)"
    )
    add_to_history(user_id, "assistant", f"Документ сохранен: {file_name} ({file_size_kb} КБ)")

    # If user added a caption (non-action), route it through AI with file context
    if caption and caption.strip():
        from task_handler import handle_text_message
        context.user_data["_photo_text_override"] = (
            f"[Документ: {file_name}, {file_size_kb} КБ, путь: {file_path}]\n\n{caption}"
        )
        await handle_text_message(update, context)
