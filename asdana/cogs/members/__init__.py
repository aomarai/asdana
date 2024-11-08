"""
Primes the Members cog for dynamic loading.
"""

from discord.ext import commands
from .members import Members


async def setup(bot: commands.Bot):
    """
    Adds the Members cog to the bot.
    :param bot: The bot to add the cog to.
    :type bot: commands.Bot
    :return: None
    """
    await bot.add_cog(Members(bot))
