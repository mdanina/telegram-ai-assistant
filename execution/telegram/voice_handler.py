#!/usr/bin/env python3
"""
Telegram Bot: Voice Message Handler

Downloads voice messages, transcribes via Whisper, then routes
the transcription through the AI handler as if user typed it.

If the voice contains multiple action items / tasks, they are
extracted and created in GTD automatically (batch mode).
"""

import os
import sys
import json
import sqlite3
import asyncio
import logging
from datetime import datetime, timedelta, timezone
from telegram import Update
from telegram.ext import ContextTypes
from task_handler import handle_text_message, _react

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common import get_openai_client, MODEL_FAST

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "data_os"))
from db_router import classify_domain

logger = logging.getLogger(__name__)

# Moscow timezone (UTC+3)
_MSK = timezone(timedelta(hours=3))

VOICE_NOTES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "voice_notes")
DB_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "aios_data.db")


_whisper_model = None


def _get_whisper_model():
    """Lazy-load faster-whisper model (stays in RAM until process exits)."""
    global _whisper_model
    if _whisper_model is None:
        try:
            from faster_whisper import WhisperModel
            _whisper_model = WhisperModel(
                "base",
                device="cpu",
                compute_type="int8",  # Quantized — 2x faster, less RAM
            )
            logger.info("Local Whisper model loaded (base, int8)")
        except ImportError:
            logger.warning("faster-whisper not installed, falling back to OpenAI API")
            _whisper_model = "api_fallback"
    return _whisper_model


def _transcribe(file_path):
    """Transcribes audio using OpenAI Whisper API (primary).
    Falls back to local faster-whisper if API unavailable.
    """
    # Primary: OpenAI API (better quality for Russian)
    try:
        client = get_openai_client()
        with open(file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="ru",
            )
        logger.info(f"Whisper API: transcribed {len(transcript.text)} chars")
        return transcript.text
    except Exception as e:
        logger.warning(f"Whisper API error: {e}, falling back to local model")

    # Fallback: local faster-whisper
    model = _get_whisper_model()
    if model != "api_fallback":
        try:
            segments, info = model.transcribe(
                file_path,
                language="ru",
                beam_size=3,
                vad_filter=True,
            )
            text = " ".join(seg.text.strip() for seg in segments)
            logger.info(f"Local Whisper fallback: {info.duration:.1f}s audio → {len(text)} chars")
            return text if text.strip() else None
        except Exception as e:
            logger.error(f"Local Whisper fallback error: {e}")

    return None


async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Downloads, transcribes, and routes a voice message through the AI handler."""
    # Ack: show the user we received the voice
    await _react(update.message, "🎙")

    voice_file = await update.message.voice.get_file()

    os.makedirs(VOICE_NOTES_DIR, exist_ok=True)
    file_path = os.path.join(VOICE_NOTES_DIR, f"{voice_file.file_id}.ogg")

    await voice_file.download_to_drive(file_path)

    # Typing while transcribing
    await update.message.chat.send_action("typing")
    loop = asyncio.get_running_loop()
    transcription = await loop.run_in_executor(None, _transcribe, file_path)

    # Clean up temp file
    try:
        os.remove(file_path)
    except OSError:
        pass

    if not transcription:
        await update.message.reply_text(
            "Не удалось расшифровать голосовое сообщение. "
            "Попробуй записать ещё раз — возможно, было слишком тихо."
        )
        return

    # Try to extract multiple tasks from the voice message
    tasks = await loop.run_in_executor(None, _extract_voice_tasks, transcription)

    if tasks and len(tasks) >= 2:
        # Batch mode: create all tasks in GTD and confirm
        created = _save_batch_tasks(tasks, transcription)
        if created:
            lines = [f"Создано {len(created)} задач из голосового:"]
            for t in created:
                due = f" (до {t['due_date']})" if t.get("due_date") else ""
                lines.append(f"  + {t['next_action']}{due}")
            await update.message.reply_text("\n".join(lines))
            return

    # Default: route through AI handler as before
    context.user_data["_photo_text_override"] = f"[Голосовое: {transcription}]"
    await handle_text_message(update, context)


def _extract_voice_tasks(transcription):
    """Uses LLM to check if voice contains multiple action items.

    Returns list of task dicts if >=2 tasks found, else None.
    """
    try:
        client = get_openai_client()

        now = datetime.now(_MSK).replace(tzinfo=None)
        today = now.strftime("%Y-%m-%d (%A)")
        tomorrow = (now + timedelta(days=1)).strftime("%Y-%m-%d")

        response = client.chat.completions.create(
            model=MODEL_FAST,
            max_completion_tokens=1024,
            messages=[
                {"role": "system", "content": "Ты извлекаешь задачи из голосовых заметок. Отвечай ТОЛЬКО валидным JSON."},
                {"role": "user", "content": f"""Проанализируй текст голосового сообщения. Если в нём есть 2 или более конкретных задач/действий — извлеки их.
Если это обычный разговор, вопрос или одна задача — верни пустой массив [].

Сегодня: {today}. "Завтра" = {tomorrow}.

Текст: {transcription}

Верни JSON массив задач:
[{{"next_action": "конкретное действие", "project": "проект или null", "due_date": "YYYY-MM-DD или null"}}]

Если задач меньше 2 — верни [].
Только JSON, без markdown."""}
            ],
        )

        content = (response.choices[0].message.content or "").strip()
        if content.startswith("```"):
            lines = content.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            content = "\n".join(lines).strip()

        tasks = json.loads(content)
        if isinstance(tasks, list) and len(tasks) >= 2:
            return tasks
        return None

    except Exception as e:
        logger.warning(f"Voice task extraction error: {e}")
        return None


def _save_batch_tasks(tasks, transcription=""):
    """Saves multiple tasks to GTD database. Returns list of saved tasks."""
    saved = []
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        # Classify domain from the original transcription (has full context)
        domain = classify_domain(transcription) if transcription else "personal"
        for t in tasks:
            action = t.get("next_action", "").strip()
            if not action:
                continue
            raw_text = f"[Из голосового] {action}"
            cursor.execute(
                """INSERT INTO tasks (raw_text, next_action, project, due_date, status, created_at, domain)
                   VALUES (?, ?, ?, ?, 'pending', ?, ?)""",
                (
                    raw_text,
                    action,
                    t.get("project"),
                    t.get("due_date"),
                    datetime.now(_MSK).replace(tzinfo=None).isoformat(),
                    domain,
                )
            )
            saved.append(t)
        conn.commit()
    except Exception as e:
        logger.error(f"Batch task save error: {e}")
    finally:
        if conn:
            conn.close()
    return saved
