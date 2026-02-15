"""Deck-related ORM models: decks, deck_cards."""

from typing import List, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Deck(Base, TimestampMixin):
    """Represents a user's deck."""

    __tablename__ = "decks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    archetype: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )
    is_valid: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )
    total_cards: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0"
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="decks")
    deck_cards: Mapped[List["DeckCard"]] = relationship(
        "DeckCard", back_populates="deck", cascade="all, delete-orphan"
    )
    battles: Mapped[List["Battle"]] = relationship(
        "Battle", back_populates="deck"
    )


class DeckCard(Base):
    """Represents a card entry within a deck, including quantity."""

    __tablename__ = "deck_cards"
    __table_args__ = (
        UniqueConstraint("deck_id", "card_id", name="uq_deck_cards_deck_id_card_id"),
        CheckConstraint("quantity >= 1 AND quantity <= 60", name="ck_deck_cards_quantity"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    deck_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("decks.id", ondelete="CASCADE"), nullable=False
    )
    card_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("cards.id"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    deck: Mapped["Deck"] = relationship("Deck", back_populates="deck_cards")
    card: Mapped["Card"] = relationship("Card", back_populates="deck_cards")
