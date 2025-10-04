"""
Contains commands for managing server configuration.
"""

import logging
from typing import Optional

import discord
from discord.ext import commands
from sqlalchemy import select

from asdana.database.database import get_session
from asdana.database.models import GuildSettings, CogSettings

logger = logging.getLogger(__name__)


def is_admin():
    """
    Decorator to check if the user is a server admin.
    Checks for Administrator permission or custom admin roles.
    """

    async def predicate(ctx: commands.Context):
        # Owner always has permission
        if ctx.guild and ctx.guild.owner_id == ctx.author.id:
            return True

        # Check for Administrator permission
        if ctx.author.guild_permissions.administrator:
            return True

        # Check for custom admin roles
        if ctx.guild:
            async with get_session() as session:
                guild_settings = await GuildSettings.get_or_create(
                    session, ctx.guild.id
                )
                user_role_ids = [role.id for role in ctx.author.roles]
                if any(
                    role_id in guild_settings.admin_role_ids
                    for role_id in user_role_ids
                ):
                    return True

        raise commands.MissingPermissions(["administrator or admin role"])

    return commands.check(predicate)


class Config(commands.Cog):
    """
    Commands for managing server configuration settings.
    Allows server admins to configure prefixes, enable/disable cogs, and manage admin roles.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(name="config", aliases=["cfg"])
    @commands.guild_only()
    @is_admin()
    async def config(self, ctx: commands.Context):
        """
        Configuration commands for server settings.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @config.command(name="prefix")
    async def set_prefix(self, ctx: commands.Context, prefix: str):
        """
        Set a custom command prefix for this server.

        Usage: !config prefix <new_prefix>
        Example: !config prefix ?
        """
        if len(prefix) > 10:
            await ctx.send("❌ Prefix must be 10 characters or less.")
            return

        async with get_session() as session:
            guild_settings = await GuildSettings.get_or_create(session, ctx.guild.id)
            old_prefix = guild_settings.command_prefix
            guild_settings.command_prefix = prefix
            guild_settings.updated_at = discord.utils.utcnow()
            await session.commit()

        await ctx.send(f"✅ Command prefix changed from `{old_prefix}` to `{prefix}`")

    @config.command(name="show")
    async def show_config(self, ctx: commands.Context):
        """
        Display current server configuration.

        Usage: !config show
        """
        async with get_session() as session:
            guild_settings = await GuildSettings.get_or_create(session, ctx.guild.id)

            embed = discord.Embed(
                title=f"⚙️ Configuration for {ctx.guild.name}",
                color=discord.Color.blue(),
            )

            embed.add_field(
                name="Command Prefix",
                value=f"`{guild_settings.command_prefix}`",
                inline=False,
            )

            # Show admin roles
            if guild_settings.admin_role_ids:
                admin_roles = []
                for role_id in guild_settings.admin_role_ids:
                    role = ctx.guild.get_role(role_id)
                    if role:
                        admin_roles.append(role.mention)
                    else:
                        admin_roles.append(f"Unknown Role ({role_id})")
                embed.add_field(
                    name="Admin Roles",
                    value="\n".join(admin_roles) if admin_roles else "None",
                    inline=False,
                )
            else:
                embed.add_field(
                    name="Admin Roles",
                    value="None (using default Administrator permission)",
                    inline=False,
                )

            embed.set_footer(text="Use !config help to see all configuration commands")

        await ctx.send(embed=embed)

    @config.command(name="adminrole")
    async def manage_admin_role(
        self, ctx: commands.Context, action: str, role: Optional[discord.Role] = None
    ):
        """
        Add or remove admin roles for this server.

        Usage: !config adminrole <add|remove> <@role>
        Example: !config adminrole add @Moderators
        """
        if action.lower() not in ["add", "remove"]:
            await ctx.send("❌ Action must be either 'add' or 'remove'")
            return

        if not role:
            await ctx.send("❌ Please specify a role")
            return

        async with get_session() as session:
            guild_settings = await GuildSettings.get_or_create(session, ctx.guild.id)

            if action.lower() == "add":
                if role.id in guild_settings.admin_role_ids:
                    await ctx.send(f"❌ {role.mention} is already an admin role")
                    return
                guild_settings.admin_role_ids.append(role.id)
                await session.commit()
                await ctx.send(f"✅ Added {role.mention} as an admin role")

            elif action.lower() == "remove":
                if role.id not in guild_settings.admin_role_ids:
                    await ctx.send(f"❌ {role.mention} is not an admin role")
                    return
                guild_settings.admin_role_ids.remove(role.id)
                await session.commit()
                await ctx.send(f"✅ Removed {role.mention} from admin roles")

    @config.group(name="cog")
    async def module_config(self, ctx: commands.Context):
        """
        Manage cog settings for this server.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @module_config.command(name="enable")
    async def enable_cog(self, ctx: commands.Context, cog_name: str):
        """
        Enable a cog for this server.

        Usage: !config cog enable <cog_name>
        Example: !config cog enable random
        """
        # Check if cog exists
        cog = self.bot.get_cog(cog_name.title())
        if not cog:
            await ctx.send(
                f"❌ Cog '{cog_name}' not found. Available cogs: {', '.join(self.bot.cogs.keys())}"
            )
            return

        async with get_session() as session:
            # Get or create cog setting
            result = await session.execute(
                select(CogSettings).where(
                    CogSettings.guild_id == ctx.guild.id,
                    CogSettings.cog_name == cog_name.lower(),
                )
            )
            cog_setting = result.scalars().first()

            if not cog_setting:
                cog_setting = CogSettings(
                    guild_id=ctx.guild.id, cog_name=cog_name.lower(), enabled=True
                )
                session.add(cog_setting)
            else:
                cog_setting.enabled = True

            await session.commit()

        await ctx.send(f"✅ Enabled cog '{cog_name}' for this server")

    @module_config.command(name="disable")
    async def disable_cog(self, ctx: commands.Context, cog_name: str):
        """
        Disable a cog for this server.

        Usage: !config cog disable <cog_name>
        Example: !config cog disable random
        """
        # Prevent disabling the config cog
        if cog_name.lower() == "config":
            await ctx.send("❌ Cannot disable the config cog")
            return

        # Check if cog exists
        cog = self.bot.get_cog(cog_name.title())
        if not cog:
            await ctx.send(
                f"❌ Cog '{cog_name}' not found. Available cogs: {', '.join(self.bot.cogs.keys())}"
            )
            return

        async with get_session() as session:
            # Get or create cog setting
            result = await session.execute(
                select(CogSettings).where(
                    CogSettings.guild_id == ctx.guild.id,
                    CogSettings.cog_name == cog_name.lower(),
                )
            )
            cog_setting = result.scalars().first()

            if not cog_setting:
                cog_setting = CogSettings(
                    guild_id=ctx.guild.id, cog_name=cog_name.lower(), enabled=False
                )
                session.add(cog_setting)
            else:
                cog_setting.enabled = False

            await session.commit()

        await ctx.send(f"✅ Disabled cog '{cog_name}' for this server")

    @module_config.command(name="list")
    async def list_cogs(self, ctx: commands.Context):
        """
        List all cogs and their status for this server.

        Usage: !config cog list
        """
        async with get_session() as session:
            # Get all cog settings for this guild
            result = await session.execute(
                select(CogSettings).where(CogSettings.guild_id == ctx.guild.id)
            )
            cog_settings = {cs.cog_name: cs.enabled for cs in result.scalars()}

        embed = discord.Embed(
            title=f"🔌 Cog Status for {ctx.guild.name}", color=discord.Color.green()
        )

        # List all loaded cogs
        enabled_cogs = []
        disabled_cogs = []

        for cog_name in self.bot.cogs.keys():
            cog_name_lower = cog_name.lower()
            is_enabled = cog_settings.get(cog_name_lower, True)  # Default to enabled

            if is_enabled:
                enabled_cogs.append(f"✅ {cog_name}")
            else:
                disabled_cogs.append(f"❌ {cog_name}")

        if enabled_cogs:
            embed.add_field(
                name="Enabled Cogs", value="\n".join(enabled_cogs), inline=False
            )

        if disabled_cogs:
            embed.add_field(
                name="Disabled Cogs", value="\n".join(disabled_cogs), inline=False
            )

        embed.set_footer(
            text="Use !config cog enable/disable <cog_name> to change status"
        )

        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        """
        Handle command errors, specifically for checking if a cog is disabled.
        """
        if isinstance(error, commands.CheckFailure):
            # Check if it's due to cog being disabled
            if ctx.command and ctx.guild:
                cog_name = ctx.command.cog_name
                if cog_name:
                    async with get_session() as session:
                        is_enabled = await CogSettings.get_cog_enabled(
                            session, ctx.guild.id, cog_name.lower()
                        )
                        if not is_enabled:
                            await ctx.send(
                                f"❌ The '{cog_name}' cog is disabled for this server."
                            )
                            return
