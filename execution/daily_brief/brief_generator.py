#!/usr/bin/env python3
"""
Daily Brief: Brief Generator

This script generates the daily intelligence brief by pulling data from the
Data OS and Intelligence Layer, synthesizing it with an LLM, and sending it
to Telegram.
"""

import os
import json
import sqlite3
import openai
from datetime import datetime, timedelta
from telegram import Bot
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

DB_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'aios_data.db')
REPORTS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'intelligence_reports')
PROMPT_FILE = os.path.join(os.path.dirname(__file__), 'brief_prompt.md')

openai.api_key = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_TARGET_USER_ID = os.getenv("TELEGRAM_ALLOWED_USER_IDS", "").split(",")[0]

def get_data_summary():
    """Retrieves a summary of key metrics from the Data OS."""
    if not os.path.exists(DB_FILE):
        return "Data OS database not found."
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Example: Get yesterday's Stripe MRR
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    cursor.execute("""
        SELECT value FROM metrics
        WHERE source = 'Stripe' AND metric_name = 'MRR'
        AND date(date) = ?
        ORDER BY date DESC LIMIT 1
    """, (yesterday,))
    mrr_row = cursor.fetchone()
    mrr = mrr_row[0] if mrr_row else "N/A"

    conn.close()
    return f"- Yesterday's Stripe MRR: ${mrr}"

def get_intelligence_summary():
    """Retrieves the latest intelligence report."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    report_path = os.path.join(REPORTS_DIR, f"{today_str}.json")
    
    if not os.path.exists(report_path):
        # Try yesterday's report if today's isn't generated yet
        yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        report_path = os.path.join(REPORTS_DIR, f"{yesterday_str}.json")
        if not os.path.exists(report_path):
            return "No recent intelligence report found."

    with open(report_path, "r") as f:
        report = json.load(f)
    
    # Create a concise summary
    summary = f"- Meetings Analyzed: {len(report.get('meetings', []))}\n"
    summary += f"- Slack Messages Analyzed: {len(report.get('slack', []))}\n"
    summary += f"- Voice Notes Processed: {len(report.get('voice_notes', []))}"
    return summary

def generate_brief():
    """Generates the full daily brief."""
    with open(PROMPT_FILE, "r") as f:
        prompt_template = f.read()

    data_summary = get_data_summary()
    intelligence_summary = get_intelligence_summary()

    final_prompt = prompt_template.format(
        date=datetime.now().strftime("%A, %B %d, %Y"),
        data_os_summary=data_summary,
        intelligence_os_summary=intelligence_summary
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are the AI Operating System, delivering a daily brief."},
                {"role": "user", "content": final_prompt}
            ],
            temperature=0.5,
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"Error generating brief: {e}"

async def send_brief_to_telegram(brief_content):
    """Sends the generated brief to the specified Telegram user."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_TARGET_USER_ID:
        print("Telegram credentials not set. Cannot send brief.")
        return

    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    # Telegram messages have a 4096 character limit
    await bot.send_message(chat_id=TELEGRAM_TARGET_USER_ID, text=brief_content[:4096])

if __name__ == "__main__":
    import asyncio
    print("Generating daily brief...")
    brief = generate_brief()
    print("Brief generated. Sending to Telegram...")
    asyncio.run(send_brief_to_telegram(brief))
    print("Brief sent.")
