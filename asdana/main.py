"""
Main entry point for the bot.

This module initializes and runs the Asdana Discord bot.
"""

import asyncio

import discord
from aiohttp import ClientSession

from asdana.core.bot import AsdanaBot, get_prefix
from asdana.core.config import config
from asdana.core.logging_config import setup_logging
from asdana.database.database import create_tables


async def main():
    """
    Main entry point for the bot.

    Sets up logging, initializes the bot with configuration,
    creates database tables, and starts the bot.
    """
    # Setup logging
    setup_logging(config.log_level)

    # Create aiohttp session for web requests
    async with ClientSession() as web_client:
        # Configure Discord intents
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True

        # Initialize and run the bot
        async with AsdanaBot(
            web_client=web_client,
            testing_guild_id=config.testing_guild_id,
            description=config.bot_description,
            intents=intents,
            command_prefix=get_prefix,
        ) as bot:
            await create_tables()
            await bot.start(config.bot_token)


if __name__ == "__main__":
    asyncio.run(main())
