#!/bin/bash

# Morning digest cron job — tasks + meetings, separate from daily brief.
# Cron: 5 7 * * * /opt/aios/cron/morning_digest.sh >> /opt/aios/logs/cron.log 2>&1

cd /opt/aios

# Load environment variables
set -a
source /opt/aios/.env
set +a

# Use venv python
/opt/aios/venv/bin/python execution/daily_brief/morning_digest.py --send
