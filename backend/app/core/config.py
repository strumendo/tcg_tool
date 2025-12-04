"""Application configuration using Pydantic Settings"""
import os
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "Pokemon TCG Analysis Platform"
    app_version: str = "0.1.0"
    debug: bool = True

    # Database - defaults to SQLite for easy testing
    database_url: str = os.environ.get(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./tcg_platform.db"
    )

    # Redis
    redis_url: str = "redis://redis:6379"

    # Storage - Local fallback or MinIO
    use_local_storage: bool = True  # Default to local for easy testing
    local_storage_path: str = "./data/storage"

    # MinIO (used when use_local_storage=False)
    minio_endpoint: str = "minio:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin123"
    minio_secure: bool = False
    minio_bucket_videos: str = "tcg-videos"
    minio_bucket_imports: str = "tcg-imports"

    # API Keys
    anthropic_api_key: Optional[str] = None
    pokemon_tcg_api_key: str = "3c9a2ed2-0c55-4550-99e3-a65d96814e07"

    # TCGdex Settings (multilingual)
    default_language: str = "en"  # en, fr, de, es, it, pt, ja, zh-tw, id, th
    supported_languages: list[str] = ["en", "fr", "de", "es", "it", "pt", "ja", "zh-tw", "id", "th"]

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # File upload limits
    max_video_size_mb: int = 500
    max_import_file_size_mb: int = 50
    allowed_video_extensions: list[str] = [".mp4", ".mov", ".avi", ".mkv", ".webm"]
    allowed_import_extensions: list[str] = [".json", ".csv", ".txt", ".xml"]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
