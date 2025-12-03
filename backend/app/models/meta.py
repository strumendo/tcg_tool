"""Meta/competitive data models"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, Text, Float, Integer, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class MetaSnapshot(Base, TimestampMixin):
    """A snapshot of the competitive meta at a point in time"""
    __tablename__ = "meta_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Snapshot info
    name: Mapped[str] = mapped_column(String(200))  # e.g., "LAIC 2024", "Week 42 2024"
    description: Mapped[Optional[str]] = mapped_column(Text)
    snapshot_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Source
    source: Mapped[Optional[str]] = mapped_column(String(100))  # "limitless", "manual", "file"
    external_id: Mapped[Optional[str]] = mapped_column(String(100))

    # Tournament info (if applicable)
    tournament_name: Mapped[Optional[str]] = mapped_column(String(200))
    total_players: Mapped[Optional[int]] = mapped_column(Integer)

    # Relationships
    meta_decks: Mapped[List["MetaDeck"]] = relationship(
        "MetaDeck",
        back_populates="snapshot",
        lazy="selectin",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<MetaSnapshot {self.name}>"


class MetaDeck(Base, TimestampMixin):
    """A deck archetype's performance in a meta snapshot"""
    __tablename__ = "meta_decks"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Snapshot relationship
    snapshot_id: Mapped[int] = mapped_column(ForeignKey("meta_snapshots.id", ondelete="CASCADE"))
    snapshot: Mapped["MetaSnapshot"] = relationship("MetaSnapshot", back_populates="meta_decks")

    # Deck info
    archetype: Mapped[str] = mapped_column(String(100), index=True)
    rank: Mapped[int] = mapped_column(Integer)

    # Performance stats
    meta_share: Mapped[float] = mapped_column(Float)  # Percentage of meta
    play_rate: Mapped[Optional[float]] = mapped_column(Float)  # Usage rate
    win_rate: Mapped[Optional[float]] = mapped_column(Float)   # Win percentage

    # Matchup data (JSON: {"archetype": win_rate})
    matchups: Mapped[Optional[dict]] = mapped_column(JSON)

    # Sample deck (reference to a deck list)
    sample_deck_id: Mapped[Optional[int]] = mapped_column(ForeignKey("decks.id"))
    sample_deck: Mapped[Optional["Deck"]] = relationship("Deck")

    # Core cards (JSON list of card names)
    core_cards: Mapped[Optional[list]] = mapped_column(JSON)

    # Additional stats
    day2_conversion: Mapped[Optional[float]] = mapped_column(Float)
    top8_count: Mapped[Optional[int]] = mapped_column(Integer)
    top16_count: Mapped[Optional[int]] = mapped_column(Integer)

    def __repr__(self) -> str:
        return f"<MetaDeck {self.archetype} #{self.rank} ({self.meta_share:.1f}%)>"


# Import here to avoid circular imports
from app.models.deck import Deck
