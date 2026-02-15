"""Limitless TCG client for fetching card and deck usage statistics.

Limitless TCG (https://limitlesstcg.com) provides tournament results and
meta-game statistics for competitive Pokemon TCG.  Since there is no
official public API, this client attempts to scrape data from the known
public pages.  If the page structure changes, the methods return empty
lists and log a warning so that callers degrade gracefully.
"""

import re
from typing import Any

import httpx


_USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 14; SM-F956B) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.6422.113 Mobile Safari/537.36"
)

_BASE_URL = "https://limitlesstcg.com"
_REQUEST_TIMEOUT = 30


async def _fetch_html(path: str, params: dict[str, str] | None = None) -> str | None:
    """Fetch an HTML page from Limitless TCG.

    Returns the response body as a string, or ``None`` if the request fails.
    """
    url = f"{_BASE_URL}{path}"
    try:
        async with httpx.AsyncClient(timeout=_REQUEST_TIMEOUT) as client:
            response = await client.get(
                url,
                params=params,
                headers={"User-Agent": _USER_AGENT},
                follow_redirects=True,
            )
            if response.status_code == 200:
                return response.text
    except Exception as exc:
        print(f"[limitless] Failed to fetch {url}: {exc}")
    return None


# ---------------------------------------------------------------------------
# HTML parsing helpers (regex-based to avoid BeautifulSoup dependency)
# ---------------------------------------------------------------------------

_CARD_ROW_RE = re.compile(
    r'<tr[^>]*>.*?'                            # row start
    r'<td[^>]*>.*?</td>\s*'                    # rank column
    r'<td[^>]*>.*?(?P<name>[A-Za-z\s\'\.\-]+?)\s*</td>\s*'  # card name
    r'<td[^>]*>\s*(?P<usage>[\d\.]+)%\s*</td>\s*'            # usage %
    r'<td[^>]*>\s*(?P<copies>[\d\.]+)\s*</td>\s*'            # avg copies
    r'<td[^>]*>\s*(?P<sample>\d+)\s*</td>',                  # sample size
    re.DOTALL,
)

_DECK_ROW_RE = re.compile(
    r'<tr[^>]*>.*?'
    r'<td[^>]*>.*?</td>\s*'                       # rank column
    r'<td[^>]*>.*?(?P<archetype>[A-Za-z\s/\'\.\-]+?)\s*</td>\s*'
    r'<td[^>]*>\s*(?P<share>[\d\.]+)%\s*</td>\s*'
    r'<td[^>]*>\s*(?P<placement>[\d\.]+)\s*</td>\s*'
    r'<td[^>]*>\s*(?P<sample>\d+)\s*</td>',
    re.DOTALL,
)


async def fetch_card_usage(format: str = "standard") -> list[dict[str, Any]]:
    """Fetch top card usage data from Limitless TCG.

    Returns a list of dicts with keys:
        - card_name (str)
        - usage_percentage (float)
        - avg_copies (float)
        - sample_size (int)

    If the page cannot be fetched or parsed, returns an empty list.
    """
    html = await _fetch_html("/cards", params={"format": format, "sort": "usage"})
    if html is None:
        print("[limitless] Could not fetch card usage page")
        return []

    results: list[dict[str, Any]] = []
    for match in _CARD_ROW_RE.finditer(html):
        try:
            results.append(
                {
                    "card_name": match.group("name").strip(),
                    "usage_percentage": float(match.group("usage")),
                    "avg_copies": float(match.group("copies")),
                    "sample_size": int(match.group("sample")),
                }
            )
        except (ValueError, IndexError):
            continue

    if not results:
        # TODO: Limitless page structure may have changed.  When/if a public
        # API becomes available, switch to that instead of HTML scraping.
        print(
            "[limitless] No card usage data parsed.  "
            "The page structure may have changed."
        )

    return results


async def fetch_deck_usage(format: str = "standard") -> list[dict[str, Any]]:
    """Fetch top deck archetype usage data from Limitless TCG.

    Returns a list of dicts with keys:
        - archetype (str)
        - meta_share (float)
        - avg_placement (float)
        - sample_size (int)

    If the page cannot be fetched or parsed, returns an empty list.
    """
    html = await _fetch_html("/decks", params={"format": format})
    if html is None:
        print("[limitless] Could not fetch deck usage page")
        return []

    results: list[dict[str, Any]] = []
    for match in _DECK_ROW_RE.finditer(html):
        try:
            results.append(
                {
                    "archetype": match.group("archetype").strip(),
                    "meta_share": float(match.group("share")),
                    "avg_placement": float(match.group("placement")),
                    "sample_size": int(match.group("sample")),
                }
            )
        except (ValueError, IndexError):
            continue

    if not results:
        # TODO: Limitless page structure may have changed.  When/if a public
        # API becomes available, switch to that instead of HTML scraping.
        print(
            "[limitless] No deck usage data parsed.  "
            "The page structure may have changed."
        )

    return results
