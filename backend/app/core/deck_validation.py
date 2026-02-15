"""
Deck validation rules for standard Pokemon TCG format.

Checks:
- Exactly 60 cards.
- No more than 4 copies of any non-basic-energy card.
- All cards are legal (not already rotated).

No framework dependencies -- pure Python only.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.core.deck_parser import ParsedDeck


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_DECK_SIZE: int = 60
MAX_COPIES: int = 4

UNLIMITED_CARDS: list[str] = [
    "Basic Fire Energy",
    "Basic Water Energy",
    "Basic Grass Energy",
    "Basic Lightning Energy",
    "Basic Psychic Energy",
    "Basic Fighting Energy",
    "Basic Darkness Energy",
    "Basic Metal Energy",
    "Basic Fairy Energy",
]

# Normalised set for fast membership checks
_UNLIMITED_LOWER: set[str] = {name.lower() for name in UNLIMITED_CARDS}


# ---------------------------------------------------------------------------
# Result data class
# ---------------------------------------------------------------------------

@dataclass
class ValidationResult:
    """Outcome of validating a deck."""
    is_valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Validation logic
# ---------------------------------------------------------------------------

def validate_deck(deck: ParsedDeck) -> ValidationResult:
    """Validate *deck* against standard format rules.

    Returns a ``ValidationResult`` with ``is_valid`` set to ``False`` if
    any hard errors are found, plus a list of warnings for softer issues.
    """
    result = ValidationResult()

    # 1. Deck size ----------------------------------------------------------
    total = deck.total_cards
    if total != MAX_DECK_SIZE:
        result.is_valid = False
        result.errors.append(
            f"Deck has {total} cards (must be exactly {MAX_DECK_SIZE})"
        )

    # 2. Max copies ---------------------------------------------------------
    name_counts: dict[str, int] = {}
    for card in deck.cards:
        lower = card.name.lower()
        name_counts[lower] = name_counts.get(lower, 0) + card.quantity

    for name, count in name_counts.items():
        if name in _UNLIMITED_LOWER:
            continue
        if count > MAX_COPIES:
            result.is_valid = False
            result.errors.append(
                f"Too many copies of '{name}': {count} (max {MAX_COPIES})"
            )

    # 3. Card legality ------------------------------------------------------
    for card in deck.cards:
        if card.is_already_rotated:
            result.is_valid = False
            result.errors.append(
                f"Illegal card (already rotated): {card.name} "
                f"[{card.set_code} {card.set_number}] "
                f"(regulation mark {card.regulation_mark})"
            )

    # 4. Rotation warnings --------------------------------------------------
    for card in deck.cards:
        if card.is_rotating:
            result.warnings.append(
                f"Rotating in March 2026: {card.name} "
                f"[{card.set_code} {card.set_number}]"
            )

    return result
