# EA Journal MCP

A daily work journal for Claude Code - track progress, decisions, and blockers.

Part of the **Early AI Adopters Claude Code Fundamentals** course.

## Why Journal?

- **Track decisions** - Remember why you made choices
- **Log blockers** - See patterns in what slows you down
- **Celebrate wins** - Keep morale high by recording achievements
- **Capture learnings** - Build a personal knowledge base
- **Review progress** - See how much you've accomplished

## Entry Types

| Type | Use For |
|------|---------|
| `work` | Tasks completed, features built |
| `decision` | Choices made and why |
| `blocker` | Issues blocking progress |
| `note` | General observations |
| `win` | Achievements and successes |
| `learning` | New things learned |

## Tools

| Tool | Description |
|------|-------------|
| `ea_log` | Log a new entry |
| `ea_today` | View today's entries |
| `ea_review` | Review past entries |
| `ea_summary` | Generate work summary |

## Installation

Add to your `.mcp.json`:

```json
{
  "mcpServers": {
    "ea-journal": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/ea-journal", "python", "server.py"]
    }
  }
}
```

## Usage

### Log Entries

```
ea_log("Finished the authentication module", entry_type="work", project="my-app")
ea_log("Decided to use SQLite instead of PostgreSQL for simplicity", entry_type="decision")
ea_log("API rate limiting causing test failures", entry_type="blocker")
ea_log("Learned about MCP prompts capability", entry_type="learning")
ea_log("Got the demo working!", entry_type="win")
```

### View Today

```
ea_today()
ea_today(entry_type="blocker")  # Filter by type
```

### Review Past Days

```
ea_review(date="2024-01-15")
ea_review(days=7)  # Last 7 days
ea_review(days=7, entry_type="decision")  # Decisions in last week
```

### Get Summary

```
ea_summary()  # Last 7 days
ea_summary(days=30)  # Last month
```

## Storage

Entries are stored by date in `~/.ea-journal/`:
- `2024-01-15.json`
- `2024-01-16.json`
- etc.

## Tips

- Log throughout the day, not just at the end
- Be specific about blockers - it helps find patterns
- Review your learnings weekly
- Use project names consistently for better summaries
- Start each session with `ea_today()` to see where you left off

---

*Built for the Early AI Adopters community*
