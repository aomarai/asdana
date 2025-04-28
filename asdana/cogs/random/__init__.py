"""
Primes the Random cog for dynamic loading.
"""

from discord.ext import commands
from asdana.cogs.random.random import Random


async def setup(bot: commands.Bot):
    """
    Adds the Members cog to the bot.
    :param bot: The bot to add the cog to.
    :type bot: commands.Bot
    :return: None
    """
    await bot.add_cog(Random(bot))
