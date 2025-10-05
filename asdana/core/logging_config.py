"""
Logging configuration for the Asdana bot.
"""

import logging
import logging.handlers

import discord.utils


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configures logging for the Discord bot.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """
    discord_logger = logging.getLogger("discord")
    discord_logger.setLevel(log_level)

    handler = logging.handlers.RotatingFileHandler(
        filename="discord.log",
        encoding="utf-8",
        maxBytes=32 * 1024 * 1024,  # 32 MB
        backupCount=5,
    )
    dt_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(
        "[{asctime}] [{levelname:<8}] {name}: {message}", dt_format, style="{"
    )
    handler.setFormatter(formatter)
    discord.utils.setup_logging(
        handler=handler, formatter=formatter, level=log_level, root=True
    )
