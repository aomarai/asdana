from discord.ext import commands


def _get_guild_name(context):
    return context.guild.name


class Guild(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="serverowner")
    async def list_owner(self, context):
        guild = context.guild
        if guild:
            owner = guild.owner
            await context.send(
                f"The owner of the {_get_guild_name(context)} server is {owner}."
            )
        else:
            await context.send("This command must be used in a server.")
