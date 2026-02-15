"""Pydantic schemas for meta-game endpoints."""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.card import CardOut


class MetaDeckCardOut(BaseModel):
    """Serialization schema for a card entry within a meta deck."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    meta_deck_id: str
    card_id: int
    quantity: int
    card: Optional[CardOut] = None


class MetaMatchupOut(BaseModel):
    """Serialization schema for a matchup between two meta decks."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    deck_a_id: str
    deck_b_id: str
    win_rate_a: Optional[float] = None
    notes_en: Optional[str] = None
    notes_pt: Optional[str] = None
    snapshot_date: Optional[date] = None


class MetaDeckOut(BaseModel):
    """Serialization schema for a meta deck archetype."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name_en: Optional[str] = None
    name_pt: Optional[str] = None
    tier: Optional[int] = None
    description_en: Optional[str] = None
    description_pt: Optional[str] = None
    strategy_en: Optional[str] = None
    strategy_pt: Optional[str] = None
    difficulty: Optional[str] = None
    meta_share: Optional[float] = None
    key_pokemon: Optional[dict] = None
    energy_types: Optional[dict] = None
    strengths_en: Optional[dict] = None
    strengths_pt: Optional[dict] = None
    weaknesses_en: Optional[dict] = None
    weaknesses_pt: Optional[dict] = None
    snapshot_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    meta_deck_cards: list[MetaDeckCardOut] = []
    matchups_as_a: list[MetaMatchupOut] = []
    matchups_as_b: list[MetaMatchupOut] = []


class MetaTierGroup(BaseModel):
    """A group of meta decks at the same tier level."""

    tier: int
    decks: list[MetaDeckOut] = []
