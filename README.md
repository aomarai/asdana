# Asdana

A powerful, highly customizable, and easy-to-use Discord bot built with Python 3.12 and discord.py.

## 🌟 Features

- **Random Number Generation**: Generate random numbers, roll dice, and play video roulette
- **YouTube Integration**: Search and fetch random YouTube videos using the YouTube Data API
- **Interactive Menus**: Create reaction-based interactive menus with persistent storage
- **Guild Management**: View guild information and manage server settings
- **Database Persistence**: PostgreSQL database for storing user data, menus, and YouTube videos
- **Extensible Cog System**: Modular architecture for easy feature additions
- **Development Tools**: Built-in development commands for testing and debugging

## 📋 Prerequisites

- Python 3.12 or higher
- PostgreSQL 17 (for database)
- Poetry (Python dependency manager)
- Discord Bot Token (from [Discord Developer Portal](https://discord.com/developers/applications))
- YouTube API Key (optional, for YouTube features)

## 🚀 Quick Start

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/aomarai/asdana.git
   cd asdana
   ```

2. **Install Poetry** (if not already installed)
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. **Install dependencies**
   ```bash
   poetry install
   ```

### Configuration

Create a `.env` file in the root directory with the following environment variables:

```env
# Required
BOT_TOKEN=your_discord_bot_token_here
BOT_DESCRIPTION=A powerful Discord bot

# Database Configuration
DB_NAME=asdana
DB_USER=postgres
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432

# Optional
YT_API_KEY=your_youtube_api_key_here
TESTING_GUILD_ID=your_test_server_id
LOG_LEVEL=INFO
CLEANUP_INTERVAL_MENUS=3600
CLEANUP_BATCH_SIZE_MENUS=100
```

### Database Setup

1. **Install PostgreSQL 17** (if not already installed)
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install postgresql-17
   
   # macOS
   brew install postgresql@17
   ```

2. **Create the database**
   ```bash
   sudo -u postgres psql
   CREATE DATABASE asdana;
   CREATE USER your_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE asdana TO your_user;
   \q
   ```

3. **Tables are created automatically** when you first run the bot

### Running the Bot

```bash
# Using Poetry
poetry run python asdana/main.py

# Or activate the virtual environment first
poetry shell
python asdana/main.py
```

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

The easiest way to run the bot with a PostgreSQL database:

1. **Create a .env file** with your configuration:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

2. **Start the services**
   ```bash
   docker-compose up -d
   ```

3. **View logs**
   ```bash
   docker-compose logs -f
   ```

4. **Stop the services**
   ```bash
   docker-compose down
   ```

Or use the Makefile shortcuts:
```bash
make compose-up      # Start all services
make compose-logs    # View logs
make compose-down    # Stop all services
make compose-restart # Restart all services
```

### Using Docker with Makefile

The project includes a Makefile for easy container management:

1. **Build the image**
   ```bash
   make build
   ```

2. **Run the container**
   ```bash
   # Make sure you have a .env file with required environment variables
   make run
   ```

3. **View logs**
   ```bash
   make logs
   ```

4. **Stop the container**
   ```bash
   make stop
   ```

5. **Clean up**
   ```bash
   make clean
   ```

For help with all available commands:
```bash
make help
```

### Using Docker Manually

1. **Build the image**
   ```bash
   docker build -t asdana:latest .
   ```

2. **Run the container**
   ```bash
   docker run -d \
     --name asdana-bot \
     --restart unless-stopped \
     --env-file .env \
     asdana:latest
   ```

   Or with individual environment variables:
   ```bash
   docker run -d \
     --name asdana-bot \
     --restart unless-stopped \
     -e BOT_TOKEN=your_token \
     -e BOT_DESCRIPTION="A powerful Discord bot" \
     -e DB_NAME=asdana \
     -e DB_USER=postgres \
     -e DB_PASSWORD=your_password \
     -e DB_HOST=your_db_host \
     -e DB_PORT=5432 \
     -e YT_API_KEY=your_youtube_key \
     -e TESTING_GUILD_ID=your_guild_id \
     asdana:latest
   ```

### Using Dev Container (VS Code)

The project includes a complete dev container configuration for easy development:

1. Open the project in VS Code
2. Install the "Remote - Containers" extension
3. Press `F1` and select "Remote-Containers: Reopen in Container"
4. The container will automatically set up Python, PostgreSQL, and all dependencies

## 🎮 Available Commands

### Random Commands
- `!random [floor] [ceiling]` or `!rand` - Generate a random number (default: 1-100)
- `!roll [sides]` or `!dice` - Roll a die with specified sides (default: 20)
- `!vroulette` or `!vr` - Get a random YouTube video (requires database setup)

### YouTube Commands
- `!randyt` or `!ryt` - Get a random YouTube video from the database

### Guild Commands
- `!menu` or `!m` - Create an example interactive menu with reactions

### Development Commands (Dev Cog)
- `!ginfo` - Display information about the current guild

## 📁 Project Structure

```
asdana/
├── asdana/                 # Main application code
│   ├── cogs/              # Bot command modules (cogs)
│   │   ├── dev/          # Development commands
│   │   ├── guild/        # Guild-related commands
│   │   ├── members/      # Member management commands
│   │   ├── menus/        # Interactive menu system
│   │   ├── random/       # Random number/dice commands
│   │   └── youtube/      # YouTube integration
│   ├── database/         # Database models and configuration
│   │   ├── database.py   # Database connection and session management
│   │   └── models.py     # SQLAlchemy models (User, Menu, YouTubeVideo)
│   ├── utils/            # Utility functions
│   └── main.py           # Bot entry point
├── tests/                # Unit tests
├── .devcontainer/        # VS Code dev container configuration
├── Dockerfile            # Production Docker image
├── pyproject.toml        # Poetry dependencies and project metadata
├── .pylintrc             # Pylint configuration
├── .pre-commit-config.yaml # Pre-commit hooks
└── README.md            # This file
```

## 🛠️ Development

### Setting Up Development Environment

1. **Install development dependencies**
   ```bash
   poetry install --with dev,test
   ```

2. **Install pre-commit hooks**
   ```bash
   poetry run pre-commit install
   ```

3. **Run linting**
   ```bash
   poetry run pylint asdana
   ```

4. **Format code**
   ```bash
   poetry run black asdana
   ```

5. **Run tests**
   ```bash
   poetry run pytest
   ```

### Adding New Cogs

1. Create a new directory under `asdana/cogs/` (e.g., `asdana/cogs/mycog/`)
2. Add `__init__.py` to make it a package
3. Create your cog file (e.g., `mycog.py`) with a `setup()` function
4. The bot will automatically load it on startup

Example cog structure:
```python
from discord.ext import commands

class MyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="mycommand")
    async def my_command(self, ctx):
        await ctx.send("Hello from MyCog!")

async def setup(bot):
    await bot.add_cog(MyCog(bot))
```

## 🗃️ Database Models

### User
Stores Discord user information, preferences, and statistics:
- Discord ID, username, discriminator
- Experience and level (for RPG features)
- Command usage metrics
- Timezone and language preferences
- Custom settings

### Menu
Stores interactive menu state for persistence:
- Message and channel IDs
- Menu type and current page
- Expiration time
- Menu data (JSON)

### YouTubeVideo
Stores YouTube video IDs for random video selection

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use Black formatter (line length: 88)
- Add docstrings to all functions and classes
- Write unit tests for new features

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Ash Omaraie**

## 🙏 Acknowledgments

- Built with [discord.py](https://github.com/Rapptz/discord.py)
- Uses [SQLAlchemy](https://www.sqlalchemy.org/) for database management
- Poetry for dependency management
- PostgreSQL for data persistence

## 📞 Support

For issues, questions, or suggestions, please open an issue on the [GitHub repository](https://github.com/aomarai/asdana/issues).
