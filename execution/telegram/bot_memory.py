#!/usr/bin/env python3
"""
Bot Memory: SQLite-based conversation history and long-term memory.

Replaces the in-memory _conversation_history dict in task_handler.py.
Two storage layers:
  1. conversation_history — full chat log, persists across restarts
  2. bot_memories — long-term facts extracted from conversations (preferences, names, etc.)
"""

import os
import json
import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

DB_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "aios_data.db")
MAX_HISTORY = 30  # Messages to send to GPT per conversation


def _get_conn():
    """Returns a SQLite connection with row_factory.

    Use as context manager for automatic close:
        with _get_conn() as conn:
            conn.execute(...)
    """
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


class _DBConn:
    """Context manager that guarantees conn.close() even on exceptions."""
    def __enter__(self):
        self.conn = _get_conn()
        return self.conn
    def __exit__(self, *exc):
        self.conn.close()
        return False


def init_memory_tables():
    """Creates memory tables if they don't exist. Safe to call multiple times."""
    conn = _get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bot_memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            memory TEXT NOT NULL,
            source_message TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            last_used_at TEXT
        )
    """)

    # Index for fast lookups
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_conv_user
        ON conversation_history(user_id, created_at DESC)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_mem_user
        ON bot_memories(user_id)
    """)

    conn.commit()
    conn.close()
    logger.info("Memory tables initialized.")


# ── Conversation History ──

def get_history(user_id: int) -> list[dict]:
    """Gets last MAX_HISTORY messages for a user. Returns list of {role, content}."""
    with _DBConn() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT role, content FROM (
                SELECT role, content, created_at
                FROM conversation_history
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ) sub ORDER BY created_at ASC
        """, (user_id, MAX_HISTORY))
        rows = cursor.fetchall()
        return [{"role": r["role"], "content": r["content"]} for r in rows]


def add_to_history(user_id: int, role: str, content: str):
    """Saves a message to conversation history."""
    with _DBConn() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO conversation_history (user_id, role, content)
            VALUES (?, ?, ?)
        """, (user_id, role, content))

        # Prune old messages beyond 200 per user (keep DB lean)
        cursor.execute("""
            DELETE FROM conversation_history
            WHERE id NOT IN (
                SELECT id FROM conversation_history
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT 200
            ) AND user_id = ?
        """, (user_id, user_id))
        conn.commit()


def clear_history(user_id: int):
    """Clears all conversation history for a user (e.g. /newchat)."""
    with _DBConn() as conn:
        conn.execute("DELETE FROM conversation_history WHERE user_id = ?", (user_id,))
        conn.commit()


def get_history_count(user_id: int) -> int:
    """Returns total number of messages in conversation history for a user."""
    with _DBConn() as conn:
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM conversation_history WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        return row["cnt"] if row else 0


def get_memory_count(user_id: int) -> int:
    """Returns total number of long-term memories for a user."""
    with _DBConn() as conn:
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM bot_memories WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        return row["cnt"] if row else 0


# ── Long-term Memories ──

def save_memory(user_id: int, memory: str, source_message: str = None):
    """Saves a long-term memory fact about the user.
    Also indexes in ChromaDB for semantic search (if available).
    """
    new_row_id = None
    with _DBConn() as conn:
        # Avoid exact duplicates
        existing = conn.execute(
            "SELECT id FROM bot_memories WHERE user_id = ? AND memory = ?",
            (user_id, memory)
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE bot_memories SET last_used_at = datetime('now') WHERE id = ?",
                (existing["id"],)
            )
            conn.commit()
        else:
            conn.execute("""
                INSERT INTO bot_memories (user_id, memory, source_message)
                VALUES (?, ?, ?)
            """, (user_id, memory, source_message))
            conn.commit()
            new_row_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    # Index in ChromaDB outside the DB connection
    if new_row_id is not None:
        try:
            from memory_search import index_memory
            index_memory(new_row_id, memory, user_id)
        except Exception:
            pass  # ChromaDB is optional
    logger.info(f"Memory saved for user {user_id}: {memory[:80]}")


def get_memories(user_id: int, limit: int = 20) -> list[str]:
    """Gets all long-term memories for a user, most recent first."""
    with _DBConn() as conn:
        rows = conn.execute("""
            SELECT memory FROM bot_memories
            WHERE user_id = ?
            ORDER BY COALESCE(last_used_at, created_at) DESC
            LIMIT ?
        """, (user_id, limit)).fetchall()
        return [r["memory"] for r in rows]


def get_memories_formatted(user_id: int, context_query: str = None) -> str:
    """Returns memories as a formatted string for injection into the system prompt.

    If context_query is provided and ChromaDB is available, uses semantic search
    to find the most relevant memories. Falls back to recency-based retrieval.
    """
    memories = []

    # Try semantic search first (if query context available)
    if context_query:
        try:
            from memory_search import semantic_search, is_available
            if is_available():
                results = semantic_search(context_query, user_id=user_id, top_k=15)
                # Filter by minimum relevance score
                memories = [r["memory"] for r in results if r["score"] > 0.3]
        except Exception:
            pass

    # Fallback to recency-based retrieval
    if not memories:
        memories = get_memories(user_id)

    if not memories:
        return ""
    lines = ["LONG-TERM MEMORY (facts you remember about this user):"]
    for m in memories:
        lines.append(f"- {m}")
    return "\n".join(lines)


def delete_memory(user_id: int, memory_id: int):
    """Deletes a specific memory by ID. Also removes from ChromaDB index."""
    with _DBConn() as conn:
        conn.execute("DELETE FROM bot_memories WHERE id = ? AND user_id = ?", (memory_id, user_id))
        conn.commit()
    try:
        from memory_search import remove_from_index
        remove_from_index(memory_id)
    except Exception:
        pass


def list_memories_with_ids(user_id: int) -> list[dict]:
    """Lists memories with their IDs (for /memory command)."""
    with _DBConn() as conn:
        rows = conn.execute("""
            SELECT id, memory, created_at FROM bot_memories
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,)).fetchall()
        return [{"id": r["id"], "memory": r["memory"], "created_at": r["created_at"]} for r in rows]


# ── Memory Extraction Prompt ──

MEMORY_EXTRACTION_PROMPT = """Analyze the following user message and assistant response.
Extract any facts worth remembering long-term about this user.

Examples of facts to save:
- User's name, role, preferences
- "Always speak Russian", "prefers short answers"
- Important business context they shared
- Recurring topics or interests

If there is NOTHING worth remembering, respond with exactly: NONE

If there ARE facts to remember, respond with one fact per line, no bullets or numbering.
Keep each fact concise (under 20 words).

USER MESSAGE:
{user_message}

ASSISTANT RESPONSE:
{assistant_response}"""


# Initialize tables on import
try:
    init_memory_tables()
except Exception as e:
    logger.error(f"Failed to initialize memory tables: {e}")
