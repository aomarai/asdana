"""
Core bot functionality and configuration.

This package contains the core components for running the Asdana Discord bot.

Modules:
    bot: Main bot class and prefix configuration.
    config: Configuration management from environment variables.
    logging_config: Logging setup and configuration.
"""

from asdana.core.bot import AsdanaBot, get_prefix
from asdana.core.config import Config, config
from asdana.core.logging_config import setup_logging

__all__ = [
    "AsdanaBot",
    "Config",
    "config",
    "get_prefix",
    "setup_logging",
]
