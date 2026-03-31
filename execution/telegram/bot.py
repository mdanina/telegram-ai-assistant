#!/usr/bin/env python3
"""
Telegram Bot: Main Application

This script runs the main Telegram bot, which serves as the primary interface
for the AIOS.
"""

import asyncio
import os
import sys
import logging
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, PicklePersistence, filters, ContextTypes,
)
from dotenv import load_dotenv

# Ensure local modules are importable regardless of cwd
sys.path.insert(0, os.path.dirname(__file__))

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

from slash_commands import handle_slash_command
from voice_handler import handle_voice_message
from task_handler import handle_text_message
from photo_handler import handle_photo_message
from document_handler import handle_document_message
from meeting_handler import handle_meeting_upload
from skills_menu import (
    handle_skills_command, handle_skill_callback,
    handle_email_action_callback, handle_task_action_callback,
)
from scheduler import get_due_reminders, mark_fired

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_USER_IDS = [int(uid) for uid in os.getenv("TELEGRAM_ALLOWED_USER_IDS", "").split(",") if uid]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    await update.message.reply_text("AIOS is online.")


async def handle_unsupported(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles stickers, animations, locations, and other unsupported message types."""
    await update.message.reply_text(
        "Этот тип сообщений пока не поддерживается. "
        "Отправь текст, голосовое, фото или файл."
    )


async def _reminder_loop(application) -> None:
    """Background loop: checks for due reminders every 30 seconds."""
    from telegram import Bot
    bot = application.bot
    while True:
        try:
            due = get_due_reminders()
            for r in due:
                try:
                    await bot.send_message(
                        chat_id=r["user_id"],
                        text=f"⏰ Напоминание:\n{r['text']}",
                    )
                    logger.info(f"Reminder #{r['id']} fired for user {r['user_id']}")
                except Exception as e:
                    logger.error(f"Failed to send reminder #{r['id']}: {e}")
                mark_fired(r["id"], r.get("repeat_seconds", 0))
        except Exception as e:
            logger.error(f"Reminder loop error: {e}")
        await asyncio.sleep(30)


async def post_init(application) -> None:
    """Called after application is initialized — start background tasks."""
    asyncio.create_task(_reminder_loop(application))
    logger.info("Reminder background loop started.")

    # Rebuild ChromaDB semantic search index from SQLite
    try:
        from memory_search import rebuild_index
        count = rebuild_index()
        if count:
            logger.info(f"ChromaDB index rebuilt: {count} memories")
    except Exception as e:
        logger.warning(f"ChromaDB index rebuild skipped: {e}")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main() -> None:
    """Start the bot."""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set. Bot cannot start.")
        return

    if not ALLOWED_USER_IDS:
        logger.error("TELEGRAM_ALLOWED_USER_IDS is not set. Bot refuses to start in open-access mode.")
        return

    # Use AIOS_ROOT or derive from cwd (run_bot.py does os.chdir to project root)
    _aios_root = os.environ.get("AIOS_ROOT", os.getcwd())
    persistence_path = os.path.join(_aios_root, "data", "bot_persistence.pickle")
    persistence = PicklePersistence(filepath=persistence_path)
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).persistence(persistence).post_init(post_init).build()

    # Filter for allowed users (whitelist is mandatory)
    user_filter = filters.User(user_id=ALLOWED_USER_IDS)

    # Register handlers (order matters — first match wins)
    application.add_handler(CommandHandler("start", start, filters=user_filter))
    application.add_handler(CommandHandler("skills", handle_skills_command, filters=user_filter))
    application.add_handler(CallbackQueryHandler(handle_skill_callback, pattern="^skill:"))
    application.add_handler(CallbackQueryHandler(handle_email_action_callback, pattern="^email:"))
    application.add_handler(CallbackQueryHandler(handle_task_action_callback, pattern="^task:"))
    application.add_handler(MessageHandler(filters.COMMAND & user_filter, handle_slash_command))
    application.add_handler(MessageHandler(filters.VOICE & user_filter, handle_voice_message))
    application.add_handler(MessageHandler(filters.AUDIO & user_filter, handle_meeting_upload))
    application.add_handler(MessageHandler(filters.VIDEO & user_filter, handle_meeting_upload))
    application.add_handler(MessageHandler(filters.VIDEO_NOTE & user_filter, handle_meeting_upload))
    application.add_handler(MessageHandler(filters.PHOTO & user_filter, handle_photo_message))
    application.add_handler(MessageHandler(filters.Document.ALL & user_filter, handle_document_message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & user_filter, handle_text_message))

    # Catch-all for stickers, animations, locations, contacts, etc.
    application.add_handler(MessageHandler(
        user_filter & ~filters.COMMAND & ~filters.TEXT & ~filters.VOICE
        & ~filters.AUDIO & ~filters.VIDEO & ~filters.VIDEO_NOTE
        & ~filters.PHOTO & ~filters.Document.ALL,
        handle_unsupported,
    ))

    # Register error handler
    application.add_error_handler(error_handler)

    # Start the Bot
    logger.info("Starting Telegram bot...")
    application.run_polling()


if __name__ == "__main__":
    main()
