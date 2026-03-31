---
description: Analyze an external workspace and generate a full Claude Code optimization report
allowed-tools: Bash, Read, Glob, Grep, Write
argument-hint: [/path/to/workspace]
model: opus
---

# EA-Analyze-Workspace

Deep-audit any Claude Code workspace against best practices. Produces a scored, prioritized optimization report saved to `docs/reports/`.

## Arguments

- `$ARGUMENTS` — Absolute path to the workspace to analyze (required)
  - Example: `/Users/you/my-project`
  - Example: `/Users/you/AIOS`

## Reference: Ideal Workspace Baseline

Use this as the scoring benchmark throughout the audit.

### 17 Canonical Commands
`EA-all-tools`, `EA-apply-learnings`, `EA-build`, `EA-commit`, `EA-create-command`, `EA-create-skill`, `EA-handoff`, `EA-parallel-subagents`, `EA-pickup`, `EA-plan`, `EA-prime`, `EA-retrospective`, `EA-review`, `EA-screenshot-compare`, `EA-subagent-log`, `EA-validate`, `EA-visual-verify`

### 5 Canonical Agents
`code-reviewer`, `doc-generator`, `secure-file-reader`, `test-runner`, `validated-builder`

### Damage-Control Hooks (5 files)
`bash-tool-guard.py`, `edit-tool-guard.py`, `write-tool-guard.py`, `bash-output-validator.py`, `patterns.yaml`

### Validator Hooks (3 files)
`auto-test-runner.py`, `build-validator.py`, `test-validator.py`

### Subagent Logger
`subagent-logger.py`

### 7 Canonical Skills
`file-factory`, `mcp-builder`, `secure-api-call`, `security-audit`, `skill-creator`, `time-travel`, `video-transcript-extractor`

### 4 Canonical MCPs
`playwright`, `ea-memory`, `ea-prompts`, `ea-journal`

### Ideal Settings.json
- Hooks use `uv run` (not `python`)
- PreToolUse: bash-tool-guard, edit-tool-guard, write-tool-guard
- PostToolUse: bash-output-validator, auto-test-runner
- No `Read` hook (common mistake)
- Deny rules: `Bash(rm -rf *)`, `Bash(sudo *)`, `Read(.env)`

### Ideal Directory Structure
```
.claude/CLAUDE.md         # project memory
.claude/commands/         # slash commands
.claude/agents/           # subagent definitions
.claude/hooks/
  damage-control/         # 5 guard scripts
  validators/             # 3 test runners
  subagent-logger.py
.claude/skills/           # skill packs
.mcp.json                 # MCP config
.gitignore                # includes logs/*.json
mcps/                     # ea-memory, ea-prompts, ea-journal servers
templates/                # command-template.md, spec-template.md, mcp-json-full.json
app/client/ + app/server/ # or equivalent source structure
ai_docs/                  # API reference docs for agents
docs/guides/              # organized reference guides
docs/retrospectives/      # session analysis
specs/todo/ + done/ + handoffs/
validation/screenshots/
logs/
README.md
```

### CLAUDE.md Must-Have Sections
Quick Reference paths, Commands table, Skills table, Agents table, MCP Services section, Hook System section, Workflow (5 phases)

---

## Workflow

### Step 1: Setup

Parse `$ARGUMENTS` as the target workspace path. Derive the workspace name from the last path segment.

```bash
# Ensure output directory exists
mkdir -p docs/reports

# Get today's date
date +%Y-%m-%d
```

Set output file: `docs/reports/[workspace-name]-YYYY-MM-DD.md`

### Step 2: Parallel Exploration

Gather data across all categories simultaneously. For each check below, record: ✅ (fully present), ⚠️ (partial), or ❌ (missing).

#### A. Root-Level Structure
```bash
ls -la $ARGUMENTS/
```
Check for: `.claude/`, `.mcp.json`, `.gitignore`, `README.md`, `mcps/`, `templates/`, `app/`, `ai_docs/`, `docs/`, `specs/`, `validation/`, `logs/`

#### B. CLAUDE.md Quality
Read `$ARGUMENTS/.claude/CLAUDE.md` if it exists. Score these elements:
- File exists
- Has Quick Reference section with key paths
- Has Commands table (with at least 10 commands)
- Has Skills table
- Has Agents table
- Has MCP Services section
- Has Hook System section
- Has Workflow / 5-phase description
- Under 500 tokens (concise, scannable)

#### C. Commands Audit
```bash
ls $ARGUMENTS/.claude/commands/ 2>/dev/null
```
Compare against the 17 canonical commands. Note:
- Which are present ✅
- Which are missing ❌
- Any non-standard commands (custom additions — these are a positive signal)
- Any EA-install.md or EA-demo-* files (course leftovers — should be removed)

#### D. Agents Audit
```bash
ls $ARGUMENTS/.claude/agents/ 2>/dev/null
```
Compare against 5 canonical agents. Note custom agents too.

#### E. Hooks Audit
```bash
ls $ARGUMENTS/.claude/hooks/ 2>/dev/null
ls $ARGUMENTS/.claude/hooks/damage-control/ 2>/dev/null
ls $ARGUMENTS/.claude/hooks/validators/ 2>/dev/null
```
Check for all 5 damage-control files, all 3 validator files, subagent-logger.py.

Also read `$ARGUMENTS/.claude/settings.json` if it exists and check:
- Are hooks registered with `uv run` (not `python`)?
- Are all 3 PreToolUse hooks wired?
- Is PostToolUse wired with bash-output-validator AND auto-test-runner?
- Is there an erroneous Read hook?
- Are deny rules present?

#### F. Skills Audit
```bash
ls $ARGUMENTS/.claude/skills/ 2>/dev/null
ls $ARGUMENTS/skills/ 2>/dev/null
```
Compare against 7 canonical skills. Note custom skills.

#### G. MCP Audit
Read `$ARGUMENTS/.mcp.json` if it exists. Check:
- File exists
- All 4 canonical MCPs configured (playwright, ea-memory, ea-prompts, ea-journal)
- ea-* MCPs use relative `./mcps/` paths (not absolute)
- ea-* MCPs use `uv run` pattern
```bash
ls $ARGUMENTS/mcps/ 2>/dev/null
```
Check for ea-memory/, ea-prompts/, ea-journal/ with server.py files

#### H. Templates Audit
```bash
ls $ARGUMENTS/templates/ 2>/dev/null
```
Check for: `command-template.md`, `spec-template.md`, `mcp-json-full.json`

#### I. Directory Structure Audit
```bash
find $ARGUMENTS -maxdepth 3 -type d | sort
```
Check for all ideal directories. Note missing ones.

#### J. Documentation Audit
```bash
ls $ARGUMENTS/docs/ 2>/dev/null
ls $ARGUMENTS/docs/guides/ 2>/dev/null
```
Check for:
- `README.md` at root (read first 20 lines to assess quality)
- `docs/guides/` with organized subdirectories
- `docs/retrospectives/`
- `ai_docs/` directory

#### K. Gitignore Audit
Read `$ARGUMENTS/.gitignore` if it exists. Check for:
- `node_modules/`, `__pycache__/`, `.env`, `.DS_Store` (standard entries)
- `logs/*.json` (subagent log exclusion — often missing)
- `.claude/settings.local.json`

### Step 3: Calculate Scores

Tally scores for each category (each ✅ = 1 point, ⚠️ = 0.5, ❌ = 0):

| Category | Max Points |
|----------|-----------|
| CLAUDE.md quality | 9 |
| Commands coverage | 17 |
| Agents coverage | 5 |
| Damage-control hooks | 5 |
| Validator hooks | 3 |
| Subagent logger | 1 |
| Settings correctness | 6 |
| Skills coverage | 7 |
| MCP configuration | 6 |
| Templates | 3 |
| Directory structure | 12 |
| Documentation | 4 |
| Gitignore | 4 |

**Total: 82 points possible**

Convert to percentage and grade:
- 90–100%: A — Production Ready
- 75–89%: B — Solid, minor gaps
- 60–74%: C — Functional, meaningful gaps
- 40–59%: D — Basic setup, significant gaps
- <40%: F — Needs major work

### Step 4: Identify Custom Additions

Beyond the baseline check, look for things the workspace has that the template doesn't:
- Custom commands not in the canonical 17
- Custom agents not in the canonical 5
- Custom skills beyond the 7
- Additional MCPs
- Project-specific guides
- Any unique architectural decisions

These are strengths — call them out positively.

### Step 5: Generate Report

Save to `docs/reports/[workspace-name]-YYYY-MM-DD.md`:

```markdown
# Workspace Audit: [Workspace Name]

**Date**: YYYY-MM-DD
**Path**: /path/to/workspace
**Overall Score**: NN/82 (NN%) — Grade: [A/B/C/D/F] — [Label]

---

## Executive Summary

[3–4 sentences: what this workspace is doing well, the biggest gap areas, and the single most impactful thing they should do first.]

---

## Category Scores

| Category | Score | Max | Status |
|----------|-------|-----|--------|
| CLAUDE.md Quality | N | 9 | ✅/⚠️/❌ |
| Commands | N | 17 | ✅/⚠️/❌ |
| Agents | N | 5 | ✅/⚠️/❌ |
| Damage-Control Hooks | N | 5 | ✅/⚠️/❌ |
| Validator Hooks | N | 3 | ✅/⚠️/❌ |
| Subagent Logger | N | 1 | ✅/⚠️/❌ |
| Settings.json | N | 6 | ✅/⚠️/❌ |
| Skills | N | 7 | ✅/⚠️/❌ |
| MCP Configuration | N | 6 | ✅/⚠️/❌ |
| Templates | N | 3 | ✅/⚠️/❌ |
| Directory Structure | N | 12 | ✅/⚠️/❌ |
| Documentation | N | 4 | ✅/⚠️/❌ |
| Gitignore | N | 4 | ✅/⚠️/❌ |
| **TOTAL** | **N** | **82** | |

---

## What This Workspace Does Well

[Bullet list of genuine strengths — present components, custom additions, good patterns.]

---

## Detailed Findings

### CLAUDE.md Quality
[What's present, what sections are missing, quality assessment]

### Commands ([N]/17 present)

**Present**: [list]
**Missing**: [list with brief note on what each does]
**Extras** (custom): [list — these are good!]
**To remove**: [EA-install / EA-demo files if found]

### Agents ([N]/5 present)

**Present**: [list]
**Missing**: [list]
**Custom agents**: [list]

### Security Hooks

**Damage-Control** ([N]/5):
- [file]: ✅/❌
...

**Validators** ([N]/3):
- [file]: ✅/❌
...

**Subagent Logger**: ✅/❌

**settings.json**:
- Hook wiring: [assessment]
- uv run usage: ✅/❌
- Deny rules: [assessment]
- Issues found: [list any problems]

### Skills ([N]/7 present)

**Present**: [list]
**Missing**: [list]
**Custom skills**: [list]

### MCP Configuration

**Configured MCPs**: [list from .mcp.json]
**Missing MCPs**: [list]
**Path style**: relative ✅ / absolute ⚠️ / n/a
**ea-* servers present**: ✅/❌

### Settings & Permissions

[Detailed assessment of .claude/settings.json]

### Templates ([N]/3 present)

[Which templates present, which missing]

### Directory Structure

**Present directories**:
- [list]

**Missing directories**:
- [directory]: [what it's used for]

### Documentation

**README.md**: [quality assessment]
**docs/guides/**: [present/missing, how many files]
**docs/retrospectives/**: ✅/❌
**ai_docs/**: ✅/❌

### Gitignore

[Assessment of .gitignore completeness]

---

## Custom Additions (Beyond Baseline)

[Positive section — everything this workspace has that the baseline doesn't. Custom commands, agents, skills, MCPs, workflows, unique architecture decisions.]

---

## Prioritized Recommendations

### 🔴 High Priority — Do These First

[Items with the biggest security or workflow impact. Each item includes:]
- **[Item]**: Why it matters + exact fix

### 🟡 Medium Priority — Next Sprint

[Items that meaningfully improve the workflow but aren't urgent.]

### 🟢 Quick Wins — Under 5 Minutes Each

[Small things with high value-to-effort ratio.]

---

## Copy-Paste Fixes

Where applicable, provide the exact commands or file snippets to resolve issues:

### Missing Commands
```bash
# Copy missing commands from the CCEA template
cp /path/to/CCEA/.claude/commands/EA-[name].md .claude/commands/
```

### Missing Hooks
```bash
# Copy damage-control suite
cp -r /path/to/CCEA/.claude/hooks/damage-control .claude/hooks/
```

### Gitignore Fix
```
# Add to .gitignore:
logs/*.json
.claude/settings.local.json
```

### Settings.json Hook Pattern
```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Bash", "hooks": [{ "type": "command", "command": "uv run .claude/hooks/damage-control/bash-tool-guard.py", "timeout": 10000 }] },
      { "matcher": "Edit", "hooks": [{ "type": "command", "command": "uv run .claude/hooks/damage-control/edit-tool-guard.py", "timeout": 10000 }] },
      { "matcher": "Write", "hooks": [{ "type": "command", "command": "uv run .claude/hooks/damage-control/write-tool-guard.py", "timeout": 10000 }] }
    ],
    "PostToolUse": [
      { "matcher": "Bash", "hooks": [
        { "type": "command", "command": "uv run .claude/hooks/damage-control/bash-output-validator.py", "timeout": 10000 },
        { "type": "command", "command": "uv run .claude/hooks/validators/auto-test-runner.py", "timeout": 10000 }
      ]}
    ]
  }
}
```

---

*Report generated by `/EA-analyze-workspace` from the CCEA starter template.*
*To re-run: `/EA-analyze-workspace [workspace-path]`*
```

### Step 6: Confirm

Output to the user:

```
Workspace audit complete!

Report: docs/reports/[workspace-name]-YYYY-MM-DD.md
Score: NN/82 (NN%) — Grade [X]

Top 3 findings:
1. [Most impactful issue]
2. [Second most impactful issue]
3. [Third most impactful issue]

Run /EA-analyze-workspace [path] to audit another workspace.
```

## Guidelines

- **Be specific**: Name exact files missing, not just "hooks are incomplete"
- **Be balanced**: Lead with what's working before diving into gaps
- **Be actionable**: Every finding must have a clear fix
- **Custom additions are a positive**: A workspace that has MORE than the baseline is doing well
- **Context matters**: A brand-new project missing guides is different from a mature workspace missing security hooks
- **Score fairly**: Partial implementations get half credit
