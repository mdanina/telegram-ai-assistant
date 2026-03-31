#!/bin/bash

# Meeting auto-processor — checks Fireflies every 2 hours for new meetings.
# Cron: 0 */2 * * * /opt/aios/cron/meeting_autoprocess.sh >> /opt/aios/logs/cron.log 2>&1

cd /opt/aios

set -a
source /opt/aios/.env
set +a

/opt/aios/venv/bin/python execution/intelligence/meeting_autoprocess.py --send
