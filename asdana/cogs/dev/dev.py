"""
Development cog for Asdana. Not intended (or most likely useful) for production use.
"""

from discord.ext import commands


class Dev(commands.Cog):
    """
    Development cog for Asdana. Not intended (or most likely useful) for production use.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="ginfo")
    async def guild_info(self, context: commands.Context):
        """
        Displays information about the guild the command was run in.
        :param context: The context of the command.
        :type context: commands.Context
        :return: None
        """
        guild = context.guild
        await context.send(
            f"Name: {guild.name}\n"
            f"ID: {guild.id}\n"
            f"Owner: {guild.owner}"
            f"\nMember Count: {guild.member_count}"
        )
