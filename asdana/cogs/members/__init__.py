from .members import Members
from discord.ext import commands


async def setup(bot: commands.Bot):
    await bot.add_cog(Members(bot))
