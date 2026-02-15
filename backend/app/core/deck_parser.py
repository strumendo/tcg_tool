"""
Parser for PTCGO / Pokemon TCG Live deck export format.

Reads plain-text deck lists and produces ``ParsedDeck`` / ``ParsedCard``
dataclass instances.  All set-code and regulation-mark resolution is
delegated to ``core.set_codes``.

No framework dependencies -- pure Python only.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from app.core.set_codes import get_regulation_mark, normalize_set_code


# ---------------------------------------------------------------------------
# Enums (local, framework-free copies)
# ---------------------------------------------------------------------------

class CardType(str, Enum):
    POKEMON = "pokemon"
    TRAINER = "trainer"
    ENERGY = "energy"


class TrainerSubtype(str, Enum):
    ITEM = "item"
    SUPPORTER = "supporter"
    STADIUM = "stadium"
    TOOL = "tool"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class ParsedCard:
    """A single card entry parsed from a deck list."""
    name: str
    card_type: CardType
    set_code: str
    set_number: str
    quantity: int = 1
    regulation_mark: str = "?"
    subtype: Optional[str] = None

    # convenience properties -------------------------------------------------

    @property
    def is_rotating(self) -> bool:
        """Card rotates in March 2026 (regulation mark G)."""
        return self.regulation_mark == "G"

    @property
    def is_already_rotated(self) -> bool:
        """Card has already rotated (regulation mark F or earlier)."""
        if not self.regulation_mark:
            return False
        return self.regulation_mark in ("A", "B", "C", "D", "E", "F")

    @property
    def is_safe(self) -> bool:
        """Card is safe post-rotation (H, I or later)."""
        if not self.regulation_mark:
            if "basic" in self.name.lower() and "energy" in self.name.lower():
                return True
            return False
        return self.regulation_mark in ("H", "I", "J", "K")

    @property
    def full_id(self) -> str:
        return f"{self.set_code} {self.set_number}"

    def __str__(self) -> str:
        return f"{self.quantity} {self.name} {self.set_code} {self.set_number}"


@dataclass
class ParsedDeck:
    """A collection of parsed cards forming a deck."""
    cards: list[ParsedCard] = field(default_factory=list)
    name: str = "My Deck"

    # aggregate properties ---------------------------------------------------

    @property
    def total_cards(self) -> int:
        return sum(c.quantity for c in self.cards)

    @property
    def pokemon_count(self) -> int:
        return sum(c.quantity for c in self.cards if c.card_type == CardType.POKEMON)

    @property
    def trainer_count(self) -> int:
        return sum(c.quantity for c in self.cards if c.card_type == CardType.TRAINER)

    @property
    def energy_count(self) -> int:
        return sum(c.quantity for c in self.cards if c.card_type == CardType.ENERGY)

    @property
    def rotating_cards(self) -> list[ParsedCard]:
        return [c for c in self.cards if c.is_rotating]

    @property
    def safe_cards(self) -> list[ParsedCard]:
        return [c for c in self.cards if not c.is_rotating]

    @property
    def rotation_impact(self) -> float:
        if self.total_cards == 0:
            return 0.0
        rotating = sum(c.quantity for c in self.rotating_cards)
        return (rotating / self.total_cards) * 100


# ---------------------------------------------------------------------------
# Regex patterns for PTCGO format lines
# ---------------------------------------------------------------------------

PATTERNS: list[re.Pattern[str]] = [
    # Standard PTCGO format: "4 Charizard ex SVI 125"
    re.compile(r"^(\d+)\s+(.+?)\s+([A-Za-z0-9]{2,4})\s+(\d+)$"),
    # With leading star: "* 4 Charizard ex SVI 125"
    re.compile(r"^\*?\s*(\d+)\s+(.+?)\s+([A-Za-z0-9]{2,4})\s+(\d+)$"),
    # Explicit energy format: "4 Basic Fire Energy SVE 2"
    re.compile(r"^(\d+)\s+(Basic\s+\w+\s+Energy)\s+([A-Za-z0-9]{2,4})\s+(\d+)$"),
]


# ---------------------------------------------------------------------------
# Card-type / subtype detection
# ---------------------------------------------------------------------------

_TRAINER_KEYWORDS: list[str] = [
    # Supporters
    "professor", "boss", "iono", "arven", "penny", "jacq", "tulip",
    "cynthia", "marnie", "giovanni", "colress", "roxanne", "irida",
    "melony", "raihan", "worker", "leon", "hop", "klara", "crispin",
    "lacey", "kieran", "briar", "lana's fishing rod", "ciphermaniac",
    "hilda", "brock", "anthea", "concordia", "lillie's determination",
    "dawn", "team rocket's petrel",
    # Items / balls
    "nest ball", "ultra ball", "level ball", "poke ball", "master ball",
    "rare candy", "switch", "escape rope", "battle vip pass",
    "forest seal stone", "counter catcher", "super rod", "night stretcher",
    "pokemon catcher", "gust", "tool", "cape", "choice", "potion",
    "trekking shoes", "earthen vessel", "energy retrieval", "rescue board",
    "technical machine", "buddy-buddy poffin", "pokegear", "pal pad",
    "prime catcher", "superior energy retrieval", "secret box",
    "precious trolley", "bravery charm", "future booster",
    "poke pad",
    # Stadiums
    "stadium", "temple", "beach", "area zero", "artazon", "mesagoza",
    "academy", "path", "training court", "collapsed", "chaotic",
    "lost city", "jubilife", "capacious bucket",
    "jamming tower", "magma basin", "crystal cave",
    "spikemuth gym", "mystery garden", "nighttime mine",
]

_SUPPORTER_KEYWORDS: list[str] = [
    "professor", "boss", "iono", "arven", "penny", "jacq", "tulip",
    "cynthia", "marnie", "giovanni", "colress", "roxanne", "irida",
    "melony", "raihan", "worker", "leon", "hop", "klara", "crispin",
    "lacey", "kieran", "briar", "lana's fishing rod", "ciphermaniac",
    "hilda", "brock", "anthea", "concordia", "lillie's determination",
    "dawn", "team rocket's petrel",
    "professor sada", "professor turo",
]

_STADIUM_KEYWORDS: list[str] = [
    "stadium", "temple", "beach", "area zero", "artazon", "mesagoza",
    "academy", "path", "training court", "collapsed", "chaotic",
    "lost city", "jubilife", "magma basin", "crystal cave",
    "jamming tower", "spikemuth gym", "mystery garden", "nighttime mine",
]

_TOOL_KEYWORDS: list[str] = [
    "seal stone", "cape", "choice belt", "choice band", "leftovers",
    "rescue board", "bravery charm", "defiance band", "hero's cape",
    "survival brace", "vengeful punch", "vitality band", "exp. share",
    "future booster energy capsule",
]


def detect_card_type(name: str) -> CardType:
    """Detect whether *name* is a Pokemon, Trainer, or Energy card."""
    lower = name.lower()

    if "energy" in lower:
        return CardType.ENERGY

    for keyword in _TRAINER_KEYWORDS:
        if keyword in lower:
            return CardType.TRAINER

    return CardType.POKEMON


def detect_trainer_subtype(name: str) -> str:
    """Return the trainer subtype (supporter / stadium / tool / item)."""
    lower = name.lower()

    for keyword in _SUPPORTER_KEYWORDS:
        if keyword in lower:
            return TrainerSubtype.SUPPORTER.value

    for keyword in _STADIUM_KEYWORDS:
        if keyword in lower:
            return TrainerSubtype.STADIUM.value

    for keyword in _TOOL_KEYWORDS:
        if keyword in lower:
            return TrainerSubtype.TOOL.value

    return TrainerSubtype.ITEM.value


# ---------------------------------------------------------------------------
# Parsing functions
# ---------------------------------------------------------------------------

def parse_line(line: str) -> ParsedCard | None:
    """Parse a single PTCGO-format deck line into a ``ParsedCard``.

    Returns ``None`` for blank lines, comments, or section headers.
    """
    line = line.strip()
    if not line or line.startswith("#") or line.startswith("//"):
        return None

    # Skip section headers
    if line.lower().rstrip(":") in (
        "pokemon", "pokémon", "trainer", "energy",
    ):
        return None

    for pattern in PATTERNS:
        match = pattern.match(line)
        if match:
            quantity = int(match.group(1))
            name = match.group(2).strip()
            set_code = match.group(3).upper()
            set_number = match.group(4)

            card_type = detect_card_type(name)
            subtype: str | None = None
            if card_type == CardType.TRAINER:
                subtype = detect_trainer_subtype(name)

            return ParsedCard(
                name=name,
                card_type=card_type,
                set_code=set_code,
                set_number=set_number,
                quantity=quantity,
                regulation_mark=get_regulation_mark(set_code),
                subtype=subtype,
            )

    return None


def parse_deck(deck_text: str) -> ParsedDeck:
    """Parse a full PTCGO-format deck list string into a ``ParsedDeck``."""
    deck = ParsedDeck()

    for line in deck_text.strip().split("\n"):
        card = parse_line(line)
        if card is not None:
            deck.cards.append(card)

    return deck


def parse_deck_file(filepath: str) -> ParsedDeck:
    """Read a file at *filepath* and parse it as a PTCGO deck list."""
    with open(filepath, "r", encoding="utf-8") as fh:
        return parse_deck(fh.read())
