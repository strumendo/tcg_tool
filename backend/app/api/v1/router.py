"""API v1 router - combines all endpoints"""
from fastapi import APIRouter

from app.api.v1.endpoints import cards, decks, matches, videos, youtube_channels, meta, health, dashboard, auth

api_router = APIRouter()

# Health check
api_router.include_router(health.router, prefix="/health", tags=["health"])

# Core endpoints
api_router.include_router(cards.router, prefix="/cards", tags=["cards"])
api_router.include_router(decks.router, prefix="/decks", tags=["decks"])
api_router.include_router(matches.router, prefix="/matches", tags=["matches"])
api_router.include_router(videos.router, prefix="/videos", tags=["videos"])
api_router.include_router(youtube_channels.router, prefix="/youtube-channels", tags=["youtube"])
api_router.include_router(meta.router, prefix="/meta", tags=["meta"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
