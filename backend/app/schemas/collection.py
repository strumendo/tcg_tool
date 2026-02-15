"""Pydantic schemas for collection endpoints."""

from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.card import CardOut


class CollectionEntryOut(BaseModel):
    """Serialization schema for a user's collection entry."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    card_id: int
    quantity_owned: int
    card: Optional[CardOut] = None


class MissingCardOut(BaseModel):
    """A card missing from the user's collection for a specific deck."""

    card_id: int
    card_name: Optional[str] = None
    quantity_needed: int
    quantity_owned: int
    quantity_missing: int


class CollectionUpdate(BaseModel):
    """Schema for updating the quantity of a card in the user's collection."""

    quantity_owned: int
