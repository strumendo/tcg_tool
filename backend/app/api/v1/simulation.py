"""Play simulation API route handlers."""

from fastapi import APIRouter, HTTPException

from app.dependencies import DBSession
from app.integrations import ClaudeClient
from app.schemas.simulation import SimulationRequest, SimulationResultOut
from app.services import deck_service, meta_service

router = APIRouter()


@router.post("/play-sequence", response_model=SimulationResultOut)
async def simulate_play_sequence(
    db: DBSession, request: SimulationRequest
) -> SimulationResultOut:
    """Simulate an optimal play sequence using AI analysis."""
    deck = await deck_service.get_deck(db, request.deck_id)

    deck_info = {
        "name": deck.name,
        "archetype": deck.archetype,
        "cards": [
            {
                "name": dc.card.name_en or dc.card.name_pt or "Unknown",
                "type": dc.card.card_type,
                "quantity": dc.quantity,
            }
            for dc in deck.deck_cards
        ],
    }

    opponent_name = "Unknown Opponent"
    opponent_info: dict = {}

    if request.opponent_deck_id:
        opponent_deck = await deck_service.get_deck(db, request.opponent_deck_id)
        opponent_name = opponent_deck.name
        opponent_info = {
            "name": opponent_deck.name,
            "archetype": opponent_deck.archetype,
            "cards": [
                {
                    "name": dc.card.name_en or dc.card.name_pt or "Unknown",
                    "type": dc.card.card_type,
                    "quantity": dc.quantity,
                }
                for dc in opponent_deck.deck_cards
            ],
        }
    elif request.opponent_meta_deck_id:
        meta_deck = await meta_service.get_meta_deck(db, request.opponent_meta_deck_id)
        opponent_name = meta_deck.name_en or meta_deck.name_pt or "Meta Deck"
        opponent_info = {
            "name": opponent_name,
            "key_pokemon": meta_deck.key_pokemon,
            "strategy": meta_deck.strategy_en,
        }

    try:
        client = ClaudeClient()
        analysis = await client.simulate_plays(
            deck_info, opponent_info, turns=request.turns
        )
        return SimulationResultOut(
            deck_name=deck.name,
            opponent_name=opponent_name,
            total_turns=request.turns,
            analysis=analysis,
            play_sequence=[],
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"AI service error: {str(exc)}",
        )
