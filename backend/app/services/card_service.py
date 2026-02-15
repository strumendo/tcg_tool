"""Service functions for card-related operations."""

from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Card, CardAbility, CardFunction, CardUsageStats


async def search_cards(
    db: AsyncSession,
    query: Optional[str] = None,
    card_type: Optional[str] = None,
    ability_category: Optional[str] = None,
    energy_type: Optional[str] = None,
    regulation_mark: Optional[str] = None,
    set_code: Optional[str] = None,
    is_ex: Optional[bool] = None,
    limit: int = 20,
    offset: int = 0,
) -> list[Card]:
    """Search and filter cards with optional criteria."""
    stmt = (
        select(Card)
        .options(
            selectinload(Card.card_set),
            selectinload(Card.abilities),
            selectinload(Card.attacks),
            selectinload(Card.functions),
        )
    )

    if query:
        stmt = stmt.where(
            Card.name_en.ilike(f"%{query}%") | Card.name_pt.ilike(f"%{query}%")
        )

    if card_type:
        stmt = stmt.where(Card.card_type == card_type)

    if energy_type:
        stmt = stmt.where(Card.energy_type == energy_type)

    if regulation_mark:
        stmt = stmt.where(Card.regulation_mark == regulation_mark)

    if is_ex is not None:
        stmt = stmt.where(Card.is_ex == is_ex)

    if set_code:
        from app.models import CardSet
        stmt = stmt.join(Card.card_set).where(CardSet.code == set_code)

    if ability_category:
        stmt = stmt.join(Card.abilities).where(
            CardAbility.category == ability_category
        )

    stmt = stmt.order_by(Card.id).offset(offset).limit(limit)

    result = await db.execute(stmt)
    return list(result.scalars().unique().all())


async def get_card(db: AsyncSession, card_id: int) -> Card:
    """Fetch a single card by ID with all relationships."""
    stmt = (
        select(Card)
        .where(Card.id == card_id)
        .options(
            selectinload(Card.card_set),
            selectinload(Card.abilities),
            selectinload(Card.attacks),
            selectinload(Card.functions),
        )
    )
    result = await db.execute(stmt)
    card = result.scalar_one_or_none()
    if card is None:
        raise HTTPException(status_code=404, detail=f"Card {card_id} not found")
    return card


async def get_card_alternatives(db: AsyncSession, card_id: int) -> list[Card]:
    """Find alternative cards with the same function(s) or similar role.

    Looks for cards that share at least one functional tag with the target card
    and belong to a different set or have a different set number.
    """
    card = await get_card(db, card_id)

    # Get the functions of the target card
    func_names = [f.function for f in card.functions]

    if not func_names:
        # Fall back: find cards with the same card_type and trainer_subtype
        stmt = (
            select(Card)
            .where(
                Card.card_type == card.card_type,
                Card.id != card.id,
            )
            .options(
                selectinload(Card.card_set),
                selectinload(Card.abilities),
                selectinload(Card.attacks),
                selectinload(Card.functions),
            )
        )
        if card.trainer_subtype:
            stmt = stmt.where(Card.trainer_subtype == card.trainer_subtype)
        stmt = stmt.limit(10)
        result = await db.execute(stmt)
        return list(result.scalars().unique().all())

    # Find cards that share any function with the target card
    stmt = (
        select(Card)
        .join(Card.functions)
        .where(
            CardFunction.function.in_(func_names),
            Card.id != card.id,
        )
        .options(
            selectinload(Card.card_set),
            selectinload(Card.abilities),
            selectinload(Card.attacks),
            selectinload(Card.functions),
        )
        .limit(10)
    )
    result = await db.execute(stmt)
    return list(result.scalars().unique().all())


async def get_card_usage(db: AsyncSession, card_id: int) -> list[CardUsageStats]:
    """Fetch usage statistics for a card."""
    # Verify card exists
    await get_card(db, card_id)

    stmt = (
        select(CardUsageStats)
        .where(CardUsageStats.card_id == card_id)
        .order_by(CardUsageStats.snapshot_date.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_ability_categories(db: AsyncSession) -> list[str]:
    """Return all distinct ability categories."""
    stmt = (
        select(distinct(CardAbility.category))
        .where(CardAbility.category.isnot(None))
        .order_by(CardAbility.category)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
