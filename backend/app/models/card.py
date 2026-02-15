"""Card-related ORM models: card_sets, cards, card_abilities, card_attacks, card_functions."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class CardSet(Base):
    """Represents a Pokemon TCG card set (e.g., Scarlet & Violet, Paldea Evolved)."""

    __tablename__ = "card_sets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    tcgdex_id: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    name_en: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    name_pt: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    regulation_mark: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)
    release_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    total_cards: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_legal: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    cards: Mapped[List["Card"]] = relationship("Card", back_populates="card_set")


class Card(Base, TimestampMixin):
    """Represents a single Pokemon TCG card."""

    __tablename__ = "cards"
    __table_args__ = (
        UniqueConstraint("set_id", "set_number", name="uq_cards_set_id_set_number"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name_en: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    name_pt: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    card_type: Mapped[str] = mapped_column(String(20), nullable=False)
    trainer_subtype: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    set_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("card_sets.id"), nullable=True
    )
    set_number: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    regulation_mark: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)
    hp: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    energy_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    stage: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    is_ex: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    image_url_hires: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    tcgdex_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    pokemontcg_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationships
    card_set: Mapped[Optional["CardSet"]] = relationship("CardSet", back_populates="cards")
    abilities: Mapped[List["CardAbility"]] = relationship(
        "CardAbility", back_populates="card", cascade="all, delete-orphan"
    )
    attacks: Mapped[List["CardAttack"]] = relationship(
        "CardAttack", back_populates="card", cascade="all, delete-orphan"
    )
    functions: Mapped[List["CardFunction"]] = relationship(
        "CardFunction", back_populates="card", cascade="all, delete-orphan"
    )
    deck_cards: Mapped[List["DeckCard"]] = relationship(
        "DeckCard", back_populates="card"
    )
    meta_deck_cards: Mapped[List["MetaDeckCard"]] = relationship(
        "MetaDeckCard", back_populates="card"
    )
    collection_entries: Mapped[List["UserCollection"]] = relationship(
        "UserCollection", back_populates="card"
    )
    usage_stats: Mapped[List["CardUsageStats"]] = relationship(
        "CardUsageStats", back_populates="card"
    )


class CardAbility(Base):
    """Represents an ability on a Pokemon card."""

    __tablename__ = "card_abilities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    card_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("cards.id", ondelete="CASCADE"), nullable=False
    )
    name_en: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    name_pt: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    effect_en: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    effect_pt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    card: Mapped["Card"] = relationship("Card", back_populates="abilities")


class CardAttack(Base):
    """Represents an attack on a Pokemon card."""

    __tablename__ = "card_attacks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    card_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("cards.id", ondelete="CASCADE"), nullable=False
    )
    name_en: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    name_pt: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    damage: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    energy_cost: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    effect_en: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    effect_pt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    card: Mapped["Card"] = relationship("Card", back_populates="attacks")


class CardFunction(Base):
    """Maps a card to its functional role(s) in a deck (e.g., DRAW, SEARCH, RECOVERY)."""

    __tablename__ = "card_functions"

    card_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("cards.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    function: Mapped[str] = mapped_column(
        String(20), primary_key=True, nullable=False
    )

    # Relationships
    card: Mapped["Card"] = relationship("Card", back_populates="functions")
