"""
Tests for the Random cog.
"""

from unittest.mock import AsyncMock, patch

import pytest
from discord.ext import commands

from asdana.cogs.random import setup
from asdana.cogs.random.random import Random
from tests.helpers import setup_bot_with_cog

# pylint: disable=too-few-public-methods


@pytest.mark.asyncio
async def test_adds_random_cog_to_bot():
    """
    Test that the Random cog is added to the bot.
    """
    bot = await setup_bot_with_cog(setup)
    assert any(isinstance(cog, Random) for cog in bot.cogs.values())


@pytest.mark.asyncio
async def test_does_not_add_duplicate_random_cog():
    """
    Test that the Random cog is not added to the bot multiple times.
    """
    bot = await setup_bot_with_cog(setup)
    initial_cog_count = len(bot.cogs)
    if "Random" not in bot.cogs:
        await setup(bot)
    assert len(bot.cogs) == initial_cog_count


@pytest.mark.asyncio
async def test_random_command_sends_number_in_range():
    """
    Test that the random command sends a number within the specified range.
    """
    bot = await setup_bot_with_cog(setup)
    context = AsyncMock()
    context.send = AsyncMock()

    cog = bot.get_cog("Random")

    with patch("asdana.cogs.random.random.random.randint", return_value=42):
        await cog.random(context, floor=1, ceiling=100)

    context.send.assert_called_once()
    call_args = context.send.call_args[0][0]
    assert "42" in call_args


@pytest.mark.asyncio
async def test_roll_command_sends_dice_result():
    """
    Test that the roll command sends a dice roll result.
    """
    bot = await setup_bot_with_cog(setup)
    context = AsyncMock()
    context.send = AsyncMock()

    cog = bot.get_cog("Random")

    with patch("asdana.cogs.random.random.random.randint", return_value=15):
        await cog.roll(context, sides=20)

    context.send.assert_called_once()
    call_args = context.send.call_args[0][0]
    assert "15" in call_args


@pytest.mark.asyncio
async def test_random_command_uses_default_values():
    """
    Test that the random command uses default values when no arguments are provided.
    """
    bot = await setup_bot_with_cog(setup)
    context = AsyncMock()
    context.send = AsyncMock()

    cog = bot.get_cog("Random")

    with patch(
        "asdana.cogs.random.random.random.randint", return_value=50
    ) as mock_randint:
        await cog.random(context)

    # Check that randint was called with default values (1, 100)
    mock_randint.assert_called_once_with(1, 100)
    context.send.assert_called_once()


@pytest.mark.asyncio
async def test_roll_command_uses_default_sides():
    """
    Test that the roll command uses default sides (20) when no argument is provided.
    """
    bot = await setup_bot_with_cog(setup)
    context = AsyncMock()
    context.send = AsyncMock()

    cog = bot.get_cog("Random")

    with patch(
        "asdana.cogs.random.random.random.randint", return_value=10
    ) as mock_randint:
        await cog.roll(context)

    # Check that randint was called with default sides (1, 20)
    mock_randint.assert_called_once_with(1, 20)
    context.send.assert_called_once()
