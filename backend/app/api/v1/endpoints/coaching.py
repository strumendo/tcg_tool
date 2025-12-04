"""AI Coaching endpoints"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.user import User
from app.services.auth import get_current_user_required
from app.services.ai_coaching import AICoachingService

router = APIRouter()


@router.get("/deck/{deck_id}")
async def analyze_deck(
    deck_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Get AI coaching analysis for a deck"""
    service = AICoachingService(db)
    result = await service.analyze_deck(deck_id, current_user.id)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@router.get("/matchup")
async def get_matchup_advice(
    deck_id: int = Query(..., description="Your deck ID"),
    opponent_archetype: str = Query(..., description="Opponent deck archetype"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Get AI coaching advice for a specific matchup"""
    service = AICoachingService(db)
    result = await service.get_matchup_advice(deck_id, opponent_archetype, current_user.id)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@router.get("/improvement-plan")
async def get_improvement_plan(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Get a personalized improvement plan based on match history"""
    service = AICoachingService(db)
    return await service.get_improvement_plan(current_user.id)


@router.get("/quick-tips")
async def get_quick_tips(
    archetype: Optional[str] = Query(None, description="Your deck archetype"),
    opponent: Optional[str] = Query(None, description="Opponent archetype"),
):
    """Get quick tips for common situations"""
    tips = {
        "general": [
            "Always count your prize cards at the start of the game",
            "Think about your win condition before playing",
            "Consider what your opponent might play next turn",
            "Manage your resources - don't overextend unnecessarily",
            "Know when to use Boss's Orders vs setting up more",
        ],
        "going_first": [
            "Focus on setting up your board",
            "Don't waste supporters if you can attach and pass",
            "Establish draw engines early",
        ],
        "going_second": [
            "Look for aggressive knock-out opportunities",
            "Use your attack advantage wisely",
            "Consider if immediate aggression is worth it",
        ],
        "late_game": [
            "Count remaining prizes and plan your path to victory",
            "Consider what boss targets are left",
            "Manage your deck resources carefully",
        ],
    }

    response = {
        "general_tips": tips["general"],
        "going_first_tips": tips["going_first"],
        "going_second_tips": tips["going_second"],
        "late_game_tips": tips["late_game"],
    }

    # Add matchup-specific tips if provided
    if archetype and opponent:
        response["matchup_context"] = f"Playing {archetype} vs {opponent}"
        response["matchup_tips"] = [
            f"Review your historical win rate against {opponent}",
            "Identify their key threats and how to answer them",
            "Know your key cards for this matchup",
        ]

    return response


@router.get("/meta-positioning")
async def get_meta_positioning(
    archetype: str = Query(..., description="Your deck archetype"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Get advice on how your deck is positioned in the current meta"""
    # This would integrate with the meta module to provide positioning advice
    # For now, return general advice
    return {
        "archetype": archetype,
        "meta_position": "competitive",
        "explanation": "Your deck archetype is a recognized competitive choice in the current meta.",
        "favorable_matchups": [
            "Research your deck's favorable matchups based on tournament data",
        ],
        "unfavorable_matchups": [
            "Identify challenging matchups and consider tech cards",
        ],
        "tech_suggestions": [
            "Review top tournament lists for tech card ideas",
            "Consider meta counters that fit your strategy",
        ],
        "tournament_viability": {
            "local": "Recommended",
            "regional": "Viable with good matchup luck",
            "international": "Requires extensive practice and optimal list",
        },
    }
