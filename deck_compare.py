"""Deck comparison and matchup analysis."""
from dataclasses import dataclass, field
from models import Deck, Card, CardType


@dataclass
class DeckComparison:
    """Result of comparing two decks."""
    deck_a: Deck
    deck_b: Deck
    deck_a_name: str = "Your Deck"
    deck_b_name: str = "Opponent Deck"

    # Shared cards (same name)
    shared_cards: list[tuple[Card, Card]] = field(default_factory=list)

    # Unique cards
    unique_to_a: list[Card] = field(default_factory=list)
    unique_to_b: list[Card] = field(default_factory=list)

    @property
    def shared_count(self) -> int:
        """Count of shared card names."""
        return len(self.shared_cards)

    @property
    def similarity_percentage(self) -> float:
        """How similar the decks are (0-100)."""
        total_unique_names = len(self.shared_cards) + len(self.unique_to_a) + len(self.unique_to_b)
        if total_unique_names == 0:
            return 0.0
        return (len(self.shared_cards) / total_unique_names) * 100


@dataclass
class MatchupAnalysis:
    """Matchup analysis between two decks."""
    deck_a: Deck
    deck_b: Deck
    deck_a_name: str = "Your Deck"
    deck_b_name: str = "Opponent Deck"

    # Type advantages
    a_advantages: list[str] = field(default_factory=list)
    b_advantages: list[str] = field(default_factory=list)

    # Key differences
    key_differences: list[str] = field(default_factory=list)

    # Scores
    speed_score_a: int = 0  # 0-10
    speed_score_b: int = 0
    consistency_score_a: int = 0  # 0-10
    consistency_score_b: int = 0
    power_score_a: int = 0  # 0-10
    power_score_b: int = 0

    @property
    def matchup_favor(self) -> str:
        """Which deck is favored."""
        score_a = len(self.a_advantages)
        score_b = len(self.b_advantages)
        if score_a > score_b:
            return self.deck_a_name
        elif score_b > score_a:
            return self.deck_b_name
        return "Even"


# Pokemon type weakness chart
TYPE_WEAKNESSES = {
    "grass": "fire",
    "fire": "water",
    "water": "lightning",
    "lightning": "fighting",
    "fighting": "psychic",
    "psychic": "darkness",
    "darkness": "fighting",
    "metal": "fire",
    "dragon": "dragon",
    "colorless": None,
    "fairy": "metal",
}


def get_deck_energy_types(deck: Deck) -> set[str]:
    """Get all energy types used in a deck."""
    types = set()
    for card in deck.cards:
        if card.card_type == CardType.POKEMON and card.energy_type:
            types.add(card.energy_type.lower())
        elif card.card_type == CardType.ENERGY:
            # Extract type from energy name
            name_lower = card.name.lower()
            for energy_type in TYPE_WEAKNESSES.keys():
                if energy_type in name_lower:
                    types.add(energy_type)
                    break
    return types


def get_main_attackers(deck: Deck) -> list[Card]:
    """Get main attacking Pokemon (ex, V, VSTAR, etc.)."""
    attackers = []
    for card in deck.cards:
        if card.card_type == CardType.POKEMON:
            name_lower = card.name.lower()
            if any(suffix in name_lower for suffix in [" ex", " v", " vstar", " vmax", " gx"]):
                attackers.append(card)
    return attackers


def count_card_type(deck: Deck, subtype: str) -> int:
    """Count cards of a specific subtype."""
    count = 0
    for card in deck.cards:
        if card.subtype and card.subtype.lower() == subtype.lower():
            count += card.quantity
    return count


def count_search_cards(deck: Deck) -> int:
    """Count search/consistency cards."""
    search_names = [
        "ultra ball", "nest ball", "level ball", "quick ball", "poke ball",
        "professor", "research", "iono", "arven", "irida", "buddy-buddy poffin",
        "battle vip pass"
    ]
    count = 0
    for card in deck.cards:
        name_lower = card.name.lower()
        if any(s in name_lower for s in search_names):
            count += card.quantity
    return count


def count_draw_supporters(deck: Deck) -> int:
    """Count draw supporters."""
    draw_names = ["professor", "research", "iono", "cynthia", "marnie", "colress"]
    count = 0
    for card in deck.cards:
        name_lower = card.name.lower()
        if card.subtype == "supporter" and any(s in name_lower for s in draw_names):
            count += card.quantity
    return count


def compare_decks(deck_a: Deck, deck_b: Deck,
                  name_a: str = "Your Deck", name_b: str = "Opponent Deck") -> DeckComparison:
    """Compare two decks and find similarities/differences."""
    comparison = DeckComparison(
        deck_a=deck_a,
        deck_b=deck_b,
        deck_a_name=name_a,
        deck_b_name=name_b
    )

    # Build name -> card maps
    cards_a = {card.name.lower(): card for card in deck_a.cards}
    cards_b = {card.name.lower(): card for card in deck_b.cards}

    # Find shared and unique
    all_names = set(cards_a.keys()) | set(cards_b.keys())

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


def analyze_matchup(deck_a: Deck, deck_b: Deck,
                    name_a: str = "Your Deck", name_b: str = "Opponent Deck") -> MatchupAnalysis:
    """Analyze matchup between two decks."""
    analysis = MatchupAnalysis(
        deck_a=deck_a,
        deck_b=deck_b,
        deck_a_name=name_a,
        deck_b_name=name_b
    )

    # Get energy types
    types_a = get_deck_energy_types(deck_a)
    types_b = get_deck_energy_types(deck_b)

    # Check type advantages
    for type_a in types_a:
        weakness = TYPE_WEAKNESSES.get(type_a)
        if weakness and weakness in types_b:
            analysis.b_advantages.append(f"{name_b} has {weakness.title()} weakness advantage over {type_a.title()}")

    for type_b in types_b:
        weakness = TYPE_WEAKNESSES.get(type_b)
        if weakness and weakness in types_a:
            analysis.a_advantages.append(f"{name_a} has {weakness.title()} weakness advantage over {type_b.title()}")

    # Get main attackers
    attackers_a = get_main_attackers(deck_a)
    attackers_b = get_main_attackers(deck_b)

    if len(attackers_a) > len(attackers_b):
        analysis.a_advantages.append(f"More attack options ({len(attackers_a)} vs {len(attackers_b)})")
    elif len(attackers_b) > len(attackers_a):
        analysis.b_advantages.append(f"More attack options ({len(attackers_b)} vs {len(attackers_a)})")

    # Calculate speed scores (based on search/setup cards)
    search_a = count_search_cards(deck_a)
    search_b = count_search_cards(deck_b)
    analysis.speed_score_a = min(10, search_a // 2)
    analysis.speed_score_b = min(10, search_b // 2)

    if search_a > search_b + 4:
        analysis.a_advantages.append(f"More consistent setup ({search_a} vs {search_b} search cards)")
    elif search_b > search_a + 4:
        analysis.b_advantages.append(f"More consistent setup ({search_b} vs {search_a} search cards)")

    # Calculate consistency scores (based on draw supporters)
    draw_a = count_draw_supporters(deck_a)
    draw_b = count_draw_supporters(deck_b)
    analysis.consistency_score_a = min(10, draw_a)
    analysis.consistency_score_b = min(10, draw_b)

    # Key differences
    pokemon_diff = deck_a.pokemon_count - deck_b.pokemon_count
    if abs(pokemon_diff) >= 4:
        if pokemon_diff > 0:
            analysis.key_differences.append(f"{name_a} runs more Pokemon ({deck_a.pokemon_count} vs {deck_b.pokemon_count})")
        else:
            analysis.key_differences.append(f"{name_b} runs more Pokemon ({deck_b.pokemon_count} vs {deck_a.pokemon_count})")

    trainer_diff = deck_a.trainer_count - deck_b.trainer_count
    if abs(trainer_diff) >= 4:
        if trainer_diff > 0:
            analysis.key_differences.append(f"{name_a} runs more Trainers ({deck_a.trainer_count} vs {deck_b.trainer_count})")
        else:
            analysis.key_differences.append(f"{name_b} runs more Trainers ({deck_b.trainer_count} vs {deck_a.trainer_count})")

    return analysis


def analyze_against_meta(your_deck: Deck, meta_decks: list[tuple[str, Deck]]) -> list[tuple[str, MatchupAnalysis]]:
    """Analyze your deck against multiple meta decks."""
    results = []
    for name, meta_deck in meta_decks:
        analysis = analyze_matchup(your_deck, meta_deck, "Your Deck", name)
        results.append((name, analysis))
    return results
