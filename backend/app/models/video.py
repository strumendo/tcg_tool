"""Video model for uploaded match videos"""
from typing import Optional
from datetime import datetime
from sqlalchemy import String, Text, Integer, ForeignKey, Enum as SQLEnum, DateTime, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.base import Base, TimestampMixin


class VideoStatus(str, enum.Enum):
    """Video processing status"""
    UPLOADING = "uploading"
    PROCESSING = "processing"
    ANALYZING = "analyzing"
    READY = "ready"
    ERROR = "error"


class Video(Base, TimestampMixin):
    """Uploaded match video"""
    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Basic info
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)

    # File info
    filename: Mapped[str] = mapped_column(String(300))
    file_path: Mapped[str] = mapped_column(String(500))  # MinIO path
    file_size: Mapped[Optional[int]] = mapped_column(BigInteger)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer)
    format: Mapped[Optional[str]] = mapped_column(String(20))
    resolution: Mapped[Optional[str]] = mapped_column(String(20))

    # Processing
    status: Mapped[VideoStatus] = mapped_column(SQLEnum(VideoStatus), default=VideoStatus.UPLOADING)
    thumbnail_path: Mapped[Optional[str]] = mapped_column(String(500))
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    # Related match
    match_id: Mapped[Optional[int]] = mapped_column(ForeignKey("matches.id"))
    match: Mapped[Optional["Match"]] = relationship("Match")

    # Related deck
    deck_id: Mapped[Optional[int]] = mapped_column(ForeignKey("decks.id"))
    deck: Mapped[Optional["Deck"]] = relationship("Deck")

    # AI Analysis
    analysis_result: Mapped[Optional[str]] = mapped_column(Text)  # JSON string of analysis
    analyzed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Metadata
    upload_source: Mapped[Optional[str]] = mapped_column(String(50))  # "mobile", "desktop", etc

    def __repr__(self) -> str:
        return f"<Video {self.title} ({self.status.value})>"


# Import here to avoid circular imports
from app.models.match import Match
from app.models.deck import Deck
