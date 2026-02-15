"""Battle-related ORM models: battles, battle_actions."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Battle(Base):
    """Represents a recorded battle/match."""

    __tablename__ = "battles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    deck_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("decks.id", ondelete="SET NULL"), nullable=True
    )
    opponent_deck_name: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True
    )
    opponent_meta_deck_id: Mapped[Optional[str]] = mapped_column(
        String(50), ForeignKey("meta_decks.id", ondelete="SET NULL"), nullable=True
    )
    result: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    total_turns: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    went_first: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(
        String(20), default="manual", server_default="manual", nullable=False
    )
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    played_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="battles")
    deck: Mapped[Optional["Deck"]] = relationship("Deck", back_populates="battles")
    opponent_meta_deck: Mapped[Optional["MetaDeck"]] = relationship(
        "MetaDeck", back_populates="battles"
    )
    actions: Mapped[List["BattleAction"]] = relationship(
        "BattleAction", back_populates="battle", cascade="all, delete-orphan"
    )


class BattleAction(Base):
    """Represents an individual action within a battle turn."""

    __tablename__ = "battle_actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    battle_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("battles.id", ondelete="CASCADE"), nullable=False
    )
    turn: Mapped[int] = mapped_column(Integer, nullable=False)
    player: Mapped[str] = mapped_column(String(10), nullable=False)
    action_type: Mapped[str] = mapped_column(String(30), nullable=False)
    card_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    battle: Mapped["Battle"] = relationship("Battle", back_populates="actions")
