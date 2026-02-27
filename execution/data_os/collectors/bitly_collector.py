#!/usr/bin/env python3
"""
Data OS: Bitly Collector

Collects key metrics from the Bitly API and stores them in the SQLite database.
"""

import os
import bitly_api
import sqlite3
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'aios_data.db')
BITLY_API_TOKEN = os.getenv("BITLY_API_TOKEN")

def get_bitly_clicks(bitly):
    """Retrieves click counts for all Bitly links."""
    # This is a simplified example. You might need to handle pagination
    # and select specific links based on your needs.
    response = bitly.get_user_metrics(unit='day', units=1, rollup=True)
    return response

def collect_bitly_metrics(snapshot_id):
    """Collects all Bitly metrics and saves them to the database."""
    if not BITLY_API_TOKEN:
        print("BITLY_API_TOKEN not set. Skipping Bitly metrics.")
        return

    bitly = bitly_api.Connection(access_token=BITLY_API_TOKEN)
    clicks_data = get_bitly_clicks(bitly)

    if not clicks_data:
        print("Could not retrieve Bitly metrics.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    metrics = []
    for item in clicks_data['link_clicks']:
        metrics.append((
            'Bitly',
            'Link Clicks',
            item['clicks'],
            item['dt'],
            snapshot_id
        ))

    cursor.executemany(
        "INSERT INTO metrics (source, metric_name, value, date, snapshot_id) VALUES (?, ?, ?, ?, ?)",
        metrics
    )

    conn.commit()
    conn.close()
    print("Successfully collected Bitly metrics.")

if __name__ == "__main__":
    collect_bitly_metrics(f"manual_run_{datetime.now().isoformat()}")
