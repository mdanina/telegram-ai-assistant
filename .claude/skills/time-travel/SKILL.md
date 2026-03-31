---
name: time-travel
description: |
  Git checkpoint and recovery system for ADW workflows. Creates save points, enables rollback,
  and forces alternative approaches when stuck in failure loops.
  Use when: (1) ADW phase fails repeatedly and needs to try a different approach, (2) User wants
  to undo recent code changes, (3) Need to revert to a previous known-good state, (4) Agent is
  stuck in a retry loop, (5) User says "undo", "rollback", "revert", "time travel", "go back",
  or "try something else"
aliases:
  - undo
  - rollback
tools:
  - Bash
  - Read
  - Write
  - Glob
  - mcp__omni-cortex__cortex_recall
  - mcp__omni-cortex__cortex_remember
---

# Time Travel - Git Checkpoint & Recovery

Intelligent rollback and recovery system that creates git checkpoints, reverts to clean states, and forces alternative approaches when automated workflows encounter persistent failures.

## Core Concept

Instead of looping endlessly on a failing approach or stopping with "needs-human":
1. **Checkpoint** before risky operations
2. **Revert** to clean state when stuck
3. **Pivot** to a fundamentally different approach with fresh context

## Pre-Travel Context

Before any time travel operation:
- Recall failed approaches: `cortex_recall: "time-travel failed-approach {project}"`
- Check for known issues: `cortex_recall: "unresolved {phase}"`
- Use recalled context to avoid repeating failed strategies

---

## User Commands

### Interactive Mode
```
/timetravel
```
Shows checkpoints, allows selection, provides revert/pivot options.

### List Checkpoints
```
/timetravel list
```
Shows all checkpoints for current project/ADW session.

### Create Manual Checkpoint
```
/timetravel create "before refactoring auth"
```
Creates a named checkpoint at current state.

### Revert to Checkpoint
```
/timetravel revert <checkpoint-name>
```
Reverts to specified checkpoint, preserving current changes in stash.

### Quick Undo (Alias)
```
/undo
```
Reverts to most recent checkpoint.

---

## Checkpoint Operations

### Creating Checkpoints

Checkpoints are named: `tt_{context}_{timestamp}`

**Automatic checkpoint triggers** (in ADW workflows):
- Before BUILD phase starts
- Before VALIDATE phase starts
- Before SECURITY_FIX phase starts
- Before each retry attempt

**Manual checkpoint creation:**

**Windows (PowerShell):**
```powershell
# Run checkpoint script
& "$env:USERPROFILE\.claude\skills\time-travel\scripts\checkpoint.ps1" `
    -CheckpointName "tt_prebuild_20260117_143000" `
    -Description "Before build phase" `
    -Method "branch"
```

**Unix (Bash):**
```bash
~/.claude/skills/time-travel/scripts/checkpoint.sh \
    --name "tt_prebuild_20260117_143000" \
    --description "Before build phase" \
    --method "branch"
```

### Checkpoint Methods

| Method | Git Command | Best For |
|--------|-------------|----------|
| `branch` | `git branch {name}` | Clean working directory, preserves history |
| `stash` | `git stash push -m "{name}"` | Uncommitted changes need saving |

### Checkpoint Storage

Checkpoints are tracked in `agents/{adw_id}/checkpoints.json`:
```json
{
  "checkpoints": [
    {
      "name": "tt_build_20260117_143000",
      "phase": "build",
      "method": "branch",
      "commit": "abc123...",
      "timestamp": "2026-01-17T14:30:00Z",
      "description": "Before build phase attempt 1"
    }
  ]
}
```

---

## Revert Operations

### Revert Strategies

| Strategy | Git Command | When Used | Destructive |
|----------|-------------|-----------|-------------|
| **Checkout** (default) | `git checkout {branch}` | Working dir is clean | No |
| **Stash Apply** | `git stash apply` | Checkpoint was a stash | No |
| **Hard Reset** | `git reset --hard` | Checkout fails, user explicitly requests | Yes |

### Revert with Preservation (Default)

```powershell
# Windows - preserves current changes before revert
& "$env:USERPROFILE\.claude\skills\time-travel\scripts\revert.ps1" `
    -CheckpointName "tt_build_20260117_143000" `
    -PreserveChanges
```

```bash
# Unix
~/.claude/skills/time-travel/scripts/revert.sh \
    --name "tt_build_20260117_143000" \
    --preserve-changes
```

### Hard Reset (Explicit Only)

```powershell
# Windows - discards all changes, full restore
& "$env:USERPROFILE\.claude\skills\time-travel\scripts\revert.ps1" `
    -CheckpointName "tt_build_20260117_143000" `
    -HardReset
```

---

## Pivot Mechanism

When Time Travel is invoked after MAX_RETRIES exhausted, generate fresh context that **blocks previous failed approaches**.

### Pivot Context Template

```markdown
## TIME TRAVEL RECOVERY MODE

Previous {N} attempts at {PHASE} phase FAILED.
You have been reverted to a clean state.

### CRITICAL: DO NOT REPEAT THESE APPROACHES

{LIST_OF_BLOCKED_APPROACHES}

### Error That Triggered Time Travel

{FINAL_ERROR_MESSAGE}

### REQUIRED ACTIONS

1. Acknowledge this time travel event
2. Analyze WHY previous approaches failed
3. Choose a FUNDAMENTALLY DIFFERENT strategy
4. Explain your new approach before implementing

### PIVOT STRATEGIES

See: references/pivot-strategies.md

You MUST try something DIFFERENT.
```

### Approach Tracking

Store failed approaches in Cortex for future reference:

```
cortex_remember:
  content: |
    Failed approaches for {phase} in {project}:
    - Approach 1: {description} → {error}
    - Approach 2: {description} → {error}
    - Approach 3: {description} → {error}
    Time Travel invoked to reset and pivot.
  tags: ["time-travel", "failed-approach", "{phase}", "{project}"]
  importance: 85
```

---

## ADW Integration

### Integration Points

Time Travel integrates with ADW at these points:

1. **Before phases** - Create checkpoints automatically
2. **On track_error()** - When `is_unresolved_final=True`, invoke Time Travel instead of stopping
3. **Pivot retry** - Inject blocking context, retry with fresh approach

### Integration Flow

```
[Checkpoint created]
Attempt 1 → Fail → track_error(attempt=1) → Retry
Attempt 2 → Fail → track_error(attempt=2) → Retry
Attempt 3 → Fail → TIME TRAVEL:
                    ├── Store failed approaches in Cortex
                    ├── Revert to pre-attempt-1 checkpoint
                    ├── Generate pivot context
                    └── Retry with blocked approaches

Pivot Attempt 1 → (new approach forced) → Success or continue cycle
```

### ADW Module Usage

```python
from adw_modules.time_travel import TimeTravel

# Create checkpoint before risky operation
tt = TimeTravel(state)
checkpoint = tt.create_checkpoint(
    phase="build",
    description="Before build phase"
)

# On failure, invoke time travel
if is_unresolved_final:
    success, pivot_context = tt.invoke(
        phase=phase,
        error_msg=error,
        failed_approaches=approaches
    )
    if success:
        # Retry with pivot context injected
        prompt = f"{pivot_context}\n\n{original_prompt}"
```

---

## Quick Reference

### Common Scenarios

| Scenario | Command |
|----------|---------|
| Undo last change | `/undo` |
| See all checkpoints | `/timetravel list` |
| Revert to specific point | `/timetravel revert tt_build_...` |
| Save current state | `/timetravel create "before refactor"` |
| Interactive mode | `/timetravel` |

### Script Locations

| Platform | Checkpoint Script | Revert Script |
|----------|-------------------|---------------|
| Windows | `~/.claude/skills/time-travel/scripts/checkpoint.ps1` | `~/.claude/skills/time-travel/scripts/revert.ps1` |
| Unix | `~/.claude/skills/time-travel/scripts/checkpoint.sh` | `~/.claude/skills/time-travel/scripts/revert.sh` |

---

## Post-Travel Memory

After any time travel operation, store the event:

```
cortex_remember:
  content: |
    Time Travel Event in {project}:
    - Phase: {phase}
    - Reverted from: {from_checkpoint}
    - Reverted to: {to_checkpoint}
    - Reason: {error_summary}
    - Blocked approaches: {list}
  tags: ["time-travel", "revert", "{project}", "{phase}"]
  importance: 80
```

---

## Troubleshooting

### "Checkout failed - uncommitted changes"
Use stash method or run with `-PreserveChanges` flag.

### "Checkpoint not found"
Run `/timetravel list` to see available checkpoints. Checkpoint may have been pruned.

### "Hard reset blocked"
Hard reset requires explicit `-HardReset` flag. Use checkout or stash methods by default.

### Git hooks blocking operations
Time Travel uses checkout/reset/stash operations which bypass commit hooks. If post-checkout hooks cause issues, check hook configuration.
