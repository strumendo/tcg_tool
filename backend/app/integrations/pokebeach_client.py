"""PokeBeach news RSS feed parser."""

import hashlib
import re
from datetime import datetime
from typing import Optional

import httpx

from app.integrations.base_client import BaseAPIClient


class PokeBeachClient(BaseAPIClient):
    """Parser for PokeBeach.com news RSS feed."""

    RSS_URL = "https://www.pokebeach.com/feed"

    def __init__(self) -> None:
        super().__init__(
            base_url="https://www.pokebeach.com",
            timeout=30,
            headers={"User-Agent": "TCGTool/1.0"},
        )

    async def fetch_news(self, limit: int = 20) -> list[dict]:
        """Fetch latest news articles from PokeBeach RSS feed."""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(
                    self.RSS_URL,
                    headers={"User-Agent": "TCGTool/1.0"},
                )
                response.raise_for_status()
                articles = self._parse_rss(response.text)
                return articles[:limit]
        except Exception:
            return []

    def _parse_rss(self, xml_text: str) -> list[dict]:
        """Parse RSS XML into article dicts."""
        articles: list[dict] = []

        # Extract items from RSS
        items = re.findall(r"<item>(.*?)</item>", xml_text, re.DOTALL)

        for item in items:
            title = self._extract_tag(item, "title")
            link = self._extract_tag(item, "link")
            description = self._extract_tag(item, "description")
            pub_date = self._extract_tag(item, "pubDate")

            # Try media:content or enclosure for image
            image_match = re.search(
                r'<(?:media:content|enclosure)[^>]*url="([^"]+)"',
                item,
            )
            # Also try to find image in content:encoded
            if not image_match:
                content = self._extract_tag(item, "content:encoded") or ""
                img_match = re.search(r'<img[^>]*src="([^"]+)"', content)
                if img_match:
                    image_match = img_match

            if not title:
                continue

            article_id = hashlib.md5(
                f"pokebeach-{link or title}".encode()
            ).hexdigest()[:16]

            # Clean HTML from description
            summary = re.sub(r"<[^>]+>", "", description or "")
            summary = summary.strip()[:500] if summary else None

            # Parse date
            published_at: Optional[str] = None
            if pub_date:
                for fmt in (
                    "%a, %d %b %Y %H:%M:%S %z",
                    "%a, %d %b %Y %H:%M:%S %Z",
                    "%Y-%m-%dT%H:%M:%S%z",
                ):
                    try:
                        published_at = datetime.strptime(
                            pub_date.strip(), fmt
                        ).isoformat()
                        break
                    except ValueError:
                        continue

            article = {
                "id": f"pb-{article_id}",
                "title": self._clean_html(title),
                "summary": summary,
                "url": link,
                "image_url": image_match.group(1) if image_match else None,
                "source": "PokeBeach",
                "published_at": published_at,
            }
            articles.append(article)

        return articles

    def _extract_tag(self, text: str, tag: str) -> Optional[str]:
        """Extract content from an XML tag."""
        # Handle CDATA
        pattern = (
            rf"<{tag}[^>]*>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</{tag}>"
        )
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1).strip() if match else None

    def _clean_html(self, text: str) -> str:
        """Remove HTML tags and decode entities."""
        text = re.sub(r"<[^>]+>", "", text)
        text = (
            text.replace("&amp;", "&")
            .replace("&lt;", "<")
            .replace("&gt;", ">")
        )
        text = (
            text.replace("&#8217;", "'")
            .replace("&#8220;", '"')
            .replace("&#8221;", '"')
        )
        return text.strip()
