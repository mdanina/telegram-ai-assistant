---
description: Generate a new skill using the skill-creator patterns
allowed-tools: Read, Write, Glob, AskUserQuestion
model: sonnet
argument-hint: [skill name or description]
---

# Create New Skill

## Purpose

Generate a new skill following best practices from the skill-creator skill. This command guides you through skill creation with the proper structure.

## Variables

SKILL_INPUT: $ARGUMENTS

## Instructions

- Follow the skill-creator patterns in skills/skill-creator/
- Keep skills focused - one domain, clear purpose
- Use the template from templates/skill-template/
- Create in current project's .claude/skills/ by default

## Workflow

1. Gather skill requirements:
   - If SKILL_INPUT provided, parse for skill name/purpose
   - Otherwise, ask:
     - What should this skill do?
     - What keywords should trigger it?
     - Does it need scripts, references, or assets?

2. Read the skill-creator SKILL.md for best practices

3. Create skill folder structure:
   ```
   .claude/skills/[skill-name]/
   ├── SKILL.md
   ├── scripts/     (if needed)
   ├── references/  (if needed)
   └── assets/      (if needed)
   ```

4. Generate SKILL.md:
   - Write frontmatter with name and description
   - Include trigger keywords in description
   - Add workflow sections
   - Reference any sub-files

5. If scripts needed:
   - Create placeholder scripts
   - Add usage instructions to SKILL.md

6. If references needed:
   - Create reference files
   - Add pointers in SKILL.md

## Report

```
Created skill: [skill-name]

Location: .claude/skills/[skill-name]/

Files created:
- SKILL.md (entry point)
- [other files]

Trigger keywords: [keywords from description]

Next steps:
1. Test the skill with a sample request
2. Refine based on actual usage
3. Run /EA-install to copy globally if desired
```

## Examples

**Quick creation:**
```
/EA-create-skill pdf-rotator
```

**With description:**
```
/EA-create-skill "A skill that helps format code for documentation"
```

**Interactive:**
```
/EA-create-skill
→ What should this skill do? Manage git worktrees
→ Keywords? worktree, parallel, branches
→ Need scripts? Yes
→ Creates .claude/skills/git-worktree-manager/
```
