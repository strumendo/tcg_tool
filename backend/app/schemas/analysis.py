"""Pydantic schemas for analysis endpoints (rotation, comparison, matchup, substitution)."""

from typing import Optional

from pydantic import BaseModel


class RotationCardOut(BaseModel):
    """A card entry in a rotation report breakdown."""

    name: str
    set_code: str
    set_number: str
    quantity: int
    regulation_mark: str
    card_type: str


class RotationBreakdownOut(BaseModel):
    """Breakdown of rotating/safe/illegal cards by type."""

    pokemon: dict[str, int]
    trainers: dict[str, int]
    energy: dict[str, int]


class RotationReportOut(BaseModel):
    """Full rotation analysis report for a deck."""

    total_cards: int
    rotating_cards: int
    illegal_cards: int
    safe_cards: int
    rotation_percentage: float
    problem_percentage: float
    severity: str
    breakdown: RotationBreakdownOut

    rotating_card_list: list[RotationCardOut] = []
    safe_card_list: list[RotationCardOut] = []


class SharedCardOut(BaseModel):
    """A card shared between two decks in a comparison."""

    name: str
    quantity_a: int
    quantity_b: int


class UniqueCardOut(BaseModel):
    """A card unique to one deck in a comparison."""

    name: str
    quantity: int
    card_type: str


class DeckComparisonOut(BaseModel):
    """Result of comparing two decks."""

    deck_a_name: str
    deck_b_name: str
    shared_count: int
    similarity_percentage: float
    shared_cards: list[SharedCardOut] = []
    unique_to_a: list[UniqueCardOut] = []
    unique_to_b: list[UniqueCardOut] = []


class MatchupAnalysisOut(BaseModel):
    """High-level matchup analysis between two decks."""

    deck_a_name: str
    deck_b_name: str
    matchup_favor: str
    a_advantages: list[str] = []
    b_advantages: list[str] = []
    key_differences: list[str] = []
    speed_score_a: int = 0
    speed_score_b: int = 0
    consistency_score_a: int = 0
    consistency_score_b: int = 0
    power_score_a: int = 0
    power_score_b: int = 0


class SubstitutionSuggestionOut(BaseModel):
    """A suggested card substitution for a rotating card."""

    original_name: str
    original_set_code: str
    original_set_number: str
    suggested_name: str
    suggested_set_code: str
    suggested_set_number: str
    match_score: float
    reasons: list[str] = []


class RotationAnalysisRequest(BaseModel):
    """Request body for rotation analysis."""

    deck_id: int


class CompareRequest(BaseModel):
    """Request body for deck comparison."""

    deck_a_id: int
    deck_b_id: int
    deck_a_name: Optional[str] = "Deck A"
    deck_b_name: Optional[str] = "Deck B"


class MatchupRequest(BaseModel):
    """Request body for matchup analysis."""

    deck_a_id: int
    deck_b_id: int
    deck_a_name: Optional[str] = "Your Deck"
    deck_b_name: Optional[str] = "Opponent Deck"


class SubstitutionRequest(BaseModel):
    """Request body for substitution suggestions."""

    deck_id: int
    min_score: float = 30.0
    max_per_card: int = 3
