"""
Primes the YouTube cog for dynamic loading.
"""

from discord.ext import commands
from .youtube import YouTube


async def setup(bot: commands.Bot):
    """
    Adds the YouTube cog to the bot.
    :param bot: The bot to add the cog to.
    :type bot: commands.Bot
    :return: None
    """
    await bot.add_cog(YouTube(bot, db_pool=bot.db_pool))
