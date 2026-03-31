---
name: data-os
description: Query business metrics using natural language. Access YouTube stats, Google Analytics, Product metrics, and more.
allowed-tools: Bash(python3 execution/data_os/query.py *), Bash(python3 execution/data_os/snapshot.py)
---

# Data OS Skill

## Purpose

Query the AIOS metrics database with natural language questions about business performance.

## Commands

### Query metrics with natural language

```bash
python3 execution/data_os/query.py "What is our current MRR?"
python3 execution/data_os/query.py "How many YouTube subscribers do we have?"
python3 execution/data_os/query.py "Show me revenue from last week"
```

### Run data snapshot (pull fresh data from all sources)

```bash
python3 execution/data_os/snapshot.py
```

## Available Metrics

- **Product (Supabase)**: users, funnel, revenue, assessments, specialists, retention, packages
- **YouTube**: subscribers, total views, video count
- **Google Analytics**: active users, new users, revenue
- **Google Sheets**: P&L data, financial metrics
- **Yandex Metrika**: visits, pageviews, bounce rate, traffic sources

## Workflow

1. User asks about a metric
2. Run `query.py` with the natural language question
3. Return the formatted results
4. If data is stale, suggest running `snapshot.py` first

## Data Location

Metrics are stored in `data/aios_data.db` (SQLite). The `query.py` script translates natural language to SQL and executes it.
