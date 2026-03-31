#!/usr/bin/env python3
"""
Intelligence Layer: Voice Processor

Transcribes audio notes using the Whisper API and sends the
transcription to the analysis pipeline.
"""

import os
from openai import OpenAI
from meeting_analyzer import analyze_transcript


def transcribe_audio(file_path):
    """Transcribes an audio file using OpenAI Whisper."""
    if not os.path.exists(file_path):
        print(f"Audio file not found: {file_path}")
        return None

    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        with open(file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
            )
        return transcript.text
    except Exception as e:
        print(f"Error during audio transcription: {e}")
        return None


def process_voice_note(file_path):
    """Transcribes and analyzes a single voice note."""
    print(f"Processing voice note: {file_path}")
    transcription = transcribe_audio(file_path)

    if transcription:
        print("Transcription successful. Analyzing content...")
        analysis = analyze_transcript(transcription)
        return analysis
    else:
        print("Transcription failed. Skipping analysis.")
        return None


if __name__ == "__main__":
    voice_notes_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "voice_notes")
    if not os.path.exists(voice_notes_dir):
        os.makedirs(voice_notes_dir)
        print(f"Created directory: {voice_notes_dir}")
        print("Place your audio files (.mp3, .wav, .m4a, .ogg) here.")

    for filename in os.listdir(voice_notes_dir):
        if filename.endswith(('.mp3', '.wav', '.m4a', '.ogg')):
            file_path = os.path.join(voice_notes_dir, filename)
            analysis = process_voice_note(file_path)
            if analysis:
                print(f"Analysis for {filename}:\n{analysis}")
