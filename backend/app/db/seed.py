"""Seed script for populating the database with initial meta deck and matchup data.

Reads data from old/meta_database.py and inserts it into the PostgreSQL database
via async SQLAlchemy. The script is idempotent: it checks for existing records
before inserting and uses merge to avoid duplicates.

Usage:
    python -m app.db.seed
"""

import asyncio
import sys
from datetime import date
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

# ---------------------------------------------------------------------------
# Import the old meta_database module via sys.path manipulation,
# since old/ is not a Python package.
# ---------------------------------------------------------------------------
_project_root = Path(__file__).resolve().parents[3]  # tcg_tool/
_old_path = str(_project_root / "old")
if _old_path not in sys.path:
    sys.path.insert(0, _old_path)

from meta_database import META_DECKS, MATCHUPS  # type: ignore[import-untyped]  # noqa: E402

# Import ORM models (must be done after path setup so app.* imports work)
from app.models.meta import MetaDeck, MetaMatchup  # noqa: E402
from app.models.user import User  # noqa: E402


async def seed_database() -> None:
    """Seed the database with default user, meta decks, and matchup data.

    This function is idempotent -- it will not create duplicate rows if
    the data already exists.
    """
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        async with session.begin():
            # -----------------------------------------------------------------
            # 1. Default user
            # -----------------------------------------------------------------
            result = await session.execute(
                select(User).where(User.username == "default")
            )
            existing_user = result.scalars().first()
            if existing_user is None:
                default_user = User(
                    id=1,
                    username="default",
                    language="pt",
                )
                session.add(default_user)
                print("[seed] Created default user (id=1, username='default', language='pt')")
            else:
                print("[seed] Default user already exists, skipping.")

            # -----------------------------------------------------------------
            # 2. Meta decks
            # -----------------------------------------------------------------
            created_decks = 0
            skipped_decks = 0
            snapshot = date.today()

            for old_deck in META_DECKS.values():
                result = await session.execute(
                    select(MetaDeck).where(MetaDeck.id == old_deck.id)
                )
                existing = result.scalars().first()
                if existing is not None:
                    skipped_decks += 1
                    continue

                meta_deck = MetaDeck(
                    id=old_deck.id,
                    name_en=old_deck.name_en,
                    name_pt=old_deck.name_pt,
                    tier=old_deck.tier,
                    description_en=old_deck.description_en,
                    description_pt=old_deck.description_pt,
                    strategy_en=old_deck.strategy_en,
                    strategy_pt=old_deck.strategy_pt,
                    difficulty=old_deck.difficulty,
                    meta_share=old_deck.meta_share,
                    key_pokemon=old_deck.key_pokemon,
                    energy_types=old_deck.energy_types,
                    strengths_en=old_deck.strengths_en,
                    strengths_pt=old_deck.strengths_pt,
                    weaknesses_en=old_deck.weaknesses_en,
                    weaknesses_pt=old_deck.weaknesses_pt,
                    snapshot_date=snapshot,
                )
                session.add(meta_deck)
                created_decks += 1

            print(
                f"[seed] Meta decks: {created_decks} created, "
                f"{skipped_decks} already existed."
            )

            # -----------------------------------------------------------------
            # 3. Matchup data
            # -----------------------------------------------------------------
            created_matchups = 0
            skipped_matchups = 0

            for matchup_data in MATCHUPS:
                result = await session.execute(
                    select(MetaMatchup).where(
                        MetaMatchup.deck_a_id == matchup_data.deck_a_id,
                        MetaMatchup.deck_b_id == matchup_data.deck_b_id,
                    )
                )
                existing = result.scalars().first()
                if existing is not None:
                    skipped_matchups += 1
                    continue

                matchup = MetaMatchup(
                    deck_a_id=matchup_data.deck_a_id,
                    deck_b_id=matchup_data.deck_b_id,
                    win_rate_a=matchup_data.win_rate_a,
                    notes_en=matchup_data.notes_en,
                    notes_pt=matchup_data.notes_pt,
                    snapshot_date=snapshot,
                )
                session.add(matchup)
                created_matchups += 1

            print(
                f"[seed] Matchups: {created_matchups} created, "
                f"{skipped_matchups} already existed."
            )

        # session.begin() auto-commits on exit
        print("[seed] Database seeding complete.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_database())
