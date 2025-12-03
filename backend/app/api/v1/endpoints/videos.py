"""Video endpoints"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db import get_db
from app.models.video import Video, VideoStatus
from app.schemas.video import (
    VideoRead, VideoUpdate, VideoListRead, VideoAnalysisRequest
)
from app.core.config import settings

router = APIRouter()


@router.get("", response_model=VideoListRead)
async def list_videos(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[VideoStatus] = None,
    deck_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all videos with optional filters"""
    query = select(Video)

    if status:
        query = query.where(Video.status == status)
    if deck_id:
        query = query.where(Video.deck_id == deck_id)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(Video.created_at.desc())
    result = await db.execute(query)
    videos = result.scalars().all()

    return VideoListRead(
        videos=[VideoRead.model_validate(v) for v in videos],
        total=total or 0,
        page=page,
        page_size=page_size
    )


@router.get("/{video_id}", response_model=VideoRead)
async def get_video(video_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific video by ID"""
    query = select(Video).where(Video.id == video_id)
    result = await db.execute(query)
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    return VideoRead.model_validate(video)


@router.post("", response_model=VideoRead)
async def upload_video(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    deck_id: Optional[int] = Form(None),
    upload_source: Optional[str] = Form("web"),
    db: AsyncSession = Depends(get_db)
):
    """Upload a new video"""
    from app.services.video_service import VideoService

    # Validate file extension
    filename = file.filename or "video"
    extension = "." + filename.split(".")[-1].lower() if "." in filename else ""

    if extension not in settings.allowed_video_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Allowed: {settings.allowed_video_extensions}"
        )

    video_service = VideoService(db)
    video = await video_service.upload_video(
        file=file,
        title=title,
        description=description,
        deck_id=deck_id,
        upload_source=upload_source
    )

    return VideoRead.model_validate(video)


@router.put("/{video_id}", response_model=VideoRead)
async def update_video(
    video_id: int,
    video_update: VideoUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update video metadata"""
    query = select(Video).where(Video.id == video_id)
    result = await db.execute(query)
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    update_data = video_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(video, field, value)

    await db.flush()
    await db.refresh(video)
    return VideoRead.model_validate(video)


@router.delete("/{video_id}")
async def delete_video(video_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a video"""
    from app.services.video_service import VideoService

    query = select(Video).where(Video.id == video_id)
    result = await db.execute(query)
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    video_service = VideoService(db)
    await video_service.delete_video(video)

    return {"message": "Video deleted successfully"}


@router.post("/{video_id}/analyze", response_model=dict)
async def analyze_video(
    video_id: int,
    analysis_type: str = Query("full", regex="^(full|summary|key_moments)$"),
    db: AsyncSession = Depends(get_db)
):
    """Analyze a video using AI"""
    from app.services.video_analysis import VideoAnalysisService

    query = select(Video).where(Video.id == video_id)
    result = await db.execute(query)
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    if video.status != VideoStatus.READY:
        raise HTTPException(status_code=400, detail="Video is not ready for analysis")

    analysis_service = VideoAnalysisService(db)
    analysis_result = await analysis_service.analyze_video(video, analysis_type)

    return analysis_result


@router.get("/{video_id}/thumbnail")
async def get_video_thumbnail(video_id: int, db: AsyncSession = Depends(get_db)):
    """Get video thumbnail"""
    from app.services.video_service import VideoService

    query = select(Video).where(Video.id == video_id)
    result = await db.execute(query)
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    if not video.thumbnail_path:
        raise HTTPException(status_code=404, detail="Thumbnail not available")

    video_service = VideoService(db)
    thumbnail_data = await video_service.get_thumbnail(video)

    return StreamingResponse(thumbnail_data, media_type="image/jpeg")
