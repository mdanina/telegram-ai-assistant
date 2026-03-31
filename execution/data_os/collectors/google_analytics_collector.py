#!/usr/bin/env python3
"""
Data OS: Google Analytics Collector

Collects key metrics from the Google Analytics Data API (GA4) and stores them in the SQLite database.
"""

import os
import sqlite3
from datetime import datetime
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest

DB_FILE = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'aios_data.db')
PROPERTY_ID = os.getenv("GA4_PROPERTY_ID")

def get_ga_report(client):
    """Runs a report on GA4 to get key metrics."""
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name="date")],
        metrics=[
            Metric(name="activeUsers"),
            Metric(name="newUsers"),
            Metric(name="totalRevenue")
        ],
        date_ranges=[DateRange(start_date="yesterday", end_date="today")],
    )
    response = client.run_report(request)
    return response

def collect_ga_metrics(snapshot_id):
    """Collects all Google Analytics metrics and saves them to the database."""
    if not PROPERTY_ID or not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        print("GA4_PROPERTY_ID or GOOGLE_APPLICATION_CREDENTIALS not set. Skipping GA metrics.")
        return

    client = BetaAnalyticsDataClient()
    report = get_ga_report(client)

    if not report.rows:
        print("Could not retrieve Google Analytics report.")
        return

    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        metrics = []
        for row in report.rows:
            metrics.append((
                'Google Analytics',
                'Active Users',
                row.metric_values[0].value,
                row.dimension_values[0].value,
                snapshot_id
            ))
            metrics.append((
                'Google Analytics',
                'New Users',
                row.metric_values[1].value,
                row.dimension_values[0].value,
                snapshot_id
            ))
            metrics.append((
                'Google Analytics',
                'Total Revenue',
                row.metric_values[2].value,
                row.dimension_values[0].value,
                snapshot_id
            ))

        cursor.executemany(
            "INSERT INTO metrics (source, metric_name, value, date, snapshot_id) VALUES (?, ?, ?, ?, ?)",
            metrics
        )

        conn.commit()
        print("Successfully collected Google Analytics metrics.")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    collect_ga_metrics(f"manual_run_{datetime.now().isoformat()}")
