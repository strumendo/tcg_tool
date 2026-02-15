"""Tournament and statistics ORM models: tournaments, news_articles, card_usage_stats, deck_usage_stats."""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
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
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Tournament(Base):
    """Represents a Pokemon TCG tournament event."""

    __tablename__ = "tournaments"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    format: Mapped[str] = mapped_column(
        String(20), default="Standard", server_default="Standard", nullable=False
    )
    event_type: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class NewsArticle(Base):
    """Represents a news article from sources like PokeBeach."""

    __tablename__ = "news_articles"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    source: Mapped[str] = mapped_column(
        String(50), default="PokeBeach", server_default="PokeBeach", nullable=False
    )
    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class CardUsageStats(Base):
    """Tracks card usage statistics across tournaments."""

    __tablename__ = "card_usage_stats"
    __table_args__ = (
        UniqueConstraint(
            "card_id",
            "format",
            "snapshot_date",
            name="uq_card_usage_stats_card_id_format_snapshot_date",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    card_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("cards.id"), nullable=False
    )
    format: Mapped[str] = mapped_column(
        String(20), default="Standard", server_default="Standard", nullable=False
    )
    usage_percentage: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    avg_copies: Mapped[Optional[float]] = mapped_column(
        Numeric(3, 1), nullable=True
    )
    sample_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Relationships
    card: Mapped["Card"] = relationship("Card", back_populates="usage_stats")


class DeckUsageStats(Base):
    """Tracks deck archetype usage and performance statistics."""

    __tablename__ = "deck_usage_stats"
    __table_args__ = (
        UniqueConstraint(
            "archetype",
            "format",
            "snapshot_date",
            name="uq_deck_usage_stats_archetype_format_snapshot_date",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    archetype: Mapped[str] = mapped_column(String(100), nullable=False)
    meta_share: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    avg_placement: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 1), nullable=True
    )
    sample_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    format: Mapped[str] = mapped_column(
        String(20), default="Standard", server_default="Standard", nullable=False
    )
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False)
