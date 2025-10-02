"""
Contains database configuration and session management.
"""

from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from asdana.core.config import config
from asdana.database.models import Base

# Get database URL from configuration
DATABASE_URL = config.database_url

# Create an async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create a configured "Session" class
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


@asynccontextmanager
async def get_session():
    """
    Context manager to get a database session.
    :return: Asynchronous database session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            pass  # Session will be closed by the AsyncSessionLocal context manager


async def create_tables():
    """
    Create the tables in the database.
    :return: None
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)
