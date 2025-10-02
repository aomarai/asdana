"""
Factory for creating reaction-interactive menus via embeds.
"""

from typing import Any, Callable, Coroutine, List, Optional, Tuple

import discord
from discord.ext import commands


class MenuFactory:
    """
    Factory for creating reaction-interactive menus via embeds.
    """

    @staticmethod
    async def get_menu_cog(bot: commands.Bot):
        """
        Retrieves the ReactionMenu cog

        Args:
            bot (commands.Bot): Instance of the Discord bot.
        """
        menu_cog = bot.get_cog("ReactionMenu")
        if not menu_cog:
            raise RuntimeError("The ReactionMenu cog is not loaded.")
        return menu_cog

    @staticmethod
    async def create_confirm_menu(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        context: commands.Context,
        title: str,
        description: str,
        on_confirm: Callable[[discord.User], Coroutine[Any, Any, Any]],
        on_cancel: Optional[Callable[[discord.User], Coroutine[Any, Any, Any]]] = None,
        timeout: int = 60,
        color: discord.Color = discord.Color.blue(),
    ) -> discord.Message:
        """
        Creates a simple confirmation menu with confirm/cancel options.

        Args:
            context (commands.Context): The command context.
            title (str): Title of the menu.
            description (str): Description text.
            on_confirm: Callback for confirmation.
            on_cancel: Callback for cancellation. Defaults to None.
            timeout (int, optional): Time before the menu expires.
                Set to -1 for infinite. Defaults to 60.
            color (discord.Color, optional): Color of the embed.
                Defaults to discord.Color.blue().

        Returns:
            discord.Message: The message object containing the confirmation menu
        """
        menu_cog = await MenuFactory.get_menu_cog(context.bot)

        if on_cancel is None:

            async def default_cancel(user):
                if user.id == context.author.id:
                    await context.send(f"Operation cancelled by {user.mention}.")

            on_cancel = default_cancel

        reactions = {"✅": on_confirm, "🚫": on_cancel}

        return await menu_cog.create_menu(
            context=context,
            title=title,
            description=description,
            reactions=reactions,
            color=color,
            timeout=timeout,
            field_confirm="✅ to confirm",
            field_cancel="🚫 to cancel",
        )

    @staticmethod
    async def create_options_menu(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        context: commands.Context,
        title: str,
        description: str,
        options: List[
            Tuple[str, str, Callable[[discord.User], Coroutine[Any, Any, Any]]]
        ],
        timeout: int = 60,
        color: discord.Color = discord.Color.blue(),
    ) -> discord.Message:
        """
        Creates a menu with multiple options.

        Args:
            context (commands.Context): The command context.
            title (str): Title of the menu.
            description (str): Description of the menu.
            options: List of tuples (emoji, description, callback)
            timeout (int, optional): Time before menu expires.
                Indefinite if set to -1. Defaults to 60.
            color (discord.Color, optional): Color of the embed.
                Defaults to discord.Color.blue().

        Returns:
            discord.Message: The message object containing the options menu.
        """
        menu_cog = await MenuFactory.get_menu_cog(context.bot)

        reactions = {}
        fields = {}

        for emoji, option_description, callback in options:
            reactions[emoji] = callback
            fields[f"field_{emoji}"] = option_description

        return await menu_cog.create_menu(
            context=context,
            title=title,
            description=description,
            reactions=reactions,
            color=color,
            timeout=timeout,
            **fields,
        )

    @staticmethod
    async def create_paginated_menu(
        context: commands.Context,
        title: str,
        pages: List[str],
        timeout: int = 120,
        color: discord.Color = discord.Color.blue(),
    ) -> discord.Message:
        """
        Creates a paginated menu for browsing through multiple pages of content.

        Args:
            context (commands.Context): The command context.
            title (str): Title of the menu.
            pages (List[str]): List of page contents.
            timeout (int, optional): Time before menu expires.
                Indefinite if set to -1. Defaults to 120.
            color (discord.Color, optional): Color of the embed.
                Defaults to discord.Color.blue().

        Returns:
            discord.Message: The message object containing the paginated menu.
        """
        menu_cog = await MenuFactory.get_menu_cog(context.bot)

        if not pages:
            raise ValueError("Pages list cannot be empty.")

        current_page = 0
        total_pages = len(pages)

        # Function to update page content
        async def update_page(message: discord.Message, page_num: int):
            embed = discord.Embed(
                title=f"{title} - Page {page_num + 1} / {total_pages}",
                description=pages[page_num],
                color=color,
            )
            await message.edit(embed=embed)

        # Button callbacks
        async def go_previous(user: discord.User):
            nonlocal current_page
            if user.id == context.author.id and current_page > 0:
                current_page -= 1
                await update_page(message, current_page)

        async def go_next(user: discord.User):
            nonlocal current_page
            if user.id == context.author.id and current_page < total_pages - 1:
                current_page += 1
                await update_page(message, current_page)

        reactions = {"⬅️": go_previous, "➡️": go_next}

        # Create the initial embed
        message = await menu_cog.create_menu(
            context=context,
            title=f"{title} - Page 1/{total_pages}",
            description=pages[0],
            reactions=reactions,
            color=color,
            timeout=timeout,
            field_navigation="Use ⬅️ and ➡️ to navigate pages.",
        )

        return message
