import os
import discord

from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
bot_token = os.getenv("DISCORD_BOT_TOKEN")

description = """A simple test bot to try out the discord.py package"""

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot_cmd_client = commands.Bot(command_prefix='!', description=description, intents=intents)


async def _get_guild_name(context):
    """Fetches the name of the current guild"""
    return context.guild

@bot_cmd_client.event
async def on_ready():
    print(f'Logged into bot user {bot_cmd_client.user} (ID: {bot_cmd_client.user.id})')
    print('----------')

@bot_cmd_client.command()
async def member_joined(context, member: discord.Member):
    """Says when a member joined"""
    await context.send(f'{member.name} joined {discord.utils.format_dt(member.joined_at)}')

@bot_cmd_client.command()
async def add(context, first_num: float, second_num: float):
    """Adds two numbers together"""
    await context.send(first_num + second_num)

@bot_cmd_client.command(name='joined')
async def joined_at(context):
    """Print when the bot joined the server."""
    join_date = context.guild.me.joined_at.strftime('%Y-%m-%d %H:%M:%S UTC')
    await context.send(f'Asdana Bot joined {await _get_guild_name(context)} at {join_date}')

@bot_cmd_client.group()
async def cool(context):
    """Says if a user is cool.
       Really just checks if a subcommand is being run."""
    if context.invoked_subcommand is None:
        await context.send(f'No, {context.subcommand_passed} is not cool')

@cool.command(name='bot')
async def _bot(context):
    """Is the bot cool?"""
    await context.send('The bot is pretty damn cool.')


bot_cmd_client.run(bot_token)