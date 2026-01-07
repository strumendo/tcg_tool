"""Deck schemas"""
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from app.models.deck import DeckFormat
from app.schemas.card import CardRead


class DeckCardBase(BaseModel):
    """Base schema for DeckCard"""
    card_id: int
    quantity: int = 1


class DeckCardCreate(DeckCardBase):
    """Schema for adding a card to a deck"""
    pass


class DeckCardRead(DeckCardBase):
    """Schema for reading a deck card"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    card: Optional[CardRead] = None


class DeckBase(BaseModel):
    """Base schema for Deck"""
    name: str
    description: Optional[str] = None
    format: DeckFormat = DeckFormat.STANDARD
    archetype: Optional[str] = None
    is_active: bool = True
    is_public: bool = False


class DeckCreate(DeckBase):
    """Schema for creating a Deck"""
    cards: Optional[List[DeckCardCreate]] = None


class DeckUpdate(BaseModel):
    """Schema for updating a Deck"""
    name: Optional[str] = None
    description: Optional[str] = None
    format: Optional[DeckFormat] = None
    archetype: Optional[str] = None
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None


class DeckRead(DeckBase):
    """Schema for reading a Deck"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    external_id: Optional[str] = None
    source: Optional[str] = None
    total_cards: int
    pokemon_count: int
    trainer_count: int
    energy_count: int
    cards: List[DeckCardRead] = []
    created_at: datetime
    updated_at: datetime


class DeckListRead(BaseModel):
    """Schema for paginated deck list"""
    decks: List[DeckRead]
    total: int
    page: int
    page_size: int


class DeckImportRequest(BaseModel):
    """Schema for importing a deck from text/file"""
    deck_list: str  # Text format deck list
    name: Optional[str] = None
    format: DeckFormat = DeckFormat.STANDARD


class DeckSuggestionRequest(BaseModel):
    """Schema for requesting deck suggestions for a Pokémon"""
    pokemon_name: str  # Name of the Pokémon
    set_code: Optional[str] = None  # Collection/set code (e.g., "sv1", "sv4pt5")
    format: DeckFormat = DeckFormat.STANDARD


class SuggestedDeckInfo(BaseModel):
    """Schema for a suggested deck's information"""
    model_config = ConfigDict(from_attributes=True)

    archetype: str
    meta_rank: Optional[int] = None
    meta_share: Optional[float] = None
    win_rate: Optional[float] = None
    deck_id: Optional[int] = None
    core_cards: Optional[List[str]] = None
    matchup_summary: Optional[dict] = None
    reasoning: str  # Why this deck is suggested


class DeckSuggestionResponse(BaseModel):
    """Schema for deck suggestion results"""
    pokemon_name: str
    set_code: Optional[str] = None
    card_found: bool
    card_info: Optional[dict] = None  # Basic info about the Pokémon card
    suggestions: List[SuggestedDeckInfo] = []
    ai_analysis: Optional[str] = None  # AI-powered analysis of the Pokémon's potential
