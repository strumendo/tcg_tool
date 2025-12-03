"""YouTube Channel schemas"""
from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class YouTubeChannelBase(BaseModel):
    """Base schema for YouTubeChannel"""
    channel_id: str
    name: str
    description: Optional[str] = None
    url: str
    thumbnail_url: Optional[str] = None
    subscriber_count: Optional[int] = None
    video_count: Optional[int] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    is_active: bool = True
    is_favorite: bool = False
    notes: Optional[str] = None


class YouTubeChannelCreate(YouTubeChannelBase):
    """Schema for creating a YouTubeChannel"""
    pass


class YouTubeChannelUpdate(BaseModel):
    """Schema for updating a YouTubeChannel"""
    name: Optional[str] = None
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    subscriber_count: Optional[int] = None
    video_count: Optional[int] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    is_active: Optional[bool] = None
    is_favorite: Optional[bool] = None
    notes: Optional[str] = None


class YouTubeChannelRead(YouTubeChannelBase):
    """Schema for reading a YouTubeChannel"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class YouTubeChannelListRead(BaseModel):
    """Schema for paginated channel list"""
    channels: list[YouTubeChannelRead]
    total: int
    page: int
    page_size: int
