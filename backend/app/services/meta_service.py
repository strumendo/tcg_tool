"""Service functions for meta-game operations."""

from collections import defaultdict

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import MetaDeck, MetaDeckCard, MetaMatchup
from app.models.card import Card
from app.schemas.meta import MetaTierGroup


async def get_meta_decks(db: AsyncSession) -> list[MetaDeck]:
    """Fetch all meta decks with their cards and matchups."""
    stmt = (
        select(MetaDeck)
        .options(
            selectinload(MetaDeck.meta_deck_cards)
            .selectinload(MetaDeckCard.card)
            .selectinload(Card.card_set),
            selectinload(MetaDeck.matchups_as_a),
            selectinload(MetaDeck.matchups_as_b),
        )
        .order_by(MetaDeck.tier, MetaDeck.id)
    )
    result = await db.execute(stmt)
    return list(result.scalars().unique().all())


async def get_meta_deck(db: AsyncSession, deck_id: str) -> MetaDeck:
    """Fetch a single meta deck by ID with all relationships."""
    stmt = (
        select(MetaDeck)
        .where(MetaDeck.id == deck_id)
        .options(
            selectinload(MetaDeck.meta_deck_cards)
            .selectinload(MetaDeckCard.card)
            .selectinload(Card.card_set),
            selectinload(MetaDeck.meta_deck_cards)
            .selectinload(MetaDeckCard.card)
            .selectinload(Card.abilities),
            selectinload(MetaDeck.meta_deck_cards)
            .selectinload(MetaDeckCard.card)
            .selectinload(Card.attacks),
            selectinload(MetaDeck.meta_deck_cards)
            .selectinload(MetaDeckCard.card)
            .selectinload(Card.functions),
            selectinload(MetaDeck.matchups_as_a),
            selectinload(MetaDeck.matchups_as_b),
        )
    )
    result = await db.execute(stmt)
    meta_deck = result.scalar_one_or_none()
    if meta_deck is None:
        raise HTTPException(
            status_code=404, detail=f"Meta deck '{deck_id}' not found"
        )
    return meta_deck


async def get_matchups(db: AsyncSession) -> list[MetaMatchup]:
    """Fetch all meta matchup records."""
    stmt = select(MetaMatchup).order_by(MetaMatchup.deck_a_id, MetaMatchup.deck_b_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_tiers(db: AsyncSession) -> list[MetaTierGroup]:
    """Fetch all meta decks grouped by tier."""
    decks = await get_meta_decks(db)

    tier_map: dict[int, list[MetaDeck]] = defaultdict(list)
    for deck in decks:
        tier = deck.tier or 3  # default to tier 3 if unset
        tier_map[tier].append(deck)

    groups = [
        MetaTierGroup(tier=tier, decks=deck_list)
        for tier, deck_list in sorted(tier_map.items())
    ]
    return groups
