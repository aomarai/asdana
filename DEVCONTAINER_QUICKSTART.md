# Quick Start Guide for Non-VSCode Development

This guide will help you set up the Asdana development environment without VS Code.

## Prerequisites

1. Install Docker Desktop (Windows/Mac) or Docker Engine (Linux)
   - Windows: https://docs.docker.com/desktop/install/windows-setup/
   - Mac: https://docs.docker.com/desktop/install/mac-install/
   - Linux: https://docs.docker.com/engine/install/

2. Ensure Docker is running (you should see the Docker icon in your system tray)

## Setup Steps

### Option 1: Using Helper Scripts (Easiest)

**On Windows (using Command Prompt or PowerShell):**
```cmd
cd path\to\asdana
.devcontainer\dev.bat start
.devcontainer\dev.bat shell
```

**On Windows (using Git Bash) / Linux / macOS:**
```bash
cd path/to/asdana
.devcontainer/dev.sh start
.devcontainer/dev.sh shell
```

Once inside the container:
```bash
# Start PostgreSQL
service postgresql start

# Run the bot (after setting up .env file)
poetry run python -m asdana.main

# Run tests
poetry run pytest
```

### Option 2: Using Docker Compose Manually

```bash
# From the project root directory
docker compose -f .devcontainer/docker-compose.yml up -d

# Access the container
docker exec -it asdana-devcontainer bash

# Inside the container, start PostgreSQL
service postgresql start

# Run the bot
poetry run python -m asdana.main
```

## Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your bot token and other settings

3. Start the bot:
   ```bash
   # Make sure you're inside the container
   poetry run python -m asdana.main
   ```

## Troubleshooting

### Docker not found
- Make sure Docker Desktop is installed and running
- On Windows, you may need to restart after installation

### Permission errors on Windows
- Ensure Docker Desktop has permission to access your project folder
- Go to Docker Desktop → Settings → Resources → File Sharing

### Container won't start
- Check if Docker is running: `docker ps`
- Try rebuilding: `.devcontainer/dev.sh rebuild` or `.devcontainer\dev.bat rebuild`

### PostgreSQL won't start
Inside the container, try:
```bash
pg_ctlcluster 17 main start
```

## IDE-Specific Setup

### PyCharm / IntelliJ IDEA
1. Start the container using the helper script or docker compose
2. In PyCharm: Settings → Project → Python Interpreter
3. Add → Docker Compose
4. Select `.devcontainer/docker-compose.yml`
5. Choose the `devcontainer` service

### JetBrains Fleet
Fleet can connect to running Docker containers. Start the container first, then connect Fleet to it.

### Neovim / Vim
Just exec into the container and use vim normally:
```bash
docker exec -it asdana-devcontainer bash
vim asdana/main.py
```

## Common Commands

Inside the container:

```bash
# Run the bot
poetry run python -m asdana.main

# Run tests
poetry run pytest

# Run linting
poetry run pylint asdana

# Format code
poetry run black asdana

# Start PostgreSQL
service postgresql start

# Access PostgreSQL
psql -U postgres

# Install new dependencies
poetry add package-name

# Update dependencies
poetry update
```

## Stopping the Environment

```bash
# Using helper scripts
.devcontainer/dev.sh stop          # Linux/Mac/Git Bash
.devcontainer\dev.bat stop         # Windows cmd

# Or manually
docker compose -f .devcontainer/docker-compose.yml down
```

## More Information

See [.devcontainer/README.md](.devcontainer/README.md) for detailed documentation.
