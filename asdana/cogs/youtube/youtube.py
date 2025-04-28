"""
Provides commands and listeners for YouTube-based functionality and other utilities.
"""

import logging
import os
from discord.ext import commands
from googleapiclient.discovery import build
from sqlalchemy import func, select

from asdana.database.database import get_session
from asdana.database.models import YouTubeVideo

logger = logging.getLogger(__name__)

class YouTube(commands.Cog):
    """
    Provides commands and listeners for YouTube-based functionality via the YouTube API.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.youtube_api_key = os.getenv("YT_API_KEY")

    def __get_youtube_service(self):
        """
        Returns a YouTube service object for interacting with the YouTube API.
        :return: The YouTube service object.
        """
        return build("youtube", "v3", developerKey=self.youtube_api_key)

    async def search_youtube(self, query: str):
        """
        Searches YouTube for videos based on a query.
        :param query: The query to search for.
        :return: The search results.
        """
        logger.info(f"Querying Youtube with query: {query}")
        youtube = self.__get_youtube_service()
        request = youtube.search().list(  # pylint: disable=no-member
            part="snippet",
            maxResults=1,
            q=query,
            type="video",
        )
        response = request.execute()
        return response

    async def __get_random_video_id_from_db(self):
        """
        Gets a random video ID from the YouTube Video ID database.
        :return: A random video ID.
        """
        # Grab a random video ID
        async for session in get_session():
            result = await session.execute(
                select(YouTubeVideo.video_id)
                .order_by(func.random())  # pylint: disable=not-callable
                .limit(1)
            )
            video_id = result.scalar()
            return video_id

    def __build_url_from_id(
        self, video_id: str
    ):  # pylint: disable=unused-private-member
        """
        Builds a YouTube video URL from a video ID.
        :param video_id: The ID of the video.
        :return: The URL of the video.
        """
        return f"https://www.youtube.com/watch?v={video_id}"

    @commands.command(name="randyt", aliases=["ryt"])
    async def random_youtube_video(self, context: commands.Context):
        """
        Selects a random video from YouTube.
        Searches for a random video ID in the database and sends the URL.
        :param context: The context of the command.
        :return: None
        """
        logger.info(f"Random Youtube video requested by user ID {context.author.id}")
        # Get a random video ID
        video_id = await self.__get_random_video_id_from_db()

        # Build the URL
        video_url = self.__build_url_from_id(video_id)

        # Send the URL
        await context.send(f"Your random video is: {video_url}")
