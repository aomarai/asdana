from .guild import Guild
from discord.ext import commands


async def setup(bot: commands.Bot):
    await bot.add_cog(Guild(bot))
