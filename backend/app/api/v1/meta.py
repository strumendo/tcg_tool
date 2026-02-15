"""Meta-game API route handlers."""

from fastapi import APIRouter

from app.dependencies import DBSession
from app.schemas.meta import MetaDeckOut, MetaMatchupOut, MetaTierGroup
from app.services import meta_service

router = APIRouter()


@router.get("/decks", response_model=list[MetaDeckOut])
async def list_meta_decks(db: DBSession) -> list[MetaDeckOut]:
    """List all meta decks."""
    decks = await meta_service.get_meta_decks(db)
    return [MetaDeckOut.model_validate(d) for d in decks]


@router.get("/decks/{deck_id}", response_model=MetaDeckOut)
async def get_meta_deck(db: DBSession, deck_id: str) -> MetaDeckOut:
    """Get a single meta deck by ID."""
    deck = await meta_service.get_meta_deck(db, deck_id)
    return MetaDeckOut.model_validate(deck)


@router.get("/matchups", response_model=list[MetaMatchupOut])
async def list_matchups(db: DBSession) -> list[MetaMatchupOut]:
    """List all meta matchup records."""
    matchups = await meta_service.get_matchups(db)
    return [MetaMatchupOut.model_validate(m) for m in matchups]


@router.get("/tiers", response_model=list[MetaTierGroup])
async def list_tiers(db: DBSession) -> list[MetaTierGroup]:
    """List meta decks grouped by tier."""
    return await meta_service.get_tiers(db)
