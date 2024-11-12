"""
Members cog for managing... members. Crazy.
"""

import os

from discord.ext import commands

import asdana.database.database


class Members(commands.Cog):
    """
    Provides commands and listeners for managing members.
    """

    def __init__(self, bot):
        self.bot = bot
