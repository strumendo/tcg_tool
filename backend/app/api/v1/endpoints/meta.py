"""Meta/competitive data endpoints"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.db import get_db
from app.models.meta import MetaSnapshot, MetaDeck
from app.models.deck import Deck
from app.schemas.meta import (
    MetaSnapshotCreate, MetaSnapshotRead, MetaSnapshotListRead,
    DeckComparisonRequest, DeckComparisonResult
)

router = APIRouter()


@router.get("/snapshots", response_model=MetaSnapshotListRead)
async def list_snapshots(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List all meta snapshots"""
    query = select(MetaSnapshot).options(selectinload(MetaSnapshot.meta_decks))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(MetaSnapshot.snapshot_date.desc())
    result = await db.execute(query)
    snapshots = result.scalars().unique().all()

    return MetaSnapshotListRead(
        snapshots=[MetaSnapshotRead.model_validate(s) for s in snapshots],
        total=total or 0,
        page=page,
        page_size=page_size
    )


@router.get("/snapshots/latest", response_model=MetaSnapshotRead)
async def get_latest_snapshot(db: AsyncSession = Depends(get_db)):
    """Get the most recent meta snapshot"""
    query = select(MetaSnapshot).options(
        selectinload(MetaSnapshot.meta_decks)
    ).order_by(MetaSnapshot.snapshot_date.desc()).limit(1)

    result = await db.execute(query)
    snapshot = result.scalar_one_or_none()

    if not snapshot:
        raise HTTPException(status_code=404, detail="No snapshots available")

    return MetaSnapshotRead.model_validate(snapshot)


@router.get("/snapshots/{snapshot_id}", response_model=MetaSnapshotRead)
async def get_snapshot(snapshot_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific meta snapshot"""
    query = select(MetaSnapshot).options(
        selectinload(MetaSnapshot.meta_decks)
    ).where(MetaSnapshot.id == snapshot_id)

    result = await db.execute(query)
    snapshot = result.scalar_one_or_none()

    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")

    return MetaSnapshotRead.model_validate(snapshot)


@router.post("/snapshots", response_model=MetaSnapshotRead)
async def create_snapshot(
    snapshot: MetaSnapshotCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new meta snapshot"""
    snapshot_data = snapshot.model_dump(exclude={"meta_decks"})
    db_snapshot = MetaSnapshot(**snapshot_data)
    db.add(db_snapshot)
    await db.flush()

    # Add meta decks if provided
    if snapshot.meta_decks:
        for deck_data in snapshot.meta_decks:
            meta_deck = MetaDeck(snapshot_id=db_snapshot.id, **deck_data.model_dump())
            db.add(meta_deck)

    await db.refresh(db_snapshot)
    return MetaSnapshotRead.model_validate(db_snapshot)


@router.post("/import/file", response_model=MetaSnapshotRead)
async def import_meta_from_file(
    file: UploadFile = File(...),
    name: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Import meta data from a file"""
    from app.services.meta_import import MetaImportService

    content = await file.read()
    filename = file.filename or "unknown"

    import_service = MetaImportService(db)

    if filename.endswith(".json"):
        snapshot = await import_service.import_from_json(content, name)
    elif filename.endswith(".csv"):
        snapshot = await import_service.import_from_csv(content, name)
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Use .json or .csv"
        )

    return MetaSnapshotRead.model_validate(snapshot)


@router.get("/top10")
async def get_top10_decks(
    snapshot_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get top 10 decks from latest or specified snapshot"""
    if snapshot_id:
        query = select(MetaSnapshot).options(
            selectinload(MetaSnapshot.meta_decks)
        ).where(MetaSnapshot.id == snapshot_id)
    else:
        query = select(MetaSnapshot).options(
            selectinload(MetaSnapshot.meta_decks)
        ).order_by(MetaSnapshot.snapshot_date.desc()).limit(1)

    result = await db.execute(query)
    snapshot = result.scalar_one_or_none()

    if not snapshot:
        raise HTTPException(status_code=404, detail="No meta data available")

    top_decks = sorted(snapshot.meta_decks, key=lambda x: x.rank)[:10]

    return {
        "snapshot_id": snapshot.id,
        "snapshot_name": snapshot.name,
        "snapshot_date": snapshot.snapshot_date.isoformat(),
        "top_decks": [
            {
                "rank": d.rank,
                "archetype": d.archetype,
                "meta_share": d.meta_share,
                "win_rate": d.win_rate,
                "matchups": d.matchups
            }
            for d in top_decks
        ]
    }


@router.post("/compare", response_model=DeckComparisonResult)
async def compare_deck_to_meta(
    request: DeckComparisonRequest,
    db: AsyncSession = Depends(get_db)
):
    """Compare a user's deck against the meta"""
    from app.services.meta_analysis import MetaAnalysisService

    # Get the deck
    deck_query = select(Deck).where(Deck.id == request.deck_id)
    deck_result = await db.execute(deck_query)
    deck = deck_result.scalar_one_or_none()

    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")

    # Get the snapshot
    if request.snapshot_id:
        snapshot_query = select(MetaSnapshot).options(
            selectinload(MetaSnapshot.meta_decks)
        ).where(MetaSnapshot.id == request.snapshot_id)
    else:
        snapshot_query = select(MetaSnapshot).options(
            selectinload(MetaSnapshot.meta_decks)
        ).order_by(MetaSnapshot.snapshot_date.desc()).limit(1)

    snapshot_result = await db.execute(snapshot_query)
    snapshot = snapshot_result.scalar_one_or_none()

    if not snapshot:
        raise HTTPException(status_code=404, detail="No meta data available")

    analysis_service = MetaAnalysisService(db)
    comparison_result = await analysis_service.compare_deck_to_meta(deck, snapshot)

    return comparison_result
