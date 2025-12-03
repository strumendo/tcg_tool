"""Meta Analysis Service - Deck comparison with LLM insights"""
import json
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import structlog
import anthropic

from app.models.deck import Deck, DeckCard
from app.models.card import Card, CardType
from app.models.meta import MetaSnapshot, MetaDeck
from app.schemas.meta import DeckComparisonResult
from app.core.config import settings

logger = structlog.get_logger()


class MetaAnalysisService:
    """Service for analyzing decks against the meta"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = None
        if settings.anthropic_api_key:
            self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    async def compare_deck_to_meta(
        self,
        deck: Deck,
        snapshot: MetaSnapshot
    ) -> DeckComparisonResult:
        """Compare a deck against the current meta"""
        # Get deck cards
        deck_query = select(Deck).options(
            selectinload(Deck.cards).selectinload(DeckCard.card)
        ).where(Deck.id == deck.id)
        result = await self.db.execute(deck_query)
        deck = result.scalar_one()

        # Get top 10 meta decks
        top_decks = sorted(snapshot.meta_decks, key=lambda x: x.rank)[:10]

        # Determine deck archetype
        deck_archetype = deck.archetype or await self._identify_archetype(deck)

        # Find position in meta if applicable
        meta_position = None
        for md in top_decks:
            if self._archetypes_match(deck_archetype, md.archetype):
                meta_position = md.rank
                break

        # Calculate matchup analysis
        matchup_analysis = await self._analyze_matchups(deck, deck_archetype, top_decks)

        # Calculate overall meta score
        overall_score = self._calculate_meta_score(matchup_analysis, top_decks)

        # Get AI insights if available
        ai_insights = await self._get_ai_insights(deck, deck_archetype, top_decks, matchup_analysis)

        return DeckComparisonResult(
            deck_archetype=deck_archetype,
            meta_position=meta_position,
            matchup_analysis=matchup_analysis,
            overall_meta_score=overall_score,
            strengths=ai_insights.get("strengths", []),
            weaknesses=ai_insights.get("weaknesses", []),
            suggestions=ai_insights.get("suggestions", [])
        )

    async def _identify_archetype(self, deck: Deck) -> str:
        """Identify deck archetype from card list"""
        # Find main attackers (V/ex/VSTAR Pokemon)
        main_pokemon = []

        for dc in deck.cards:
            if dc.card and dc.card.card_type == CardType.POKEMON:
                if dc.card.subtype and dc.card.subtype.value in ["ex", "v", "vstar", "vmax"]:
                    main_pokemon.append((dc.card.name, dc.quantity))

        if main_pokemon:
            # Sort by quantity and return the most common
            main_pokemon.sort(key=lambda x: x[1], reverse=True)
            return main_pokemon[0][0]

        return "Unknown"

    def _archetypes_match(self, arch1: str, arch2: str) -> bool:
        """Check if two archetypes are similar"""
        arch1 = arch1.lower().strip()
        arch2 = arch2.lower().strip()

        # Direct match
        if arch1 == arch2:
            return True

        # Check if one contains the other
        if arch1 in arch2 or arch2 in arch1:
            return True

        # Check common name variations
        variations = {
            "charizard": ["charizard ex", "zard"],
            "lugia": ["lugia vstar", "archeops"],
            "gardevoir": ["gardevoir ex", "garde"],
            "miraidon": ["miraidon ex", "regieleki"],
            "roaring moon": ["roaring moon ex", "moon"],
            "chien-pao": ["chien pao ex", "baxcalibur"],
        }

        for key, alts in variations.items():
            if key in arch1 or any(alt in arch1 for alt in alts):
                if key in arch2 or any(alt in arch2 for alt in alts):
                    return True

        return False

    async def _analyze_matchups(
        self,
        deck: Deck,
        deck_archetype: str,
        top_decks: list[MetaDeck]
    ) -> dict:
        """Analyze matchups against top decks"""
        matchup_analysis = {}

        for meta_deck in top_decks:
            # Check if meta deck has matchup data
            if meta_deck.matchups:
                # Look for our deck in their matchup data
                for opponent, win_rate in meta_deck.matchups.items():
                    if self._archetypes_match(deck_archetype, opponent):
                        # Invert the win rate (their win rate against us)
                        matchup_analysis[meta_deck.archetype] = {
                            "win_rate": 100 - win_rate,
                            "notes": f"Based on {meta_deck.archetype} matchup data"
                        }
                        break

            if meta_deck.archetype not in matchup_analysis:
                # Use type-based estimation or default to 50%
                estimated_wr = self._estimate_matchup(deck, deck_archetype, meta_deck)
                matchup_analysis[meta_deck.archetype] = {
                    "win_rate": estimated_wr,
                    "notes": "Estimated based on deck composition"
                }

        return matchup_analysis

    def _estimate_matchup(
        self,
        deck: Deck,
        deck_archetype: str,
        meta_deck: MetaDeck
    ) -> float:
        """Estimate matchup win rate based on deck composition"""
        # Base 50% win rate
        win_rate = 50.0

        # TODO: Implement type-based and card-based matchup estimation
        # This would require analyzing energy types, key cards, etc.

        return win_rate

    def _calculate_meta_score(
        self,
        matchup_analysis: dict,
        top_decks: list[MetaDeck]
    ) -> float:
        """Calculate overall meta score (weighted by meta share)"""
        total_score = 0.0
        total_weight = 0.0

        for meta_deck in top_decks:
            if meta_deck.archetype in matchup_analysis:
                wr = matchup_analysis[meta_deck.archetype]["win_rate"]
                weight = meta_deck.meta_share

                total_score += wr * weight
                total_weight += weight

        if total_weight > 0:
            return round(total_score / total_weight, 1)
        return 50.0

    async def _get_ai_insights(
        self,
        deck: Deck,
        deck_archetype: str,
        top_decks: list[MetaDeck],
        matchup_analysis: dict
    ) -> dict:
        """Get AI-powered insights using Claude"""
        if not self.client:
            return {
                "strengths": ["AI analysis not available - configure ANTHROPIC_API_KEY"],
                "weaknesses": [],
                "suggestions": []
            }

        # Build deck list string
        deck_list = []
        for dc in deck.cards:
            if dc.card:
                deck_list.append(f"{dc.quantity}x {dc.card.name}")

        # Build meta summary
        meta_summary = []
        for md in top_decks[:10]:
            mu = matchup_analysis.get(md.archetype, {})
            meta_summary.append(
                f"{md.rank}. {md.archetype} ({md.meta_share:.1f}% meta) - "
                f"Estimated WR: {mu.get('win_rate', 50)}%"
            )

        prompt = f"""Analyze this Pokemon TCG deck against the current meta:

DECK: {deck_archetype}
{chr(10).join(deck_list)}

CURRENT META TOP 10:
{chr(10).join(meta_summary)}

Provide insights in JSON format:
{{
    "strengths": ["list of deck strengths in current meta"],
    "weaknesses": ["list of deck weaknesses and bad matchups"],
    "suggestions": ["specific suggestions to improve meta positioning"]
}}

Be specific and practical. Focus on actionable insights."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = response.content[0].text

            # Parse JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                return json.loads(json_match.group())

        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")

        return {
            "strengths": ["Analysis pending"],
            "weaknesses": [],
            "suggestions": []
        }
