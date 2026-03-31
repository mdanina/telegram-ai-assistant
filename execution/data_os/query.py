#!/usr/bin/env python3
"""
Data OS: Query Interface

This script provides a CLI for querying the metrics database using natural language.
"""

import os
import sys
import sqlite3
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common import call_gpt, MODEL_MAIN

DB_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'aios_data.db')

def get_db_schema(cursor):
    """Returns the database schema as a string."""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    schema = ""
    for table_name in tables:
        table_name = table_name[0]
        schema += f"Table {table_name}:\n"
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        for col in columns:
            schema += f"  {col[1]} {col[2]}\n"
    return schema

def query_database(natural_language_query):
    """Converts a natural language query to SQL and executes it."""
    if not os.path.exists(DB_FILE):
        return "Database file not found. Please run the snapshot first."

    # Read-only connection — prevents destructive queries even if LLM generates them
    conn = sqlite3.connect(f"file:{DB_FILE}?mode=ro", uri=True)
    cursor = conn.cursor()

    schema = get_db_schema(cursor)

    prompt = f"""Given the following database schema:

{schema}

Domain separation notes:
- The `metrics` table has a `source` column that identifies data origin:
  Product sources: 'Product', 'YandexMetrika'
  Personal sources: 'YouTube', 'GoogleAnalytics', 'Sheets'
- The `tasks` table has a `domain` column: 'product', 'secondary_product', or 'personal'
- When user asks about a specific business (e.g. "метрики Product"), filter by the relevant source/domain values

Convert the following natural language query into a SQL query. Return only the SQL query, nothing else.

Query: '{natural_language_query}'

SQL:"""

    try:
        msg = call_gpt(
            messages=[
                {"role": "system", "content": "Convert natural language to SQL. Return only the SQL query, nothing else."},
                {"role": "user", "content": prompt}
            ],
            model=MODEL_MAIN,
            max_tokens=150,
        )
        sql_query = msg.content.strip()

        # Strip any trailing semicolon for safety
        sql_query = sql_query.rstrip(';')

        # Only allow SELECT queries
        if not sql_query.strip().upper().startswith("SELECT"):
            return "Только SELECT-запросы разрешены."

        # Enforce LIMIT to prevent runaway queries
        if "LIMIT" not in sql_query.upper():
            sql_query += " LIMIT 1000"

        print(f"Generated SQL: {sql_query}")
        conn.execute("PRAGMA busy_timeout = 5000")
        cursor.execute(sql_query)
        results = cursor.fetchall()

        # Get column names
        col_names = [description[0] for description in cursor.description]

        # Format results
        formatted_results = "\t".join(col_names) + "\n"
        for row in results:
            formatted_results += "\t".join(map(str, row)) + "\n"

        return formatted_results

    except Exception as e:
        return f"An error occurred: {e}"
    finally:
        conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query the AIOS database with natural language.")
    parser.add_argument("query", type=str, help="The natural language query to execute.")
    args = parser.parse_args()

    result = query_database(args.query)
    print("\n--- Query Results ---")
    print(result)
