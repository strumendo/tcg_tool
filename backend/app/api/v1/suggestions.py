"""AI-powered card swap suggestion API route handlers."""

from fastapi import APIRouter, HTTPException

from app.dependencies import DBSession
from app.integrations import ClaudeClient
from app.services import deck_service

router = APIRouter()


@router.post("/swaps")
async def suggest_swaps(
    db: DBSession,
    deck_id: int,
) -> dict:
    """Get AI-powered card swap suggestions for a deck.

    Sends the deck information and current meta context to Claude
    for intelligent swap recommendations.
    """
    deck = await deck_service.get_deck(db, deck_id)

    # Build deck info dict for the AI
    deck_info = {
        "name": deck.name,
        "archetype": deck.archetype,
        "total_cards": deck.total_cards,
        "cards": [
            {
                "name": dc.card.name_en or dc.card.name_pt or "Unknown",
                "type": dc.card.card_type,
                "quantity": dc.quantity,
                "regulation_mark": dc.card.regulation_mark,
                "set_code": dc.card.card_set.code if dc.card.card_set else None,
            }
            for dc in deck.deck_cards
        ],
    }

    # Basic meta context
    meta_context = {
        "rotation_date": "March 2026",
        "rotating_marks": ["G"],
        "safe_marks": ["H", "I"],
    }

    try:
        client = ClaudeClient()
        response = await client.suggest_swaps(deck_info, meta_context)
        return {"suggestions": response}
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"AI service error: {str(exc)}",
        )
