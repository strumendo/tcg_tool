"""Meta/competitive data schemas"""
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class MetaDeckBase(BaseModel):
    """Base schema for MetaDeck"""
    archetype: str
    rank: int
    meta_share: float
    play_rate: Optional[float] = None
    win_rate: Optional[float] = None
    matchups: Optional[dict] = None
    sample_deck_id: Optional[int] = None
    core_cards: Optional[list] = None
    day2_conversion: Optional[float] = None
    top8_count: Optional[int] = None
    top16_count: Optional[int] = None


class MetaDeckCreate(MetaDeckBase):
    """Schema for creating a MetaDeck"""
    pass


class MetaDeckRead(MetaDeckBase):
    """Schema for reading a MetaDeck"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    snapshot_id: int
    created_at: datetime
    updated_at: datetime


class MetaSnapshotBase(BaseModel):
    """Base schema for MetaSnapshot"""
    name: str
    description: Optional[str] = None
    snapshot_date: datetime
    source: Optional[str] = None
    external_id: Optional[str] = None
    tournament_name: Optional[str] = None
    total_players: Optional[int] = None


class MetaSnapshotCreate(MetaSnapshotBase):
    """Schema for creating a MetaSnapshot"""
    meta_decks: Optional[List[MetaDeckCreate]] = None


class MetaSnapshotRead(MetaSnapshotBase):
    """Schema for reading a MetaSnapshot"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    meta_decks: List[MetaDeckRead] = []
    created_at: datetime
    updated_at: datetime


class MetaSnapshotListRead(BaseModel):
    """Schema for paginated snapshot list"""
    snapshots: List[MetaSnapshotRead]
    total: int
    page: int
    page_size: int


class DeckComparisonRequest(BaseModel):
    """Schema for comparing a deck against meta"""
    deck_id: int
    snapshot_id: Optional[int] = None  # Use latest if not provided


class DeckComparisonResult(BaseModel):
    """Schema for deck comparison results"""
    deck_archetype: str
    meta_position: Optional[int] = None
    matchup_analysis: dict  # {"archetype": {"win_rate": 0.55, "notes": "..."}}
    overall_meta_score: float  # Weighted score against top 10
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
