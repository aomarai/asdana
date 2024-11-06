from discord.ext import commands

class Guild(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super.__init__()
        self.bot = bot

    async def _get_guild_name(self, context):
        return context.guild

