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

    @commands.command(name="owner")
    async def list_owner(self, context: commands.Context):
        """
        Sends a message with the owner of the guild.
        :param context: The context object containing the guild information.
        :type context: discord.ext.commands.Context
        :return: None
        """
        guild = context.guild
        if guild:
            owner = guild.owner
            await context.send(
                f"The owner of the {_get_guild_name(context)} server is {owner}."
            )
        else:
            await context.send("This command must be used in a server.")
