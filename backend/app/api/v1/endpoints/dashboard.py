"""Dashboard endpoints - Aggregated stats and analytics"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.db import get_db
from app.models.card import Card, CardSet
from app.models.deck import Deck
from app.models.match import Match, MatchResult
from app.models.video import Video, VideoStatus
from app.models.youtube_channel import YouTubeChannel
from app.models.meta import MetaSnapshot, MetaDeck

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Get aggregated statistics for the dashboard"""

    # Card stats
    card_count = await db.scalar(select(func.count()).select_from(Card))
    set_count = await db.scalar(select(func.count()).select_from(CardSet))

    # Deck stats
    deck_count = await db.scalar(select(func.count()).select_from(Deck))
    active_decks = await db.scalar(
        select(func.count()).select_from(Deck).where(Deck.is_active == True)
    )

    # Match stats
    match_count = await db.scalar(select(func.count()).select_from(Match))
    wins = await db.scalar(
        select(func.count()).select_from(Match).where(Match.result == MatchResult.WIN)
    )
    losses = await db.scalar(
        select(func.count()).select_from(Match).where(Match.result == MatchResult.LOSS)
    )

    # Video stats
    video_count = await db.scalar(select(func.count()).select_from(Video))
    analyzed_videos = await db.scalar(
        select(func.count()).select_from(Video).where(Video.status == VideoStatus.READY)
    )

    # Channel stats
    channel_count = await db.scalar(select(func.count()).select_from(YouTubeChannel))
    favorite_channels = await db.scalar(
        select(func.count()).select_from(YouTubeChannel).where(YouTubeChannel.is_favorite == True)
    )

    # Meta stats
    snapshot_count = await db.scalar(select(func.count()).select_from(MetaSnapshot))

    # Calculate win rate
    total_matches = (wins or 0) + (losses or 0)
    win_rate = round((wins / total_matches * 100) if total_matches > 0 else 0, 1)

    return {
        "cards": {
            "total": card_count or 0,
            "sets": set_count or 0,
        },
        "decks": {
            "total": deck_count or 0,
            "active": active_decks or 0,
        },
        "matches": {
            "total": match_count or 0,
            "wins": wins or 0,
            "losses": losses or 0,
            "win_rate": win_rate,
        },
        "videos": {
            "total": video_count or 0,
            "analyzed": analyzed_videos or 0,
        },
        "channels": {
            "total": channel_count or 0,
            "favorites": favorite_channels or 0,
        },
        "meta": {
            "snapshots": snapshot_count or 0,
        },
    }


@router.get("/activity")
async def get_recent_activity(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get recent activity across all modules"""
    activities = []

    # Recent matches
    match_result = await db.execute(
        select(Match).order_by(Match.created_at.desc()).limit(5)
    )
    for match in match_result.scalars():
        result_text = match.result.value if match.result else "unknown"
        activities.append({
            "type": "match",
            "title": f"Match vs {match.opponent_deck_archetype or 'Unknown'}",
            "subtitle": f"Result: {result_text.upper()} ({match.player_prizes_taken}-{match.opponent_prizes_taken})",
            "timestamp": match.created_at.isoformat() if match.created_at else None,
            "link": f"/matches",
        })

    # Recent decks
    deck_result = await db.execute(
        select(Deck).order_by(Deck.created_at.desc()).limit(5)
    )
    for deck in deck_result.scalars():
        activities.append({
            "type": "deck",
            "title": f"Deck: {deck.name}",
            "subtitle": f"{deck.format} - {deck.total_cards} cards",
            "timestamp": deck.created_at.isoformat() if deck.created_at else None,
            "link": f"/decks/{deck.id}",
        })

    # Recent videos
    video_result = await db.execute(
        select(Video).order_by(Video.created_at.desc()).limit(5)
    )
    for video in video_result.scalars():
        activities.append({
            "type": "video",
            "title": f"Video: {video.title}",
            "subtitle": f"Status: {video.status.value}",
            "timestamp": video.created_at.isoformat() if video.created_at else None,
            "link": f"/videos",
        })

    # Sort all by timestamp and limit
    activities.sort(key=lambda x: x.get("timestamp") or "", reverse=True)
    return {"activities": activities[:limit]}


@router.get("/matchup-summary")
async def get_matchup_summary(
    deck_id: Optional[int] = None,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """Get matchup win rates summary"""
    cutoff = datetime.utcnow() - timedelta(days=days)

    query = select(Match).where(Match.created_at >= cutoff)
    if deck_id:
        query = query.where(Match.deck_id == deck_id)

    result = await db.execute(query)
    matches = result.scalars().all()

    # Calculate matchup stats
    matchups = {}
    for match in matches:
        arch = match.opponent_deck_archetype or "Unknown"
        if arch not in matchups:
            matchups[arch] = {"wins": 0, "losses": 0, "draws": 0, "total": 0}

        matchups[arch]["total"] += 1
        if match.result:
            if match.result.value == "win":
                matchups[arch]["wins"] += 1
            elif match.result.value == "loss":
                matchups[arch]["losses"] += 1
            elif match.result.value == "draw":
                matchups[arch]["draws"] += 1

    # Calculate win rates
    for arch in matchups:
        total = matchups[arch]["total"]
        wins = matchups[arch]["wins"]
        matchups[arch]["win_rate"] = round((wins / total * 100) if total > 0 else 0, 1)

    # Sort by total games
    sorted_matchups = sorted(matchups.items(), key=lambda x: x[1]["total"], reverse=True)

    return {
        "period_days": days,
        "total_matches": len(matches),
        "matchups": [{"archetype": k, **v} for k, v in sorted_matchups],
    }


@router.get("/win-rate-trend")
async def get_win_rate_trend(
    deck_id: Optional[int] = None,
    days: int = Query(30, ge=7, le=365),
    db: AsyncSession = Depends(get_db)
):
    """Get win rate trend over time"""
    cutoff = datetime.utcnow() - timedelta(days=days)

    query = select(Match).where(Match.created_at >= cutoff).order_by(Match.created_at.asc())
    if deck_id:
        query = query.where(Match.deck_id == deck_id)

    result = await db.execute(query)
    matches = result.scalars().all()

    # Calculate rolling win rate
    trend = []
    running_wins = 0
    running_total = 0

    for match in matches:
        running_total += 1
        if match.result and match.result.value == "win":
            running_wins += 1

        win_rate = round((running_wins / running_total * 100) if running_total > 0 else 0, 1)
        trend.append({
            "date": match.created_at.strftime("%Y-%m-%d") if match.created_at else None,
            "match_number": running_total,
            "cumulative_win_rate": win_rate,
        })

    return {
        "period_days": days,
        "total_matches": len(matches),
        "final_win_rate": trend[-1]["cumulative_win_rate"] if trend else 0,
        "trend": trend,
    }


@router.get("/top-decks")
async def get_user_top_decks(
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """Get user's top performing decks by win rate"""
    # Get all decks with match counts
    deck_result = await db.execute(select(Deck))
    decks = deck_result.scalars().all()

    deck_stats = []
    for deck in decks:
        # Get matches for this deck
        match_result = await db.execute(
            select(Match).where(Match.deck_id == deck.id)
        )
        matches = match_result.scalars().all()

        if not matches:
            continue

        wins = len([m for m in matches if m.result and m.result.value == "win"])
        total = len(matches)
        win_rate = round((wins / total * 100) if total > 0 else 0, 1)

        deck_stats.append({
            "id": deck.id,
            "name": deck.name,
            "format": deck.format.value if deck.format else "unknown",
            "archetype": deck.archetype,
            "matches_played": total,
            "wins": wins,
            "win_rate": win_rate,
        })

    # Sort by win rate (with minimum games filter)
    deck_stats.sort(key=lambda x: (x["matches_played"] >= 3, x["win_rate"]), reverse=True)

    return {"decks": deck_stats[:limit]}
