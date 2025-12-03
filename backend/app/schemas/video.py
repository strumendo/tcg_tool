"""Video schemas"""
from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from app.models.video import VideoStatus


class VideoBase(BaseModel):
    """Base schema for Video"""
    title: str
    description: Optional[str] = None
    deck_id: Optional[int] = None
    match_id: Optional[int] = None


class VideoCreate(VideoBase):
    """Schema for creating a Video"""
    pass


class VideoUpdate(BaseModel):
    """Schema for updating a Video"""
    title: Optional[str] = None
    description: Optional[str] = None
    deck_id: Optional[int] = None
    match_id: Optional[int] = None


class VideoRead(VideoBase):
    """Schema for reading a Video"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    file_path: str
    file_size: Optional[int] = None
    duration_seconds: Optional[int] = None
    format: Optional[str] = None
    resolution: Optional[str] = None
    status: VideoStatus
    thumbnail_path: Optional[str] = None
    error_message: Optional[str] = None
    analysis_result: Optional[str] = None
    analyzed_at: Optional[datetime] = None
    upload_source: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class VideoListRead(BaseModel):
    """Schema for paginated video list"""
    videos: list[VideoRead]
    total: int
    page: int
    page_size: int


class VideoAnalysisRequest(BaseModel):
    """Schema for requesting video analysis"""
    video_id: int
    analysis_type: str = "full"  # "full", "summary", "key_moments"
