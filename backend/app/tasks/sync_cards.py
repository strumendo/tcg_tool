"""Sync card data from TCGdex API into the PostgreSQL database.

This task fetches set and card information from the TCGdex REST API and
upserts it into the local ``card_sets``, ``cards``, ``card_abilities``,
and ``card_attacks`` tables.

Usage (standalone)::

    python -m app.tasks.sync_cards          # sync everything
    python -m app.tasks.sync_cards sv7      # sync a single set
"""

import asyncio
import sys
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory
from app.integrations.tcgdex_client import TCGdexClient
from app.models.card import Card, CardAbility, CardAttack, CardSet


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_CARD_TYPE_MAP = {
    "pokemon": "POKEMON",
    "trainer": "TRAINER",
    "energy": "ENERGY",
}

_TRAINER_SUBTYPE_MAP = {
    "supporter": "Supporter",
    "item": "Item",
    "stadium": "Stadium",
    "tool": "Tool",
}


def _resolve_card_type(raw: str | None) -> str:
    """Normalise a TCGdex ``category`` value to an internal card-type string."""
    if raw is None:
        return "POKEMON"
    return _CARD_TYPE_MAP.get(raw.lower().strip(), "POKEMON")


def _resolve_trainer_subtype(raw: str | None) -> str | None:
    """Return a clean trainer subtype if applicable."""
    if raw is None:
        return None
    return _TRAINER_SUBTYPE_MAP.get(raw.lower().strip())


def _is_ex(name: str | None) -> bool:
    """Detect whether the card name indicates a Pokemon ex."""
    if name is None:
        return False
    lower = name.lower()
    return lower.endswith(" ex") or " ex " in lower


def _parse_date(raw: str | None) -> Optional[datetime]:
    """Parse a TCGdex release-date string (YYYY-MM-DD or YYYY/MM/DD)."""
    if not raw:
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    return None


# ---------------------------------------------------------------------------
# Set sync
# ---------------------------------------------------------------------------

async def sync_all_sets(client: TCGdexClient | None = None) -> list[CardSet]:
    """Fetch every set from TCGdex and upsert into ``card_sets``.

    Returns the list of persisted ``CardSet`` instances.
    """
    own_client = client is None
    if own_client:
        client = TCGdexClient()

    raw_sets = await client.get("/en/sets") or []
    if not isinstance(raw_sets, list):
        raw_sets = raw_sets.get("data", raw_sets.get("sets", []))

    print(f"[sync_cards] Fetched {len(raw_sets)} sets from TCGdex")

    persisted: list[CardSet] = []
    async with async_session_factory() as session:
        for s in raw_sets:
            try:
                card_set = await _upsert_set(session, s)
                persisted.append(card_set)
            except Exception as exc:
                sid = s.get("id", "?")
                print(f"[sync_cards] Error upserting set {sid}: {exc}")
        await session.commit()

    print(f"[sync_cards] Upserted {len(persisted)} sets")
    return persisted


async def _upsert_set(session: AsyncSession, data: dict) -> CardSet:
    """Insert or update a single ``CardSet`` row."""
    tcgdex_id = data.get("id", "")
    code = data.get("abbreviation") or data.get("id", "")

    stmt = select(CardSet).where(CardSet.code == code)
    result = await session.execute(stmt)
    card_set = result.scalar_one_or_none()

    if card_set is None:
        card_set = CardSet(code=code)
        session.add(card_set)

    card_set.tcgdex_id = tcgdex_id
    card_set.name_en = data.get("name")
    card_set.total_cards = data.get("cardCount", {}).get("total") if isinstance(data.get("cardCount"), dict) else data.get("total")
    card_set.release_date = _parse_date(data.get("releaseDate"))
    # TCGdex doesn't always include regulation mark at the set level;
    # it is set per-card instead.  We store it here when available.
    card_set.regulation_mark = data.get("regulationMark")

    return card_set


# ---------------------------------------------------------------------------
# Card sync (per set)
# ---------------------------------------------------------------------------

async def sync_set_cards(set_code: str, client: TCGdexClient | None = None) -> int:
    """Fetch all cards in *set_code* from TCGdex and upsert them.

    Returns the number of cards upserted.
    """
    own_client = client is None
    if own_client:
        client = TCGdexClient()

    set_data = await client.fetch_set(set_code)
    if set_data is None:
        print(f"[sync_cards] Set '{set_code}' not found on TCGdex")
        return 0

    card_list = set_data.get("cards", [])
    if not card_list:
        print(f"[sync_cards] No cards in set '{set_code}'")
        return 0

    print(f"[sync_cards] Set '{set_code}': {len(card_list)} cards to sync")

    count = 0
    async with async_session_factory() as session:
        # Ensure we have the CardSet row.
        stmt = select(CardSet).where(CardSet.code == set_code)
        result = await session.execute(stmt)
        card_set = result.scalar_one_or_none()
        if card_set is None:
            card_set = CardSet(
                code=set_code,
                tcgdex_id=set_data.get("id", set_code),
                name_en=set_data.get("name"),
            )
            session.add(card_set)
            await session.flush()

        for card_brief in card_list:
            try:
                card_id_str = card_brief.get("id") or f"{set_code}-{card_brief.get('localId', '')}"
                # Fetch full card detail.
                full = await client.fetch_card_by_id(card_id_str)
                if full is None:
                    print(f"[sync_cards]   Skipping card {card_id_str} (fetch failed)")
                    continue

                await _upsert_card(session, card_set, full, client)
                count += 1
            except Exception as exc:
                cid = card_brief.get("id", "?")
                print(f"[sync_cards]   Error processing card {cid}: {exc}")

            # Be respectful to the API.
            await asyncio.sleep(0.15)

        await session.commit()

    print(f"[sync_cards] Set '{set_code}': {count} cards upserted")
    return count


async def _upsert_card(
    session: AsyncSession,
    card_set: CardSet,
    data: dict,
    client: TCGdexClient,
) -> Card:
    """Insert or update a single ``Card`` row together with its abilities
    and attacks."""
    tcgdex_id = data.get("id", "")
    local_id = data.get("localId", "")
    name = data.get("name", "")

    # Look up by tcgdex_id first, then by set+number.
    stmt = select(Card).where(Card.tcgdex_id == tcgdex_id)
    result = await session.execute(stmt)
    card = result.scalar_one_or_none()

    if card is None:
        stmt2 = select(Card).where(
            Card.set_id == card_set.id,
            Card.set_number == str(local_id),
        )
        result2 = await session.execute(stmt2)
        card = result2.scalar_one_or_none()

    is_new = card is None
    if is_new:
        card = Card(
            set_id=card_set.id,
            set_number=str(local_id),
            tcgdex_id=tcgdex_id,
            card_type=_resolve_card_type(data.get("category")),
        )
        session.add(card)

    # Update scalar fields.
    card.name_en = name
    card.tcgdex_id = tcgdex_id
    card.card_type = _resolve_card_type(data.get("category"))
    card.trainer_subtype = _resolve_trainer_subtype(data.get("item") or data.get("trainerType"))
    card.hp = int(data["hp"]) if data.get("hp") else None
    card.energy_type = data.get("types", [None])[0] if data.get("types") else None
    card.stage = data.get("stage")
    card.is_ex = _is_ex(name)
    card.regulation_mark = data.get("regulationMark") or (card_set.regulation_mark if card_set else None)
    card.image_url = client.get_card_image_url(card_set.code, str(local_id), quality="high")
    card.image_url_hires = client.get_card_image_url(card_set.code, str(local_id), quality="high")

    # Flush to ensure card.id is available for FK references.
    await session.flush()

    # --- Abilities -----------------------------------------------------------
    if not is_new:
        # Remove existing abilities so we can recreate them cleanly.
        for old in list(card.abilities):
            await session.delete(old)
        await session.flush()

    for ab in data.get("abilities", []):
        session.add(
            CardAbility(
                card_id=card.id,
                name_en=ab.get("name"),
                effect_en=ab.get("effect"),
                category=None,  # category is set later by seed_abilities
            )
        )

    # --- Attacks -------------------------------------------------------------
    if not is_new:
        for old in list(card.attacks):
            await session.delete(old)
        await session.flush()

    for atk in data.get("attacks", []):
        energy_cost = atk.get("cost")
        session.add(
            CardAttack(
                card_id=card.id,
                name_en=atk.get("name"),
                damage=atk.get("damage"),
                energy_cost=energy_cost if isinstance(energy_cost, (list, dict)) else None,
                effect_en=atk.get("effect"),
            )
        )

    return card


# ---------------------------------------------------------------------------
# Full sync
# ---------------------------------------------------------------------------

async def sync_all_cards() -> None:
    """Sync every set and every card from TCGdex into the database."""
    client = TCGdexClient()

    print("[sync_cards] === Starting full card sync ===")
    sets = await sync_all_sets(client)
    total = 0
    for cs in sets:
        n = await sync_set_cards(cs.code, client)
        total += n
    print(f"[sync_cards] === Full sync complete: {total} cards across {len(sets)} sets ===")


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------

async def _main() -> None:
    args = sys.argv[1:]
    if args:
        # Sync a specific set.
        for code in args:
            await sync_set_cards(code)
    else:
        await sync_all_cards()


if __name__ == "__main__":
    asyncio.run(_main())
