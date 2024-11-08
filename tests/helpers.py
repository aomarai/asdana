"""
Contains helper functions for tests.
"""

import discord
from discord.ext import commands

# Define the default intents for the bot
intents = discord.Intents.default()


async def setup_bot_with_cog(setup_func):
    """
    Helper function to set up a bot and add a cog to it.

    Args:
        setup_func (function): The setup function to add the cog to the bot.

    Returns:
        commands.Bot: The bot instance with the cog added.
    """
    bot = commands.Bot(command_prefix="!", intents=intents)
    await setup_func(bot)
    return bot
