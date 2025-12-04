"""Export service for decks, tournaments, and match data"""
import json
import csv
import io
from datetime import datetime
from typing import Optional, Dict, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.deck import Deck, DeckCard
from app.models.match import Match, MatchResult
from app.models.tournament import Tournament, TournamentRound
from app.models.card import Card


class ExportService:
    """Service for exporting data in various formats"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================== DECK EXPORTS ====================

    async def export_deck_text(self, deck_id: int) -> str:
        """Export deck as plain text list"""
        deck = await self._get_deck_with_cards(deck_id)
        if not deck:
            return ""

        lines = [f"Deck: {deck.name}"]
        if deck.archetype:
            lines.append(f"Archetype: {deck.archetype}")
        lines.append(f"Format: {deck.format.value.title()}")
        lines.append("")

        # Group cards by type
        pokemon = []
        trainers = []
        energy = []

        for dc in deck.cards:
            card = dc.card
            entry = f"{dc.quantity} {card.name}"
            if card.set:
                entry += f" {card.set.code} {card.set_number}"

            if card.card_type.value == "pokemon":
                pokemon.append(entry)
            elif card.card_type.value == "energy":
                energy.append(entry)
            else:
                trainers.append(entry)

        if pokemon:
            lines.append(f"Pokemon: {len(pokemon)}")
            lines.extend(pokemon)
            lines.append("")

        if trainers:
            lines.append(f"Trainers: {len(trainers)}")
            lines.extend(trainers)
            lines.append("")

        if energy:
            lines.append(f"Energy: {len(energy)}")
            lines.extend(energy)
            lines.append("")

        lines.append(f"Total Cards: {sum(dc.quantity for dc in deck.cards)}")

        return "\n".join(lines)

    async def export_deck_ptcgo(self, deck_id: int) -> str:
        """Export deck in Pokemon TCG Online format"""
        deck = await self._get_deck_with_cards(deck_id)
        if not deck:
            return ""

        lines = [f"****** Pokémon Trading Card Game Deck List ******"]
        lines.append("")
        lines.append(f"##Pokémon - {deck.pokemon_count}")

        # Group by type
        pokemon = []
        trainers = []
        energy = []

        for dc in deck.cards:
            card = dc.card
            set_code = card.set.code.upper() if card.set else "XXX"
            entry = f"* {dc.quantity} {card.name} {set_code} {card.set_number or 'XX'}"

            if card.card_type.value == "pokemon":
                pokemon.append(entry)
            elif card.card_type.value == "energy":
                energy.append(entry)
            else:
                trainers.append(entry)

        lines.extend(pokemon)
        lines.append("")
        lines.append(f"##Trainer Cards - {deck.trainer_count}")
        lines.extend(trainers)
        lines.append("")
        lines.append(f"##Energy - {deck.energy_count}")
        lines.extend(energy)
        lines.append("")
        lines.append(f"Total Cards - {deck.total_cards}")

        return "\n".join(lines)

    async def export_deck_json(self, deck_id: int) -> str:
        """Export deck as JSON"""
        deck = await self._get_deck_with_cards(deck_id)
        if not deck:
            return "{}"

        cards = []
        for dc in deck.cards:
            card = dc.card
            cards.append({
                "name": card.name,
                "quantity": dc.quantity,
                "card_type": card.card_type.value,
                "set_code": card.set.code if card.set else None,
                "set_number": card.set_number,
                "card_id": card.external_id,
            })

        data = {
            "name": deck.name,
            "archetype": deck.archetype,
            "format": deck.format.value,
            "description": deck.description,
            "pokemon_count": deck.pokemon_count,
            "trainer_count": deck.trainer_count,
            "energy_count": deck.energy_count,
            "total_cards": deck.total_cards,
            "cards": cards,
            "exported_at": datetime.utcnow().isoformat(),
        }

        return json.dumps(data, indent=2)

    async def export_deck_limitless(self, deck_id: int) -> str:
        """Export deck in Limitless TCG format"""
        deck = await self._get_deck_with_cards(deck_id)
        if not deck:
            return ""

        lines = []
        for dc in deck.cards:
            card = dc.card
            set_code = card.set.code.lower() if card.set else "xxx"
            # Limitless format: count name set number
            lines.append(f"{dc.quantity} {card.name} {set_code} {card.set_number or 'XX'}")

        return "\n".join(lines)

    # ==================== TOURNAMENT EXPORTS ====================

    async def export_tournament_report(self, tournament_id: int, user_id: int) -> Dict[str, Any]:
        """Export complete tournament report"""
        query = select(Tournament).options(
            selectinload(Tournament.rounds),
            selectinload(Tournament.deck)
        ).where(
            Tournament.id == tournament_id,
            Tournament.user_id == user_id
        )
        result = await self.db.execute(query)
        tournament = result.scalar_one_or_none()

        if not tournament:
            return {}

        rounds_data = []
        for r in sorted(tournament.rounds, key=lambda x: x.round_number):
            rounds_data.append({
                "round": r.round_number,
                "is_top_cut": r.is_top_cut,
                "top_cut_round": r.top_cut_round,
                "opponent": r.opponent_name or "Unknown",
                "opponent_deck": r.opponent_archetype or r.opponent_deck or "Unknown",
                "result": r.result.value,
                "games": f"{r.games_won}-{r.games_lost}",
                "notes": r.notes,
            })

        wins = sum(1 for r in tournament.rounds if r.result.value in ["win", "bye"])
        losses = sum(1 for r in tournament.rounds if r.result.value == "loss")
        ties = sum(1 for r in tournament.rounds if r.result.value in ["tie", "id"])

        report = {
            "tournament": {
                "name": tournament.name,
                "date": tournament.event_date.isoformat(),
                "location": tournament.location,
                "format": tournament.format.value,
                "type": tournament.tournament_type.value,
                "players": tournament.total_players,
            },
            "deck": {
                "name": tournament.deck.name if tournament.deck else None,
                "archetype": tournament.deck_archetype,
            },
            "results": {
                "record": f"{wins}-{losses}-{ties}",
                "final_standing": tournament.final_standing,
                "championship_points": tournament.championship_points,
            },
            "rounds": rounds_data,
            "notes": tournament.notes,
            "exported_at": datetime.utcnow().isoformat(),
        }

        return report

    async def export_tournament_csv(self, tournament_id: int, user_id: int) -> str:
        """Export tournament rounds as CSV"""
        query = select(Tournament).options(
            selectinload(Tournament.rounds)
        ).where(
            Tournament.id == tournament_id,
            Tournament.user_id == user_id
        )
        result = await self.db.execute(query)
        tournament = result.scalar_one_or_none()

        if not tournament:
            return ""

        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            "Round", "Top Cut", "Opponent", "Opponent Deck",
            "Result", "Games Won", "Games Lost", "Notes"
        ])

        # Data
        for r in sorted(tournament.rounds, key=lambda x: x.round_number):
            writer.writerow([
                r.round_number,
                r.top_cut_round if r.is_top_cut else "",
                r.opponent_name or "",
                r.opponent_archetype or r.opponent_deck or "",
                r.result.value.upper(),
                r.games_won,
                r.games_lost,
                r.notes or "",
            ])

        return output.getvalue()

    # ==================== MATCH HISTORY EXPORTS ====================

    async def export_matches_csv(
        self, user_id: int, deck_id: Optional[int] = None
    ) -> str:
        """Export match history as CSV"""
        query = select(Match).options(
            selectinload(Match.deck)
        ).order_by(Match.played_at.desc())

        if deck_id:
            query = query.where(Match.deck_id == deck_id)

        result = await self.db.execute(query)
        matches = result.scalars().all()

        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            "Date", "Deck", "Opponent Deck", "Result",
            "Games Won", "Games Lost", "Went First", "Source", "Notes"
        ])

        # Data
        for m in matches:
            writer.writerow([
                m.played_at.isoformat() if m.played_at else "",
                m.deck.name if m.deck else "",
                m.opponent_archetype or m.opponent_deck or "",
                m.result.value.upper() if m.result else "",
                m.games_won or 0,
                m.games_lost or 0,
                "Yes" if m.went_first else "No" if m.went_first is False else "",
                m.source or "",
                m.notes or "",
            ])

        return output.getvalue()

    async def export_matches_json(
        self, user_id: int, deck_id: Optional[int] = None
    ) -> str:
        """Export match history as JSON"""
        query = select(Match).options(
            selectinload(Match.deck)
        ).order_by(Match.played_at.desc())

        if deck_id:
            query = query.where(Match.deck_id == deck_id)

        result = await self.db.execute(query)
        matches = result.scalars().all()

        data = []
        for m in matches:
            data.append({
                "date": m.played_at.isoformat() if m.played_at else None,
                "deck": m.deck.name if m.deck else None,
                "deck_archetype": m.deck.archetype if m.deck else None,
                "opponent_deck": m.opponent_archetype or m.opponent_deck,
                "result": m.result.value if m.result else None,
                "games_won": m.games_won,
                "games_lost": m.games_lost,
                "went_first": m.went_first,
                "source": m.source,
                "notes": m.notes,
            })

        return json.dumps({
            "matches": data,
            "total": len(data),
            "exported_at": datetime.utcnow().isoformat(),
        }, indent=2)

    # ==================== STATS EXPORTS ====================

    async def export_stats_summary(self, user_id: int) -> Dict[str, Any]:
        """Export comprehensive stats summary"""
        # Get all matches
        matches_query = select(Match).options(selectinload(Match.deck))
        matches_result = await self.db.execute(matches_query)
        matches = matches_result.scalars().all()

        # Get all tournaments
        tournaments_query = select(Tournament).where(
            Tournament.user_id == user_id
        )
        tournaments_result = await self.db.execute(tournaments_query)
        tournaments = tournaments_result.scalars().all()

        # Calculate match stats
        total_matches = len(matches)
        wins = sum(1 for m in matches if m.result == MatchResult.WIN)
        losses = sum(1 for m in matches if m.result == MatchResult.LOSS)

        # Deck performance
        deck_stats = {}
        for m in matches:
            if m.deck:
                if m.deck.id not in deck_stats:
                    deck_stats[m.deck.id] = {
                        "name": m.deck.name,
                        "archetype": m.deck.archetype,
                        "wins": 0,
                        "losses": 0,
                    }
                if m.result == MatchResult.WIN:
                    deck_stats[m.deck.id]["wins"] += 1
                elif m.result == MatchResult.LOSS:
                    deck_stats[m.deck.id]["losses"] += 1

        # Tournament stats
        total_tournaments = len(tournaments)
        total_cp = sum(t.championship_points for t in tournaments)
        best_finish = min((t.final_standing for t in tournaments if t.final_standing), default=None)

        return {
            "matches": {
                "total": total_matches,
                "wins": wins,
                "losses": losses,
                "win_rate": round(wins / (wins + losses) * 100, 1) if (wins + losses) > 0 else 0,
            },
            "tournaments": {
                "total": total_tournaments,
                "championship_points": total_cp,
                "best_finish": best_finish,
            },
            "decks": list(deck_stats.values()),
            "exported_at": datetime.utcnow().isoformat(),
        }

    # ==================== HELPER METHODS ====================

    async def _get_deck_with_cards(self, deck_id: int) -> Optional[Deck]:
        """Get deck with cards loaded"""
        query = select(Deck).options(
            selectinload(Deck.cards).selectinload(DeckCard.card).selectinload(Card.set)
        ).where(Deck.id == deck_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
