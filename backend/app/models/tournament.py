"""Tournament models for tracking competitive events"""
from datetime import datetime, date
from typing import Optional, TYPE_CHECKING
from enum import Enum
from sqlalchemy import String, Integer, Text, Date, DateTime, ForeignKey, Enum as SQLEnum, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.deck import Deck


class TournamentFormat(str, Enum):
    """Tournament format types"""
    STANDARD = "standard"
    EXPANDED = "expanded"
    UNLIMITED = "unlimited"
    GLC = "glc"  # Gym Leader Challenge
    OTHER = "other"


class TournamentType(str, Enum):
    """Type of tournament"""
    LOCAL = "local"
    LEAGUE_CUP = "league_cup"
    LEAGUE_CHALLENGE = "league_challenge"
    REGIONAL = "regional"
    INTERNATIONAL = "international"
    WORLD = "world"
    ONLINE = "online"
    CASUAL = "casual"


class TournamentStatus(str, Enum):
    """Tournament status"""
    UPCOMING = "upcoming"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MatchResult(str, Enum):
    """Match result types"""
    WIN = "win"
    LOSS = "loss"
    TIE = "tie"
    BYE = "bye"
    INTENTIONAL_DRAW = "id"


class Tournament(Base, TimestampMixin):
    """Tournament event model"""
    __tablename__ = "tournaments"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Basic info
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    format: Mapped[TournamentFormat] = mapped_column(
        SQLEnum(TournamentFormat), default=TournamentFormat.STANDARD
    )
    tournament_type: Mapped[TournamentType] = mapped_column(
        SQLEnum(TournamentType), default=TournamentType.LOCAL
    )

    # Date and location
    event_date: Mapped[date] = mapped_column(Date)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    organizer: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Tournament details
    total_rounds: Mapped[int] = mapped_column(Integer, default=0)
    total_players: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    entry_fee: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Status and results
    status: Mapped[TournamentStatus] = mapped_column(
        SQLEnum(TournamentStatus), default=TournamentStatus.UPCOMING
    )
    final_standing: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    final_record: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # e.g., "5-2-1"
    championship_points: Mapped[int] = mapped_column(Integer, default=0)

    # Deck used
    deck_id: Mapped[Optional[int]] = mapped_column(ForeignKey("decks.id"), nullable=True)
    deck_archetype: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="tournaments")
    deck: Mapped[Optional["Deck"]] = relationship("Deck", back_populates="tournaments")
    rounds: Mapped[list["TournamentRound"]] = relationship(
        "TournamentRound", back_populates="tournament", cascade="all, delete-orphan",
        order_by="TournamentRound.round_number"
    )


class TournamentRound(Base, TimestampMixin):
    """Individual round/match in a tournament"""
    __tablename__ = "tournament_rounds"

    id: Mapped[int] = mapped_column(primary_key=True)
    tournament_id: Mapped[int] = mapped_column(ForeignKey("tournaments.id"))

    # Round info
    round_number: Mapped[int] = mapped_column(Integer)
    is_top_cut: Mapped[bool] = mapped_column(Boolean, default=False)
    top_cut_round: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # e.g., "Top 8", "Finals"

    # Opponent info
    opponent_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    opponent_deck: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    opponent_archetype: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Match result
    result: Mapped[MatchResult] = mapped_column(SQLEnum(MatchResult))
    games_won: Mapped[int] = mapped_column(Integer, default=0)
    games_lost: Mapped[int] = mapped_column(Integer, default=0)

    # Game details
    went_first_game1: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    went_first_game2: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    went_first_game3: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    key_plays: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    tournament: Mapped["Tournament"] = relationship("Tournament", back_populates="rounds")
