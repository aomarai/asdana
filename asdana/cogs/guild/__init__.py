"""
Primes the Guild cog for dynamic loading.
"""

from discord.ext import commands
from .guild import Guild


async def setup(bot: commands.Bot):
    """
    Adds the Guild cog to the bot.
    :param bot: The bot to add the cog to.
    :return: None
    """
    await bot.add_cog(Guild(bot))
