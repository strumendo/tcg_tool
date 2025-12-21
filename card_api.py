"""Pokemon TCG API integration."""
import httpx
import json
from typing import Optional
from models import Card, CardType, CardFunction


# TCGdex API base URL
TCGDEX_BASE = "https://api.tcgdex.net/v2/en"

# Pokemon TCG API base URL (fallback)
POKEMONTCG_BASE = "https://api.pokemontcg.io/v2"


def fetch_card_tcgdex(set_code: str, number: str) -> Optional[dict]:
    """Fetch card from TCGdex API."""
    try:
        url = f"{TCGDEX_BASE}/cards/{set_code.lower()}-{number}"
        with httpx.Client(timeout=30) as client:
            response = client.get(url)
            if response.status_code == 200:
                return response.json()
    except Exception:
        pass
    return None


def fetch_set_cards_tcgdex(set_code: str) -> list[dict]:
    """Fetch all cards from a set via TCGdex."""
    try:
        url = f"{TCGDEX_BASE}/sets/{set_code.lower()}"
        with httpx.Client(timeout=60) as client:
            response = client.get(url)
            if response.status_code == 200:
                data = response.json()
                cards = data.get("cards", [])
                # Fetch full details for each card
                full_cards = []
                for card in cards:
                    card_id = card.get("id", "")
                    detail = fetch_card_tcgdex_by_id(card_id)
                    if detail:
                        full_cards.append(detail)
                return full_cards
    except Exception:
        pass
    return []


def fetch_card_tcgdex_by_id(card_id: str) -> Optional[dict]:
    """Fetch card by ID from TCGdex."""
    try:
        url = f"{TCGDEX_BASE}/cards/{card_id}"
        with httpx.Client(timeout=30) as client:
            response = client.get(url)
            if response.status_code == 200:
                return response.json()
    except Exception:
        pass
    return None


def fetch_set_cards_pokemontcg(set_code: str) -> list[dict]:
    """Fetch all cards from a set via Pokemon TCG API."""
    try:
        url = f"{POKEMONTCG_BASE}/cards"
        params = {"q": f"set.id:{set_code.lower()}", "pageSize": 250}
        with httpx.Client(timeout=60) as client:
            response = client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
    except Exception:
        pass
    return []


def parse_tcgdex_card(data: dict, set_code: str) -> Optional[Card]:
    """Parse TCGdex response to Card model."""
    try:
        category = data.get("category", "").lower()

        if category == "pokemon":
            card_type = CardType.POKEMON
        elif category == "trainer":
            card_type = CardType.TRAINER
        elif category == "energy":
            card_type = CardType.ENERGY
        else:
            card_type = CardType.POKEMON  # default

        # Get attacks as string
        attacks = data.get("attacks", [])
        attacks_str = json.dumps(attacks) if attacks else None

        # Get abilities as string
        abilities = data.get("abilities", [])
        abilities_str = json.dumps(abilities) if abilities else None

        return Card(
            name=data.get("name", "Unknown"),
            card_type=card_type,
            set_code=set_code.upper(),
            set_number=str(data.get("localId", "")),
            regulation_mark=data.get("regulationMark", ""),
            subtype=data.get("stage", data.get("trainerType", "")),
            hp=data.get("hp"),
            energy_type=data.get("types", [""])[0] if data.get("types") else None,
            abilities=abilities_str,
            attacks=attacks_str,
            functions=detect_functions(data)
        )
    except Exception:
        return None


def parse_pokemontcg_card(data: dict) -> Optional[Card]:
    """Parse Pokemon TCG API response to Card model."""
    try:
        supertype = data.get("supertype", "").lower()

        if supertype == "pokémon" or supertype == "pokemon":
            card_type = CardType.POKEMON
        elif supertype == "trainer":
            card_type = CardType.TRAINER
        elif supertype == "energy":
            card_type = CardType.ENERGY
        else:
            card_type = CardType.POKEMON

        set_data = data.get("set", {})

        attacks = data.get("attacks", [])
        attacks_str = json.dumps(attacks) if attacks else None

        abilities = data.get("abilities", [])
        abilities_str = json.dumps(abilities) if abilities else None

        return Card(
            name=data.get("name", "Unknown"),
            card_type=card_type,
            set_code=set_data.get("id", "").upper(),
            set_number=data.get("number", ""),
            regulation_mark=data.get("regulationMark", ""),
            subtype=data.get("subtypes", [""])[0] if data.get("subtypes") else None,
            hp=int(data.get("hp", 0)) if data.get("hp") else None,
            energy_type=data.get("types", [""])[0] if data.get("types") else None,
            abilities=abilities_str,
            attacks=attacks_str,
            functions=detect_functions_from_text(data)
        )
    except Exception:
        return None


def detect_functions(data: dict) -> list[CardFunction]:
    """Detect card functions from TCGdex data."""
    functions = []

    # Check abilities
    for ability in data.get("abilities", []):
        effect = ability.get("effect", "").lower()
        functions.extend(analyze_effect_text(effect))

    # Check attacks
    for attack in data.get("attacks", []):
        effect = attack.get("effect", "").lower()
        functions.extend(analyze_effect_text(effect))

    # Check trainer effect
    effect = data.get("effect", "")
    if effect:
        functions.extend(analyze_effect_text(effect.lower()))

    return list(set(functions))


def detect_functions_from_text(data: dict) -> list[CardFunction]:
    """Detect functions from Pokemon TCG API data."""
    functions = []

    # Check abilities
    for ability in data.get("abilities", []):
        text = ability.get("text", "").lower()
        functions.extend(analyze_effect_text(text))

    # Check attacks
    for attack in data.get("attacks", []):
        text = attack.get("text", "").lower()
        functions.extend(analyze_effect_text(text))

    # Check rules
    for rule in data.get("rules", []):
        functions.extend(analyze_effect_text(rule.lower()))

    return list(set(functions))


def analyze_effect_text(text: str) -> list[CardFunction]:
    """Analyze effect text to determine functions."""
    functions = []

    # Draw
    if any(kw in text for kw in ["draw", "draws", "draw cards"]):
        functions.append(CardFunction.DRAW)

    # Search
    if any(kw in text for kw in ["search", "look at", "find"]):
        functions.append(CardFunction.SEARCH)

    # Recovery
    if any(kw in text for kw in ["discard pile", "from your discard", "shuffle back", "put back"]):
        functions.append(CardFunction.RECOVERY)

    # Switching
    if any(kw in text for kw in ["switch", "retreat", "to your bench", "from your bench"]):
        functions.append(CardFunction.SWITCHING)

    # Energy acceleration
    if any(kw in text for kw in ["attach", "energy from", "energy to"]):
        functions.append(CardFunction.ENERGY_ACCEL)

    # Damage
    if any(kw in text for kw in ["damage", "knock out", "ko"]):
        functions.append(CardFunction.DAMAGE)

    # Healing
    if any(kw in text for kw in ["heal", "remove damage"]):
        functions.append(CardFunction.HEALING)

    # Disruption
    if any(kw in text for kw in ["opponent's hand", "discard from", "shuffle opponent"]):
        functions.append(CardFunction.DISRUPTION)

    # Removal
    if any(kw in text for kw in ["discard", "remove", "put in lost zone"]):
        functions.append(CardFunction.REMOVAL)

    # Protection
    if any(kw in text for kw in ["prevent", "can't be", "protected", "immune"]):
        functions.append(CardFunction.PROTECTION)

    # Setup
    if any(kw in text for kw in ["evolve", "put onto", "basic pokemon"]):
        functions.append(CardFunction.SETUP)

    return functions


def get_new_set_cards(set_code: str = "ASC") -> list[Card]:
    """Get cards from the new set (Ascended Heroes)."""
    cards = []

    # Try TCGdex first
    raw_cards = fetch_set_cards_tcgdex(set_code)

    if not raw_cards:
        # Fall back to Pokemon TCG API
        raw_cards = fetch_set_cards_pokemontcg(set_code)
        for data in raw_cards:
            card = parse_pokemontcg_card(data)
            if card:
                cards.append(card)
    else:
        for data in raw_cards:
            card = parse_tcgdex_card(data, set_code)
            if card:
                cards.append(card)

    return cards
