#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Test Validator - PostToolUse Hook (Blocking)
Validates test output after test commands run.

This validator runs AFTER Bash commands and checks if tests passed.
If tests failed, it BLOCKS and returns feedback to the agent.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Log file in same directory as script
LOG_FILE = Path(__file__).parent / "test-validator.log"


def log(message: str):
    """Append timestamped message to log file."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


def main():
    log("=" * 50)
    log("TEST VALIDATOR POSTTOOLUSE HOOK TRIGGERED")

    # Read hook input from stdin
    try:
        stdin_data = sys.stdin.read()
        hook_input = json.loads(stdin_data) if stdin_data.strip() else {}
        log(f"hook_input keys: {list(hook_input.keys())}")
    except json.JSONDecodeError:
        hook_input = {}
        log("No JSON input received")

    # Get tool information
    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})
    tool_output = hook_input.get("tool_output", {})

    log(f"Tool: {tool_name}")

    # Only process Bash commands
    if tool_name != "Bash":
        log("Not a Bash command, passing through")
        print(json.dumps({}))
        return

    command = tool_input.get("command", "")
    log(f"Command: {command[:100]}...")

    # Check if this was a test command
    test_triggers = [
        "npm test",
        "npm run test",
        "bun test",
        "pytest",
        "vitest",
        "jest",
        "cargo test",
        "go test",
        "python -m pytest",
        "npx vitest",
        "npx jest",
    ]

    is_test = any(trigger in command for trigger in test_triggers)

    if not is_test:
        log("Not a test command, passing through")
        print(json.dumps({}))
        return

    log("Test command detected, checking output...")

    # Get the output from the tool result
    stdout = tool_output.get("stdout", "")
    stderr = tool_output.get("stderr", "")
    exit_code = tool_output.get("exit_code", 0)

    log(f"Exit code: {exit_code}")

    errors = []

    # Check exit code
    if exit_code != 0:
        # Extract failure summary from output
        output_combined = stdout + stderr

        # Look for common failure patterns
        failure_lines = []
        for line in output_combined.split("\n"):
            line_lower = line.lower()
            if any(word in line_lower for word in ["fail", "error", "assert"]):
                failure_lines.append(line.strip())

        # Limit to first 5 failures
        failure_summary = failure_lines[:5]
        if len(failure_lines) > 5:
            failure_summary.append(f"... and {len(failure_lines) - 5} more issues")

        errors.append(
            f"Tests failed (exit code {exit_code}).\n"
            f"Issues found:\n" + "\n".join(f"  - {line}" for line in failure_summary)
        )
        log(f"Test failures detected: {len(failure_lines)} issues")
    else:
        log("Tests passed (exit code 0)")

    # Output JSON decision
    if errors:
        log(f"RESULT: BLOCK ({len(errors)} errors)")

        print(json.dumps({
            "decision": "block",
            "reason": "Test validation failed:\n" + "\n".join(errors)
        }))
    else:
        log("RESULT: PASS")
        print(json.dumps({}))


if __name__ == "__main__":
    main()
