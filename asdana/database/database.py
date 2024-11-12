"""
Contains database configuration and session management.
"""

import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select
from dotenv import load_dotenv

from asdana.database.models import Base, GuildCogs

# Load environment variables
load_dotenv()

DATABASE_URL = (
    f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# Create an async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create a configured "Session" class
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


# Dependency to get the session
async def get_session():
    """
    Dependency to get the session from the database.
    :return: Asynchronous database session.
    """
    async with AsyncSessionLocal() as session:
        yield session


async def create_tables():
    """
    Create the tables in the database.
    :return: None
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)


async def get_selected_cogs(guild_id: int):
    """
    Get the selected cogs for a guild.
    :param guild_id: The ID of the guild.
    :return: The selected cogs for the guild.
    """
    async for session in get_session():
        result = await session.execute(
            select(GuildCogs).where(GuildCogs.guild_id == guild_id)
        )
        guild_cogs = result.scalar_one_or_none()
        return guild_cogs.cogs if guild_cogs else {}


async def save_selected_cogs(guild_id: int, cogs: dict):
    """
    Save the selected cogs for a guild.
    :param guild_id: The ID of the guild.
    :param cogs: The cogs to save.
    :return: None
    """
    async for session in get_session():
        guild_cogs = await get_selected_cogs(guild_id)
        if not guild_cogs:
            guild_cogs = GuildCogs(guild_id=guild_id, cogs=cogs)
            session.add(guild_cogs)
        else:
            guild_cogs.cogs = cogs
        await session.commit()

