from fastapi import APIRouter

from app.api.v1 import (
    analysis,
    battles,
    cards,
    chat,
    collection,
    decks,
    meta,
    simulation,
    stats,
    suggestions,
    tournaments,
)

api_router = APIRouter()

api_router.include_router(cards.router,       prefix="/cards",       tags=["cards"])
api_router.include_router(decks.router,       prefix="/decks",       tags=["decks"])
api_router.include_router(meta.router,        prefix="/meta",        tags=["meta"])
api_router.include_router(analysis.router,    prefix="/analysis",    tags=["analysis"])
api_router.include_router(battles.router,     prefix="/battles",     tags=["battles"])
api_router.include_router(chat.router,        prefix="/chat",        tags=["chat"])
api_router.include_router(stats.router,       prefix="/stats",       tags=["stats"])
api_router.include_router(collection.router,  prefix="/collection",  tags=["collection"])
api_router.include_router(suggestions.router, prefix="/suggestions", tags=["suggestions"])
api_router.include_router(simulation.router,  prefix="/simulation",  tags=["simulation"])
api_router.include_router(tournaments.router, prefix="/tournaments", tags=["tournaments"])
