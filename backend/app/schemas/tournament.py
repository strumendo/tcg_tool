"""Pydantic schemas for tournament and news endpoints."""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TournamentOut(BaseModel):
    """Serialization schema for a tournament event."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    date: Optional[date] = None
    end_date: Optional[date] = None
    location: Optional[str] = None
    country: Optional[str] = None
    format: str
    event_type: Optional[str] = None
    url: Optional[str] = None
    created_at: datetime


class NewsArticleOut(BaseModel):
    """Serialization schema for a news article."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    summary: Optional[str] = None
    url: Optional[str] = None
    image_url: Optional[str] = None
    source: str
    published_at: Optional[datetime] = None
    created_at: datetime
