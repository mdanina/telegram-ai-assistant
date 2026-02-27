#!/usr/bin/env python3
"""
Data OS: YouTube Collector

Collects key metrics from the YouTube Data API v3 and stores them in the SQLite database.
"""

import os
import sqlite3
from datetime import datetime
from googleapiclient.discovery import build

DB_FILE = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'aios_data.db')
API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")

def get_channel_stats(youtube, channel_id):
    """Retrieves statistics for a given YouTube channel."""
    request = youtube.channels().list(
        part="statistics",
        id=channel_id
    )
    response = request.execute()
    
    if 'items' in response and response['items']:
        return response['items'][0]['statistics']
    return {}

def collect_youtube_metrics(snapshot_id):
    """Collects all YouTube metrics and saves them to the database."""
    if not API_KEY or not CHANNEL_ID:
        print("YOUTUBE_API_KEY or YOUTUBE_CHANNEL_ID not set. Skipping YouTube metrics.")
        return

    youtube = build('youtube', 'v3', developerKey=API_KEY)
    stats = get_channel_stats(youtube, CHANNEL_ID)

    if not stats:
        print("Could not retrieve YouTube channel stats.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    metrics = [
        ('YouTube', 'Subscribers', stats.get('subscriberCount', 0), datetime.now().isoformat(), snapshot_id),
        ('YouTube', 'Total Views', stats.get('viewCount', 0), datetime.now().isoformat(), snapshot_id),
        ('YouTube', 'Total Videos', stats.get('videoCount', 0), datetime.now().isoformat(), snapshot_id),
    ]

    cursor.executemany(
        "INSERT INTO metrics (source, metric_name, value, date, snapshot_id) VALUES (?, ?, ?, ?, ?)",
        metrics
    )

    conn.commit()
    conn.close()
    print("Successfully collected YouTube metrics.")

if __name__ == "__main__":
    collect_youtube_metrics(f"manual_run_{datetime.now().isoformat()}")
