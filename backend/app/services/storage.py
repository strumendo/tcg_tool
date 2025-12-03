"""MinIO/S3 Storage Service with local file fallback"""
from typing import Optional, BinaryIO
from io import BytesIO
from pathlib import Path
import os
import structlog

from app.core.config import settings

logger = structlog.get_logger()

# Try to import minio, use local fallback if not available
try:
    from minio import Minio
    from minio.error import S3Error
    MINIO_AVAILABLE = True
except ImportError:
    MINIO_AVAILABLE = False
    S3Error = Exception


class StorageService:
    """Service for interacting with MinIO/S3 storage or local filesystem"""

    def __init__(self):
        self.use_local = not MINIO_AVAILABLE or settings.use_local_storage
        self.local_base = Path(settings.local_storage_path) if hasattr(settings, 'local_storage_path') else Path("./data/storage")

        if not self.use_local and MINIO_AVAILABLE:
            try:
                self.client = Minio(
                    settings.minio_endpoint,
                    access_key=settings.minio_access_key,
                    secret_key=settings.minio_secret_key,
                    secure=settings.minio_secure
                )
            except Exception as e:
                logger.warning(f"MinIO not available, using local storage: {e}")
                self.use_local = True
        else:
            self.client = None
            self.use_local = True

        if self.use_local:
            self.local_base.mkdir(parents=True, exist_ok=True)
            logger.info(f"Using local storage at: {self.local_base}")

    async def initialize_buckets(self) -> None:
        """Initialize required buckets/directories"""
        buckets = [
            settings.minio_bucket_videos,
            settings.minio_bucket_imports,
        ]

        if self.use_local:
            for bucket in buckets:
                bucket_path = self.local_base / bucket
                bucket_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created local bucket directory: {bucket_path}")
        else:
            for bucket in buckets:
                try:
                    if not self.client.bucket_exists(bucket):
                        self.client.make_bucket(bucket)
                        logger.info(f"Created bucket: {bucket}")
                except S3Error as e:
                    logger.error(f"Failed to create bucket {bucket}", error=str(e))

    async def upload_file(
        self,
        bucket: str,
        object_name: str,
        data: bytes,
        content_type: str = "application/octet-stream"
    ) -> str:
        """Upload a file to storage"""
        if self.use_local:
            file_path = self.local_base / bucket / object_name
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_bytes(data)
            logger.info(f"Uploaded file locally: {file_path}")
            return f"{bucket}/{object_name}"

        try:
            data_stream = BytesIO(data)
            self.client.put_object(
                bucket,
                object_name,
                data_stream,
                length=len(data),
                content_type=content_type
            )
            logger.info(f"Uploaded file: {bucket}/{object_name}")
            return f"{bucket}/{object_name}"
        except S3Error as e:
            logger.error(f"Failed to upload file", error=str(e))
            raise

    async def upload_stream(
        self,
        bucket: str,
        object_name: str,
        stream: BinaryIO,
        length: int,
        content_type: str = "application/octet-stream"
    ) -> str:
        """Upload a file stream to storage"""
        if self.use_local:
            file_path = self.local_base / bucket / object_name
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_bytes(stream.read())
            logger.info(f"Uploaded stream locally: {file_path}")
            return f"{bucket}/{object_name}"

        try:
            self.client.put_object(
                bucket,
                object_name,
                stream,
                length=length,
                content_type=content_type
            )
            logger.info(f"Uploaded stream: {bucket}/{object_name}")
            return f"{bucket}/{object_name}"
        except S3Error as e:
            logger.error(f"Failed to upload stream", error=str(e))
            raise

    async def download_file(self, bucket: str, object_name: str) -> bytes:
        """Download a file from storage"""
        if self.use_local:
            file_path = self.local_base / bucket / object_name
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            return file_path.read_bytes()

        try:
            response = self.client.get_object(bucket, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            logger.error(f"Failed to download file", error=str(e))
            raise

    async def get_file_stream(self, bucket: str, object_name: str) -> BinaryIO:
        """Get a file stream from storage"""
        if self.use_local:
            file_path = self.local_base / bucket / object_name
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            return BytesIO(file_path.read_bytes())

        try:
            response = self.client.get_object(bucket, object_name)
            return BytesIO(response.read())
        except S3Error as e:
            logger.error(f"Failed to get file stream", error=str(e))
            raise

    async def delete_file(self, bucket: str, object_name: str) -> None:
        """Delete a file from storage"""
        if self.use_local:
            file_path = self.local_base / bucket / object_name
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted local file: {file_path}")
            return

        try:
            self.client.remove_object(bucket, object_name)
            logger.info(f"Deleted file: {bucket}/{object_name}")
        except S3Error as e:
            logger.error(f"Failed to delete file", error=str(e))
            raise

    async def file_exists(self, bucket: str, object_name: str) -> bool:
        """Check if a file exists"""
        if self.use_local:
            file_path = self.local_base / bucket / object_name
            return file_path.exists()

        try:
            self.client.stat_object(bucket, object_name)
            return True
        except S3Error:
            return False

    def get_presigned_url(
        self,
        bucket: str,
        object_name: str,
        expires_hours: int = 1
    ) -> str:
        """Get a presigned URL for a file"""
        if self.use_local:
            # For local storage, return a local file path
            return f"/api/v1/storage/{bucket}/{object_name}"

        from datetime import timedelta
        try:
            url = self.client.presigned_get_object(
                bucket,
                object_name,
                expires=timedelta(hours=expires_hours)
            )
            return url
        except S3Error as e:
            logger.error(f"Failed to get presigned URL", error=str(e))
            raise

    def get_local_path(self, bucket: str, object_name: str) -> Path:
        """Get the local file path (for local storage mode)"""
        return self.local_base / bucket / object_name
