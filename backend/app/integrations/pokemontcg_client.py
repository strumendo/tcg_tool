from app.config import settings
from app.integrations.base_client import BaseAPIClient


class PokemonTCGClient(BaseAPIClient):
    """Async client for the Pokemon TCG API (https://pokemontcg.io) -- fallback source."""

    def __init__(self) -> None:
        headers: dict[str, str] = {}
        if settings.POKEMONTCG_API_KEY:
            headers["X-Api-Key"] = settings.POKEMONTCG_API_KEY
        super().__init__(
            base_url=settings.POKEMONTCG_BASE_URL,
            timeout=30,
            headers=headers,
        )

    async def fetch_cards(self, query: str, page_size: int = 50) -> list[dict]:
        """Fetch cards matching a Lucene-style query string."""
        result = await self.get("/cards", params={"q": query, "pageSize": page_size})
        if result is None:
            return []
        return result.get("data", [])

    async def search_by_name(self, name: str) -> list[dict]:
        """Search for cards whose name contains the given string."""
        return await self.fetch_cards(f'name:"{name}"')

    async def fetch_set_cards(self, set_code: str) -> list[dict]:
        """Fetch all cards belonging to a specific set."""
        return await self.fetch_cards(f"set.id:{set_code}", page_size=250)
