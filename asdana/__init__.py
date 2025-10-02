"""
Asdana - A powerful, highly customizable Discord bot.

This package contains the main bot application and its components.

Main modules:
    core: Core bot functionality, configuration, and logging.
    cogs: Bot command extensions organized by functionality.
    database: Database models and connection management.
    utils: Utility classes and helpers.
"""

__version__ = "0.1.0"
__author__ = "Ash Omaraie"

from asdana.core import AsdanaBot, config, get_prefix, setup_logging

__all__ = [
    "AsdanaBot",
    "config",
    "get_prefix",
    "setup_logging",
]
