---
name: intelligence
description: Access daily intelligence reports from meetings and voice notes.
allowed-tools: Bash(python3 execution/intelligence/intelligence_orchestrator.py), Read(data/intelligence_reports/*)
---

# Intelligence Skill

## Purpose

Access analyzed intelligence from Fireflies meetings and voice notes.

## Commands

### Run intelligence pipeline (pull and analyze new data)

```bash
python3 execution/intelligence/intelligence_orchestrator.py
```

### Read latest intelligence report

Use the Read tool to open the most recent file from `data/intelligence_reports/`.

Example:
```
Read data/intelligence_reports/2026-02-27.json
```

## Report Structure

Each daily report (JSON) contains:
- `meetings`: array of analyzed transcripts (summary, action_items, strategy_flags, content_ideas, sentiment)
- `voice_notes`: array of processed voice notes

## Workflow

1. Check if today's report exists in `data/intelligence_reports/`
2. If not, run `intelligence_orchestrator.py` to generate it
3. Read the report and summarize key insights
4. Highlight action items, strategy flags, and content ideas

## Meeting Analysis Fields

Each meeting entry includes:
- `summary`: one-paragraph summary
- `action_items`: list of tasks with owner and due_date
- `strategy_flags`: strategic decisions or changes discussed
- `content_ideas`: YouTube/blog content opportunities
- `sentiment`: Positive / Neutral / Negative / Mixed
