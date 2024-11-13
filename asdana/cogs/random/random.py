"""
Random cog for managing random-based functionality.
"""

import random

from discord.ext import commands


class Random(commands.Cog):
    """
    Provides commands and listeners for random-based functionality.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="random", aliases=["rand"])
    async def random(
        self, context: commands.Context, floor: int = 1, ceiling: int = 100
    ):
        """
        Generates a random number from a given floor to a given ceiling.
        Floor defaults to 1 and ceiling defaults to 100.
        :param context: The context of the command.
        :type context: commands.Context
        :param floor: The lower bound of the random number.
        :type floor: int
        :param ceiling: The upper bound of the random number.
        :type ceiling: int
        :return: None
        """
        await context.send(
            f"Your random number is: **{random.randint(floor, ceiling)}**!"
        )

    @commands.command(name="roll", aliases=["dice"])
    async def roll(self, context: commands.Context, sides: int = 20):
        """
        Rolls a die with a given number of sides.
        :param context: The context of the command.
        :param sides: The number of sides on the die. Defaults to 20.
        :return: None
        """
        await context.send(f"You rolled a **{random.randint(1, sides)}**!")

    @commands.command(name="vroulette", aliases=["vr"])
    async def random_yt_video(self, context: commands.Context):
        """
        Selects a random video from YouTube via the YouTube API.
        :param context: The context of the command.
        :return: None
        """
