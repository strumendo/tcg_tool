"""MinIO/S3 Storage Service"""
from typing import Optional, BinaryIO
from io import BytesIO
from minio import Minio
from minio.error import S3Error
import structlog

from app.core.config import settings

logger = structlog.get_logger()


class StorageService:
    """Service for interacting with MinIO/S3 storage"""

    def __init__(self):
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure
        )

    async def initialize_buckets(self) -> None:
        """Initialize required buckets"""
        buckets = [
            settings.minio_bucket_videos,
            settings.minio_bucket_imports,
        ]

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
        try:
            response = self.client.get_object(bucket, object_name)
            return BytesIO(response.read())
        except S3Error as e:
            logger.error(f"Failed to get file stream", error=str(e))
            raise

    async def delete_file(self, bucket: str, object_name: str) -> None:
        """Delete a file from storage"""
        try:
            self.client.remove_object(bucket, object_name)
            logger.info(f"Deleted file: {bucket}/{object_name}")
        except S3Error as e:
            logger.error(f"Failed to delete file", error=str(e))
            raise

    async def file_exists(self, bucket: str, object_name: str) -> bool:
        """Check if a file exists"""
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
