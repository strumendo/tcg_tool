"""SQLAlchemy ORM models for the TCG Tool backend."""

from app.models.base import Base, TimestampMixin
from app.models.battle import Battle, BattleAction
from app.models.card import Card, CardAbility, CardAttack, CardFunction, CardSet
from app.models.collection import UserCollection
from app.models.deck import Deck, DeckCard
from app.models.meta import MetaDeck, MetaDeckCard, MetaMatchup
from app.models.tournament import (
    CardUsageStats,
    DeckUsageStats,
    NewsArticle,
    Tournament,
)
from app.models.user import User

__all__ = [
    # Base
    "Base",
    "TimestampMixin",
    # Card
    "CardSet",
    "Card",
    "CardAbility",
    "CardAttack",
    "CardFunction",
    # User
    "User",
    # Deck
    "Deck",
    "DeckCard",
    # Meta
    "MetaDeck",
    "MetaDeckCard",
    "MetaMatchup",
    # Battle
    "Battle",
    "BattleAction",
    # Collection
    "UserCollection",
    # Tournament & Stats
    "Tournament",
    "NewsArticle",
    "CardUsageStats",
    "DeckUsageStats",
]
