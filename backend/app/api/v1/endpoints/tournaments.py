"""Tournament endpoints"""
from typing import Optional, Literal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload

from app.db import get_db
from app.models.tournament import (
    Tournament, TournamentRound, TournamentFormat, TournamentType,
    TournamentStatus, MatchResult
)
from app.models.user import User
from app.schemas.tournament import (
    TournamentCreate, TournamentRead, TournamentUpdate, TournamentListRead,
    TournamentRoundCreate, TournamentRoundRead, TournamentRoundUpdate,
    TournamentStats
)
from app.services.auth import get_current_user_required

router = APIRouter()


def calculate_record(rounds: list[TournamentRound]) -> tuple[int, int, int]:
    """Calculate wins, losses, ties from rounds"""
    wins = sum(1 for r in rounds if r.result == MatchResult.WIN or r.result == MatchResult.BYE)
    losses = sum(1 for r in rounds if r.result == MatchResult.LOSS)
    ties = sum(1 for r in rounds if r.result == MatchResult.TIE or r.result == MatchResult.INTENTIONAL_DRAW)
    return wins, losses, ties


def enrich_tournament(tournament: Tournament) -> dict:
    """Add computed fields to tournament"""
    wins, losses, ties = calculate_record(tournament.rounds)
    data = {
        **{c.name: getattr(tournament, c.name) for c in tournament.__table__.columns},
        "rounds": tournament.rounds,
        "wins": wins,
        "losses": losses,
        "ties": ties,
    }
    return data


@router.get("", response_model=TournamentListRead)
async def list_tournaments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    format: Optional[TournamentFormat] = None,
    tournament_type: Optional[TournamentType] = None,
    status: Optional[TournamentStatus] = None,
    year: Optional[int] = None,
    sort_by: Literal["event_date", "created_at", "name"] = "event_date",
    sort_order: Literal["asc", "desc"] = "desc",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """List user's tournaments with filters"""
    query = select(Tournament).options(
        selectinload(Tournament.rounds)
    ).where(Tournament.user_id == current_user.id)

    # Apply filters
    if format:
        query = query.where(Tournament.format == format)
    if tournament_type:
        query = query.where(Tournament.tournament_type == tournament_type)
    if status:
        query = query.where(Tournament.status == status)
    if year:
        query = query.where(func.extract('year', Tournament.event_date) == year)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Apply sorting
    sort_column = getattr(Tournament, sort_by, Tournament.event_date)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    tournaments = result.scalars().all()

    return TournamentListRead(
        tournaments=[TournamentRead.model_validate(enrich_tournament(t)) for t in tournaments],
        total=total or 0,
        page=page,
        page_size=page_size
    )


@router.get("/stats", response_model=TournamentStats)
async def get_tournament_stats(
    year: Optional[int] = None,
    format: Optional[TournamentFormat] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Get aggregated tournament statistics"""
    query = select(Tournament).options(
        selectinload(Tournament.rounds)
    ).where(Tournament.user_id == current_user.id)

    if year:
        query = query.where(func.extract('year', Tournament.event_date) == year)
    if format:
        query = query.where(Tournament.format == format)

    result = await db.execute(query)
    tournaments = result.scalars().all()

    total_wins = 0
    total_losses = 0
    total_ties = 0
    archetypes_faced = {}
    by_type = {}
    by_format = {}

    for t in tournaments:
        wins, losses, ties = calculate_record(t.rounds)
        total_wins += wins
        total_losses += losses
        total_ties += ties

        # Count by type
        type_name = t.tournament_type.value
        if type_name not in by_type:
            by_type[type_name] = 0
        by_type[type_name] += 1

        # Count by format
        format_name = t.format.value
        if format_name not in by_format:
            by_format[format_name] = {"tournaments": 0, "wins": 0, "losses": 0}
        by_format[format_name]["tournaments"] += 1
        by_format[format_name]["wins"] += wins
        by_format[format_name]["losses"] += losses

        # Track archetypes faced
        for r in t.rounds:
            if r.opponent_archetype:
                if r.opponent_archetype not in archetypes_faced:
                    archetypes_faced[r.opponent_archetype] = {"count": 0, "wins": 0, "losses": 0}
                archetypes_faced[r.opponent_archetype]["count"] += 1
                if r.result == MatchResult.WIN:
                    archetypes_faced[r.opponent_archetype]["wins"] += 1
                elif r.result == MatchResult.LOSS:
                    archetypes_faced[r.opponent_archetype]["losses"] += 1

    total_games = total_wins + total_losses + total_ties
    win_rate = (total_wins / total_games * 100) if total_games > 0 else 0.0

    best_finish = None
    completed = [t for t in tournaments if t.final_standing]
    if completed:
        best_finish = min(t.final_standing for t in completed)

    # Sort archetypes by count
    top_archetypes = sorted(
        [{"archetype": k, **v} for k, v in archetypes_faced.items()],
        key=lambda x: x["count"],
        reverse=True
    )[:10]

    return TournamentStats(
        total_tournaments=len(tournaments),
        total_championship_points=sum(t.championship_points for t in tournaments),
        best_finish=best_finish,
        total_wins=total_wins,
        total_losses=total_losses,
        total_ties=total_ties,
        win_rate=round(win_rate, 1),
        tournaments_by_type=by_type,
        top_archetypes_faced=top_archetypes,
        performance_by_format=by_format
    )


@router.get("/{tournament_id}", response_model=TournamentRead)
async def get_tournament(
    tournament_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Get a specific tournament"""
    query = select(Tournament).options(
        selectinload(Tournament.rounds)
    ).where(
        Tournament.id == tournament_id,
        Tournament.user_id == current_user.id
    )
    result = await db.execute(query)
    tournament = result.scalar_one_or_none()

    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    return TournamentRead.model_validate(enrich_tournament(tournament))


@router.post("", response_model=TournamentRead)
async def create_tournament(
    data: TournamentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Create a new tournament"""
    tournament = Tournament(
        **data.model_dump(),
        user_id=current_user.id
    )
    db.add(tournament)
    await db.flush()
    await db.refresh(tournament)

    return TournamentRead.model_validate(enrich_tournament(tournament))


@router.put("/{tournament_id}", response_model=TournamentRead)
async def update_tournament(
    tournament_id: int,
    data: TournamentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Update a tournament"""
    query = select(Tournament).options(
        selectinload(Tournament.rounds)
    ).where(
        Tournament.id == tournament_id,
        Tournament.user_id == current_user.id
    )
    result = await db.execute(query)
    tournament = result.scalar_one_or_none()

    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tournament, field, value)

    await db.flush()
    await db.refresh(tournament)

    return TournamentRead.model_validate(enrich_tournament(tournament))


@router.delete("/{tournament_id}")
async def delete_tournament(
    tournament_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Delete a tournament"""
    query = select(Tournament).where(
        Tournament.id == tournament_id,
        Tournament.user_id == current_user.id
    )
    result = await db.execute(query)
    tournament = result.scalar_one_or_none()

    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    await db.delete(tournament)
    return {"message": "Tournament deleted"}


# Tournament Rounds endpoints
@router.post("/{tournament_id}/rounds", response_model=TournamentRoundRead)
async def add_round(
    tournament_id: int,
    data: TournamentRoundCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Add a round to a tournament"""
    # Verify tournament ownership
    query = select(Tournament).where(
        Tournament.id == tournament_id,
        Tournament.user_id == current_user.id
    )
    result = await db.execute(query)
    tournament = result.scalar_one_or_none()

    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    round_entry = TournamentRound(
        **data.model_dump(),
        tournament_id=tournament_id
    )
    db.add(round_entry)

    # Update tournament status if needed
    if tournament.status == TournamentStatus.UPCOMING:
        tournament.status = TournamentStatus.IN_PROGRESS

    # Update total rounds
    tournament.total_rounds = max(tournament.total_rounds, data.round_number)

    await db.flush()
    await db.refresh(round_entry)

    return TournamentRoundRead.model_validate(round_entry)


@router.put("/{tournament_id}/rounds/{round_id}", response_model=TournamentRoundRead)
async def update_round(
    tournament_id: int,
    round_id: int,
    data: TournamentRoundUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Update a tournament round"""
    # Verify tournament ownership
    query = select(Tournament).where(
        Tournament.id == tournament_id,
        Tournament.user_id == current_user.id
    )
    result = await db.execute(query)
    tournament = result.scalar_one_or_none()

    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    # Get the round
    round_query = select(TournamentRound).where(
        TournamentRound.id == round_id,
        TournamentRound.tournament_id == tournament_id
    )
    result = await db.execute(round_query)
    round_entry = result.scalar_one_or_none()

    if not round_entry:
        raise HTTPException(status_code=404, detail="Round not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(round_entry, field, value)

    await db.flush()
    await db.refresh(round_entry)

    return TournamentRoundRead.model_validate(round_entry)


@router.delete("/{tournament_id}/rounds/{round_id}")
async def delete_round(
    tournament_id: int,
    round_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Delete a tournament round"""
    # Verify tournament ownership
    query = select(Tournament).where(
        Tournament.id == tournament_id,
        Tournament.user_id == current_user.id
    )
    result = await db.execute(query)
    tournament = result.scalar_one_or_none()

    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    # Get the round
    round_query = select(TournamentRound).where(
        TournamentRound.id == round_id,
        TournamentRound.tournament_id == tournament_id
    )
    result = await db.execute(round_query)
    round_entry = result.scalar_one_or_none()

    if not round_entry:
        raise HTTPException(status_code=404, detail="Round not found")

    await db.delete(round_entry)
    return {"message": "Round deleted"}


@router.post("/{tournament_id}/complete", response_model=TournamentRead)
async def complete_tournament(
    tournament_id: int,
    final_standing: Optional[int] = None,
    championship_points: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Mark a tournament as completed"""
    query = select(Tournament).options(
        selectinload(Tournament.rounds)
    ).where(
        Tournament.id == tournament_id,
        Tournament.user_id == current_user.id
    )
    result = await db.execute(query)
    tournament = result.scalar_one_or_none()

    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    tournament.status = TournamentStatus.COMPLETED
    if final_standing:
        tournament.final_standing = final_standing
    tournament.championship_points = championship_points

    # Calculate final record
    wins, losses, ties = calculate_record(tournament.rounds)
    tournament.final_record = f"{wins}-{losses}-{ties}"

    await db.flush()
    await db.refresh(tournament)

    return TournamentRead.model_validate(enrich_tournament(tournament))
