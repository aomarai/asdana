"""
Tests for the Members cog.
"""

import pytest
from asdana.cogs.members import setup, Members
from tests.helpers import setup_bot_with_cog

# pylint: disable=too-few-public-methods


@pytest.mark.asyncio
async def test_adds_members_cog_to_bot():
    """
    Test that the Members cog is added to the bot.
    """
    bot = await setup_bot_with_cog(setup)
    assert any(isinstance(cog, Members) for cog in bot.cogs.values())


@pytest.mark.asyncio
async def test_does_not_add_duplicate_members_cog():
    """
    Test that the Members cog is not added to the bot multiple times.
    """
    bot = await setup_bot_with_cog(setup)
    initial_cog_count = len(bot.cogs)
    if 'Members' not in bot.cogs:
        await setup(bot)
    assert len(bot.cogs) == initial_cog_count
