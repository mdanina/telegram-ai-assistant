# EA Memory MCP

A simple, beginner-friendly memory system for Claude Code.

Part of the **Early AI Adopters Claude Code Fundamentals** course.

## Features

- **Remember** - Store memories with optional tags and importance
- **Recall** - Search memories by keyword
- **List** - View all memories with filtering
- **Forget** - Delete memories you no longer need

## Installation

### Option 1: Add to .mcp.json (Project-level)

```json
{
  "mcpServers": {
    "ea-memory": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/ea-memory", "python", "server.py"]
    }
  }
}
```

### Option 2: Add to settings.json (Global)

Add to `~/.claude/settings.json` (Mac/Linux) or `%USERPROFILE%\.claude\settings.json` (Windows):

```json
{
  "mcpServers": {
    "ea-memory": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/ea-memory", "python", "server.py"]
    }
  }
}
```

## Usage

### Store a Memory

```
ea_remember("The API endpoint for users is /api/v1/users", tags="api,endpoint", importance=80)
```

### Search Memories

```
ea_recall("API endpoint")
ea_recall("database", tags="config")
```

### List All Memories

```
ea_list()
ea_list(tags="api,config", limit=10)
```

### Delete a Memory

```
ea_forget("mem_0001", confirm=True)
```

## Storage

Memories are stored in `~/.ea-memory/memories.json`.

## Tips

- Use consistent tags for better organization (e.g., "api", "config", "decision", "solution")
- Higher importance (1-100) means the memory appears first in search results
- Use `/recall` to find past solutions before asking Claude to solve the same problem again

---

*Built for the Early AI Adopters community*
