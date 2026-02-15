"""Deck API route handlers."""

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from app.dependencies import DBSession
from app.schemas.collection import MissingCardOut
from app.schemas.deck import DeckCreate, DeckImport, DeckOut, DeckUpdate
from app.services import deck_service

router = APIRouter()

# Hardcoded user ID until authentication is implemented.
_USER_ID = 1


@router.get("/", response_model=list[DeckOut])
async def list_decks(db: DBSession) -> list[DeckOut]:
    """List all decks for the current user."""
    decks = await deck_service.get_user_decks(db, _USER_ID)
    return [DeckOut.model_validate(d) for d in decks]


@router.post("/", response_model=DeckOut, status_code=201)
async def create_deck(db: DBSession, data: DeckCreate) -> DeckOut:
    """Create a new deck."""
    deck = await deck_service.create_deck(db, _USER_ID, data)
    return DeckOut.model_validate(deck)


@router.post("/import", response_model=DeckOut, status_code=201)
async def import_deck(db: DBSession, data: DeckImport) -> DeckOut:
    """Import a deck from PTCGO/TCG Live text format."""
    deck = await deck_service.import_deck(db, _USER_ID, data)
    return DeckOut.model_validate(deck)


@router.get("/{deck_id}", response_model=DeckOut)
async def get_deck(db: DBSession, deck_id: int) -> DeckOut:
    """Get a single deck by ID with all cards."""
    deck = await deck_service.get_deck(db, deck_id)
    return DeckOut.model_validate(deck)


@router.put("/{deck_id}", response_model=DeckOut)
async def update_deck(db: DBSession, deck_id: int, data: DeckUpdate) -> DeckOut:
    """Update a deck's metadata and/or card list."""
    deck = await deck_service.update_deck(db, deck_id, data)
    return DeckOut.model_validate(deck)


@router.delete("/{deck_id}", status_code=204)
async def delete_deck(db: DBSession, deck_id: int) -> None:
    """Delete a deck."""
    await deck_service.delete_deck(db, deck_id)


@router.get("/{deck_id}/export", response_class=PlainTextResponse)
async def export_deck(db: DBSession, deck_id: int) -> str:
    """Export a deck to PTCGO/TCG Live text format."""
    return await deck_service.export_deck(db, deck_id)


@router.get("/{deck_id}/missing", response_model=list[MissingCardOut])
async def get_missing_cards(db: DBSession, deck_id: int) -> list[MissingCardOut]:
    """Get cards missing from the user's collection for a deck."""
    return await deck_service.get_deck_missing_cards(db, deck_id, _USER_ID)
