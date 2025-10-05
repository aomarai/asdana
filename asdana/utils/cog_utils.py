"""
Utility functions for checking cog status and permissions.
"""

import logging
from discord.ext import commands

from asdana.database.database import get_session
from asdana.database.models import CogSettings

logger = logging.getLogger(__name__)


def cog_enabled():
    """
    Decorator to check if a cog is enabled for the current guild.
    """

    async def predicate(ctx: commands.Context):
        # Only check in guilds, not in DMs
        if not ctx.guild:
            return True

        # Get the cog name from the command
        cog_name = ctx.command.cog_name
        if not cog_name:
            return True

        # Config cog is always enabled
        if cog_name.lower() == "config":
            return True

        # Check database for cog status
        try:
            # pylint: disable=duplicate-code
            async with get_session() as session:
                is_enabled = await CogSettings.get_cog_enabled(
                    session, ctx.guild.id, cog_name.lower()
                )
                if not is_enabled:
                    # Try to get the prefix for this context
                    prefix = "!"
                    if hasattr(ctx, "bot") and hasattr(ctx.bot, "command_prefix"):
                        if callable(ctx.bot.command_prefix):
                            # command_prefix can return a string or a list
                            result = await ctx.bot.command_prefix(ctx.bot, ctx.message)
                            if isinstance(result, (list, tuple)):
                                prefix = result[0]
                            else:
                                prefix = result
                        else:
                            prefix = ctx.bot.command_prefix
                    await ctx.send(
                        f"❌ The '{cog_name}' cog is disabled for this server. "
                        f"Ask an admin to enable it with "
                        f"`{prefix}config cog enable {cog_name.lower()}`"
                    )
                return is_enabled
            # pylint: enable=duplicate-code
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Error checking cog status: %s", e)
            # Default to enabled if there's an error
            return True

    return commands.check(predicate)
