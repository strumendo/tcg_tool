"""Match schemas"""
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from app.models.match import MatchResult, ActionType


class MatchActionBase(BaseModel):
    """Base schema for MatchAction"""
    turn_number: int
    action_order: int
    is_player_action: bool = True
    action_type: ActionType
    card_name: Optional[str] = None
    target_card: Optional[str] = None
    description: Optional[str] = None
    damage_dealt: Optional[int] = None


class MatchActionCreate(MatchActionBase):
    """Schema for creating a MatchAction"""
    pass


class MatchActionRead(MatchActionBase):
    """Schema for reading a MatchAction"""
    model_config = ConfigDict(from_attributes=True)

    id: int


class MatchBase(BaseModel):
    """Base schema for Match"""
    deck_id: Optional[int] = None
    opponent_deck_archetype: Optional[str] = None
    result: Optional[MatchResult] = None
    player_prizes_taken: int = 0
    opponent_prizes_taken: int = 0
    total_turns: Optional[int] = None
    went_first: Optional[bool] = None
    match_date: Optional[datetime] = None
    notes: Optional[str] = None


class MatchCreate(MatchBase):
    """Schema for creating a Match"""
    actions: Optional[List[MatchActionCreate]] = None


class MatchRead(MatchBase):
    """Schema for reading a Match"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    import_source: Optional[str] = None
    raw_data: Optional[str] = None
    actions: List[MatchActionRead] = []
    created_at: datetime
    updated_at: datetime


class MatchListRead(BaseModel):
    """Schema for paginated match list"""
    matches: List[MatchRead]
    total: int
    page: int
    page_size: int


class MatchImportRequest(BaseModel):
    """Schema for importing match from OCR/file"""
    image_data: Optional[str] = None  # Base64 encoded image
    text_data: Optional[str] = None   # Raw text data
    deck_id: Optional[int] = None
