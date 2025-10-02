"""
The main Asdana bot class and prefix configuration.
"""

import logging
import os
from typing import Optional

import discord
from aiohttp import ClientSession
from discord.ext import commands
from typing_extensions import override

logger = logging.getLogger(__name__)


def get_prefix(bot: commands.Bot, message: discord.Message) -> list[str]:
    """
    Returns the bot's command prefix based on the message.

    Args:
        bot: The bot instance.
        message: The message to get the prefix for.

    Returns:
        List of valid command prefixes for this message.
    """
    prefixes = ["!", "?", "$"]
    return commands.when_mentioned_or(*prefixes)(bot, message)


class AsdanaBot(commands.Bot):
    """
    The main bot class for Asdana.

    This extends discord.py's Bot class with custom functionality for
    loading/unloading cogs and managing bot state.

    Attributes:
        web_client: Aiohttp client session for making HTTP requests.
        testing_guild_id: Optional guild ID for testing slash commands.
    """

    def __init__(
        self,
        *args,
        web_client: ClientSession,
        testing_guild_id: Optional[int] = None,
        **kwargs,
    ):
        """
        Initialize the Asdana bot.

        Args:
            web_client: Aiohttp client session for HTTP requests.
            testing_guild_id: Optional guild ID for testing.
            *args: Additional positional arguments for commands.Bot.
            **kwargs: Additional keyword arguments for commands.Bot.
        """
        super().__init__(*args, **kwargs)
        self.web_client = web_client
        self.testing_guild_id = testing_guild_id

    async def load_cogs(self):
        """
        Dynamically loads all cogs in the cogs directory into the bot.
        """
        logger.info("Attempting to load cogs.")
        cogs_dir = os.path.join(os.path.dirname(__file__), "..", "cogs")

        logger.debug("Looking for cogs in: %s", os.path.abspath(cogs_dir))

        for root, _, files in os.walk(cogs_dir):
            logger.debug("Checking directory: %s", root)
            if root == cogs_dir:  # Skip the root cogs directory
                continue
            if "__init__.py" in files:
                # Get just the subdirectory name (e.g., 'guild')
                cog_name = os.path.basename(root)
                # Create the absolute import path
                module_path = f"asdana.cogs.{cog_name}"

                logger.debug("Attempting to load: %s", module_path)
                try:
                    await self.load_extension(module_path)
                    logger.info("✅ Successfully loaded cog: %s", module_path)
                except (
                    commands.ExtensionNotFound,
                    commands.ExtensionFailed,
                    commands.NoEntryPointError,
                ) as e:
                    logger.error(
                        "❌ Failed to load cog %s: %s: %s",
                        module_path,
                        type(e).__name__,
                        e,
                    )

        logger.info("Finished cog loading process.")

    async def unload_cogs(self):
        """
        Unloads all currently loaded cogs.
        """
        logger.warning("Deactivation of all cogs requested. Unloading all cogs.")
        for cog in self.cogs:
            try:
                await self.unload_extension(f"cogs.{cog}")
                logger.info("Unloaded Cog %s", cog)
            except commands.ExtensionNotLoaded as e:
                logger.error("Failed to unload Cog %s: %s", cog, e)

    @override
    async def setup_hook(self) -> None:
        """
        Performs setup tasks for the bot.

        This is called automatically by discord.py before the bot connects.
        """
        await self.load_cogs()
