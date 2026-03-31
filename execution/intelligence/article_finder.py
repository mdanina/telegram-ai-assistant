#!/usr/bin/env python3
"""
Intelligence Layer: Article Finder

Daily job that finds a new open-access article on a configured topic,
generates a detailed review via Claude Code, and sends it via Telegram.

Configure ARTICLE_TOPIC and ARTICLE_EXCLUDE below for your domain.

Pipeline:
  1. Claude Code: searches PubMed/PMC for a relevant article → returns PMCID
  2. Python: fetches full text + metadata via NCBI EFetch API
  3. Claude Code: writes narrative Russian review (full text piped via stdin)
  4. Python: validates review, sends to Telegram, saves to SQLite registry

Cron: 0 6 * * * (6:00 UTC = 9:00 Moscow)
"""

import os
import json
import subprocess
import sqlite3
import asyncio
import logging
import tempfile
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from telegram import Bot
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

BASE_DIR = os.path.join(os.path.dirname(__file__), '..', '..')
DB_FILE = os.path.join(BASE_DIR, 'data', 'aios_data.db')
ARTICLES_DIR = os.path.join(BASE_DIR, 'data', 'articles')
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_TARGET_USER_ID = os.getenv("TELEGRAM_ALLOWED_USER_IDS", "").split(",")[0]

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

NCBI_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

# ── Customize these for your domain ──────────────────────────────────
# Search terms for PubMed (English, used in API query)
ARTICLE_SEARCH_TERMS = os.getenv(
    "ARTICLE_SEARCH_TERMS",
    "(artificial+intelligence+OR+machine+learning)+AND+(your+topic+here)+AND+%22open+access%22[filter]"
)
# Topic description for Claude prompts (Russian or your language)
ARTICLE_TOPIC = os.getenv("ARTICLE_TOPIC", "применения ИИ в вашей области")
# Topics to exclude (Russian or your language)
ARTICLE_EXCLUDE = os.getenv("ARTICLE_EXCLUDE", "нерелевантные темы")
# Target audience for the review
ARTICLE_AUDIENCE = os.getenv("ARTICLE_AUDIENCE", "профессионалов вашей отрасли")


# ── Database ──────────────────────────────────────────────────────────

def _ensure_table():
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS article_registry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pmid TEXT,
            pmcid TEXT UNIQUE,
            title TEXT,
            authors TEXT,
            journal TEXT,
            pub_date TEXT,
            doi TEXT,
            url TEXT,
            review_text TEXT,
            pdf_path TEXT,
            sent_at TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def _get_processed_ids():
    """Returns set of already-processed PMCIDs (including failed ones)."""
    conn = sqlite3.connect(DB_FILE)
    rows = conn.execute("SELECT pmcid FROM article_registry").fetchall()
    conn.close()
    return {r[0] for r in rows if r[0]}


def _save_failed_to_registry(pmcid, reason="full text unavailable"):
    """Save a failed PMCID so it won't be selected again."""
    conn = sqlite3.connect(DB_FILE)
    conn.execute(
        """INSERT OR IGNORE INTO article_registry
           (pmid, pmcid, title, authors, journal, pub_date, doi, url, review_text, pdf_path, sent_at, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (None, pmcid, None, None, None, None, None, None,
         f"FAILED: {reason}", None, None, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()
    log.info("Saved %s to registry as failed (%s)", pmcid, reason)


def _save_to_registry(data):
    conn = sqlite3.connect(DB_FILE)
    conn.execute(
        """INSERT OR IGNORE INTO article_registry
           (pmid, pmcid, title, authors, journal, pub_date, doi, url, review_text, pdf_path, sent_at, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            data.get("pmid"),
            data.get("pmcid"),
            data.get("title"),
            data.get("authors"),
            data.get("journal"),
            data.get("pub_date"),
            data.get("doi"),
            data.get("url"),
            data.get("review_text"),
            data.get("pdf_path"),
            data.get("sent_at"),
            datetime.now().isoformat(),
        ),
    )
    conn.commit()
    conn.close()


# ── Claude Code calls ────────────────────────────────────────────────

    # NOTE: PubMed MCP tools are NOT available on the server.
    # Claude uses Bash (curl/python) to query NCBI ESearch API instead.


def _call_claude(prompt, timeout=600):
    """Call Claude Code CLI and return stdout."""
    try:
        cmd = ["claude", "--allowedTools", "Bash,Read,Write,WebFetch", "-p", prompt]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=BASE_DIR,
            env={**os.environ},
        )
        output = result.stdout.strip()
        if not output:
            log.error("Claude returned empty output. stderr: %s", result.stderr[:500])
            return None
        return output
    except subprocess.TimeoutExpired:
        log.error("Claude timed out (%ds)", timeout)
        return None
    except FileNotFoundError:
        log.error("Claude Code CLI not found")
        return None
    except Exception as e:
        log.error("Claude error: %s", e)
        return None


def _call_claude_with_stdin(prompt, stdin_text, timeout=600):
    """Call Claude Code CLI, piping text via stdin to avoid CLI arg length limits."""
    try:
        result = subprocess.run(
            ["claude", "--allowedTools", "Bash,Read,Write,WebFetch", "-p", prompt],
            input=stdin_text,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=BASE_DIR,
            env={**os.environ},
        )
        output = result.stdout.strip()
        if not output:
            log.error("Claude returned empty output. stderr: %s", result.stderr[:500])
            return None
        return output
    except subprocess.TimeoutExpired:
        log.error("Claude timed out (%ds)", timeout)
        return None
    except Exception as e:
        log.error("Claude with stdin error: %s", e)
        return None


def _claude_search(processed_pmcids):
    """Ask Claude to search for a new article. Returns PMCID or None."""
    processed_list = ", ".join(sorted(processed_pmcids)) if processed_pmcids else "(пока нет)"

    prompt = f"""Найди одну НОВУЮ научную статью на PubMed Central на тему {ARTICLE_TOPIC}.

Используй Bash с curl для запросов к NCBI ESearch API:
curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pmc&term={ARTICLE_SEARCH_TERMS}&retmax=20&sort=date&retmode=json&mindate=2025/01/01&maxdate=2026/12/31"

Требования:
- Свежая (за последние 60 дней)
- НАПРЯМУЮ по теме: {ARTICLE_TOPIC}
- НЕ подходят: {ARTICLE_EXCLUDE}
- Полный текст доступен бесплатно (open access, PubMed Central)
- НЕ из списка уже обработанных PMCIDs: {processed_list}

Для каждой найденной статьи получи заголовок через:
curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pmc&id=NUMERIC_ID&retmode=json"

Ответь СТРОГО в формате JSON (и НИЧЕГО больше):
{{"pmcid": "PMC...", "title": "..."}}

Если подходящей статьи нет, ответь: {{"pmcid": null, "title": null}}"""

    output = _call_claude(prompt, timeout=600)
    if not output:
        return None

    # Parse JSON from Claude's response
    try:
        # Find JSON in the output
        start = output.index("{")
        end = output.rindex("}") + 1
        data = json.loads(output[start:end])
        pmcid = data.get("pmcid")
        if pmcid and pmcid.startswith("PMC"):
            log.info("Claude found: %s — %s", pmcid, data.get("title", "?")[:80])
            return pmcid
    except (ValueError, json.JSONDecodeError) as e:
        log.warning("Failed to parse Claude search response: %s", e)
        log.warning("Raw output: %s", output[:500])

    return None


def _claude_write_review(full_text, meta):
    """Ask Claude to write a narrative review. Full text piped via stdin."""
    title = meta.get("title", "")
    authors = meta.get("authors", "")
    journal = meta.get("journal", "")
    doi = meta.get("doi", "")
    pub_date = meta.get("pub_date", "")

    prompt = f"""Ты — автор профессионального Telegram-канала для {ARTICLE_AUDIENCE}.

Через stdin передан полный текст научной статьи. Напиши по ней подробный обзор на русском языке (3000–4000 символов).

Данные статьи:
- Название: {title}
- Авторы: {authors}
- Журнал: {journal}
- Дата: {pub_date}
- DOI: {doi}

СТИЛЬ — живой, нарративный, вдумчивый. НЕ формальный академический обзор с заголовками "Цель", "Методология", "Результаты". Связный текст, который читается как увлекательный рассказ об исследовании. Как пост для коллег-профессионалов.

ПРИНЦИПЫ СТИЛЯ:
- Начни с контекста: почему эта тема важна, какую проблему решают авторы
- Веди читателя через логику статьи: от постановки вопроса → через метод → к находкам → к значению
- Используй естественные переходы между мыслями, не используй шаблонные фразы
- Добавляй собственную профессиональную оценку: что убедительно, что вызывает вопросы
- Не пересказывай сухо — интерпретируй для практика
- Используй "мы" где уместно (как профессиональное сообщество)
- НЕ используй эмодзи, маркдаун, заголовки — только чистый текст абзацами
- НЕ начинай с "Обзор статьи" — сразу погружай в текст

В КОНЦЕ обзора добавь блок источника через пустую строку:
Источник:
{authors} ({pub_date[:4] if pub_date else ''}). {title}. {journal}.
https://doi.org/{doi}

ВАЖНО: Выведи ТОЛЬКО текст обзора. Никаких комментариев, пояснений, вопросов — только готовый текст для публикации."""

    return _call_claude_with_stdin(prompt, full_text, timeout=600)


def _claude_validate_terminology(review):
    """Ask Claude to check and fix professional terminology in the review."""
    prompt = f"""Ты — редактор-терминолог, эксперт по профессиональной терминологии в области, связанной с {ARTICLE_TOPIC}.

Через stdin передан текст обзора научной статьи на русском языке. Твоя задача:

1. Найди ВСЕ профессиональные термины (названия методов, шкал, конструктов, технологий)
2. Проверь, что каждый термин переведён в соответствии с УСТОЯВШЕЙСЯ русскоязычной профессиональной традицией
3. Исправь неточные переводы

ПРАВИЛА:
- Используй термины, принятые в профессиональной литературе
- Если устоявшегося перевода нет — оставь английский термин в скобках
- НЕ меняй стиль, структуру или содержание текста — только терминологию
- Если все термины корректны — верни текст без изменений

Выведи ТОЛЬКО исправленный текст обзора целиком. БЕЗ преамбул вроде "Текст проверен", "Возвращаю без изменений" и т.п. Начни сразу с текста обзора."""

    output = _call_claude_with_stdin(prompt, review, timeout=300)
    if not output:
        return None

    # Strip preamble: if Claude added commentary before "---" or before the review
    lines = output.split("\n")
    # Remove leading lines that look like Claude's commentary (short meta-lines)
    skip_markers = [
        "текст проверен", "возвращаю без изменений", "все термины",
        "исправленный текст", "корректн", "без изменений",
    ]
    clean_lines = []
    skipping = True
    for line in lines:
        stripped = line.strip().lower()
        if skipping:
            if stripped == "---" or stripped == "":
                continue
            if any(m in stripped for m in skip_markers):
                continue
            skipping = False
        clean_lines.append(line)

    return "\n".join(clean_lines).strip()


def _claude_generate_title(review):
    """Ask Claude to generate a short catchy title for the post."""
    prompt = f"""Ты — автор профессионального Telegram-канала для {ARTICLE_AUDIENCE}.

Через stdin передан текст обзора научной статьи. Придумай короткий, цепляющий заголовок для этого поста.

ТРЕБОВАНИЯ:
- 5–12 слов максимум
- Живой, интригующий — чтобы хотелось прочитать
- НЕ сухой академический стиль
- НЕ используй эмодзи, кавычки, маркдаун
- НЕ начинай с "Обзор:", "Статья:" и т.п.

Выведи ТОЛЬКО заголовок — одну строку, ничего больше."""

    output = _call_claude_with_stdin(prompt, review, timeout=120)
    if not output:
        return None
    # Take only the first non-empty line
    for line in output.strip().split("\n"):
        line = line.strip()
        if line:
            return line
    return None


# ── NCBI full text fetch ─────────────────────────────────────────────

def _fetch_full_text(pmcid):
    """Fetch full article text + metadata from PMC via EFetch. Returns (text, meta)."""
    numeric_id = pmcid.replace("PMC", "")
    params = {"db": "pmc", "id": numeric_id, "rettype": "xml", "retmode": "xml"}
    try:
        resp = requests.get(f"{NCBI_BASE}/efetch.fcgi", params=params, timeout=60)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
    except Exception as e:
        log.error("EFetch failed for %s: %s", pmcid, e)
        return None, {}

    article = root.find(".//article")
    if article is None:
        return None, {}

    # ── Metadata ──
    meta = {"pmcid": pmcid}
    pmid_el = article.find(".//article-id[@pub-id-type='pmid']")
    if pmid_el is not None and pmid_el.text:
        meta["pmid"] = pmid_el.text
    doi_el = article.find(".//article-id[@pub-id-type='doi']")
    if doi_el is not None and doi_el.text:
        meta["doi"] = doi_el.text
        meta["url"] = f"https://doi.org/{doi_el.text}"
    title_el = article.find(".//article-title")
    if title_el is not None:
        meta["title"] = "".join(title_el.itertext())
    journal_el = article.find(".//journal-title")
    if journal_el is not None and journal_el.text:
        meta["journal"] = journal_el.text

    # Authors
    authors = []
    for contrib in article.findall(".//contrib[@contrib-type='author']"):
        surname = contrib.findtext("name/surname", "")
        given = contrib.findtext("name/given-names", "")
        if surname:
            authors.append(f"{surname} {given}".strip())
    meta["authors"] = ", ".join(authors[:6])
    if len(authors) > 6:
        meta["authors"] += " et al."

    # Pub date
    pub_date_el = article.find(".//pub-date[@pub-type='epub']")
    if pub_date_el is None:
        pub_date_el = article.find(".//pub-date")
    if pub_date_el is not None:
        y = pub_date_el.findtext("year", "")
        m = pub_date_el.findtext("month", "01")
        d = pub_date_el.findtext("day", "01")
        if y:
            meta["pub_date"] = f"{y}-{m.zfill(2)}-{d.zfill(2)}"

    # ── Full text — all <p> from <body> ──
    body = article.find(".//body")
    if body is None:
        return None, meta
    paragraphs = []
    for p in body.findall(".//p"):
        text = "".join(p.itertext()).strip()
        if text:
            paragraphs.append(text)

    full_text = "\n\n".join(paragraphs)
    return full_text, meta


# ── PDF download ──────────────────────────────────────────────────────

def download_pdf(pmcid):
    """Try to download PDF from PMC. Returns file path or None."""
    if not pmcid:
        return None
    os.makedirs(ARTICLES_DIR, exist_ok=True)
    pdf_path = os.path.join(ARTICLES_DIR, f"{pmcid}.pdf")

    oa_url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id={pmcid}"
    try:
        resp = requests.get(oa_url, timeout=30)
        root = ET.fromstring(resp.content)
        for link in root.findall(".//link"):
            if link.get("format") == "pdf":
                pdf_url = link.get("href", "")
                if pdf_url.startswith("ftp://"):
                    pdf_url = pdf_url.replace("ftp://", "https://")
                if pdf_url:
                    pdf_resp = requests.get(pdf_url, timeout=60)
                    pdf_resp.raise_for_status()
                    with open(pdf_path, "wb") as f:
                        f.write(pdf_resp.content)
                    log.info("PDF downloaded: %s", pdf_path)
                    return pdf_path
    except Exception as e:
        log.warning("PDF download failed for %s: %s", pmcid, e)

    return None


# ── Telegram ──────────────────────────────────────────────────────────

async def send_to_telegram(text):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    for i in range(0, len(text), 4096):
        await bot.send_message(chat_id=TELEGRAM_TARGET_USER_ID, text=text[i:i + 4096])


# ── Validation ────────────────────────────────────────────────────────

def _is_valid_review(text):
    """Check that Claude's output is an actual review, not an error message."""
    if not text or len(text) < 500:
        return False
    error_markers = [
        "не удалось", "не могу", "нужно разрешение", "предоставь полный текст",
        "нет доступа", "Проблема:", "I can't", "I don't have",
        "permission", "access denied", "unable to",
    ]
    first_500 = text[:500].lower()
    for marker in error_markers:
        if marker.lower() in first_500:
            log.warning("Review looks like an error (contains '%s')", marker)
            return False
    return True


# ── Main pipeline ─────────────────────────────────────────────────────

MAX_SEARCH_ATTEMPTS = 3


def main():
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_TARGET_USER_ID:
        log.error("Telegram credentials not set.")
        return

    _ensure_table()

    # 1. Get already-processed articles
    processed_pmcids = _get_processed_ids()
    log.info("Already processed: %d articles", len(processed_pmcids))

    # 2–3. Search + fetch with retry: if full text unavailable, blacklist and retry
    full_text = None
    meta = {}
    chosen_pmcid = None

    for attempt in range(1, MAX_SEARCH_ATTEMPTS + 1):
        log.info("Search attempt %d/%d...", attempt, MAX_SEARCH_ATTEMPTS)

        chosen_pmcid = _claude_search(processed_pmcids)
        if not chosen_pmcid:
            log.info("No suitable article found today.")
            return

        log.info("Claude chose: %s", chosen_pmcid)

        # Fetch full text
        log.info("Fetching full text for %s...", chosen_pmcid)
        full_text, meta = _fetch_full_text(chosen_pmcid)

        if full_text and len(full_text) >= 500:
            log.info("Full text: %d chars. Title: %s", len(full_text), meta.get("title", "?")[:80])
            break

        # Full text unavailable — blacklist this PMCID and retry
        chars = len(full_text) if full_text else 0
        log.warning("Full text too short or unavailable for %s (%d chars). Blacklisting.", chosen_pmcid, chars)
        _save_failed_to_registry(chosen_pmcid, f"full text unavailable ({chars} chars)")
        processed_pmcids.add(chosen_pmcid)
        full_text = None
        chosen_pmcid = None

    if not full_text or not chosen_pmcid:
        log.error("Failed to find an article with available full text after %d attempts.", MAX_SEARCH_ATTEMPTS)
        return

    # 4. Claude writes the review (full text piped via stdin — no truncation)
    log.info("Asking Claude to write review...")
    review = _claude_write_review(full_text, meta)

    if not review:
        log.error("Claude returned no review.")
        return

    # 5. Validate — don't send error messages as reviews
    if not _is_valid_review(review):
        log.error("Review failed validation — likely an error, not sending.")
        log.error("First 300 chars: %s", review[:300])
        return

    # 6. Validate terminology — fix professional terms
    log.info("Validating terminology...")
    validated = _claude_validate_terminology(review)
    if validated and _is_valid_review(validated):
        review = validated
        log.info("Terminology validated. Review length: %d chars", len(review))
    else:
        log.warning("Terminology validation failed, using original review.")

    log.info("Review length: %d chars", len(review))

    # 7. Generate title
    log.info("Generating title...")
    title = _claude_generate_title(review)
    if title:
        review = f"{title}\n\n{review}"
        log.info("Title: %s", title)
    else:
        log.warning("Title generation failed, sending without title.")

    # 8. Download PDF (optional)
    pdf_path = download_pdf(chosen_pmcid)

    # 9. Send to Telegram
    log.info("Sending to Telegram...")
    asyncio.run(send_to_telegram(review))

    # 10. Save to registry
    meta["review_text"] = review
    meta["pdf_path"] = pdf_path
    meta["sent_at"] = datetime.now().isoformat()
    _save_to_registry(meta)
    log.info("Done! Article %s processed and sent.", chosen_pmcid)


if __name__ == "__main__":
    main()
