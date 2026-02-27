#!/usr/bin/env python3
"""
Telegram Bot: Main Application

This script runs the main Telegram bot, which serves as the primary interface
for the AIOS.
"""

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

from slash_commands import handle_slash_command
from voice_handler import handle_voice_message
from task_handler import handle_text_message

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

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main() -> None:
    """Start the bot."""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set. Bot cannot start.")
        return

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Filter for allowed users
    user_filter = filters.User(user_id=ALLOWED_USER_IDS) if ALLOWED_USER_IDS else filters.ALL

    # Register handlers
    application.add_handler(CommandHandler("start", start, filters=user_filter))
    application.add_handler(MessageHandler(filters.COMMAND & user_filter, handle_slash_command))
    application.add_handler(MessageHandler(filters.VOICE & user_filter, handle_voice_message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & user_filter, handle_text_message))

    # Register error handler
    application.add_error_handler(error_handler)

    # Start the Bot
    logger.info("Starting Telegram bot...")
    application.run_polling()

if __name__ == "__main__":
    main()
