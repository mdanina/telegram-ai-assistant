#!/bin/bash

# This script is intended to be run by a cron job to take a daily snapshot of all data sources.
# Example cron job (runs every day at 6 AM):
# 0 6 * * * /path/to/your/project/liam_ottley_aios/cron/data_snapshot.sh >> /path/to/your/project/liam_ottley_aios/logs/cron.log 2>&1

# Navigate to the script directory to ensure correct relative paths
cd "$(dirname "$0")/../execution/data_os"

# Activate virtual environment if you have one
# source /path/to/your/venv/bin/activate

# Run the snapshot script
python3 snapshot.py
