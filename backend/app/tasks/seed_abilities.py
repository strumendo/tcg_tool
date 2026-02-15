"""Seed the ability catalog from the legacy abilities database.

Reads ``old/abilities_database.py`` and populates ``cards``,
``card_abilities``, and ``card_functions`` with the curated data.

This task is idempotent: running it again will skip rows that already
exist (matched by card name_en + set_code + set_number).

Usage (standalone)::

    python -m app.tasks.seed_abilities
"""

import asyncio
import importlib.util
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory
from app.models.card import Card, CardAbility, CardFunction, CardSet


# ---------------------------------------------------------------------------
# Load the old abilities database via importlib
# ---------------------------------------------------------------------------

def _load_old_module():
    """Dynamically import old/abilities_database.py from the project root."""
    # Determine project root (two levels up from backend/app/tasks/).
    project_root = Path(__file__).resolve().parents[3]
    module_path = project_root / "old" / "abilities_database.py"

    if not module_path.exists():
        raise FileNotFoundError(
            f"Old abilities database not found at {module_path}.  "
            "Ensure the 'old/abilities_database.py' file exists in the project root."
        )

    spec = importlib.util.spec_from_file_location("abilities_database", str(module_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Ability category -> CardFunction mapping
# ---------------------------------------------------------------------------

# Maps AbilityCategory enum values to the function strings used in
# the CardFunction model.  Only the most common/useful mappings are
# included.
_CATEGORY_TO_FUNCTION = {
    "draw_power": "DRAW",
    "search": "SEARCH",
    "pokemon_search": "SEARCH",
    "recovery": "RECOVERY",
    "switching": "SWITCHING",
    "energy_accel": "ENERGY_ACCEL",
    "energy_transfer": "ENERGY_ACCEL",
    "healing": "HEALING",
    "bench_barrier": "BENCH_BARRIER",
    "safeguard": "WALL",
    "damage_reduction": "WALL",
    "effect_block": "WALL",
    "spread_damage": "SPREAD",
    "snipe": "SNIPE",
    "damage_boost": "DAMAGE_BOOST",
    "hand_disruption": "DISRUPTION",
    "item_lock": "DISRUPTION",
    "ability_lock": "DISRUPTION",
    "mill": "MILL",
    "energy_denial": "DISRUPTION",
    "free_retreat": "SWITCHING",
    "evolution_support": "SETUP",
}


# ---------------------------------------------------------------------------
# Seeding logic
# ---------------------------------------------------------------------------

async def seed_abilities() -> None:
    """Seed cards, abilities, and functions from the old abilities database."""
    module = _load_old_module()
    pokemon_db: dict = getattr(module, "POKEMON_DATABASE", {})

    if not pokemon_db:
        print("[seed_abilities] POKEMON_DATABASE is empty, nothing to seed")
        return

    print(f"[seed_abilities] Found {len(pokemon_db)} Pokemon entries to seed")

    created = 0
    skipped = 0

    async with async_session_factory() as session:
        for key, poke in pokemon_db.items():
            try:
                was_created = await _seed_pokemon(session, poke)
                if was_created:
                    created += 1
                else:
                    skipped += 1
            except Exception as exc:
                name = getattr(poke, "name_en", key)
                print(f"[seed_abilities]   Error seeding '{name}': {exc}")

        await session.commit()

    print(
        f"[seed_abilities] Done: {created} created, {skipped} already existed "
        f"(total {created + skipped})"
    )


async def _seed_pokemon(session: AsyncSession, poke) -> bool:
    """Seed a single PokemonCard from the old database.

    Returns ``True`` if the card was newly created, ``False`` if it
    already existed.
    """
    name_en = poke.name_en
    set_code = poke.set_code
    set_number = poke.set_number

    # Check if the card already exists (by name + set_code + set_number).
    card = await _find_existing_card(session, name_en, set_code, set_number)
    if card is not None:
        # Card already seeded -- ensure abilities and functions are present
        # but do not duplicate.
        await _ensure_abilities(session, card, poke)
        await _ensure_functions(session, card, poke)
        return False

    # Resolve or create CardSet.
    card_set = await _get_or_create_set(session, set_code)

    # Create Card.
    card = Card(
        name_en=name_en,
        name_pt=poke.name_pt,
        card_type="POKEMON",
        set_id=card_set.id if card_set else None,
        set_number=set_number,
        hp=poke.hp,
        energy_type=poke.energy_type,
        stage=poke.stage,
        is_ex=poke.is_ex,
        regulation_mark=poke.regulation_mark,
    )
    session.add(card)
    await session.flush()

    # Create abilities.
    for ab in poke.abilities:
        session.add(
            CardAbility(
                card_id=card.id,
                name_en=ab.name,
                name_pt=ab.name_pt,
                effect_en=ab.effect_en,
                effect_pt=ab.effect_pt,
                category=ab.category.value if hasattr(ab.category, "value") else str(ab.category),
            )
        )

    # Create functions from ability categories + attack categories.
    functions_added: set[str] = set()
    for ab in poke.abilities:
        cat_val = ab.category.value if hasattr(ab.category, "value") else str(ab.category)
        func_name = _CATEGORY_TO_FUNCTION.get(cat_val)
        if func_name and func_name not in functions_added:
            session.add(CardFunction(card_id=card.id, function=func_name))
            functions_added.add(func_name)

    for atk_cat in getattr(poke, "attack_categories", []):
        cat_val = atk_cat.value if hasattr(atk_cat, "value") else str(atk_cat)
        func_name = _CATEGORY_TO_FUNCTION.get(cat_val)
        if func_name and func_name not in functions_added:
            session.add(CardFunction(card_id=card.id, function=func_name))
            functions_added.add(func_name)

    return True


async def _find_existing_card(
    session: AsyncSession,
    name_en: str,
    set_code: str,
    set_number: str,
) -> Card | None:
    """Look up an existing card by name + set code + number."""
    # First try by set_id + set_number.
    stmt_set = select(CardSet).where(CardSet.code == set_code)
    result_set = await session.execute(stmt_set)
    card_set = result_set.scalar_one_or_none()

    if card_set is not None:
        stmt = select(Card).where(
            Card.set_id == card_set.id,
            Card.set_number == set_number,
        )
        result = await session.execute(stmt)
        card = result.scalar_one_or_none()
        if card is not None:
            return card

    # Fallback: search by name (case-insensitive).
    stmt2 = select(Card).where(Card.name_en.ilike(name_en)).limit(1)
    result2 = await session.execute(stmt2)
    return result2.scalar_one_or_none()


async def _get_or_create_set(session: AsyncSession, set_code: str) -> CardSet | None:
    """Get or create a ``CardSet`` row for the given code."""
    stmt = select(CardSet).where(CardSet.code == set_code)
    result = await session.execute(stmt)
    card_set = result.scalar_one_or_none()

    if card_set is None:
        card_set = CardSet(code=set_code)
        session.add(card_set)
        await session.flush()

    return card_set


async def _ensure_abilities(session: AsyncSession, card: Card, poke) -> None:
    """Ensure all abilities from the old data exist on the card."""
    # Fetch existing ability names.
    stmt = select(CardAbility.name_en).where(CardAbility.card_id == card.id)
    result = await session.execute(stmt)
    existing_names = {row[0] for row in result.all()}

    for ab in poke.abilities:
        if ab.name in existing_names:
            continue
        session.add(
            CardAbility(
                card_id=card.id,
                name_en=ab.name,
                name_pt=ab.name_pt,
                effect_en=ab.effect_en,
                effect_pt=ab.effect_pt,
                category=ab.category.value if hasattr(ab.category, "value") else str(ab.category),
            )
        )


async def _ensure_functions(session: AsyncSession, card: Card, poke) -> None:
    """Ensure all functions derived from the old data exist on the card."""
    stmt = select(CardFunction.function).where(CardFunction.card_id == card.id)
    result = await session.execute(stmt)
    existing_functions = {row[0] for row in result.all()}

    for ab in poke.abilities:
        cat_val = ab.category.value if hasattr(ab.category, "value") else str(ab.category)
        func_name = _CATEGORY_TO_FUNCTION.get(cat_val)
        if func_name and func_name not in existing_functions:
            session.add(CardFunction(card_id=card.id, function=func_name))
            existing_functions.add(func_name)

    for atk_cat in getattr(poke, "attack_categories", []):
        cat_val = atk_cat.value if hasattr(atk_cat, "value") else str(atk_cat)
        func_name = _CATEGORY_TO_FUNCTION.get(cat_val)
        if func_name and func_name not in existing_functions:
            session.add(CardFunction(card_id=card.id, function=func_name))
            existing_functions.add(func_name)


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------

async def _main() -> None:
    await seed_abilities()


if __name__ == "__main__":
    asyncio.run(_main())
