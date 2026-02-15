"""Chat service for AI-powered conversations."""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import Deck, DeckCard, Card, MetaDeck


async def build_deck_context(db: AsyncSession, deck_id: int) -> str:
    """Build a context string from a deck for the AI."""
    # Query deck with cards
    stmt = (
        select(Deck)
        .where(Deck.id == deck_id)
        .options(
            selectinload(Deck.deck_cards)
            .selectinload(DeckCard.card)
            .selectinload(Card.card_set)
        )
    )
    result = await db.execute(stmt)
    deck = result.scalar_one_or_none()
    if not deck:
        return ""

    lines = [f"Deck: {deck.name} (Archetype: {deck.archetype or 'Unknown'})"]
    lines.append(f"Total cards: {deck.total_cards}")

    pokemon, trainers, energy = [], [], []
    for dc in deck.deck_cards:
        card = dc.card
        name = card.name_en or card.name_pt or "Unknown"
        entry = f"{dc.quantity}x {name}"
        if card.regulation_mark:
            entry += f" [{card.regulation_mark}]"
        if card.card_set:
            entry += f" ({card.card_set.code})"

        if card.card_type == "pokemon":
            pokemon.append(entry)
        elif card.card_type == "trainer":
            trainers.append(entry)
        else:
            energy.append(entry)

    if pokemon:
        lines.append(f"\nPokemon ({len(pokemon)}):")
        lines.extend(f"  {p}" for p in pokemon)
    if trainers:
        lines.append(f"\nTrainers ({len(trainers)}):")
        lines.extend(f"  {t}" for t in trainers)
    if energy:
        lines.append(f"\nEnergy ({len(energy)}):")
        lines.extend(f"  {e}" for e in energy)

    return "\n".join(lines)


async def build_meta_context(db: AsyncSession) -> str:
    """Build a summary of current meta for AI context."""
    stmt = (
        select(MetaDeck)
        .order_by(MetaDeck.tier, MetaDeck.meta_share.desc())
        .limit(10)
    )
    result = await db.execute(stmt)
    meta_decks = result.scalars().all()

    if not meta_decks:
        return ""

    lines = ["Current Meta (March 2026 format):"]
    for md in meta_decks:
        name = md.name_en or md.name_pt or "Unknown"
        lines.append(f"  Tier {md.tier}: {name} ({md.meta_share:.1f}% share)")

    lines.append("\nRotation: Regulation Mark G rotating out (SVI, PAL, OBF, MEW, PAR, PAF)")
    lines.append("Legal: Regulation Marks H (TEF+) and I (PRE+)")

    return "\n".join(lines)


def build_system_prompt(deck_context: str = "", meta_context: str = "") -> str:
    """Build the full system prompt with available context."""
    parts = [
        "You are a Pokemon TCG expert assistant. You help players with deck building, "
        "strategy analysis, card substitutions, and competitive play advice. "
        "You are knowledgeable about the current Standard format (March 2026 rotation), "
        "meta decks, matchups, and card interactions. "
        "Respond in the same language as the user's message. "
        "Format your responses with clear structure using markdown when helpful."
    ]

    if meta_context:
        parts.append(f"\n\n--- META CONTEXT ---\n{meta_context}")

    if deck_context:
        parts.append(f"\n\n--- USER'S DECK ---\n{deck_context}")

    return "\n".join(parts)


def format_history_for_api(history: list[dict]) -> list[dict]:
    """Format chat history for the Claude API messages parameter."""
    formatted = []
    for msg in history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role in ("user", "assistant") and content:
            formatted.append({"role": role, "content": content})
    return formatted
