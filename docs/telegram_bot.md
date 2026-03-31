# AIOS Telegram Bot — Документация

## Обзор

Telegram-бот — основной интерфейс AIOS. Пользователь общается с ботом текстом, голосом, фото или файлами. GPT-5.4 с function calling маршрутизирует сообщения: задачи → GTD, вопросы → ИИ-ответ, данные → запрос к БД, почта → нативный IMAP/SMTP, скиллы → Claude Code.

## Архитектура

```
Telegram → bot.py (роутер)
              ├── task_handler.py    ← текст → GPT-5.4 (function calling) → действие
              ├── slash_commands.py  ← /brief, /query, /tasks, /files, /cc, /newchat
              ├── skills_menu.py    ← /skills → inline-кнопки
              ├── email_handler.py  ← Яндекс Почта (IMAP/SMTP)
              ├── voice_handler.py  ← голос → Whisper (ru) → текст → GPT-5.4
              ├── photo_handler.py  ← фото → GPT-4o Vision
              ├── document_handler.py ← файлы → inbox / транскрипт
              └── meeting_handler.py  ← аудио/видео → Fireflies
```

## Модули

### bot.py — точка входа
Регистрирует обработчики в порядке приоритета:
1. `/start` → приветствие
2. `/skills` → меню кнопок (skills_menu.py)
3. `CallbackQueryHandler` → нажатия кнопок (patterns: `^skill:`, `^email:`, `^task:`, проверка user whitelist)
4. Остальные команды → slash_commands.py
5. Голос, аудио, видео, фото, документы → соответствующие хендлеры
6. Текст → task_handler.py (основной ИИ)

Безопасность: `filters.User(user_id=ALLOWED_USER_IDS)` на всех хендлерах + отдельная проверка в `handle_skill_callback`.

### task_handler.py — мозг бота
GPT-5.4 с OpenAI Function Calling. Бот отправляет сообщение + описание доступных функций, GPT решает какую вызвать:

**Доступные функции (tools):**
| Функция | Описание |
|---------|----------|
| `create_task` | Создать задачу в GTD (когда пользователь просит добавить/сохранить/запланировать) |
| `generate_brief` | Сгенерировать ежедневный брифинг |
| `query_data` | Запрос бизнес-данных (MRR, метрики и т.д.) |
| `send_files` | Отправить файлы из data/outbox/ |
| `run_claude_code` | Делегировать Claude Code (календарь, файлы) |

**Создание задач:**
- GPT-5.4 решает, когда вызвать `create_task`, но текст задачи всегда берётся из оригинального сообщения пользователя (`raw_user_text`), а не из аргументов GPT. Причина: GPT иногда галлюцинирует совершенно другой текст задачи (напр. пользователь пишет о коучинге, а GPT создаёт задачу про календарь из предыдущего контекста).
- GTD-процессор (`gtd_processor.py`) сам разбирает оригинальный текст.

**Дедупликация (два уровня):**
1. **В рамках одного ответа:** GPT-5.4 иногда возвращает несколько одинаковых tool_calls (напр. два `create_task`). Бот отслеживает вызванные функции через `seen_tools` и пропускает дубли.
2. **Между сообщениями:** если пользователь отправляет одно и то же дважды (напр. отправил + пересылка), MD5-хэш текста задачи проверяется в `_recent_tasks` с окном 60 секунд.

Если GPT не вызывает функцию — это обычный чат-ответ.

**Контекст для GPT-5.4:**
- Бизнес-контекст из `context/*.md` (кэш в памяти, TTL 1 час)
- История диалога (30 сообщений, SQLite)
- Долгосрочная память о пользователе
- Контекст последнего файла (если пользователь только что отправил документ)

**Retry-логика:**
- 3 попытки с экспоненциальным backoff на 429/502/503/504/timeout
- Если GPT возвращает пустой ответ с tools — повторный запрос без tools

**OpenAI-клиент:** singleton (один экземпляр на всё время жизни бота).

После каждого обмена GPT извлекает факты для долгосрочной памяти (фоново, через `run_in_executor`, модель `gpt-4o-mini`).

### slash_commands.py — быстрые команды
| Команда | Действие |
|---------|----------|
| `/brief` | Генерирует ежедневный брифинг |
| `/query <вопрос>` | Запрос данных на естественном языке |
| `/tasks` | Список задач с группировкой по срокам |
| `/files` | Отправляет файлы из data/outbox/ |
| `/cc <запрос>` | Передаёт запрос в Claude Code CLI |
| `/skills` | Меню быстрых действий (кнопки) |
| `/newchat` | Очистить контекст беседы |

`/brief`, `/cc`, `/query` выполняются неблокирующе (`run_in_executor`) с typing-индикатором. Результаты сохраняются в историю диалога (первые 2000 символов), чтобы GPT знал контекст предыдущих команд.

### skills_menu.py — кнопки скиллов
Команда `/skills` показывает inline-клавиатуру (6 кнопок, 3 ряда):

```
[ 📧 Почта ] [ 📩 Читать ]
[ ✉️ Письмо ] [ 📊 Брифинг ]
[ 📋 Задачи ] [ 📄 Документ ]
```

**Один тап (выполняются сразу):**
| Кнопка | Действие | Реализация |
|--------|----------|------------|
| 📧 Почта | Список непрочитанных писем (до 10) | Нативный IMAP (email_handler.py) |
| 📊 Брифинг | Запускает brief_generator.py | Напрямую, без Claude Code |
| 📋 Задачи | Показывает список задач из SQLite + кнопки ✅ | SQL-запрос, группировка по срокам, отметка выполненных |

**Два шага (бот спрашивает детали):**
| Кнопка | Вопрос бота | Реализация |
|--------|------------|------------|
| 📩 Читать | Какое письмо прочитать? (номер) | Нативный IMAP (email_handler.py) |
| ✉️ Письмо | Кому и о чём? (адрес, тема, текст) | Нативный SMTP + подтверждение |
| 📄 Документ | Что создать? | Claude Code (file-factory) |

**Действия после прочтения письма:** после отображения письма бот показывает inline-кнопки:
```
[ ↩️ Ответить ] [ ✅ Прочитано ] [ 📝 Саммари ]
```
- **↩️ Ответить** — бот спрашивает текст ответа, отправляет reply с цитатой оригинала
- **✅ Прочитано** — помечает письмо прочитанным в IMAP (флаг `\Seen` через UID STORE)
- **📝 Саммари** — GPT-5 генерирует краткое содержание (3-5 предложений на русском)

Метаданные письма (from, subject, body, msg_uid) сохраняются в `context.user_data["last_read_email"]` для follow-up действий.

**Подтверждение отправки писем:** бот показывает превью (кому, тема, текст) и спрашивает «Отправить? (да/нет)». Используется трёхступенчатый флоу:
1. `pending_skill = "mail_send"` → ввод адреса/темы/текста
2. `pending_skill = "mail_send_confirm"` + `pending_email = {...}` → превью + да/нет
3. При «да» → отправка через SMTP, при «нет» → отмена

Двухшаговый флоу использует `context.user_data["pending_skill"]` для состояния. Специальные ключи (`mail_send_confirm`, `email_reply`) обрабатываются ДО проверки SKILLS dict.

**Отметка задач как выполненных:** после списка задач бот показывает кнопки `✅ 1`, `✅ 2`, ... (до 10). Нажатие → `UPDATE tasks SET status='done' WHERE id=?`. После отметки бот обновляет список и показывает новые кнопки. Обработчик: `handle_task_action_callback` (pattern `^task:`).

Безопасность: `handle_skill_callback`, `handle_email_action_callback` и `handle_task_action_callback` проверяют `ALLOWED_USER_IDS` перед выполнением.

### email_handler.py — Яндекс Почта (IMAP/SMTP)
Нативная интеграция с Яндекс Почтой без зависимости от Claude Code. Используется пароль приложения (не основной пароль аккаунта).

**Подключение:**
- IMAP: `imap.yandex.ru:993` (SSL) — чтение
- SMTP: `smtp.yandex.ru:465` (SSL) — отправка

**Публичный API:**
| Функция | Описание |
|---------|----------|
| `check_inbox(count, unread_only)` | Список непрочитанных: отправитель, тема, дата |
| `read_email(index)` | Полный текст N-го непрочитанного письма (обёртка) |
| `read_email_full(index)` | Чтение с метаданными (from, subject, body, msg_uid) для follow-up |
| `mark_as_read(msg_uid)` | Пометить письмо как прочитанное (IMAP UID STORE +FLAGS \Seen) |
| `reply_to_email(to, subject, body, original_body)` | Ответ на письмо с цитатой оригинала (Re: + quote) |
| `summarize_email(body, subject, from_name)` | AI-саммари письма через GPT-5 (3-5 предложений, русский) |
| `send_email(to, subject, body)` | Отправка через SMTP |

**Особенности:**
- `BODY.PEEK[]` — не помечает прочитанным при чтении
- Декодирование заголовков (RFC 2047) для кириллицы
- Извлечение plain text из MIME (fallback на HTML → strip tags)
- Обрезка тела письма до 3000 символов для Telegram (полный текст хранится для саммари/ответа)
- Дата: «14:30» (сегодня), «вчера 14:30», «07.03» (старше)
- IMAP UID для mark-as-read (получается при чтении, используется через UID STORE)

### utils.py — общие утилиты
`run_claude_code(prompt)` — вызывает `claude -p "prompt"` как subprocess. Таймаут 120 сек. Автоматически добавляет инструкцию отвечать по-русски.

### voice_handler.py — голосовые сообщения
Голос → скачивание .ogg → Whisper API (whisper-1, `language="ru"`) → транскрипция → GPT-5.4 обрабатывает как текст. Временный файл удаляется после транскрипции.

### photo_handler.py — фото
Фото → скачивание в data/inbox/ → GPT-4o Vision (OCR + описание + задачи). Если есть подпись — результат анализа идёт в GPT-5.4 для ответа.

### document_handler.py — документы
Документы → data/inbox/. Маршрутизация:
1. **Аудио/видео** → meeting_handler (Fireflies)
2. **Текст с ключевыми словами транскрипта** → transcript_store → ежедневный бриф
3. **Подпись с действием** (перевести, проанализировать, резюмировать, извлечь, прочитать, обработать) → Claude Code обрабатывает файл напрямую
4. **Обычный файл** → сохраняется, бот подтверждает

Контекст файлов: после загрузки файл записывается в `context.user_data["last_file"]` и в историю диалога. Если следующее текстовое сообщение ссылается на файл — GPT-5.4 получает контекст (имя, путь, размер).

### meeting_handler.py — записи встреч
Аудио/видео → загрузка в Fireflies.ai (GraphQL API) → асинхронная транскрипция → попадает в ежедневный бриф.

### bot_memory.py — память бота
SQLite (`data/aios_data.db`), две таблицы:
- `conversation_history` — история диалога (макс. 30 для GPT, 200 хранится)
- `bot_memories` — долгосрочные факты (макс. 20 для промпта)

### transcript_store.py — хранилище транскриптов
JSON-файлы в `data/intelligence_reports/transcripts/`. Ключевые слова: транскрипт, расшифровка, протокол, встреча, созвон. Транскрипты включаются в ежедневный бриф.

## Task OS

### gtd_processor.py — создание задач
GPT-5.4 разбирает сырой текст задачи по методологии GTD:
- `next_action` — конкретное следующее действие
- `project` — проект (если часть большего результата)
- `context` — где делать (@computer, @phone, @office)
- `delegated_to` — кому делегировать
- `due_date` — дата/время (YYYY-MM-DD или YYYY-MM-DD HH:MM)
- `is_someday_maybe` — отложить на потом

Задачи сохраняются в SQLite таблицу `tasks`.

### reminder.py — система напоминаний
Cron каждые 15 минут. Многоступенчатые напоминания:
- **Задачи с датой и временем:** напоминания за 24ч, 3ч, 1ч до срока
- **Задачи только с датой:** одно напоминание в день срока
- **Просроченные:** одно напоминание при обнаружении

После финального напоминания (1ч или дата) статус → `reminded`. Отправка в Telegram через Bot API.

## Директории данных

| Путь | Назначение |
|------|-----------|
| `data/voice_notes/` | Временные .ogg (удаляются после транскрипции) |
| `data/inbox/` | Фото, документы от пользователя |
| `data/outbox/` | Файлы для отправки (отправляются и удаляются) |
| `data/intelligence_reports/transcripts/` | JSON-транскрипты для брифинга |
| `data/aios_data.db` | SQLite — история, память, задачи |

## Data OS — сбор метрик

### Коллекторы (`execution/data_os/collectors/`)

| Коллектор | Источник | Метрики |
|-----------|---------|---------|
| `youtube_collector.py` | YouTube Data API v3 | Подписчики, просмотры, кол-во видео |
| `google_analytics_collector.py` | GA4 Data API | Активные пользователи, новые, доход |
| `sheets_collector.py` | Google Sheets API | Кастомные метрики из таблиц |
| `product_collector.py` | Supabase (PostgREST) | 30+ product metrics (users, funnel, revenue, diagnostics, specialists, retention, packages) |
| `yandex_metrika_collector.py` | Яндекс Метрика API | Визиты, просмотры, посетители, отказы, ср. время, источники трафика (вчера + 30 дней) |

Оркестратор: `snapshot.py` запускает все коллекторы последовательно, данные записываются в `data/aios_data.db` таблицу `metrics` с `snapshot_id` и датой. Cron: `0 6 * * *` (6:00 UTC = 9:00 МСК).

**Динамика:** каждый запуск создаёт новый снимок. Все исторические данные хранятся — можно анализировать тренды, сравнивать периоды.

### Article Finder (`execution/intelligence/article_finder.py`)

Ежедневный автоматический поиск и обзор статей по вашей тематике.

**Пайплайн:**
1. Claude Code ищет новую статью на PubMed Central (через MCP PubMed tools)
2. Python скачивает полный текст + метаданные через NCBI EFetch API
3. Claude Code пишет нарративный обзор на русском (3000-4000 символов)
4. Claude Code проверяет и исправляет профессиональную терминологию
5. Claude Code генерирует заголовок
6. PDF скачивается в `data/articles/`
7. Обзор отправляется в Telegram
8. Метаданные сохраняются в `article_registry` (SQLite)

**Фильтрация:** исключает уже обработанные статьи (по PMCID), статьи не по теме (настраивается через переменные окружения).

Cron: `0 6 * * *` (6:00 UTC = 9:00 МСК).

### Яндекс Метрика — получение токена

1. Зайти на https://oauth.yandex.com/client/new/ (**не** `/client/new/id/` — там нет скоупов Метрики)
2. Создать приложение → платформа «Веб-сервисы» → Redirect URI: `https://oauth.yandex.com/verification_code`
3. Доступы → Яндекс Метрика → `metrika:read`
4. Создать → получить `client_id`
5. Открыть: `https://oauth.yandex.com/authorize?response_type=token&client_id=CLIENT_ID`
6. Авторизоваться → токен на странице

## Внешние сервисы

| Сервис | Модель/API | Где используется |
|--------|-----------|-----------------|
| OpenAI | GPT-5.4 | task_handler (чат, function calling, задачи), gtd_processor, brief_generator |
| OpenAI | GPT-4o | photo_handler (Vision/OCR) |
| OpenAI | GPT-4o-mini | task_handler (извлечение памяти) |
| OpenAI | Whisper-1 | voice_handler (транскрипция голоса, language=ru) |
| Яндекс Почта | IMAP/SMTP | email_handler (чтение, отправка писем) |
| Яндекс Метрика | REST API | yandex_metrika_collector (веб-аналитика) |
| Claude Code CLI | claude -p | utils.py → skills_menu, slash_commands, task_handler, article_finder |
| Fireflies.ai | GraphQL API | meeting_handler (транскрипция встреч) |
| NCBI E-utilities | ESearch/EFetch | article_finder (PubMed Central) |
| Telegram Bot API | — | Все модули |

## Переменные окружения

| Переменная | Описание |
|-----------|----------|
| `TELEGRAM_BOT_TOKEN` | Токен бота |
| `TELEGRAM_ALLOWED_USER_IDS` | ID разрешённых пользователей (через запятую) |
| `OPENAI_API_KEY` | Ключ OpenAI |
| `YANDEX_EMAIL` | Адрес Яндекс Почты (напр. user@yandex.ru) |
| `YANDEX_APP_PASSWORD` | Пароль приложения Яндекс (не основной пароль!) |
| `FIREFLIES_API_KEY` | Ключ Fireflies.ai (опционально) |

## Интеграции

### Яндекс Почта (нативная, без Claude Code)
Почта работает через нативный IMAP/SMTP (`email_handler.py`). Пароль приложения хранится в `.env` на сервере.

Чтобы получить пароль приложения: Яндекс ID → Безопасность → Пароли приложений → Создать пароль для «Почта».

Пароль приложения **не даёт доступа** к аккаунту Яндекс (только IMAP/SMTP). Основной пароль не используется.

### Telegram-чаты (пересылка)
Бот не читает групповые чаты напрямую. Для передачи информации из рабочих чатов — пересылать сообщения боту. Пересланные сообщения обрабатываются как обычные текстовые (GPT-5.4 анализирует контент, может создать задачу или ответить).

### Claude Code (делегирование)
GPT-5.4 автоматически определяет, когда пользователю нужен скилл (календарь, файлы, обработка документов), и вызывает функцию `run_claude_code` с промптом на английском. Claude Code выполняет через MCP-серверы (Google Calendar, file-factory).

Обработка файлов: если пользователь отправляет документ с подписью-действием (перевести, проанализировать и т.д.), document_handler напрямую делегирует Claude Code. Если пользователь отправляет файл без подписи, а потом просит что-то сделать — GPT-5.4 получает контекст файла и формирует cc_prompt с путём к файлу.

Ручной вариант: `/cc <запрос>` — напрямую в Claude Code.

---

## Установка с нуля

Пошаговая инструкция для развёртывания AIOS Telegram-бота на чистом VPS (Ubuntu 22.04/24.04).

### 1. Подготовка сервера

```bash
# Обновить систему
sudo apt update && sudo apt upgrade -y

# Установить Python 3.11+ и git
sudo apt install -y python3 python3-venv python3-pip git

# Создать директорию проекта
sudo mkdir -p /opt/aios
sudo chown $USER:$USER /opt/aios
```

### 2. Клонирование репозитория

```bash
cd /opt/aios

# Вариант A: через HTTPS (потребуется токен)
git clone https://github.com/<your-username>/aios.git .

# Вариант B: через SSH (потребуется deploy key)
git clone git@github.com:<your-username>/aios.git .
```

### 3. Python-окружение

```bash
cd /opt/aios
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Переменные окружения

```bash
cp .env.example .env
nano .env
```

Заполнить:

| Переменная | Где получить |
|-----------|-------------|
| `OPENAI_API_KEY` | https://platform.openai.com/api-keys |
| `TELEGRAM_BOT_TOKEN` | @BotFather в Telegram → `/newbot` |
| `TELEGRAM_ALLOWED_USER_IDS` | Отправить `/start` боту @userinfobot, скопировать свой ID |
| `YANDEX_EMAIL` | Адрес Яндекс Почты |
| `YANDEX_APP_PASSWORD` | Яндекс ID → Безопасность → Пароли приложений |
| `FIREFLIES_API_KEY` | https://app.fireflies.ai/integrations/custom (опционально) |
| `YOUTUBE_API_KEY` | Google Cloud Console → APIs & Services (опционально) |
| `GA4_PROPERTY_ID` | Google Analytics → Admin → Property Settings (опционально) |
| `YANDEX_METRIKA_TOKEN` | OAuth-токен Яндекс Метрики (scope `metrika:read`) |
| `YANDEX_METRIKA_COUNTER_ID` | ID счётчика Яндекс Метрики |

Минимум для работы бота: `OPENAI_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_USER_IDS`.
Для почты: + `YANDEX_EMAIL`, `YANDEX_APP_PASSWORD`.
Для Метрики: + `YANDEX_METRIKA_TOKEN`, `YANDEX_METRIKA_COUNTER_ID`.

### 5. Создание директорий данных

```bash
mkdir -p /opt/aios/data/{voice_notes,inbox,outbox,intelligence_reports/transcripts}
mkdir -p /opt/aios/logs
```

### 6. Проверка запуска

```bash
cd /opt/aios
source venv/bin/activate
source .env
python execution/telegram/bot.py
```

Отправить боту `/start` в Telegram — должен ответить «AIOS is online.»

### 7. Установка Claude Code (для скиллов)

Claude Code нужен для `/cc`, автоделегирования (Calendar, файлы) и кнопки «Документ» в /skills.

```bash
# Установить Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo bash -
sudo apt install -y nodejs

# Установить Claude Code глобально
sudo npm install -g @anthropic-ai/claude-code

# Авторизоваться (нужна подписка Claude Max или API ключ)
claude auth login
```

Без Claude Code бот работает (чат, задачи, брифинг, данные, **почта**), но `/cc` и кнопка «Документ» будут выдавать ошибку.

### 8. Systemd-сервис (автозапуск)

```bash
sudo nano /etc/systemd/system/aios-bot.service
```

Содержимое:

```ini
[Unit]
Description=AIOS Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/aios
EnvironmentFile=/opt/aios/.env
ExecStart=/opt/aios/venv/bin/python execution/telegram/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Активировать:

```bash
sudo systemctl daemon-reload
sudo systemctl enable aios-bot
sudo systemctl start aios-bot

# Проверить статус
sudo systemctl status aios-bot

# Логи
sudo journalctl -u aios-bot -f
```

### 9. Cron-задачи

```bash
crontab -e
```

Добавить:

```cron
# Сбор метрик — каждый день в 6:00 UTC (9:00 МСК)
0 6 * * * /opt/aios/cron/data_snapshot.sh >> /opt/aios/logs/cron.log 2>&1

# Обзор статьи по вашей теме — каждый день в 6:00 UTC (9:00 МСК)
0 6 * * * /opt/aios/cron/article_finder.sh >> /opt/aios/logs/cron.log 2>&1

# Ежедневный бриф — каждый день в 7:00 UTC (10:00 МСК)
0 7 * * * /opt/aios/cron/daily_brief.sh >> /opt/aios/logs/cron.log 2>&1

# Напоминания о задачах — каждые 15 минут
*/15 * * * * /opt/aios/cron/task_reminder.sh >> /opt/aios/logs/cron.log 2>&1

# Автосинхронизация с GitHub — каждые 5 минут
*/5 * * * * /opt/aios/cron/git_sync.sh >> /opt/aios/logs/cron.log 2>&1
```

### 10. Управление ботом

```bash
# Перезапустить бота
sudo systemctl restart aios-bot

# Остановить
sudo systemctl stop aios-bot

# Логи в реальном времени
sudo journalctl -u aios-bot -f

# Обновить код вручную
cd /opt/aios && git pull && sudo systemctl restart aios-bot
```

## Что работает без дополнительных API

| Функция | Нужные ключи |
|---------|-------------|
| Чат с ИИ | OPENAI_API_KEY |
| Задачи (GTD) + напоминания | OPENAI_API_KEY |
| Голосовые сообщения | OPENAI_API_KEY |
| Анализ фото | OPENAI_API_KEY |
| Почта (чтение, ответ, отправка) | YANDEX_EMAIL + YANDEX_APP_PASSWORD |
| Почта (AI-саммари писем) | OPENAI_API_KEY + YANDEX_EMAIL + YANDEX_APP_PASSWORD |
| Приём и обработка документов | OPENAI_API_KEY (для контекста) или Claude Code (для обработки) |
| Создание документов (скилл) | OPENAI_API_KEY + Claude Code |
| Ежедневный бриф | OPENAI_API_KEY + источники данных |
| Транскрипция встреч | FIREFLIES_API_KEY |
