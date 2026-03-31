#!/usr/bin/env python3
"""
Migration 001: Add domain column to tasks table.

Adds a `domain` column (product / secondary_product / personal) for
multi-business separation. Default is 'personal'.

Run once on server:
    cd /opt/aios
    venv/bin/python execution/data_os/migrations/001_add_domain.py
"""

import os
import sqlite3

DB_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "aios_data.db")


def migrate():
    if not os.path.exists(DB_FILE):
        print(f"DB not found: {DB_FILE}")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Add domain column (idempotent)
    try:
        cursor.execute("ALTER TABLE tasks ADD COLUMN domain TEXT DEFAULT 'personal'")
        print("Added 'domain' column to tasks table.")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("Column 'domain' already exists, skipping.")
        else:
            raise

    # Backfill: tasks with Product-related content → 'product'
    updated = cursor.execute("""
        UPDATE tasks SET domain = 'product'
        WHERE domain = 'personal' AND (
            lower(raw_text) LIKE '%балансит%'
            OR lower(raw_text) LIKE '%your_product%'
            OR lower(raw_text) LIKE '%клиент%'
            OR lower(raw_text) LIKE '%специалист%'
            OR lower(raw_text) LIKE '%консультац%'
            OR lower(raw_text) LIKE '%маршрут%'
            OR lower(project) LIKE '%балансит%'
            OR lower(project) LIKE '%your_product%'
        )
    """).rowcount
    print(f"Backfilled {updated} tasks as 'product'.")

    conn.commit()
    conn.close()
    print("Migration 001 complete.")


if __name__ == "__main__":
    migrate()
