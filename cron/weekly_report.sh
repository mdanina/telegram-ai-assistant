#!/bin/bash

# Weekly strategic report — runs every Sunday at 19:00 UTC.
# Cron: 0 19 * * 0 /opt/aios/cron/weekly_report.sh >> /opt/aios/logs/cron.log 2>&1

cd /opt/aios

set -a
source /opt/aios/.env
set +a

/opt/aios/venv/bin/python execution/intelligence/weekly_report.py --send
