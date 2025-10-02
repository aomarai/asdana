# Asdana

A powerful, highly customizable, and easy-to-use Discord bot.

## Project Structure

The project is organized into several key packages:

```
asdana/
├── core/                   # Core bot functionality
│   ├── bot.py             # Main bot class and setup
│   ├── config.py          # Configuration management
│   └── logging_config.py  # Logging setup
├── cogs/                   # Bot command extensions
│   ├── dev/               # Development utilities
│   ├── guild/             # Guild-related commands
│   ├── members/           # Member management
│   ├── menus/             # Interactive reaction menus
│   │   ├── reaction_menu.py    # Main menu cog
│   │   ├── menu_handlers.py    # Menu handler functions
│   │   └── menu_cleanup.py     # Cleanup utilities
│   ├── random/            # Random number generation
│   └── youtube/           # YouTube integration
├── database/               # Database layer
│   ├── database.py        # Connection and session management
│   └── models.py          # SQLAlchemy ORM models
├── utils/                  # Utility modules
│   └── menu_factory.py    # Factory for creating menus
└── main.py                 # Application entry point
```

## Key Components

### Core Module

The `core` module contains essential bot functionality:

- **bot.py**: Defines the `AsdanaBot` class with cog loading/unloading
- **config.py**: Centralized configuration from environment variables
- **logging_config.py**: Standardized logging setup

### Cogs

Cogs are modular extensions that add specific functionality:

- **dev**: Development and debugging tools
- **guild**: Guild/server management commands
- **members**: Member-related functionality
- **menus**: Interactive reaction-based menus with persistence
- **random**: Random number and dice rolling commands
- **youtube**: YouTube video search and integration

### Database

The database layer uses SQLAlchemy with async PostgreSQL:

- **models.py**: Defines `User`, `Menu`, and `YouTubeVideo` models
- **database.py**: Handles connections and session management

### Configuration

All configuration is managed through environment variables:

- `BOT_TOKEN`: Discord bot token
- `BOT_DESCRIPTION`: Bot description
- `DB_*`: Database connection parameters
- `YT_API_KEY`: YouTube API key
- `LOG_LEVEL`: Logging level (default: INFO)

## Development

### Setup

1. Install dependencies:
```bash
poetry install --with dev,test
```

2. Set up environment variables in `.env` file

3. Run the bot:
```bash
poetry run python -m asdana.main
```

### Testing

Run the test suite:
```bash
poetry run pytest tests/
```

### Code Quality

Check code with pylint:
```bash
poetry run pylint asdana/
```

Format code with black:
```bash
poetry run black asdana/
```

## Architecture Improvements

This project follows clean architecture principles:

1. **Separation of Concerns**: Core logic, configuration, and features are separated
2. **Modularity**: Each cog handles specific functionality independently
3. **Dependency Injection**: Configuration and dependencies are injected at runtime
4. **Testability**: Modular structure enables easy unit testing
5. **Maintainability**: Clear structure makes code easy to understand and modify

## License

See LICENSE file for details.
