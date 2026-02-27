#!/usr/bin/env python3
"""
Data OS: Query Interface

This script provides a CLI for querying the metrics database using natural language.
"""

import os
import sqlite3
import argparse
import openai

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

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    schema = get_db_schema(cursor)

    prompt = f"""Given the following database schema:

{schema}

Convert the following natural language query into a SQL query:

'{natural_language_query}'

SQL Query:"""

    try:
        response = openai.Completion.create(
            engine="text-davinci-003", # Or another suitable model
            prompt=prompt,
            max_tokens=150,
            temperature=0.0,
            stop=[";"]
        )
        sql_query = response.choices[0].text.strip()

        print(f"Generated SQL: {sql_query}")
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

    # Make sure to set OPENAI_API_KEY in your environment
    openai.api_key = os.getenv("OPENAI_API_KEY")

    result = query_database(args.query)
    print("\n--- Query Results ---")
    print(result)
