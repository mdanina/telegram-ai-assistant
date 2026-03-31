#!/usr/bin/env python3
"""
Text-to-Speech via edge-tts (Microsoft Edge, free).

Converts text to OGG voice message compatible with Telegram.
"""

import os
import tempfile
import asyncio
import logging

logger = logging.getLogger(__name__)

# Russian male voice (natural, clear)
VOICE = os.getenv("AIOS_TTS_VOICE", "ru-RU-DmitryNeural")

# Max text length for TTS (longer texts are truncated)
MAX_TTS_CHARS = 4000

# Language → male voice mapping for edge-tts
LANG_VOICES = {
    "ru": "ru-RU-DmitryNeural",
    "en": "en-US-GuyNeural",
    "tr": "tr-TR-AhmetNeural",
    "es": "es-ES-AlvaroNeural",
    "fr": "fr-FR-HenriNeural",
    "de": "de-DE-ConradNeural",
    "it": "it-IT-DiegoNeural",
    "pt": "pt-BR-AntonioNeural",
    "zh": "zh-CN-YunxiNeural",
    "ja": "ja-JP-KeitaNeural",
    "ko": "ko-KR-InJoonNeural",
    "ar": "ar-SA-HamedNeural",
    "hi": "hi-IN-MadhurNeural",
    "th": "th-TH-NiwatNeural",
    "vi": "vi-VN-NamMinhNeural",
    "el": "el-GR-NestorasNeural",
    "pl": "pl-PL-MarekNeural",
    "uk": "uk-UA-OstapNeural",
    "cs": "cs-CZ-AntoninNeural",
    "nl": "nl-NL-MaartenNeural",
    "sv": "sv-SE-MattiasNeural",
    "he": "he-IL-AvriNeural",
    "id": "id-ID-ArdiNeural",
}

# Language code → human-readable name (for GPT translation prompts)
LANG_NAMES = {
    "ru": "Russian", "en": "English", "tr": "Turkish", "es": "Spanish",
    "fr": "French", "de": "German", "it": "Italian", "pt": "Portuguese",
    "zh": "Chinese", "ja": "Japanese", "ko": "Korean", "ar": "Arabic",
    "hi": "Hindi", "th": "Thai", "vi": "Vietnamese", "el": "Greek",
    "pl": "Polish", "uk": "Ukrainian", "cs": "Czech", "nl": "Dutch",
    "sv": "Swedish", "he": "Hebrew", "id": "Indonesian",
}


async def text_to_voice(text: str, voice: str | None = None) -> str | None:
    """Converts text to an OGG audio file. Returns file path or None on error.

    Args:
        text: Text to speak.
        voice: Optional edge-tts voice name or language code (e.g. "tr", "en").
    Caller is responsible for deleting the file after use.
    """
    try:
        import edge_tts
    except ImportError:
        logger.error("edge-tts not installed. Run: pip install edge-tts")
        return None

    if not text or not text.strip():
        return None

    # Resolve voice: lang code → full voice name, or use default
    resolved_voice = VOICE
    if voice:
        if voice.lower() in LANG_VOICES:
            resolved_voice = LANG_VOICES[voice.lower()]
        elif "-" in voice:  # full voice name like "tr-TR-AhmetNeural"
            resolved_voice = voice

    # Clean text for speech: remove markdown-like formatting
    clean = text.strip()
    if len(clean) > MAX_TTS_CHARS:
        clean = clean[:MAX_TTS_CHARS]

    try:
        # edge-tts outputs mp3 by default
        tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        tmp_path = tmp.name
        tmp.close()

        communicate = edge_tts.Communicate(clean, resolved_voice)
        await communicate.save(tmp_path)

        # Check file was created and has content
        if not os.path.exists(tmp_path) or os.path.getsize(tmp_path) < 100:
            logger.warning("TTS produced empty or tiny file")
            _safe_remove(tmp_path)
            return None

        return tmp_path

    except Exception as e:
        logger.error(f"TTS error: {e}")
        _safe_remove(tmp_path)
        return None


def _safe_remove(path):
    """Remove file if it exists, ignore errors."""
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except OSError:
        pass
