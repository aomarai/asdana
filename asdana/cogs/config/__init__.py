"""
Primes the Config cog for dynamic loading.
"""

from discord.ext import commands
from asdana.cogs.config.config import Config


async def setup(bot: commands.Bot):
    """
    Adds the Config cog to the bot.
    :param bot: The bot to add the cog to.
    :type bot: commands.Bot
    :return: None
    """
    await bot.add_cog(Config(bot))
