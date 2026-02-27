#!/usr/bin/env python3
"""
Data OS: Snapshot Orchestrator

This script runs all the individual data collectors and creates a unified
data snapshot in the SQLite database.
"""

import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

from collectors.stripe_collector import collect_stripe_metrics
from collectors.youtube_collector import collect_youtube_metrics
from collectors.google_analytics_collector import collect_ga_metrics
from collectors.sheets_collector import collect_sheets_metrics
from collectors.bitly_collector import collect_bitly_metrics
from db_setup import create_database

def run_snapshot():
    """Runs all data collectors to create a new snapshot."""
    # Ensure the database and tables exist
    create_database()
    
    snapshot_id = f"snapshot_{datetime.now().isoformat()}"
    print(f"Starting data snapshot: {snapshot_id}")

    # Run each collector
    collect_stripe_metrics(snapshot_id)
    collect_youtube_metrics(snapshot_id)
    collect_ga_metrics(snapshot_id)
    collect_sheets_metrics(snapshot_id)
    collect_bitly_metrics(snapshot_id)

    print(f"Data snapshot complete: {snapshot_id}")

if __name__ == "__main__":
    run_snapshot()
