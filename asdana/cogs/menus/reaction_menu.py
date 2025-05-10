import asyncio
import datetime
import os
import logging
import discord

from discord.ext import commands
from typing import Dict, Callable, Coroutine, Any

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from asdana.database.models import Menu, User
from asdana.database.database import get_session as get_db_session

logger = logging.getLogger(__name__)


class ReactionMenu(commands.Cog):
    """
    A cog class that provides functionality to create interactive menus with reaction buttons.

    This cog allows creating various types of interactive menus in Discord channels:
    - Custom menus with arbitrary reaction handlers
    - Confirmation menus (with confirm/cancel buttons)
    - Paginated menus (with next/previous navigation)
    - Option selection menus

    Features:
    - Configurable timeout for menu interactivity
    - Persistent menus that survive bot restarts
    - Automatic cleanup of expired menus
    - Support for custom fields and data in menus

    Attributes:
        bot (commands.Bot): The Discord bot instance.
        active_menus (dict): Cache of currently active menu messages and their handlers.
        menu_cleanup_task (asyncio.Task): Background task that periodically cleans expired menus.

    Example usage:
        ```python
        # Create a simple confirmation menu
        await bot.get_cog('ReactionMenu').create_menu(
            ctx,
            "Confirm Action",
            "Do you want to proceed with this action?",
            {
                "✅": confirm_callback,
                "🚫": cancel_callback
            },
            timeout=60  # Menu expires after 60 seconds
        ```
    """

    def __init__(self, bot):
        self.bot = bot
        self.active_menus = {}
        self.bot.loop.create_task(self.load_persistent_menus())
        self.menu_cleanup_task = self.bot.loop.create_task(self.bg_task_menu_cleanup())

    async def create_menu(
        self,
        context: commands.Context,
        title: str,
        description: str,
        reactions: Dict[str, Callable[[discord.User], Coroutine[Any, Any, Any]]],
        color: discord.Color = discord.Color.blue(),
        timeout: int = 60,
        **kwargs,
    ):
        """
        Creates an interactive menu with reaction buttons via Discord embeds.

        Args:
            context (commands.Context): Command context.
            title (str): Title of the embed.
            description (str): Description text to displayed inside the embed.
            reactions (Dict[str, Callable[[discord.User], Coroutine[Any, Any, Any]]]): Dict mapping emoji to callback functions.
            color (discord.Color, optional): The color of the embed. Defaults to discord.Color.blue().
            timeout (int, optional): Time in seconds before reactions stop working on the embed. If set to -1, works indefinitely. Defaults to 60.

        Returns:
            discord.Message: The message object that was sent.
        """
        embed = discord.Embed(title=title, description=description, color=color)

        # Add any fields passed into kwargs
        for name, value in kwargs.items():
            if name.startswith("field_"):
                field_name = name[6:]  # Removing the 'field_' prefix
                embed.add_field(name=field_name, value=value, inline=True)

        message = await context.send(embed=embed)

        # Add reactions
        for emoji in reactions:
            await message.add_reaction(emoji)

        # Determine menu type based on reactions
        menu_type = "custom"
        if "✅" in reactions and "🚫" in reactions:
            menu_type = "confirm"
        elif "⬅️" in reactions and "➡️" in reactions:
            menu_type = "paginated"
        elif len(reactions) > 0:
            menu_type = "options"

        # Prepare menu data
        menu_data = {
            "title": title,
            "description": description,
            "reactions": list(reactions.keys()),  # Store reaction emojis
            "author_id": context.author.id,
            "channel_id": context.channel.id,
            "guild_id": context.guild.id if context.guild else 0,
        }

        # Add any extra data from kwargs
        for key, value in kwargs.items():
            if not key.startswith("field_"):
                menu_data[key] = value

        # Store the menu data in memory
        self.active_menus[message.id] = {
            "reactions": reactions,
            "timeout": timeout,
            "created_at": discord.utils.utcnow(),
            "author_id": context.author.id,
        }

        # Store in database for persistence
        async with get_db_session() as session:
            user = await User.get_or_create(session, context.author)
            expires_at = (
                discord.utils.utcnow() + datetime.timedelta(seconds=timeout)
                if timeout > 0
                else None
            )
            menu_model = Menu(
                message_id=message.id,
                channel_id=context.channel.id,
                guild_id=(
                    context.guild.id if context.guild else 0
                ),  # DMs are always guild ID 0
                discord_author_id=context.author.id,
                user_id=user.id,
                menu_type=menu_type,
                current_page=0 if menu_type == "paginated" else None,
                expires_at=expires_at,
            )
            menu_model.set_data(menu_data)  # Fix: Pass menu_data, not menu_model

            # Add to session and commit
            session.add(menu_model)
            await session.commit()

        return message

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        """
        Handles reactions to menu messages.

        Args:
            reaction (discord.Reaction): The Discord reaction that is being added.
            user (discord.User): The user that is reacting to the embed.
        """
        if user.bot:  # No effect for reactions added by bot
            return

        message_id = reaction.message.id
        menu = self.active_menus.get(message_id)

        if not menu:  # No menu exists
            return

        if (
            menu["timeout"] != -1
            and (discord.utils.utcnow() - menu["created_at"]).total_seconds()
            > menu["timeout"]
        ):
            del self.active_menus[message_id]
            return

        logger.debug("Received reaction %s from %s", reaction.emoji, user.name)
        logger.debug("Available callbacks: %s", list(menu["reactions"].keys()))

        # Check if the emoji has a callback function
        emoji = str(reaction.emoji)
        if emoji in menu["reactions"]:
            # Get channel and guild info for logging
            channel_name = (
                reaction.message.channel.name
                if hasattr(reaction.message.channel, "name")
                else "DM"
            )
            channel_id = reaction.message.channel.id

            guild_name = "DM"
            guild_id = "N/A"
            if reaction.message.guild:
                guild_name = reaction.message.guild.name
                guild_id = reaction.message.guild.id

            logger.debug(
                "Executing callback for %s in channel #%s (%s), guild: %s (%s)",
                emoji,
                channel_name,
                channel_id,
                guild_name,
                guild_id,
            )
            # Execute callback if present
            await menu["reactions"][emoji](user)
        else:
            logger.debug("No callback found for emoji: '%s'", emoji)

        # Remove the reaction to allow a selection again
        try:
            await reaction.remove(user)
        except discord.HTTPException:
            pass  # Missing permissions, continue anyway

    async def load_persistent_menus(self):
        """
        Load active menus from the database when the bot starts up.
        """
        await self.bot.wait_until_ready()
        logger.info("Loading active menus from database...")

        async with get_db_session() as session:
            # Get all non-expired menus
            now = datetime.datetime.utcnow()
            query = (
                select(Menu)
                .options(joinedload(Menu.author))
                .where((Menu.expires_at > now) | (Menu.expires_at is None))
            )

            result = await session.execute(query)
            persistent_menus = result.scalars().all()

            for menu_model in persistent_menus:
                try:
                    # Fetch the channel and message
                    channel = self.bot.get_channel(menu_model.channel_id)
                    if not channel:
                        continue

                    try:
                        message = await channel.fetch_message(menu_model.message_id)
                    except discord.NotFound:
                        # Message was deleted
                        await session.delete(menu_model)
                        continue

                    # Create reaction handlers based on menu type
                    reaction_handlers = {}

                    if menu_model.menu_type == "paginated":
                        # Restore paginated menu handlers
                        reaction_handlers = await self._create_paginated_handlers(
                            message, menu_model
                        )
                    else:
                        # For other menu types, create generic handlers
                        reaction_handlers = await self._create_generic_handlers(
                            message, menu_model
                        )

                    # Store in active menus
                    self.active_menus[menu_model.message_id] = {
                        "reactions": reaction_handlers,
                        "timeout": -1,  # No timeout for restored menus
                        "created_at": menu_model.created_at,
                        "author_id": menu_model.discord_author_id,
                    }

                    logger.debug(
                        "✅ Restored %s menu (ID: %s)",
                        menu_model.menu_type,
                        menu_model.message_id,
                    )

                except Exception as e:
                    logger.error(
                        "❌ Failed to restore menu %s: %s", menu_model.message_id, e
                    )
                    await session.delete(menu_model)

            # Commit any changes (like deleting invalid menus)
            await session.commit()

        logger.info(
            "Finished loading menus. Restored %d active menus.", len(self.active_menus)
        )

    async def _create_paginated_handlers(self, message, menu_model):
        """
        Create handlers for paginated menus loaded from the database
        """
        reaction_handlers = {}

        menu_data = menu_model.get_data()
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
            if (
                user.id == menu_model.discord_author_id
                and current_page < len(pages) - 1
            ):
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

    async def _create_generic_handlers(self, message, menu_model):
        """Create generic handlers for other menu types"""
        reaction_handlers = {}
        menu_data = menu_model.get_data()
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

    async def bg_task_menu_cleanup(
        self,
        cleanup_interval=int(os.getenv("CLEANUP_INTERVAL_MENUS", "3600")),
        batch_size=int(os.getenv("CLEANUP_BATCH_SIZE_MENUS", "100")),
    ):
        """
        Background task that periodically cleans up expired menus from the database.
        """
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            try:
                logger.info("Running scheduled menu cleanup task.")
                await self.cleanup_expired_menus(batch_size)

                # Wait for next cleanup interval
                await asyncio.sleep(cleanup_interval)
            except Exception as e:
                logger.error("Error during menu cleanup task: %s", e, exc_info=True)
                await asyncio.sleep(60)  # Retry after 60 seconds

    async def cleanup_expired_menus(self, batch_size=100):
        """Delete expired menus from the database in batches"""

        try:
            now = datetime.datetime.now(datetime.timezone.utc)
            total_deleted = 0

            async with get_db_session() as session:
                query = (
                    select(Menu)
                    .where(
                        (Menu.expires_at is not None)  # Not indefinite
                        & (Menu.expires_at < now)  # Expired
                    )
                    .limit(batch_size)
                )

                result = await session.execute(query)
                expired_menus = result.scalars().all()
                logger.debug("Found %d expired menus", len(expired_menus))

                # Process expired menus
                for menu in expired_menus:
                    if menu.message_id in self.active_menus:
                        logger.debug(
                            "Removing menu %s from active menus cache.", menu.message_id
                        )
                        del self.active_menus[menu.message_id]

                    # Delete from database
                    await session.delete(menu)
                    total_deleted += 1

                if total_deleted > 0:
                    await session.commit()
                    logger.info(
                        "Deleted %d expired menus from database.", total_deleted
                    )

        except Exception as e:
            logger.error("Error during menu cleanup task: %s", e, exc_info=True)


async def setup(bot):
    """
    Asynchronously sets up the ReactionMenu cog with the bot.

    This function is automatically called by the bot's extension loader
    to register the ReactionMenu cog with the Discord bot instance.

    Args:
        bot (discord.ext.commands.Bot): The Discord bot instance.

    Returns:
        None
    """
    await bot.add_cog(ReactionMenu(bot))
