"""
Main entry point for the bot. This file is responsible for setting up the bot and running it.
"""

import asyncio
import logging
import logging.handlers
import os
from typing import Optional

import discord
import discord.utils
from typing_extensions import override

from discord.ext import commands
from dotenv import load_dotenv
from aiohttp import ClientSession

from asdana.database.database import create_tables

logger = logging.getLogger(__name__)


def get_prefix(bot: commands.Bot, message: discord.Message) -> list[str]:
    """
    Returns the bot's command prefix based on the message.
    :param bot: The bot.
    :param message: The message.
    :return: The command prefix.
    """
    prefixes = ["!", "?", "$"]
    return commands.when_mentioned_or(*prefixes)(bot, message)


class AsdanaBot(commands.Bot):
    """
    The main bot class for Asdana.
    """

    def __init__(
        self,
        *args,
        web_client: ClientSession,
        testing_guild_id: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.web_client = web_client
        self.testing_guild_id = testing_guild_id

    async def load_cogs(self):
        """
        Dynamically loads all cogs in the cogs directory into the bot.
        :return: None
        """
        logger.info("Attempting to load cogs.")
        cogs_dir = os.path.join(os.path.dirname(__file__), "cogs")

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
                except Exception as e:
                    logger.error(
                        "❌ Failed to load cog %s: %s: %s",
                        module_path,
                        type(e).__name__,
                        e,
                    )

        logger.info("Finished cog loading process.")

    async def unload_cogs(self):
        """
        Unloads all cogs.
        :return: None
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
        :return:
        """
        await self.load_cogs()


async def main():
    """
    Main entry point for the bot.
    :return: None
    """
    # Load required environment variables
    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    description = os.getenv("BOT_DESCRIPTION")
    log_level = os.getenv("LOG_LEVEL", "INFO")

    discord_logger = logging.getLogger("discord")
    discord_logger.setLevel(log_level)

    handler = logging.handlers.RotatingFileHandler(
        filename="discord.log",
        encoding="utf-8",
        maxBytes=32 * 1024 * 1024,
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

    async with ClientSession() as web_client:
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True

        async with AsdanaBot(
            web_client=web_client,
            testing_guild_id=os.getenv("TESTING_GUILD_ID"),
            description=description,
            intents=intents,
            command_prefix=get_prefix,
        ) as bot:
            await create_tables()
            await bot.start(token)


asyncio.run(main())
