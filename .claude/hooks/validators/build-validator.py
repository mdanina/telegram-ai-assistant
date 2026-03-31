#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Build Validator - Stop Hook (Blocking)
Validates that a build operation completed successfully.

This is a BLOCKING validator - if it fails, the agent receives
feedback and can retry. This is the IDD "self-validating agent" pattern.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Log file in same directory as script
LOG_FILE = Path(__file__).parent / "build-validator.log"


def log(message: str):
    """Append timestamped message to log file."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


def main():
    log("=" * 50)
    log("BUILD VALIDATOR STOP HOOK TRIGGERED")

    # Read hook input from stdin
    try:
        stdin_data = sys.stdin.read()
        hook_input = json.loads(stdin_data) if stdin_data.strip() else {}
        log(f"hook_input keys: {list(hook_input.keys())}")
    except json.JSONDecodeError:
        hook_input = {}
        log("No JSON input received")

    errors = []
    project_root = Path.cwd()
    log(f"Project root: {project_root}")

    # Check for common build artifacts that indicate success
    build_indicators = {
        # JavaScript/TypeScript
        "dist/": "JavaScript/TypeScript build output",
        "build/": "Build output directory",
        ".next/": "Next.js build output",
        "out/": "Static export output",
        # Python
        "dist/*.whl": "Python wheel package",
        "dist/*.tar.gz": "Python source distribution",
        # Rust
        "target/release/": "Rust release build",
        "target/debug/": "Rust debug build",
        # Go
        "bin/": "Go binary output",
    }

    found_artifacts = []
    for pattern, description in build_indicators.items():
        if "*" in pattern:
            # Glob pattern
            matches = list(project_root.glob(pattern))
            if matches:
                found_artifacts.append(f"{pattern} ({description})")
                log(f"  ✓ Found: {pattern}")
        else:
            # Directory check
            if (project_root / pattern).exists():
                found_artifacts.append(f"{pattern} ({description})")
                log(f"  ✓ Found: {pattern}")

    # Check for package.json build script (common case)
    package_json = project_root / "package.json"
    if package_json.exists():
        try:
            import json as json_lib
            with open(package_json, encoding="utf-8") as f:
                pkg = json_lib.load(f)
            scripts = pkg.get("scripts", {})
            if "build" in scripts:
                log(f"  ✓ package.json has build script: {scripts['build']}")
        except Exception as e:
            log(f"  Warning: Could not parse package.json: {e}")

    # Validation logic
    if not found_artifacts:
        # No build artifacts found - this might be okay for some projects
        # Only block if we expected a build
        log("No build artifacts found")

        # Check if there's evidence a build was attempted
        if package_json.exists():
            errors.append(
                "No build output found. Expected dist/, build/, or .next/ directory. "
                "Run 'npm run build' or equivalent and try again."
            )
    else:
        log(f"Found {len(found_artifacts)} build artifacts")

    # Output JSON decision
    if errors:
        log(f"RESULT: BLOCK ({len(errors)} errors)")
        for err in errors:
            log(f"  ✗ {err}")

        # Output blocking decision
        print(json.dumps({
            "decision": "block",
            "reason": "Build validation failed:\n" + "\n".join(errors)
        }))
    else:
        log("RESULT: PASS")
        # Empty object = allow/continue
        print(json.dumps({}))


if __name__ == "__main__":
    main()
