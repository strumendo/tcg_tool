"""Pydantic v2 schemas for request/response serialization."""

from app.schemas.analysis import (
    DeckComparisonOut,
    MatchupAnalysisOut,
    RotationBreakdownOut,
    RotationReportOut,
    SubstitutionSuggestionOut,
)
from app.schemas.battle import BattleActionOut, BattleCreate, BattleOut, BattleUpdate
from app.schemas.card import (
    CardAbilityOut,
    CardAttackOut,
    CardOut,
    CardSearchQuery,
    CardSetOut,
)
from app.schemas.chat import ChatMessage, ChatRequest, ChatResponse
from app.schemas.collection import CollectionEntryOut, CollectionUpdate, MissingCardOut
from app.schemas.deck import DeckCardOut, DeckCreate, DeckImport, DeckOut, DeckUpdate
from app.schemas.meta import MetaDeckOut, MetaMatchupOut, MetaTierGroup
from app.schemas.simulation import PlaySequenceOut, SimulationRequest, SimulationResultOut
from app.schemas.stats import CardUsageStatsOut, DeckUsageStatsOut, UserStatsOut
from app.schemas.tournament import NewsArticleOut, TournamentOut
from app.schemas.user import UserCreate, UserOut

__all__ = [
    # Card
    "CardSetOut",
    "CardAbilityOut",
    "CardAttackOut",
    "CardOut",
    "CardSearchQuery",
    # Deck
    "DeckCardOut",
    "DeckOut",
    "DeckCreate",
    "DeckImport",
    "DeckUpdate",
    # Meta
    "MetaMatchupOut",
    "MetaDeckOut",
    "MetaTierGroup",
    # Analysis
    "RotationBreakdownOut",
    "RotationReportOut",
    "DeckComparisonOut",
    "MatchupAnalysisOut",
    "SubstitutionSuggestionOut",
    # Battle
    "BattleActionOut",
    "BattleOut",
    "BattleCreate",
    "BattleUpdate",
    # Chat
    "ChatRequest",
    "ChatMessage",
    "ChatResponse",
    # Stats
    "CardUsageStatsOut",
    "DeckUsageStatsOut",
    "UserStatsOut",
    # User
    "UserOut",
    "UserCreate",
    # Collection
    "CollectionEntryOut",
    "MissingCardOut",
    "CollectionUpdate",
    # Simulation
    "SimulationRequest",
    "PlaySequenceOut",
    "SimulationResultOut",
    # Tournament
    "TournamentOut",
    "NewsArticleOut",
]
