"""
Development cog for Asdana. Not intended (or most likely useful) for production use.
"""

from discord.ext import commands
import os
from asdana.database.database import get_selected_cogs


class Dev(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="ginfo")
    async def guild_info(self, context: commands.Context):
        guild = context.guild
        await context.send(
            f"Name: {guild.name}\nID: {guild.id}\nOwner: {guild.owner}\nMember Count: {guild.member_count}"
        )

    @commands.command(name="dbtest")
    async def dbtest(self, context: commands.Context):
        selected_cogs = await get_selected_cogs(int(os.getenv("TESTING_GUILD_ID")))
        print(f"selected_cogs: {selected_cogs}")  # Debug print
        await context.send(f"selected_cogs: {selected_cogs}")
