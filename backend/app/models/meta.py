"""Meta-game ORM models: meta_decks, meta_deck_cards, meta_matchups."""

from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class MetaDeck(Base, TimestampMixin):
    """Represents a competitive meta deck archetype."""

    __tablename__ = "meta_decks"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name_en: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    name_pt: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    tier: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    description_en: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description_pt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    strategy_en: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    strategy_pt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    difficulty: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    meta_share: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    key_pokemon: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    energy_types: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    strengths_en: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    strengths_pt: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    weaknesses_en: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    weaknesses_pt: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    snapshot_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    __table_args__ = (
        CheckConstraint("tier >= 1 AND tier <= 3", name="ck_meta_decks_tier"),
    )

    # Relationships
    meta_deck_cards: Mapped[List["MetaDeckCard"]] = relationship(
        "MetaDeckCard", back_populates="meta_deck", cascade="all, delete-orphan"
    )
    matchups_as_a: Mapped[List["MetaMatchup"]] = relationship(
        "MetaMatchup",
        foreign_keys="MetaMatchup.deck_a_id",
        back_populates="deck_a",
        cascade="all, delete-orphan",
    )
    matchups_as_b: Mapped[List["MetaMatchup"]] = relationship(
        "MetaMatchup",
        foreign_keys="MetaMatchup.deck_b_id",
        back_populates="deck_b",
        cascade="all, delete-orphan",
    )
    battles: Mapped[List["Battle"]] = relationship(
        "Battle", back_populates="opponent_meta_deck"
    )


class MetaDeckCard(Base):
    """Represents a card entry within a meta deck."""

    __tablename__ = "meta_deck_cards"
    __table_args__ = (
        UniqueConstraint(
            "meta_deck_id", "card_id", name="uq_meta_deck_cards_meta_deck_id_card_id"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    meta_deck_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("meta_decks.id", ondelete="CASCADE"), nullable=False
    )
    card_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("cards.id"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    meta_deck: Mapped["MetaDeck"] = relationship(
        "MetaDeck", back_populates="meta_deck_cards"
    )
    card: Mapped["Card"] = relationship("Card", back_populates="meta_deck_cards")


class MetaMatchup(Base):
    """Represents a matchup win rate between two meta decks."""

    __tablename__ = "meta_matchups"
    __table_args__ = (
        UniqueConstraint(
            "deck_a_id", "deck_b_id", name="uq_meta_matchups_deck_a_id_deck_b_id"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    deck_a_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("meta_decks.id", ondelete="CASCADE"), nullable=False
    )
    deck_b_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("meta_decks.id", ondelete="CASCADE"), nullable=False
    )
    win_rate_a: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    notes_en: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes_pt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    snapshot_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Relationships
    deck_a: Mapped["MetaDeck"] = relationship(
        "MetaDeck", foreign_keys=[deck_a_id], back_populates="matchups_as_a"
    )
    deck_b: Mapped["MetaDeck"] = relationship(
        "MetaDeck", foreign_keys=[deck_b_id], back_populates="matchups_as_b"
    )
