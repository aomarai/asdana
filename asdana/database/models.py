"""
Contains the SQLAlchemy models for the Asdana database.
"""

# pylint: disable=too-few-public-methods

import datetime
import json

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
    Represents a Discord user.
    """

    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    discord_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(128), nullable=True)
    discriminator = Column(String(4), nullable=True)
    display_name = Column(String(128), nullable=True)
    avatar_url = Column(String(512), nullable=True)
    created_at = Column(DateTime(timezone=True), default=discord.utils.utcnow())
    last_seen_at = Column(DateTime(timezone=True), default=discord.utils.utcnow())

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

    def set_preferences(self, preferences_dict):
        """
        Stores preferences dictionary as a JSON string
        """
        self.preferences = json.dumps(preferences_dict)

    def get_preferences(self):
        """
        Returns user preferences as a dictionary.
        """
        return json.loads(self.preferences) if self.preferences else {}

    @classmethod
    async def get_or_create(cls, session, discord_user):
        from sqlalchemy.future import select

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

    def set_data(self, data_dict):
        """
        Store dictionary as a JSON
        """
        self.data = json.dumps(data_dict)

    def get_data(self):
        """
        Retrieve JSON data as a dictionary
        """
        return json.loads(self.data) if self.data else {}
