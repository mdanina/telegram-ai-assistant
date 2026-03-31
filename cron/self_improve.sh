#!/bin/bash

# Daily self-improvement scout — searches for AI agent features and proposes improvements.
# Cron: 0 8 * * * /opt/aios/cron/self_improve.sh >> /opt/aios/logs/cron.log 2>&1

cd /opt/aios

set -a
source /opt/aios/.env
set +a

/opt/aios/venv/bin/python execution/intelligence/self_improve.py
