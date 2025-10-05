#!/bin/bash
# Startup script for the devcontainer
# This script starts PostgreSQL and sets up the development environment

set -e

echo "Starting PostgreSQL..."
# Try different methods to start PostgreSQL
if command -v service &> /dev/null; then
    service postgresql start || {
        # Try to detect PostgreSQL version dynamically
        PG_VERSION=$(ls /etc/postgresql/ 2>/dev/null | head -n 1)
        if [ -n "$PG_VERSION" ]; then
            pg_ctlcluster "$PG_VERSION" main start
        else
            echo "Warning: Could not detect PostgreSQL version or start PostgreSQL"
        fi
    }
elif command -v pg_ctl &> /dev/null; then
    PG_DATA=$(find /var/lib/postgresql -maxdepth 2 -name "main" -type d 2>/dev/null | head -n 1)
    if [ -n "$PG_DATA" ]; then
        su postgres -c "pg_ctl -D $PG_DATA start"
    else
        echo "Warning: Could not find PostgreSQL data directory"
    fi
else
    echo "Warning: Could not start PostgreSQL automatically"
fi

echo "Installing project dependencies..."
poetry install --with dev

echo ""
echo "==================================="
echo "Development container is ready!"
echo "==================================="
echo ""
echo "PostgreSQL is running on port 5432"
echo ""
echo "To run the bot:"
echo "  poetry run python -m asdana.main"
echo ""
echo "To run tests:"
echo "  poetry run pytest"
echo ""
echo "To access PostgreSQL:"
echo "  psql -U postgres"
echo ""

# Keep the container running
exec "$@"
