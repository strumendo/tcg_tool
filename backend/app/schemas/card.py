"""Card and CardSet schemas"""
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from app.models.card import CardType, CardSubtype, EnergyType


class CardSetBase(BaseModel):
    """Base schema for CardSet"""
    code: str
    name: str
    series: Optional[str] = None
    release_date: Optional[str] = None
    total_cards: Optional[int] = None
    logo_url: Optional[str] = None
    symbol_url: Optional[str] = None


class CardSetCreate(CardSetBase):
    """Schema for creating a CardSet"""
    pass


class CardSetRead(CardSetBase):
    """Schema for reading a CardSet"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class CardBase(BaseModel):
    """Base schema for Card"""
    name: str
    card_type: CardType
    subtype: Optional[CardSubtype] = None
    limitless_id: Optional[str] = None
    ptcgo_code: Optional[str] = None
    set_number: Optional[str] = None
    hp: Optional[int] = None
    energy_type: Optional[EnergyType] = None
    weakness: Optional[str] = None
    resistance: Optional[str] = None
    retreat_cost: Optional[int] = None
    abilities: Optional[dict] = None
    attacks: Optional[dict] = None
    rules: Optional[str] = None
    image_small: Optional[str] = None
    image_large: Optional[str] = None
    rarity: Optional[str] = None
    artist: Optional[str] = None
    regulation_mark: Optional[str] = None
    is_standard_legal: bool = True
    is_expanded_legal: bool = True


class CardCreate(CardBase):
    """Schema for creating a Card"""
    set_id: Optional[int] = None


class CardRead(CardBase):
    """Schema for reading a Card"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    set_id: Optional[int] = None
    set: Optional[CardSetRead] = None
    created_at: datetime
    updated_at: datetime


class CardListRead(BaseModel):
    """Schema for paginated card list"""
    cards: List[CardRead]
    total: int
    page: int
    page_size: int
