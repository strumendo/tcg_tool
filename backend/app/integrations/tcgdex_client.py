from app.config import settings
from app.integrations.base_client import BaseAPIClient


class TCGdexClient(BaseAPIClient):
    """Async client for the TCGdex API (https://tcgdex.dev)."""

    def __init__(self) -> None:
        super().__init__(base_url=settings.TCGDEX_BASE_URL, timeout=30)

    async def fetch_card(self, set_code: str, number: str) -> dict | None:
        """Fetch a single card by set code and collector number."""
        return await self.get(f"/en/cards/{set_code}-{number}")

    async def fetch_card_by_id(self, card_id: str) -> dict | None:
        """Fetch a single card by its unique TCGdex identifier."""
        return await self.get(f"/en/cards/{card_id}")

    async def fetch_set(self, set_code: str) -> dict | None:
        """Fetch set information and card list."""
        return await self.get(f"/en/sets/{set_code}")

    async def search_cards(self, name: str, lang: str = "en") -> list[dict]:
        """Search for cards by name in the specified language."""
        result = await self.get(f"/{lang}/cards", params={"name": name})
        if result is None:
            return []
        # The API returns a list directly when searching.
        if isinstance(result, list):
            return result
        # Some endpoints wrap the list in a dict.
        return result.get("cards", result.get("data", []))

    @staticmethod
    def get_card_image_url(
        set_code: str,
        number: str,
        quality: str = "high",
        lang: str = "en",
    ) -> str:
        """Build the URL for a card image on the TCGdex CDN."""
        return f"https://assets.tcgdex.net/{lang}/{set_code}/{number}/{quality}.webp"
