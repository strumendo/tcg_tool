"""Deck models for Pokemon TCG"""
from typing import Optional, List
from sqlalchemy import String, Text, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.base import Base, TimestampMixin


class DeckFormat(str, enum.Enum):
    """Deck format/legality"""
    STANDARD = "standard"
    EXPANDED = "expanded"
    UNLIMITED = "unlimited"


class Deck(Base, TimestampMixin):
    """User-created deck"""
    __tablename__ = "decks"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Basic info
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)
    format: Mapped[DeckFormat] = mapped_column(SQLEnum(DeckFormat), default=DeckFormat.STANDARD)

    # Archetype (e.g., "Charizard ex", "Lugia VSTAR")
    archetype: Mapped[Optional[str]] = mapped_column(String(100), index=True)

    # Deck status
    is_active: Mapped[bool] = mapped_column(default=True)
    is_public: Mapped[bool] = mapped_column(default=False)

    # External reference (imported deck ID)
    external_id: Mapped[Optional[str]] = mapped_column(String(100))
    source: Mapped[Optional[str]] = mapped_column(String(50))  # "limitless", "file", "manual"

    # Stats (calculated)
    total_cards: Mapped[int] = mapped_column(Integer, default=0)
    pokemon_count: Mapped[int] = mapped_column(Integer, default=0)
    trainer_count: Mapped[int] = mapped_column(Integer, default=0)
    energy_count: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    cards: Mapped[List["DeckCard"]] = relationship(
        "DeckCard",
        back_populates="deck",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
    matches: Mapped[List["Match"]] = relationship("Match", back_populates="deck")
    tournaments: Mapped[List["Tournament"]] = relationship("Tournament", back_populates="deck")

    def __repr__(self) -> str:
        return f"<Deck {self.name} ({self.format.value})>"


class DeckCard(Base):
    """Association table for deck-card relationship with quantity"""
    __tablename__ = "deck_cards"

    id: Mapped[int] = mapped_column(primary_key=True)

    deck_id: Mapped[int] = mapped_column(ForeignKey("decks.id", ondelete="CASCADE"))
    card_id: Mapped[int] = mapped_column(ForeignKey("cards.id"))
    quantity: Mapped[int] = mapped_column(Integer, default=1)

    # Relationships
    deck: Mapped["Deck"] = relationship("Deck", back_populates="cards")
    card: Mapped["Card"] = relationship("Card", back_populates="deck_cards")

    def __repr__(self) -> str:
        return f"<DeckCard {self.card.name if self.card else 'N/A'} x{self.quantity}>"


# Import here to avoid circular imports
from app.models.card import Card
from app.models.match import Match
from app.models.tournament import Tournament
