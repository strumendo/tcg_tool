"""Card endpoints"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.db import get_db
from app.models.card import Card, CardSet, CardType
from app.schemas.card import (
    CardCreate, CardRead, CardListRead,
    CardSetCreate, CardSetRead
)

router = APIRouter()


@router.get("", response_model=CardListRead)
async def list_cards(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    card_type: Optional[CardType] = None,
    name: Optional[str] = None,
    set_code: Optional[str] = None,
    standard_only: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """List cards with optional filters"""
    query = select(Card).options(selectinload(Card.set))

    # Apply filters
    if card_type:
        query = query.where(Card.card_type == card_type)
    if name:
        query = query.where(Card.name.ilike(f"%{name}%"))
    if set_code:
        query = query.join(CardSet).where(CardSet.code == set_code)
    if standard_only:
        query = query.where(Card.is_standard_legal == True)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    cards = result.scalars().all()

    return CardListRead(
        cards=[CardRead.model_validate(c) for c in cards],
        total=total or 0,
        page=page,
        page_size=page_size
    )


@router.get("/{card_id}", response_model=CardRead)
async def get_card(card_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific card by ID"""
    query = select(Card).options(selectinload(Card.set)).where(Card.id == card_id)
    result = await db.execute(query)
    card = result.scalar_one_or_none()

    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    return CardRead.model_validate(card)


@router.post("", response_model=CardRead)
async def create_card(card: CardCreate, db: AsyncSession = Depends(get_db)):
    """Create a new card"""
    db_card = Card(**card.model_dump())
    db.add(db_card)
    await db.flush()
    await db.refresh(db_card)
    return CardRead.model_validate(db_card)


@router.post("/import", response_model=dict)
async def import_cards(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Import cards from a JSON or CSV file"""
    from app.services.card_import import CardImportService

    content = await file.read()
    filename = file.filename or "unknown"

    import_service = CardImportService(db)

    if filename.endswith(".json"):
        result = await import_service.import_from_json(content)
    elif filename.endswith(".csv"):
        result = await import_service.import_from_csv(content)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Use .json or .csv")

    return result


# Card Sets endpoints
@router.get("/sets/", response_model=list[CardSetRead])
async def list_sets(db: AsyncSession = Depends(get_db)):
    """List all card sets"""
    result = await db.execute(select(CardSet).order_by(CardSet.release_date.desc()))
    sets = result.scalars().all()
    return [CardSetRead.model_validate(s) for s in sets]


@router.post("/sets/", response_model=CardSetRead)
async def create_set(card_set: CardSetCreate, db: AsyncSession = Depends(get_db)):
    """Create a new card set"""
    db_set = CardSet(**card_set.model_dump())
    db.add(db_set)
    await db.flush()
    await db.refresh(db_set)
    return CardSetRead.model_validate(db_set)
