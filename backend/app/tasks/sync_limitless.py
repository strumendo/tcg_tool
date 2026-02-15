"""Sync card and deck usage statistics from Limitless TCG.

Fetches usage data from the Limitless TCG scraper and upserts it into
``card_usage_stats`` and ``deck_usage_stats`` tables with today's date
as the snapshot date.

Usage (standalone)::

    python -m app.tasks.sync_limitless
"""

import asyncio
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory
from app.integrations.limitless_client import fetch_card_usage, fetch_deck_usage
from app.models.card import Card
from app.models.tournament import CardUsageStats, DeckUsageStats


# ---------------------------------------------------------------------------
# Card usage sync
# ---------------------------------------------------------------------------

async def sync_card_usage(format: str = "standard") -> int:
    """Fetch card usage from Limitless and upsert ``CardUsageStats`` rows.

    Returns the number of records upserted.
    """
    print(f"[sync_limitless] Fetching card usage (format={format})...")
    usage_data = await fetch_card_usage(format=format)
    if not usage_data:
        print("[sync_limitless] No card usage data returned from Limitless")
        return 0

    today = date.today()
    count = 0

    async with async_session_factory() as session:
        for entry in usage_data:
            try:
                card_name = entry.get("card_name", "")
                if not card_name:
                    continue

                # Look up the card by English name.
                card = await _find_card_by_name(session, card_name)
                if card is None:
                    print(f"[sync_limitless]   Card '{card_name}' not found in DB, skipping")
                    continue

                await _upsert_card_usage(
                    session,
                    card_id=card.id,
                    format_str=format,
                    snapshot_date=today,
                    usage_percentage=entry.get("usage_percentage"),
                    avg_copies=entry.get("avg_copies"),
                    sample_size=entry.get("sample_size"),
                )
                count += 1
            except Exception as exc:
                print(f"[sync_limitless]   Error syncing card usage for '{entry}': {exc}")

        await session.commit()

    print(f"[sync_limitless] Upserted {count} card usage records")
    return count


async def _find_card_by_name(session: AsyncSession, name: str) -> Card | None:
    """Find a card by its English name (case-insensitive, first match)."""
    stmt = select(Card).where(Card.name_en.ilike(name)).limit(1)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def _upsert_card_usage(
    session: AsyncSession,
    card_id: int,
    format_str: str,
    snapshot_date: date,
    usage_percentage: float | None,
    avg_copies: float | None,
    sample_size: int | None,
) -> CardUsageStats:
    """Insert or update a ``CardUsageStats`` row (unique on card+format+date)."""
    stmt = select(CardUsageStats).where(
        CardUsageStats.card_id == card_id,
        CardUsageStats.format == format_str,
        CardUsageStats.snapshot_date == snapshot_date,
    )
    result = await session.execute(stmt)
    stats = result.scalar_one_or_none()

    if stats is None:
        stats = CardUsageStats(
            card_id=card_id,
            format=format_str,
            snapshot_date=snapshot_date,
        )
        session.add(stats)

    stats.usage_percentage = usage_percentage
    stats.avg_copies = avg_copies
    stats.sample_size = sample_size
    return stats


# ---------------------------------------------------------------------------
# Deck usage sync
# ---------------------------------------------------------------------------

async def sync_deck_usage(format: str = "standard") -> int:
    """Fetch deck usage from Limitless and upsert ``DeckUsageStats`` rows.

    Returns the number of records upserted.
    """
    print(f"[sync_limitless] Fetching deck usage (format={format})...")
    usage_data = await fetch_deck_usage(format=format)
    if not usage_data:
        print("[sync_limitless] No deck usage data returned from Limitless")
        return 0

    today = date.today()
    count = 0

    async with async_session_factory() as session:
        for entry in usage_data:
            try:
                archetype = entry.get("archetype", "")
                if not archetype:
                    continue

                await _upsert_deck_usage(
                    session,
                    archetype=archetype,
                    format_str=format,
                    snapshot_date=today,
                    meta_share=entry.get("meta_share"),
                    avg_placement=entry.get("avg_placement"),
                    sample_size=entry.get("sample_size"),
                )
                count += 1
            except Exception as exc:
                print(f"[sync_limitless]   Error syncing deck usage for '{entry}': {exc}")

        await session.commit()

    print(f"[sync_limitless] Upserted {count} deck usage records")
    return count


async def _upsert_deck_usage(
    session: AsyncSession,
    archetype: str,
    format_str: str,
    snapshot_date: date,
    meta_share: float | None,
    avg_placement: float | None,
    sample_size: int | None,
) -> DeckUsageStats:
    """Insert or update a ``DeckUsageStats`` row (unique on archetype+format+date)."""
    stmt = select(DeckUsageStats).where(
        DeckUsageStats.archetype == archetype,
        DeckUsageStats.format == format_str,
        DeckUsageStats.snapshot_date == snapshot_date,
    )
    result = await session.execute(stmt)
    stats = result.scalar_one_or_none()

    if stats is None:
        stats = DeckUsageStats(
            archetype=archetype,
            format=format_str,
            snapshot_date=snapshot_date,
        )
        session.add(stats)

    stats.meta_share = meta_share
    stats.avg_placement = avg_placement
    stats.sample_size = sample_size
    return stats


# ---------------------------------------------------------------------------
# Full Limitless sync
# ---------------------------------------------------------------------------

async def sync_all_limitless(format: str = "standard") -> None:
    """Run both card and deck usage syncs."""
    await sync_card_usage(format=format)
    await sync_deck_usage(format=format)


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------

async def _main() -> None:
    await sync_all_limitless()


if __name__ == "__main__":
    asyncio.run(_main())
