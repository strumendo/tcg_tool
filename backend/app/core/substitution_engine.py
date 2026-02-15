"""
Card substitution engine.

Scores how well a candidate card can replace a rotating card using
type match (40 %), function match (40 %), and archetype fit (20 %).
Provides helpers to find the best substitutions from a pool of
available cards and to generate an updated deck list.

No framework dependencies -- pure Python only.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.core.deck_parser import ParsedCard, CardType


# ---------------------------------------------------------------------------
# Substitution data class
# ---------------------------------------------------------------------------

@dataclass
class Substitution:
    """A suggested replacement for a rotating card."""
    original_card: ParsedCard
    suggested_card: ParsedCard
    match_score: float          # 0 -- 100
    reasons: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        return (
            f"{self.original_card.name} -> {self.suggested_card.name} "
            f"({self.match_score:.0f}%)"
        )


# ---------------------------------------------------------------------------
# Known staple substitutions
# ---------------------------------------------------------------------------

KNOWN_SUBSTITUTIONS: dict[str, list[str]] = {
    # Supporters
    "Professor's Research": ["Professor Turo's Scenario", "Professor Sada's Vitality"],
    "Boss's Orders":        ["Boss's Orders (Ghetsis)", "Counter Catcher"],
    "Iono":                 [],
    "Arven":                [],
    # Items
    "Nest Ball":            ["Buddy-Buddy Poffin", "Pokemon Catcher"],
    "Ultra Ball":           [],
    "Rare Candy":           [],
    "Switch":               ["Escape Rope", "Switch Cart"],
    "Battle VIP Pass":      [],
    # Stadiums
    "Artazon":              [],
    "Mesagoza":             [],
}


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------

def calculate_type_match(original: ParsedCard, candidate: ParsedCard) -> float:
    """Score based on card type and subtype (0 -- 100)."""
    if original.card_type != candidate.card_type:
        return 0.0

    score = 50.0  # same card type

    if original.subtype and candidate.subtype:
        if original.subtype.lower() == candidate.subtype.lower():
            score += 50.0
        elif original.subtype.lower() in candidate.subtype.lower():
            score += 25.0
    elif not original.subtype and not candidate.subtype:
        score += 30.0

    return min(score, 100.0)


def calculate_function_match(
    original: ParsedCard,
    candidate: ParsedCard,
    original_functions: list[str] | None = None,
    candidate_functions: list[str] | None = None,
) -> float:
    """Score based on functional overlap (0 -- 100).

    Because ``ParsedCard`` is a lightweight parse result without enriched
    function data, callers may optionally supply function lists.  When no
    functions are available a neutral 30 % is returned.
    """
    o_funcs = set(original_functions or [])
    c_funcs = set(candidate_functions or [])

    if not o_funcs or not c_funcs:
        return 30.0

    intersection = len(o_funcs & c_funcs)
    union = len(o_funcs | c_funcs)

    if union == 0:
        return 30.0

    return (intersection / union) * 100


def calculate_archetype_match(original: ParsedCard, candidate: ParsedCard) -> float:
    """Score based on archetype compatibility (0 -- 100).

    For Pokemon, same energy type => 100; colorless candidate => 70.
    Trainers are generally archetype-neutral (70).
    Energy requires exact name match.
    """
    if original.card_type == CardType.POKEMON and candidate.card_type == CardType.POKEMON:
        # Without enriched data, compare by name heuristics (e.g. energy
        # type embedded in name).  Fall back to neutral.
        return 50.0

    if original.card_type == CardType.TRAINER:
        return 70.0

    if original.card_type == CardType.ENERGY:
        if original.name.lower() == candidate.name.lower():
            return 100.0
        return 20.0

    return 50.0


def calculate_match_score(
    original: ParsedCard,
    candidate: ParsedCard,
    original_functions: list[str] | None = None,
    candidate_functions: list[str] | None = None,
) -> tuple[float, list[str]]:
    """Compute an overall match score with reasons.

    Weights: type/subtype 40 %, function 40 %, archetype 20 %.
    """
    reasons: list[str] = []

    type_score = calculate_type_match(original, candidate)
    if type_score >= 80:
        reasons.append(f"Same type/subtype ({type_score:.0f}%)")
    elif type_score >= 50:
        reasons.append(f"Same card type ({type_score:.0f}%)")

    func_score = calculate_function_match(
        original, candidate, original_functions, candidate_functions
    )
    if func_score >= 70:
        reasons.append(f"Similar function ({func_score:.0f}%)")
    elif func_score >= 40:
        reasons.append(f"Partial function match ({func_score:.0f}%)")

    arch_score = calculate_archetype_match(original, candidate)
    if arch_score >= 80:
        reasons.append(f"Good archetype fit ({arch_score:.0f}%)")

    total = (type_score * 0.4) + (func_score * 0.4) + (arch_score * 0.2)

    return total, reasons


# ---------------------------------------------------------------------------
# Substitution search
# ---------------------------------------------------------------------------

def find_substitutions_from_pool(
    rotating_cards: list[ParsedCard],
    available_cards: list[ParsedCard],
    min_score: float = 30.0,
    max_per_card: int = 3,
) -> list[Substitution]:
    """Find the best substitutions for *rotating_cards* from *available_cards*.

    Only non-rotating candidates are considered.  Returns up to
    *max_per_card* suggestions per rotating card, sorted by score.
    """
    substitutions: list[Substitution] = []

    for rotating in rotating_cards:
        best: list[Substitution] = []

        for candidate in available_cards:
            # Skip candidates that are themselves rotating
            if candidate.is_rotating:
                continue
            # Must share a card type
            if rotating.card_type != candidate.card_type:
                continue

            score, reasons = calculate_match_score(rotating, candidate)
            if score >= min_score:
                best.append(Substitution(
                    original_card=rotating,
                    suggested_card=candidate,
                    match_score=score,
                    reasons=reasons,
                ))

        best.sort(key=lambda s: s.match_score, reverse=True)
        substitutions.extend(best[:max_per_card])

    return substitutions


# ---------------------------------------------------------------------------
# Deck generation with substitutions applied
# ---------------------------------------------------------------------------

def generate_updated_deck(
    original_cards: list[ParsedCard],
    substitutions: list[Substitution],
) -> list[ParsedCard]:
    """Return a new card list with substitutions applied.

    * Rotating cards with a substitution are replaced (keeping the original
      quantity).
    * Safe cards are kept as-is.
    * Rotating cards *without* a substitution are dropped.
    """
    # Build a map of the best substitution per original card identity
    sub_map: dict[tuple[str, str], Substitution] = {}
    for sub in substitutions:
        key = (sub.original_card.set_code, sub.original_card.set_number)
        if key not in sub_map or sub.match_score > sub_map[key].match_score:
            sub_map[key] = sub

    updated: list[ParsedCard] = []

    for card in original_cards:
        key = (card.set_code, card.set_number)

        if card.is_rotating and key in sub_map:
            replacement = sub_map[key].suggested_card
            updated.append(ParsedCard(
                name=replacement.name,
                card_type=replacement.card_type,
                set_code=replacement.set_code,
                set_number=replacement.set_number,
                quantity=card.quantity,
                regulation_mark=replacement.regulation_mark,
                subtype=replacement.subtype,
            ))
        elif not card.is_rotating:
            updated.append(card)
        # else: rotating without substitution -- dropped

    return updated
