"""Pydantic schemas for statistics endpoints."""

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CardUsageStatsOut(BaseModel):
    """Serialization schema for card usage statistics."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    card_id: int
    format: str
    usage_percentage: Optional[float] = None
    avg_copies: Optional[float] = None
    sample_size: Optional[int] = None
    snapshot_date: date


class DeckUsageStatsOut(BaseModel):
    """Serialization schema for deck archetype usage statistics."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    archetype: str
    meta_share: Optional[float] = None
    avg_placement: Optional[float] = None
    sample_size: Optional[int] = None
    format: str
    snapshot_date: date


class UserStatsOut(BaseModel):
    """Aggregated statistics for a user."""

    total_decks: int = 0
    total_battles: int = 0
    wins: int = 0
    losses: int = 0
    ties: int = 0
    win_rate: float = 0.0
    collection_size: int = 0
    most_played_deck: Optional[str] = None
    most_faced_archetype: Optional[str] = None


class BattleStatsOut(BaseModel):
    """Detailed battle statistics."""

    total_battles: int = 0
    wins: int = 0
    losses: int = 0
    ties: int = 0
    win_rate: float = 0.0
    went_first_win_rate: float = 0.0
    went_second_win_rate: float = 0.0
    avg_turns: float = 0.0
    results_by_opponent: list[dict] = []
    results_by_deck: list[dict] = []
