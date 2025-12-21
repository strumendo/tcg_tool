"""Parser for PTCGO deck format."""
import re
from models import Card, Deck, CardType


# Set code mappings (Portuguese/Brazilian to standard)
SET_CODE_MAP = {
    # Scarlet & Violet era
    "PAF": "sv4pt5",  # Paldean Fates
    "OBF": "sv3",     # Obsidian Flames
    "PAL": "sv2",     # Paldea Evolved
    "SVI": "sv1",     # Scarlet & Violet Base
    "MEW": "sv3pt5",  # 151
    "PAR": "sv4",     # Paradox Rift
    "TEF": "sv5",     # Temporal Forces
    "TWM": "sv6",     # Twilight Masquerade
    "SFA": "sv6pt5",  # Shrouded Fable
    "SCR": "sv7",     # Stellar Crown
    "SSP": "sv8",     # Surging Sparks
    "PRE": "sv8pt5",  # Prismatic Evolutions
    "JTG": "sv9",     # Journey Together
    "ASC": "sv9pt5",  # Ascended Heroes
    # Sword & Shield era (mostly rotating)
    "SSH": "swsh1",
    "RCL": "swsh2",
    "DAA": "swsh3",
    "VIV": "swsh4",
    "BST": "swsh5",
    "CRE": "swsh6",
    "EVS": "swsh7",
    "FST": "swsh8",
    "BRS": "swsh9",
    "ASR": "swsh10",
    "LOR": "swsh11",
    "SIT": "swsh12",
    "CRZ": "swsh12pt5",
}

# Regulation marks by set (approximate)
REGULATION_MARKS = {
    # G regulation (rotating March 2026)
    "sv1": "G", "sv2": "G", "sv3": "G", "sv3pt5": "G",
    "sv4": "G", "sv4pt5": "G",
    "SVI": "G", "PAL": "G", "OBF": "G", "MEW": "G",
    "PAR": "G", "PAF": "G",
    # H regulation (safe)
    "sv5": "H", "sv6": "H", "sv6pt5": "H", "sv7": "H", "sv8": "H",
    "TEF": "H", "TWM": "H", "SFA": "H", "SCR": "H", "SSP": "H",
    # I regulation (new sets)
    "sv8pt5": "I", "sv9": "I", "sv9pt5": "I",
    "PRE": "I", "JTG": "I", "ASC": "I",
    # Basic Energy (always legal)
    "SVE": "H", "sve": "H",
    # Sword & Shield (already rotating or rotated)
    "swsh1": "D", "swsh2": "D", "swsh3": "D", "swsh4": "D",
    "swsh5": "E", "swsh6": "E", "swsh7": "E", "swsh8": "E",
    "swsh9": "F", "swsh10": "F", "swsh11": "F", "swsh12": "F", "swsh12pt5": "F",
}

# Patterns for parsing deck lines
PATTERNS = [
    # PTCGO format: "4 Charizard ex SVI 125"
    re.compile(r'^(\d+)\s+(.+?)\s+([A-Z]{2,4})\s+(\d+)$'),
    # With star: "* 4 Charizard ex SVI 125"
    re.compile(r'^\*?\s*(\d+)\s+(.+?)\s+([A-Z]{2,4})\s+(\d+)$'),
    # Energy format: "4 Basic Fire Energy SVE 2"
    re.compile(r'^(\d+)\s+(Basic\s+\w+\s+Energy)\s+([A-Z]{2,4})\s+(\d+)$'),
]


def normalize_set_code(code: str) -> str:
    """Normalize set code to standard format."""
    code = code.upper().strip()
    return SET_CODE_MAP.get(code, code)


def get_regulation_mark(set_code: str) -> str:
    """Get regulation mark for a set."""
    normalized = normalize_set_code(set_code)
    return REGULATION_MARKS.get(set_code, REGULATION_MARKS.get(normalized, "?"))


def detect_card_type(name: str) -> CardType:
    """Detect card type from name."""
    name_lower = name.lower()

    if "energy" in name_lower:
        return CardType.ENERGY

    trainer_keywords = [
        "professor", "boss", "iono", "arven", "penny", "jacq", "tulip",
        "nest ball", "ultra ball", "level ball", "poke ball", "master ball",
        "rare candy", "switch", "escape rope", "battle vip pass",
        "forest seal stone", "counter catcher", "super rod", "night stretcher",
        "pokemon catcher", "gust", "tool", "cape", "choice", "potion",
        "trekking shoes", "earthen vessel", "energy retrieval", "rescue board",
        "technical machine", "stadium", "temple", "beach", "area zero",
        "artazon", "mesagoza", "academy", "path", "training court",
        "collapsed", "chaotic", "lost city", "jubilife", "capacious bucket"
    ]

    for keyword in trainer_keywords:
        if keyword in name_lower:
            return CardType.TRAINER

    return CardType.POKEMON


def detect_trainer_subtype(name: str) -> str:
    """Detect trainer subtype from name."""
    name_lower = name.lower()

    supporters = [
        "professor", "boss", "iono", "arven", "penny", "jacq", "tulip",
        "cynthia", "marnie", "giovanni", "colress", "roxanne", "irida",
        "melony", "raihan", "worker", "leon", "hop", "klara", "crispin",
        "lacey", "kieran", "briar", "lana's fishing rod", "ciphermaniac"
    ]

    stadiums = [
        "stadium", "temple", "beach", "area zero", "artazon", "mesagoza",
        "academy", "path", "training court", "collapsed", "chaotic",
        "lost city", "jubilife", "magma basin", "crystal cave"
    ]

    tools = [
        "seal stone", "cape", "choice belt", "choice band", "leftovers",
        "rescue board", "bravery charm", "defiance band", "hero's cape",
        "survival brace", "vengeful punch", "vitality band", "exp. share"
    ]

    for keyword in supporters:
        if keyword in name_lower:
            return "supporter"

    for keyword in stadiums:
        if keyword in name_lower:
            return "stadium"

    for keyword in tools:
        if keyword in name_lower:
            return "tool"

    return "item"


def parse_line(line: str) -> Card | None:
    """Parse a single deck line."""
    line = line.strip()
    if not line or line.startswith("#") or line.startswith("//"):
        return None

    # Skip section headers
    if line.lower() in ["pokemon:", "pokémon:", "trainer:", "energy:",
                        "pokemon", "pokémon", "trainer", "energy"]:
        return None

    for pattern in PATTERNS:
        match = pattern.match(line)
        if match:
            quantity = int(match.group(1))
            name = match.group(2).strip()
            set_code = match.group(3).upper()
            set_number = match.group(4)

            card_type = detect_card_type(name)
            subtype = None
            if card_type == CardType.TRAINER:
                subtype = detect_trainer_subtype(name)

            return Card(
                name=name,
                card_type=card_type,
                set_code=set_code,
                set_number=set_number,
                quantity=quantity,
                regulation_mark=get_regulation_mark(set_code),
                subtype=subtype
            )

    return None


def parse_deck(deck_text: str) -> Deck:
    """Parse full deck from PTCGO format text."""
    deck = Deck()

    for line in deck_text.strip().split("\n"):
        card = parse_line(line)
        if card:
            deck.cards.append(card)

    return deck


def parse_deck_file(filepath: str) -> Deck:
    """Parse deck from file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return parse_deck(f.read())
