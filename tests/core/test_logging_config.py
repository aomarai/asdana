"""
Tests for the core logging configuration module.
"""

import logging
from unittest.mock import MagicMock, patch

from asdana.core.logging_config import setup_logging


def test_setup_logging_configures_discord_logger():
    """Test that setup_logging configures the discord logger."""
    with (
        patch("logging.getLogger") as mock_get_logger,
        patch("logging.handlers.RotatingFileHandler") as mock_handler,
        patch("discord.utils.setup_logging") as mock_discord_setup,
    ):
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        setup_logging("INFO")

        # Verify logger was configured
        mock_get_logger.assert_called_once_with("discord")
        mock_logger.setLevel.assert_called_once_with("INFO")

        # Verify handler was created
        mock_handler.assert_called_once()

        # Verify discord.utils.setup_logging was called
        mock_discord_setup.assert_called_once()


def test_setup_logging_with_debug_level():
    """Test that setup_logging accepts DEBUG level."""
    with (
        patch("logging.getLogger") as mock_get_logger,
        patch("logging.handlers.RotatingFileHandler"),
        patch("discord.utils.setup_logging"),
    ):
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        setup_logging("DEBUG")

        mock_logger.setLevel.assert_called_once_with("DEBUG")


def test_setup_logging_creates_rotating_file_handler():
    """Test that setup_logging creates a rotating file handler with correct settings."""
    with (
        patch("logging.getLogger"),
        patch("logging.handlers.RotatingFileHandler") as mock_handler,
        patch("discord.utils.setup_logging"),
    ):
        setup_logging("INFO")

        # Verify handler was created with correct parameters
        mock_handler.assert_called_once_with(
            filename="discord.log",
            encoding="utf-8",
            maxBytes=32 * 1024 * 1024,  # 32 MB
            backupCount=5,
        )


def test_setup_logging_formats_log_messages_correctly():
    """Test that setup_logging sets up the log formatter correctly."""
    with (
        patch("logging.getLogger"),
        patch("logging.handlers.RotatingFileHandler") as mock_handler_class,
        patch("discord.utils.setup_logging"),
        patch("logging.Formatter") as mock_formatter,
    ):
        mock_handler = MagicMock()
        mock_handler_class.return_value = mock_handler

        setup_logging("INFO")

        # Verify formatter was created with correct format
        mock_formatter.assert_called_once()
        call_args = mock_formatter.call_args[0]
        assert "{asctime}" in call_args[0]
        assert "{levelname:<8}" in call_args[0]
        assert "{name}" in call_args[0]
        assert "{message}" in call_args[0]

        # Verify formatter was set on handler
        mock_handler.setFormatter.assert_called_once()
