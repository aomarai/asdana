"""
Tests for the core bot module.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from discord.ext import commands

from asdana.core.bot import AsdanaBot, get_prefix


@pytest.mark.asyncio
async def test_get_prefix_returns_default_prefixes():
    """Test that get_prefix returns default prefixes."""
    bot = MagicMock()
    message = MagicMock()
    message.guild = None  # DM context

    with patch("asdana.core.bot.commands.when_mentioned_or") as mock_when_mentioned:
        mock_when_mentioned.return_value = lambda b, m: ["!", "?", "$"]
        result = await get_prefix(bot, message)

        # Verify default prefixes are used
        mock_when_mentioned.assert_called_once()
        call_args = mock_when_mentioned.call_args[0]
        assert "!" in call_args
        assert "?" in call_args
        assert "$" in call_args


@pytest.mark.asyncio
async def test_get_prefix_with_custom_guild_prefix():
    """Test that get_prefix returns custom guild prefix from database."""
    bot = MagicMock()
    message = MagicMock()
    message.guild = MagicMock()
    message.guild.id = 123456

    # Mock database session and guild settings
    mock_session = AsyncMock()
    mock_guild_settings = MagicMock()
    mock_guild_settings.command_prefix = ">"

    with (
        patch("asdana.core.bot.get_session") as mock_get_session,
        patch(
            "asdana.core.bot.GuildSettings.get_or_create",
            return_value=mock_guild_settings,
        ) as mock_get_or_create,
        patch("asdana.core.bot.commands.when_mentioned_or") as mock_when_mentioned,
    ):
        mock_get_session.return_value.__aenter__.return_value = mock_session
        mock_when_mentioned.return_value = lambda b, m: [">", "!", "?", "$"]

        result = await get_prefix(bot, message)

        # Verify custom prefix is included
        mock_get_or_create.assert_called_once_with(mock_session, 123456)
        mock_when_mentioned.assert_called_once()
        call_args = mock_when_mentioned.call_args[0]
        assert ">" in call_args  # Custom prefix
        assert "!" in call_args  # Default prefixes
        assert "?" in call_args
        assert "$" in call_args


@pytest.mark.asyncio
async def test_get_prefix_handles_database_error():
    """Test that get_prefix falls back to defaults on database error."""
    bot = MagicMock()
    message = MagicMock()
    message.guild = MagicMock()
    message.guild.id = 123456

    with (
        patch(
            "asdana.core.bot.get_session", side_effect=RuntimeError("Database error")
        ),
        patch("asdana.core.bot.commands.when_mentioned_or") as mock_when_mentioned,
    ):
        mock_when_mentioned.return_value = lambda b, m: ["!", "?", "$"]

        result = await get_prefix(bot, message)

        # Should fall back to default prefixes
        mock_when_mentioned.assert_called()
        call_args = mock_when_mentioned.call_args[0]
        assert "!" in call_args
        assert "?" in call_args
        assert "$" in call_args


@pytest.mark.asyncio
async def test_asdana_bot_initialization():
    """Test that AsdanaBot initializes correctly."""
    import discord

    web_client = MagicMock()
    testing_guild_id = 123456

    intents = discord.Intents.default()

    bot = AsdanaBot(
        web_client=web_client,
        testing_guild_id=testing_guild_id,
        command_prefix="!",
        intents=intents,
    )

    assert bot.web_client == web_client
    assert bot.testing_guild_id == testing_guild_id


@pytest.mark.asyncio
async def test_asdana_bot_loads_cogs():
    """Test that AsdanaBot loads cogs from the cogs directory."""
    import discord

    web_client = MagicMock()
    intents = discord.Intents.default()

    bot = AsdanaBot(
        web_client=web_client,
        testing_guild_id=None,
        command_prefix="!",
        intents=intents,
    )

    # Mock load_extension
    bot.load_extension = AsyncMock()

    with patch("os.walk") as mock_walk, patch("os.path.basename") as mock_basename:
        # Simulate finding a cog directory
        mock_walk.return_value = [
            ("/fake/path/cogs", [], []),  # Root cogs dir (skipped)
            ("/fake/path/cogs/test_cog", [], ["__init__.py", "test_cog.py"]),
        ]
        mock_basename.return_value = "test_cog"

        await bot.load_cogs()

        # Verify load_extension was called
        bot.load_extension.assert_called_once_with("asdana.cogs.test_cog")


@pytest.mark.asyncio
async def test_asdana_bot_handles_cog_load_failure():
    """Test that AsdanaBot handles cog loading failures gracefully."""
    import discord

    web_client = MagicMock()
    intents = discord.Intents.default()

    bot = AsdanaBot(
        web_client=web_client,
        testing_guild_id=None,
        command_prefix="!",
        intents=intents,
    )

    # Mock load_extension to raise an error
    bot.load_extension = AsyncMock(side_effect=commands.ExtensionNotFound("test"))

    with patch("os.walk") as mock_walk, patch("os.path.basename") as mock_basename:
        mock_walk.return_value = [
            ("/fake/path/cogs", [], []),
            ("/fake/path/cogs/test_cog", [], ["__init__.py"]),
        ]
        mock_basename.return_value = "test_cog"

        # Should not raise an exception
        await bot.load_cogs()


@pytest.mark.asyncio
async def test_asdana_bot_setup_hook_loads_cogs():
    """Test that setup_hook calls load_cogs."""
    import discord

    web_client = MagicMock()
    intents = discord.Intents.default()

    bot = AsdanaBot(
        web_client=web_client,
        testing_guild_id=None,
        command_prefix="!",
        intents=intents,
    )

    bot.load_cogs = AsyncMock()

    await bot.setup_hook()

    bot.load_cogs.assert_called_once()
