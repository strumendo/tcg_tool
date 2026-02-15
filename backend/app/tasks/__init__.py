"""Background tasks for syncing external data into the local database."""

from app.tasks.seed_abilities import seed_abilities
from app.tasks.sync_cards import sync_all_cards, sync_all_sets, sync_set_cards
from app.tasks.sync_limitless import sync_all_limitless, sync_card_usage, sync_deck_usage
from app.tasks.sync_news import sync_news
from app.tasks.sync_tournaments import sync_tournaments

__all__ = [
    # Card sync (TCGdex)
    "sync_all_sets",
    "sync_set_cards",
    "sync_all_cards",
    # Limitless usage sync
    "sync_card_usage",
    "sync_deck_usage",
    "sync_all_limitless",
    # Tournament sync (RK9)
    "sync_tournaments",
    # News sync (PokeBeach)
    "sync_news",
    # Seeding
    "seed_abilities",
]
