"""
Tests for menu handlers module.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from asdana.cogs.menus.menu_handlers import (
    create_generic_handlers,
    create_paginated_handlers,
)


@pytest.mark.asyncio
async def test_create_paginated_handlers_creates_previous_and_next():
    """Test that create_paginated_handlers creates previous and next handlers."""
    message = MagicMock()
    message.embeds = [MagicMock()]
    message.embeds[0].title = "Test - Page 1/3"
    message.embeds[0].description = "Page content"
    message.id = 123

    menu_model = MagicMock()
    menu_model.data = {"pages": ["Page 1", "Page 2", "Page 3"]}
    menu_model.current_page = 0
    menu_model.discord_author_id = 456

    handlers = await create_paginated_handlers(message, menu_model)

    assert "⬅️" in handlers
    assert "➡️" in handlers
    assert callable(handlers["⬅️"])
    assert callable(handlers["➡️"])


@pytest.mark.asyncio
async def test_paginated_handler_next_updates_page():
    """Test that next page handler updates the current page."""
    message = MagicMock()
    message.embeds = [MagicMock()]
    message.embeds[0].title = "Test - Page 1/3"
    message.embeds[0].description = "Page 1"
    message.edit = AsyncMock()
    message.id = 123

    menu_model = MagicMock()
    menu_model.data = {"pages": ["Page 1", "Page 2", "Page 3"]}
    menu_model.current_page = 0
    menu_model.discord_author_id = 456

    user = MagicMock()
    user.id = 456

    with (
        patch("asdana.cogs.menus.menu_handlers.get_db_session") as mock_session,
        patch("asdana.cogs.menus.menu_handlers.select"),
    ):
        mock_db = AsyncMock()
        mock_session.return_value.__aenter__.return_value = mock_db

        mock_result = MagicMock()
        mock_menu = MagicMock()
        mock_menu.current_page = 0
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_menu)
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()

        handlers = await create_paginated_handlers(message, menu_model)
        await handlers["➡️"](user)

        # Verify page was updated
        assert message.embeds[0].description == "Page 2"
        message.edit.assert_called_once()


@pytest.mark.asyncio
async def test_paginated_handler_prevents_out_of_bounds():
    """Test that paginated handlers don't go out of bounds."""
    message = MagicMock()
    message.embeds = [MagicMock()]
    message.embeds[0].title = "Test"
    message.embeds[0].description = "Page 1"
    message.edit = AsyncMock()
    message.id = 123

    menu_model = MagicMock()
    menu_model.data = {"pages": ["Page 1", "Page 2"]}
    menu_model.current_page = 0
    menu_model.discord_author_id = 456

    user = MagicMock()
    user.id = 456

    with (
        patch("asdana.cogs.menus.menu_handlers.get_db_session") as mock_session,
        patch("asdana.cogs.menus.menu_handlers.select"),
    ):
        mock_db = AsyncMock()
        mock_session.return_value.__aenter__.return_value = mock_db

        mock_result = MagicMock()
        mock_menu = MagicMock()
        mock_menu.current_page = 0
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_menu)
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()

        handlers = await create_paginated_handlers(message, menu_model)

        # Try to go previous from first page - should not update
        initial_edit_count = message.edit.call_count
        await handlers["⬅️"](user)
        assert message.edit.call_count == initial_edit_count


@pytest.mark.asyncio
async def test_paginated_handler_checks_user_permission():
    """Test that paginated handlers only work for the menu author."""
    message = MagicMock()
    message.embeds = [MagicMock()]
    message.embeds[0].title = "Test"
    message.embeds[0].description = "Page 1"
    message.edit = AsyncMock()
    message.id = 123

    menu_model = MagicMock()
    menu_model.data = {"pages": ["Page 1", "Page 2"]}
    menu_model.current_page = 0
    menu_model.discord_author_id = 456

    wrong_user = MagicMock()
    wrong_user.id = 789  # Different from author

    handlers = await create_paginated_handlers(message, menu_model)
    await handlers["➡️"](wrong_user)

    # Page should not be updated for unauthorized user
    message.edit.assert_not_called()


@pytest.mark.asyncio
async def test_create_generic_handlers_for_confirm_menu():
    """Test that create_generic_handlers creates confirm and cancel handlers."""
    message = MagicMock()
    message.channel = MagicMock()
    message.channel.send = AsyncMock()

    menu_model = MagicMock()
    menu_model.menu_type = "confirm"
    menu_model.data = {"reactions": ["✅", "🚫"]}
    menu_model.discord_author_id = 456

    handlers = await create_generic_handlers(message, menu_model)

    assert "✅" in handlers
    assert "🚫" in handlers


@pytest.mark.asyncio
async def test_confirm_handler_sends_confirmation_message():
    """Test that confirm handler sends a confirmation message."""
    message = MagicMock()
    message.channel = MagicMock()
    message.channel.send = AsyncMock()

    menu_model = MagicMock()
    menu_model.menu_type = "confirm"
    menu_model.data = {"reactions": ["✅", "🚫"]}
    menu_model.discord_author_id = 456

    user = MagicMock()
    user.id = 456

    handlers = await create_generic_handlers(message, menu_model)
    await handlers["✅"](user)

    # Verify confirmation message was sent
    message.channel.send.assert_called_once()
    call_args = message.channel.send.call_args[0][0]
    assert "confirmed" in call_args.lower()


@pytest.mark.asyncio
async def test_cancel_handler_sends_cancellation_message():
    """Test that cancel handler sends a cancellation message."""
    message = MagicMock()
    message.channel = MagicMock()
    message.channel.send = AsyncMock()

    menu_model = MagicMock()
    menu_model.menu_type = "confirm"
    menu_model.data = {"reactions": ["✅", "🚫"]}
    menu_model.discord_author_id = 456

    user = MagicMock()
    user.id = 456

    handlers = await create_generic_handlers(message, menu_model)
    await handlers["🚫"](user)

    # Verify cancellation message was sent
    message.channel.send.assert_called_once()
    call_args = message.channel.send.call_args[0][0]
    assert "cancel" in call_args.lower()


@pytest.mark.asyncio
async def test_option_handlers_created_for_options_menu():
    """Test that option handlers are created for options menu."""
    message = MagicMock()
    message.channel = MagicMock()
    message.channel.send = AsyncMock()

    menu_model = MagicMock()
    menu_model.menu_type = "options"
    menu_model.data = {"reactions": ["1️⃣", "2️⃣", "3️⃣"]}
    menu_model.discord_author_id = 456

    handlers = await create_generic_handlers(message, menu_model)

    assert "1️⃣" in handlers
    assert "2️⃣" in handlers
    assert "3️⃣" in handlers
    assert len(handlers) == 3


@pytest.mark.asyncio
async def test_generic_handlers_check_user_permission():
    """Test that generic handlers only work for the menu author."""
    message = MagicMock()
    message.channel = MagicMock()
    message.channel.send = AsyncMock()

    menu_model = MagicMock()
    menu_model.menu_type = "confirm"
    menu_model.data = {"reactions": ["✅"]}
    menu_model.discord_author_id = 456

    wrong_user = MagicMock()
    wrong_user.id = 789

    handlers = await create_generic_handlers(message, menu_model)
    await handlers["✅"](wrong_user)

    # Should not send message for unauthorized user
    message.channel.send.assert_not_called()
