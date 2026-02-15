"""RK9.gg tournament calendar scraper."""

import hashlib
import re
from datetime import datetime
from typing import Optional

import httpx

from app.integrations.base_client import BaseAPIClient


class RK9Client(BaseAPIClient):
    """Scraper for RK9.gg Pokemon TCG tournament calendar."""

    BASE_URL = "https://rk9.gg"

    def __init__(self) -> None:
        super().__init__(
            base_url=self.BASE_URL,
            timeout=30,
            headers={"User-Agent": "TCGTool/1.0"},
        )

    async def fetch_tournaments(self) -> list[dict]:
        """Fetch upcoming Pokemon TCG tournaments from RK9.gg."""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(
                    f"{self.BASE_URL}/events/pokemon",
                    headers={"User-Agent": "TCGTool/1.0"},
                )
                response.raise_for_status()
                return self._parse_tournaments(response.text)
        except Exception:
            # Return empty list on failure - tournaments are non-critical
            return []

    def _parse_tournaments(self, html: str) -> list[dict]:
        """Parse tournament data from RK9 HTML page."""
        tournaments: list[dict] = []

        # Look for event blocks - RK9 typically has structured event listings
        # Pattern: event name, date, location, country
        event_blocks = re.findall(
            r'<div[^>]*class="[^"]*event[^"]*"[^>]*>(.*?)</div>\s*</div>',
            html,
            re.DOTALL | re.IGNORECASE,
        )

        if not event_blocks:
            # Fallback: try to find any event-like links
            links = re.findall(
                r'href="(/events/pokemon/[^"]+)"[^>]*>\s*([^<]+)',
                html,
            )
            for href, name in links:
                name = name.strip()
                if not name:
                    continue
                event_id = hashlib.md5(f"rk9-{href}".encode()).hexdigest()[:16]
                tournaments.append(
                    {
                        "id": f"rk9-{event_id}",
                        "name": name,
                        "url": f"{self.BASE_URL}{href}",
                        "format": "Standard",
                        "event_type": "tournament",
                    }
                )

        for block in event_blocks:
            name_match = re.search(
                r'<[^>]*class="[^"]*name[^"]*"[^>]*>([^<]+)', block
            )
            date_match = re.search(
                r'(\w+ \d{1,2},?\s*\d{4}|\d{4}-\d{2}-\d{2})', block
            )
            location_match = re.search(
                r'<[^>]*class="[^"]*location[^"]*"[^>]*>([^<]+)', block
            )

            if not name_match:
                continue

            name = name_match.group(1).strip()
            event_id = hashlib.md5(f"rk9-{name}".encode()).hexdigest()[:16]

            event: dict = {
                "id": f"rk9-{event_id}",
                "name": name,
                "format": "Standard",
                "event_type": "tournament",
            }

            if date_match:
                try:
                    date_str = date_match.group(1).strip()
                    for fmt in ("%B %d, %Y", "%B %d %Y", "%Y-%m-%d"):
                        try:
                            event["date"] = (
                                datetime.strptime(date_str, fmt)
                                .date()
                                .isoformat()
                            )
                            break
                        except ValueError:
                            continue
                except Exception:
                    pass

            if location_match:
                event["location"] = location_match.group(1).strip()

            tournaments.append(event)

        return tournaments
