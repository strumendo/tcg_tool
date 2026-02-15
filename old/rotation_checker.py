"""Rotation validation for March 2026."""
from dataclasses import dataclass, field
from models import Deck, Card, CardType


@dataclass
class RotationReport:
    """Report on deck rotation impact."""
    deck: Deck
    # Cards rotating in March 2026 (regulation G)
    rotating_pokemon: list[Card] = field(default_factory=list)
    rotating_trainers: list[Card] = field(default_factory=list)
    rotating_energy: list[Card] = field(default_factory=list)
    # Cards already rotated/illegal (regulation F or earlier)
    illegal_pokemon: list[Card] = field(default_factory=list)
    illegal_trainers: list[Card] = field(default_factory=list)
    illegal_energy: list[Card] = field(default_factory=list)
    # Cards safe (regulation H, I or later)
    safe_pokemon: list[Card] = field(default_factory=list)
    safe_trainers: list[Card] = field(default_factory=list)
    safe_energy: list[Card] = field(default_factory=list)

    @property
    def total_rotating(self) -> int:
        """Total cards rotating in March 2026."""
        return (
            sum(c.quantity for c in self.rotating_pokemon) +
            sum(c.quantity for c in self.rotating_trainers) +
            sum(c.quantity for c in self.rotating_energy)
        )

    @property
    def total_illegal(self) -> int:
        """Total cards already illegal."""
        return (
            sum(c.quantity for c in self.illegal_pokemon) +
            sum(c.quantity for c in self.illegal_trainers) +
            sum(c.quantity for c in self.illegal_energy)
        )

    @property
    def total_safe(self) -> int:
        """Total cards safe post-rotation."""
        return (
            sum(c.quantity for c in self.safe_pokemon) +
            sum(c.quantity for c in self.safe_trainers) +
            sum(c.quantity for c in self.safe_energy)
        )

    @property
    def total_cards(self) -> int:
        """Total cards in deck."""
        return self.total_rotating + self.total_illegal + self.total_safe

    @property
    def rotation_percentage(self) -> float:
        """Percentage of deck that rotates (March 2026)."""
        if self.total_cards == 0:
            return 0.0
        return (self.total_rotating / self.total_cards) * 100

    @property
    def problem_percentage(self) -> float:
        """Percentage of deck with problems (rotating + already illegal)."""
        if self.total_cards == 0:
            return 0.0
        return ((self.total_rotating + self.total_illegal) / self.total_cards) * 100

    @property
    def severity(self) -> str:
        """Severity level based on rotation impact."""
        pct = self.problem_percentage
        if pct == 0:
            return "NONE"
        elif pct < 20:
            return "LOW"
        elif pct < 40:
            return "MODERATE"
        elif pct < 60:
            return "HIGH"
        else:
            return "CRITICAL"


def analyze_rotation(deck: Deck) -> RotationReport:
    """Analyze deck for rotation impact."""
    report = RotationReport(deck=deck)

    for card in deck.cards:
        # Categorize by legality status
        if card.is_already_rotated:
            if card.card_type == CardType.POKEMON:
                report.illegal_pokemon.append(card)
            elif card.card_type == CardType.TRAINER:
                report.illegal_trainers.append(card)
            else:
                report.illegal_energy.append(card)
        elif card.is_rotating:
            if card.card_type == CardType.POKEMON:
                report.rotating_pokemon.append(card)
            elif card.card_type == CardType.TRAINER:
                report.rotating_trainers.append(card)
            else:
                report.rotating_energy.append(card)
        else:
            # Safe (H, I or later, or basic energy)
            if card.card_type == CardType.POKEMON:
                report.safe_pokemon.append(card)
            elif card.card_type == CardType.TRAINER:
                report.safe_trainers.append(card)
            else:
                report.safe_energy.append(card)

    return report


def get_rotation_summary(report: RotationReport) -> dict:
    """Get summary statistics."""
    return {
        "total_cards": report.total_cards,
        "rotating_cards": report.total_rotating,
        "illegal_cards": report.total_illegal,
        "safe_cards": report.total_safe,
        "rotation_percentage": round(report.rotation_percentage, 1),
        "problem_percentage": round(report.problem_percentage, 1),
        "severity": report.severity,
        "breakdown": {
            "pokemon": {
                "rotating": sum(c.quantity for c in report.rotating_pokemon),
                "illegal": sum(c.quantity for c in report.illegal_pokemon),
                "safe": sum(c.quantity for c in report.safe_pokemon)
            },
            "trainers": {
                "rotating": sum(c.quantity for c in report.rotating_trainers),
                "illegal": sum(c.quantity for c in report.illegal_trainers),
                "safe": sum(c.quantity for c in report.safe_trainers)
            },
            "energy": {
                "rotating": sum(c.quantity for c in report.rotating_energy),
                "illegal": sum(c.quantity for c in report.illegal_energy),
                "safe": sum(c.quantity for c in report.safe_energy)
            }
        }
    }
