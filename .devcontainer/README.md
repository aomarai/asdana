# Development Container

This directory contains the development container configuration for the Asdana project. The devcontainer can be used with VS Code or standalone with any IDE.

## Prerequisites

- Docker Desktop (for Windows/Mac) or Docker Engine (for Linux)
- Docker Compose (usually included with Docker Desktop)

**Note:** The commands in this guide use `docker-compose`, but newer Docker versions use `docker compose` (without hyphen). Both work the same way, so use whichever is available on your system.

## Using with VS Code (Recommended)

1. Install the "Remote - Containers" extension in VS Code
2. Open the project folder in VS Code
3. Press `F1` and select "Remote-Containers: Reopen in Container"
4. Wait for the container to build and start

## Using with Other IDEs (IntelliJ, PyCharm, vim, etc.)

### Quick Start with Helper Script

The easiest way to use the devcontainer without VS Code is to use the provided helper script:

**On Linux/macOS/Windows (Git Bash/WSL):**
```bash
# From the project root directory
.devcontainer/dev.sh start
```

**On Windows (cmd.exe):**
```cmd
.devcontainer\dev.bat start
```

This will build and start the development container. Then access it:

**Linux/macOS/Git Bash:**
```bash
.devcontainer/dev.sh shell
```

**Windows (cmd.exe):**
```cmd
.devcontainer\dev.bat shell
```

### Manual Setup (Alternative)

If you prefer not to use the helper scripts:

1. **Build and start the container:**
   ```bash
   # From the project root directory
   # Use either:
   docker-compose -f .devcontainer/docker-compose.yml up -d
   # or (newer Docker versions):
   docker compose -f .devcontainer/docker-compose.yml up -d
   ```

2. **Access the container shell:**
   ```bash
   docker exec -it asdana-devcontainer bash
   ```

3. **Start PostgreSQL inside the container:**
   ```bash
   service postgresql start || pg_ctlcluster 17 main start
   ```

4. **Install dependencies (if not already done):**
   ```bash
   poetry install --with dev
   ```

5. **Run the bot:**
   ```bash
   poetry run python -m asdana.main
   ```

### Windows-Specific Notes

On Windows, you can use PowerShell or Command Prompt with the same commands:

```powershell
# Build and start
docker-compose -f .devcontainer/docker-compose.yml up -d

# Access the container
docker exec -it asdana-devcontainer bash

# Inside the container, everything works the same as Linux
```

### Useful Commands

**Stop the container:**
```bash
docker-compose -f .devcontainer/docker-compose.yml down
```

**View container logs:**
```bash
docker-compose -f .devcontainer/docker-compose.yml logs -f
```

**Rebuild the container (after Dockerfile changes):**
```bash
docker-compose -f .devcontainer/docker-compose.yml build --no-cache
docker-compose -f .devcontainer/docker-compose.yml up -d
```

**Run commands in the container without entering it:**
```bash
docker exec asdana-devcontainer poetry run pytest
docker exec asdana-devcontainer poetry run pylint asdana
```

## What's Included

The development container includes:

- Python 3.12
- Poetry for dependency management
- PostgreSQL 17 database server
- Git
- All project dependencies (installed via Poetry)

## IDE Integration

### PyCharm / IntelliJ IDEA

1. Start the devcontainer as described above
2. In PyCharm, go to Settings → Project → Python Interpreter
3. Click the gear icon → Add
4. Select "Docker Compose"
5. Choose the `.devcontainer/docker-compose.yml` file
6. Select the `devcontainer` service
7. PyCharm will now use the Python environment inside the container

### VS Codium / Other VS Code Alternatives

These editors may support the same Remote-Containers functionality as VS Code. Install the appropriate extension for your editor.

### Terminal-Based IDEs (vim, emacs, nano)

Simply exec into the running container and use your preferred editor:

```bash
docker exec -it asdana-devcontainer bash
# Now you're inside the container with all tools available
vim asdana/main.py
```

## Troubleshooting

### PostgreSQL won't start

If PostgreSQL fails to start, try initializing it manually:

```bash
docker exec -it asdana-devcontainer bash
su - postgres
initdb -D /var/lib/postgresql/17/main
pg_ctl -D /var/lib/postgresql/17/main start
```

### Permission issues on Windows

If you encounter permission issues with mounted volumes on Windows:
1. Ensure Docker Desktop has access to the drive where your project is located
2. Go to Docker Desktop Settings → Resources → File Sharing
3. Add the drive/folder containing your project

### Container won't build

Try removing old containers and images:

```bash
docker-compose -f .devcontainer/docker-compose.yml down -v
docker system prune -a
docker-compose -f .devcontainer/docker-compose.yml build --no-cache
```

## Configuration

### devcontainer.json

This file contains VS Code-specific configuration. When using other IDEs, you can ignore this file.

### Dockerfile

The Dockerfile defines the container image. Modify this if you need to add system packages or change the base image.

### docker-compose.yml

This file defines how to run the container. It includes volume mounts, port mappings, and other runtime configuration.
