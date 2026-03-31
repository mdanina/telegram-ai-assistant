#!/usr/bin/env python3
"""
Product Collector — pulls key business metrics from self-hosted Supabase.

Connects to your Supabase instance via PostgREST API using service_role key.
Metrics mirror the admin dashboard.

Metric groups for daily CEO brief:
  1. Users & Clients (client = user with >= 1 completed appointment)
  2. Consultation funnel (pending_specialist → payment_pending → scheduled → completed)
  3. Revenue (today, yesterday, month, avg check, LTV, MRR)
  4. Assessments (completed, paid, conversion rate)
  5. Specialists (active, avg rating)
  6. Sessions (repeat clients, skip rate)
  7. Packages (sold, sessions used/remaining)
"""

import os
import sqlite3
import logging
from datetime import datetime, timedelta

import requests

logger = logging.getLogger(__name__)

DB_FILE = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'aios_data.db')

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

# PostgREST API base
API = f"{SUPABASE_URL}/rest/v1"


def _headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "count=exact",
    }


def _get(table, params=None):
    """Makes a GET request to Supabase PostgREST."""
    try:
        r = requests.get(f"{API}/{table}", headers=_headers(), params=params or {}, timeout=15)
        r.raise_for_status()
        count_header = r.headers.get("content-range", "")
        total = None
        if "/" in count_header:
            try:
                total = int(count_header.split("/")[1])
            except (ValueError, IndexError):
                pass
        return r.json(), total
    except Exception as e:
        logger.error(f"Supabase request failed ({table}): {e}")
        return [], None


def _count(table, params=None):
    """Shortcut: returns only the count (int or 0)."""
    p = dict(params or {})
    p["select"] = "id"
    p["limit"] = "0"
    _, total = _get(table, p)
    return total if total is not None else 0


# ─────────────────────────────────────────────────────
# Main collector
# ─────────────────────────────────────────────────────

def collect():
    """Collects all Product metrics. Returns dict of metric_name → value."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.warning("Supabase credentials not set, skipping Product collector.")
        return {}

    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    month_start = datetime.now().strftime("%Y-%m-01")
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    m = {}  # metric_name → value

    # ── 1. Users & Clients ──────────────────────────
    m["users_total"] = _count("users")
    m["users_new_today"] = _count("users", {"created_at": f"gte.{today}T00:00:00"})
    m["users_new_month"] = _count("users", {"created_at": f"gte.{month_start}T00:00:00"})

    # Active users = created appointment this month (assessments have profile_id, not user_id)
    appt_users, _ = _get("appointments", {
        "select": "user_id",
        "scheduled_at": f"gte.{month_start}T00:00:00",
        "limit": "10000",
    })
    active_ids = set()
    for row in appt_users:
        uid = row.get("user_id")
        if uid:
            active_ids.add(uid)
    m["users_active_month"] = len(active_ids)

    # Clients = unique users with >= 1 completed appointment (all-time)
    completed_appts_all, _ = _get("appointments", {
        "select": "user_id",
        "status": "eq.completed",
        "limit": "10000",
    })
    client_ids = set(r.get("user_id") for r in completed_appts_all if r.get("user_id"))
    m["clients_total"] = len(client_ids)

    # New clients this month (first completed appointment in this month, but user had none before)
    completed_month, _ = _get("appointments", {
        "select": "user_id",
        "status": "eq.completed",
        "scheduled_at": f"gte.{month_start}T00:00:00",
        "limit": "10000",
    })
    completed_before, _ = _get("appointments", {
        "select": "user_id",
        "status": "eq.completed",
        "scheduled_at": f"lt.{month_start}T00:00:00",
        "limit": "10000",
    })
    old_client_ids = set(r.get("user_id") for r in completed_before if r.get("user_id"))
    new_client_ids = set(r.get("user_id") for r in completed_month if r.get("user_id")) - old_client_ids
    m["clients_new_month"] = len(new_client_ids)

    # ── 2. Consultation Funnel (the key metric user requested) ──
    # Statuses: pending_specialist → payment_pending → scheduled → in_progress → completed
    #           + cancelled, no_show

    # Today's funnel
    for status in ["pending_specialist", "payment_pending", "scheduled",
                   "in_progress", "completed", "cancelled", "no_show"]:
        m[f"funnel_today_{status}"] = _count("appointments", {
            "status": f"eq.{status}",
            "created_at": f"gte.{today}T00:00:00",
        })

    # Monthly funnel
    for status in ["pending_specialist", "payment_pending", "scheduled",
                   "in_progress", "completed", "cancelled", "no_show"]:
        m[f"funnel_month_{status}"] = _count("appointments", {
            "status": f"eq.{status}",
            "scheduled_at": f"gte.{month_start}T00:00:00",
        })

    # ── 3. Revenue ──────────────────────────────────
    # Today
    pay_today, _ = _get("payments", {
        "select": "amount",
        "status": "eq.completed",
        "created_at": f"gte.{today}T00:00:00",
    })
    m["revenue_today"] = sum(float(p.get("amount", 0)) for p in pay_today)

    # Yesterday
    pay_yesterday, _ = _get("payments", {
        "select": "amount",
        "status": "eq.completed",
        "created_at": f"gte.{yesterday}T00:00:00",
        "and": f"(created_at.lt.{today}T00:00:00)",
    })
    m["revenue_yesterday"] = sum(float(p.get("amount", 0)) for p in pay_yesterday)

    # Month
    pay_month, _ = _get("payments", {
        "select": "amount,user_id",
        "status": "eq.completed",
        "created_at": f"gte.{month_start}T00:00:00",
    })
    month_revenue = sum(float(p.get("amount", 0)) for p in pay_month)
    m["revenue_month"] = month_revenue
    m["payments_count_month"] = len(pay_month)
    m["avg_check_month"] = round(month_revenue / len(pay_month), 0) if pay_month else 0

    # LTV: average revenue per paying user (all-time)
    all_payments, _ = _get("payments", {
        "select": "amount,user_id",
        "status": "eq.completed",
        "limit": "10000",
    })
    if all_payments:
        revenue_by_user = {}
        for p in all_payments:
            uid = p.get("user_id")
            if uid:
                revenue_by_user[uid] = revenue_by_user.get(uid, 0) + float(p.get("amount", 0))
        if revenue_by_user:
            m["ltv"] = round(sum(revenue_by_user.values()) / len(revenue_by_user), 0)
        else:
            m["ltv"] = 0
    else:
        m["ltv"] = 0

    # MRR: revenue in last 30 days
    pay_30d, _ = _get("payments", {
        "select": "amount",
        "status": "eq.completed",
        "created_at": f"gte.{thirty_days_ago}T00:00:00",
    })
    m["mrr"] = round(sum(float(p.get("amount", 0)) for p in pay_30d), 0)

    # Refund rate
    _, refunded_count = _get("payments", {
        "select": "id",
        "status": "eq.refunded",
        "limit": "0",
    })
    _, completed_pay_count = _get("payments", {
        "select": "id",
        "status": "eq.completed",
        "limit": "0",
    })
    refunded_count = refunded_count or 0
    completed_pay_count = completed_pay_count or 0
    total_with_refund = completed_pay_count + refunded_count
    m["refund_rate"] = round((refunded_count / total_with_refund) * 100, 1) if total_with_refund > 0 else 0

    # ── 4. Assessments (diagnostics) ────────────────
    m["assessments_total_month"] = _count("assessments", {
        "created_at": f"gte.{month_start}T00:00:00",
    })
    m["assessments_completed_month"] = _count("assessments", {
        "status": "eq.completed",
        "created_at": f"gte.{month_start}T00:00:00",
    })
    m["assessments_abandoned_month"] = _count("assessments", {
        "status": "eq.abandoned",
        "created_at": f"gte.{month_start}T00:00:00",
    })
    m["assessments_paid_month"] = _count("assessments", {
        "is_paid": "eq.true",
        "created_at": f"gte.{month_start}T00:00:00",
    })
    # Conversion: completed / total
    if m["assessments_total_month"] > 0:
        m["assessments_conversion"] = round(
            (m["assessments_completed_month"] / m["assessments_total_month"]) * 100, 1
        )
    else:
        m["assessments_conversion"] = 0

    # ── 5. Specialists ──────────────────────────────
    m["specialists_active"] = _count("specialists", {"is_available": "eq.true"})

    # Average rating
    ratings, _ = _get("specialist_ratings", {
        "select": "rating",
        "limit": "10000",
    })
    if ratings:
        valid = [float(r["rating"]) for r in ratings if r.get("rating") is not None]
        m["specialists_avg_rating"] = round(sum(valid) / len(valid), 2) if valid else 0
        m["specialists_rating_count"] = len(valid)
    else:
        m["specialists_avg_rating"] = 0
        m["specialists_rating_count"] = 0

    # ── 6. Sessions & Repeat Clients ────────────────
    # Repeat clients = users with >= 2 completed appointments
    if completed_appts_all:
        user_session_counts = {}
        for a in completed_appts_all:
            uid = a.get("user_id")
            if uid:
                user_session_counts[uid] = user_session_counts.get(uid, 0) + 1
        m["repeat_clients"] = sum(1 for c in user_session_counts.values() if c >= 2)
        total_sessions = sum(user_session_counts.values())
        m["avg_sessions_per_client"] = round(total_sessions / len(user_session_counts), 1) if user_session_counts else 0
    else:
        m["repeat_clients"] = 0
        m["avg_sessions_per_client"] = 0

    # Skip rate: (cancelled + no_show) / total scheduled this month
    total_scheduled_month = (
        m.get("funnel_month_completed", 0) +
        m.get("funnel_month_cancelled", 0) +
        m.get("funnel_month_no_show", 0) +
        m.get("funnel_month_in_progress", 0) +
        m.get("funnel_month_scheduled", 0)
    )
    skipped = m.get("funnel_month_cancelled", 0) + m.get("funnel_month_no_show", 0)
    m["skip_rate_month"] = round((skipped / total_scheduled_month) * 100, 1) if total_scheduled_month > 0 else 0

    # ── 7. Packages ─────────────────────────────────
    m["packages_sold_month"] = _count("package_purchases", {
        "created_at": f"gte.{month_start}T00:00:00",
    })

    # Package sessions used vs remaining
    pkgs, _ = _get("packages", {
        "select": "id,session_count",
        "limit": "10000",
    })
    purchases, _ = _get("package_purchases", {
        "select": "package_id,sessions_remaining",
        "limit": "10000",
    })
    pkg_sessions = {}
    for p in (pkgs or []):
        pkg_sessions[p.get("id", "")] = int(p.get("session_count", 0))

    if purchases:
        total_bought = 0
        total_remaining = 0
        for pp in purchases:
            pid = pp.get("package_id")
            remaining = int(pp.get("sessions_remaining", 0))
            total_remaining += remaining
            total_bought += pkg_sessions.get(pid, 0)
        m["pkg_sessions_total"] = total_bought
        m["pkg_sessions_used"] = total_bought - total_remaining
        m["pkg_sessions_remaining"] = total_remaining
    else:
        m["pkg_sessions_total"] = 0
        m["pkg_sessions_used"] = 0
        m["pkg_sessions_remaining"] = 0

    logger.info(f"Product metrics collected: {len(m)} metrics")
    return m


def collect_product_metrics(snapshot_id):
    """Collects Product metrics and saves them to the SQLite database."""
    data = collect()
    if not data:
        print("No Product metrics collected (credentials missing or API error).")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    now = datetime.now().isoformat()
    rows = [
        ('Product', metric_name, float(value), now, snapshot_id)
        for metric_name, value in data.items()
    ]

    cursor.executemany(
        "INSERT INTO metrics (source, metric_name, value, date, snapshot_id) VALUES (?, ?, ?, ?, ?)",
        rows,
    )

    conn.commit()
    conn.close()
    print(f"Successfully collected {len(rows)} Product metrics.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))
    data = collect()
    for k, v in sorted(data.items()):
        print(f"  {k}: {v}")
