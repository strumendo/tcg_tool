"""Deck endpoints"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.db import get_db
from app.models.deck import Deck, DeckCard, DeckFormat
from app.models.card import Card, CardType
from app.schemas.deck import (
    DeckCreate, DeckRead, DeckUpdate, DeckListRead,
    DeckCardCreate, DeckImportRequest
)

router = APIRouter()


@router.get("", response_model=DeckListRead)
async def list_decks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    format: Optional[DeckFormat] = None,
    archetype: Optional[str] = None,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """List all decks with optional filters"""
    query = select(Deck).options(
        selectinload(Deck.cards).selectinload(DeckCard.card)
    )

    if format:
        query = query.where(Deck.format == format)
    if archetype:
        query = query.where(Deck.archetype.ilike(f"%{archetype}%"))
    if active_only:
        query = query.where(Deck.is_active == True)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(Deck.updated_at.desc())
    result = await db.execute(query)
    decks = result.scalars().unique().all()

    return DeckListRead(
        decks=[DeckRead.model_validate(d) for d in decks],
        total=total or 0,
        page=page,
        page_size=page_size
    )


@router.get("/{deck_id}", response_model=DeckRead)
async def get_deck(deck_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific deck by ID"""
    query = select(Deck).options(
        selectinload(Deck.cards).selectinload(DeckCard.card).selectinload(Card.set)
    ).where(Deck.id == deck_id)

    result = await db.execute(query)
    deck = result.scalar_one_or_none()

    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")

    return DeckRead.model_validate(deck)


@router.post("", response_model=DeckRead)
async def create_deck(deck: DeckCreate, db: AsyncSession = Depends(get_db)):
    """Create a new deck"""
    deck_data = deck.model_dump(exclude={"cards"})
    db_deck = Deck(**deck_data)
    db.add(db_deck)
    await db.flush()

    # Add cards if provided
    if deck.cards:
        await _add_cards_to_deck(db, db_deck, deck.cards)

    await db.refresh(db_deck)
    return DeckRead.model_validate(db_deck)


@router.put("/{deck_id}", response_model=DeckRead)
async def update_deck(
    deck_id: int,
    deck_update: DeckUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a deck"""
    query = select(Deck).where(Deck.id == deck_id)
    result = await db.execute(query)
    deck = result.scalar_one_or_none()

    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")

    update_data = deck_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(deck, field, value)

    await db.flush()
    await db.refresh(deck)
    return DeckRead.model_validate(deck)


@router.delete("/{deck_id}")
async def delete_deck(deck_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a deck"""
    query = select(Deck).where(Deck.id == deck_id)
    result = await db.execute(query)
    deck = result.scalar_one_or_none()

    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")

    await db.delete(deck)
    return {"message": "Deck deleted successfully"}


@router.post("/{deck_id}/cards", response_model=DeckRead)
async def add_card_to_deck(
    deck_id: int,
    card_data: DeckCardCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add a card to a deck"""
    query = select(Deck).options(
        selectinload(Deck.cards)
    ).where(Deck.id == deck_id)
    result = await db.execute(query)
    deck = result.scalar_one_or_none()

    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")

    await _add_cards_to_deck(db, deck, [card_data])
    await db.refresh(deck)
    return DeckRead.model_validate(deck)


@router.post("/import", response_model=DeckRead)
async def import_deck(
    import_request: DeckImportRequest,
    db: AsyncSession = Depends(get_db)
):
    """Import a deck from text format"""
    from app.services.deck_import import DeckImportService

    import_service = DeckImportService(db)
    deck = await import_service.import_from_text(
        deck_list=import_request.deck_list,
        name=import_request.name,
        format=import_request.format
    )
    return DeckRead.model_validate(deck)


@router.post("/import/file", response_model=DeckRead)
async def import_deck_from_file(
    file: UploadFile = File(...),
    name: Optional[str] = None,
    format: DeckFormat = DeckFormat.STANDARD,
    db: AsyncSession = Depends(get_db)
):
    """Import a deck from a file"""
    from app.services.deck_import import DeckImportService

    content = await file.read()
    import_service = DeckImportService(db)

    deck = await import_service.import_from_text(
        deck_list=content.decode("utf-8"),
        name=name or file.filename,
        format=format
    )
    return DeckRead.model_validate(deck)


async def _add_cards_to_deck(
    db: AsyncSession,
    deck: Deck,
    cards: list[DeckCardCreate]
):
    """Helper to add cards to a deck and update counts"""
    pokemon_count = 0
    trainer_count = 0
    energy_count = 0
    total_count = 0

    for card_data in cards:
        # Verify card exists
        card_query = select(Card).where(Card.id == card_data.card_id)
        card_result = await db.execute(card_query)
        card = card_result.scalar_one_or_none()

        if not card:
            continue

        deck_card = DeckCard(
            deck_id=deck.id,
            card_id=card_data.card_id,
            quantity=card_data.quantity
        )
        db.add(deck_card)

        # Update counts
        total_count += card_data.quantity
        if card.card_type == CardType.POKEMON:
            pokemon_count += card_data.quantity
        elif card.card_type == CardType.TRAINER:
            trainer_count += card_data.quantity
        elif card.card_type == CardType.ENERGY:
            energy_count += card_data.quantity

    deck.total_cards = total_count
    deck.pokemon_count = pokemon_count
    deck.trainer_count = trainer_count
    deck.energy_count = energy_count
