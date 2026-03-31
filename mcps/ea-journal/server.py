#!/usr/bin/env python3
"""EA Journal MCP - Daily work journal for Claude Code.

A beginner-friendly journaling system for tracking work, decisions, and blockers.
Part of the Early AI Adopters Claude Code Fundamentals course.

Tools provided:
- ea_log: Log an entry (work, decision, blocker, note, win, or learning)
- ea_today: View today's journal entries
- ea_review: Review entries from a specific date or date range
- ea_summary: Generate a summary of work over time
"""

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, Literal
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, field_validator
from mcp.server.fastmcp import FastMCP

# === Server Metadata ===
SERVER_METADATA = {
    "name": "ea-journal",
    "version": "1.0.0",
    "author": "Early AI Adopters",
    "course": "Claude Code Fundamentals",
    "module": "04 - MCP Servers",
    "description": "Daily work journal for tracking progress, decisions, and blockers",
    "capabilities": ["tools"],
    "tools": [
        {"name": "ea_log", "description": "Log an entry (work, decision, blocker, note, win, learning)"},
        {"name": "ea_today", "description": "View today's journal entries"},
        {"name": "ea_review", "description": "Review entries from a specific date or range"},
        {"name": "ea_summary", "description": "Generate a summary of work over time"},
        {"name": "ea_journal_status", "description": "Get server status and metadata"},
    ],
    "entry_types": ["work", "decision", "blocker", "note", "win", "learning"],
    "storage_location": "~/.ea-journal/<date>.json",
}

# Initialize the MCP server
mcp = FastMCP(
    name="ea-journal",
    instructions="Daily work journal for tracking progress, decisions, and blockers"
)


# === Entry Types ===

class EntryType(str, Enum):
    """Valid journal entry types."""
    WORK = "work"
    DECISION = "decision"
    BLOCKER = "blocker"
    NOTE = "note"
    WIN = "win"
    LEARNING = "learning"


ENTRY_ICONS = {
    "work": "hammer",
    "decision": "signpost",
    "blocker": "stop",
    "note": "memo",
    "win": "trophy",
    "learning": "lightbulb"
}


# === Pydantic Input Models ===

class LogInput(BaseModel):
    """Input for logging a journal entry."""
    model_config = ConfigDict(str_strip_whitespace=True)

    content: str = Field(
        ...,
        description="What you want to log",
        min_length=1,
        max_length=5000
    )
    entry_type: EntryType = Field(
        default=EntryType.NOTE,
        description="Type of entry: work, decision, blocker, note, win, or learning"
    )
    project: Optional[str] = Field(
        default=None,
        description="Optional project name for context",
        max_length=100
    )


class TodayInput(BaseModel):
    """Input for viewing today's entries."""
    model_config = ConfigDict(str_strip_whitespace=True)

    entry_type: Optional[EntryType] = Field(
        default=None,
        description="Filter by type (optional)"
    )


class ReviewInput(BaseModel):
    """Input for reviewing past entries."""
    model_config = ConfigDict(str_strip_whitespace=True)

    date: Optional[str] = Field(
        default=None,
        description="Specific date in YYYY-MM-DD format (default: today)"
    )
    days: Optional[int] = Field(
        default=None,
        description="Number of days to look back (overrides date)",
        ge=1,
        le=365
    )
    entry_type: Optional[EntryType] = Field(
        default=None,
        description="Filter by type (optional)"
    )

    @field_validator('date')
    @classmethod
    def validate_date(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")


class SummaryInput(BaseModel):
    """Input for generating a summary."""
    model_config = ConfigDict(str_strip_whitespace=True)

    days: int = Field(
        default=7,
        description="Number of days to summarize (default: 7)",
        ge=1,
        le=365
    )


# === Storage ===

def get_storage_path() -> Path:
    """Get the path to the journal storage directory."""
    storage_dir = Path.home() / ".ea-journal"
    storage_dir.mkdir(exist_ok=True)
    return storage_dir


def get_journal_file(date: datetime) -> Path:
    """Get the journal file for a specific date."""
    storage_dir = get_storage_path()
    return storage_dir / f"{date.strftime('%Y-%m-%d')}.json"


def load_journal(date: datetime) -> list:
    """Load journal entries for a specific date."""
    journal_file = get_journal_file(date)
    if journal_file.exists():
        try:
            return json.loads(journal_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_journal(date: datetime, entries: list) -> None:
    """Save journal entries for a specific date."""
    journal_file = get_journal_file(date)
    journal_file.write_text(json.dumps(entries, indent=2), encoding="utf-8")


def parse_date(date_str: str) -> datetime:
    """Parse a date string in YYYY-MM-DD format."""
    return datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)


def format_entry(entry: dict, show_date: bool = False) -> str:
    """Format a single entry for display."""
    time_str = entry["timestamp"].split("T")[1][:5]
    date_prefix = f"{entry['timestamp'][:10]} " if show_date else ""
    project_str = f" [{entry['project']}]" if entry.get("project") else ""

    return f"""**[{date_prefix}{time_str}] {entry['type'].upper()}{project_str}**
{entry['content']}
"""


# === Tools ===

@mcp.tool(
    name="ea_log",
    annotations={
        "title": "Log Journal Entry",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False
    }
)
async def ea_log(params: LogInput) -> str:
    """Log a journal entry.

    Record work completed, decisions made, blockers encountered,
    wins achieved, or lessons learned. Entries are automatically
    timestamped and organized by date.

    Args:
        params: LogInput containing:
            - content (str): What you want to log
            - entry_type (EntryType): Type - work, decision, blocker, note, win, learning
            - project (Optional[str]): Project name for context

    Returns:
        str: Confirmation with timestamp and entry details

    Examples:
        - Log work: "Finished the authentication module"
        - Log decision: "Decided to use SQLite for simplicity"
        - Log blocker: "API rate limiting causing test failures"
        - Log win: "Got the demo working!"
    """
    now = datetime.now(timezone.utc)

    entry = {
        "id": f"entry_{now.strftime('%H%M%S')}_{hash(params.content) % 10000:04d}",
        "content": params.content,
        "type": params.entry_type.value,
        "project": params.project,
        "timestamp": now.isoformat()
    }

    entries = load_journal(now)
    entries.append(entry)
    save_journal(now, entries)

    project_line = f"Project: {params.project}\n" if params.project else ""
    preview = params.content[:100] + ('...' if len(params.content) > 100 else '')

    return f"""Logged {params.entry_type.value.upper()} at {now.strftime('%H:%M')}
{project_line}Entry: {preview}"""


@mcp.tool(
    name="ea_today",
    annotations={
        "title": "View Today's Journal",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def ea_today(params: TodayInput) -> str:
    """View today's journal entries.

    Shows all entries for today, optionally filtered by type.
    Entries are grouped by type for easy scanning.

    Args:
        params: TodayInput containing:
            - entry_type (Optional[EntryType]): Filter to one type only

    Returns:
        str: Today's entries formatted as markdown

    Examples:
        - "Show today's journal" -> all entries
        - "Show today's blockers" -> only blocker entries
    """
    now = datetime.now(timezone.utc)
    entries = load_journal(now)

    if not entries:
        return f"No journal entries for today ({now.strftime('%Y-%m-%d')}). Use ea_log to add your first entry!"

    # Filter by type if specified
    if params.entry_type:
        entries = [e for e in entries if e["type"] == params.entry_type.value]
        if not entries:
            return f"No {params.entry_type.value} entries for today."

    # Group by type
    by_type: dict = {}
    for entry in entries:
        t = entry["type"]
        if t not in by_type:
            by_type[t] = []
        by_type[t].append(entry)

    # Format output
    output = [f"# Journal - {now.strftime('%A, %B %d, %Y')}\n"]

    # Summary counts
    counts = ", ".join(f"{len(v)} {k}{'s' if len(v) > 1 else ''}" for k, v in sorted(by_type.items()))
    output.append(f"**Summary:** {counts}")
    output.append("\n---\n")

    # Entries by type (in a consistent order)
    for entry_t in [e.value for e in EntryType]:
        if entry_t in by_type:
            output.append(f"## {entry_t.title()}s\n")
            for entry in by_type[entry_t]:
                output.append(format_entry(entry))

    return "\n".join(output)


@mcp.tool(
    name="ea_review",
    annotations={
        "title": "Review Past Entries",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def ea_review(params: ReviewInput) -> str:
    """Review journal entries from a specific date or date range.

    Look back at past entries to review decisions, track progress,
    or find patterns in blockers.

    Args:
        params: ReviewInput containing:
            - date (Optional[str]): Specific date in YYYY-MM-DD (default: today)
            - days (Optional[int]): Number of days to look back (overrides date)
            - entry_type (Optional[EntryType]): Filter to one type only

    Returns:
        str: Past entries formatted as markdown

    Examples:
        - "Review yesterday" -> entries from yesterday
        - "Review last 7 days" -> entries from past week
        - "Review decisions from last 30 days" -> only decisions
    """
    now = datetime.now(timezone.utc)

    # Determine date range
    if params.days:
        dates = [(now - timedelta(days=i)) for i in range(params.days)]
    elif params.date:
        target = parse_date(params.date)
        dates = [target]
    else:
        dates = [now]

    # Collect entries
    all_entries = []
    for d in dates:
        entries = load_journal(d)
        for entry in entries:
            entry["_date"] = d.strftime("%Y-%m-%d")
            all_entries.append(entry)

    if not all_entries:
        if params.days:
            return f"No journal entries in the last {params.days} days."
        else:
            return f"No journal entries for {dates[0].strftime('%Y-%m-%d')}."

    # Filter by type
    if params.entry_type:
        all_entries = [e for e in all_entries if e["type"] == params.entry_type.value]
        if not all_entries:
            return f"No {params.entry_type.value} entries found."

    # Sort by timestamp (newest first)
    all_entries.sort(key=lambda e: e["timestamp"], reverse=True)

    # Format output
    if params.days:
        output = [f"# Journal - Last {params.days} Days\n"]
    else:
        output = [f"# Journal - {dates[0].strftime('%Y-%m-%d')}\n"]

    output.append(f"**Total entries:** {len(all_entries)}\n")
    output.append("---\n")

    current_date = None
    for entry in all_entries:
        entry_date = entry["_date"]
        if entry_date != current_date:
            current_date = entry_date
            output.append(f"\n## {entry_date}\n")
        output.append(format_entry(entry))

    return "\n".join(output)


@mcp.tool(
    name="ea_summary",
    annotations={
        "title": "Generate Work Summary",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def ea_summary(params: SummaryInput) -> str:
    """Generate a summary of work over time.

    Creates a high-level overview with statistics, highlights of wins,
    recurring blockers, and key learnings.

    Args:
        params: SummaryInput containing:
            - days (int): Number of days to summarize (default: 7)

    Returns:
        str: Summary report with statistics and highlights

    Examples:
        - "Summarize this week" -> 7-day summary
        - "Summarize this month" -> 30-day summary
    """
    now = datetime.now(timezone.utc)

    # Collect all entries
    all_entries = []
    dates_with_entries = 0
    for i in range(params.days):
        d = now - timedelta(days=i)
        entries = load_journal(d)
        if entries:
            dates_with_entries += 1
            all_entries.extend(entries)

    if not all_entries:
        return f"No journal entries in the last {params.days} days. Start journaling with ea_log!"

    # Calculate statistics
    by_type: dict = {}
    by_project: dict = {}
    for entry in all_entries:
        t = entry["type"]
        by_type[t] = by_type.get(t, 0) + 1

        project = entry.get("project") or "General"
        by_project[project] = by_project.get(project, 0) + 1

    # Build summary
    start_date = (now - timedelta(days=params.days - 1)).strftime('%Y-%m-%d')
    end_date = now.strftime('%Y-%m-%d')

    output = [f"# Work Summary - Last {params.days} Days\n"]
    output.append(f"**Period:** {start_date} to {end_date}")
    output.append(f"**Active days:** {dates_with_entries} of {params.days}")
    output.append(f"**Total entries:** {len(all_entries)}")
    output.append("")

    # Type breakdown
    output.append("## Entry Types\n")
    for entry_t in [e.value for e in EntryType]:
        if entry_t in by_type:
            output.append(f"- **{entry_t.title()}s:** {by_type[entry_t]}")

    # Project breakdown
    if len(by_project) > 1 or list(by_project.keys())[0] != "General":
        output.append("\n## Projects\n")
        for project, count in sorted(by_project.items(), key=lambda x: -x[1]):
            output.append(f"- **{project}:** {count} entries")

    # Highlights
    wins = [e for e in all_entries if e["type"] == "win"]
    blockers = [e for e in all_entries if e["type"] == "blocker"]
    learnings = [e for e in all_entries if e["type"] == "learning"]

    if wins:
        output.append("\n## Wins\n")
        for entry in wins[:5]:
            preview = entry['content'][:100]
            output.append(f"- {preview}")

    if blockers:
        output.append("\n## Blockers\n")
        for entry in blockers[:5]:
            preview = entry['content'][:100]
            output.append(f"- {preview}")

    if learnings:
        output.append("\n## Learnings\n")
        for entry in learnings[:5]:
            preview = entry['content'][:100]
            output.append(f"- {preview}")

    return "\n".join(output)


@mcp.tool(
    name="ea_journal_status",
    annotations={
        "title": "Server Status",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def ea_journal_status() -> str:
    """Get server status and metadata.

    Returns information about this MCP server including version,
    available tools, and current journaling statistics.

    Use this to verify the server is running and see what it can do.

    Returns:
        str: Server metadata and status formatted as markdown
    """
    now = datetime.now(timezone.utc)
    today_entries = load_journal(now)
    storage_dir = get_storage_path()

    # Count journal files (days with entries)
    journal_files = list(storage_dir.glob("*.json"))
    total_days = len(journal_files)

    # Count today's entries by type
    type_counts = {}
    for entry in today_entries:
        t = entry.get("type", "note")
        type_counts[t] = type_counts.get(t, 0) + 1

    tools_list = "\n".join(f"  - **{t['name']}**: {t['description']}" for t in SERVER_METADATA["tools"])
    entry_types = ", ".join(SERVER_METADATA["entry_types"])

    today_summary = ", ".join(f"{count} {t}" for t, count in type_counts.items()) if type_counts else "No entries yet"

    return f"""# {SERVER_METADATA['name']} v{SERVER_METADATA['version']}

**Author:** {SERVER_METADATA['author']}
**Course:** {SERVER_METADATA['course']}
**Module:** {SERVER_METADATA['module']}

## Description
{SERVER_METADATA['description']}

## Available Tools
{tools_list}

## Entry Types
{entry_types}

## Current Stats
- **Today's date:** {now.strftime('%Y-%m-%d')}
- **Today's entries:** {today_summary}
- **Days with entries:** {total_days}
- **Storage path:** {storage_dir}

## Status: CONNECTED
Server is running and ready to accept commands."""


# === Entry Point ===

if __name__ == "__main__":
    mcp.run()
