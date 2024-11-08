"""
Main entry point for the bot. Responsible for loading cogs and starting the bot.
"""

import os
import discord

from discord.ext import commands
from dotenv import load_dotenv

BOT_NAME = "asdana"

# Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
DESCRIPTION = os.getenv("BOT_DESCRIPTION")

# Get the necessary intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Create the bot instance
bot = commands.Bot(
    command_prefix=["!", "?", "$"],
    intents=intents,
    description=DESCRIPTION,
    case_insensitive=True,
)


async def load_cogs():
    """
    Dynamically loads all cogs in the cogs directory.
    :return: None
    """
    cogs_dir = os.path.join("cogs")
    for root, _, files in os.walk(cogs_dir):
        if root == "cogs":
            continue

        if "__init__.py" in files:
            cog_path = root.replace(os.path.sep, ".")
            try:
                await bot.load_extension(cog_path)
                print(f"Loaded Cog {cog_path[5:]}")
            except (commands.ExtensionNotLoaded, commands.ExtensionAlreadyLoaded) as e:
                print(f"Failed to load Cog {cog_path[5:]}: {e}")


async def unload_cogs():
    """
     Unloads all currently active cogs on the bot.
    :return: None
    """
    for cog in bot.cogs:
        try:
            await bot.unload_extension(f"cogs.{cog}")
            print(f"Unloaded Cog {cog}")
        except (commands.ExtensionNotLoaded, commands.ExtensionNotLoaded) as e:
            print(f"Failed to unload Cog {cog}: {e}")


# Start the bot instance
@bot.event
async def on_ready():
    """
    Event handler for when the bot is ready.
    :return: None
    """
    await load_cogs()
    print(f"Logged into bot user {bot.user} (ID: {bot.user.id})")
    print("----------")


bot.run(TOKEN)
