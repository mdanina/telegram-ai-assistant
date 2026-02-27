#!/usr/bin/env python3
"""
Telegram Bot: Text Message (Task) Handler

This script handles incoming text messages, treating them as new tasks for the GTD system.
"""

from telegram import Update
from telegram.ext import ContextTypes
from ..task_os.gtd_processor import process_raw_task

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processes a raw text message as a new task."""
    raw_task = update.message.text
    await update.message.reply_text(f"Task received: ‘{raw_task}’. Processing with GTD system...")

    # Process the task using the GTD processor
    # This is a simplified integration. The gtd_processor would ideally return a status.
    try:
        # In a real system, you might pass the user ID to the processor
        process_raw_task(raw_task)
        await update.message.reply_text("Task processed and added to your system.")
    except Exception as e:
        await update.message.reply_text(f"Could not process task: {e}")
