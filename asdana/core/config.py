"""
Configuration management for the Asdana bot.
"""

import os
from typing import Optional

from dotenv import load_dotenv


class Config:
    """
    Configuration holder for bot settings loaded from environment variables.
    """

    def __init__(self):
        """Initialize configuration from environment variables."""
        load_dotenv()

        # Bot configuration
        self.bot_token: Optional[str] = os.getenv("BOT_TOKEN")
        self.bot_description: Optional[str] = os.getenv("BOT_DESCRIPTION")
        self.testing_guild_id: Optional[str] = os.getenv("TESTING_GUILD_ID")

        # Logging configuration
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")

        # Database configuration
        self.db_name: Optional[str] = os.getenv("DB_NAME")
        self.db_user: Optional[str] = os.getenv("DB_USER")
        self.db_password: Optional[str] = os.getenv("DB_PASSWORD")
        self.db_host: Optional[str] = os.getenv("DB_HOST")
        self.db_port: Optional[str] = os.getenv("DB_PORT")

        # API keys
        self.youtube_api_key: Optional[str] = os.getenv("YT_API_KEY")

    @property
    def database_url(self) -> str:
        """
        Constructs the database URL from configuration.

        Returns:
            str: PostgreSQL connection URL for asyncpg.
        """
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


# Global configuration instance
config = Config()
