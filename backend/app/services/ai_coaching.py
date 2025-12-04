"""AI Coaching Service for deck analysis and game advice"""
import json
from typing import Optional, Dict, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.models.deck import Deck
from app.models.match import Match, MatchResult


class AICoachingService:
    """AI-powered coaching for Pokemon TCG players"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.has_anthropic = bool(settings.anthropic_api_key)

    async def analyze_deck(self, deck_id: int, user_id: int) -> Dict[str, Any]:
        """Analyze a deck and provide AI coaching insights"""
        # Get deck with cards
        query = select(Deck).options(
            selectinload(Deck.cards)
        ).where(Deck.id == deck_id)
        result = await self.db.execute(query)
        deck = result.scalar_one_or_none()

        if not deck:
            return {"error": "Deck not found"}

        # Get match history for this deck
        matches_query = select(Match).where(
            Match.deck_id == deck_id
        ).order_by(Match.played_at.desc()).limit(20)
        matches_result = await self.db.execute(matches_query)
        matches = matches_result.scalars().all()

        # Calculate statistics
        stats = self._calculate_deck_stats(matches)

        # Generate analysis
        if self.has_anthropic:
            analysis = await self._generate_ai_analysis(deck, matches, stats)
        else:
            analysis = self._generate_basic_analysis(deck, matches, stats)

        return {
            "deck_name": deck.name,
            "archetype": deck.archetype,
            "stats": stats,
            "analysis": analysis,
        }

    def _calculate_deck_stats(self, matches: List[Match]) -> Dict[str, Any]:
        """Calculate statistics from match history"""
        if not matches:
            return {
                "total_matches": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0.0,
                "matchup_breakdown": {},
                "first_turn_win_rate": None,
            }

        wins = sum(1 for m in matches if m.result == MatchResult.WIN)
        losses = sum(1 for m in matches if m.result == MatchResult.LOSS)
        total = wins + losses

        # Calculate matchup breakdown
        matchup_breakdown = {}
        for match in matches:
            if match.opponent_archetype:
                if match.opponent_archetype not in matchup_breakdown:
                    matchup_breakdown[match.opponent_archetype] = {"wins": 0, "losses": 0}
                if match.result == MatchResult.WIN:
                    matchup_breakdown[match.opponent_archetype]["wins"] += 1
                elif match.result == MatchResult.LOSS:
                    matchup_breakdown[match.opponent_archetype]["losses"] += 1

        # Calculate first turn advantage
        first_turn_wins = sum(1 for m in matches if m.went_first and m.result == MatchResult.WIN)
        first_turn_games = sum(1 for m in matches if m.went_first is not None and m.went_first)
        first_turn_win_rate = (first_turn_wins / first_turn_games * 100) if first_turn_games > 0 else None

        return {
            "total_matches": total,
            "wins": wins,
            "losses": losses,
            "win_rate": round(wins / total * 100, 1) if total > 0 else 0.0,
            "matchup_breakdown": matchup_breakdown,
            "first_turn_win_rate": round(first_turn_win_rate, 1) if first_turn_win_rate else None,
        }

    def _generate_basic_analysis(
        self, deck: Deck, matches: List[Match], stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate basic analysis without AI"""
        strengths = []
        weaknesses = []
        tips = []
        matchup_advice = []

        # Analyze based on stats
        if stats["win_rate"] >= 60:
            strengths.append("Strong overall performance with a winning record")
        elif stats["win_rate"] < 45 and stats["total_matches"] >= 5:
            weaknesses.append("Struggling to maintain a positive win rate")
            tips.append("Consider reviewing your deck list for consistency issues")

        # Analyze matchups
        for archetype, data in stats.get("matchup_breakdown", {}).items():
            total = data["wins"] + data["losses"]
            if total >= 3:
                wr = data["wins"] / total * 100
                if wr >= 70:
                    strengths.append(f"Strong matchup against {archetype} ({wr:.0f}% win rate)")
                elif wr <= 30:
                    weaknesses.append(f"Struggling against {archetype} ({wr:.0f}% win rate)")
                    matchup_advice.append({
                        "archetype": archetype,
                        "win_rate": round(wr, 1),
                        "advice": f"Consider tech cards specifically for the {archetype} matchup",
                    })

        # First turn analysis
        if stats.get("first_turn_win_rate") is not None:
            if stats["first_turn_win_rate"] < 40:
                tips.append("Your first-turn performance is below average. Consider more aggressive opening plays.")
            elif stats["first_turn_win_rate"] > 65:
                strengths.append("Excellent first-turn performance")

        # Deck composition tips
        if deck.pokemon_count < 12:
            tips.append("Consider adding more Pokemon for consistency")
        if deck.trainer_count < 30:
            tips.append("Most competitive decks run 35+ trainers for consistency")

        if not strengths:
            strengths.append("Keep practicing and tracking your matches to identify patterns")
        if not tips:
            tips.append("Continue tracking matches to get more detailed insights")

        return {
            "summary": f"Analysis of {deck.name} ({deck.archetype or 'Unknown archetype'})",
            "strengths": strengths,
            "weaknesses": weaknesses,
            "tips": tips,
            "matchup_advice": matchup_advice,
        }

    async def _generate_ai_analysis(
        self, deck: Deck, matches: List[Match], stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate AI-powered analysis using Claude"""
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

            # Build context
            deck_info = f"""
Deck: {deck.name}
Archetype: {deck.archetype or 'Unknown'}
Format: {deck.format.value}
Pokemon: {deck.pokemon_count}, Trainers: {deck.trainer_count}, Energy: {deck.energy_count}
"""

            match_info = f"""
Total Matches: {stats['total_matches']}
Win Rate: {stats['win_rate']}%
Matchup Breakdown: {json.dumps(stats['matchup_breakdown'], indent=2)}
"""

            prompt = f"""You are an expert Pokemon TCG coach. Analyze this deck and provide actionable coaching advice.

{deck_info}

Match History:
{match_info}

Provide your analysis in the following JSON format:
{{
    "summary": "Brief 1-2 sentence summary of the deck's performance",
    "strengths": ["list of 2-3 key strengths"],
    "weaknesses": ["list of 2-3 areas for improvement"],
    "tips": ["list of 3-5 specific, actionable tips"],
    "matchup_advice": [
        {{"archetype": "opponent deck", "advice": "specific advice for this matchup"}}
    ]
}}

Focus on practical, specific advice. Reference actual match data when available."""

            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse the response
            content = response.content[0].text
            # Try to extract JSON from the response
            if "{" in content:
                json_start = content.index("{")
                json_end = content.rindex("}") + 1
                return json.loads(content[json_start:json_end])
            else:
                return self._generate_basic_analysis(deck, matches, stats)

        except Exception as e:
            print(f"AI analysis error: {e}")
            return self._generate_basic_analysis(deck, matches, stats)

    async def get_matchup_advice(
        self, deck_id: int, opponent_archetype: str, user_id: int
    ) -> Dict[str, Any]:
        """Get specific advice for a matchup"""
        # Get deck
        query = select(Deck).where(Deck.id == deck_id)
        result = await self.db.execute(query)
        deck = result.scalar_one_or_none()

        if not deck:
            return {"error": "Deck not found"}

        # Get match history vs this archetype
        matches_query = select(Match).where(
            Match.deck_id == deck_id,
            Match.opponent_archetype == opponent_archetype
        ).order_by(Match.played_at.desc()).limit(10)
        matches_result = await self.db.execute(matches_query)
        matches = matches_result.scalars().all()

        wins = sum(1 for m in matches if m.result == MatchResult.WIN)
        total = len(matches)
        win_rate = (wins / total * 100) if total > 0 else None

        if self.has_anthropic and total >= 3:
            advice = await self._generate_ai_matchup_advice(deck, opponent_archetype, matches, win_rate)
        else:
            advice = self._generate_basic_matchup_advice(deck, opponent_archetype, win_rate, total)

        return {
            "your_deck": deck.name,
            "your_archetype": deck.archetype,
            "opponent_archetype": opponent_archetype,
            "matches_played": total,
            "win_rate": round(win_rate, 1) if win_rate else None,
            "advice": advice,
        }

    def _generate_basic_matchup_advice(
        self, deck: Deck, opponent_archetype: str, win_rate: Optional[float], matches: int
    ) -> Dict[str, Any]:
        """Generate basic matchup advice"""
        tips = []
        key_cards = []
        game_plan = ""

        if win_rate is None:
            game_plan = f"You haven't played against {opponent_archetype} yet. Focus on learning their strategy."
            tips = [
                "Watch gameplay videos of this matchup",
                "Identify their key Pokemon and how to counter them",
                "Practice the matchup in casual games first",
            ]
        elif win_rate >= 60:
            game_plan = f"You have a favorable matchup against {opponent_archetype}. Stay consistent."
            tips = [
                "Don't overextend - play your normal game",
                "Take calculated risks since the matchup favors you",
            ]
        elif win_rate <= 40:
            game_plan = f"This is a challenging matchup. You may need to take more risks."
            tips = [
                "Consider aggressive mulligans for key cards",
                "Look for tech options that help this matchup",
                "Study how top players approach this matchup",
            ]
        else:
            game_plan = f"This is an even matchup. Execution and draws will determine the winner."
            tips = [
                "Focus on consistent play",
                "Avoid misplays - small edges matter",
                "Track which games you won/lost to identify patterns",
            ]

        return {
            "game_plan": game_plan,
            "tips": tips,
            "key_cards_to_find": key_cards,
            "common_mistakes": ["Data needed from more matches to identify patterns"],
        }

    async def _generate_ai_matchup_advice(
        self, deck: Deck, opponent_archetype: str, matches: List[Match], win_rate: float
    ) -> Dict[str, Any]:
        """Generate AI-powered matchup advice"""
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

            prompt = f"""You are an expert Pokemon TCG coach. Provide specific matchup advice.

Your deck: {deck.name} ({deck.archetype or 'Unknown'})
Opponent archetype: {opponent_archetype}
Your win rate in this matchup: {win_rate:.1f}% ({len(matches)} games)

Provide your advice in this JSON format:
{{
    "game_plan": "2-3 sentence overview of how to approach this matchup",
    "tips": ["3-5 specific tips for this matchup"],
    "key_cards_to_find": ["list of key cards to prioritize in this matchup"],
    "common_mistakes": ["2-3 common mistakes to avoid"]
}}

Be specific to this matchup with practical advice."""

            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text
            if "{" in content:
                json_start = content.index("{")
                json_end = content.rindex("}") + 1
                return json.loads(content[json_start:json_end])
            else:
                return self._generate_basic_matchup_advice(deck, opponent_archetype, win_rate, len(matches))

        except Exception as e:
            print(f"AI matchup advice error: {e}")
            return self._generate_basic_matchup_advice(deck, opponent_archetype, win_rate, len(matches))

    async def get_improvement_plan(self, user_id: int) -> Dict[str, Any]:
        """Generate a personalized improvement plan based on all user data"""
        # Get all user matches
        matches_query = select(Match).order_by(Match.played_at.desc()).limit(50)
        matches_result = await self.db.execute(matches_query)
        matches = matches_result.scalars().all()

        if not matches:
            return {
                "status": "no_data",
                "message": "Start logging matches to get a personalized improvement plan!",
                "next_steps": [
                    "Create your deck in the Deck Builder",
                    "Log your matches with opponent information",
                    "Track at least 10 matches for meaningful insights",
                ],
            }

        # Calculate overall stats
        total = len(matches)
        wins = sum(1 for m in matches if m.result == MatchResult.WIN)
        losses = sum(1 for m in matches if m.result == MatchResult.LOSS)
        win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0

        # Find problem matchups
        matchup_data = {}
        for match in matches:
            if match.opponent_archetype:
                if match.opponent_archetype not in matchup_data:
                    matchup_data[match.opponent_archetype] = {"wins": 0, "losses": 0}
                if match.result == MatchResult.WIN:
                    matchup_data[match.opponent_archetype]["wins"] += 1
                elif match.result == MatchResult.LOSS:
                    matchup_data[match.opponent_archetype]["losses"] += 1

        problem_matchups = []
        strong_matchups = []
        for arch, data in matchup_data.items():
            total_games = data["wins"] + data["losses"]
            if total_games >= 3:
                wr = data["wins"] / total_games * 100
                if wr <= 35:
                    problem_matchups.append({"archetype": arch, "win_rate": round(wr, 1)})
                elif wr >= 65:
                    strong_matchups.append({"archetype": arch, "win_rate": round(wr, 1)})

        # Generate improvement plan
        focus_areas = []
        goals = []

        if win_rate < 50:
            focus_areas.append("Overall win rate improvement")
            goals.append("Aim to reach 50% win rate by focusing on consistency")

        if problem_matchups:
            focus_areas.append(f"Improve vs {problem_matchups[0]['archetype']}")
            goals.append(f"Study the {problem_matchups[0]['archetype']} matchup and add tech cards")

        if total < 20:
            focus_areas.append("Build match history")
            goals.append("Log at least 20 matches for better insights")

        return {
            "status": "active",
            "overall_stats": {
                "total_matches": total,
                "win_rate": round(win_rate, 1),
                "wins": wins,
                "losses": losses,
            },
            "problem_matchups": problem_matchups[:3],
            "strong_matchups": strong_matchups[:3],
            "focus_areas": focus_areas or ["Keep practicing and logging matches"],
            "weekly_goals": goals or ["Continue tracking matches for insights"],
            "next_steps": [
                "Review your problem matchups in detail",
                "Watch tournament footage of top players with your deck",
                "Practice sequencing and optimal lines of play",
            ],
        }
