"""Pydantic schemas for battle-related endpoints."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BattleActionOut(BaseModel):
    """Serialization schema for an individual battle action."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    battle_id: int
    turn: int
    player: str
    action_type: str
    card_name: Optional[str] = None
    details: Optional[str] = None
    sequence_order: int


class BattleOut(BaseModel):
    """Serialization schema for a battle record."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    deck_id: Optional[int] = None
    opponent_deck_name: Optional[str] = None
    opponent_meta_deck_id: Optional[str] = None
    result: Optional[str] = None
    total_turns: Optional[int] = None
    went_first: Optional[bool] = None
    notes: Optional[str] = None
    source: str
    source_url: Optional[str] = None
    played_at: datetime
    created_at: datetime

    actions: list[BattleActionOut] = []


class BattleActionInput(BaseModel):
    """Input schema for a single battle action."""

    turn: int
    player: str
    action_type: str
    card_name: Optional[str] = None
    details: Optional[str] = None
    sequence_order: int


class BattleCreate(BaseModel):
    """Schema for creating a battle record."""

    deck_id: Optional[int] = None
    opponent_deck_name: Optional[str] = None
    opponent_meta_deck_id: Optional[str] = None
    result: Optional[str] = None
    total_turns: Optional[int] = None
    went_first: Optional[bool] = None
    notes: Optional[str] = None
    source: str = "manual"
    source_url: Optional[str] = None
    played_at: Optional[datetime] = None
    actions: list[BattleActionInput] = []


class BattleUpdate(BaseModel):
    """Schema for updating a battle record."""

    opponent_deck_name: Optional[str] = None
    opponent_meta_deck_id: Optional[str] = None
    result: Optional[str] = None
    total_turns: Optional[int] = None
    went_first: Optional[bool] = None
    notes: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
