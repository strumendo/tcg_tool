"""Card and CardSet models for Pokemon TCG"""
from typing import Optional, List
from sqlalchemy import String, Text, Integer, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.base import Base, TimestampMixin


class CardType(str, enum.Enum):
    """Pokemon card types"""
    POKEMON = "pokemon"
    TRAINER = "trainer"
    ENERGY = "energy"


class CardSubtype(str, enum.Enum):
    """Card subtypes"""
    # Pokemon subtypes
    BASIC = "basic"
    STAGE1 = "stage1"
    STAGE2 = "stage2"
    VSTAR = "vstar"
    VMAX = "vmax"
    V = "v"
    EX = "ex"
    GX = "gx"
    RADIANT = "radiant"

    # Trainer subtypes
    ITEM = "item"
    SUPPORTER = "supporter"
    STADIUM = "stadium"
    TOOL = "tool"

    # Energy subtypes
    BASIC_ENERGY = "basic_energy"
    SPECIAL_ENERGY = "special_energy"


class EnergyType(str, enum.Enum):
    """Pokemon energy types"""
    GRASS = "grass"
    FIRE = "fire"
    WATER = "water"
    LIGHTNING = "lightning"
    PSYCHIC = "psychic"
    FIGHTING = "fighting"
    DARKNESS = "darkness"
    METAL = "metal"
    DRAGON = "dragon"
    COLORLESS = "colorless"
    FAIRY = "fairy"


class CardSet(Base, TimestampMixin):
    """Pokemon TCG Set"""
    __tablename__ = "card_sets"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    series: Mapped[Optional[str]] = mapped_column(String(100))
    release_date: Mapped[Optional[str]] = mapped_column(String(20))
    total_cards: Mapped[Optional[int]] = mapped_column(Integer)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500))
    symbol_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Relationships
    cards: Mapped[List["Card"]] = relationship("Card", back_populates="set", lazy="selectin")


class Card(Base, TimestampMixin):
    """Pokemon TCG Card"""
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(primary_key=True)

    # External IDs
    ptcg_id: Mapped[Optional[str]] = mapped_column(String(50), unique=True, index=True)  # Pokemon TCG API ID
    limitless_id: Mapped[Optional[str]] = mapped_column(String(50), index=True)  # Legacy
    ptcgo_code: Mapped[Optional[str]] = mapped_column(String(50))

    # Basic info
    name: Mapped[str] = mapped_column(String(200), index=True)
    card_type: Mapped[CardType] = mapped_column(SQLEnum(CardType))
    subtype: Mapped[Optional[CardSubtype]] = mapped_column(SQLEnum(CardSubtype))

    # Set relationship
    set_id: Mapped[Optional[int]] = mapped_column(ForeignKey("card_sets.id"))
    set: Mapped[Optional["CardSet"]] = relationship("CardSet", back_populates="cards")
    set_number: Mapped[Optional[str]] = mapped_column(String(20))

    # Pokemon-specific
    hp: Mapped[Optional[int]] = mapped_column(Integer)
    energy_type: Mapped[Optional[EnergyType]] = mapped_column(SQLEnum(EnergyType))
    weakness: Mapped[Optional[str]] = mapped_column(String(50))
    resistance: Mapped[Optional[str]] = mapped_column(String(50))
    retreat_cost: Mapped[Optional[int]] = mapped_column(Integer)

    # Card text
    abilities: Mapped[Optional[dict]] = mapped_column(JSON)  # List of abilities
    attacks: Mapped[Optional[dict]] = mapped_column(JSON)    # List of attacks
    rules: Mapped[Optional[str]] = mapped_column(Text)       # Rule text

    # Images
    image_small: Mapped[Optional[str]] = mapped_column(String(500))
    image_large: Mapped[Optional[str]] = mapped_column(String(500))

    # Metadata
    rarity: Mapped[Optional[str]] = mapped_column(String(50))
    artist: Mapped[Optional[str]] = mapped_column(String(200))
    regulation_mark: Mapped[Optional[str]] = mapped_column(String(10))

    # Legality
    is_standard_legal: Mapped[bool] = mapped_column(default=True)
    is_expanded_legal: Mapped[bool] = mapped_column(default=True)

    # Relationships
    deck_cards: Mapped[List["DeckCard"]] = relationship("DeckCard", back_populates="card")

    def __repr__(self) -> str:
        return f"<Card {self.name} ({self.set.code if self.set else 'N/A'} {self.set_number})>"


# Import here to avoid circular imports
from app.models.deck import DeckCard
