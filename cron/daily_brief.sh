#!/bin/bash

# Daily brief cron job — generates brief and sends to Telegram.
# Cron: 0 7 * * * /opt/aios/cron/daily_brief.sh >> /opt/aios/logs/cron.log 2>&1

cd /opt/aios

# Load environment variables
set -a
source /opt/aios/.env
set +a

# Use venv python (packages installed there)
/opt/aios/venv/bin/python execution/daily_brief/brief_generator.py --send
