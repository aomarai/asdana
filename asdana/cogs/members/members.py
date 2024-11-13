"""
Members cog for managing... members. Crazy.
"""

from discord.ext import commands


class Members(commands.Cog):
    """
    Provides commands and listeners for managing members.
    """

    def __init__(self, bot):
        self.bot = bot
