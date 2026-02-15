"""Tournament and news API route handlers."""

from fastapi import APIRouter, Query
from sqlalchemy import select

from app.dependencies import DBSession
from app.models import NewsArticle, Tournament
from app.schemas.tournament import NewsArticleOut, TournamentOut

router = APIRouter()


@router.get("/", response_model=list[TournamentOut])
async def list_tournaments(
    db: DBSession,
    format: str = Query("Standard", description="Game format"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> list[TournamentOut]:
    """List upcoming and recent tournaments."""
    stmt = (
        select(Tournament)
        .where(Tournament.format == format)
        .order_by(Tournament.date.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    tournaments = result.scalars().all()
    return [TournamentOut.model_validate(t) for t in tournaments]


@router.get("/news", response_model=list[NewsArticleOut])
async def list_news(
    db: DBSession,
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0),
) -> list[NewsArticleOut]:
    """List latest news articles."""
    stmt = (
        select(NewsArticle)
        .order_by(NewsArticle.published_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    articles = result.scalars().all()
    return [NewsArticleOut.model_validate(a) for a in articles]
