#!/bin/bash

# Heartbeat cron — proactive CEO nudges every 30 minutes.
# Cron: */30 * * * * /opt/aios/cron/heartbeat.sh >> /opt/aios/logs/cron.log 2>&1

cd /opt/aios

set -a
source /opt/aios/.env
set +a

/opt/aios/venv/bin/python execution/daily_brief/heartbeat.py
