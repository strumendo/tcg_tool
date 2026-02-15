"""Collection API route handlers."""

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dependencies import DBSession
from app.models import Card, UserCollection
from app.schemas.collection import CollectionEntryOut, CollectionUpdate, MissingCardOut
from app.services import deck_service

router = APIRouter()

# Hardcoded user ID until authentication is implemented.
_USER_ID = 1


@router.get("/", response_model=list[CollectionEntryOut])
async def list_collection(db: DBSession) -> list[CollectionEntryOut]:
    """List all cards in the current user's collection."""
    stmt = (
        select(UserCollection)
        .where(UserCollection.user_id == _USER_ID)
        .options(
            selectinload(UserCollection.card).selectinload(Card.card_set),
            selectinload(UserCollection.card).selectinload(Card.abilities),
            selectinload(UserCollection.card).selectinload(Card.attacks),
            selectinload(UserCollection.card).selectinload(Card.functions),
        )
        .order_by(UserCollection.card_id)
    )
    result = await db.execute(stmt)
    entries = result.scalars().unique().all()
    return [CollectionEntryOut.model_validate(e) for e in entries]


@router.put("/{card_id}", response_model=CollectionEntryOut)
async def update_collection_entry(
    db: DBSession, card_id: int, data: CollectionUpdate
) -> CollectionEntryOut:
    """Update the owned quantity for a card in the user's collection.

    Creates a new entry if the card is not already in the collection.
    """
    stmt = select(UserCollection).where(
        UserCollection.user_id == _USER_ID,
        UserCollection.card_id == card_id,
    )
    result = await db.execute(stmt)
    entry = result.scalar_one_or_none()

    if entry is None:
        # Verify card exists
        card_result = await db.execute(select(Card).where(Card.id == card_id))
        if card_result.scalar_one_or_none() is None:
            raise HTTPException(status_code=404, detail=f"Card {card_id} not found")

        entry = UserCollection(
            user_id=_USER_ID,
            card_id=card_id,
            quantity_owned=data.quantity_owned,
        )
        db.add(entry)
    else:
        entry.quantity_owned = data.quantity_owned

    await db.commit()

    # Reload with relationships
    stmt = (
        select(UserCollection)
        .where(UserCollection.id == entry.id)
        .options(
            selectinload(UserCollection.card).selectinload(Card.card_set),
            selectinload(UserCollection.card).selectinload(Card.abilities),
            selectinload(UserCollection.card).selectinload(Card.attacks),
            selectinload(UserCollection.card).selectinload(Card.functions),
        )
    )
    result = await db.execute(stmt)
    entry = result.scalar_one()
    return CollectionEntryOut.model_validate(entry)


@router.get("/missing/{deck_id}", response_model=list[MissingCardOut])
async def get_missing_cards(db: DBSession, deck_id: int) -> list[MissingCardOut]:
    """Get cards missing from the user's collection for a specific deck."""
    return await deck_service.get_deck_missing_cards(db, deck_id, _USER_ID)
