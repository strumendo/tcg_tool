"""Tournament schemas"""
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.models.tournament import (
    TournamentFormat, TournamentType, TournamentStatus, MatchResult
)


# Tournament Round Schemas
class TournamentRoundBase(BaseModel):
    """Base tournament round schema"""
    round_number: int = Field(..., ge=1)
    is_top_cut: bool = False
    top_cut_round: Optional[str] = None
    opponent_name: Optional[str] = None
    opponent_deck: Optional[str] = None
    opponent_archetype: Optional[str] = None
    result: MatchResult
    games_won: int = Field(0, ge=0, le=3)
    games_lost: int = Field(0, ge=0, le=3)
    went_first_game1: Optional[bool] = None
    went_first_game2: Optional[bool] = None
    went_first_game3: Optional[bool] = None
    notes: Optional[str] = None
    key_plays: Optional[str] = None


class TournamentRoundCreate(TournamentRoundBase):
    """Create a tournament round"""
    pass


class TournamentRoundUpdate(BaseModel):
    """Update a tournament round"""
    round_number: Optional[int] = Field(None, ge=1)
    is_top_cut: Optional[bool] = None
    top_cut_round: Optional[str] = None
    opponent_name: Optional[str] = None
    opponent_deck: Optional[str] = None
    opponent_archetype: Optional[str] = None
    result: Optional[MatchResult] = None
    games_won: Optional[int] = Field(None, ge=0, le=3)
    games_lost: Optional[int] = Field(None, ge=0, le=3)
    went_first_game1: Optional[bool] = None
    went_first_game2: Optional[bool] = None
    went_first_game3: Optional[bool] = None
    notes: Optional[str] = None
    key_plays: Optional[str] = None


class TournamentRoundRead(TournamentRoundBase):
    """Read tournament round"""
    id: int
    tournament_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Tournament Schemas
class TournamentBase(BaseModel):
    """Base tournament schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    format: TournamentFormat = TournamentFormat.STANDARD
    tournament_type: TournamentType = TournamentType.LOCAL
    event_date: date
    location: Optional[str] = None
    organizer: Optional[str] = None
    total_rounds: int = Field(0, ge=0)
    total_players: Optional[int] = Field(None, ge=0)
    entry_fee: Optional[float] = Field(None, ge=0)
    deck_id: Optional[int] = None
    deck_archetype: Optional[str] = None
    notes: Optional[str] = None


class TournamentCreate(TournamentBase):
    """Create a tournament"""
    pass


class TournamentUpdate(BaseModel):
    """Update a tournament"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    format: Optional[TournamentFormat] = None
    tournament_type: Optional[TournamentType] = None
    event_date: Optional[date] = None
    location: Optional[str] = None
    organizer: Optional[str] = None
    total_rounds: Optional[int] = Field(None, ge=0)
    total_players: Optional[int] = Field(None, ge=0)
    entry_fee: Optional[float] = Field(None, ge=0)
    status: Optional[TournamentStatus] = None
    final_standing: Optional[int] = Field(None, ge=1)
    final_record: Optional[str] = None
    championship_points: Optional[int] = Field(None, ge=0)
    deck_id: Optional[int] = None
    deck_archetype: Optional[str] = None
    notes: Optional[str] = None


class TournamentRead(TournamentBase):
    """Read tournament"""
    id: int
    user_id: int
    status: TournamentStatus
    final_standing: Optional[int] = None
    final_record: Optional[str] = None
    championship_points: int = 0
    created_at: datetime
    updated_at: datetime

    # Computed fields from rounds
    wins: int = 0
    losses: int = 0
    ties: int = 0
    rounds: List[TournamentRoundRead] = []

    model_config = {"from_attributes": True}


class TournamentListRead(BaseModel):
    """Paginated tournament list"""
    tournaments: List[TournamentRead]
    total: int
    page: int
    page_size: int


class TournamentStats(BaseModel):
    """Tournament statistics"""
    total_tournaments: int = 0
    total_championship_points: int = 0
    best_finish: Optional[int] = None
    total_wins: int = 0
    total_losses: int = 0
    total_ties: int = 0
    win_rate: float = 0.0
    tournaments_by_type: dict = {}
    top_archetypes_faced: List[dict] = []
    performance_by_format: dict = {}
