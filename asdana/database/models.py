"""
Contains the SQLAlchemy models for the Asdana database.
"""

# pylint: disable=too-few-public-methods

import discord
from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy import select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class YouTubeVideo(Base):
    """
    Represents a YouTube video.
    """

    __tablename__ = "yt_videos"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, unique=True, index=True, nullable=True)
    title = Column(String, nullable=True)


class User(Base):
    """
    Represents a Discord user in the database.

    This class stores Discord user information, interaction metrics, profile data,
    and user preferences. It provides methods to manage user data and interact
    with the database.

    Attributes:
        id (int): The primary key for the database record.
        discord_id (int): The unique Discord user ID.
        username (str): The user's Discord username.
        discriminator (str): The user's Discord discriminator (4-digit tag).
        display_name (str): The user's display name on Discord.
        avatar_url (str): URL to the user's avatar image.
        created_at (datetime): When the user was first added to the database.
        last_seen_at (datetime): When the user was last active.
        commands_used (int): Count of commands used by the user.
        message_count (int): Count of messages sent by the user.
        experience (int): User's experience points in the system.
        level (int): User's level in the system.
        timezone (str): User's preferred timezone.
        preferred_language (str): User's preferred language code.
        notifications_enabled (bool): Whether notifications are enabled.
        custom_prefix (str): User's custom command prefix if set.
        preferences (dict): JSON field storing user preferences.
        menus (relationship): Relationship to menus created by this user.

    Methods:
        set_preferences(preferences_dict): Stores user preferences as JSON.
        get_preferences(): Retrieves user preferences as a dictionary.
        get_or_create(session, discord_user): Gets or creates a user from Discord data.
    """

    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    discord_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(128), nullable=True)
    discriminator = Column(String(4), nullable=True)
    display_name = Column(String(128), nullable=True)
    avatar_url = Column(String(512), nullable=True)
    created_at = Column(DateTime(timezone=True), default=discord.utils.utcnow)
    last_seen_at = Column(DateTime(timezone=True), default=discord.utils.utcnow)

    # Bot interaction metrics
    commands_used = Column(Integer, default=0)
    message_count = Column(Integer, default=0)

    # Profile (RPG?) Related
    experience = Column(Integer, default=0)
    level = Column(Integer, default=0)

    # User settings and preferences
    timezone = Column(String(50), nullable=True)
    preferred_language = Column(String(10), default="en")
    notifications_enabled = Column(Boolean, default=True)
    custom_prefix = Column(String(10), nullable=True)
    preferences = Column(JSON, nullable=True)

    # Relationships
    menus = relationship("Menu", back_populates="author")

    @classmethod
    async def get_or_create(cls, session, discord_user):
        """
        Get an existing user from the database or create a new one if not found.

        This method attempts to retrieve a user based on their Discord ID. If the user
        doesn't exist in the database, it creates a new user record. If the user exists,
        it updates any fields that have changed in the Discord user object.

        Parameters:
        ----------
        session : AsyncSession
            The SQLAlchemy async session to use for database operations.
        discord_user : discord.User or discord.Member
            The Discord user object containing the user's information.

        Returns:
        -------
        User
            The retrieved or newly created user object.

        Notes:
        -----
        - The method automatically updates the user's last_seen_at timestamp
        - The following fields are checked and updated if changed:
          - username
          - discriminator (if available)
          - display_name
          - avatar_url (if display_avatar is available)
        """

        # Try to find the user
        result = await session.execute(
            select(cls).where(cls.discord_id == discord_user.id)
        )
        user = result.scalars().first()

        # Couldn't find user, create instead
        if not user:
            user = cls(
                discord_id=discord_user.id,
                username=discord_user.name,
                discriminator=getattr(discord_user, "discriminator", "0000"),
                display_name=discord_user.display_name,
                avatar_url=(
                    discord_user.display_avatar.url
                    if hasattr(discord_user, "display_avatar")
                    else None
                ),
            )
            session.add(user)
            await session.commit()
        else:  # Update user if anything has changed
            updated = False
            if user.username != discord_user.name:
                user.username = discord_user.name
                updated = True
            if (
                hasattr(discord_user, "discriminator")
                and user.discriminator != discord_user.discriminator
            ):
                user.discriminator = discord_user.discriminator
                updated = True
            if user.display_name != discord_user.display_name:
                user.display_name = discord_user.display_name
                updated = True
            if (
                hasattr(discord_user, "display_avatar")
                and user.avatar_url != discord_user.display_avatar
            ):
                user.avatar_url = discord_user.display_avatar.url
                updated = True

            # Update last seen time
            user.last_seen_at = discord.utils.utcnow()

            if updated:
                await session.commit()
        return user


class Menu(Base):
    """
    Represents a menu message stored in the database.

    This class models interactive menu messages that can be paginated or have special functionality.

    Attributes:
        id (int): Primary key for the menu entry.
        message_id (int): Discord message ID of the menu message (unique).
        channel_id (int): Discord channel ID where the menu is located.
        guild_id (int): Discord guild/server ID where the menu is located.
        discord_author_id (int): Discord user ID of the menu creator.
        user_id (int, optional): Foreign key to the User table.
        author (User): Relationship with the User model who created the menu.
        menu_type (str): Type of menu (e.g., "pagination", "selection", etc.).
        current_page (int): Current page number for paginated menus (defaults to 0).
        created_at (datetime): Timestamp when the menu was created (defaults to UTC now).
        expires_at (datetime, optional): Timestamp when the menu will expire.
        data (JSON): Structured data specific to the menu implementation.
    """

    __tablename__ = "menu"

    id = Column(Integer, primary_key=True)
    message_id = Column(BigInteger, unique=True, nullable=False, index=True)
    channel_id = Column(BigInteger, nullable=False)
    guild_id = Column(BigInteger, nullable=False)

    discord_author_id = Column(BigInteger, nullable=False)

    # Relationships
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    author = relationship("User", back_populates="menus")

    # Menu-specific fields
    menu_type = Column(String(50), nullable=False)
    current_page = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=discord.utils.utcnow())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    data = Column(JSON, nullable=False)
