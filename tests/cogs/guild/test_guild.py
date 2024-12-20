"""
Tests for the Guild cog.
"""

from unittest.mock import AsyncMock, Mock
import pytest
import discord
from discord.ext import commands
from asdana.cogs.guild.guild import Guild, _get_guild_name
from asdana.cogs.guild import setup
from tests.helpers import setup_bot_with_cog

# pylint: disable=too-few-public-methods

# Define the default intents for the bot
intents = discord.Intents.default()


@pytest.mark.asyncio
async def test_adds_guild_cog_to_bot():
    """
    Test that the Guild cog is added to the bot.
    """
    bot = await setup_bot_with_cog(setup)
    assert any(isinstance(cog, Guild) for cog in bot.cogs.values())


@pytest.mark.asyncio
async def test_does_not_add_duplicate_guild_cog():
    """
    Test that the Guild cog is not added to the bot multiple times.
    """
    bot = await setup_bot_with_cog(setup)
    initial_cog_count = len(bot.cogs)
    if "Guild" not in bot.cogs:
        await setup(bot)
    assert len(bot.cogs) == initial_cog_count


@pytest.mark.asyncio
async def test_sends_owner_name_when_guild_exists():
    """
    Test that the `list_owner` method sends the owner's name when the guild exists.
    """
    bot = commands.Bot(command_prefix="!", intents=intents)
    await bot.add_cog(Guild(bot))
    context = AsyncMock()
    context.guild = MockGuild(name="MockGuild", owner="OwnerName")
    context.send = AsyncMock()
    command = bot.get_command("owner")
    await command.invoke(context)
    context.send.assert_called_with("The owner of the MockGuild server is OwnerName.")


@pytest.mark.asyncio
async def test_sends_error_message_when_no_guild():
    """
    Test that the `list_owner` method sends an error message when no guild is present.
    """
    bot = commands.Bot(command_prefix="!", intents=intents)
    await bot.add_cog(Guild(bot))
    context = AsyncMock()
    context.guild = MockGuild(name="MockGuild", owner="OwnerName")
    context.send = AsyncMock()
    command = bot.get_command("owner")
    await command.invoke(context)
    context.send.assert_called_with("The owner of the MockGuild server is OwnerName.")


def test_returns_guild_name():
    """
    Test that the `_get_guild_name` function returns the correct guild name.
    """
    context = Mock()
    context.guild = MockGuild(name="MockGuild")
    assert _get_guild_name(context) == "MockGuild"


class MockGuild:
    """
    A mock class to simulate a Discord guild.

    Attributes:
        name (str): The name of the guild.
        owner (str): The owner of the guild.
    """

    def __init__(self, name=None, owner=None):
        self.name = name
        self.owner = owner
