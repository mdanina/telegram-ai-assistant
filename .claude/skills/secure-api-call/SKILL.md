---
description: Makes API calls with response validation for leaked credentials
hooks:
  post_tool_use:
    - matcher: WebFetch
      command: uv run ${CLAUDE_PROJECT_DIR}/.claude/hooks/damage-control/bash-output-validator.py
---

# Secure API Call Skill

A skill for making API calls that validates responses don't contain leaked credentials.

## Purpose

When fetching from APIs, some responses might accidentally include:
- Debug information with API keys
- Error messages with connection strings
- Leaked credentials in response bodies

This skill catches those issues.

## Trigger Keywords

- "secure api call"
- "safe fetch"
- "validated request"

## Usage

```
Make a secure API call to https://api.example.com/users
```

## How It Works

1. Skill makes the API request via WebFetch
2. post_tool_use hook scans the response
3. If credentials detected, warning is displayed
4. User is alerted to potential exposure

## What It Detects

- API keys in response bodies
- Connection strings with passwords
- Bearer tokens in error messages
- Debug output containing secrets

## Note

This is a defensive measure. Well-designed APIs shouldn't leak credentials, but this catches edge cases and misconfigured endpoints.
