---
description: Create a new command using the standard template
allowed-tools: Write, Read, WebFetch
model: sonnet
argument-hint: [description of what the command should do]
---

# Create Command

## Purpose

Generate a new command file using the standard template pattern. Provide a high-level description of what you want the command to do, and this will create a properly structured command file.

## Variables

HIGH_LEVEL_PROMPT: $ARGUMENTS
COMMANDS_DIR: .claude/commands/

## Instructions

- Always use the standard template structure
- Generate a descriptive kebab-case filename
- Include all relevant sections (Purpose, Variables, Instructions, Workflow, Report)
- Choose appropriate tools based on what the command needs to do
- Set model to "sonnet" unless deep reasoning is required (then "opus")
- Do not create sections not in the template

## Workflow

1. **Analyze the request**
   - Understand what the command should accomplish
   - Identify required tools
   - Determine if arguments are needed

2. **Generate command name**
   - Create descriptive kebab-case name
   - Example: "search-and-replace", "generate-docs", "run-tests"

3. **Determine metadata**
   - Select appropriate allowed-tools
   - Choose model (sonnet for most, opus for complex reasoning)
   - Write clear description
   - Define argument-hint if arguments needed

4. **Design the command**
   - Write clear Purpose section
   - Define Variables (dynamic first, then static)
   - List Instructions as bullet points
   - Create numbered Workflow steps
   - Define Report format

5. **Save the command**
   - Write to `.claude/commands/[name].md`
   - Confirm creation

## Template Structure

```markdown
---
description: [clear description for /help]
allowed-tools: [comma-separated tools]
model: sonnet
argument-hint: [if arguments needed]
---

# Command Name

## Purpose
[What it does and when to use it]

## Variables
[Dynamic and static variables]

## Instructions
[Bullet-pointed rules and constraints]

## Workflow
[Numbered execution steps]

## Report
[Output format]
```

## Report

```
Command Created

File: .claude/commands/[name].md
Description: [description from metadata]
Tools: [allowed-tools]
Model: [model]

To use: /[command-name] [arguments if any]
```
