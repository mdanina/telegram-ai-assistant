---
description: Launch parallel agents to accomplish a task
allowed-tools: Task
model: sonnet
argument-hint: [prompt request] [count]
---

# Parallel Subagents

## Purpose

Launch multiple agents simultaneously to work on a task in parallel. Useful for research, searching, or any task that can be split into independent pieces.

## Variables

PROMPT_REQUEST: $1
COUNT: $2

## Instructions

- Each agent receives complete context (they don't share memory)
- Design prompts that are self-contained
- Agents work independently and return their results
- Use for tasks that can be parallelized (research, search, analysis)

## Workflow

1. Parse input parameters
   - Extract PROMPT_REQUEST to understand the task
   - Determine COUNT (use provided value or infer from task complexity)

2. Design agent prompts
   - Create detailed, self-contained prompts for each agent
   - Include specific instructions on what to accomplish
   - Define clear output expectations
   - Remember: agents are stateless and need complete context

3. Launch parallel agents
   - Use Task tool to spawn all agents simultaneously
   - Ensure all agents launch in a single parallel batch

4. Collect and summarize results
   - Gather outputs from all completed agents
   - Synthesize findings into cohesive response

## Report

```
Parallel Execution Complete

Agents Launched: [count]
Task: [brief description]

Results:
Agent 1: [summary of findings]
Agent 2: [summary of findings]
...

Combined Summary:
[Synthesized findings from all agents]
```
