#!/usr/bin/env python3
"""
SubagentStop Hook - Logs subagent activity to JSON file.
Triggered when any subagent completes.
Logs to: logs/subagent-activity.json
"""

import sys
import json
from pathlib import Path
from datetime import datetime

LOG_FILE = Path("logs/subagent-activity.json")


def ensure_log_file():
    """Create log file and directory if needed."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not LOG_FILE.exists():
        LOG_FILE.write_text("[]")


def append_log_entry(entry: dict):
    """Append entry to log, keeping last 100."""
    ensure_log_file()
    try:
        logs = json.loads(LOG_FILE.read_text())
    except (json.JSONDecodeError, FileNotFoundError):
        logs = []
    logs.append(entry)
    if len(logs) > 100:
        logs = logs[-100:]
    LOG_FILE.write_text(json.dumps(logs, indent=2))


def main():
    try:
        hook_input = json.loads(sys.stdin.read())
        session_id = hook_input.get("session_id", "unknown")
        task = hook_input.get("task_description", hook_input.get("description", "Subagent task"))
        result = hook_input.get("result", "")
        if isinstance(result, dict):
            result = result.get("summary", str(result)[:200])
        elif isinstance(result, str) and len(result) > 200:
            result = result[:200] + "..."
        duration_ms = hook_input.get("duration_ms")
        duration_sec = round(duration_ms / 1000, 1) if duration_ms else None
        error = hook_input.get("error")
        status = "error" if error else "completed"

        entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "task": task[:100] if task else "Unknown",
            "status": status,
            "duration_seconds": duration_sec,
            "result_preview": result[:150] if result else None
        }
        if error:
            entry["error"] = str(error)[:200]

        append_log_entry(entry)
    except Exception as e:
        print(f"Subagent logger warning: {e}", file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
