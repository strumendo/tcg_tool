"""Sync tournaments from RK9.gg to the database.

Fetches tournament data from the RK9.gg event calendar and upserts it
into the ``tournaments`` table.

Usage (standalone)::

    python -m app.tasks.sync_tournaments
"""

import asyncio
from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory
from app.integrations.rk9_client import RK9Client
from app.models import Tournament


async def sync_tournaments(db: AsyncSession | None = None) -> dict:
    """Fetch and upsert tournaments from RK9.gg.

    If *db* is ``None`` a new session is created automatically via the
    application session factory.

    Returns a summary dict with ``created``, ``updated``, and ``total`` keys.
    """
    client = RK9Client()
    tournaments_data = await client.fetch_tournaments()

    created = 0
    updated = 0

    async def _do_sync(session: AsyncSession) -> None:
        nonlocal created, updated

        for t_data in tournaments_data:
            t_id = t_data["id"]
            stmt = select(Tournament).where(Tournament.id == t_id)
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            t_date = None
            if t_data.get("date"):
                try:
                    t_date = date.fromisoformat(t_data["date"])
                except (ValueError, TypeError):
                    pass

            if existing is None:
                tournament = Tournament(
                    id=t_id,
                    name=t_data["name"],
                    date=t_date,
                    location=t_data.get("location"),
                    country=t_data.get("country"),
                    format=t_data.get("format", "Standard"),
                    event_type=t_data.get("event_type"),
                    url=t_data.get("url"),
                )
                session.add(tournament)
                created += 1
            else:
                existing.name = t_data["name"]
                if t_date:
                    existing.date = t_date
                if t_data.get("location"):
                    existing.location = t_data["location"]
                if t_data.get("url"):
                    existing.url = t_data["url"]
                updated += 1

        await session.commit()

    if db is not None:
        await _do_sync(db)
    else:
        async with async_session_factory() as session:
            await _do_sync(session)

    summary = {"created": created, "updated": updated, "total": len(tournaments_data)}
    print(f"[sync_tournaments] {summary}")
    return summary


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------

async def _main() -> None:
    await sync_tournaments()


if __name__ == "__main__":
    asyncio.run(_main())
