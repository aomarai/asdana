"""
Contains commands and listeners related to guilds.
"""

from discord.ext import commands

def _get_guild_name(context: commands.Context) -> str:
    """
    Returns the name of the guild from the context.
    :param context: The context object containing the guild information.
    :type context: discord.ext.commands.Context
    :return: The name of the guild.
    :rtype: str
    """
    return context.guild.name


class Guild(commands.Cog):
    """
    Class containing commands and listeners related to guilds.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
