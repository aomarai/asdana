"""
Contains database configuration and session management.
"""

import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

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

# Create a base class for declarative class definitions
Base = declarative_base()


# Dependency to get the session
async def get_session() -> AsyncSession:
    """
    Dependency to get the session from the database.
    :return: The session.
    :rtype: AsyncSession
    """
    async with AsyncSessionLocal() as session:
        yield session


async def create_tables():
    """
    Create the tables in the database.
    :return: None
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
