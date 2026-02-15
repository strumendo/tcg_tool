"""Service functions for deck-related operations."""

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deck_parser import parse_deck
from app.models import Card, CardSet, Deck, DeckCard, UserCollection
from app.schemas.collection import MissingCardOut
from app.schemas.deck import DeckCreate, DeckImport, DeckUpdate


async def create_deck(
    db: AsyncSession, user_id: int, data: DeckCreate
) -> Deck:
    """Create a new deck for the user with optional cards."""
    deck = Deck(
        user_id=user_id,
        name=data.name,
        archetype=data.archetype,
        notes=data.notes,
        is_active=data.is_active,
        total_cards=0,
    )
    db.add(deck)
    await db.flush()

    total = 0
    for card_input in data.cards:
        deck_card = DeckCard(
            deck_id=deck.id,
            card_id=card_input.card_id,
            quantity=card_input.quantity,
        )
        db.add(deck_card)
        total += card_input.quantity

    deck.total_cards = total
    deck.is_valid = total == 60
    await db.commit()

    return await get_deck(db, deck.id)


async def get_user_decks(db: AsyncSession, user_id: int) -> list[Deck]:
    """List all decks for a user."""
    stmt = (
        select(Deck)
        .where(Deck.user_id == user_id)
        .options(
            selectinload(Deck.deck_cards).selectinload(DeckCard.card).selectinload(Card.card_set),
            selectinload(Deck.deck_cards).selectinload(DeckCard.card).selectinload(Card.abilities),
            selectinload(Deck.deck_cards).selectinload(DeckCard.card).selectinload(Card.attacks),
            selectinload(Deck.deck_cards).selectinload(DeckCard.card).selectinload(Card.functions),
        )
        .order_by(Deck.updated_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().unique().all())


async def get_deck(db: AsyncSession, deck_id: int) -> Deck:
    """Fetch a single deck by ID with all card relationships."""
    stmt = (
        select(Deck)
        .where(Deck.id == deck_id)
        .options(
            selectinload(Deck.deck_cards).selectinload(DeckCard.card).selectinload(Card.card_set),
            selectinload(Deck.deck_cards).selectinload(DeckCard.card).selectinload(Card.abilities),
            selectinload(Deck.deck_cards).selectinload(DeckCard.card).selectinload(Card.attacks),
            selectinload(Deck.deck_cards).selectinload(DeckCard.card).selectinload(Card.functions),
        )
    )
    result = await db.execute(stmt)
    deck = result.scalar_one_or_none()
    if deck is None:
        raise HTTPException(status_code=404, detail=f"Deck {deck_id} not found")
    return deck


async def update_deck(
    db: AsyncSession, deck_id: int, data: DeckUpdate
) -> Deck:
    """Update a deck's metadata and optionally replace its card list."""
    deck = await get_deck(db, deck_id)

    if data.name is not None:
        deck.name = data.name
    if data.archetype is not None:
        deck.archetype = data.archetype
    if data.notes is not None:
        deck.notes = data.notes
    if data.is_active is not None:
        deck.is_active = data.is_active

    if data.cards is not None:
        # Remove existing cards and replace with new list
        for existing in list(deck.deck_cards):
            await db.delete(existing)
        await db.flush()

        total = 0
        for card_input in data.cards:
            deck_card = DeckCard(
                deck_id=deck.id,
                card_id=card_input.card_id,
                quantity=card_input.quantity,
            )
            db.add(deck_card)
            total += card_input.quantity

        deck.total_cards = total
        deck.is_valid = total == 60

    await db.commit()
    return await get_deck(db, deck.id)


async def delete_deck(db: AsyncSession, deck_id: int) -> None:
    """Delete a deck by ID."""
    deck = await get_deck(db, deck_id)
    await db.delete(deck)
    await db.commit()


async def import_deck(
    db: AsyncSession, user_id: int, data: DeckImport
) -> Deck:
    """Import a deck from PTCGO/TCG Live text format.

    Parses the text, resolves cards against the database by name + set code,
    and creates a new deck.
    """
    parsed = parse_deck(data.deck_text)

    deck = Deck(
        user_id=user_id,
        name=data.name,
        total_cards=0,
    )
    db.add(deck)
    await db.flush()

    total = 0
    unresolved: list[str] = []

    for parsed_card in parsed.cards:
        # Try to find the card in the database by name and set code
        stmt = (
            select(Card)
            .join(Card.card_set)
            .where(
                Card.name_en.ilike(parsed_card.name),
                CardSet.code == parsed_card.set_code,
            )
        )
        result = await db.execute(stmt)
        card = result.scalar_one_or_none()

        if card is None:
            # Try matching just by name
            stmt = select(Card).where(Card.name_en.ilike(parsed_card.name))
            result = await db.execute(stmt)
            card = result.scalar_one_or_none()

        if card is not None:
            deck_card = DeckCard(
                deck_id=deck.id,
                card_id=card.id,
                quantity=parsed_card.quantity,
            )
            db.add(deck_card)
            total += parsed_card.quantity
        else:
            unresolved.append(
                f"{parsed_card.quantity} {parsed_card.name} "
                f"{parsed_card.set_code} {parsed_card.set_number}"
            )

    deck.total_cards = total
    deck.is_valid = total == 60

    if unresolved:
        deck.notes = "Unresolved cards:\n" + "\n".join(unresolved)

    await db.commit()
    return await get_deck(db, deck.id)


async def export_deck(db: AsyncSession, deck_id: int) -> str:
    """Export a deck to PTCGO/TCG Live text format."""
    deck = await get_deck(db, deck_id)

    lines: list[str] = []
    pokemon_lines: list[str] = []
    trainer_lines: list[str] = []
    energy_lines: list[str] = []

    for dc in deck.deck_cards:
        card = dc.card
        set_code = card.card_set.code if card.card_set else "UNK"
        set_number = card.set_number or "0"
        name = card.name_en or card.name_pt or "Unknown"
        line = f"{dc.quantity} {name} {set_code} {set_number}"

        if card.card_type == "pokemon":
            pokemon_lines.append(line)
        elif card.card_type == "trainer":
            trainer_lines.append(line)
        elif card.card_type == "energy":
            energy_lines.append(line)
        else:
            trainer_lines.append(line)

    if pokemon_lines:
        lines.append("Pokemon:")
        lines.extend(pokemon_lines)
        lines.append("")

    if trainer_lines:
        lines.append("Trainer:")
        lines.extend(trainer_lines)
        lines.append("")

    if energy_lines:
        lines.append("Energy:")
        lines.extend(energy_lines)
        lines.append("")

    return "\n".join(lines)


async def get_deck_missing_cards(
    db: AsyncSession, deck_id: int, user_id: int
) -> list[MissingCardOut]:
    """Determine which cards in a deck the user is missing from their collection."""
    deck = await get_deck(db, deck_id)

    # Fetch the user's collection for the cards in this deck
    card_ids = [dc.card_id for dc in deck.deck_cards]
    if not card_ids:
        return []

    stmt = (
        select(UserCollection)
        .where(
            UserCollection.user_id == user_id,
            UserCollection.card_id.in_(card_ids),
        )
    )
    result = await db.execute(stmt)
    collection_map: dict[int, int] = {
        uc.card_id: uc.quantity_owned for uc in result.scalars().all()
    }

    missing: list[MissingCardOut] = []
    for dc in deck.deck_cards:
        owned = collection_map.get(dc.card_id, 0)
        needed = dc.quantity
        if owned < needed:
            card_name = None
            if dc.card:
                card_name = dc.card.name_en or dc.card.name_pt
            missing.append(
                MissingCardOut(
                    card_id=dc.card_id,
                    card_name=card_name,
                    quantity_needed=needed,
                    quantity_owned=owned,
                    quantity_missing=needed - owned,
                )
            )

    return missing
