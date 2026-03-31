# AIOS — AI Operating System for Business

A Telegram-based AI Operating System that acts as a personal CEO assistant. Handles tasks, meetings, metrics, emails, reminders, research, and strategic reporting — all through natural conversation.

## Architecture

5-layer system:

1. **Context OS** — Markdown files with business knowledge (`context/`)
2. **Data OS** — SQLite + 7 data collectors for business metrics (`execution/data_os/`)
3. **Intelligence Layer** — Automated analysis: meetings, articles, self-improvement (`execution/intelligence/`)
4. **Automation Layer** — 9 cron jobs for scheduled operations (`cron/`)
5. **Interface Layer** — Telegram bot + daily briefings + heartbeat nudges (`execution/telegram/`, `execution/daily_brief/`)

## Features

### Telegram Bot (Python)

| Feature | Details |
|---------|---------|
| **AI Chat** | GPT-5.4 with 11 function-calling tools, context-aware routing |
| **Voice Messages** | Faster-Whisper (int8 quantized, local), batch task extraction from single voice |
| **Text-to-Speech** | edge-tts, 23 languages (RU, EN, TR, ES, FR, DE, IT, PT, ZH, JA, KO, AR, HI + 10 more) |
| **Photo Analysis** | GPT-4o Vision — OCR, description, task extraction |
| **Email** | IMAP/SMTP (Yandex) — check, read, send, reply with RFC 2822 quoting |
| **GTD Tasks** | Create, list, complete, with domain classification (product / secondary / personal) |
| **Reminders** | Relative (+30m, +2h), absolute (14:00), recurring (repeat_seconds), Moscow TZ |
| **File Delivery** | Smart filtering by name, auto-archive to categories (contracts, invoices, accounting) |
| **Meeting Upload** | Audio/video/video notes → Fireflies.ai transcription |
| **Document Processing** | Transcript detection, action keywords (translate, analyze, summarize), Claude Code delegation |
| **Semantic Memory** | ChromaDB vector search over long-term conversation memories |
| **Web Search** | Built-in web search tool |
| **Translation** | Translate text + generate voice in target language |
| **Claude Code** | Proxy to Claude Code CLI for advanced tasks |

### Alternative Bot (TypeScript)

A full alternative implementation in `execution/bot/src/` using the grammy framework:
- Agent-based message routing
- Voice (transcribe + synthesize)
- SQLite database, scheduler, memory system
- Context window tracking

### Intelligence Layer (Automated)

| Module | Schedule | What it does |
|--------|----------|--------------|
| **Daily Brief** | 07:00 UTC | Aggregates metrics from 7 sources, synthesizes CEO briefing via LLM |
| **Morning Digest** | 07:05 UTC | Structured task list + yesterday's meetings (no LLM) |
| **Heartbeat** | Every 30 min | CEO nudges: insights (metric changes), coaching, evening recap. Anti-spam: max 2/day, 4h gap, quiet hours |
| **Meeting Autoprocess** | Every 2h | Fireflies → LLM analysis → action items → GTD tasks |
| **Article Finder** | 06:00 UTC | PubMed search → full text fetch → LLM narrative review → PDF → Telegram |
| **Self-Improvement** | 08:00 UTC | Even days: code review of entire codebase. Odd days: web search for AI patterns |
| **Weekly Report** | Sun 19:00 UTC | 7-day trends: revenue, users, funnel, tasks, meetings → strategic summary |

### Data OS — 5 Collectors

| Collector | Source | Metrics |
|-----------|--------|---------|
| **YouTube** | Data API v3 | Subscribers, views, video count |
| **Google Analytics** | GA4 API | Active users, new users, revenue |
| **Google Sheets** | Sheets API | Custom metrics from spreadsheets |
| **Yandex Metrika** | Metrika API | Visits, pageviews, traffic sources, bounce rate |
| **Product (Supabase)** | PostgREST | 30+ product metrics (users, funnel, revenue, retention) |

Domain router classifies all data into: `product`, `secondary_product`, `personal`.

## Telegram Commands

| Command | Description |
|---------|-------------|
| `/brief` | Generate daily CEO briefing |
| `/query <question>` | Query business data in natural language |
| `/dashboard` | Instant key metrics (no LLM) |
| `/tasks` | View tasks with done-buttons |
| `/files` | Send outbox files, auto-archive |
| `/cc <prompt>` | Delegate to Claude Code |
| `/skills` | Quick action buttons |
| `/newchat` | Clear conversation history |
| `/status` | Model info, stats, uptime |
| `/compact` | Compress long conversation history |
| `/memory` | List stored memory facts |
| `/forget <id>` | Delete memory fact |
| `/reminders` | List pending reminders |
| `/cancel <id>` | Cancel reminder |
| `/translate <lang> <text>` | Translate + voice |
| `/voice` | Toggle voice reply mode |
| `/search <query>` | Web search |
| `/help` | Full command reference |

## Quick Start

### 1. Clone and install

```bash
git clone <this-repo-url>
cd aios
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
```

Fill in API keys. Minimum required:

| Variable | Required | Purpose |
|----------|----------|---------|
| `OPENAI_API_KEY` | Yes | GPT chat, Whisper, Vision |
| `TELEGRAM_BOT_TOKEN` | Yes | Telegram bot |
| `TELEGRAM_ALLOWED_USER_IDS` | Yes | Comma-separated user IDs for access control |

Optional integrations:

| Variable | Purpose |
|----------|---------|
| `GROQ_API_KEY` | Fallback LLM when OpenAI is down |
| `YOUTUBE_API_KEY`, `YOUTUBE_CHANNEL_ID` | YouTube collector |
| `GA4_PROPERTY_ID` | Google Analytics collector |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to GCP service account JSON (GA4, Sheets) |
| `FINANCE_SHEET_ID` | Google Sheets collector |
| `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` | Product (Supabase) collector |
| `FIREFLIES_API_KEY` | Meeting transcription + autoprocess |
| `YANDEX_EMAIL`, `YANDEX_APP_PASSWORD` | Email integration |
| `YANDEX_METRIKA_TOKEN`, `YANDEX_METRIKA_COUNTER_ID` | Yandex Metrika collector |
| `ARTICLE_SEARCH_TERMS` | PubMed search query for article finder |
| `ARTICLE_TOPIC` | Topic description for article reviews (Russian) |
| `ARTICLE_EXCLUDE` | Exclusion keywords for articles |
| `ARTICLE_AUDIENCE` | Target audience for articles |
| `AIOS_TTS_VOICE` | Default TTS voice (e.g., `ru-RU-DmitryNeural`) |

### 3. Customize context

Edit files in `context/` with your business information:
- `business_hierarchy.md` — company structure
- `team.md` — team roles
- `strategy.md` — goals and priorities
- `offers.md` — products and services
- `soul.md` — bot personality
- `voice.md` — brand voice guidelines

### 4. Run

```bash
python3 execution/telegram/bot.py
```

### 5. Set up cron jobs (optional)

```cron
# Data collection
0 6 * * *      /opt/aios/cron/data_snapshot.sh

# Daily briefings
0 7 * * *      /opt/aios/cron/daily_brief.sh
5 7 * * *      /opt/aios/cron/morning_digest.sh

# Reminders
*/15 * * * *   /opt/aios/cron/task_reminder.sh

# Intelligence
0 8 * * *      /opt/aios/cron/self_improve.sh
0 6 * * *      /opt/aios/cron/article_finder.sh
*/120 * * * *  /opt/aios/cron/meeting_autoprocess.sh

# Heartbeat nudges
*/30 * * * *   /opt/aios/cron/heartbeat.sh

# Weekly report
0 19 * * 0     /opt/aios/cron/weekly_report.sh
```

## Database Schema

SQLite with the following tables:

| Table | Purpose |
|-------|---------|
| `tasks` | GTD tasks (text, next_action, project, due_date, domain, status) |
| `metrics` | Business metrics snapshots (source, metric_name, value, date) |
| `conversation_history` | Chat context for GPT |
| `bot_memories` | Long-term memory facts extracted from conversations |
| `reminders` | Scheduled reminders (fire_at, repeat_seconds, status) |
| `processed_meetings` | Deduplication for Fireflies autoprocess |
| `article_registry` | Processed articles (pmid, title, review_text, pdf_path) |
| `self_improve_log` | Self-improvement suggestions log |

## Claude Code Integration

This repo includes a full `.claude/` setup with:
- 50+ business skills (marketing, sales, strategy, content)
- Custom commands (`/plan`, `/build`, `/review`, `/commit`)
- Hook system (tool guards, output validators)
- Agent definitions (code reviewer, test runner, doc generator)

## Project Structure

```
execution/
  telegram/           # Bot handlers
    bot.py              # Entry point, handler registration
    task_handler.py     # Main AI router (11 function-calling tools)
    slash_commands.py   # All / commands
    voice_handler.py    # Faster-Whisper STT
    tts.py              # edge-tts (23 languages)
    photo_handler.py    # GPT-4o Vision
    email_handler.py    # IMAP/SMTP
    document_handler.py # File + transcript processing
    meeting_handler.py  # Fireflies upload
    scheduler.py        # Reminders (relative, absolute, recurring)
    memory_search.py    # ChromaDB semantic search
    skills_menu.py      # Inline buttons
    utils.py            # Claude Code proxy, git ops
  daily_brief/
    brief_generator.py  # Daily CEO briefing
    morning_digest.py   # Tasks + meetings digest
    heartbeat.py        # CEO nudges (3 types, anti-spam)
  intelligence/
    meeting_autoprocess.py  # Fireflies → action items → GTD
    article_finder.py       # PubMed → review → PDF
    self_improve.py         # Code review / feature scout
    weekly_report.py        # 7-day strategic summary
    intelligence_orchestrator.py  # Unstructured data analysis
  data_os/
    query.py            # Natural language data queries
    db_router.py         # Domain classification
    collectors/          # 5 data collectors
  bot/src/              # TypeScript alternative (grammy)
context/                # Business knowledge (markdown)
cron/                   # 9 shell scripts for scheduling
data/                   # SQLite DB, articles, transcripts
```

## Documentation

See `docs/telegram_bot.md` for detailed bot documentation including module-by-module breakdown and setup from scratch.

## License

MIT
