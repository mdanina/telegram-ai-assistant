---
description: Apply learnings from retrospective reports to improve commands and workflows
allowed-tools: Bash, Read, Glob, Grep, Edit, Write
argument-hint: [N] or [path] - number for last N retrospectives, path for specific file
model: sonnet
---

# EA-Apply-Learnings Command

Read retrospective files and apply recommended improvements to commands and workflows.

## Arguments

- (none) - Apply the most recent retrospective only
- `N` (1-9) - Apply the last N retrospectives
- `<path>` - Apply a specific retrospective file

## Workflow

### Step 1: Locate Retrospective Files

Based on the argument:

**No argument (most recent):**
```
Glob: docs/retrospectives/retrospective-*.md
Sort by filename descending, take first
```

**Number N:**
```
Glob: docs/retrospectives/retrospective-*.md
Sort by filename descending, take first N
```

**Specific path:**
```
Read: <provided path>
Verify file exists
```

### Step 2: Parse Retrospective Content

For each retrospective file, extract:

1. **Command Improvements** section
   - Target command name
   - Specific change needed

2. **Process Improvements** section
   - Workflow changes
   - Documentation updates

3. **Lessons Learned** section
   - Patterns to codify
   - Checks to add

### Step 3: Categorize by Risk

**Low Risk (auto-apply):**
- Adding comments or documentation
- Adding new validation steps
- Fixing typos in commands
- Adding helpful output messages

**Medium Risk (apply with note):**
- Changing command logic
- Adding new workflow steps
- Modifying report formats
- Adding new checks

**High Risk (ask first):**
- Removing functionality
- Changing allowed-tools
- Structural refactoring
- Modifying core workflow steps

### Step 4: Execute Improvements

For each improvement:

1. **Check if applicable**
   - Does the target file exist?
   - Is the change still relevant?

2. **Apply based on risk level**

   **Low Risk:**
   ```
   Apply automatically
   Log: "Applied: [description]"
   ```

   **Medium Risk:**
   ```
   Apply automatically
   Log: "Applied (review recommended): [description]"
   ```

   **High Risk:**
   ```
   Skip application
   Log: "Skipped (manual review required): [description]"
   List in report for user review
   ```

3. **Track results**
   - Success count
   - Skipped count
   - Failed count

### Step 5: Error Handling

**Retry Logic:**
- MAX_RETRIES = 3 per improvement
- If an improvement fails, retry up to 3 times
- After 3 failures, mark as failed and continue

**Circuit Breaker:**
- MAX_CONSECUTIVE_ERRORS = 5
- If 5 improvements fail in a row, stop processing
- Report current state and ask user how to proceed

**Failure Logging:**
- Record all failures with error messages
- Include in final report for manual review

### Step 6: Generate Report

```markdown
## Apply Learnings Summary

**Retrospective(s) Processed:**
- docs/retrospectives/retrospective-YYYY-MM-DD-NNN.md
- [additional files if multiple]

**Improvements Applied:**

| # | Risk | Type | Target | Change | Status |
|---|------|------|--------|--------|--------|
| 1 | Low | Command | /EA-build | Added lint check before build | Applied |
| 2 | Medium | Process | Workflow | Added pre-commit validation step | Applied |
| 3 | High | Command | /EA-validate | New framework detection logic | Skipped |

**Statistics:**
- Total improvements: X
- Applied: Y
- Skipped (high risk): Z
- Failed: W

**Commands Modified:**
- `.claude/commands/EA-build.md` - [change summary]
- `.claude/commands/EA-validate.md` - [change summary]

**Files Created:**
- [any new files created]

**Skipped (needs manual review):**

1. **[Improvement description]**
   - Target: [file or command]
   - Reason: High risk - [specific concern]
   - Recommended action: [what to do manually]

**Failed (needs investigation):**

1. **[Improvement description]**
   - Target: [file or command]
   - Error: [error message]
   - Suggestion: [how to fix manually]

**Next Steps:**
1. Test modified commands to verify changes work
2. Review skipped improvements and apply manually if appropriate
3. Investigate any failed improvements
```

## Improvement Types

### Command Improvements

When applying command improvements:

1. Read the target command file
2. Locate the section to modify
3. Apply the change using Edit tool
4. Verify the change was applied correctly

Example:
```
Target: /EA-validate
Change: Add Python type checking step

Action: Edit .claude/commands/EA-validate.md
Add "python -m mypy ." to Python validation steps
```

### Process Improvements

When applying process improvements:

1. Determine if it affects commands or documentation
2. For commands: Update the relevant workflow section
3. For documentation: Create or update doc files
4. For both: Apply to all relevant locations

### Documentation Updates

When adding documentation:

1. Prefer updating existing files over creating new ones
2. Add to relevant sections (don't scatter information)
3. Use consistent formatting with existing docs

## Notes

- This command works with file-based retrospectives (no Omni-Cortex required)
- Always preview high-risk changes before applying
- Keep a log of all changes for audit purposes
- Run /EA-validate after applying changes to ensure nothing broke
