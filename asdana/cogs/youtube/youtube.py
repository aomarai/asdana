"""
Provides commands and listeners for YouTube-based functionality and other utilities.
"""
import os
from discord.ext import commands
from googleapiclient.discovery import build


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
        youtube = self.__get_youtube_service()
        request = youtube.search().list( # pylint: disable=no-member
            part="snippet",
            maxResults=1,
            q=query,
            type="video",
        )
        response = request.execute()
        return response

    def __build_url_from_id(self, video_id: str):
        """
        Builds a YouTube video URL from a video ID.
        :param video_id: The ID of the video.
        :return: The URL of the video.
        """
        return f"https://www.youtube.com/watch?v={video_id}"
