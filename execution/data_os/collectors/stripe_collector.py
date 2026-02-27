#!/usr/bin/env python3
"""
Data OS: Stripe Collector

Collects key metrics from the Stripe API and stores them in the SQLite database.
"""

import os
import stripe
import sqlite3
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'aios_data.db')
API_KEY = os.getenv("STRIPE_API_KEY")

def get_mrr():
    """Retrieves the total Monthly Recurring Revenue from Stripe."""
    stripe.api_key = API_KEY
    subscriptions = stripe.Subscription.list(status='active', limit=100)
    mrr = 0
    for sub in subscriptions.auto_paging_iter():
        mrr += sub['items']['data'][0]['price']['unit_amount'] / 100
    return mrr

def collect_stripe_metrics(snapshot_id):
    """Collects all Stripe metrics and saves them to the database."""
    if not API_KEY:
        print("STRIPE_API_KEY not set. Skipping Stripe metrics.")
        return

    mrr = get_mrr()

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    metrics = [
        ('Stripe', 'MRR', mrr, datetime.now().isoformat(), snapshot_id),
    ]

    cursor.executemany(
        "INSERT INTO metrics (source, metric_name, value, date, snapshot_id) VALUES (?, ?, ?, ?, ?)",
        metrics
    )

    conn.commit()
    conn.close()
    print("Successfully collected Stripe metrics.")

if __name__ == "__main__":
    collect_stripe_metrics(f"manual_run_{datetime.now().isoformat()}")
