"""
Menu handler functions for different types of reaction menus.

This module contains helper functions to create reaction handlers
for various menu types (paginated, confirm, options).
"""

import logging

import discord
from sqlalchemy import select

from asdana.database.database import get_session as get_db_session
from asdana.database.models import Menu

logger = logging.getLogger(__name__)


async def create_paginated_handlers(message: discord.Message, menu_model: Menu) -> dict:
    """
    Create handlers for paginated menus loaded from the database.

    Args:
        message: The Discord message containing the menu.
        menu_model: The menu database model.

    Returns:
        Dictionary mapping emoji to handler functions.
    """
    reaction_handlers = {}

    menu_data = menu_model.data
    pages = menu_data.get("pages", [menu_data.get("description", "No content")])
    current_page = menu_model.current_page or 0

    async def update_page(page_num):
        """Update the page content in the embed"""
        embed = message.embeds[0]
        embed.description = pages[page_num]

        # Update the title if it contains page info
        if " - Page " in embed.title:
            base_title = embed.title.split(" - Page ")[0]
            embed.title = f"{base_title} - Page {page_num + 1}/{len(pages)}"

        await message.edit(embed=embed)

    async def go_previous(user):
        """Handler for previous page reaction"""
        nonlocal current_page
        if user.id == menu_model.discord_author_id and current_page > 0:
            current_page -= 1
            await update_page(current_page)

            # Update in database
            async with get_db_session() as session:
                result = await session.execute(
                    select(Menu).where(Menu.message_id == message.id)
                )
                db_menu = result.scalar_one_or_none()
                if db_menu:
                    db_menu.current_page = current_page
                    await session.commit()

    async def go_next(user):
        """Handler for next page reaction"""
        nonlocal current_page
        if user.id == menu_model.discord_author_id and current_page < len(pages) - 1:
            current_page += 1
            await update_page(current_page)

            # Update in database
            async with get_db_session() as session:
                result = await session.execute(
                    select(Menu).where(Menu.message_id == message.id)
                )
                db_menu = result.scalar_one_or_none()
                if db_menu:
                    db_menu.current_page = current_page
                    await session.commit()

    reaction_handlers["⬅️"] = go_previous
    reaction_handlers["➡️"] = go_next

    return reaction_handlers


async def create_generic_handlers(message: discord.Message, menu_model: Menu) -> dict:
    """
    Create generic handlers for non-paginated menu types.

    Args:
        message: The Discord message containing the menu.
        menu_model: The menu database model.

    Returns:
        Dictionary mapping emoji to handler functions.
    """
    reaction_handlers = {}
    menu_data = menu_model.data
    author_id = menu_model.discord_author_id

    # For simple confirm/cancel menus
    if menu_model.menu_type == "confirm":

        async def on_confirm(user):
            if user.id == author_id:
                channel = message.channel
                await channel.send(f"<@{user.id}> confirmed the action!")

        async def on_cancel(user):
            if user.id == author_id:
                channel = message.channel
                await channel.send(f"<@{user.id}> cancelled the action.")

        reaction_handlers["✅"] = on_confirm
        reaction_handlers["🚫"] = on_cancel

    # For option menus - create a generic handler for each option
    elif menu_model.menu_type == "options":
        for emoji in menu_data.get("reactions", []):

            async def option_handler(user, emoji=emoji):  # Capture emoji in closure
                if user.id == author_id:
                    channel = message.channel
                    await channel.send(f"<@{user.id}> selected option {emoji}")

            reaction_handlers[emoji] = option_handler

    return reaction_handlers
