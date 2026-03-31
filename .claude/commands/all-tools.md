---
description: List all available Claude Code tools
model: sonnet
---

# List All Tools

## Purpose

Display all tools available in your current Claude Code session. Useful for understanding what capabilities are available and how to use them.

## Workflow

1. List all available tools from the system prompt
2. Display each tool in TypeScript function signature format
3. Include a brief description of what each tool does
4. Use double line breaks between tools for readability

## Report

Output each tool as:

```
toolName(param1: type, param2: type): returnType
  - Brief description of what this tool does

nextTool(param: type): returnType
  - Brief description
```

Group related tools together if applicable (e.g., file operations, search tools, etc.).
