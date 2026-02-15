import asyncio
from typing import Any

import httpx


class BaseAPIClient:
    """Base HTTP client with retry logic for external API calls."""

    def __init__(
        self,
        base_url: str,
        timeout: int = 30,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.base_url = base_url
        self.timeout = timeout
        self.headers = headers or {}

    async def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        retries: int = 3,
    ) -> dict | None:
        """Perform a GET request with automatic retries and exponential back-off."""
        async with httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers=self.headers,
        ) as client:
            for attempt in range(retries):
                try:
                    response = await client.get(path, params=params)
                    if response.status_code == 200:
                        return response.json()
                except Exception:
                    if attempt == retries - 1:
                        return None
                    await asyncio.sleep(1 * (attempt + 1))
        return None
