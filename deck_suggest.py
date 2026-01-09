"""Deck suggestion module for Pokemon TCG."""
from dataclasses import dataclass, field
from typing import Optional
from card_api import search_pokemon_by_name, get_pokemon_details


@dataclass
class PokemonInfo:
    """Information about a Pokemon card."""
    name: str
    set_name: str
    set_code: str
    number: str
    regulation_mark: str
    types: list[str]
    hp: Optional[int]
    subtypes: list[str]
    is_ex: bool = False
    is_v: bool = False
    is_vstar: bool = False
    is_vmax: bool = False
    attacks: list[dict] = field(default_factory=list)
    abilities: list[dict] = field(default_factory=list)


@dataclass
class DeckSuggestion:
    """A deck suggestion for a Pokemon."""
    archetype_name: str
    description: str
    pokemon: PokemonInfo
    strategy: str
    key_cards: list[str]
    energy_types: list[str]
    strengths: list[str]
    weaknesses: list[str]
    difficulty: str  # Beginner, Intermediate, Advanced


# Meta deck archetypes with their characteristics
DECK_ARCHETYPES = {
    "Fire": {
        "partners": ["Arcanine", "Entei", "Magcargo", "Delphox", "Blaziken"],
        "supports": ["Arven", "Iono", "Boss's Orders", "Rare Candy", "Ultra Ball"],
        "energy_accel": ["Magma Basin", "Blacksmith", "Welder"],
        "strategy": "Aggressive damage with Fire-type acceleration",
    },
    "Water": {
        "partners": ["Palkia", "Kyogre", "Suicune", "Greninja", "Blastoise"],
        "supports": ["Irida", "Melony", "Origin Forme Palkia VSTAR"],
        "energy_accel": ["Capacious Bucket", "Energy Retrieval"],
        "strategy": "Control the board with Water-type synergies",
    },
    "Lightning": {
        "partners": ["Pikachu", "Raikou", "Zeraora", "Miraidon", "Regieleki"],
        "supports": ["Electric Generator", "Flaaffy"],
        "energy_accel": ["Electric Generator", "Flaaffy (Dynamotor)"],
        "strategy": "Fast energy acceleration with Lightning attackers",
    },
    "Psychic": {
        "partners": ["Gardevoir", "Mewtwo", "Mew", "Alakazam", "Espeon"],
        "supports": ["Fog Crystal", "Mysterious Treasure"],
        "energy_accel": ["Gardevoir (Psychic Embrace)", "Shadow Rider Calyrex"],
        "strategy": "Psychic energy manipulation and powerful attacks",
    },
    "Fighting": {
        "partners": ["Lucario", "Machamp", "Primeape", "Terrakion", "Buzzwole"],
        "supports": ["Korrina", "Bruno", "Martial Arts Dojo"],
        "energy_accel": ["Stonjourner", "Carbink"],
        "strategy": "Hit hard with Fighting-type damage bonuses",
    },
    "Darkness": {
        "partners": ["Darkrai", "Zoroark", "Umbreon", "Weavile", "Hydreigon"],
        "supports": ["Dark Patch", "Galarian Moltres"],
        "energy_accel": ["Dark Patch", "Galarian Moltres V"],
        "strategy": "Dark energy acceleration and control",
    },
    "Metal": {
        "partners": ["Dialga", "Metagross", "Aegislash", "Copperajah", "Archaludon"],
        "supports": ["Metal Saucer", "Bronzong"],
        "energy_accel": ["Metal Saucer", "Bronzong (Metal Links)"],
        "strategy": "Tanky Metal Pokemon with energy recovery",
    },
    "Dragon": {
        "partners": ["Rayquaza", "Dragonite", "Garchomp", "Salamence", "Regidrago"],
        "supports": ["Lance", "Dragon's Wish"],
        "energy_accel": ["Double Dragon Energy", "Regidrago VSTAR"],
        "strategy": "High damage Dragon attackers with multi-type energy",
    },
    "Grass": {
        "partners": ["Sceptile", "Venusaur", "Leafeon", "Decidueye", "Tsareena"],
        "supports": ["Gardenia's Vigor", "Cheryl"],
        "energy_accel": ["Leafeon VSTAR", "Gogoat"],
        "strategy": "Healing and energy efficient Grass attackers",
    },
    "Colorless": {
        "partners": ["Lugia", "Archeops", "Pidgeot", "Slaking", "Regigigas"],
        "supports": ["Double Turbo Energy", "Powerful Colorless Energy"],
        "energy_accel": ["Archeops (Primal Turbo)", "Double Turbo Energy"],
        "strategy": "Flexible attackers that work with any energy type",
    },
}


def find_pokemon_cards(pokemon_name: str) -> list[PokemonInfo]:
    """Search for Pokemon cards by name and return detailed info."""
    results = search_pokemon_by_name(pokemon_name)
    pokemon_list = []

    for card in results:
        # Handle both TCGdex and Pokemon TCG API formats
        name = card.get("name", "")

        # Skip if not a Pokemon
        supertype = card.get("supertype", card.get("category", "")).lower()
        if supertype and supertype not in ["pokemon", "pokémon", ""]:
            continue

        # Check for special card types
        subtypes = card.get("subtypes", [])
        if isinstance(subtypes, str):
            subtypes = [subtypes]

        is_ex = "ex" in name.lower() or "EX" in name or "ex" in subtypes
        is_v = "V" in name and "VSTAR" not in name and "VMAX" not in name
        is_vstar = "VSTAR" in name or "VSTAR" in subtypes
        is_vmax = "VMAX" in name or "VMAX" in subtypes

        # Get types
        types = card.get("types", [])
        if isinstance(types, str):
            types = [types]

        # Parse HP
        hp_str = card.get("hp", "")
        hp = None
        if hp_str:
            try:
                hp = int(hp_str)
            except (ValueError, TypeError):
                pass

        pokemon_info = PokemonInfo(
            name=name,
            set_name=card.get("set", card.get("set_name", "")),
            set_code=card.get("set_code", card.get("localId", "").split("-")[0] if "-" in str(card.get("localId", "")) else "").upper(),
            number=str(card.get("number", card.get("localId", ""))),
            regulation_mark=card.get("regulationMark", card.get("regulation_mark", "")),
            types=types,
            hp=hp,
            subtypes=subtypes if isinstance(subtypes, list) else [subtypes] if subtypes else [],
            is_ex=is_ex,
            is_v=is_v,
            is_vstar=is_vstar,
            is_vmax=is_vmax,
            attacks=card.get("attacks", []),
            abilities=card.get("abilities", []),
        )
        pokemon_list.append(pokemon_info)

    return pokemon_list


def get_pokemon_collections(pokemon_name: str) -> list[dict]:
    """Get all collections/sets where a Pokemon appears."""
    pokemon_cards = find_pokemon_cards(pokemon_name)

    collections = {}
    for card in pokemon_cards:
        key = card.set_code or card.set_name
        if key and key not in collections:
            collections[key] = {
                "set_code": card.set_code,
                "set_name": card.set_name,
                "cards": [],
                "regulation_mark": card.regulation_mark,
            }
        if key:
            collections[key]["cards"].append({
                "name": card.name,
                "number": card.number,
                "hp": card.hp,
                "is_ex": card.is_ex,
                "is_v": card.is_v,
                "is_vstar": card.is_vstar,
                "is_vmax": card.is_vmax,
                "types": card.types,
            })

    return list(collections.values())


def suggest_deck_for_pokemon(pokemon_name: str) -> list[DeckSuggestion]:
    """Suggest the best deck archetype for a given Pokemon."""
    pokemon_cards = find_pokemon_cards(pokemon_name)

    if not pokemon_cards:
        return []

    suggestions = []

    # Group cards by variant (ex, V, VSTAR, regular)
    best_cards = []
    for card in pokemon_cards:
        # Prioritize ex/V/VSTAR cards as main attackers
        if card.is_ex or card.is_v or card.is_vstar or card.is_vmax:
            best_cards.append(card)

    # If no special cards, use regular versions
    if not best_cards:
        best_cards = pokemon_cards[:3]  # Limit to 3 variants

    # Remove duplicates by name
    seen_names = set()
    unique_cards = []
    for card in best_cards:
        if card.name not in seen_names:
            seen_names.add(card.name)
            unique_cards.append(card)

    for card in unique_cards[:3]:  # Limit suggestions
        suggestion = create_deck_suggestion(card)
        if suggestion:
            suggestions.append(suggestion)

    return suggestions


def create_deck_suggestion(pokemon: PokemonInfo) -> Optional[DeckSuggestion]:
    """Create a deck suggestion based on Pokemon characteristics."""
    # Determine primary type
    primary_type = pokemon.types[0] if pokemon.types else "Colorless"

    # Get archetype info
    archetype = DECK_ARCHETYPES.get(primary_type, DECK_ARCHETYPES["Colorless"])

    # Determine difficulty based on card type
    if pokemon.is_vstar or pokemon.is_vmax:
        difficulty = "Intermediate"
    elif pokemon.is_ex or pokemon.is_v:
        difficulty = "Beginner"
    else:
        difficulty = "Advanced"  # Stage 2 evolutions are harder to play

    # Build key cards list
    key_cards = [
        f"4 {pokemon.name}",
    ]

    # Add evolution line if applicable
    base_name = pokemon.name.replace(" ex", "").replace(" EX", "").replace(" V", "").replace(" VSTAR", "").replace(" VMAX", "")
    if "Stage" in str(pokemon.subtypes) or pokemon.is_ex:
        key_cards.append(f"4 {base_name} (Basic)")
        if "Stage 2" in str(pokemon.subtypes):
            key_cards.append(f"3 {base_name} (Stage 1)")
            key_cards.append("4 Rare Candy")

    # Add support cards
    key_cards.extend([
        "4 Ultra Ball",
        "4 Nest Ball",
        "4 Iono",
        "4 Arven",
        "2 Boss's Orders",
    ])

    # Add type-specific support
    for support in archetype.get("supports", [])[:2]:
        if support not in [c.split(" ", 1)[1] if " " in c else c for c in key_cards]:
            key_cards.append(f"2-4 {support}")

    # Add energy acceleration
    for accel in archetype.get("energy_accel", [])[:1]:
        key_cards.append(f"2-4 {accel}")

    # Energy types
    energy_types = [f"Basic {primary_type} Energy"]
    if primary_type == "Colorless":
        energy_types = ["Double Turbo Energy", "Any Basic Energy"]
    elif primary_type == "Dragon":
        energy_types = ["Basic Fire Energy", "Basic Water Energy", "Double Dragon Energy"]

    # Strengths based on type
    type_strengths = {
        "Fire": ["Strong against Grass/Metal", "Good energy acceleration options"],
        "Water": ["Strong against Fire", "Good control options"],
        "Lightning": ["Strong against Water", "Fast setup with Electric Generator"],
        "Psychic": ["Strong against Fighting", "Powerful abilities"],
        "Fighting": ["Strong against Lightning/Dark/Colorless", "High base damage"],
        "Darkness": ["Strong against Psychic", "Good disruption options"],
        "Metal": ["Strong against Fairy", "High HP and tanky"],
        "Dragon": ["High damage output", "Versatile energy requirements"],
        "Grass": ["Strong against Water", "Healing capabilities"],
        "Colorless": ["Flexible energy requirements", "Works with any deck"],
    }

    type_weaknesses = {
        "Fire": ["Weak to Water", "Energy intensive"],
        "Water": ["Weak to Lightning", "Setup can be slow"],
        "Lightning": ["Weak to Fighting", "Low HP Pokemon"],
        "Psychic": ["Weak to Darkness", "Complex combos"],
        "Fighting": ["Weak to Psychic", "Limited search options"],
        "Darkness": ["Weak to Fighting", "Relies on discard pile"],
        "Metal": ["Weak to Fire", "Slow setup"],
        "Dragon": ["Weak to Fairy", "Complex energy requirements"],
        "Grass": ["Weak to Fire", "Lower damage output"],
        "Colorless": ["No type advantages", "Generic strategy"],
    }

    strengths = type_strengths.get(primary_type, ["Versatile attacker"])
    weaknesses = type_weaknesses.get(primary_type, ["Standard weaknesses"])

    # Add HP-based strength/weakness
    if pokemon.hp and pokemon.hp >= 300:
        strengths.append(f"High HP ({pokemon.hp})")
    elif pokemon.hp and pokemon.hp < 200:
        weaknesses.append(f"Low HP ({pokemon.hp})")

    # Card-specific notes
    if pokemon.is_ex:
        weaknesses.append("Gives 2 prize cards when KO'd")
    elif pokemon.is_vstar:
        strengths.append("Powerful VSTAR Power (once per game)")
        weaknesses.append("Gives 2 prize cards when KO'd")
    elif pokemon.is_vmax:
        strengths.append("Very high HP")
        weaknesses.append("Gives 3 prize cards when KO'd")

    # Build archetype name
    archetype_name = f"{pokemon.name} Deck"
    if archetype.get("partners"):
        partner = archetype["partners"][0]
        archetype_name = f"{pokemon.name} / {partner}"

    return DeckSuggestion(
        archetype_name=archetype_name,
        description=f"A {primary_type}-type deck featuring {pokemon.name} as the main attacker",
        pokemon=pokemon,
        strategy=archetype.get("strategy", "Standard beatdown strategy"),
        key_cards=key_cards,
        energy_types=energy_types,
        strengths=strengths,
        weaknesses=weaknesses,
        difficulty=difficulty,
    )


def get_legal_status(regulation_mark: str) -> str:
    """Get the legality status of a card based on regulation mark."""
    if not regulation_mark:
        return "Unknown"

    if regulation_mark in ["A", "B", "C", "D", "E", "F"]:
        return "Illegal (Rotated)"
    elif regulation_mark == "G":
        return "Rotating March 2026"
    elif regulation_mark in ["H", "I", "J", "K"]:
        return "Legal (Standard)"
    else:
        return "Unknown"
