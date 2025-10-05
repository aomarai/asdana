#!/bin/bash
# Startup script for the devcontainer
# This script starts PostgreSQL and sets up the development environment

set -e

echo "Starting PostgreSQL..."
# Try different methods to start PostgreSQL
if command -v service &> /dev/null; then
    service postgresql start || pg_ctlcluster 17 main start
elif command -v pg_ctl &> /dev/null; then
    su postgres -c "pg_ctl -D /var/lib/postgresql/17/main start"
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
