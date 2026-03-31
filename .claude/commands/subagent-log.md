---
description: View, search, or clear the subagent activity log
allowed-tools: Read, Write, Bash
argument-hint: [view|clear|last N|search TERM]
---

# Subagent Activity Log

## Purpose
View what subagents have been doing.

## Arguments
- `view` (default): Show all entries
- `clear`: Clear the log
- `last N`: Show last N entries
- `search TERM`: Find entries containing TERM

## Workflow

### Parse Arguments
INPUT: $ARGUMENTS (default: view)

### Execute

**view/empty**: Read `logs/subagent-activity.json`, format as table, newest first

**clear**: Write `[]` to log file, confirm cleared

**last N**: Read log, take last N, display

**search TERM**: Filter entries where task contains TERM

### Output Format

```
## Subagent Activity Log

| Time | Task | Status | Duration |
|------|------|--------|----------|
| [time] | [task] | [status] | [Xs] |

Total: [count] entries
```

If empty:
```
No subagent activity logged yet.
Try spawning an agent with the Task tool.
```
