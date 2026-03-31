#!/usr/bin/env python3
"""
Semantic memory search using ChromaDB.

Adds vector-based similarity search on top of the existing SQLite bot_memories.
SQLite remains the source of truth; ChromaDB is a search index rebuilt on startup.

Usage:
    from memory_search import semantic_search, index_memory, remove_from_index

Flow:
    1. On bot startup: rebuild_index() syncs SQLite → ChromaDB
    2. On new memory: index_memory(id, text) adds to ChromaDB
    3. On search: semantic_search(query) returns relevant memories
    4. On delete: remove_from_index(id) removes from ChromaDB
"""

import os
import logging

logger = logging.getLogger(__name__)

# ── ChromaDB setup (in-process, no separate server) ──────────────────────

_collection = None
_available = False


def _get_collection():
    """Lazy-init ChromaDB collection. Returns None if chromadb not installed."""
    global _collection, _available
    if _collection is not None:
        return _collection

    try:
        import chromadb
        persist_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "data", "chromadb"
        )
        os.makedirs(persist_dir, exist_ok=True)
        client = chromadb.PersistentClient(path=persist_dir)
        _collection = client.get_or_create_collection(
            name="bot_memories",
            metadata={"hnsw:space": "cosine"},
        )
        _available = True
        logger.info(
            "ChromaDB initialized (persist=%s, count=%d)",
            persist_dir, _collection.count(),
        )
        return _collection
    except ImportError:
        logger.warning("chromadb not installed — semantic search disabled")
        _available = False
        return None
    except Exception as e:
        logger.error("ChromaDB init failed: %s", e)
        _available = False
        return None


def is_available() -> bool:
    """Check if semantic search is available."""
    _get_collection()
    return _available


# ── Index operations ─────────────────────────────────────────────────────

def index_memory(memory_id: int, text: str, user_id: int = None):
    """Add or update a memory in the vector index."""
    col = _get_collection()
    if col is None:
        return
    try:
        metadata = {}
        if user_id is not None:
            metadata["user_id"] = str(user_id)
        col.upsert(
            ids=[str(memory_id)],
            documents=[text],
            metadatas=[metadata] if metadata else None,
        )
    except Exception as e:
        logger.error("ChromaDB index_memory failed: %s", e)


def remove_from_index(memory_id: int):
    """Remove a memory from the vector index."""
    col = _get_collection()
    if col is None:
        return
    try:
        col.delete(ids=[str(memory_id)])
    except Exception as e:
        logger.error("ChromaDB remove_from_index failed: %s", e)


def semantic_search(query: str, user_id: int = None, top_k: int = 10) -> list[dict]:
    """Search memories by semantic similarity.

    Args:
        query: Natural language search query.
        user_id: Filter to specific user (optional).
        top_k: Max results to return.

    Returns:
        List of {id: int, memory: str, score: float} sorted by relevance.
        Score is 0..1 where 1 = perfect match.
    """
    col = _get_collection()
    if col is None:
        return []

    try:
        kwargs = {
            "query_texts": [query],
            "n_results": top_k,
        }
        if user_id is not None:
            kwargs["where"] = {"user_id": str(user_id)}

        results = col.query(**kwargs)

        memories = []
        if results and results["ids"] and results["ids"][0]:
            ids = results["ids"][0]
            docs = results["documents"][0] if results["documents"] else [""] * len(ids)
            distances = results["distances"][0] if results.get("distances") else [0] * len(ids)
            for doc_id, doc, dist in zip(ids, docs, distances):
                # ChromaDB cosine distance: 0 = identical, 2 = opposite
                # Convert to similarity score: 1 = identical, 0 = opposite
                score = max(0, 1 - dist / 2)
                memories.append({
                    "id": int(doc_id),
                    "memory": doc,
                    "score": round(score, 3),
                })
        return memories
    except Exception as e:
        logger.error("ChromaDB search failed: %s", e)
        return []


# ── Bulk rebuild from SQLite ─────────────────────────────────────────────

def rebuild_index():
    """Rebuild the entire ChromaDB index from SQLite bot_memories table.

    Call this on bot startup to ensure the index is in sync.
    Safe to call multiple times — uses upsert.
    """
    col = _get_collection()
    if col is None:
        return 0

    try:
        from bot_memory import _get_conn
        conn = _get_conn()
        rows = conn.execute(
            "SELECT id, user_id, memory FROM bot_memories ORDER BY id"
        ).fetchall()
        conn.close()

        if not rows:
            logger.info("No memories to index")
            return 0

        # Batch upsert (ChromaDB handles batches up to 41666)
        batch_size = 500
        total = 0
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            col.upsert(
                ids=[str(r["id"]) for r in batch],
                documents=[r["memory"] for r in batch],
                metadatas=[{"user_id": str(r["user_id"])} for r in batch],
            )
            total += len(batch)

        logger.info("ChromaDB index rebuilt: %d memories indexed", total)
        return total
    except Exception as e:
        logger.error("ChromaDB rebuild failed: %s", e)
        return 0
