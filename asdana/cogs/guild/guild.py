"""
Contains commands and listeners related to guilds.
"""

from discord.ext import commands
from asdana.utils.menu_factory import MenuFactory


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

    @commands.command(name="menu", aliases=["m"])
    async def example_menu(self, context: commands.Context):
        """
        Creates an example menu
        """

        async def on_confirm(user):
            if user.id == context.author.id:
                await context.send(f"{user.mention} confirmed the action!")

        await MenuFactory.create_confirm_menu(
            context=context,
            title="Example confirmation",
            description="Would you like to proceed?",
            on_confirm=on_confirm,
        )
