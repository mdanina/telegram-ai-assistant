#!/usr/bin/env python3
"""
Task OS: GTD Processor

Takes a raw task (from Telegram, voice, etc.), processes it with GTD methodology
via LLM, saves to SQLite, and prints structured result.
"""

import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common import get_openai_client, call_gpt, MODEL_MAIN

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "data_os"))
from db_router import classify_domain

# Moscow timezone (UTC+3) — server runs UTC, but user input is in Moscow time
_MSK = timezone(timedelta(hours=3))

DB_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "aios_data.db")


def load_context():
    """Loads the core business context from the context/ directory."""
    context = ""
    context_dir = os.path.join(os.path.dirname(__file__), "..", "..", "context")
    if not os.path.exists(context_dir):
        return ""
    for filename in sorted(os.listdir(context_dir)):
        if filename.endswith(".md"):
            with open(os.path.join(context_dir, filename), "r") as f:
                context += f"\n\n--- {filename} ---\n\n" + f.read()
    return context


def _save_task(raw_text, task_data):
    """Saves a processed task to the SQLite database."""
    conn = None
    try:
        os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Ensure tasks table exists
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

        domain = classify_domain(raw_text)

        cursor.execute(
            """INSERT INTO tasks (raw_text, next_action, project, context, delegated_to, due_date, status, created_at, domain)
               VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, ?)""",
            (
                raw_text,
                task_data.get("next_action"),
                task_data.get("project"),
                task_data.get("context"),
                task_data.get("delegated_to"),
                task_data.get("due_date"),
                datetime.now(_MSK).replace(tzinfo=None).isoformat(),
                domain,
            ),
        )
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Error saving task to DB: {e}")
        return None
    finally:
        if conn:
            conn.close()


def process_raw_task(raw_task_text):
    """Processes a raw task using an LLM to apply the GTD framework."""
    business_context = load_context()
    now = datetime.now(_MSK).replace(tzinfo=None)
    today = now.strftime("%Y-%m-%d %H:%M (%A)")
    tomorrow = (now + timedelta(days=1)).strftime("%Y-%m-%d")

    prompt = f"""You are a GTD task processor. Extract a structured task from the user's message.

Today: {today}

Business context:
{business_context}

User message:
{raw_task_text}

Return a JSON object with these fields:
- "next_action": the concrete action to take (short, in the user's language)
- "project": project name if part of a larger project, otherwise null
- "context": where to do it (@computer, @phone, @office), null if unclear
- "delegated_to": person to delegate to, null if self
- "due_date": deadline as "YYYY-MM-DD" or "YYYY-MM-DD HH:MM", null if none.
  Compute relative dates from today. "завтра" = {tomorrow}, etc.
- "is_someday_maybe": true if not urgent, false otherwise

IMPORTANT: "next_action" must be a clear, concise action — not a copy of the full message.
Return ONLY valid JSON, no markdown, no explanation.
"""

    try:
        msg = call_gpt(
            messages=[
                {"role": "system", "content": "You are a helpful GTD assistant. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            model=MODEL_MAIN,
            max_tokens=1024,
        )
        processed_task_json = (msg.content or "").strip()

        # Strip markdown code fences if present
        if processed_task_json.startswith("```"):
            lines = processed_task_json.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            processed_task_json = "\n".join(lines).strip()

        if not processed_task_json:
            print("GTD processor: GPT returned empty response")
            return None

        processed_task = json.loads(processed_task_json)

        # Save to database
        task_id = _save_task(raw_task_text, processed_task)

        # Print JSON for task_handler to parse
        print(json.dumps(processed_task, ensure_ascii=False))

        if task_id:
            print(f"[saved:id={task_id}]", flush=True)

        return processed_task

    except Exception as e:
        print(f"An error occurred during GTD processing: {e}")
        return None


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        raw_task = " ".join(sys.argv[1:])
    else:
        raw_task = sys.stdin.read().strip()

    if not raw_task:
        print("Usage: python gtd_processor.py <task text>")
        sys.exit(1)

    process_raw_task(raw_task)
