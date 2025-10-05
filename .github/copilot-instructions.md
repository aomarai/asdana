# Asdana Discord Bot - Copilot Agent Instructions

## Repository Overview

**Asdana** is a powerful, highly customizable Discord bot written in Python 3.12. It's a small-to-medium sized project (~645 lines of Python code) that uses discord.py, SQLAlchemy with asyncpg for PostgreSQL database management, and Poetry for dependency management.

### Key Technologies
- **Language**: Python 3.12+
- **Framework**: discord.py 2.4.0+
- **Database**: PostgreSQL 17 with SQLAlchemy (async) + asyncpg
- **Dependency Manager**: Poetry 1.8.2
- **Testing**: pytest with pytest-asyncio
- **Linting**: pylint (configured for score 10.0/10)
- **Formatting**: Black (line length: 88, version 24.10.0)
- **Container**: Docker with devcontainer support

## Build and Validation Commands

**IMPORTANT**: Always run these commands in the exact sequence shown. All commands require Poetry to be in PATH.

### Environment Setup (First Time Only)
```bash
# Install Poetry if not available (may require internet access)
pip3 install poetry==1.8.2

# Ensure Poetry is in PATH
export PATH="$HOME/.local/bin:$PATH"

# Install all dependencies (takes ~2-3 minutes)
poetry install --with test,dev
```

### Running Tests
```bash
# ALWAYS run tests before making changes to check baseline
export PATH="$HOME/.local/bin:$PATH"
poetry run pytest tests/ -v

# Expected: 16 tests passing (as of current state)
# Test time: ~2 seconds
```

### Running Linter
```bash
# ALWAYS run before committing changes
export PATH="$HOME/.local/bin:$PATH"
poetry run pylint $(git ls-files '*.py')

# Expected output: "Your code has been rated at 10.00/10"
# Runtime: ~10-15 seconds
```

### Running Formatter
```bash
# Check formatting (CI requirement)
export PATH="$HOME/.local/bin:$PATH"
poetry run black --check .

# Auto-fix formatting issues
poetry run black .
```

### Complete Validation Sequence
```bash
# Run this full sequence before submitting any PR
export PATH="$HOME/.local/bin:$PATH"
poetry run black .
poetry run pylint $(git ls-files '*.py')
poetry run pytest tests/ -v
```

## GitHub Actions CI/CD

The repository has THREE GitHub workflows that run on every PR and push to main:

1. **Black Formatter** (`.github/workflows/black.yml`)
   - Runs: `poetry run black --check .`
   - **CRITICAL**: Must pass with no formatting changes needed

2. **Pylint Linter** (`.github/workflows/pylint.yml`)
   - Runs: `poetry run pylint $(git ls-files '*.py')`
   - **CRITICAL**: Must achieve 10.00/10 score

3. **Pytest Unit Tests** (`.github/workflows/pytest.yml`)
   - Runs: `poetry run pytest tests/ -v`
   - **CRITICAL**: All tests must pass

**Setup Action**: All workflows use `.github/actions/setup/action.yml` which:
- Uses Python 3.10 (note: different from dev Python 3.12)
- Installs Poetry 1.7.1
- Runs `poetry install --with test`

> **⚠️ WARNING: Version Mismatch Between Development and CI**
>
> - **Development Environment:** Python 3.12, Poetry 1.8.2
> - **CI Environment:** Python 3.10, Poetry 1.7.1
>
> This version mismatch can lead to inconsistent behavior, such as:
> - Dependency resolution differences (Poetry 1.7.1 vs 1.8.2)
> - Syntax or feature incompatibilities (Python 3.10 vs 3.12)
> - Tests passing locally but failing in CI, or vice versa
>
> **Guidance:**
> - When adding or updating dependencies, check compatibility with both Python 3.10 and 3.12.
> - If you encounter issues that only appear in CI, verify if they are related to the Python or Poetry version.
> - Consider using [pyenv](https://github.com/pyenv/pyenv) or Docker to test your code in both environments.
> - If possible, align your local environment with CI for maximum consistency.
## Project Structure

```
asdana/
├── .github/
│   ├── actions/setup/        # Reusable CI setup action
│   └── workflows/             # CI/CD pipelines (black, pylint, pytest)
├── .devcontainer/             # VS Code devcontainer + standalone Docker support
│   ├── Dockerfile             # Dev environment (Python 3.12 + PostgreSQL 17)
│   ├── docker-compose.yml     # Dev container orchestration
│   ├── dev.sh                 # Helper script for Linux/Mac/Git Bash
│   └── README.md              # Detailed devcontainer docs
├── asdana/                    # Main source code
│   ├── cogs/                  # Discord bot extensions (commands)
│   │   ├── config/            # Server configuration commands (admin only)
│   │   ├── dev/               # Development/debugging commands
│   │   ├── guild/             # Guild information commands
│   │   ├── members/           # Member management
│   │   ├── menus/             # Reaction-based interactive menus
│   │   ├── random/            # Random number/dice commands
│   │   └── youtube/           # YouTube integration commands
│   ├── database/              # Database layer
│   │   ├── database.py        # Session management, engine config
│   │   └── models.py          # SQLAlchemy models (GuildSettings, CogSettings, etc.)
│   ├── utils/                 # Utility modules
│   │   ├── cog_utils.py       # Cog helper functions
│   │   └── menu_factory.py    # Menu creation utilities
│   └── main.py                # Bot entry point
├── tests/                     # Unit tests (mirrors asdana/ structure)
│   └── cogs/                  # Tests for each cog
├── .pylintrc                  # Pylint configuration (fail-under=10)
├── pyproject.toml             # Poetry dependencies and tool configs
├── Dockerfile                 # Production Docker image
├── docker-compose.yml         # Production deployment (bot + PostgreSQL)
├── Makefile                   # Docker build/run helpers
└── README.md                  # User-facing documentation
```

## Architecture & Key Files

### Main Entry Point
- **`asdana/main.py`**: Initializes bot, loads environment variables from `.env`, creates database tables, dynamically loads all cogs from `asdana/cogs/`, and starts the bot

### Database Layer
- **`asdana/database/database.py`**: Creates async PostgreSQL engine using asyncpg, provides `get_session()` context manager
- **`asdana/database/models.py`**: Defines SQLAlchemy models:
  - `GuildSettings`: Per-server configuration (prefix, admin roles, enabled cogs)
  - `CogSettings`: Per-server cog enable/disable state
  - `YouTubeVideo`: Cached YouTube video metadata
  - Other models for menus and reactions
- **Database URL format**: `postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}`
- **Note**: Uses deprecated `declarative_base()` (SQLAlchemy 2.0 warning exists but not blocking)

### Cogs Architecture
- Each cog is in its own directory under `asdana/cogs/`
- Each cog must have `__init__.py` with an `async setup()` function
- Cogs are auto-loaded by `main.py` using directory walk
- Example cog structure: `asdana/cogs/random/` contains `__init__.py` and `random.py`

### Environment Variables
Required in `.env` file (copy from `.env.example`):
```
BOT_TOKEN=<required>          # Discord bot token
BOT_DESCRIPTION=<optional>    # Bot description
DB_NAME=asdana                # Database name
DB_USER=postgres              # Database user
DB_PASSWORD=<required>        # Database password
DB_HOST=localhost             # Use 'postgres' for Docker Compose
DB_PORT=5432                  # PostgreSQL port
YT_API_KEY=<optional>         # YouTube API key
TESTING_GUILD_ID=<optional>   # Test server ID for slash commands
LOG_LEVEL=INFO                # Logging level
```

## Development Workflow

### Using Devcontainer (Recommended for Development)
The devcontainer includes Python 3.12 and PostgreSQL 17 pre-configured.

**Start container**:
```bash
# Linux/Mac/Git Bash
.devcontainer/dev.sh start
.devcontainer/dev.sh shell

# Windows cmd
.devcontainer\dev.bat start
.devcontainer\dev.bat shell
```

**Inside container**:
```bash
# Start PostgreSQL (required for bot to run)
service postgresql start

# Run the bot (requires .env file configured)
poetry run python -m asdana.main

# Run tests
poetry run pytest

# Run linting
poetry run pylint asdana
```

### Common Pitfalls & Workarounds

1. **Poetry not in PATH**: Always export PATH before running poetry commands:
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```

2. **Lock file compatibility warning**: If you see a warning about the Poetry lock file being created with a different Poetry version (e.g., "The lock file was generated with Poetry 1.7.1, but you are running 1.8.2"), this is usually safe to ignore for minor version differences *if* dependencies install and the project runs as expected. However, if you encounter installation errors or are using a significantly different Poetry version, regenerate the lock file with:
   ```bash
   poetry lock --no-update

3. **PostgreSQL not running**: If tests fail with connection errors, PostgreSQL may not be running:
   ```bash
   # In devcontainer
   service postgresql start
   # Or
   pg_ctlcluster 17 main start
   ```

4. **Test database isolation**: Tests use separate DB config set in `tests/conftest.py`:
   - `DB_NAME=test_asdana`
   - `DB_USER=test_user`
   - Test warnings about `declarative_base()` and coroutine warnings are expected and non-blocking

5. **Pre-commit hooks**: If pre-commit fails with network errors, it's likely due to blocked domains. Pre-commit is not required for local development but is configured in `.pre-commit-config.yaml` for black formatting.

## Testing Guidelines

### Test Structure
- Tests mirror source structure: `tests/cogs/random/` tests `asdana/cogs/random/`
- Use pytest fixtures from `tests/conftest.py` and `tests/helpers.py`
- Async tests use `pytest-asyncio` with `asyncio_mode = 'auto'` (configured in `pyproject.toml`)

### Writing Tests
- **ALWAYS write tests for new cogs or commands**
- Use `pytest-mock` for mocking Discord objects
- Mock database sessions when testing database interactions
- Follow existing patterns in `tests/cogs/` for consistency

### Test Execution
```bash
# Run all tests
poetry run pytest tests/ -v

# Run specific test file
poetry run pytest tests/cogs/random/test_random.py -v

# Run with coverage
poetry run pytest tests/ --cov=asdana
```

## Code Style Requirements

### Pylint
- **Must achieve 10.00/10 score** (configured in `.pylintrc`)
- Line length: 100 characters
- Snake_case for functions/variables, PascalCase for classes
- Docstrings required for all public functions and classes

### Black
- Line length: 88 characters (configured in `pyproject.toml`)
- Version: 24.10.0 (must match exactly)
- Auto-formats on save if using pre-commit hooks

### General Guidelines
1. **Always write relevant unit tests when making code changes**
2. **Always ensure all linting and tests pass (10/10 and 100%)**
3. **Follow DRY principles where it improves maintainability**
4. **Add docstrings to all functions and classes** (PEP 257)
5. **Use type hints** where beneficial for clarity

## Docker Deployment

### Production Deployment
```bash
# Using docker-compose (recommended)
docker-compose up -d

# Or using Makefile
make compose-up
```

### Production Image
- Based on `python:3.12-slim`
- Uses Poetry 1.7.1
- Multi-stage build for smaller image size
- Entrypoint: `/entrypoint.sh` → runs `python asdana/main.py`

## Trust These Instructions

**These instructions have been validated by running all commands and workflows**. When working on this repository:

1. **Start here**: Read these instructions first to understand the project
2. **Follow the sequences**: Use the exact command sequences provided
3. **Run validations frequently**: Test, lint, and format after each change
4. **Only search if**: Instructions are incomplete, incorrect, or the codebase has changed

## Key Reminders

- Python version: **3.12** (dev) / **3.10** (CI)
- Poetry version: **1.8.2** (local) / **1.7.1** (CI)
- PostgreSQL version: **17** (with asyncpg driver)
- All CI checks must pass: Black, Pylint 10/10, Pytest 100%
- Tests should take ~2 seconds, linting ~10-15 seconds
- Repository size: ~645 lines of Python code (small-to-medium project)
