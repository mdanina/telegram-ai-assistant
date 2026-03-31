---
name: secure-file-reader
description: Reads files and warns if secrets are detected in the content
model: sonnet
allowed-tools: Read, Glob, Grep
hooks:
  PostToolUse:
    - matcher: "Read"
      hooks:
        - type: command
          command: uv run .claude/hooks/damage-control/bash-output-validator.py
---

# Secure File Reader Agent

An agent that reads files with automatic secret detection.

## Purpose

When reading files, automatically scan the content for accidentally stored secrets like:
- API keys
- Passwords
- Private keys
- Access tokens

## Usage

This agent is spawned by other commands when secure file reading is needed.

## How It Works

1. Agent receives a Read request
2. Reads the file content
3. post_tool_use hook scans for secrets
4. If secrets found, warning appears in stderr
5. Agent can alert the user or take action

## Why Use This

Files sometimes contain secrets that shouldn't be there:
- A config file with a hardcoded API key
- A log file that captured credentials
- A backup that includes .env contents

This agent helps identify these issues before they spread.

## Hook Details

The hook reuses `bash-output-validator.py` which detects:
- Anthropic API keys (sk-ant-...)
- OpenAI API keys (sk-...)
- GitHub tokens (ghp_...)
- AWS credentials (AKIA...)
- Private keys (-----BEGIN PRIVATE KEY-----)
- Bearer tokens
