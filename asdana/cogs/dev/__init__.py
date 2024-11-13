"""
Primes the Dev cog for dynamic loading. Not intended (or most likely useful) for production use.
"""

from discord.ext import commands
from .dev import Dev


async def setup(bot: commands.Bot):
    """
    Adds the Guild cog to the bot.
    :param bot: The bot to add the cog to.
    :return: None
    """
    await bot.add_cog(Dev(bot))
