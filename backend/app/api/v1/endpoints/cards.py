"""Card endpoints"""
from typing import Optional, Literal
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.db import get_db
from app.models.card import Card, CardSet, CardType, CardSubtype, EnergyType
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
    subtype: Optional[CardSubtype] = None,
    energy_type: Optional[EnergyType] = None,
    name: Optional[str] = None,
    set_code: Optional[str] = None,
    rarity: Optional[str] = None,
    regulation_mark: Optional[str] = None,
    standard_only: bool = False,
    sort_by: Literal["name", "hp", "set_number", "created_at"] = "name",
    sort_order: Literal["asc", "desc"] = "asc",
    db: AsyncSession = Depends(get_db)
):
    """List cards with filters and sorting"""
    query = select(Card).options(selectinload(Card.set))

    # Apply filters
    if card_type:
        query = query.where(Card.card_type == card_type)
    if subtype:
        query = query.where(Card.subtype == subtype)
    if energy_type:
        query = query.where(Card.energy_type == energy_type)
    if name:
        query = query.where(Card.name.ilike(f"%{name}%"))
    if set_code:
        query = query.join(CardSet).where(CardSet.code == set_code)
    if rarity:
        query = query.where(Card.rarity.ilike(f"%{rarity}%"))
    if regulation_mark:
        query = query.where(Card.regulation_mark == regulation_mark)
    if standard_only:
        query = query.where(Card.is_standard_legal == True)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Apply sorting
    sort_column = getattr(Card, sort_by, Card.name)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

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


@router.get("/search", response_model=CardListRead)
async def search_cards(
    q: str = Query(..., min_length=2, description="Search query"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Quick search cards by name (for autocomplete)"""
    query = select(Card).options(selectinload(Card.set)).where(
        Card.name.ilike(f"%{q}%")
    ).order_by(Card.name).offset((page - 1) * page_size).limit(page_size)

    count_query = select(func.count()).select_from(
        select(Card).where(Card.name.ilike(f"%{q}%")).subquery()
    )
    total = await db.scalar(count_query)

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


# Sync endpoints (Pokemon TCG API)
@router.post("/sync/sets")
async def sync_sets(db: AsyncSession = Depends(get_db)):
    """Sync all card sets from Pokemon TCG API"""
    from app.services.card_sync import CardSyncService

    sync_service = CardSyncService(db)
    result = await sync_service.sync_all_sets()
    return result


@router.post("/sync/set/{set_code}")
async def sync_set_cards(set_code: str, db: AsyncSession = Depends(get_db)):
    """Sync all cards from a specific set"""
    from app.services.card_sync import CardSyncService

    sync_service = CardSyncService(db)
    result = await sync_service.sync_set_cards(set_code)
    return result


@router.post("/sync/standard")
async def sync_standard_cards(db: AsyncSession = Depends(get_db)):
    """Sync all standard legal cards from Pokemon TCG API"""
    from app.services.card_sync import CardSyncService

    sync_service = CardSyncService(db)
    result = await sync_service.sync_standard_legal_cards()
    return result


@router.get("/api/search")
async def search_api_cards(
    q: str = Query(..., min_length=2, description="Search query"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    lang: str = Query("en", description="Language code (en, fr, de, es, it, pt, ja, zh-tw, id, th)"),
    db: AsyncSession = Depends(get_db)
):
    """Search cards from TCGdex (multilingual) with Pokemon TCG API fallback"""
    from app.services.card_api import DualCardApiService

    api_service = DualCardApiService(db, language=lang)
    result = await api_service.search_cards(q, page, page_size)
    return result


@router.get("/api/card/{card_id}")
async def get_api_card(
    card_id: str,
    lang: str = Query("en", description="Language code"),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific card from external API with multilingual support"""
    from app.services.card_api import DualCardApiService

    api_service = DualCardApiService(db, language=lang)
    result = await api_service.get_card(card_id)
    if not result:
        raise HTTPException(status_code=404, detail="Card not found")
    return result


@router.get("/api/sets")
async def get_api_sets(
    lang: str = Query("en", description="Language code"),
    db: AsyncSession = Depends(get_db)
):
    """Get all card sets from external API with multilingual support"""
    from app.services.card_api import DualCardApiService

    api_service = DualCardApiService(db, language=lang)
    return await api_service.get_sets()


@router.get("/api/set/{set_id}")
async def get_api_set(
    set_id: str,
    lang: str = Query("en", description="Language code"),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific set from external API"""
    from app.services.card_api import DualCardApiService

    api_service = DualCardApiService(db, language=lang)
    result = await api_service.get_set(set_id)
    if not result:
        raise HTTPException(status_code=404, detail="Set not found")
    return result


@router.get("/api/set/{set_id}/cards")
async def get_api_set_cards(
    set_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=250),
    lang: str = Query("en", description="Language code"),
    db: AsyncSession = Depends(get_db)
):
    """Get all cards from a specific set with multilingual support"""
    from app.services.card_api import DualCardApiService

    api_service = DualCardApiService(db, language=lang)
    return await api_service.get_set_cards(set_id, page, page_size)


@router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages for card data"""
    from app.core.config import settings
    return {
        "default": settings.default_language,
        "supported": [
            {"code": "en", "name": "English"},
            {"code": "fr", "name": "Français"},
            {"code": "de", "name": "Deutsch"},
            {"code": "es", "name": "Español"},
            {"code": "it", "name": "Italiano"},
            {"code": "pt", "name": "Português"},
            {"code": "ja", "name": "日本語"},
            {"code": "zh-tw", "name": "繁體中文"},
            {"code": "id", "name": "Bahasa Indonesia"},
            {"code": "th", "name": "ภาษาไทย"},
        ]
    }
