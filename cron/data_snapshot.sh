#!/bin/bash

# Data snapshot cron — collects metrics from all data sources.
# Cron: 0 6 * * * /opt/aios/cron/data_snapshot.sh >> /opt/aios/logs/cron.log 2>&1

cd /opt/aios

set -a
source /opt/aios/.env
set +a

# Use venv python (packages installed there)
/opt/aios/venv/bin/python execution/data_os/snapshot.py
