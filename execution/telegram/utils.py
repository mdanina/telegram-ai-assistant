#!/usr/bin/env python3
"""
Telegram Bot: Shared Utilities

Functions used by both task_handler.py and slash_commands.py.
"""

import os
import sys
import subprocess
import logging
import requests
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common import get_openai_client, MODEL_MAIN

logger = logging.getLogger(__name__)

BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "..")


def run_claude_code(prompt):
    """Runs Claude Code CLI with a prompt and returns the output."""
    try:
        full_prompt = (
            "You are AIOS — a personal AI assistant for the CEO. "
            "You are running on the AIOS server at /opt/aios/. "
            "RULES:\n"
            "1. Always respond in Russian.\n"
            "2. Execute tasks directly — never ask for approval or confirmation.\n"
            "3. Do NOT use markdown formatting (no **, no ```, no headers). "
            "Use plain text with line breaks and dashes for lists.\n"
            "4. Be concise — the response goes to Telegram (character limit).\n"
            "5. If you create files for the user, save them to data/outbox/ — "
            "the bot will auto-deliver them to Telegram.\n"
            "6. For email: use the gmail skill. For calendar: use google-calendar skill.\n\n"
            + prompt
        )
        result = subprocess.run(
            ["claude", "-p", "--allowedTools", "Bash,Read,Write,Edit,Glob,Grep,WebFetch,WebSearch"],
            input=full_prompt,
            capture_output=True,
            text=True,
            timeout=1800,  # 30 min — Claude Code может долго работать
            cwd=BASE_DIR,
            env={**os.environ},
        )
        output = result.stdout.strip() if result.stdout else ""
        stderr = result.stderr.strip() if result.stderr else ""
        if "Reached max turns" in (output + stderr):
            output = output.replace("Error: Reached max turns", "").strip()
            output = (output + "\n\n" if output else "") + "⚠️ Claude Code исчерпал лимит ходов."
        elif not output and stderr:
            output = f"Ошибка: {stderr[:2000]}"
        elif not output:
            output = "Claude Code не вернул результат."
        return output
    except subprocess.TimeoutExpired:
        return "Таймаут — Claude Code работал дольше 30 минут."
    except FileNotFoundError:
        return "Claude Code не найден на сервере. Убедитесь, что claude установлен глобально."
    except Exception as e:
        logger.error(f"Claude Code error: {e}")
        return f"Ошибка: {e}"


PRODUCT_REPO_DIR = "/opt/product"

# SSH wrapper for Product git operations (uses dedicated deploy key)
PRODUCT_GIT_SSH = "ssh -i /root/.ssh/product_deploy -o StrictHostKeyChecking=no"


def _product_reset_to_main():
    """Force-reset Product repo to main, cleaning up any dirty state."""
    git_env = {**os.environ, "GIT_SSH_COMMAND": PRODUCT_GIT_SSH}
    # Discard any uncommitted changes
    subprocess.run(
        ["git", "reset", "--hard"],
        cwd=PRODUCT_REPO_DIR, capture_output=True, text=True, timeout=10, env=git_env,
    )
    subprocess.run(
        ["git", "clean", "-fd"],
        cwd=PRODUCT_REPO_DIR, capture_output=True, text=True, timeout=10, env=git_env,
    )
    checkout = subprocess.run(
        ["git", "checkout", "main"],
        cwd=PRODUCT_REPO_DIR, capture_output=True, text=True, timeout=10, env=git_env,
    )
    if checkout.returncode != 0:
        logger.error("Product checkout main failed: %s", checkout.stderr)
        return  # don't continue cleanup in unknown state
    # Delete local bot/* branches to avoid clutter
    branches = subprocess.run(
        ["git", "branch", "--list", "bot/*"],
        cwd=PRODUCT_REPO_DIR, capture_output=True, text=True, timeout=10, env=git_env,
    )
    for branch in branches.stdout.strip().splitlines():
        branch = branch.strip().lstrip("* ")
        if branch:
            subprocess.run(
                ["git", "branch", "-D", branch],
                cwd=PRODUCT_REPO_DIR, capture_output=True, text=True, timeout=10, env=git_env,
            )


def run_claude_code_product(prompt):
    """Runs Claude Code CLI against the Product repo.

    Safety: Claude Code works in a feature branch, never touches main directly.
    The user reviews and merges PRs on GitHub.
    """
    try:
        git_env = {**os.environ, "GIT_SSH_COMMAND": PRODUCT_GIT_SSH}

        # 1. Clean state: discard leftovers, switch to main
        _product_reset_to_main()

        # 2. Update main before branching
        pull = subprocess.run(
            ["git", "pull", "origin", "main"],
            cwd=PRODUCT_REPO_DIR, capture_output=True, text=True, timeout=60,
            env=git_env,
        )
        if pull.returncode != 0:
            logger.warning(f"Product git pull failed: {pull.stderr}")
            return f"Ошибка обновления репо: {pull.stderr[:500]}"

        # 3. Run Claude Code with strict instructions + methodology
        full_prompt = (
            "IMPORTANT: Always respond in Russian (русский язык). "
            "Do not use markdown formatting.\n\n"
            "You are working in the Product web app repository.\n\n"
            "GIT RULES:\n"
            "- Create a new git branch from main: bot/<short-description>\n"
            "- Commit with a clear message in Russian\n"
            "- Push: git push origin <branch-name> (GIT_SSH_COMMAND configured)\n"
            "- NEVER merge into main, NEVER push to main\n\n"
            "METHODOLOGY (follow strictly):\n\n"
            "PHASE 1 — ANALYSIS:\n"
            "- Read CLAUDE.md for project context\n"
            "- Find and read ALL files related to the task\n"
            "- Understand the existing architecture, patterns, and conventions\n"
            "- Identify dependencies and potential impact areas\n\n"
            "PHASE 2 — PLANNING:\n"
            "- List the specific changes needed\n"
            "- Assess risks: what could break? What side effects?\n"
            "- If the task is too broad or risky, narrow the scope\n"
            "- Create the branch: git checkout -b bot/<description>\n\n"
            "PHASE 3 — IMPLEMENTATION:\n"
            "- Make changes incrementally, one file at a time\n"
            "- Follow existing code style and conventions exactly\n"
            "- Add comments only where logic is non-obvious\n\n"
            "PHASE 4 — SELF-REVIEW:\n"
            "- Re-read every changed file in full\n"
            "- Check for: typos, missing imports, broken references, type errors\n"
            "- Verify no unintended changes to other functionality\n"
            "- If the project has linting/type-checking, run it\n"
            "- Fix ALL issues found — repeat until clean\n\n"
            "PHASE 5 — COMMIT & REPORT:\n"
            "- Commit and push\n"
            "- Output: branch name, list of changed files, summary of changes\n\n"
            "TASK:\n" + prompt
        )
        result = subprocess.run(
            ["claude", "-p", "--max-turns", "100", "--allowedTools", "Bash,Read,Write,Edit,Glob,Grep,WebFetch,WebSearch"],
            input=full_prompt,
            capture_output=True,
            text=True,
            timeout=1800,  # 30 min for complex code changes
            cwd=PRODUCT_REPO_DIR,
            env=git_env,
        )

        output = result.stdout.strip() if result.stdout else ""
        stderr = result.stderr.strip() if result.stderr else ""

        # Handle max turns exhaustion
        if "Reached max turns" in (output + stderr):
            useful = output.replace("Error: Reached max turns (100)", "").strip()
            if useful:
                output = (
                    f"{useful}\n\n"
                    "⚠️ Claude Code исчерпал лимит ходов (100). "
                    "Задача оказалась слишком объёмной — попробуй разбить на части."
                )
            else:
                output = (
                    "⚠️ Claude Code исчерпал лимит ходов (100) и не успел закончить.\n"
                    "Попробуй дать более конкретную задачу:\n"
                    "— указать конкретный файл\n"
                    "— описать что именно искать/менять"
                )
        elif not output and stderr:
            output = f"Ошибка: {stderr[:2000]}"
        elif not output:
            output = "Claude Code не вернул результат."

        # 4. Check if a branch was pushed — extract branch name for PR link
        branch_check = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=PRODUCT_REPO_DIR, capture_output=True, text=True, timeout=10,
        )
        current_branch = branch_check.stdout.strip()
        if current_branch and current_branch != "main":
            pr_url = f"https://github.com/YOUR_USERNAME/YOUR_REPO/compare/main...{current_branch}"
            output += f"\n\n🔗 Создать PR: {pr_url}"

        # 5. Return to main, clean up
        _product_reset_to_main()

        return output

    except subprocess.TimeoutExpired:
        _product_reset_to_main()
        return "Таймаут — Claude Code работал дольше 30 минут. Попробуй разбить задачу на части."
    except FileNotFoundError:
        return "Claude Code не найден на сервере."
    except Exception as e:
        logger.error(f"Claude Code Product error: {e}")
        _product_reset_to_main()
        return f"Ошибка: {e}"


# ── Fireflies.ai integration ─────────────────────────────────────────────

# ── Web Search & Crawl ───────────────────────────────────────────────────

BRAVE_SEARCH_API_KEY = os.getenv("BRAVE_SEARCH_API_KEY")


def web_search(query, count=5):
    """Search the web using Brave Search API. Returns formatted results."""
    if not BRAVE_SEARCH_API_KEY:
        return "Brave Search не настроен (BRAVE_SEARCH_API_KEY отсутствует в .env)."

    try:
        resp = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers={
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": BRAVE_SEARCH_API_KEY,
            },
            params={"q": query, "count": count},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()

        results = data.get("web", {}).get("results", [])
        if not results:
            return f"По запросу '{query}' ничего не найдено."

        lines = [f"Результаты поиска: {query}\n"]
        for i, r in enumerate(results, 1):
            title = r.get("title", "")
            url = r.get("url", "")
            desc = r.get("description", "")
            lines.append(f"{i}. {title}")
            lines.append(f"   {url}")
            if desc:
                lines.append(f"   {desc}")
            lines.append("")

        return "\n".join(lines)

    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response else "?"
        logger.error(f"Brave Search HTTP error {status}: {e}")
        if status == 429:
            return "Превышен лимит запросов Brave Search. Попробуй позже."
        return f"Ошибка Brave Search (HTTP {status})."
    except Exception as e:
        logger.error(f"Web search error: {e}")
        return f"Ошибка поиска: {e}"


def crawl_page(url):
    """Crawl a web page and extract clean text via Jina Reader API."""
    try:
        resp = requests.get(
            f"https://r.jina.ai/{url}",
            headers={
                "Accept": "text/markdown",
                "X-Return-Format": "markdown",
            },
            timeout=30,
        )
        resp.raise_for_status()
        text = resp.text.strip()

        if not text:
            return f"Не удалось извлечь текст со страницы {url}."

        # Limit to ~12000 chars to fit in GPT context
        if len(text) > 12000:
            text = text[:12000] + "\n\n[...текст обрезан...]"

        return text

    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response else "?"
        logger.error(f"Crawl HTTP error {status} for {url}: {e}")
        return f"Не удалось загрузить страницу (HTTP {status})."
    except Exception as e:
        logger.error(f"Crawl error for {url}: {e}")
        return f"Ошибка загрузки страницы: {e}"


# ── Fireflies.ai integration ─────────────────────────────────────────────

FIREFLIES_API_KEY = os.getenv("FIREFLIES_API_KEY")
FIREFLIES_ENDPOINT = "https://api.fireflies.ai/graphql"


def _fireflies_headers():
    return {
        "Authorization": f"Bearer {FIREFLIES_API_KEY}",
        "Content-Type": "application/json",
    }


def _parse_fireflies_date(raw):
    """Parse Fireflies date (Unix ms timestamp or ISO string)."""
    if not raw:
        return ""
    try:
        ts = int(raw) / 1000
        return datetime.fromtimestamp(ts).strftime("%d.%m.%Y %H:%M")
    except (ValueError, TypeError, OSError):
        return str(raw)[:16]


def search_fireflies_meetings(days=7, keyword=None):
    """Search recent meetings in Fireflies. Returns formatted text."""
    if not FIREFLIES_API_KEY:
        return "Fireflies не настроен (FIREFLIES_API_KEY отсутствует)."

    from_date = (
        datetime.now(timezone.utc) - timedelta(days=days)
    ).strftime("%Y-%m-%dT%H:%M:%S.000Z")

    query = """
        query($fromDate: DateTime, $limit: Int) {
            transcripts(fromDate: $fromDate, limit: $limit) {
                id
                title
                date
                duration
                participants
                summary {
                    overview
                    action_items
                    keywords
                }
            }
        }
    """

    try:
        resp = requests.post(
            FIREFLIES_ENDPOINT,
            headers=_fireflies_headers(),
            json={"query": query, "variables": {"fromDate": from_date, "limit": 30}},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        if "errors" in data:
            return f"Ошибка Fireflies: {data['errors']}"

        transcripts = data.get("data", {}).get("transcripts", []) or []

        # Filter by keyword if provided (match ANY word from the keyword)
        if keyword and transcripts:
            words = [w.lower() for w in keyword.split() if len(w) >= 2]
            if words:
                def _matches(t):
                    haystack = " ".join([
                        (t.get("title") or ""),
                        " ".join(t.get("participants") or []),
                        (t.get("summary", {}).get("overview") or ""),
                    ]).lower()
                    return any(w in haystack for w in words)
                transcripts = [t for t in transcripts if _matches(t)]

        if not transcripts:
            period = f"за последние {days} дн." if days > 1 else "за сегодня"
            extra = f" по запросу '{keyword}'" if keyword else ""
            return f"Встреч {period}{extra} не найдено."

        lines = [f"Найдено встреч: {len(transcripts)}\n"]
        for t in transcripts:
            title = t.get("title", "Без названия")
            date_str = _parse_fireflies_date(t.get("date"))
            duration = t.get("duration", 0)
            dur_min = round(duration / 60) if duration else 0
            participants = ", ".join(t.get("participants") or [])

            lines.append(f"--- {title} ---")
            if date_str:
                lines.append(f"Дата: {date_str}")
            if dur_min:
                lines.append(f"Длительность: {dur_min} мин")
            if participants:
                lines.append(f"Участники: {participants}")

            summary = t.get("summary") or {}
            if summary.get("overview"):
                # Strip markdown formatting from Fireflies summary
                overview = summary["overview"].replace("**", "").replace("*", "")
                lines.append(f"Обзор: {overview}")
            if summary.get("action_items"):
                action_items = summary["action_items"].replace("**", "").replace("*", "")
                lines.append(f"Задачи: {action_items}")

            lines.append(f"[ID: {t.get('id', '?')}]")
            lines.append("")

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"Fireflies search error: {e}")
        return f"Ошибка при поиске встреч: {e}"


def analyze_fireflies_meeting(meeting_id, question=None):
    """Fetch a meeting transcript from Fireflies and analyze it with GPT."""
    if not FIREFLIES_API_KEY:
        return "Fireflies не настроен (FIREFLIES_API_KEY отсутствует)."

    query = """
        query($id: String!) {
            transcript(id: $id) {
                id
                title
                date
                duration
                participants
                summary {
                    overview
                    action_items
                    keywords
                }
                sentences {
                    text
                    speaker_name
                }
            }
        }
    """

    try:
        resp = requests.post(
            FIREFLIES_ENDPOINT,
            headers=_fireflies_headers(),
            json={"query": query, "variables": {"id": meeting_id}},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        if "errors" in data:
            return f"Ошибка Fireflies: {data['errors']}"

        t = data.get("data", {}).get("transcript")
        if not t:
            return "Встреча не найдена по этому ID."

        # Format transcript
        sentences = t.get("sentences") or []
        transcript_text = "\n".join(
            f"{s.get('speaker_name', '?')}: {s.get('text', '')}"
            for s in sentences
        )
        if len(transcript_text) > 15000:
            transcript_text = transcript_text[:15000] + "\n\n[...транскрипт обрезан...]"

        title = t.get("title", "Встреча")
        participants = ", ".join(t.get("participants") or [])
        summary = t.get("summary") or {}

        analysis_prompt = (
            f"Проанализируй транскрипт встречи. Ответ на русском, без markdown.\n\n"
            f"Встреча: {title}\n"
            f"Участники: {participants}\n"
            f"Fireflies обзор: {summary.get('overview', 'нет')}\n"
            f"Action items: {summary.get('action_items', 'нет')}\n\n"
            f"Полный транскрипт:\n{transcript_text}\n\n"
        )

        if question:
            analysis_prompt += f"Конкретный вопрос: {question}\n\n"

        analysis_prompt += (
            "Дай структурированный анализ:\n"
            "1. Основные темы и решения\n"
            "2. Ключевые договорённости\n"
            "3. Задачи и следующие шаги (кто, что, когда)\n"
            "4. Важные инсайты или риски\n"
            "Формат: plain text, русский язык."
        )

        client = get_openai_client()
        gpt_resp = client.chat.completions.create(
            model=MODEL_MAIN,
            max_completion_tokens=2500,
            messages=[{"role": "user", "content": analysis_prompt}],
        )

        analysis = (gpt_resp.choices[0].message.content or "").strip()
        return analysis or "Не удалось проанализировать встречу."

    except Exception as e:
        logger.error(f"Fireflies analyze error: {e}")
        return f"Ошибка при анализе встречи: {e}"
