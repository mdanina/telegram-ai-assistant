#!/usr/bin/env python3
"""
Intelligence Layer: Orchestrator

This script runs all intelligence gathering and analysis processes and
consolidates the output into a single daily report.
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

from fireflies_client import get_recent_transcripts
from meeting_analyzer import analyze_transcript
from slack_monitor import process_slack_messages
from voice_processor import process_voice_note

def run_intelligence_pipeline():
    """Runs the full intelligence pipeline for the day."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    report_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'intelligence_reports', f"{today_str}.json")

    full_report = {
        "date": today_str,
        "meetings": [],
        "slack": [],
        "voice_notes": []
    }

    # 1. Process Fireflies meetings
    print("--- Processing Fireflies Transcripts ---")
    transcripts = get_recent_transcripts()
    for transcript in transcripts:
        transcript_text = " ".join([sentence['text'] for sentence in transcript['sentences']])
        analysis = analyze_transcript(transcript_text)
        if analysis:
            full_report["meetings"].append({"title": transcript["title"], "analysis": analysis})

    # 2. Process Slack messages
    print("\n--- Processing Slack Messages ---")
    slack_analyses = process_slack_messages()
    full_report["slack"] = slack_analyses

    # 3. Process voice notes
    print("\n--- Processing Voice Notes ---")
    voice_notes_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "voice_notes")
    if os.path.exists(voice_notes_dir):
        for filename in os.listdir(voice_notes_dir):
            if filename.endswith(('.mp3', '.wav', '.m4a', '.ogg')):
                file_path = os.path.join(voice_notes_dir, filename)
                analysis = process_voice_note(file_path)
                if analysis:
                    full_report["voice_notes"].append({"filename": filename, "analysis": analysis})
                # Optional: remove the file after processing
                # os.remove(file_path)

    # Save the consolidated report
    with open(report_path, "w") as f:
        json.dump(full_report, f, indent=2)

    print(f"\nIntelligence pipeline complete. Report saved to {report_path}")

if __name__ == "__main__":
    run_intelligence_pipeline()
