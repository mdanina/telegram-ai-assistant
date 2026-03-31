#!/usr/bin/env python3
"""
Auto Test Runner - PostToolUse Hook
Runs tests automatically after build operations.
"""

import json
import os
import subprocess
import sys

def main():
    # Read hook input from stdin
    hook_input = json.load(sys.stdin)

    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})

    # Only trigger on Bash commands
    if tool_name != "Bash":
        print(json.dumps({"continue": True}))
        return

    command = tool_input.get("command", "")

    # Check if this was a build-related command
    build_triggers = ["npm run build", "bun build", "python -m build", "cargo build"]

    is_build = any(trigger in command for trigger in build_triggers)

    if not is_build:
        print(json.dumps({"continue": True}))
        return

    # Detect project type and run tests
    project_root = os.getcwd()

    test_command = None

    if os.path.exists("bun.lockb"):
        test_command = "bun test"
    elif os.path.exists("package.json"):
        # Check for vitest
        if os.path.exists("vitest.config.ts") or os.path.exists("vitest.config.js"):
            test_command = "npx vitest run --reporter=verbose"
        else:
            test_command = "npm test"
    elif os.path.exists("pyproject.toml"):
        test_command = "pytest tests/ -v --tb=short"
    elif os.path.exists("Cargo.toml"):
        test_command = "cargo test"
    elif os.path.exists("go.mod"):
        test_command = "go test ./..."

    if test_command:
        # Log that tests are running
        sys.stderr.write(f"[auto-test-runner] Build detected, running: {test_command}\n")

        try:
            result = subprocess.run(
                test_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode != 0:
                # Tests failed - report but don't block
                sys.stderr.write(f"[auto-test-runner] Tests failed:\n{result.stdout}\n{result.stderr}\n")
            else:
                sys.stderr.write(f"[auto-test-runner] Tests passed\n")

        except subprocess.TimeoutExpired:
            sys.stderr.write("[auto-test-runner] Test timeout (5 min)\n")
        except Exception as e:
            sys.stderr.write(f"[auto-test-runner] Error: {e}\n")

    # Always continue - this is informational, not blocking
    print(json.dumps({"continue": True}))

if __name__ == "__main__":
    main()
