"""Card API route handlers."""

from typing import Optional

from fastapi import APIRouter, Query

from app.dependencies import DBSession
from app.schemas.card import CardOut, CardSearchQuery
from app.schemas.stats import CardUsageStatsOut
from app.services import card_service

router = APIRouter()


@router.get("/", response_model=list[CardOut])
async def list_cards(
    db: DBSession,
    query: Optional[str] = Query(None, description="Search by card name"),
    card_type: Optional[str] = Query(None, description="Filter by card type"),
    ability_category: Optional[str] = Query(None, description="Filter by ability category"),
    energy_type: Optional[str] = Query(None, description="Filter by energy type"),
    regulation_mark: Optional[str] = Query(None, description="Filter by regulation mark"),
    set_code: Optional[str] = Query(None, description="Filter by set code"),
    is_ex: Optional[bool] = Query(None, description="Filter ex cards"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
) -> list[CardOut]:
    """Search and list cards with optional filters."""
    cards = await card_service.search_cards(
        db,
        query=query,
        card_type=card_type,
        ability_category=ability_category,
        energy_type=energy_type,
        regulation_mark=regulation_mark,
        set_code=set_code,
        is_ex=is_ex,
        limit=limit,
        offset=offset,
    )
    return [CardOut.model_validate(c) for c in cards]


@router.get("/abilities", response_model=list[str])
async def list_ability_categories(db: DBSession) -> list[str]:
    """List all distinct ability categories."""
    return await card_service.get_ability_categories(db)


@router.get("/{card_id}", response_model=CardOut)
async def get_card(db: DBSession, card_id: int) -> CardOut:
    """Get a single card by ID."""
    card = await card_service.get_card(db, card_id)
    return CardOut.model_validate(card)


@router.get("/{card_id}/alternatives", response_model=list[CardOut])
async def get_card_alternatives(db: DBSession, card_id: int) -> list[CardOut]:
    """Get alternative cards with similar function."""
    cards = await card_service.get_card_alternatives(db, card_id)
    return [CardOut.model_validate(c) for c in cards]


@router.get("/{card_id}/usage", response_model=list[CardUsageStatsOut])
async def get_card_usage(db: DBSession, card_id: int) -> list[CardUsageStatsOut]:
    """Get usage statistics for a card."""
    stats = await card_service.get_card_usage(db, card_id)
    return [CardUsageStatsOut.model_validate(s) for s in stats]
