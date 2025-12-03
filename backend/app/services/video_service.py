"""Video Service - Handle video uploads and processing"""
from typing import Optional, BinaryIO
from io import BytesIO
import uuid
from datetime import datetime
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.models.video import Video, VideoStatus
from app.services.storage import StorageService
from app.core.config import settings

logger = structlog.get_logger()


class VideoService:
    """Service for handling video uploads and processing"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.storage = StorageService()

    async def upload_video(
        self,
        file: UploadFile,
        title: str,
        description: Optional[str] = None,
        deck_id: Optional[int] = None,
        upload_source: Optional[str] = "web"
    ) -> Video:
        """Upload a video file"""
        # Generate unique filename
        original_filename = file.filename or "video"
        extension = "." + original_filename.split(".")[-1].lower() if "." in original_filename else ".mp4"
        unique_filename = f"{uuid.uuid4()}{extension}"

        # Read file content
        content = await file.read()
        file_size = len(content)

        # Check file size
        max_size = settings.max_video_size_mb * 1024 * 1024
        if file_size > max_size:
            raise ValueError(f"File size exceeds maximum allowed ({settings.max_video_size_mb}MB)")

        # Create video record
        video = Video(
            title=title,
            description=description,
            filename=original_filename,
            file_path=f"{settings.minio_bucket_videos}/{unique_filename}",
            file_size=file_size,
            format=extension.lstrip("."),
            status=VideoStatus.UPLOADING,
            deck_id=deck_id,
            upload_source=upload_source
        )

        self.db.add(video)
        await self.db.flush()

        try:
            # Upload to storage
            await self.storage.upload_file(
                bucket=settings.minio_bucket_videos,
                object_name=unique_filename,
                data=content,
                content_type=file.content_type or "video/mp4"
            )

            # Update status
            video.status = VideoStatus.PROCESSING

            # Extract video metadata
            await self._extract_metadata(video, content)

            # Generate thumbnail
            await self._generate_thumbnail(video, content)

            video.status = VideoStatus.READY
            await self.db.flush()

        except Exception as e:
            video.status = VideoStatus.ERROR
            video.error_message = str(e)
            await self.db.flush()
            logger.error(f"Failed to upload video: {str(e)}")
            raise

        await self.db.refresh(video)
        logger.info(f"Uploaded video: {video.title}")
        return video

    async def _extract_metadata(self, video: Video, content: bytes) -> None:
        """Extract metadata from video file"""
        try:
            from moviepy.editor import VideoFileClip
            import tempfile
            import os

            # Write to temp file for moviepy
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{video.format}") as tmp:
                tmp.write(content)
                tmp_path = tmp.name

            try:
                clip = VideoFileClip(tmp_path)
                video.duration_seconds = int(clip.duration)
                video.resolution = f"{clip.size[0]}x{clip.size[1]}"
                clip.close()
            finally:
                os.unlink(tmp_path)

        except Exception as e:
            logger.warning(f"Failed to extract video metadata: {str(e)}")

    async def _generate_thumbnail(self, video: Video, content: bytes) -> None:
        """Generate thumbnail from video"""
        try:
            from moviepy.editor import VideoFileClip
            import tempfile
            import os

            # Write to temp file for moviepy
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{video.format}") as tmp:
                tmp.write(content)
                tmp_path = tmp.name

            try:
                clip = VideoFileClip(tmp_path)

                # Get frame at 1 second or middle of video
                time = min(1, clip.duration / 2)
                frame = clip.get_frame(time)

                # Convert to JPEG
                from PIL import Image
                img = Image.fromarray(frame)
                thumb_buffer = BytesIO()
                img.save(thumb_buffer, format="JPEG", quality=85)
                thumb_data = thumb_buffer.getvalue()

                # Upload thumbnail
                thumb_filename = f"thumb_{uuid.uuid4()}.jpg"
                await self.storage.upload_file(
                    bucket=settings.minio_bucket_videos,
                    object_name=thumb_filename,
                    data=thumb_data,
                    content_type="image/jpeg"
                )

                video.thumbnail_path = f"{settings.minio_bucket_videos}/{thumb_filename}"
                clip.close()

            finally:
                os.unlink(tmp_path)

        except Exception as e:
            logger.warning(f"Failed to generate thumbnail: {str(e)}")

    async def get_video_stream(self, video: Video) -> BinaryIO:
        """Get video file stream"""
        bucket, object_name = video.file_path.split("/", 1)
        return await self.storage.get_file_stream(bucket, object_name)

    async def get_thumbnail(self, video: Video) -> BinaryIO:
        """Get video thumbnail stream"""
        if not video.thumbnail_path:
            raise ValueError("Video has no thumbnail")

        bucket, object_name = video.thumbnail_path.split("/", 1)
        return await self.storage.get_file_stream(bucket, object_name)

    async def delete_video(self, video: Video) -> None:
        """Delete a video and its associated files"""
        # Delete video file
        try:
            bucket, object_name = video.file_path.split("/", 1)
            await self.storage.delete_file(bucket, object_name)
        except Exception as e:
            logger.warning(f"Failed to delete video file: {str(e)}")

        # Delete thumbnail
        if video.thumbnail_path:
            try:
                bucket, object_name = video.thumbnail_path.split("/", 1)
                await self.storage.delete_file(bucket, object_name)
            except Exception as e:
                logger.warning(f"Failed to delete thumbnail: {str(e)}")

        # Delete database record
        await self.db.delete(video)
        logger.info(f"Deleted video: {video.title}")
