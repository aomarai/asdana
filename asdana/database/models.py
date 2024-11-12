"""
Contains the SQLAlchemy models for the Asdana database.
"""

# pylint: disable=too-few-public-methods

from sqlalchemy import Column, Integer, String, BigInteger
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class YouTubeVideo(Base):
    """
    Represents a YouTube video.
    """

    __tablename__ = "yt_videos"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, unique=True, index=True, nullable=True)
    title = Column(String, nullable=True)


class GuildCogs(Base):
    """
    Represents which cogs are enabled/disabled for a guild.
    """

    __tablename__ = "guild_cogs"

    id = Column(Integer, primary_key=True, index=True)
    guild_id = Column(BigInteger, unique=True, index=True, nullable=False)
    cogs = Column(JSONB, nullable=False)
