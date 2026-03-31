#!/bin/bash

# Daily article finder — searches PMC for articles on your configured topic,
# generates a review, sends to Telegram.
# Cron: 0 6 * * * /opt/aios/cron/article_finder.sh >> /opt/aios/logs/cron.log 2>&1

cd /opt/aios

set -a
source /opt/aios/.env
set +a

/opt/aios/venv/bin/python execution/intelligence/article_finder.py
