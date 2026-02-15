"""Pydantic schemas for card-related endpoints."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CardSetOut(BaseModel):
    """Serialization schema for a card set."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    tcgdex_id: Optional[str] = None
    name_en: Optional[str] = None
    name_pt: Optional[str] = None
    regulation_mark: Optional[str] = None
    release_date: Optional[datetime] = None
    total_cards: Optional[int] = None
    is_legal: bool


class CardAbilityOut(BaseModel):
    """Serialization schema for a card ability."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    card_id: int
    name_en: Optional[str] = None
    name_pt: Optional[str] = None
    effect_en: Optional[str] = None
    effect_pt: Optional[str] = None
    category: Optional[str] = None


class CardAttackOut(BaseModel):
    """Serialization schema for a card attack."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    card_id: int
    name_en: Optional[str] = None
    name_pt: Optional[str] = None
    damage: Optional[str] = None
    energy_cost: Optional[dict] = None
    effect_en: Optional[str] = None
    effect_pt: Optional[str] = None


class CardFunctionOut(BaseModel):
    """Serialization schema for a card function mapping."""

    model_config = ConfigDict(from_attributes=True)

    card_id: int
    function: str


class CardOut(BaseModel):
    """Serialization schema for a card with nested relationships."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name_en: Optional[str] = None
    name_pt: Optional[str] = None
    card_type: str
    trainer_subtype: Optional[str] = None
    set_id: Optional[int] = None
    set_number: Optional[str] = None
    regulation_mark: Optional[str] = None
    hp: Optional[int] = None
    energy_type: Optional[str] = None
    stage: Optional[str] = None
    is_ex: bool
    image_url: Optional[str] = None
    image_url_hires: Optional[str] = None
    tcgdex_id: Optional[str] = None
    pokemontcg_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    card_set: Optional[CardSetOut] = None
    abilities: list[CardAbilityOut] = []
    attacks: list[CardAttackOut] = []
    functions: list[CardFunctionOut] = []


class CardSearchQuery(BaseModel):
    """Query parameters for card search."""

    query: Optional[str] = None
    card_type: Optional[str] = None
    ability_category: Optional[str] = None
    energy_type: Optional[str] = None
    regulation_mark: Optional[str] = None
    set_code: Optional[str] = None
    is_ex: Optional[bool] = None
    limit: int = 20
    offset: int = 0
