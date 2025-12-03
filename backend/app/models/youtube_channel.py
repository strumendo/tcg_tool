"""YouTube Channel model for tracking TCG content creators"""
from typing import Optional
from sqlalchemy import String, Text, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class YouTubeChannel(Base, TimestampMixin):
    """YouTube channel for Pokemon TCG content"""
    __tablename__ = "youtube_channels"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Channel info
    channel_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)
    url: Mapped[str] = mapped_column(String(500))

    # Channel metadata
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500))
    subscriber_count: Mapped[Optional[int]] = mapped_column(Integer)
    video_count: Mapped[Optional[int]] = mapped_column(Integer)

    # Categories/tags
    category: Mapped[Optional[str]] = mapped_column(String(100))  # "competitive", "casual", "news"
    tags: Mapped[Optional[str]] = mapped_column(String(500))  # Comma-separated

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<YouTubeChannel {self.name}>"
