#!/usr/bin/env python3
"""
Data OS: Google Sheets Collector

Collects key metrics from a Google Sheet (e.g., P&L) and stores them in the SQLite database.
"""

import os
import gspread
import sqlite3
from datetime import datetime
from google.oauth2.service_account import Credentials

DB_FILE = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'aios_data.db')
SHEET_ID = os.getenv("FINANCE_SHEET_ID")
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

def get_sheet_data():
    """Retrieves data from the specified Google Sheet."""
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path:
        return None
    creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).sheet1
    return sheet.get_all_records()

def collect_sheets_metrics(snapshot_id):
    """Collects all Google Sheets metrics and saves them to the database."""
    if not SHEET_ID or not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        print("FINANCE_SHEET_ID or GOOGLE_APPLICATION_CREDENTIALS not set. Skipping Google Sheets metrics.")
        return

    data = get_sheet_data()
    if not data:
        print("Could not retrieve Google Sheets data.")
        return

    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # This is a placeholder - you'll need to adapt this to your sheet's structure
        # For example, assuming a sheet with 'Date', 'Metric', and 'Value' columns
        metrics = []
        for row in data:
            if 'Date' in row and 'Metric' in row and 'Value' in row:
                metrics.append((
                    'Google Sheets',
                    row['Metric'],
                    row['Value'],
                    row['Date'],
                    snapshot_id
                ))

        cursor.executemany(
            "INSERT INTO metrics (source, metric_name, value, date, snapshot_id) VALUES (?, ?, ?, ?, ?)",
            metrics
        )

        conn.commit()
        print("Successfully collected Google Sheets metrics.")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    collect_sheets_metrics(f"manual_run_{datetime.now().isoformat()}")
