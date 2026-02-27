#!/bin/bash

# This script is intended to be run by a cron job to generate and send the daily brief.
# Example cron job (runs every day at 7 AM):
# 0 7 * * * /path/to/your/project/liam_ottley_aios/cron/daily_brief.sh >> /path/to/your/project/liam_ottley_aios/logs/cron.log 2>&1

# Navigate to the script directory
cd "$(dirname "$0")/../execution/daily_brief"

# Run the brief generator script
python3 brief_generator.py
