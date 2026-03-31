#!/bin/bash

# Task reminder cron — checks for due tasks and sends Telegram reminders.
# Cron: */15 * * * * /opt/aios/cron/task_reminder.sh >> /opt/aios/logs/cron.log 2>&1

cd /opt/aios

set -a
source /opt/aios/.env
set +a

# Use venv python (packages installed there)
/opt/aios/venv/bin/python execution/task_os/reminder.py
