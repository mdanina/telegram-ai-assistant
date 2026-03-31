#!/usr/bin/env python3
"""EA Memory MCP - Simple memory management for Claude Code.

A beginner-friendly memory system with tagging support.
Part of the Early AI Adopters Claude Code Fundamentals course.

Tools provided:
- ea_remember: Store a memory with optional tags
- ea_recall: Search memories by keyword
- ea_list: List all memories (with optional tag filter)
- ea_forget: Delete a memory by ID
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from mcp.server.fastmcp import FastMCP

# === Server Metadata ===
SERVER_METADATA = {
    "name": "ea-memory",
    "version": "1.0.0",
    "author": "Early AI Adopters",
    "course": "Claude Code Fundamentals",
    "module": "04 - MCP Servers",
    "description": "Simple memory system with tagging for Claude Code",
    "capabilities": ["tools"],
    "tools": [
        {"name": "ea_remember", "description": "Store a memory with optional tags"},
        {"name": "ea_recall", "description": "Search memories by keyword"},
        {"name": "ea_list", "description": "List all memories with optional filtering"},
        {"name": "ea_forget", "description": "Delete a memory by ID"},
        {"name": "ea_memory_status", "description": "Get server status and metadata"},
    ],
    "storage_location": "~/.ea-memory/memories.json",
}

# Initialize the MCP server
mcp = FastMCP(
    name="ea-memory",
    instructions="Simple memory system with tagging for Claude Code"
)


# === Pydantic Input Models ===

class RememberInput(BaseModel):
    """Input for storing a memory."""
    model_config = ConfigDict(str_strip_whitespace=True)

    content: str = Field(
        ...,
        description="The information to remember",
        min_length=1,
        max_length=10000
    )
    tags: Optional[str] = Field(
        default=None,
        description="Comma-separated tags (e.g., 'python,bugfix,api')"
    )
    importance: Optional[int] = Field(
        default=50,
        description="Priority 1-100 (default: 50)",
        ge=1,
        le=100
    )


class RecallInput(BaseModel):
    """Input for searching memories."""
    model_config = ConfigDict(str_strip_whitespace=True)

    query: str = Field(
        ...,
        description="Search term to find in memory content",
        min_length=1
    )
    tags: Optional[str] = Field(
        default=None,
        description="Filter by comma-separated tags (optional)"
    )
    limit: Optional[int] = Field(
        default=10,
        description="Maximum results (default: 10)",
        ge=1,
        le=50
    )


class ListInput(BaseModel):
    """Input for listing memories."""
    model_config = ConfigDict(str_strip_whitespace=True)

    tags: Optional[str] = Field(
        default=None,
        description="Filter by comma-separated tags (optional)"
    )
    limit: Optional[int] = Field(
        default=20,
        description="Maximum results (default: 20)",
        ge=1,
        le=100
    )
    offset: Optional[int] = Field(
        default=0,
        description="Skip this many results for pagination",
        ge=0
    )


class ForgetInput(BaseModel):
    """Input for deleting a memory."""
    model_config = ConfigDict(str_strip_whitespace=True)

    memory_id: str = Field(
        ...,
        description="The memory ID to delete (e.g., 'mem_0001')"
    )
    confirm: bool = Field(
        default=False,
        description="Must be True to confirm deletion"
    )


# === Storage ===

def get_storage_path() -> Path:
    """Get the path to the memory storage file."""
    storage_dir = Path.home() / ".ea-memory"
    storage_dir.mkdir(exist_ok=True)
    return storage_dir / "memories.json"


def load_memories() -> dict:
    """Load memories from storage."""
    storage_path = get_storage_path()
    if storage_path.exists():
        try:
            return json.loads(storage_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError):
            return {"memories": [], "next_id": 1}
    return {"memories": [], "next_id": 1}


def save_memories(data: dict) -> None:
    """Save memories to storage."""
    storage_path = get_storage_path()
    storage_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def generate_id(data: dict) -> str:
    """Generate a simple sequential ID."""
    mem_id = f"mem_{data['next_id']:04d}"
    data["next_id"] += 1
    return mem_id


def parse_tags(tags_str: Optional[str]) -> List[str]:
    """Parse comma-separated tags into a list."""
    if not tags_str:
        return []
    return [t.strip().lower() for t in tags_str.split(",") if t.strip()]


# === Tools ===

@mcp.tool(
    name="ea_remember",
    annotations={
        "title": "Remember Information",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False
    }
)
async def ea_remember(params: RememberInput) -> str:
    """Store a memory with optional tags and importance.

    Use this tool to save information you want to recall later.
    Memories persist between sessions and can be searched by content or tags.

    Args:
        params: RememberInput containing:
            - content (str): The information to remember
            - tags (Optional[str]): Comma-separated tags for organization
            - importance (Optional[int]): Priority 1-100, higher = more important

    Returns:
        str: Confirmation with memory ID, tags, and importance

    Examples:
        - "Remember the API endpoint is /api/v1/users" -> stores with default importance
        - "Remember this bugfix with tags 'python,bugfix'" -> stores with tags
    """
    data = load_memories()

    tag_list = parse_tags(params.tags)
    importance = params.importance or 50

    memory = {
        "id": generate_id(data),
        "content": params.content,
        "tags": tag_list,
        "importance": importance,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    data["memories"].append(memory)
    save_memories(data)

    tag_display = ", ".join(tag_list) if tag_list else "none"
    return f"""Remembered: {memory['id']}
Tags: {tag_display}
Importance: {importance}/100
Created: {memory['created_at'][:10]}"""


@mcp.tool(
    name="ea_recall",
    annotations={
        "title": "Search Memories",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def ea_recall(params: RecallInput) -> str:
    """Search memories by keyword or phrase.

    Searches through all stored memories for content matching the query.
    Results are sorted by importance (highest first), then by date.

    Args:
        params: RecallInput containing:
            - query (str): Search term to find in memory content
            - tags (Optional[str]): Filter results to only these tags
            - limit (Optional[int]): Maximum results to return (default: 10)

    Returns:
        str: Matching memories formatted as markdown, or "No memories found"

    Examples:
        - "Recall API" -> finds memories containing "API"
        - "Recall database with tags 'config'" -> finds database memories tagged 'config'
    """
    data = load_memories()
    memories = data["memories"]

    if not memories:
        return "No memories stored yet. Use ea_remember to store your first memory."

    filter_tags = parse_tags(params.tags)
    query_lower = params.query.lower()
    results = []

    for mem in memories:
        if query_lower not in mem["content"].lower():
            continue
        if filter_tags:
            mem_tags = set(mem.get("tags", []))
            if not any(t in mem_tags for t in filter_tags):
                continue
        results.append(mem)

    # Sort by importance (desc), then date (desc)
    results.sort(key=lambda m: (-m["importance"], m["created_at"]), reverse=False)

    total_matches = len(results)
    results = results[:params.limit]

    if not results:
        return f"No memories found matching: {params.query}"

    # Format output with pagination info
    output = [f"# Found {total_matches} memories (showing {len(results)})\n"]

    for mem in results:
        tags_str = ", ".join(mem.get("tags", [])) or "none"
        output.append(f"""## [{mem['id']}] Importance: {mem['importance']}/100
**Tags:** {tags_str}
**Created:** {mem['created_at'][:10]}

{mem['content']}

---""")

    if total_matches > len(results):
        output.append(f"\n*{total_matches - len(results)} more results available. Increase limit to see more.*")

    return "\n".join(output)


@mcp.tool(
    name="ea_list",
    annotations={
        "title": "List Memories",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def ea_list(params: ListInput) -> str:
    """List all stored memories with optional filtering.

    Returns a summary table of all memories. Use offset for pagination
    through large memory collections.

    Args:
        params: ListInput containing:
            - tags (Optional[str]): Filter to only memories with these tags
            - limit (Optional[int]): Maximum results to return (default: 20)
            - offset (Optional[int]): Skip this many results for pagination

    Returns:
        str: Summary table of memories with pagination info

    Examples:
        - "List all memories" -> shows all memories
        - "List memories with tags 'api'" -> shows only API-tagged memories
        - "List memories with offset 20" -> shows memories 21-40
    """
    data = load_memories()
    memories = data["memories"]

    if not memories:
        return "No memories stored yet. Use ea_remember to store your first memory."

    filter_tags = parse_tags(params.tags)

    # Filter by tags
    results = []
    for mem in memories:
        if filter_tags:
            mem_tags = set(mem.get("tags", []))
            if not any(t in mem_tags for t in filter_tags):
                continue
        results.append(mem)

    # Sort by date (newest first)
    results.sort(key=lambda m: m["created_at"], reverse=True)

    total_matches = len(results)

    # Apply pagination
    paginated = results[params.offset:params.offset + params.limit]

    if not paginated:
        if params.offset > 0:
            return f"No more memories. Total: {total_matches}"
        return f"No memories found with tags: {params.tags}"

    # Format as table with pagination info
    has_more = (params.offset + len(paginated)) < total_matches
    next_offset = params.offset + len(paginated) if has_more else None

    output = [f"# Memories ({len(paginated)} of {total_matches})\n"]
    output.append("| ID | Preview | Tags | Importance | Created |")
    output.append("|-----|---------|------|------------|---------|")

    for mem in paginated:
        preview = mem["content"][:50].replace("\n", " ").replace("|", "/")
        if len(mem["content"]) > 50:
            preview += "..."
        tags_str = ", ".join(mem.get("tags", [])[:3]) or "-"
        output.append(
            f"| {mem['id']} | {preview} | {tags_str} | "
            f"{mem['importance']} | {mem['created_at'][:10]} |"
        )

    # Pagination footer
    output.append("")
    if has_more:
        output.append(f"*More results available. Use offset={next_offset} to see next page.*")
    output.append(f"**Total:** {total_matches} | **Showing:** {params.offset + 1}-{params.offset + len(paginated)}")

    return "\n".join(output)


@mcp.tool(
    name="ea_forget",
    annotations={
        "title": "Delete Memory",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def ea_forget(params: ForgetInput) -> str:
    """Delete a memory by ID.

    Permanently removes a memory from storage. Requires confirmation
    to prevent accidental deletion.

    Args:
        params: ForgetInput containing:
            - memory_id (str): The memory ID to delete (e.g., "mem_0001")
            - confirm (bool): Must be True to confirm deletion

    Returns:
        str: Confirmation of deletion or error message

    Examples:
        - "Forget mem_0001" -> asks for confirmation
        - "Forget mem_0001 with confirm=True" -> deletes the memory
    """
    if not params.confirm:
        return "Set confirm=True to delete. This action cannot be undone."

    data = load_memories()

    for i, mem in enumerate(data["memories"]):
        if mem["id"] == params.memory_id:
            removed = data["memories"].pop(i)
            save_memories(data)
            preview = removed['content'][:100]
            if len(removed['content']) > 100:
                preview += "..."
            return f"Deleted: {params.memory_id}\nContent was: {preview}"

    return f"Memory not found: {params.memory_id}. Use ea_list to see available memory IDs."


@mcp.tool(
    name="ea_memory_status",
    annotations={
        "title": "Server Status",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def ea_memory_status() -> str:
    """Get server status and metadata.

    Returns information about this MCP server including version,
    available tools, and current storage statistics.

    Use this to verify the server is running and see what it can do.

    Returns:
        str: Server metadata and status formatted as markdown
    """
    # Get storage stats
    data = load_memories()
    memory_count = len(data.get("memories", []))
    storage_path = get_storage_path()

    # Get unique tags
    all_tags = set()
    for mem in data.get("memories", []):
        all_tags.update(mem.get("tags", []))

    tools_list = "\n".join(f"  - **{t['name']}**: {t['description']}" for t in SERVER_METADATA["tools"])

    return f"""# {SERVER_METADATA['name']} v{SERVER_METADATA['version']}

**Author:** {SERVER_METADATA['author']}
**Course:** {SERVER_METADATA['course']}
**Module:** {SERVER_METADATA['module']}

## Description
{SERVER_METADATA['description']}

## Available Tools
{tools_list}

## Current Stats
- **Memories stored:** {memory_count}
- **Unique tags:** {len(all_tags)}
- **Storage path:** {storage_path}

## Status: CONNECTED
Server is running and ready to accept commands."""


# === Entry Point ===

if __name__ == "__main__":
    mcp.run()
