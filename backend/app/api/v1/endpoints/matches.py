"""Match endpoints"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.db import get_db
from app.models.match import Match, MatchAction, MatchResult
from app.schemas.match import (
    MatchCreate, MatchRead, MatchListRead, MatchImportRequest
)

router = APIRouter()


@router.get("", response_model=MatchListRead)
async def list_matches(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    deck_id: Optional[int] = None,
    result: Optional[MatchResult] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all matches with optional filters"""
    query = select(Match).options(selectinload(Match.actions))

    if deck_id:
        query = query.where(Match.deck_id == deck_id)
    if result:
        query = query.where(Match.result == result)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(Match.created_at.desc())
    result_db = await db.execute(query)
    matches = result_db.scalars().unique().all()

    return MatchListRead(
        matches=[MatchRead.model_validate(m) for m in matches],
        total=total or 0,
        page=page,
        page_size=page_size
    )


@router.get("/{match_id}", response_model=MatchRead)
async def get_match(match_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific match by ID with all actions"""
    query = select(Match).options(
        selectinload(Match.actions)
    ).where(Match.id == match_id)

    result = await db.execute(query)
    match = result.scalar_one_or_none()

    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    return MatchRead.model_validate(match)


@router.post("", response_model=MatchRead)
async def create_match(match: MatchCreate, db: AsyncSession = Depends(get_db)):
    """Create a new match manually"""
    match_data = match.model_dump(exclude={"actions"})
    db_match = Match(**match_data)
    db.add(db_match)
    await db.flush()

    # Add actions if provided
    if match.actions:
        for action_data in match.actions:
            action = MatchAction(match_id=db_match.id, **action_data.model_dump())
            db.add(action)

    await db.refresh(db_match)
    return MatchRead.model_validate(db_match)


@router.delete("/{match_id}")
async def delete_match(match_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a match"""
    query = select(Match).where(Match.id == match_id)
    result = await db.execute(query)
    match = result.scalar_one_or_none()

    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    await db.delete(match)
    return {"message": "Match deleted successfully"}


@router.post("/import/ocr", response_model=MatchRead)
async def import_match_from_screenshot(
    file: UploadFile = File(...),
    deck_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Import match from Pokemon TCG Live screenshot using OCR"""
    from app.services.match_import import MatchImportService

    content = await file.read()
    import_service = MatchImportService(db)

    match = await import_service.import_from_screenshot(content, deck_id)
    return MatchRead.model_validate(match)


@router.post("/import/text", response_model=MatchRead)
async def import_match_from_text(
    import_request: MatchImportRequest,
    db: AsyncSession = Depends(get_db)
):
    """Import match from text data"""
    from app.services.match_import import MatchImportService

    if not import_request.text_data:
        raise HTTPException(status_code=400, detail="text_data is required")

    import_service = MatchImportService(db)
    match = await import_service.import_from_text(
        import_request.text_data,
        import_request.deck_id
    )
    return MatchRead.model_validate(match)


@router.get("/{match_id}/stats")
async def get_match_stats(match_id: int, db: AsyncSession = Depends(get_db)):
    """Get detailed statistics for a match"""
    query = select(Match).options(
        selectinload(Match.actions)
    ).where(Match.id == match_id)

    result = await db.execute(query)
    match = result.scalar_one_or_none()

    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    # Calculate statistics
    player_actions = [a for a in match.actions if a.is_player_action]
    opponent_actions = [a for a in match.actions if not a.is_player_action]

    stats = {
        "match_id": match.id,
        "result": match.result.value if match.result else None,
        "total_turns": match.total_turns,
        "player": {
            "prizes_taken": match.player_prizes_taken,
            "total_actions": len(player_actions),
            "attacks": len([a for a in player_actions if a.action_type.value == "attack"]),
            "knockouts": len([a for a in player_actions if a.action_type.value == "knock_out"]),
        },
        "opponent": {
            "prizes_taken": match.opponent_prizes_taken,
            "total_actions": len(opponent_actions),
            "attacks": len([a for a in opponent_actions if a.action_type.value == "attack"]),
            "knockouts": len([a for a in opponent_actions if a.action_type.value == "knock_out"]),
        }
    }

    return stats
