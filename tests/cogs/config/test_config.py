"""
Tests for the Config cog.
"""

from unittest.mock import AsyncMock, Mock, patch

import discord
import pytest
from sqlalchemy import select

from asdana.cogs.config import setup
from asdana.cogs.config.config import Config
from asdana.database.models import GuildSettings, CogSettings
from tests.helpers import setup_bot_with_cog

# pylint: disable=too-few-public-methods,protected-access


intents = discord.Intents.default()


@pytest.mark.asyncio
async def test_adds_config_cog_to_bot():
    """
    Test that the Config cog is added to the bot.
    """
    bot = await setup_bot_with_cog(setup)
    assert any(isinstance(cog, Config) for cog in bot.cogs.values())


@pytest.mark.asyncio
async def test_guild_settings_get_or_create():
    """
    Test that GuildSettings.get_or_create creates a new guild settings entry.
    """
    mock_session = AsyncMock()
    mock_result = Mock()
    mock_result.scalars.return_value.first.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()

    guild_id = 123456789

    guild_settings = await GuildSettings.get_or_create(mock_session, guild_id)

    assert guild_settings.guild_id == guild_id
    assert guild_settings.command_prefix == "!"
    assert guild_settings.admin_role_ids == []
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_cog_settings_get_cog_enabled_default():
    """
    Test that CogSettings.get_cog_enabled returns True when no setting exists.
    """
    mock_session = AsyncMock()
    mock_result = Mock()
    mock_result.scalars.return_value.first.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    is_enabled = await CogSettings.get_cog_enabled(mock_session, 123456789, "test_cog")

    assert is_enabled is True


@pytest.mark.asyncio
async def test_cog_settings_get_cog_enabled_true():
    """
    Test that CogSettings.get_cog_enabled returns True when cog is enabled.
    """
    mock_session = AsyncMock()
    mock_cog_setting = Mock()
    mock_cog_setting.enabled = True
    mock_result = Mock()
    mock_result.scalars.return_value.first.return_value = mock_cog_setting
    mock_session.execute = AsyncMock(return_value=mock_result)

    is_enabled = await CogSettings.get_cog_enabled(mock_session, 123456789, "test_cog")

    assert is_enabled is True


@pytest.mark.asyncio
async def test_cog_settings_get_cog_enabled_false():
    """
    Test that CogSettings.get_cog_enabled returns False when cog is disabled.
    """
    mock_session = AsyncMock()
    mock_cog_setting = Mock()
    mock_cog_setting.enabled = False
    mock_result = Mock()
    mock_result.scalars.return_value.first.return_value = mock_cog_setting
    mock_session.execute = AsyncMock(return_value=mock_result)

    is_enabled = await CogSettings.get_cog_enabled(mock_session, 123456789, "test_cog")

    assert is_enabled is False


class MockGuild:
    """
    A mock class to simulate a Discord guild.
    """

    def __init__(self, guild_id=123456789, name="Test Guild", owner_id=111111111):
        self.id = guild_id
        self.name = name
        self.owner_id = owner_id


class MockRole:
    """
    A mock class to simulate a Discord role.
    """

    def __init__(self, role_id=222222222, name="Admin"):
        self.id = role_id
        self.name = name
        self.mention = f"@{name}"


class MockUser:
    """
    A mock class to simulate a Discord user.
    """

    def __init__(self, user_id=111111111, name="TestUser", is_admin=False, roles=None):
        self.id = user_id
        self.name = name
        self.roles = roles or []
        self.guild_permissions = Mock()
        self.guild_permissions.administrator = is_admin
