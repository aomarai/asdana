"""
Tests for the core configuration module.
"""

import os
from unittest.mock import patch

import pytest

from asdana.core.config import Config


def test_config_loads_environment_variables():
    """Test that Config loads environment variables correctly."""
    with patch.dict(
        os.environ,
        {
            "BOT_TOKEN": "test_token_123",
            "BOT_DESCRIPTION": "Test Description",
            "TESTING_GUILD_ID": "123456789",
            "LOG_LEVEL": "DEBUG",
            "DB_NAME": "test_db",
            "DB_USER": "test_user",
            "DB_PASSWORD": "test_pass",
            "DB_HOST": "test_host",
            "DB_PORT": "5432",
            "YT_API_KEY": "test_yt_key",
        },
    ):
        config = Config()

        assert config.bot_token == "test_token_123"
        assert config.bot_description == "Test Description"
        assert config.testing_guild_id == 123456789
        assert config.log_level == "DEBUG"
        assert config.db_name == "test_db"
        assert config.db_user == "test_user"
        assert config.db_password == "test_pass"
        assert config.db_host == "test_host"
        assert config.db_port == "5432"
        assert config.youtube_api_key == "test_yt_key"


def test_config_uses_default_log_level():
    """Test that Config uses default log level when not set."""
    with patch.dict(os.environ, {}, clear=True):
        config = Config()
        assert config.log_level == "INFO"


def test_config_database_url_construction():
    """Test that database URL is constructed correctly."""
    with patch.dict(
        os.environ,
        {
            "DB_USER": "myuser",
            "DB_PASSWORD": "mypass",
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "DB_NAME": "mydb",
        },
    ):
        config = Config()
        expected_url = "postgresql+asyncpg://myuser:mypass@localhost:5432/mydb"
        assert config.database_url == expected_url


def test_config_handles_missing_optional_values():
    """Test that Config handles missing optional environment variables."""
    with patch.dict(os.environ, {}, clear=True):
        config = Config()

        # Optional values should be None
        assert config.bot_token is None
        assert config.bot_description is None
        assert config.testing_guild_id is None
        assert config.db_name is None
        assert config.youtube_api_key is None

        # Required with defaults
        assert config.log_level == "INFO"
