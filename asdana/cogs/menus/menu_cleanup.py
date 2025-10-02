"""
Menu cleanup utilities for managing expired menus.

This module handles the background task for cleaning up expired
reaction menus from the database.
"""

import asyncio
import logging
import os

import discord
from sqlalchemy import select

from asdana.database.database import get_session as get_db_session
from asdana.database.models import Menu

logger = logging.getLogger(__name__)


async def cleanup_expired_menus(
    active_menus: dict, batch_size: int = 100
) -> int:
    """
    Delete expired menus from the database in batches.

    Args:
        active_menus: Dictionary of currently active menus to update.
        batch_size: Maximum number of menus to delete in one batch.

    Returns:
        Number of menus deleted.
    """
    try:
        now = discord.utils.utcnow()
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
                if menu.message_id in active_menus:
                    logger.debug(
                        "Removing menu %s from active menus cache.", menu.message_id
                    )
                    del active_menus[menu.message_id]

                # Delete from database
                await session.delete(menu)
                total_deleted += 1

            if total_deleted > 0:
                await session.commit()
                logger.info("Deleted %d expired menus from database.", total_deleted)

        return total_deleted

    except (OSError, RuntimeError) as e:
        logger.error("Error during menu cleanup: %s", e, exc_info=True)
        return 0


async def run_menu_cleanup_task(bot, active_menus: dict) -> None:
    """
    Background task that periodically cleans up expired menus.

    Args:
        bot: The Discord bot instance.
        active_menus: Dictionary of currently active menus to update.
    """
    cleanup_interval = int(os.getenv("CLEANUP_INTERVAL_MENUS", "3600"))
    batch_size = int(os.getenv("CLEANUP_BATCH_SIZE_MENUS", "100"))

    await bot.wait_until_ready()

    while not bot.is_closed():
        try:
            logger.info("Running scheduled menu cleanup task.")
            await cleanup_expired_menus(active_menus, batch_size)

            # Wait for next cleanup interval
            await asyncio.sleep(cleanup_interval)
        except (asyncio.CancelledError, KeyboardInterrupt):
            logger.info("Menu cleanup task cancelled.")
            break
        except (OSError, RuntimeError) as e:
            logger.error("Error during menu cleanup task: %s", e, exc_info=True)
            await asyncio.sleep(60)  # Retry after 60 seconds
