#!/usr/bin/env python3
"""
Telegram Bot: Photo Handler

Receives photos, saves them to data/inbox/, analyzes with GPT-4o Vision,
and routes the analysis through the AI handler for an intelligent response.
No duplicate messages — user sees only the final AI response.
"""

import os
import sys
import base64
import asyncio
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from task_handler import handle_text_message, _react

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common import get_openai_client, MODEL_MAIN

logger = logging.getLogger(__name__)

INBOX_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "inbox")


def _analyze_image(image_path):
    """Sends an image to GPT-4o Vision for analysis."""
    try:
        client = get_openai_client()
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")

        response = client.chat.completions.create(
            model=MODEL_MAIN,
            max_completion_tokens=1024,
            timeout=30,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an assistant that analyzes images sent by the CEO. "
                        "Extract all text (OCR), describe what you see, and if there's "
                        "an actionable item (meeting invite, task, deadline, receipt), "
                        "highlight it clearly. Respond in the same language as the text "
                        "in the image (Russian or English). Be concise."
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze this image:"},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                        },
                    ],
                },
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Vision analysis error: {e}")
        return None


async def handle_photo_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Downloads a photo, saves it, analyzes with Vision, and routes to AI."""
    caption = update.message.caption or ""

    # If caption starts with a slash command, route to slash handler
    if caption.strip().startswith("/"):
        from slash_commands import handle_slash_command
        cmd = caption.strip().split()[0].lower()

        # /bal and /cc benefit from seeing the screenshot — analyze first
        if cmd in ("/bal", "/cc"):
            await _react(update.message, "📷")
            await update.message.chat.send_action("typing")
            photo = update.message.photo[-1]
            photo_file = await photo.get_file()
            os.makedirs(INBOX_DIR, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            fpath = os.path.join(INBOX_DIR, f"photo_{ts}.jpg")
            await photo_file.download_to_drive(fpath)
            loop = asyncio.get_running_loop()
            analysis = await loop.run_in_executor(None, _analyze_image, fpath)
            if analysis:
                context.user_data["_photo_analysis"] = analysis
                logger.info(f"Photo analyzed for {cmd}: {analysis[:100]}")

        try:
            await handle_slash_command(update, context)
        except Exception as e:
            logger.error(f"Slash command from caption error: {e}")
            await update.message.reply_text(f"Ошибка команды: {e}")
        return

    # Ack: show we received the photo
    await _react(update.message, "📷")
    await update.message.chat.send_action("typing")

    # Get the highest resolution photo
    photo = update.message.photo[-1]
    photo_file = await photo.get_file()

    # Save to inbox
    os.makedirs(INBOX_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(INBOX_DIR, f"photo_{timestamp}.jpg")
    await photo_file.download_to_drive(file_path)

    logger.info(f"Photo saved: {file_path}")

    # Analyze with Vision
    await update.message.chat.send_action("typing")
    loop = asyncio.get_running_loop()
    analysis = await loop.run_in_executor(None, _analyze_image, file_path)

    if analysis:
        # Route through AI handler with analysis context
        if caption.strip():
            synthetic_text = f"[Фото: {analysis[:500]}]\n\n{caption}"
        else:
            synthetic_text = (
                f"[Фото: {analysis[:500]}]\n\n"
                f"Что ты видишь на этом фото? Есть ли тут что-то важное?"
            )
        context.user_data["_photo_text_override"] = synthetic_text
        await handle_text_message(update, context)
    else:
        await update.message.reply_text(
            "Фото сохранено, но не удалось проанализировать. "
            "Попробуй отправить ещё раз или опиши что на фото текстом."
        )
