"""YouTube Channel endpoints"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db import get_db
from app.models.youtube_channel import YouTubeChannel
from app.schemas.youtube_channel import (
    YouTubeChannelCreate, YouTubeChannelRead, YouTubeChannelUpdate,
    YouTubeChannelListRead
)

router = APIRouter()


@router.get("", response_model=YouTubeChannelListRead)
async def list_channels(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    favorites_only: bool = False,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """List all YouTube channels with optional filters"""
    query = select(YouTubeChannel)

    if category:
        query = query.where(YouTubeChannel.category == category)
    if favorites_only:
        query = query.where(YouTubeChannel.is_favorite == True)
    if active_only:
        query = query.where(YouTubeChannel.is_active == True)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(YouTubeChannel.is_favorite.desc(), YouTubeChannel.name)
    result = await db.execute(query)
    channels = result.scalars().all()

    return YouTubeChannelListRead(
        channels=[YouTubeChannelRead.model_validate(c) for c in channels],
        total=total or 0,
        page=page,
        page_size=page_size
    )


@router.get("/{channel_id}", response_model=YouTubeChannelRead)
async def get_channel(channel_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific YouTube channel by ID"""
    query = select(YouTubeChannel).where(YouTubeChannel.id == channel_id)
    result = await db.execute(query)
    channel = result.scalar_one_or_none()

    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    return YouTubeChannelRead.model_validate(channel)


@router.post("", response_model=YouTubeChannelRead)
async def create_channel(
    channel: YouTubeChannelCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add a new YouTube channel"""
    # Check if channel already exists
    existing_query = select(YouTubeChannel).where(
        YouTubeChannel.channel_id == channel.channel_id
    )
    existing_result = await db.execute(existing_query)
    if existing_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Channel already exists")

    db_channel = YouTubeChannel(**channel.model_dump())
    db.add(db_channel)
    await db.flush()
    await db.refresh(db_channel)
    return YouTubeChannelRead.model_validate(db_channel)


@router.post("/from-url", response_model=YouTubeChannelRead)
async def add_channel_from_url(
    url: str = Query(..., description="YouTube channel URL"),
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Add a YouTube channel from its URL"""
    from app.services.youtube_service import YouTubeService

    youtube_service = YouTubeService()
    channel_data = await youtube_service.get_channel_info(url)

    if not channel_data:
        raise HTTPException(status_code=400, detail="Could not fetch channel information")

    # Check if channel already exists
    existing_query = select(YouTubeChannel).where(
        YouTubeChannel.channel_id == channel_data["channel_id"]
    )
    existing_result = await db.execute(existing_query)
    if existing_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Channel already exists")

    if category:
        channel_data["category"] = category

    db_channel = YouTubeChannel(**channel_data)
    db.add(db_channel)
    await db.flush()
    await db.refresh(db_channel)
    return YouTubeChannelRead.model_validate(db_channel)


@router.put("/{channel_id}", response_model=YouTubeChannelRead)
async def update_channel(
    channel_id: int,
    channel_update: YouTubeChannelUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a YouTube channel"""
    query = select(YouTubeChannel).where(YouTubeChannel.id == channel_id)
    result = await db.execute(query)
    channel = result.scalar_one_or_none()

    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    update_data = channel_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(channel, field, value)

    await db.flush()
    await db.refresh(channel)
    return YouTubeChannelRead.model_validate(channel)


@router.delete("/{channel_id}")
async def delete_channel(channel_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a YouTube channel"""
    query = select(YouTubeChannel).where(YouTubeChannel.id == channel_id)
    result = await db.execute(query)
    channel = result.scalar_one_or_none()

    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    await db.delete(channel)
    return {"message": "Channel deleted successfully"}


@router.post("/{channel_id}/favorite", response_model=YouTubeChannelRead)
async def toggle_favorite(channel_id: int, db: AsyncSession = Depends(get_db)):
    """Toggle favorite status for a channel"""
    query = select(YouTubeChannel).where(YouTubeChannel.id == channel_id)
    result = await db.execute(query)
    channel = result.scalar_one_or_none()

    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    channel.is_favorite = not channel.is_favorite
    await db.flush()
    await db.refresh(channel)
    return YouTubeChannelRead.model_validate(channel)
