#!/usr/bin/env python3
"""
Intelligence Layer: Slack Monitor

This script monitors a specified Slack channel for messages and runs them through
the analysis pipeline.
"""

import os
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from meeting_analyzer import analyze_transcript # Re-using the analyzer for consistency

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
CHANNEL_ID = os.getenv("SLACK_MONITOR_CHANNEL_ID")

def fetch_recent_messages(client, channel_id):
    """Fetches messages from the last 24 hours from a Slack channel."""
    try:
        result = client.conversations_history(
            channel=channel_id,
            oldest=str(time.time() - 24 * 60 * 60) # 24 hours ago
        )
        return result["messages"]
    except SlackApiError as e:
        print(f"Error fetching Slack messages: {e}")
        return []

def process_slack_messages():
    """Fetches and analyzes recent Slack messages."""
    if not SLACK_BOT_TOKEN or not CHANNEL_ID:
        print("SLACK_BOT_TOKEN or SLACK_MONITOR_CHANNEL_ID not set. Skipping Slack monitoring.")
        return []

    client = WebClient(token=SLACK_BOT_TOKEN)
    messages = fetch_recent_messages(client, CHANNEL_ID)
    
    all_analyses = []
    for message in messages:
        # We only care about top-level messages, not replies in this simple case
        if 'thread_ts' not in message and 'text' in message:
            print(f"Analyzing Slack message: {message['text'][:50]}...")
            # We treat each message as a mini-transcript
            analysis = analyze_transcript(f"{message['user']}: {message['text']}")
            if analysis:
                all_analyses.append(analysis)
    
    return all_analyses

if __name__ == "__main__":
    analyses = process_slack_messages()
    if analyses:
        print(f"Successfully analyzed {len(analyses)} Slack messages.")
    else:
        print("No new Slack messages to analyze.")
