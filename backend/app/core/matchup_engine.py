"""
Deck comparison and matchup analysis engine.

Compares two ``ParsedDeck`` instances to find shared / unique cards,
type advantages, speed / consistency scores, and key differences.

No framework dependencies -- pure Python only.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.core.deck_parser import ParsedCard, ParsedDeck, CardType
from app.core.type_chart import TYPE_WEAKNESSES


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class DeckComparison:
    """Result of comparing two decks card-by-card."""
    deck_a: ParsedDeck
    deck_b: ParsedDeck
    deck_a_name: str = "Your Deck"
    deck_b_name: str = "Opponent Deck"

    shared_cards: list[tuple[ParsedCard, ParsedCard]] = field(default_factory=list)
    unique_to_a: list[ParsedCard] = field(default_factory=list)
    unique_to_b: list[ParsedCard] = field(default_factory=list)

    @property
    def shared_count(self) -> int:
        return len(self.shared_cards)

    @property
    def similarity_percentage(self) -> float:
        total = len(self.shared_cards) + len(self.unique_to_a) + len(self.unique_to_b)
        if total == 0:
            return 0.0
        return (len(self.shared_cards) / total) * 100


@dataclass
class MatchupAnalysis:
    """High-level matchup analysis between two decks."""
    deck_a: ParsedDeck
    deck_b: ParsedDeck
    deck_a_name: str = "Your Deck"
    deck_b_name: str = "Opponent Deck"

    a_advantages: list[str] = field(default_factory=list)
    b_advantages: list[str] = field(default_factory=list)
    key_differences: list[str] = field(default_factory=list)

    speed_score_a: int = 0       # 0-10
    speed_score_b: int = 0
    consistency_score_a: int = 0  # 0-10
    consistency_score_b: int = 0
    power_score_a: int = 0       # 0-10
    power_score_b: int = 0

    @property
    def matchup_favor(self) -> str:
        score_a = len(self.a_advantages)
        score_b = len(self.b_advantages)
        if score_a > score_b:
            return self.deck_a_name
        elif score_b > score_a:
            return self.deck_b_name
        return "Even"


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def get_deck_energy_types(deck: ParsedDeck) -> set[str]:
    """Return the set of energy types present in *deck*."""
    types: set[str] = set()
    for card in deck.cards:
        if card.card_type == CardType.ENERGY:
            lower = card.name.lower()
            for energy_type in TYPE_WEAKNESSES:
                if energy_type in lower:
                    types.add(energy_type)
                    break
    return types


def get_main_attackers(deck: ParsedDeck) -> list[ParsedCard]:
    """Return the main attacking Pokemon (ex, V, VSTAR, VMAX, GX)."""
    attackers: list[ParsedCard] = []
    for card in deck.cards:
        if card.card_type == CardType.POKEMON:
            lower = card.name.lower()
            if any(s in lower for s in (" ex", " v", " vstar", " vmax", " gx")):
                attackers.append(card)
    return attackers


def count_search_cards(deck: ParsedDeck) -> int:
    """Count search / consistency cards in *deck*."""
    search_names = [
        "ultra ball", "nest ball", "level ball", "quick ball", "poke ball",
        "professor", "research", "iono", "arven", "irida",
        "buddy-buddy poffin", "battle vip pass",
    ]
    total = 0
    for card in deck.cards:
        lower = card.name.lower()
        if any(s in lower for s in search_names):
            total += card.quantity
    return total


def count_draw_supporters(deck: ParsedDeck) -> int:
    """Count draw supporters in *deck*."""
    draw_names = ["professor", "research", "iono", "cynthia", "marnie", "colress"]
    total = 0
    for card in deck.cards:
        lower = card.name.lower()
        if card.subtype == "supporter" and any(s in lower for s in draw_names):
            total += card.quantity
    return total


# ---------------------------------------------------------------------------
# Comparison / analysis entry points
# ---------------------------------------------------------------------------

def compare_decks(
    deck_a: ParsedDeck,
    deck_b: ParsedDeck,
    name_a: str = "Your Deck",
    name_b: str = "Opponent Deck",
) -> DeckComparison:
    """Compare two decks and identify shared / unique cards."""
    comparison = DeckComparison(
        deck_a=deck_a,
        deck_b=deck_b,
        deck_a_name=name_a,
        deck_b_name=name_b,
    )

    cards_a = {card.name.lower(): card for card in deck_a.cards}
    cards_b = {card.name.lower(): card for card in deck_b.cards}

    all_names = set(cards_a) | set(cards_b)

    for name in all_names:
        in_a = name in cards_a
        in_b = name in cards_b

        if in_a and in_b:
            comparison.shared_cards.append((cards_a[name], cards_b[name]))
        elif in_a:
            comparison.unique_to_a.append(cards_a[name])
        else:
            comparison.unique_to_b.append(cards_b[name])

    return comparison


def analyze_matchup(
    deck_a: ParsedDeck,
    deck_b: ParsedDeck,
    name_a: str = "Your Deck",
    name_b: str = "Opponent Deck",
) -> MatchupAnalysis:
    """Perform a matchup analysis between two decks."""
    analysis = MatchupAnalysis(
        deck_a=deck_a,
        deck_b=deck_b,
        deck_a_name=name_a,
        deck_b_name=name_b,
    )

    types_a = get_deck_energy_types(deck_a)
    types_b = get_deck_energy_types(deck_b)

    # Type advantages -------------------------------------------------------
    for t_a in types_a:
        weakness = TYPE_WEAKNESSES.get(t_a)
        if weakness and weakness in types_b:
            analysis.b_advantages.append(
                f"{name_b} has {weakness.title()} weakness advantage over {t_a.title()}"
            )

    for t_b in types_b:
        weakness = TYPE_WEAKNESSES.get(t_b)
        if weakness and weakness in types_a:
            analysis.a_advantages.append(
                f"{name_a} has {weakness.title()} weakness advantage over {t_b.title()}"
            )

    # Attacker count --------------------------------------------------------
    attackers_a = get_main_attackers(deck_a)
    attackers_b = get_main_attackers(deck_b)

    if len(attackers_a) > len(attackers_b):
        analysis.a_advantages.append(
            f"More attack options ({len(attackers_a)} vs {len(attackers_b)})"
        )
    elif len(attackers_b) > len(attackers_a):
        analysis.b_advantages.append(
            f"More attack options ({len(attackers_b)} vs {len(attackers_a)})"
        )

    # Speed scores ----------------------------------------------------------
    search_a = count_search_cards(deck_a)
    search_b = count_search_cards(deck_b)
    analysis.speed_score_a = min(10, search_a // 2)
    analysis.speed_score_b = min(10, search_b // 2)

    if search_a > search_b + 4:
        analysis.a_advantages.append(
            f"More consistent setup ({search_a} vs {search_b} search cards)"
        )
    elif search_b > search_a + 4:
        analysis.b_advantages.append(
            f"More consistent setup ({search_b} vs {search_a} search cards)"
        )

    # Consistency scores ----------------------------------------------------
    draw_a = count_draw_supporters(deck_a)
    draw_b = count_draw_supporters(deck_b)
    analysis.consistency_score_a = min(10, draw_a)
    analysis.consistency_score_b = min(10, draw_b)

    # Key differences -------------------------------------------------------
    pokemon_diff = deck_a.pokemon_count - deck_b.pokemon_count
    if abs(pokemon_diff) >= 4:
        if pokemon_diff > 0:
            analysis.key_differences.append(
                f"{name_a} runs more Pokemon ({deck_a.pokemon_count} vs {deck_b.pokemon_count})"
            )
        else:
            analysis.key_differences.append(
                f"{name_b} runs more Pokemon ({deck_b.pokemon_count} vs {deck_a.pokemon_count})"
            )

    trainer_diff = deck_a.trainer_count - deck_b.trainer_count
    if abs(trainer_diff) >= 4:
        if trainer_diff > 0:
            analysis.key_differences.append(
                f"{name_a} runs more Trainers ({deck_a.trainer_count} vs {deck_b.trainer_count})"
            )
        else:
            analysis.key_differences.append(
                f"{name_b} runs more Trainers ({deck_b.trainer_count} vs {deck_a.trainer_count})"
            )

    return analysis
