#!/usr/bin/env python3
"""
Intelligence Layer: Orchestrator

Runs all intelligence gathering and analysis processes and
consolidates the output into a single daily report.
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

from meeting_analyzer import analyze_transcript
from voice_processor import process_voice_note

# Optional sources — import only if available
try:
    from fireflies_client import get_recent_transcripts
    HAS_FIREFLIES = True
except Exception:
    HAS_FIREFLIES = False

def run_intelligence_pipeline():
    """Runs the full intelligence pipeline for the day."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    reports_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'intelligence_reports')
    os.makedirs(reports_dir, exist_ok=True)
    report_path = os.path.join(reports_dir, f"{today_str}.json")

    full_report = {
        "date": today_str,
        "meetings": [],
        "voice_notes": []
    }

    # 1. Process Fireflies meetings
    if HAS_FIREFLIES:
        print("--- Processing Fireflies Transcripts ---")
        try:
            transcripts = get_recent_transcripts()
            for transcript in transcripts:
                transcript_text = " ".join([s['text'] for s in transcript.get('sentences', [])])
                analysis = analyze_transcript(transcript_text)
                if analysis:
                    full_report["meetings"].append({"title": transcript["title"], "analysis": analysis})
        except Exception as e:
            print(f"Fireflies error: {e}")
    else:
        print("Fireflies not configured, skipping meetings.")

    # 2. Process voice notes
    print("\n--- Processing Voice Notes ---")
    voice_notes_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "voice_notes")
    if os.path.exists(voice_notes_dir):
        for filename in os.listdir(voice_notes_dir):
            if filename.endswith(('.mp3', '.wav', '.m4a', '.ogg')):
                file_path = os.path.join(voice_notes_dir, filename)
                analysis = process_voice_note(file_path)
                if analysis:
                    full_report["voice_notes"].append({"filename": filename, "analysis": analysis})

    # Save the consolidated report
    with open(report_path, "w") as f:
        json.dump(full_report, f, indent=2)

    print(f"\nIntelligence pipeline complete. Report saved to {report_path}")


if __name__ == "__main__":
    run_intelligence_pipeline()
