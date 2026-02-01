"""
Deck Import Service - Parse and validate decks from various sources.

Supports:
- PTCGO/TCG Live text format (copy/paste)
- .txt files with single or multiple decks
- Validation and error reporting
"""

import re
import sys
import os
from dataclasses import dataclass
from typing import Optional
from enum import Enum

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from .user_database import UserCard, UserDeck


# =============================================================================
# CONSTANTS
# =============================================================================

# Set code mappings (PTCGO codes to standard)
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
    "DRI": "sv10",    # Destined Rivals
    # Basic Energy
    "SVE": "sve",
}

# Regulation marks by set
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
    "sv8pt5": "I", "sv9": "I", "sv9pt5": "I", "sv10": "I",
    "PRE": "I", "JTG": "I", "ASC": "I", "DRI": "I",
    # Basic Energy (always legal)
    "SVE": "H", "sve": "H",
}

# Patterns for parsing deck lines
DECK_LINE_PATTERNS = [
    # PTCGO format: "4 Charizard ex SVI 125"
    re.compile(r'^(\d+)\s+(.+?)\s+([A-Z]{2,4})\s+(\d+)$'),
    # With star: "* 4 Charizard ex SVI 125"
    re.compile(r'^\*?\s*(\d+)\s+(.+?)\s+([A-Z]{2,4})\s+(\d+)$'),
    # Energy format: "4 Basic Fire Energy SVE 2"
    re.compile(r'^(\d+)\s+(Basic\s+\w+\s+Energy)\s+([A-Z]{2,4})\s+(\d+)$'),
]

# Keywords for detecting card types
TRAINER_KEYWORDS = [
    "professor", "boss", "iono", "arven", "penny", "jacq", "tulip",
    "nest ball", "ultra ball", "level ball", "poke ball", "master ball",
    "rare candy", "switch", "escape rope", "battle vip pass",
    "forest seal stone", "counter catcher", "super rod", "night stretcher",
    "pokemon catcher", "gust", "tool", "cape", "choice", "potion",
    "trekking shoes", "earthen vessel", "energy retrieval", "rescue board",
    "technical machine", "stadium", "temple", "beach", "area zero",
    "artazon", "mesagoza", "academy", "path", "training court",
    "collapsed", "chaotic", "lost city", "jubilife", "capacious bucket",
    "ciphermaniac", "lana", "crispin", "lacey", "kieran", "briar", "cynthia",
    "marnie", "giovanni", "colress", "roxanne", "irida", "melony", "raihan",
    "worker", "leon", "hop", "klara", "n", "research", "judge", "acerola",
    "crasher wake", "eri", "peonia", "pokegear", "hisuian heavy ball"
]

SUPPORTER_KEYWORDS = [
    "professor", "boss", "iono", "arven", "penny", "jacq", "tulip",
    "cynthia", "marnie", "giovanni", "colress", "roxanne", "irida",
    "melony", "raihan", "worker", "leon", "hop", "klara", "crispin",
    "lacey", "kieran", "briar", "lana", "ciphermaniac", "research",
    "judge", "n", "acerola", "crasher wake", "eri", "peonia"
]

STADIUM_KEYWORDS = [
    "stadium", "temple", "beach", "area zero", "artazon", "mesagoza",
    "academy", "path", "training court", "collapsed", "chaotic",
    "lost city", "jubilife", "magma basin", "crystal cave", "spikemuth"
]

TOOL_KEYWORDS = [
    "seal stone", "cape", "choice belt", "choice band", "leftovers",
    "rescue board", "bravery charm", "defiance band", "hero's cape",
    "survival brace", "vengeful punch", "vitality band", "exp. share",
    "technical machine", "heavy baton", "booster energy"
]


# =============================================================================
# VALIDATION RESULTS
# =============================================================================

class ValidationSeverity(str, Enum):
    """Severity of validation issues."""
    ERROR = "error"      # Cannot be used (e.g., illegal cards)
    WARNING = "warning"  # Can be used but has issues (e.g., incomplete)
    INFO = "info"        # Informational (e.g., rotating cards)


@dataclass
class ValidationIssue:
    """A validation issue found in a deck."""
    severity: ValidationSeverity
    message_en: str
    message_pt: str
    card_name: str = ""


@dataclass
class ImportResult:
    """Result of importing a deck."""
    success: bool
    deck: Optional[UserDeck]
    issues: list[ValidationIssue]
    raw_text: str = ""

    @property
    def has_errors(self) -> bool:
        return any(i.severity == ValidationSeverity.ERROR for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.severity == ValidationSeverity.WARNING for i in self.issues)


@dataclass
class MultiImportResult:
    """Result of importing multiple decks from a file."""
    total_found: int
    successful: int
    failed: int
    results: list[ImportResult]


# =============================================================================
# DECK IMPORT SERVICE
# =============================================================================

class DeckImportService:
    """Service for importing and validating decks."""

    def __init__(self):
        pass

    def import_from_text(self, text: str, deck_name: str = "Imported Deck") -> ImportResult:
        """
        Import a single deck from PTCGO format text.

        Args:
            text: The deck text in PTCGO format
            deck_name: Name to give the deck

        Returns:
            ImportResult with the deck and any validation issues
        """
        issues = []
        cards = []

        lines = text.strip().split('\n')
        line_number = 0

        for line in lines:
            line_number += 1
            line = line.strip()

            # Skip empty lines, comments, and section headers
            if not line or line.startswith('#') or line.startswith('//'):
                continue

            # Skip section headers (Pokemon: 20, Trainer: 32, Energy: 8, etc.)
            if re.match(r'^(pokemon|pokémon|trainer|energy):?\s*\d*$', line, re.IGNORECASE):
                continue

            # Try to parse the line
            card = self._parse_line(line)

            if card:
                cards.append(card)
            else:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message_en=f"Could not parse line {line_number}: {line[:50]}",
                    message_pt=f"Não foi possível processar linha {line_number}: {line[:50]}"
                ))

        # Create deck
        deck = UserDeck(
            name=deck_name,
            cards=cards,
            is_complete=sum(c.quantity for c in cards) == 60
        )

        # Validate
        validation_issues = self._validate_deck(deck)
        issues.extend(validation_issues)

        success = not any(i.severity == ValidationSeverity.ERROR for i in issues)

        return ImportResult(
            success=success,
            deck=deck if cards else None,
            issues=issues,
            raw_text=text
        )

    def import_from_file(self, file_path: str) -> MultiImportResult:
        """
        Import one or more decks from a .txt file.

        Args:
            file_path: Path to the .txt file

        Returns:
            MultiImportResult with all found decks
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return MultiImportResult(
                total_found=0,
                successful=0,
                failed=1,
                results=[ImportResult(
                    success=False,
                    deck=None,
                    issues=[ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        message_en=f"Could not read file: {str(e)}",
                        message_pt=f"Não foi possível ler arquivo: {str(e)}"
                    )]
                )]
            )

        # Split into multiple decks if present
        deck_texts = self._split_multiple_decks(content)
        results = []

        for i, deck_text in enumerate(deck_texts):
            deck_name = f"Deck {i + 1}" if len(deck_texts) > 1 else "Imported Deck"
            result = self.import_from_text(deck_text, deck_name)
            results.append(result)

        successful = sum(1 for r in results if r.success and r.deck)
        failed = len(results) - successful

        return MultiImportResult(
            total_found=len(deck_texts),
            successful=successful,
            failed=failed,
            results=results
        )

    def _split_multiple_decks(self, content: str) -> list[str]:
        """
        Split file content into multiple deck texts.
        Decks are separated by double blank lines or deck markers.
        """
        # Common deck separators
        separators = [
            r'\n\s*\n\s*\n',           # Triple newline
            r'\n---+\n',               # Dashes
            r'\n===+\n',               # Equals
            r'\nDeck\s*\d*:?\s*\n',    # "Deck 1:" markers
        ]

        # Try to split
        for sep in separators:
            parts = re.split(sep, content, flags=re.IGNORECASE)
            if len(parts) > 1:
                # Filter out empty parts
                return [p.strip() for p in parts if p.strip() and self._has_deck_content(p)]

        # No separators found - treat as single deck
        return [content]

    def _has_deck_content(self, text: str) -> bool:
        """Check if text contains deck content (not just headers/comments)."""
        for line in text.split('\n'):
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('//'):
                continue
            # Skip section headers (Pokemon: 20, Trainer: 32, Energy: 8, etc.)
            if re.match(r'^(pokemon|pokémon|trainer|energy):?\s*\d*$', line, re.IGNORECASE):
                continue
            # Check if line matches a card pattern
            for pattern in DECK_LINE_PATTERNS:
                if pattern.match(line):
                    return True
        return False

    def _parse_line(self, line: str) -> Optional[UserCard]:
        """Parse a single deck line into a UserCard."""
        line = line.strip()

        for pattern in DECK_LINE_PATTERNS:
            match = pattern.match(line)
            if match:
                quantity = int(match.group(1))
                name = match.group(2).strip()
                set_code = match.group(3).upper()
                set_number = match.group(4)

                card_type = self._detect_card_type(name)
                subtype = self._detect_trainer_subtype(name) if card_type == "trainer" else ""
                regulation_mark = self._get_regulation_mark(set_code)

                return UserCard(
                    name=name,
                    set_code=set_code,
                    set_number=set_number,
                    quantity=quantity,
                    card_type=card_type,
                    subtype=subtype,
                    regulation_mark=regulation_mark
                )

        return None

    def _detect_card_type(self, name: str) -> str:
        """Detect card type from name."""
        name_lower = name.lower()

        if "energy" in name_lower:
            return "energy"

        for keyword in TRAINER_KEYWORDS:
            if keyword in name_lower:
                return "trainer"

        return "pokemon"

    def _detect_trainer_subtype(self, name: str) -> str:
        """Detect trainer subtype from name."""
        name_lower = name.lower()

        for keyword in SUPPORTER_KEYWORDS:
            if keyword in name_lower:
                return "supporter"

        for keyword in STADIUM_KEYWORDS:
            if keyword in name_lower:
                return "stadium"

        for keyword in TOOL_KEYWORDS:
            if keyword in name_lower:
                return "tool"

        return "item"

    def _get_regulation_mark(self, set_code: str) -> str:
        """Get regulation mark for a set code."""
        normalized = SET_CODE_MAP.get(set_code.upper(), set_code)
        return REGULATION_MARKS.get(set_code.upper(),
               REGULATION_MARKS.get(normalized, "?"))

    def _validate_deck(self, deck: UserDeck) -> list[ValidationIssue]:
        """Validate a deck and return list of issues."""
        issues = []

        total = deck.total_cards

        # Check total cards
        if total < 60:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                message_en=f"Deck is incomplete ({total}/60 cards)",
                message_pt=f"Deck incompleto ({total}/60 cartas)"
            ))
        elif total > 60:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message_en=f"Deck has too many cards ({total}/60)",
                message_pt=f"Deck tem cartas demais ({total}/60)"
            ))

        # Check 4-copy rule
        card_counts = {}
        for card in deck.cards:
            # Skip basic energy
            if "basic" in card.name.lower() and "energy" in card.name.lower():
                continue
            key = card.name.lower()
            card_counts[key] = card_counts.get(key, 0) + card.quantity
            if card_counts[key] > 4:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    message_en=f"More than 4 copies of {card.name}",
                    message_pt=f"Mais de 4 cópias de {card.name}",
                    card_name=card.name
                ))

        # Check rotation status
        rotating_cards = []
        for card in deck.cards:
            if card.regulation_mark == "G":
                rotating_cards.append(card.name)

        if rotating_cards:
            unique_rotating = list(set(rotating_cards))
            issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                message_en=f"{len(unique_rotating)} cards rotating in March 2026",
                message_pt=f"{len(unique_rotating)} cartas rotacionam em Março 2026"
            ))

        # Check for already rotated cards
        for card in deck.cards:
            if card.regulation_mark in ["D", "E", "F"]:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    message_en=f"{card.name} is no longer legal (regulation {card.regulation_mark})",
                    message_pt=f"{card.name} não é mais legal (regulação {card.regulation_mark})",
                    card_name=card.name
                ))

        return issues

    def suggest_deck_name(self, deck: UserDeck) -> str:
        """Suggest a name based on deck contents."""
        # Find main Pokemon (highest HP or most copies)
        pokemon = [c for c in deck.cards if c.card_type == "pokemon"]

        if not pokemon:
            return "My Deck"

        # Check for ex Pokemon
        ex_pokemon = [p for p in pokemon if " ex" in p.name.lower()]

        if ex_pokemon:
            # Sort by quantity, then by name length (longer names often more specific)
            ex_pokemon.sort(key=lambda p: (-p.quantity, -len(p.name)))
            main_pokemon = ex_pokemon[0].name

            # Clean up name
            main_pokemon = main_pokemon.replace(" ex", "").replace(" EX", "")
            return f"{main_pokemon} Deck"

        # Fallback to most common Pokemon
        pokemon.sort(key=lambda p: -p.quantity)
        return f"{pokemon[0].name} Deck"
