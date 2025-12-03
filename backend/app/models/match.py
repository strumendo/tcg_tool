"""Match models for Pokemon TCG Live imports"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, Text, Integer, ForeignKey, Enum as SQLEnum, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.base import Base, TimestampMixin


class MatchResult(str, enum.Enum):
    """Match outcome"""
    WIN = "win"
    LOSS = "loss"
    DRAW = "draw"
    CONCEDE = "concede"


class ActionType(str, enum.Enum):
    """Types of actions in a match"""
    DRAW = "draw"
    PLAY_POKEMON = "play_pokemon"
    EVOLVE = "evolve"
    ATTACH_ENERGY = "attach_energy"
    PLAY_TRAINER = "play_trainer"
    ATTACK = "attack"
    ABILITY = "ability"
    RETREAT = "retreat"
    KNOCK_OUT = "knock_out"
    PRIZE_TAKE = "prize_take"
    TURN_START = "turn_start"
    TURN_END = "turn_end"
    OTHER = "other"


class Match(Base, TimestampMixin):
    """A match imported from Pokemon TCG Live"""
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Deck used
    deck_id: Mapped[Optional[int]] = mapped_column(ForeignKey("decks.id"))
    deck: Mapped[Optional["Deck"]] = relationship("Deck", back_populates="matches")

    # Match info
    opponent_deck_archetype: Mapped[Optional[str]] = mapped_column(String(100))
    result: Mapped[Optional[MatchResult]] = mapped_column(SQLEnum(MatchResult))

    # Match details
    player_prizes_taken: Mapped[int] = mapped_column(Integer, default=0)
    opponent_prizes_taken: Mapped[int] = mapped_column(Integer, default=0)
    total_turns: Mapped[Optional[int]] = mapped_column(Integer)
    went_first: Mapped[Optional[bool]] = mapped_column(Boolean)

    # Timestamps
    match_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Import source
    import_source: Mapped[Optional[str]] = mapped_column(String(50))  # "ocr", "file"
    raw_data: Mapped[Optional[str]] = mapped_column(Text)  # Original imported data

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    actions: Mapped[List["MatchAction"]] = relationship(
        "MatchAction",
        back_populates="match",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="MatchAction.turn_number, MatchAction.action_order"
    )

    def __repr__(self) -> str:
        return f"<Match vs {self.opponent_deck_archetype} - {self.result.value if self.result else 'N/A'}>"


class MatchAction(Base):
    """Individual action in a match (step-by-step replay)"""
    __tablename__ = "match_actions"

    id: Mapped[int] = mapped_column(primary_key=True)

    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id", ondelete="CASCADE"))
    match: Mapped["Match"] = relationship("Match", back_populates="actions")

    # Turn tracking
    turn_number: Mapped[int] = mapped_column(Integer)
    action_order: Mapped[int] = mapped_column(Integer)  # Order within the turn
    is_player_action: Mapped[bool] = mapped_column(Boolean, default=True)

    # Action details
    action_type: Mapped[ActionType] = mapped_column(SQLEnum(ActionType))
    card_name: Mapped[Optional[str]] = mapped_column(String(200))
    target_card: Mapped[Optional[str]] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Damage/effect
    damage_dealt: Mapped[Optional[int]] = mapped_column(Integer)

    def __repr__(self) -> str:
        return f"<MatchAction T{self.turn_number}: {self.action_type.value}>"


# Import here to avoid circular imports
from app.models.deck import Deck
