"""Card substitution logic with analysis."""
from dataclasses import dataclass, field
from models import Card, CardType, CardFunction, Substitution
from card_api import get_new_set_cards


# Known staple substitutions
KNOWN_SUBSTITUTIONS = {
    # Supporters
    "Professor's Research": ["Professor Turo's Scenario", "Professor Sada's Vitality"],
    "Boss's Orders": ["Boss's Orders (Ghetsis)", "Counter Catcher"],
    "Iono": [],  # Will need new alternative
    "Arven": [],  # Unique effect

    # Items
    "Nest Ball": ["Buddy-Buddy Poffin", "Pokémon Catcher"],
    "Ultra Ball": [],  # Staple in every set
    "Rare Candy": [],  # Staple reprinted
    "Switch": ["Escape Rope", "Switch Cart"],
    "Battle VIP Pass": [],  # No direct replacement

    # Stadiums
    "Artazon": [],
    "Mesagoza": [],
}


def calculate_type_match(original: Card, candidate: Card) -> float:
    """Calculate match score based on card type/subtype (0-100)."""
    if original.card_type != candidate.card_type:
        return 0.0

    score = 50.0  # Base score for same type

    if original.subtype and candidate.subtype:
        if original.subtype.lower() == candidate.subtype.lower():
            score += 50.0  # Perfect subtype match
        elif original.subtype.lower() in candidate.subtype.lower():
            score += 25.0  # Partial match
    elif not original.subtype and not candidate.subtype:
        score += 30.0  # Both without subtype

    return min(score, 100.0)


def calculate_function_match(original: Card, candidate: Card) -> float:
    """Calculate match score based on function (0-100)."""
    if not original.functions or not candidate.functions:
        return 30.0  # Unknown function, neutral score

    original_funcs = set(original.functions)
    candidate_funcs = set(candidate.functions)

    if not original_funcs:
        return 30.0

    # Calculate Jaccard similarity
    intersection = len(original_funcs & candidate_funcs)
    union = len(original_funcs | candidate_funcs)

    if union == 0:
        return 30.0

    return (intersection / union) * 100


def calculate_archetype_match(original: Card, candidate: Card) -> float:
    """Calculate match score based on archetype compatibility (0-100)."""
    # For Pokemon, check energy type match
    if original.card_type == CardType.POKEMON and candidate.card_type == CardType.POKEMON:
        if original.energy_type and candidate.energy_type:
            if original.energy_type.lower() == candidate.energy_type.lower():
                return 100.0
            # Colorless is always compatible
            if candidate.energy_type.lower() == "colorless":
                return 70.0
            return 30.0

    # For trainers, all are generally archetype-neutral
    if original.card_type == CardType.TRAINER:
        return 70.0

    # For energy, type match is critical
    if original.card_type == CardType.ENERGY:
        if original.name.lower() == candidate.name.lower():
            return 100.0
        return 20.0

    return 50.0


def calculate_match_score(original: Card, candidate: Card) -> tuple[float, list[str]]:
    """
    Calculate overall match score with reasons.

    Weights:
    - Type/Subtype: 40%
    - Function: 40%
    - Archetype: 20%
    """
    reasons = []

    # Type match (40%)
    type_score = calculate_type_match(original, candidate)
    if type_score >= 80:
        reasons.append(f"Same type/subtype ({type_score:.0f}%)")
    elif type_score >= 50:
        reasons.append(f"Same card type ({type_score:.0f}%)")

    # Function match (40%)
    func_score = calculate_function_match(original, candidate)
    if func_score >= 70:
        reasons.append(f"Similar function ({func_score:.0f}%)")
    elif func_score >= 40:
        reasons.append(f"Partial function match ({func_score:.0f}%)")

    # Archetype match (20%)
    arch_score = calculate_archetype_match(original, candidate)
    if arch_score >= 80:
        reasons.append(f"Good archetype fit ({arch_score:.0f}%)")

    # Weighted average
    total_score = (type_score * 0.4) + (func_score * 0.4) + (arch_score * 0.2)

    return total_score, reasons


def find_substitutions(
    rotating_cards: list[Card],
    new_set_code: str = "ASC",
    min_score: float = 30.0
) -> list[Substitution]:
    """Find substitutions from new set for rotating cards."""
    substitutions = []

    # Get cards from new set
    new_cards = get_new_set_cards(new_set_code)

    if not new_cards:
        return substitutions

    for rotating_card in rotating_cards:
        best_subs = []

        for new_card in new_cards:
            # Skip if same card type doesn't match
            if rotating_card.card_type != new_card.card_type:
                continue

            score, reasons = calculate_match_score(rotating_card, new_card)

            if score >= min_score:
                best_subs.append(Substitution(
                    original_card=rotating_card,
                    suggested_card=new_card,
                    match_score=score,
                    reasons=reasons
                ))

        # Sort by score and take top 3
        best_subs.sort(key=lambda x: x.match_score, reverse=True)
        substitutions.extend(best_subs[:3])

    return substitutions


def find_substitutions_from_pool(
    rotating_cards: list[Card],
    available_cards: list[Card],
    min_score: float = 30.0
) -> list[Substitution]:
    """Find substitutions from a pool of available cards."""
    substitutions = []

    for rotating_card in rotating_cards:
        best_subs = []

        for available_card in available_cards:
            # Skip rotating cards
            if available_card.is_rotating:
                continue

            # Skip if card type doesn't match
            if rotating_card.card_type != available_card.card_type:
                continue

            score, reasons = calculate_match_score(rotating_card, available_card)

            if score >= min_score:
                best_subs.append(Substitution(
                    original_card=rotating_card,
                    suggested_card=available_card,
                    match_score=score,
                    reasons=reasons
                ))

        # Sort by score and take top 3
        best_subs.sort(key=lambda x: x.match_score, reverse=True)
        substitutions.extend(best_subs[:3])

    return substitutions


def generate_updated_deck(
    original_cards: list[Card],
    substitutions: list[Substitution]
) -> list[Card]:
    """Generate updated deck with substitutions applied."""
    updated = []
    substitution_map = {}

    # Build map of best substitutions
    for sub in substitutions:
        key = (sub.original_card.set_code, sub.original_card.set_number)
        if key not in substitution_map or sub.match_score > substitution_map[key].match_score:
            substitution_map[key] = sub

    for card in original_cards:
        key = (card.set_code, card.set_number)

        if card.is_rotating and key in substitution_map:
            # Replace with substitution
            sub = substitution_map[key]
            new_card = Card(
                name=sub.suggested_card.name,
                card_type=sub.suggested_card.card_type,
                set_code=sub.suggested_card.set_code,
                set_number=sub.suggested_card.set_number,
                quantity=card.quantity,
                regulation_mark=sub.suggested_card.regulation_mark,
                subtype=sub.suggested_card.subtype
            )
            updated.append(new_card)
        elif not card.is_rotating:
            # Keep safe cards
            updated.append(card)
        # Rotating cards without substitution are dropped

    return updated
