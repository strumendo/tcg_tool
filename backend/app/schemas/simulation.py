"""Pydantic schemas for play simulation endpoints."""

from typing import Optional

from pydantic import BaseModel


class SimulationRequest(BaseModel):
    """Request body for simulating a play sequence."""

    deck_id: int
    opponent_deck_id: Optional[int] = None
    opponent_meta_deck_id: Optional[str] = None
    turns: int = 6


class PlaySequenceOut(BaseModel):
    """A single turn in a simulated play sequence."""

    turn: int
    player: str
    action: str
    card_name: Optional[str] = None
    details: Optional[str] = None


class SimulationResultOut(BaseModel):
    """Full simulation result with turn-by-turn play sequence."""

    deck_name: str
    opponent_name: str
    total_turns: int
    analysis: str
    play_sequence: list[PlaySequenceOut] = []
