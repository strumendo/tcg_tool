"""Sync news articles from PokeBeach to the database.

Fetches the latest articles from the PokeBeach RSS feed and inserts any
new entries into the ``news_articles`` table.

Usage (standalone)::

    python -m app.tasks.sync_news
"""

import asyncio
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory
from app.integrations.pokebeach_client import PokeBeachClient
from app.models import NewsArticle


async def sync_news(db: AsyncSession | None = None) -> dict:
    """Fetch and upsert news articles from PokeBeach.

    If *db* is ``None`` a new session is created automatically via the
    application session factory.

    Returns a summary dict with ``created``, ``skipped``, and ``total`` keys.
    """
    client = PokeBeachClient()
    articles_data = await client.fetch_news(limit=30)

    created = 0
    skipped = 0

    async def _do_sync(session: AsyncSession) -> None:
        nonlocal created, skipped

        for a_data in articles_data:
            a_id = a_data["id"]
            stmt = select(NewsArticle).where(NewsArticle.id == a_id)
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing is not None:
                skipped += 1
                continue

            published_at = None
            if a_data.get("published_at"):
                try:
                    published_at = datetime.fromisoformat(a_data["published_at"])
                except (ValueError, TypeError):
                    pass

            article = NewsArticle(
                id=a_id,
                title=a_data["title"],
                summary=a_data.get("summary"),
                url=a_data.get("url"),
                image_url=a_data.get("image_url"),
                source=a_data.get("source", "PokeBeach"),
                published_at=published_at,
            )
            session.add(article)
            created += 1

        await session.commit()

    if db is not None:
        await _do_sync(db)
    else:
        async with async_session_factory() as session:
            await _do_sync(session)

    summary = {"created": created, "skipped": skipped, "total": len(articles_data)}
    print(f"[sync_news] {summary}")
    return summary


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------

async def _main() -> None:
    await sync_news()


if __name__ == "__main__":
    asyncio.run(_main())
