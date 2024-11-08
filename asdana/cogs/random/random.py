"""
Random cog for managing random-based functionality.
"""

from discord.ext import commands


class Random(commands.Cog):
    """
    Provides commands and listeners for random-based functionality.
    """

    def __init__(self, bot):
        self.bot = bot
