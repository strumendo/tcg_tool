"""
News Service - Fetch Pokemon TCG news from PokeBeach

Features:
- RSS feed parsing from PokeBeach
- Event fetching from RK9
- Caching for offline access
- Background refresh
"""

import re
import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Optional
from urllib.request import urlopen, Request
from urllib.error import URLError
from xml.etree import ElementTree


@dataclass
class NewsArticle:
    """Represents a news article."""
    id: str = ""
    title: str = ""
    summary: str = ""
    url: str = ""
    image_url: str = ""
    published_date: str = ""
    source: str = "PokeBeach"

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> 'NewsArticle':
        return NewsArticle(**data)


@dataclass
class Tournament:
    """Represents a Pokemon TCG tournament."""
    id: str = ""
    name: str = ""
    date: str = ""
    end_date: str = ""
    location: str = ""
    country: str = ""
    format: str = "Standard"
    event_type: str = "Regional"  # Regional, International, Worlds, League Cup, etc.
    url: str = ""
    is_registered: bool = False
    deck_id: Optional[int] = None

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> 'Tournament':
        return Tournament(**data)


class NewsService:
    """Service for fetching Pokemon TCG news and events."""

    POKEBEACH_RSS = "https://www.pokebeach.com/feed"
    RK9_EVENTS_URL = "https://rk9.gg/events/pokemon"
    CACHE_FILE = "news_cache.json"
    CACHE_DURATION_HOURS = 1

    def __init__(self, cache_dir: str = None):
        """Initialize news service."""
        self.cache_dir = cache_dir or os.path.dirname(os.path.abspath(__file__))
        self.cache_path = os.path.join(self.cache_dir, self.CACHE_FILE)
        self._news_cache = []
        self._events_cache = []
        self._last_fetch = None
        self._load_cache()

    def _load_cache(self):
        """Load cached data from file."""
        try:
            if os.path.exists(self.cache_path):
                with open(self.cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._news_cache = [NewsArticle.from_dict(n) for n in data.get('news', [])]
                    self._events_cache = [Tournament.from_dict(e) for e in data.get('events', [])]
                    last_fetch_str = data.get('last_fetch')
                    if last_fetch_str:
                        self._last_fetch = datetime.fromisoformat(last_fetch_str)
        except (json.JSONDecodeError, IOError):
            pass

    def _save_cache(self):
        """Save data to cache file."""
        try:
            data = {
                'news': [n.to_dict() for n in self._news_cache],
                'events': [e.to_dict() for e in self._events_cache],
                'last_fetch': self._last_fetch.isoformat() if self._last_fetch else None
            }
            with open(self.cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError:
            pass

    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid."""
        if not self._last_fetch:
            return False
        return datetime.now() - self._last_fetch < timedelta(hours=self.CACHE_DURATION_HOURS)

    def get_news(self, force_refresh: bool = False, limit: int = 10) -> list[NewsArticle]:
        """
        Get news articles.

        Args:
            force_refresh: Force fetching from network
            limit: Maximum number of articles to return

        Returns:
            List of news articles
        """
        if not force_refresh and self._is_cache_valid() and self._news_cache:
            return self._news_cache[:limit]

        # Try to fetch from network
        try:
            articles = self._fetch_pokebeach_rss()
            if articles:
                self._news_cache = articles
                self._last_fetch = datetime.now()
                self._save_cache()
                return articles[:limit]
        except Exception:
            pass

        # Return cached data if available
        return self._news_cache[:limit]

    def _fetch_pokebeach_rss(self) -> list[NewsArticle]:
        """Fetch news from PokeBeach RSS feed."""
        articles = []

        try:
            req = Request(
                self.POKEBEACH_RSS,
                headers={'User-Agent': 'TCG Tool/1.0'}
            )
            with urlopen(req, timeout=10) as response:
                content = response.read().decode('utf-8')

            root = ElementTree.fromstring(content)

            # Parse RSS items
            for item in root.findall('.//item'):
                title = item.find('title')
                link = item.find('link')
                description = item.find('description')
                pub_date = item.find('pubDate')
                guid = item.find('guid')

                # Extract image from description if present
                image_url = ""
                if description is not None and description.text:
                    img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', description.text)
                    if img_match:
                        image_url = img_match.group(1)

                    # Clean description text
                    desc_text = re.sub(r'<[^>]+>', '', description.text)
                    desc_text = desc_text.strip()[:200]
                else:
                    desc_text = ""

                article = NewsArticle(
                    id=guid.text if guid is not None else link.text if link is not None else "",
                    title=title.text if title is not None else "Untitled",
                    summary=desc_text,
                    url=link.text if link is not None else "",
                    image_url=image_url,
                    published_date=pub_date.text if pub_date is not None else "",
                    source="PokeBeach"
                )
                articles.append(article)

        except (URLError, ElementTree.ParseError):
            pass

        return articles

    def get_events(self, force_refresh: bool = False, limit: int = 10) -> list[Tournament]:
        """
        Get upcoming tournaments.

        Args:
            force_refresh: Force fetching from network
            limit: Maximum number of events to return

        Returns:
            List of tournaments
        """
        if not force_refresh and self._is_cache_valid() and self._events_cache:
            return self._events_cache[:limit]

        # For now, return sample events (RK9 requires more complex parsing)
        # In a real implementation, this would scrape RK9 or use their API
        sample_events = self._get_sample_events()
        self._events_cache = sample_events
        self._last_fetch = datetime.now()
        self._save_cache()

        return sample_events[:limit]

    def _get_sample_events(self) -> list[Tournament]:
        """Get sample events for demonstration."""
        # These would normally come from RK9
        return [
            Tournament(
                id="euic2026",
                name="European International Championships 2026",
                date="2026-04-10",
                end_date="2026-04-12",
                location="London, UK",
                country="UK",
                format="Standard",
                event_type="International",
                url="https://rk9.gg/event/euic2026"
            ),
            Tournament(
                id="naic2026",
                name="North American International Championships 2026",
                date="2026-06-20",
                end_date="2026-06-22",
                location="Columbus, OH, USA",
                country="USA",
                format="Standard",
                event_type="International",
                url="https://rk9.gg/event/naic2026"
            ),
            Tournament(
                id="worlds2026",
                name="Pokemon World Championships 2026",
                date="2026-08-14",
                end_date="2026-08-16",
                location="Anaheim, CA, USA",
                country="USA",
                format="Standard",
                event_type="Worlds",
                url="https://rk9.gg/event/worlds2026"
            ),
            Tournament(
                id="spregional2026",
                name="São Paulo Regional Championships",
                date="2026-03-15",
                end_date="2026-03-16",
                location="São Paulo, Brazil",
                country="Brazil",
                format="Standard",
                event_type="Regional",
                url="https://rk9.gg/event/spregional2026"
            ),
            Tournament(
                id="rjregional2026",
                name="Rio de Janeiro Regional Championships",
                date="2026-05-10",
                end_date="2026-05-11",
                location="Rio de Janeiro, Brazil",
                country="Brazil",
                format="Standard",
                event_type="Regional",
                url="https://rk9.gg/event/rjregional2026"
            ),
        ]

    def get_registered_events(self) -> list[Tournament]:
        """Get events the user has registered for."""
        return [e for e in self._events_cache if e.is_registered]

    def register_for_event(self, event_id: str, deck_id: Optional[int] = None) -> bool:
        """Mark an event as registered."""
        for event in self._events_cache:
            if event.id == event_id:
                event.is_registered = True
                event.deck_id = deck_id
                self._save_cache()
                return True
        return False

    def unregister_from_event(self, event_id: str) -> bool:
        """Unmark an event as registered."""
        for event in self._events_cache:
            if event.id == event_id:
                event.is_registered = False
                event.deck_id = None
                self._save_cache()
                return True
        return False
