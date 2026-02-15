"""Battle API route handlers."""

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dependencies import DBSession
from app.models import Battle, BattleAction
from app.schemas.battle import BattleCreate, BattleOut, BattleUpdate

router = APIRouter()

# Hardcoded user ID until authentication is implemented.
_USER_ID = 1


async def _get_battle(db: AsyncSession, battle_id: int) -> Battle:
    """Fetch a battle by ID with actions loaded."""
    stmt = (
        select(Battle)
        .where(Battle.id == battle_id)
        .options(selectinload(Battle.actions))
    )
    result = await db.execute(stmt)
    battle = result.scalar_one_or_none()
    if battle is None:
        raise HTTPException(status_code=404, detail=f"Battle {battle_id} not found")
    return battle


@router.get("/", response_model=list[BattleOut])
async def list_battles(db: DBSession) -> list[BattleOut]:
    """List all battles for the current user."""
    stmt = (
        select(Battle)
        .where(Battle.user_id == _USER_ID)
        .options(selectinload(Battle.actions))
        .order_by(Battle.played_at.desc())
    )
    result = await db.execute(stmt)
    battles = result.scalars().unique().all()
    return [BattleOut.model_validate(b) for b in battles]


@router.post("/", response_model=BattleOut, status_code=201)
async def create_battle(db: DBSession, data: BattleCreate) -> BattleOut:
    """Create a new battle record."""
    battle = Battle(
        user_id=_USER_ID,
        deck_id=data.deck_id,
        opponent_deck_name=data.opponent_deck_name,
        opponent_meta_deck_id=data.opponent_meta_deck_id,
        result=data.result,
        total_turns=data.total_turns,
        went_first=data.went_first,
        notes=data.notes,
        source=data.source,
        source_url=data.source_url,
        played_at=data.played_at or datetime.now(timezone.utc),
    )
    db.add(battle)
    await db.flush()

    for action_input in data.actions:
        action = BattleAction(
            battle_id=battle.id,
            turn=action_input.turn,
            player=action_input.player,
            action_type=action_input.action_type,
            card_name=action_input.card_name,
            details=action_input.details,
            sequence_order=action_input.sequence_order,
        )
        db.add(action)

    await db.commit()
    return BattleOut.model_validate(await _get_battle(db, battle.id))


@router.get("/{battle_id}", response_model=BattleOut)
async def get_battle(db: DBSession, battle_id: int) -> BattleOut:
    """Get a single battle by ID."""
    battle = await _get_battle(db, battle_id)
    return BattleOut.model_validate(battle)


@router.put("/{battle_id}", response_model=BattleOut)
async def update_battle(
    db: DBSession, battle_id: int, data: BattleUpdate
) -> BattleOut:
    """Update a battle record."""
    battle = await _get_battle(db, battle_id)

    if data.opponent_deck_name is not None:
        battle.opponent_deck_name = data.opponent_deck_name
    if data.opponent_meta_deck_id is not None:
        battle.opponent_meta_deck_id = data.opponent_meta_deck_id
    if data.result is not None:
        battle.result = data.result
    if data.total_turns is not None:
        battle.total_turns = data.total_turns
    if data.went_first is not None:
        battle.went_first = data.went_first
    if data.notes is not None:
        battle.notes = data.notes
    if data.source is not None:
        battle.source = data.source
    if data.source_url is not None:
        battle.source_url = data.source_url

    await db.commit()
    return BattleOut.model_validate(await _get_battle(db, battle.id))


@router.delete("/{battle_id}", status_code=204)
async def delete_battle(db: DBSession, battle_id: int) -> None:
    """Delete a battle record."""
    battle = await _get_battle(db, battle_id)
    await db.delete(battle)
    await db.commit()
