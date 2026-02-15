"""Pydantic schemas for deck-related endpoints."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.card import CardOut


class DeckCardOut(BaseModel):
    """Serialization schema for a card entry within a deck."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    deck_id: int
    card_id: int
    quantity: int
    card: Optional[CardOut] = None


class DeckOut(BaseModel):
    """Serialization schema for a user deck."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    archetype: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool
    is_valid: bool
    total_cards: int
    created_at: datetime
    updated_at: datetime

    deck_cards: list[DeckCardOut] = []


class DeckCardInput(BaseModel):
    """Input schema for a single card in a deck."""

    card_id: int
    quantity: int


class DeckCreate(BaseModel):
    """Schema for creating a new deck."""

    name: str
    archetype: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool = False
    cards: list[DeckCardInput] = []


class DeckImport(BaseModel):
    """Schema for importing a deck from PTCGO/TCG Live text format."""

    name: str
    deck_text: str


class DeckUpdate(BaseModel):
    """Schema for updating a deck."""

    name: Optional[str] = None
    archetype: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    cards: Optional[list[DeckCardInput]] = None
