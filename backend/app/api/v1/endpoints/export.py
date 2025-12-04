"""Export endpoints for decks, tournaments, and stats"""
from typing import Optional, Literal
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.user import User
from app.services.auth import get_current_user_required
from app.services.export import ExportService

router = APIRouter()


# ==================== DECK EXPORTS ====================

@router.get("/deck/{deck_id}")
async def export_deck(
    deck_id: int,
    format: Literal["text", "ptcgo", "json", "limitless"] = Query("text", description="Export format"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Export a deck in various formats"""
    service = ExportService(db)

    if format == "text":
        content = await service.export_deck_text(deck_id)
        return PlainTextResponse(
            content,
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename=deck_{deck_id}.txt"}
        )
    elif format == "ptcgo":
        content = await service.export_deck_ptcgo(deck_id)
        return PlainTextResponse(
            content,
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename=deck_{deck_id}_ptcgo.txt"}
        )
    elif format == "limitless":
        content = await service.export_deck_limitless(deck_id)
        return PlainTextResponse(
            content,
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename=deck_{deck_id}_limitless.txt"}
        )
    else:  # json
        content = await service.export_deck_json(deck_id)
        return JSONResponse(
            content=eval(content),  # Parse JSON string to dict
            headers={"Content-Disposition": f"attachment; filename=deck_{deck_id}.json"}
        )


@router.get("/deck/{deck_id}/clipboard")
async def get_deck_for_clipboard(
    deck_id: int,
    format: Literal["text", "ptcgo", "limitless"] = Query("text"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Get deck text for copying to clipboard"""
    service = ExportService(db)

    if format == "ptcgo":
        content = await service.export_deck_ptcgo(deck_id)
    elif format == "limitless":
        content = await service.export_deck_limitless(deck_id)
    else:
        content = await service.export_deck_text(deck_id)

    return {"content": content, "format": format}


# ==================== TOURNAMENT EXPORTS ====================

@router.get("/tournament/{tournament_id}")
async def export_tournament(
    tournament_id: int,
    format: Literal["json", "csv"] = Query("json", description="Export format"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Export tournament report"""
    service = ExportService(db)

    if format == "csv":
        content = await service.export_tournament_csv(tournament_id, current_user.id)
        if not content:
            raise HTTPException(status_code=404, detail="Tournament not found")
        return PlainTextResponse(
            content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=tournament_{tournament_id}.csv"}
        )
    else:  # json
        report = await service.export_tournament_report(tournament_id, current_user.id)
        if not report:
            raise HTTPException(status_code=404, detail="Tournament not found")
        return JSONResponse(
            content=report,
            headers={"Content-Disposition": f"attachment; filename=tournament_{tournament_id}.json"}
        )


@router.get("/tournament/{tournament_id}/summary")
async def get_tournament_summary(
    tournament_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Get tournament summary for sharing"""
    service = ExportService(db)
    report = await service.export_tournament_report(tournament_id, current_user.id)

    if not report:
        raise HTTPException(status_code=404, detail="Tournament not found")

    # Create shareable summary text
    t = report["tournament"]
    r = report["results"]

    summary_lines = [
        f"🏆 {t['name']}",
        f"📅 {t['date']}",
        f"📍 {t['location'] or 'Location N/A'}",
        f"",
        f"📊 Record: {r['record']}",
    ]

    if r.get("final_standing"):
        summary_lines.append(f"🥇 Finish: #{r['final_standing']}")
    if r.get("championship_points"):
        summary_lines.append(f"⭐ CP: +{r['championship_points']}")

    summary_lines.append(f"")
    summary_lines.append(f"🎴 Playing: {report['deck']['archetype'] or 'Deck N/A'}")

    return {
        "summary": "\n".join(summary_lines),
        "report": report,
    }


# ==================== MATCH EXPORTS ====================

@router.get("/matches")
async def export_matches(
    format: Literal["json", "csv"] = Query("json", description="Export format"),
    deck_id: Optional[int] = Query(None, description="Filter by deck"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Export match history"""
    service = ExportService(db)

    if format == "csv":
        content = await service.export_matches_csv(current_user.id, deck_id)
        return PlainTextResponse(
            content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=matches.csv"}
        )
    else:  # json
        content = await service.export_matches_json(current_user.id, deck_id)
        return JSONResponse(
            content=eval(content),
            headers={"Content-Disposition": "attachment; filename=matches.json"}
        )


# ==================== STATS EXPORTS ====================

@router.get("/stats")
async def export_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Export comprehensive stats summary"""
    service = ExportService(db)
    return await service.export_stats_summary(current_user.id)


# ==================== SHARE CARD GENERATION ====================

@router.get("/share/deck/{deck_id}")
async def get_deck_share_data(
    deck_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Get deck data formatted for social sharing"""
    service = ExportService(db)
    json_data = await service.export_deck_json(deck_id)

    if not json_data or json_data == "{}":
        raise HTTPException(status_code=404, detail="Deck not found")

    import json
    deck_data = json.loads(json_data)

    # Create share text
    share_text = f"🎴 {deck_data['name']}"
    if deck_data.get('archetype'):
        share_text += f" ({deck_data['archetype']})"
    share_text += f"\n📦 {deck_data['pokemon_count']}P / {deck_data['trainer_count']}T / {deck_data['energy_count']}E"
    share_text += f"\n🃏 {deck_data['format'].title()} Format"

    return {
        "deck": deck_data,
        "share_text": share_text,
        "hashtags": ["PokemonTCG", deck_data.get('archetype', '').replace(' ', ''), "TCGDeck"],
    }


@router.get("/share/stats")
async def get_stats_share_data(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Get stats formatted for social sharing"""
    service = ExportService(db)
    stats = await service.export_stats_summary(current_user.id)

    share_lines = [
        "📊 My Pokemon TCG Stats",
        f"",
        f"🎯 Win Rate: {stats['matches']['win_rate']}%",
        f"🎮 Matches: {stats['matches']['total']}",
        f"🏆 Tournaments: {stats['tournaments']['total']}",
    ]

    if stats['tournaments']['championship_points'] > 0:
        share_lines.append(f"⭐ Championship Points: {stats['tournaments']['championship_points']}")

    if stats['tournaments']['best_finish']:
        share_lines.append(f"🥇 Best Finish: #{stats['tournaments']['best_finish']}")

    return {
        "stats": stats,
        "share_text": "\n".join(share_lines),
        "hashtags": ["PokemonTCG", "TCGStats", "CompetitivePokemon"],
    }
