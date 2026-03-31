#!/usr/bin/env python3
"""
Data OS: Yandex Metrika Collector

Collects key website metrics from Yandex Metrika API and stores them
in the SQLite database.

API docs: https://yandex.com/dev/metrika/en/stat/
"""

import os
import sqlite3
import requests
from datetime import datetime, timedelta

DB_FILE = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'aios_data.db')
TOKEN = os.getenv("YANDEX_METRIKA_TOKEN")
COUNTER_ID = os.getenv("YANDEX_METRIKA_COUNTER_ID")

API_BASE = "https://api-metrika.yandex.net/stat/v1/data"


def _fetch_metrics(date1, date2, metrics):
    """Fetch metrics from Yandex Metrika API for a date range."""
    headers = {"Authorization": f"OAuth {TOKEN}"}
    params = {
        "id": COUNTER_ID,
        "metrics": ",".join(metrics),
        "date1": date1,
        "date2": date2,
    }
    resp = requests.get(API_BASE, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    # API returns totals[] array matching metrics[] order
    totals = data.get("totals", [])
    result = {}
    for i, metric_name in enumerate(metrics):
        if i < len(totals):
            result[metric_name] = totals[i]
    return result


def _fetch_traffic_sources(date1, date2):
    """Fetch traffic source breakdown."""
    headers = {"Authorization": f"OAuth {TOKEN}"}
    params = {
        "id": COUNTER_ID,
        "metrics": "ym:s:visits,ym:s:users",
        "dimensions": "ym:s:lastTrafficSource",
        "date1": date1,
        "date2": date2,
        "limit": 10,
    }
    resp = requests.get(API_BASE, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    sources = {}
    for row in data.get("data", []):
        dims = row.get("dimensions", [])
        mets = row.get("metrics", [])
        if dims and mets:
            source_name = dims[0].get("name", "unknown")
            sources[source_name] = {
                "visits": int(mets[0]) if len(mets) > 0 else 0,
                "users": int(mets[1]) if len(mets) > 1 else 0,
            }
    return sources


def collect_metrika_metrics(snapshot_id):
    """Collects Yandex Metrika metrics and saves them to the database."""
    if not TOKEN or not COUNTER_ID:
        print("YANDEX_METRIKA_TOKEN or YANDEX_METRIKA_COUNTER_ID not set. Skipping Metrika.")
        return

    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    today = datetime.now().strftime("%Y-%m-%d")

    # Last 30 days for monthly totals
    month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    metrics_list = []

    try:
        # ── Yesterday's metrics ──
        daily_metrics = [
            "ym:s:visits",
            "ym:s:pageviews",
            "ym:s:users",
            "ym:s:newUsers",
            "ym:s:bounceRate",
            "ym:s:avgVisitDurationSeconds",
        ]
        daily = _fetch_metrics(yesterday, yesterday, daily_metrics)

        metric_names = {
            "ym:s:visits": "Визиты (вчера)",
            "ym:s:pageviews": "Просмотры страниц (вчера)",
            "ym:s:users": "Посетители (вчера)",
            "ym:s:newUsers": "Новые посетители (вчера)",
            "ym:s:bounceRate": "Отказы % (вчера)",
            "ym:s:avgVisitDurationSeconds": "Ср. время визита сек (вчера)",
        }

        for key, value in daily.items():
            name = metric_names.get(key, key)
            metrics_list.append((
                'YandexMetrika', name, round(value, 2), yesterday, snapshot_id
            ))

        # ── Monthly totals ──
        monthly_metrics = [
            "ym:s:visits",
            "ym:s:pageviews",
            "ym:s:users",
        ]
        monthly = _fetch_metrics(month_ago, today, monthly_metrics)

        monthly_names = {
            "ym:s:visits": "Визиты (30 дней)",
            "ym:s:pageviews": "Просмотры (30 дней)",
            "ym:s:users": "Посетители (30 дней)",
        }

        for key, value in monthly.items():
            name = monthly_names.get(key, key)
            metrics_list.append((
                'YandexMetrika', name, round(value, 2), today, snapshot_id
            ))

        # ── Traffic sources (yesterday) ──
        sources = _fetch_traffic_sources(yesterday, yesterday)
        for source_name, vals in sources.items():
            metrics_list.append((
                'YandexMetrika',
                f"Источник: {source_name} (визиты)",
                vals["visits"],
                yesterday,
                snapshot_id,
            ))

    except requests.RequestException as e:
        print(f"Yandex Metrika API error: {e}")
        return
    except Exception as e:
        print(f"Yandex Metrika collector error: {e}")
        return

    if not metrics_list:
        print("No Yandex Metrika metrics collected.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT INTO metrics (source, metric_name, value, date, snapshot_id) VALUES (?, ?, ?, ?, ?)",
        metrics_list,
    )
    conn.commit()
    conn.close()
    print(f"Successfully collected {len(metrics_list)} Yandex Metrika metrics.")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))
    # Re-read after dotenv
    TOKEN = os.getenv("YANDEX_METRIKA_TOKEN")
    COUNTER_ID = os.getenv("YANDEX_METRIKA_COUNTER_ID")
    collect_metrika_metrics(f"manual_run_{datetime.now().isoformat()}")
