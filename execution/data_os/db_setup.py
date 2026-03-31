#!/usr/bin/env python3
"""
Data OS: Database Setup

This script creates the local SQLite database and the necessary tables to store
all business metrics.
"""

import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'aios_data.db')

def create_database():
    """Creates and initializes the SQLite database."""
    # Ensure the data directory exists
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create the main metrics table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            metric_name TEXT NOT NULL,
            value REAL NOT NULL,
            date TEXT NOT NULL,
            snapshot_id TEXT NOT NULL
        )
    """)

    # Create the tasks table for GTD reminders
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_text TEXT NOT NULL,
            next_action TEXT,
            project TEXT,
            context TEXT,
            delegated_to TEXT,
            due_date TEXT,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL,
            reminded_at TEXT,
            domain TEXT DEFAULT 'personal'
        )
    """)

    conn.commit()
    conn.close()
    print("Database and tables created successfully.")

if __name__ == "__main__":
    create_database()
