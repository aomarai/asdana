#!/bin/bash
set -e

echo "Starting Asdana Discord Bot..."

# Run database migrations/table creation on startup
# This is handled automatically by the bot's main.py

# Activate the virtual environment and execute the bot
cd /app
source .venv/bin/activate
exec python asdana/main.py
