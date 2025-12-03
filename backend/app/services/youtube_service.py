"""YouTube Service - Fetch channel information"""
import re
from typing import Optional
import httpx
import structlog

logger = structlog.get_logger()


class YouTubeService:
    """Service for fetching YouTube channel information"""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_channel_info(self, url: str) -> Optional[dict]:
        """
        Fetch channel information from a YouTube URL.

        Supports:
        - youtube.com/channel/UC...
        - youtube.com/c/ChannelName
        - youtube.com/@username
        """
        try:
            # Extract channel identifier from URL
            channel_id = self._extract_channel_id(url)

            if not channel_id:
                # Try to fetch the page and extract channel ID
                channel_id = await self._fetch_channel_id_from_url(url)

            if not channel_id:
                logger.warning(f"Could not extract channel ID from URL: {url}")
                return None

            # Fetch channel page to get info
            channel_info = await self._fetch_channel_info(channel_id, url)
            return channel_info

        except Exception as e:
            logger.error(f"Failed to fetch channel info: {str(e)}")
            return None

    def _extract_channel_id(self, url: str) -> Optional[str]:
        """Extract channel ID from URL"""
        # Channel ID format: youtube.com/channel/UC...
        match = re.search(r"youtube\.com/channel/([a-zA-Z0-9_-]+)", url)
        if match:
            return match.group(1)

        return None

    async def _fetch_channel_id_from_url(self, url: str) -> Optional[str]:
        """Fetch the page and extract channel ID"""
        try:
            response = await self.client.get(url, follow_redirects=True)
            response.raise_for_status()

            # Look for channel ID in page content
            match = re.search(r'"channelId":"([a-zA-Z0-9_-]+)"', response.text)
            if match:
                return match.group(1)

            # Alternative pattern
            match = re.search(r'channel/([a-zA-Z0-9_-]+)', response.text)
            if match:
                return match.group(1)

        except Exception as e:
            logger.warning(f"Failed to fetch channel page: {str(e)}")

        return None

    async def _fetch_channel_info(self, channel_id: str, original_url: str) -> dict:
        """Fetch channel information"""
        # Construct canonical channel URL
        channel_url = f"https://www.youtube.com/channel/{channel_id}"

        try:
            response = await self.client.get(channel_url, follow_redirects=True)
            response.raise_for_status()
            html = response.text

            # Extract channel name
            name_match = re.search(r'"name":\s*"([^"]+)"', html)
            name = name_match.group(1) if name_match else "Unknown Channel"

            # Extract description
            desc_match = re.search(r'"description":\s*"([^"]*)"', html)
            description = desc_match.group(1) if desc_match else None

            # Extract thumbnail
            thumb_match = re.search(r'"avatar":\s*\{"thumbnails":\s*\[\{"url":\s*"([^"]+)"', html)
            thumbnail = thumb_match.group(1) if thumb_match else None

            # Extract subscriber count (approximate)
            sub_match = re.search(r'"subscriberCountText":\s*\{"simpleText":\s*"([^"]+)"', html)
            subscribers = self._parse_subscriber_count(sub_match.group(1)) if sub_match else None

            # Extract video count
            video_match = re.search(r'"videoCountText":\s*\{"runs":\s*\[\{"text":\s*"([^"]+)"', html)
            video_count = self._parse_video_count(video_match.group(1)) if video_match else None

            return {
                "channel_id": channel_id,
                "name": name,
                "description": description,
                "url": channel_url,
                "thumbnail_url": thumbnail,
                "subscriber_count": subscribers,
                "video_count": video_count
            }

        except Exception as e:
            logger.warning(f"Failed to parse channel info: {str(e)}")
            return {
                "channel_id": channel_id,
                "name": "Unknown Channel",
                "url": original_url
            }

    def _parse_subscriber_count(self, text: str) -> Optional[int]:
        """Parse subscriber count from text like '1.5M subscribers'"""
        try:
            text = text.lower().replace("subscribers", "").replace("subscriber", "").strip()

            multiplier = 1
            if "k" in text:
                multiplier = 1000
                text = text.replace("k", "")
            elif "m" in text:
                multiplier = 1000000
                text = text.replace("m", "")
            elif "b" in text:
                multiplier = 1000000000
                text = text.replace("b", "")

            return int(float(text) * multiplier)
        except:
            return None

    def _parse_video_count(self, text: str) -> Optional[int]:
        """Parse video count from text"""
        try:
            # Extract numbers
            numbers = re.findall(r'[\d,]+', text)
            if numbers:
                return int(numbers[0].replace(",", ""))
        except:
            pass
        return None

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
