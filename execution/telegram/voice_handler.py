#!/usr/bin/env python3
"""
Telegram Bot: Voice Message Handler

This script handles incoming voice messages, transcribes them, and processes them.
"""

import os
import json
from telegram import Update
from telegram.ext import ContextTypes
from ..intelligence.voice_processor import process_voice_note

VOICE_NOTES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "voice_notes")

async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Downloads, transcribes, and analyzes a voice message."""
    voice_file = await update.message.voice.get_file()
    
    # Ensure the directory exists
    os.makedirs(VOICE_NOTES_DIR, exist_ok=True)
    file_path = os.path.join(VOICE_NOTES_DIR, f"{voice_file.file_id}.ogg")

    await voice_file.download_to_drive(file_path)
    await update.message.reply_text("Voice note received. Transcribing and analyzing...")

    # Process the voice note using the intelligence layer script
    analysis = process_voice_note(file_path)

    if analysis:
        # For now, just send the raw analysis back. A more advanced system
        # would route the tasks to the GTD processor.
        response_text = f"**Voice Note Analysis:**\n\n```json\n{json.dumps(analysis, indent=2)}\n```"
        await update.message.reply_text(response_text, parse_mode="MarkdownV2")
    else:
        await update.message.reply_text("Could not analyze the voice note.")

    # Clean up the downloaded file
    os.remove(file_path)
