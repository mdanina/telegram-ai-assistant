#!/usr/bin/env python3
"""
Telegram Bot: Slash Command Handler

This script handles incoming slash commands from the Telegram bot.
"""

import subprocess
from telegram import Update
from telegram.ext import ContextTypes

async def handle_slash_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Executes the appropriate script based on the slash command."""
    command = update.message.text.split(" ")[0][1:] # Get command without slash
    args = update.message.text.split(" ")[1:]

    script_path = ""
    if command == "brief":
        script_path = "execution/daily_brief/brief_generator.py"
    elif command == "query":
        script_path = "execution/data_os/query.py"
    # Add more command mappings here
    else:
        await update.message.reply_text(f"Unknown command: /{command}")
        return

    await update.message.reply_text(f"Executing /{command}... Please wait.")

    try:
        # We use subprocess to run the scripts. This is a simple approach.
        # A more robust system might use a job queue like Celery.
        result = subprocess.run(
            ["python3", script_path] + args,
            capture_output=True,
            text=True,
            check=True,
            timeout=300 # 5-minute timeout
        )
        output = result.stdout
        # Send the first 4096 characters of the output, as Telegram has a message limit
        await update.message.reply_text(f"**Output for /{command}:**\n\n```\n{output[:4000]}\n```", parse_mode="MarkdownV2")

    except subprocess.CalledProcessError as e:
        await update.message.reply_text(f"Error executing /{command}:\n\n```\n{e.stderr}\n```", parse_mode="MarkdownV2")
    except subprocess.TimeoutExpired:
        await update.message.reply_text(f"Command /{command} timed out after 5 minutes.")
    except Exception as e:
        await update.message.reply_text(f"An unexpected error occurred: {e}")
