#!/usr/bin/env python3
"""
Heartbeat: Proactive CEO nudges via Telegram.

Runs every 30 minutes via cron. Checks business signals and sends
contextual messages — metrics insights, coaching nudges, or evening recaps.

Rules (anti-spam):
  - Max 2 nudges per day (Type B + C combined)
  - Min 4 hours between nudges
  - Morning quiet (before 9:00 MSK) — skip
  - Evening recap (21:00-21:30 MSK) — Type D, independent limit
  - Night quiet (after 22:00 MSK) — skip

Message types:
  B = Insight + action suggestion (metric changed, task stale, hypothesis stale)
  C = Coaching nudge (anti-pattern warning, skill suggestion)
  D = Evening recap (daily summary, open threads)

State persisted in data/heartbeat_state.json.
"""

import os
import sys
import json
import sqlite3
import asyncio
import logging
from datetime import datetime, timedelta, timezone
from telegram import Bot
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Paths
_BASE = os.path.join(os.path.dirname(__file__), '..', '..')
load_dotenv(os.path.join(_BASE, '.env'))

DB_FILE = os.path.join(_BASE, 'data', 'aios_data.db')
STATE_FILE = os.path.join(_BASE, 'data', 'heartbeat_state.json')

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_TARGET_USER_ID = os.getenv("TELEGRAM_ALLOWED_USER_IDS", "").split(",")[0]

_MSK = timezone(timedelta(hours=3))


# ── State management ─────────────────────────────────────────────────

def _load_state() -> dict:
    """Load heartbeat state. Reset if new day."""
    default = {
        "today": "",
        "nudge_count": 0,
        "last_nudge_at": "",
        "last_nudge_type": "",
        "last_recap_date": "",
    }
    if not os.path.exists(STATE_FILE):
        return default
    try:
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
        # Reset counters on new day
        today = datetime.now(_MSK).strftime("%Y-%m-%d")
        if state.get("today") != today:
            state["today"] = today
            state["nudge_count"] = 0
        return state
    except Exception:
        return default


def _save_state(state: dict):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


# ── Signal checks ────────────────────────────────────────────────────

def _check_overdue_tasks() -> str | None:
    """Check for overdue tasks."""
    if not os.path.exists(DB_FILE):
        return None
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        today = datetime.now(_MSK).strftime("%Y-%m-%d")
        rows = conn.execute(
            "SELECT COUNT(*) as cnt FROM tasks WHERE status = 'pending' AND due_date IS NOT NULL AND due_date < ?",
            (today,)
        ).fetchone()
        cnt = rows["cnt"] if rows else 0
        if cnt > 0:
            return f"🔴 {cnt} просроченных задач. Посмотри /tasks и реши — перенести или закрыть."
        return None
    finally:
        conn.close()


def _check_stale_tasks() -> str | None:
    """Check for tasks without due dates that have been pending too long."""
    if not os.path.exists(DB_FILE):
        return None
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT COUNT(*) as cnt FROM tasks WHERE status = 'pending' AND due_date IS NULL"
        ).fetchone()
        cnt = rows["cnt"] if rows else 0
        if cnt >= 5:
            return f"⚪ {cnt} задач без срока — они копятся. Расставь приоритеты: /tasks"
        return None
    finally:
        conn.close()


def _check_metric_changes() -> str | None:
    """Check if latest metrics show significant changes vs previous snapshot."""
    if not os.path.exists(DB_FILE):
        return None
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        # Get last 2 snapshots for Product
        rows = conn.execute("""
            SELECT snapshot_id, source, key, value
            FROM metrics
            WHERE source = 'Product'
            ORDER BY snapshot_id DESC
            LIMIT 40
        """).fetchall()

        if len(rows) < 2:
            return None

        # Group by snapshot
        snapshots = {}
        for r in rows:
            sid = r["snapshot_id"]
            if sid not in snapshots:
                snapshots[sid] = {}
            snapshots[sid][r["key"]] = r["value"]

        sids = sorted(snapshots.keys(), reverse=True)
        if len(sids) < 2:
            return None

        latest = snapshots[sids[0]]
        prev = snapshots[sids[1]]

        # Check key metrics for significant changes
        alerts = []
        for key, label in [
            ("total_clients", "Клиентов"),
            ("active_consultations", "Консультаций"),
            ("total_revenue", "Выручка"),
        ]:
            curr_val = _to_float(latest.get(key))
            prev_val = _to_float(prev.get(key))
            if curr_val is not None and prev_val is not None and prev_val > 0:
                change_pct = ((curr_val - prev_val) / prev_val) * 100
                if abs(change_pct) >= 10:  # 10%+ change
                    direction = "📈" if change_pct > 0 else "📉"
                    alerts.append(f"{direction} {label}: {change_pct:+.0f}% ({prev_val:.0f} → {curr_val:.0f})")

        if alerts:
            return "Изменения в метриках Product:\n" + "\n".join(alerts)
        return None
    except Exception as e:
        logger.error(f"Metric check error: {e}")
        return None
    finally:
        conn.close()


def _to_float(val) -> float | None:
    if val is None:
        return None
    try:
        return float(str(val).replace(",", "").replace(" ", "").replace("₽", ""))
    except (ValueError, TypeError):
        return None


def _check_no_brief_today() -> str | None:
    """Check if daily brief was sent today."""
    today = datetime.now(_MSK).strftime("%Y-%m-%d")
    log_file = os.path.join(_BASE, "logs", "cron.log")
    if not os.path.exists(log_file):
        return None
    try:
        with open(log_file, "r") as f:
            lines = f.readlines()[-50:]
        for line in lines:
            if today in line and "brief" in line.lower() and "sent" in line.lower():
                return None
        # If after 10:00 and no brief — warn
        if datetime.now(_MSK).hour >= 10:
            return "⚠️ Сегодня не было утреннего брифа. Что-то сломалось? Попробуй /brief"
        return None
    except Exception:
        return None


# ── Coaching nudges ──────────────────────────────────────────────────

_COACHING_NUDGES = [
    "💡 Давно не разговаривала с клиентами? Самый быстрый способ узнать что не работает — спросить. `/cc conducting-user-interviews`",
    "💡 Есть ли у Product чёткое позиционирование? Проверь: `/cc positioning-messaging`",
    "💡 Когда последний раз пересматривала ценообразование? `/cc pricing-strategy`",
    "💡 Попробуй еженедельный CEO-обзор в воскресенье: `/cc ceo-weekly-review`",
    "💡 Есть гипотезы, которые не проверяешь дольше недели? `/cc hypothesis-tracker`",
    "💡 Контент-стратегия для блога может привести родителей через поиск: `/cc content-strategy`",
    "💡 SEO-аудит сайта — быстрый способ найти упущенный трафик: `/cc seo-audit`",
]


def _get_coaching_nudge(state: dict) -> str | None:
    """Return a coaching nudge, rotating through the list."""
    # Use day of year to rotate
    day = datetime.now(_MSK).timetuple().tm_yday
    idx = day % len(_COACHING_NUDGES)
    return _COACHING_NUDGES[idx]


# ── Evening recap ────────────────────────────────────────────────────

def _build_evening_recap() -> str | None:
    """Build evening recap from today's activity."""
    if not os.path.exists(DB_FILE):
        return None

    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    today = datetime.now(_MSK).strftime("%Y-%m-%d")

    try:
        # Tasks created today
        created = conn.execute(
            "SELECT COUNT(*) as cnt FROM tasks WHERE created_at LIKE ?",
            (today + "%",)
        ).fetchone()["cnt"]

        # Tasks completed today
        completed = conn.execute(
            "SELECT COUNT(*) as cnt FROM tasks WHERE status = 'done' AND created_at LIKE ?",
            (today + "%",)
        ).fetchone()["cnt"]

        # Memories saved today
        memories = conn.execute(
            "SELECT COUNT(*) as cnt FROM bot_memories WHERE created_at LIKE ?",
            (today + "%",)
        ).fetchone()["cnt"]

        # Pending tasks total
        pending = conn.execute(
            "SELECT COUNT(*) as cnt FROM tasks WHERE status = 'pending'"
        ).fetchone()["cnt"]

        if created == 0 and completed == 0 and memories == 0:
            return None

        parts = ["🌙 Итог дня:\n"]
        if created:
            parts.append(f"  • Создано задач: {created}")
        if completed:
            parts.append(f"  • Выполнено: {completed}")
        if memories:
            parts.append(f"  • Новых фактов в памяти: {memories}")
        parts.append(f"  • Всего в работе: {pending}")

        if pending > 0:
            parts.append(f"\nЗавтра не забудь проверить задачи: /tasks")

        return "\n".join(parts)
    except Exception as e:
        logger.error(f"Evening recap error: {e}")
        return None
    finally:
        conn.close()


# ── Main logic ───────────────────────────────────────────────────────

async def run_heartbeat():
    """Main heartbeat logic. Called every 30 minutes by cron."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_TARGET_USER_ID:
        print("Telegram credentials not set.")
        return

    now = datetime.now(_MSK)
    hour = now.hour
    state = _load_state()

    # Night quiet: 22:00 - 08:59
    if hour >= 22 or hour < 9:
        print(f"Quiet hours ({hour}:xx MSK). Skipping.")
        return

    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    # ── Type D: Evening recap (21:00-21:30) ──
    if hour == 21 and now.minute < 30:
        today = now.strftime("%Y-%m-%d")
        if state.get("last_recap_date") != today:
            recap = _build_evening_recap()
            if recap:
                try:
                    await bot.send_message(chat_id=TELEGRAM_TARGET_USER_ID, text=recap[:4096])
                    state["last_recap_date"] = today
                    _save_state(state)
                    print("Evening recap sent.")
                except Exception as e:
                    print(f"Error sending recap: {e}")
            else:
                print("No activity today — skipping recap.")
        return

    # ── Gate: max 2 nudges per day ──
    if state.get("nudge_count", 0) >= 2:
        print(f"Nudge limit reached ({state['nudge_count']}/2). Skipping.")
        return

    # ── Gate: min 4h between nudges ──
    last_at = state.get("last_nudge_at", "")
    if last_at:
        try:
            last_dt = datetime.fromisoformat(last_at)
            if (now - last_dt.replace(tzinfo=None)) < timedelta(hours=4):
                print("Too soon since last nudge. Skipping.")
                return
        except Exception:
            pass

    # ── Choose message type: alternate B → C → B ──
    last_type = state.get("last_nudge_type", "C")
    if last_type == "C":
        # Type B: insight
        msg = _pick_insight()
        msg_type = "B"
    else:
        # Type C: coaching
        msg = _get_coaching_nudge(state)
        msg_type = "C"

    if not msg:
        print("No signal to send. Skipping.")
        return

    try:
        await bot.send_message(chat_id=TELEGRAM_TARGET_USER_ID, text=msg[:4096])
        state["nudge_count"] = state.get("nudge_count", 0) + 1
        state["last_nudge_at"] = now.replace(tzinfo=None).isoformat()
        state["last_nudge_type"] = msg_type
        _save_state(state)
        print(f"Heartbeat sent: Type {msg_type}")
    except Exception as e:
        print(f"Error sending heartbeat: {e}")


def _pick_insight() -> str | None:
    """Pick the most relevant insight to send right now."""
    # Priority order: overdue tasks > metric changes > stale tasks > no brief
    checks = [
        _check_overdue_tasks,
        _check_metric_changes,
        _check_stale_tasks,
        _check_no_brief_today,
    ]
    for check in checks:
        try:
            result = check()
            if result:
                return result
        except Exception as e:
            logger.error(f"Heartbeat check error: {e}")
    return None


if __name__ == "__main__":
    asyncio.run(run_heartbeat())
