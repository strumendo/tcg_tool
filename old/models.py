"""Data models for TCG Rotation Checker."""
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class CardType(str, Enum):
    POKEMON = "pokemon"
    TRAINER = "trainer"
    ENERGY = "energy"


class TrainerSubtype(str, Enum):
    ITEM = "item"
    SUPPORTER = "supporter"
    STADIUM = "stadium"
    TOOL = "tool"


class CardFunction(str, Enum):
    """Functional categories for substitution analysis."""
    DRAW = "draw"              # Draw cards
    SEARCH = "search"          # Search deck
    RECOVERY = "recovery"      # Recover from discard
    REMOVAL = "removal"        # Remove opponent's cards
    SWITCHING = "switching"    # Switch Pokemon
    ENERGY_ACCEL = "energy_accel"  # Energy acceleration
    DAMAGE = "damage"          # Direct damage
    HEALING = "healing"        # Heal damage
    DISRUPTION = "disruption"  # Disrupt opponent
    SETUP = "setup"            # Setup/evolution
    PROTECTION = "protection"  # Protect Pokemon
    OTHER = "other"


@dataclass
class Card:
    """Represents a Pokemon TCG card."""
    name: str
    card_type: CardType
    set_code: str
    set_number: str
    quantity: int = 1
    regulation_mark: Optional[str] = None
    subtype: Optional[str] = None
    hp: Optional[int] = None
    energy_type: Optional[str] = None
    abilities: Optional[str] = None
    attacks: Optional[str] = None
    functions: list[CardFunction] = field(default_factory=list)

    @property
    def is_rotating(self) -> bool:
        """Check if card rotates in March 2026 (regulation mark G)."""
        return self.regulation_mark == "G"

    @property
    def is_already_rotated(self) -> bool:
        """Check if card already rotated (regulation mark F or earlier)."""
        if not self.regulation_mark:
            return False
        return self.regulation_mark in ["A", "B", "C", "D", "E", "F"]

    @property
    def is_safe(self) -> bool:
        """Check if card is safe (H, I or later)."""
        if not self.regulation_mark:
            # Basic energy without mark is always legal
            if "basic" in self.name.lower() and "energy" in self.name.lower():
                return True
            return False
        return self.regulation_mark in ["H", "I", "J", "K"]

    @property
    def is_legal_post_rotation(self) -> bool:
        """Check if card will be legal after March 2026 rotation."""
        return self.is_safe

    @property
    def full_id(self) -> str:
        """Get full card identifier."""
        return f"{self.set_code} {self.set_number}"

    def __str__(self) -> str:
        return f"{self.quantity} {self.name} {self.set_code} {self.set_number}"


@dataclass
class Deck:
    """Represents a Pokemon TCG deck."""
    cards: list[Card] = field(default_factory=list)
    name: str = "My Deck"

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
    def rotating_cards(self) -> list[Card]:
        """Get all cards that will rotate."""
        return [c for c in self.cards if c.is_rotating]

    @property
    def safe_cards(self) -> list[Card]:
        """Get all cards that won't rotate."""
        return [c for c in self.cards if not c.is_rotating]

    @property
    def rotation_impact(self) -> float:
        """Percentage of deck that rotates."""
        if self.total_cards == 0:
            return 0.0
        rotating = sum(c.quantity for c in self.rotating_cards)
        return (rotating / self.total_cards) * 100


@dataclass
class Substitution:
    """Represents a card substitution suggestion."""
    original_card: Card
    suggested_card: Card
    match_score: float  # 0-100
    reasons: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        return f"{self.original_card.name} → {self.suggested_card.name} ({self.match_score:.0f}%)"
