"""
Main entry point for the bot. This file is responsible for setting up the bot and running it.
"""

import asyncio
import logging
import logging.handlers
import os
from typing import Optional

import asyncpg
import discord
import discord.utils
from typing_extensions import override

from discord.ext import commands
from dotenv import load_dotenv
from aiohttp import ClientSession
from asdana.postgres.connection import PostgresConnection


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
        db_pool: asyncpg.Pool,
        web_client: ClientSession,
        testing_guild_id: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.db_pool = db_pool
        self.web_client = web_client
        self.testing_guild_id = testing_guild_id

    async def load_cogs(self):
        """
        Dynamically loads all cogs in the cogs directory into the bot.
        :return: None
        """
        cogs_dir = os.path.join("cogs")
        for root, _, files in os.walk(cogs_dir):
            if root == "cogs":
                continue
            if "__init__.py" in files:
                cog_path = root.replace(os.path.sep, ".")
                try:
                    await self.load_extension(cog_path)
                    print(f"Loaded Cog {cog_path[5:]}")
                except (
                    commands.ExtensionNotLoaded,
                    commands.ExtensionAlreadyLoaded,
                ) as e:
                    print(f"Failed to load Cog {cog_path[5:]}: {e}")

    async def unload_cogs(self):
        """
        Unloads all cogs.
        :return: None
        """
        for cog in self.cogs:
            try:
                await self.unload_extension(f"cogs.{cog}")
                print(f"Unloaded Cog {cog}")
            except (commands.ExtensionNotLoaded, commands.ExtensionNotLoaded) as e:
                print(f"Failed to unload Cog {cog}: {e}")

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
    pg_kwargs = {
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
    }

    logger = logging.getLogger("discord")
    logger.setLevel(logging.INFO)

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
        handler=handler, formatter=formatter, level=logging.INFO, root=True
    )

    async with (
        ClientSession() as web_client,
        PostgresConnection(**pg_kwargs) as db_pool,
    ):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True

        async with AsdanaBot(
            db_pool=db_pool,
            web_client=web_client,
            testing_guild_id=os.getenv("TESTING_GUILD_ID"),
            description=description,
            intents=intents,
            command_prefix=get_prefix,
        ) as bot:
            await bot.start(token)


asyncio.run(main())
