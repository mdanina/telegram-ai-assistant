# Self-Improvement v2: Code Review + Feature Scout через Claude Code

## Проблема

Текущий `self_improve.py`:
- Использует GPT-4o в обход Claude Code
- Ищет только внешние фичи ("что нового в AI агентах") — предложения в вакууме
- Не анализирует реальный код AIOS — не знает о багах, дублировании, слабых местах
- `aios_capabilities` захардкожен строкой на 15 пунктов и отстаёт от реальности
- Результат: generic идеи типа "добавьте RAG" вместо "в brief_generator.py дублируется логика подключения к SQLite — вынести в общий модуль"

## Цель

Переписать self-improvement pipeline так, чтобы он:
1. Работал через Claude Code CLI (а не GPT напрямую)
2. Совмещал два режима: **Code Review** (анализ кода) + **Feature Scout** (поиск идей)
3. Приземлял все предложения на конкретные файлы и строки кода

## Архитектура

### Два режима, чередующихся по дням

| День    | Режим          | Что делает                                                |
|---------|----------------|-----------------------------------------------------------|
| Чётный  | Code Review    | Claude Code читает модули AIOS, находит баги и улучшения  |
| Нечётный| Feature Scout  | Brave Search + Jina + Claude Code анализирует находки      |

### Режим 1: Code Review (новый)

Claude Code CLI получает prompt для полного ревью всей кодовой базы AIOS. Каждый запуск анализирует ВСЮ систему целиком — все модули, все слои. Это возможно, потому что Claude Code сам читает файлы через Read tool и может обойти всё дерево за один вызов.

**Prompt для Code Review:**

```
Прочитай ВСЕ Python-файлы проекта AIOS:
- execution/telegram/ (bot.py, task_handler.py, slash_commands.py, skills_menu.py, email_handler.py, voice_handler.py, photo_handler.py, document_handler.py, meeting_handler.py, bot_memory.py, transcript_store.py, utils.py)
- execution/daily_brief/ (brief_generator.py, morning_digest.py)
- execution/intelligence/ (intelligence_orchestrator.py, meeting_analyzer.py, meeting_autoprocess.py, article_finder.py, self_improve.py, weekly_report.py, voice_processor.py, fireflies_client.py)
- execution/task_os/ (gtd_processor.py, reminder.py)
- execution/data_os/ (query.py, snapshot.py, db_setup.py, db_router.py + collectors/)

Проведи комплексный анализ с фокусом на ТРИ направления:

1. НАДЁЖНОСТЬ И БЕЗОПАСНОСТЬ
   - Необработанные edge cases, отсутствие retry/fallback
   - Утечки ресурсов (SQLite соединения, subprocess, память)
   - Потенциальные инъекции (SQL, prompt injection через user input)
   - Захардкоженные значения которые стоит вынести в конфиг
   - Дублирование кода между модулями

2. ФУНКЦИОНАЛЬНОСТЬ — ЧТО ДОБАВИТЬ
   - Какие возможности системы недоиспользуются или могут быть расширены
   - Какие данные уже собираются но не анализируются
   - Какие связи между модулями можно создать (например: данные из meeting_analyzer могут обогащать weekly_report)
   - Какие новые автоматизации просятся на базе существующей инфраструктуры
   - Что можно автоматизировать из того что сейчас делается вручную

3. ПОЛЬЗОВАТЕЛЬСКИЙ ОПЫТ
   - Как улучшить взаимодействие через Telegram бот (новые команды, улучшение существующих)
   - Что в текущих ответах бота можно сделать полезнее, информативнее, удобнее
   - Какие сценарии использования не покрыты (частые запросы CEO которые бот не умеет)
   - Как улучшить брифинги, отчёты, напоминания

Для КАЖДОГО предложения укажи:
- Файл(ы) и строку где менять
- Что не так / чего не хватает
- Как исправить / что добавить (конкретно)
- Категория: баг / надёжность / новая фича / UX
- Приоритет: критичный / высокий / средний / низкий

Также прочитай context/strategy.md — учитывай бизнес-стратегию при предложении фич.

Не выдумывай проблем. Приоритизируй: сначала то что ломается или мешает, потом то что добавит ценность.
Формат: plain text, без markdown.
```

### Режим 2: Feature Scout (рефакторинг текущего)

Заменить GPT-4o вызов на Claude Code CLI. Claude Code сам умеет делать WebSearch и WebFetch — не нужны отдельные вызовы Brave и Jina из Python.

**Ключевое изменение:** перед анализом внешних находок Claude Code читает реальный код AIOS, чтобы предложения были привязаны к конкретным файлам.

**Prompt для Feature Scout:**

```
1. Прочитай файлы: execution/telegram/task_handler.py, execution/daily_brief/brief_generator.py (чтобы понять текущие возможности AIOS)

2. Найди в интернете: {today_query}

3. На основе найденного предложи 2-3 улучшения для AIOS.

Для каждого предложения:
- Что: одно предложение
- Зачем: какую бизнес-проблему решает
- Где в коде: конкретный файл и что в нём менять
- Как: конкретные шаги реализации
- Сложность: легко (1 час) / средне (полдня) / сложно (день+)

ПРАВИЛА:
- Только то, чего реально нет в коде
- Привязывай к конкретным файлам и функциям
- VPS 2CPU/2GB RAM — учитывай ограничения
```

## Конкретные изменения в коде

### Файл: `execution/intelligence/self_improve.py`

**Удалить:**
- `from openai import OpenAI` и весь `_analyze_with_gpt()` — заменить на Claude Code CLI
- `OPENAI_API_KEY` зависимость — не нужна для этого модуля
- Захардкоженный `aios_capabilities` блок — Claude Code сам читает код

**Добавить:**
- `_call_claude(prompt, timeout=900)` — вызов Claude Code CLI (аналог из article_finder.py, можно вынести в общую утилиту). Таймаут увеличен до 15 минут — полный ревью кодовой базы требует больше времени
- `_get_today_mode()` — чётный/нечётный день → code_review/feature_scout
- `_run_code_review()` — формирует prompt для полного ревью, вызывает Claude Code
- `_run_feature_scout(query)` — формирует prompt с чтением кода, вызывает Claude Code

**Оставить как есть:**
- `_brave_search()` и `_crawl_page()` — удалить. Claude Code умеет WebSearch и WebFetch сам через --allowedTools
- `_send_to_telegram()` — оставить
- `_get_today_query()` — оставить для Feature Scout дней
- Логирование и cron wrapper — оставить

### Структура main():

```python
def main():
    _ensure_log_table()          # для истории предложений

    mode = _get_today_mode()     # "code_review" или "feature_scout"

    if mode == "code_review":
        targets = _get_today_review_targets()
        result = _run_code_review(targets)
    else:
        query = _get_today_query()
        result = _run_feature_scout(query)

    if result and len(result) > 100:
        header = "CODE REVIEW" if mode == "code_review" else "FEATURE SCOUT"
        text = f"{header} ({datetime.now().strftime('%d.%m.%Y')})\n\n{result}"
        asyncio.run(_send_to_telegram(text))
        _save_to_log(mode, text)
```

### Опционально: таблица истории предложений

```sql
CREATE TABLE IF NOT EXISTS self_improve_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    mode TEXT,           -- 'code_review' или 'feature_scout'
    content TEXT,
    created_at TEXT
)
```

Это позволит не повторять одни и те же предложения, и отслеживать что было принято.

## Что НЕ менять

- Cron расписание (`0 8 * * *`) — оставить
- `cron/self_improve.sh` — оставить как есть
- Telegram доставку — оставить
- `SEARCH_QUERIES` — оставить для Feature Scout дней (можно расширить)

## Общие утилиты — вынести

В процессе обнаружено дублирование вызова Claude Code CLI между модулями:

| Модуль | Функция |
|--------|---------|
| `article_finder.py` | `_call_claude()`, `_call_claude_with_stdin()` |
| `telegram/utils.py` | `run_claude_code()` |
| `self_improve.py` (после рефакторинга) | `_call_claude()` |

Рекомендация: вынести в `execution/common/claude_cli.py`:
```python
def call_claude(prompt, stdin_text=None, timeout=600, allowed_tools="Bash,Read,Write,WebFetch,WebSearch"):
    """Unified Claude Code CLI wrapper."""
```

И импортировать из всех модулей. Это отдельная задача, не блокирует текущий рефакторинг.

## Порядок реализации

1. Написать новый `self_improve.py` с двумя режимами (code_review + feature_scout)
2. Заменить GPT на Claude Code CLI
3. Протестировать оба режима: `python self_improve.py --mode code_review` и `--mode feature_scout`
4. Убедиться что Telegram доставка работает
5. Опционально: добавить таблицу self_improve_log

## Ожидаемый результат

Вместо:
> "Скаут улучшений: AI agents. Предложение 1: добавить RAG для работы с документами..."

Получаем:
> CODE REVIEW (15.03.2026)
>
> НАДЁЖНОСТЬ
> 1. [Критичный, баг] task_handler.py:833 — _recent_tasks dict растёт бесконечно, нет периодической очистки. Memory leak при долгой работе бота. Исправление: добавить max size или TTL чистку в начале каждого вызова.
> 2. [Высокий, надёжность] task_handler.py:492 — _call_gpt ловит все Exception, не различает AuthenticationError (фатальная) от RateLimitError (retry). Исправление: ловить openai.APIError для retry, остальное пробрасывать.
> 3. [Средний, надёжность] brief_generator.py:51 — SQLite cursor не закрывается при исключении. Исправление: использовать context manager или try/finally.
>
> ФУНКЦИОНАЛЬНОСТЬ
> 4. [Высокий, новая фича] meeting_autoprocess.py + weekly_report.py — action items из встреч не попадают в GTD автоматически. Сейчас meeting_analyzer извлекает action_items (строка 45), но они только логируются. Исправление: вызывать gtd_processor.py для каждого action item, привязывая к проекту из встречи.
> 5. [Средний, новая фича] data_os/collectors/ — нет алертов на аномалии. Revenue_today = 0 или skip_rate > 20% не вызывают уведомления. Исправление: добавить threshold-проверки в snapshot.py после сбора, отправлять alert в Telegram.
>
> ПОЛЬЗОВАТЕЛЬСКИЙ ОПЫТ
> 6. [Высокий, UX] task_handler.py — бот не показывает прогресс по задачам. /tasks выводит список, но нет "за эту неделю выполнено X из Y" или "просрочено Z". Исправление: добавить саммари в начало ответа /tasks.
> 7. [Средний, UX] brief_generator.py — бриф не содержит сравнения с прошлым периодом. "Выручка 150,000" ничего не значит без "vs 120,000 на прошлой неделе (+25%)". Исправление: в get_product_summary() добавить запрос метрик за предыдущий snapshot и расчёт дельты.
