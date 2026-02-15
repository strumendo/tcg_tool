"""Statistics API route handlers."""

from fastapi import APIRouter, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import DBSession
from app.models import Battle, CardUsageStats, Deck, DeckUsageStats, UserCollection
from app.schemas.stats import CardUsageStatsOut, DeckUsageStatsOut, UserStatsOut

router = APIRouter()

# Hardcoded user ID until authentication is implemented.
_USER_ID = 1


@router.get("/cards", response_model=list[CardUsageStatsOut])
async def list_card_usage_stats(
    db: DBSession,
    format: str = Query("Standard", description="Game format"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> list[CardUsageStatsOut]:
    """List card usage statistics."""
    stmt = (
        select(CardUsageStats)
        .where(CardUsageStats.format == format)
        .order_by(CardUsageStats.usage_percentage.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    stats = result.scalars().all()
    return [CardUsageStatsOut.model_validate(s) for s in stats]


@router.get("/decks", response_model=list[DeckUsageStatsOut])
async def list_deck_usage_stats(
    db: DBSession,
    format: str = Query("Standard", description="Game format"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> list[DeckUsageStatsOut]:
    """List deck archetype usage statistics."""
    stmt = (
        select(DeckUsageStats)
        .where(DeckUsageStats.format == format)
        .order_by(DeckUsageStats.meta_share.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    stats = result.scalars().all()
    return [DeckUsageStatsOut.model_validate(s) for s in stats]


@router.get("/user", response_model=UserStatsOut)
async def get_user_stats(db: DBSession) -> UserStatsOut:
    """Get aggregated statistics for the current user."""
    # Total decks
    total_decks_result = await db.execute(
        select(func.count(Deck.id)).where(Deck.user_id == _USER_ID)
    )
    total_decks = total_decks_result.scalar_one()

    # Battle stats
    battles_result = await db.execute(
        select(Battle.result, func.count(Battle.id))
        .where(Battle.user_id == _USER_ID)
        .group_by(Battle.result)
    )
    battle_rows = battles_result.all()

    total_battles = 0
    wins = 0
    losses = 0
    ties = 0
    for result_val, count in battle_rows:
        total_battles += count
        if result_val == "win":
            wins = count
        elif result_val == "loss":
            losses = count
        elif result_val == "tie":
            ties = count

    win_rate = 0.0
    if total_battles > 0:
        win_rate = round((wins / total_battles) * 100, 1)

    # Collection size
    collection_result = await db.execute(
        select(func.sum(UserCollection.quantity_owned)).where(
            UserCollection.user_id == _USER_ID
        )
    )
    collection_size = collection_result.scalar_one() or 0

    # Most played deck
    most_played_result = await db.execute(
        select(Deck.name, func.count(Battle.id).label("cnt"))
        .join(Battle, Battle.deck_id == Deck.id)
        .where(Battle.user_id == _USER_ID)
        .group_by(Deck.name)
        .order_by(func.count(Battle.id).desc())
        .limit(1)
    )
    most_played_row = most_played_result.first()
    most_played_deck = most_played_row[0] if most_played_row else None

    # Most faced archetype
    most_faced_result = await db.execute(
        select(Battle.opponent_deck_name, func.count(Battle.id).label("cnt"))
        .where(
            Battle.user_id == _USER_ID,
            Battle.opponent_deck_name.isnot(None),
        )
        .group_by(Battle.opponent_deck_name)
        .order_by(func.count(Battle.id).desc())
        .limit(1)
    )
    most_faced_row = most_faced_result.first()
    most_faced_archetype = most_faced_row[0] if most_faced_row else None

    return UserStatsOut(
        total_decks=total_decks,
        total_battles=total_battles,
        wins=wins,
        losses=losses,
        ties=ties,
        win_rate=win_rate,
        collection_size=collection_size,
        most_played_deck=most_played_deck,
        most_faced_archetype=most_faced_archetype,
    )
