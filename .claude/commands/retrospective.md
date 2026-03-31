---
description: Analyze session for errors, snags, and lessons learned - creates improvement documentation
allowed-tools: Read, Write, Glob, Grep
argument-hint: [session-name]
model: opus
---

# EA-Retrospective Command

End-of-session analysis that extracts lessons learned, errors encountered, and improvement recommendations. Creates a file-based retrospective document.

## Arguments

- `[session-name]` - Optional name for the session (used in filename)
  - Default: "session" if not provided
  - Format: kebab-case (e.g., "validation-module", "api-refactor")

## Output Location

`docs/retrospectives/retrospective-YYYY-MM-DD-NNN-session-name.md`

## File Naming

Sequential numbering per day:
```
retrospective-2026-01-25-001-validation-module.md
retrospective-2026-01-25-002-bug-fixes.md
retrospective-2026-01-25-003-session.md
```

## Workflow

### Step 1: Ensure Directory Exists

```bash
mkdir -p docs/retrospectives
```

### Step 2: Determine File Number

Find existing retrospectives for today:
```
Glob: docs/retrospectives/retrospective-YYYY-MM-DD-*.md
```

Extract numbers and calculate next:
- If no files exist: next = 001
- If files exist: next = max(existing NNN) + 1

### Step 3: Analyze Conversation

Review the current conversation session for:

**Errors Encountered:**
- Build failures
- Type errors
- Test failures
- Runtime exceptions
- Configuration issues

**Snags and Blockers:**
- Unexpected issues that slowed progress
- Missing dependencies
- Unclear requirements
- Tool limitations

**Workarounds Applied:**
- Temporary fixes
- Alternative approaches taken
- Hacks that should be revisited

**Time Sinks:**
- Tasks that took longer than expected
- Repeated attempts at the same problem
- Debugging sessions

**Successes:**
- Features completed
- Problems solved
- Improvements made

### Step 4: Categorize Findings

Group findings into:

1. **Preventable Issues** - Could have been avoided with better preparation
2. **Knowledge Gaps** - Things we didn't know that caused problems
3. **Tool Improvements Needed** - Commands or workflows that need enhancement
4. **Process Improvements Needed** - Workflow changes to prevent recurrence

### Step 5: Generate Retrospective Document

Create the file with this structure:

```markdown
# Retrospective: [SESSION_NAME]

**Date**: YYYY-MM-DD
**File**: retrospective-YYYY-MM-DD-NNN-session-name.md

## Summary

Brief overview of what was accomplished during this session.

## Errors Encountered

| Error | Cause | Resolution | Prevention |
|-------|-------|------------|------------|
| [error message] | [root cause] | [how it was fixed] | [how to avoid next time] |

## Snags & Blockers

- **[Snag Name]**: Description of the issue, its impact, and how it was resolved.

## Workarounds Applied

- **[Workaround]**: What was done and why. Note if this should be revisited.

## Lessons Learned

1. [Key takeaway 1]
2. [Key takeaway 2]
3. [Key takeaway 3]

## Command Improvements

Specific changes recommended for existing commands:

- `/EA-command-name`: [Specific change needed and why]

## Process Improvements

Workflow or process changes to consider:

- [Recommendation 1]
- [Recommendation 2]

## Metrics

- Tasks completed: [count]
- Issues encountered: [count]
- Estimated time on issues vs productive work: [ratio or percentage]

## Next Session Recommendations

Actionable items for the next session:

- [ ] [Action item 1]
- [ ] [Action item 2]
- [ ] [Action item 3]
```

### Step 6: Save and Report

Write the file and confirm:

```
Retrospective created!

File: docs/retrospectives/retrospective-YYYY-MM-DD-NNN-session-name.md

Summary:
- Errors documented: [count]
- Lessons learned: [count]
- Improvements suggested: [count]

Run /EA-apply-learnings to implement recommended changes.
```

## Analysis Guidelines

When analyzing the conversation:

1. **Be specific** - Quote actual error messages and file paths
2. **Find root causes** - Don't just document symptoms
3. **Make actionable** - Every lesson should have a prevention strategy
4. **Be honest** - Include failures and missteps, not just successes
5. **Prioritize** - Focus on issues with the biggest impact

## Notes

- This command does NOT require Omni-Cortex or any external memory system
- All data is stored in local markdown files
- Retrospectives can be reviewed and searched using standard file tools
- The /EA-apply-learnings command can process these files to implement improvements
