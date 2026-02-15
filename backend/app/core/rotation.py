"""
Rotation impact analysis for March 2026.

Given a ``ParsedDeck``, this module produces a ``RotationReport`` that
categorises every card as *rotating* (regulation G), *already illegal*
(regulation F or earlier), or *safe* (regulation H / I or later).

No framework dependencies -- pure Python only.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from app.core.deck_parser import ParsedCard, ParsedDeck, CardType


# ---------------------------------------------------------------------------
# Severity levels
# ---------------------------------------------------------------------------

class Severity(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ---------------------------------------------------------------------------
# Rotation report
# ---------------------------------------------------------------------------

@dataclass
class RotationReport:
    """Detailed breakdown of a deck's rotation exposure."""
    deck: ParsedDeck

    # Cards rotating in March 2026 (regulation G)
    rotating_pokemon: list[ParsedCard] = field(default_factory=list)
    rotating_trainers: list[ParsedCard] = field(default_factory=list)
    rotating_energy: list[ParsedCard] = field(default_factory=list)

    # Cards already rotated / illegal (regulation F or earlier)
    illegal_pokemon: list[ParsedCard] = field(default_factory=list)
    illegal_trainers: list[ParsedCard] = field(default_factory=list)
    illegal_energy: list[ParsedCard] = field(default_factory=list)

    # Cards safe (regulation H, I or later)
    safe_pokemon: list[ParsedCard] = field(default_factory=list)
    safe_trainers: list[ParsedCard] = field(default_factory=list)
    safe_energy: list[ParsedCard] = field(default_factory=list)

    # -- aggregate properties ------------------------------------------------

    @property
    def total_rotating(self) -> int:
        return (
            sum(c.quantity for c in self.rotating_pokemon)
            + sum(c.quantity for c in self.rotating_trainers)
            + sum(c.quantity for c in self.rotating_energy)
        )

    @property
    def total_illegal(self) -> int:
        return (
            sum(c.quantity for c in self.illegal_pokemon)
            + sum(c.quantity for c in self.illegal_trainers)
            + sum(c.quantity for c in self.illegal_energy)
        )

    @property
    def total_safe(self) -> int:
        return (
            sum(c.quantity for c in self.safe_pokemon)
            + sum(c.quantity for c in self.safe_trainers)
            + sum(c.quantity for c in self.safe_energy)
        )

    @property
    def total_cards(self) -> int:
        return self.total_rotating + self.total_illegal + self.total_safe

    @property
    def rotation_percentage(self) -> float:
        """Percentage of deck that rotates in March 2026."""
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
        """Severity level based on problem percentage.

        * NONE:     0 %
        * LOW:      1 -- 19 %
        * MODERATE: 20 -- 39 %
        * HIGH:     40 -- 59 %
        * CRITICAL: 60 % +
        """
        pct = self.problem_percentage
        if pct == 0:
            return Severity.NONE.value
        elif pct < 20:
            return Severity.LOW.value
        elif pct < 40:
            return Severity.MODERATE.value
        elif pct < 60:
            return Severity.HIGH.value
        else:
            return Severity.CRITICAL.value


# ---------------------------------------------------------------------------
# Analysis functions
# ---------------------------------------------------------------------------

def analyze_rotation(deck: ParsedDeck) -> RotationReport:
    """Analyse *deck* and return a ``RotationReport``."""
    report = RotationReport(deck=deck)

    for card in deck.cards:
        if card.is_already_rotated:
            _bucket_by_type(card, report.illegal_pokemon,
                            report.illegal_trainers, report.illegal_energy)
        elif card.is_rotating:
            _bucket_by_type(card, report.rotating_pokemon,
                            report.rotating_trainers, report.rotating_energy)
        else:
            _bucket_by_type(card, report.safe_pokemon,
                            report.safe_trainers, report.safe_energy)

    return report


def get_rotation_summary(report: RotationReport) -> dict:
    """Return a plain dict summarising the rotation report."""
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
                "safe": sum(c.quantity for c in report.safe_pokemon),
            },
            "trainers": {
                "rotating": sum(c.quantity for c in report.rotating_trainers),
                "illegal": sum(c.quantity for c in report.illegal_trainers),
                "safe": sum(c.quantity for c in report.safe_trainers),
            },
            "energy": {
                "rotating": sum(c.quantity for c in report.rotating_energy),
                "illegal": sum(c.quantity for c in report.illegal_energy),
                "safe": sum(c.quantity for c in report.safe_energy),
            },
        },
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _bucket_by_type(
    card: ParsedCard,
    pokemon_list: list[ParsedCard],
    trainer_list: list[ParsedCard],
    energy_list: list[ParsedCard],
) -> None:
    """Append *card* to the correct category list based on its type."""
    if card.card_type == CardType.POKEMON:
        pokemon_list.append(card)
    elif card.card_type == CardType.TRAINER:
        trainer_list.append(card)
    else:
        energy_list.append(card)
