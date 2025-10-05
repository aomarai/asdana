"""
Primes the Reaction Menu cog for dynamic loading.
"""

from discord.ext import commands
from asdana.cogs.menus.reaction_menu import ReactionMenu


async def setup(bot: commands.Bot):
    """
    Adds the ReactionMenu cog to the bot.
    :param bot: The bot to add the cog to.
    :type bot: commands.Bot
    :return: None
    """
    await bot.add_cog(ReactionMenu(bot))
