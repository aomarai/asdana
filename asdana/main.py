import discord
import os

from discord.ext import commands
from dotenv import load_dotenv

BOT_NAME = 'asdana'

# Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
DESCRIPTION = os.getenv("BOT_DESCRIPTION")

# Get the necessary intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Create the bot instance
bot = commands.Bot(command_prefix=['!', '?', '$'], intents=intents, description=DESCRIPTION, case_insensitive=True)

# Dynamically load available cogs
async def load_cogs():
    for root, _, files in os.walk('/cogs'):
        if '__init__.py' in files:
            cog_path = root.replace("/", ".").replace("\\", ".")
            try:
                await bot.load_extension(cog_path)
                print(f'Loaded Cog {cog_path}')
            except Exception as e:
                print(f'Failed to load Cog {cog_path}: {e}')

# Start the bot instance
@bot.event
async def on_ready():
    await load_cogs()
    print(f'Logged into bot user {bot.user} (ID: {bot.user.id})')
    print('----------')

bot.run(TOKEN)
