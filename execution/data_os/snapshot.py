#!/usr/bin/env python3
"""
Data OS: Snapshot Orchestrator

This script runs all the individual data collectors and creates a unified
data snapshot in the SQLite database.
"""

import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

from collectors.youtube_collector import collect_youtube_metrics
from collectors.google_analytics_collector import collect_ga_metrics
from collectors.sheets_collector import collect_sheets_metrics
from collectors.product_collector import collect_product_metrics
from collectors.yandex_metrika_collector import collect_metrika_metrics
from db_setup import create_database

# Each collector: (name, function) — isolated so one failure doesn't stop the rest
_COLLECTORS = [
    ("YouTube", collect_youtube_metrics),
    ("GoogleAnalytics", collect_ga_metrics),
    ("Sheets", collect_sheets_metrics),
    ("Product", collect_product_metrics),
    ("YandexMetrika", collect_metrika_metrics),
]


def run_snapshot():
    """Runs all data collectors to create a new snapshot.

    Each collector is wrapped in try/except so one failure
    doesn't prevent the others from running.
    """
    # Ensure the database and tables exist
    create_database()

    snapshot_id = f"snapshot_{datetime.now().isoformat()}"
    print(f"Starting data snapshot: {snapshot_id}")

    succeeded = 0
    failed = []
    for name, collector_fn in _COLLECTORS:
        try:
            collector_fn(snapshot_id)
            succeeded += 1
        except Exception as e:
            failed.append(name)
            logger.error("Collector %s failed: %s", name, e)

    if failed:
        print(f"Data snapshot complete: {snapshot_id} ({succeeded} OK, {len(failed)} failed: {', '.join(failed)})")
    else:
        print(f"Data snapshot complete: {snapshot_id} (all {succeeded} collectors OK)")

if __name__ == "__main__":
    run_snapshot()
