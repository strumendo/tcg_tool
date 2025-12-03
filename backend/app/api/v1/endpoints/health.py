"""Health check endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import redis.asyncio as redis

from app.db import get_db
from app.core.config import settings

router = APIRouter()


@router.get("")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "version": settings.app_version}


@router.get("/db")
async def database_health(db: AsyncSession = Depends(get_db)):
    """Database connection health check"""
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}


@router.get("/redis")
async def redis_health():
    """Redis connection health check"""
    try:
        r = redis.from_url(settings.redis_url)
        await r.ping()
        await r.close()
        return {"status": "healthy", "redis": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "redis": "disconnected", "error": str(e)}


@router.get("/full")
async def full_health_check(db: AsyncSession = Depends(get_db)):
    """Full system health check"""
    health_status = {
        "status": "healthy",
        "version": settings.app_version,
        "services": {}
    }

    # Check database
    try:
        await db.execute(text("SELECT 1"))
        health_status["services"]["database"] = "healthy"
    except Exception:
        health_status["services"]["database"] = "unhealthy"
        health_status["status"] = "degraded"

    # Check Redis
    try:
        r = redis.from_url(settings.redis_url)
        await r.ping()
        await r.close()
        health_status["services"]["redis"] = "healthy"
    except Exception:
        health_status["services"]["redis"] = "unhealthy"
        health_status["status"] = "degraded"

    # Check if Anthropic API key is configured
    health_status["services"]["llm"] = "configured" if settings.anthropic_api_key else "not_configured"

    return health_status
