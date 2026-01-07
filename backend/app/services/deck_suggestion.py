"""Deck Suggestion Service - Suggest best decks for a given Pokémon"""
import json
import re
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
import structlog
import anthropic

from app.models.deck import Deck, DeckCard
from app.models.card import Card, CardType, CardSet
from app.models.meta import MetaSnapshot, MetaDeck
from app.schemas.deck import (
    DeckSuggestionRequest,
    DeckSuggestionResponse,
    SuggestedDeckInfo,
)
from app.services.card_api import DualCardApiService
from app.core.config import settings

logger = structlog.get_logger()


# Common set code mappings (Portuguese/regional codes to standard)
SET_CODE_MAPPING = {
    "PAF": "sv4pt5",   # Paldean Fates
    "OBF": "sv3",      # Obsidian Flames
    "MEW": "sv3pt5",   # 151/Mew
    "SVI": "sv1",      # Scarlet & Violet Base
    "PAL": "sv2",      # Paldea Evolved
    "TEF": "sv5",      # Temporal Forces
    "TWM": "sv6",      # Twilight Masquerade
    "SFA": "sv6pt5",   # Shrouded Fable
    "SCR": "sv7",      # Stellar Crown
    "SSP": "sv8",      # Surging Sparks
    "PRE": "sv8pt5",   # Prismatic Evolutions
}


class DeckSuggestionService:
    """Service for suggesting the best decks for a given Pokémon"""

    def __init__(self, db: AsyncSession, language: str = "en"):
        self.db = db
        self.language = language
        self.card_api = DualCardApiService(db, language)
        self.client = None
        if settings.anthropic_api_key:
            self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    async def suggest_deck(
        self,
        request: DeckSuggestionRequest
    ) -> DeckSuggestionResponse:
        """Suggest the best deck for a given Pokémon from a specific collection"""
        pokemon_name = request.pokemon_name.strip()
        set_code = self._normalize_set_code(request.set_code) if request.set_code else None

        # Step 1: Find the Pokémon card in database or API
        card_info = await self._find_pokemon_card(pokemon_name, set_code)

        if not card_info:
            return DeckSuggestionResponse(
                pokemon_name=pokemon_name,
                set_code=request.set_code,
                card_found=False,
                suggestions=[],
                ai_analysis=f"Could not find a Pokémon card matching '{pokemon_name}'"
                + (f" in set {request.set_code}" if request.set_code else "")
            )

        # Step 2: Find decks containing this Pokémon
        decks_with_pokemon = await self._find_decks_with_pokemon(
            pokemon_name,
            card_info.get("card_id"),
            request.format
        )

        # Step 3: Analyze meta data for archetypes featuring this Pokémon
        meta_archetypes = await self._find_meta_archetypes(pokemon_name)

        # Step 4: Build suggestions
        suggestions = await self._build_suggestions(
            pokemon_name,
            card_info,
            decks_with_pokemon,
            meta_archetypes
        )

        # Step 5: Get AI analysis
        ai_analysis = await self._get_ai_analysis(
            pokemon_name,
            card_info,
            suggestions
        )

        return DeckSuggestionResponse(
            pokemon_name=pokemon_name,
            set_code=request.set_code,
            card_found=True,
            card_info=card_info,
            suggestions=suggestions,
            ai_analysis=ai_analysis
        )

    def _normalize_set_code(self, set_code: str) -> str:
        """Normalize set code to standard format"""
        if not set_code:
            return set_code
        code_upper = set_code.upper().strip()
        return SET_CODE_MAPPING.get(code_upper, set_code.lower())

    async def _find_pokemon_card(
        self,
        pokemon_name: str,
        set_code: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Find a Pokémon card in database or via API"""
        # First, try to find in database
        query = select(Card).where(
            Card.card_type == CardType.POKEMON,
            Card.name.ilike(f"%{pokemon_name}%")
        )

        if set_code:
            # Join with CardSet to filter by set code
            query = query.join(Card.set).where(
                or_(
                    CardSet.code == set_code,
                    CardSet.code.ilike(f"%{set_code}%")
                )
            )

        query = query.options(selectinload(Card.set))
        result = await self.db.execute(query)
        cards = result.scalars().all()

        if cards:
            # Return the first match
            card = cards[0]
            return {
                "card_id": card.id,
                "ptcg_id": card.ptcg_id,
                "name": card.name,
                "hp": card.hp,
                "type": card.energy_type.value if card.energy_type else None,
                "subtype": card.subtype.value if card.subtype else None,
                "set_code": card.set.code if card.set else None,
                "set_name": card.set.name if card.set else None,
                "set_number": card.set_number,
                "abilities": card.abilities,
                "attacks": card.attacks,
                "image_small": card.image_small,
                "image_large": card.image_large,
            }

        # If not in database, try the API
        try:
            search_result = await self.card_api.search_cards(pokemon_name, page_size=10)
            if search_result.get("cards"):
                for api_card in search_result["cards"]:
                    # Check if it's a Pokémon
                    if api_card.get("supertype", "").lower() != "pokémon" and \
                       api_card.get("supertype", "").lower() != "pokemon":
                        continue

                    # Check set code if provided
                    card_set = api_card.get("set", {})
                    if set_code and card_set.get("id", "").lower() != set_code.lower():
                        continue

                    return {
                        "card_id": None,  # Not in database
                        "ptcg_id": api_card.get("id"),
                        "name": api_card.get("name"),
                        "hp": api_card.get("hp"),
                        "type": api_card.get("types", [None])[0] if api_card.get("types") else None,
                        "subtype": api_card.get("subtypes", [None])[0] if api_card.get("subtypes") else None,
                        "set_code": card_set.get("id"),
                        "set_name": card_set.get("name"),
                        "set_number": api_card.get("number"),
                        "abilities": api_card.get("abilities"),
                        "attacks": api_card.get("attacks"),
                        "image_small": api_card.get("images", {}).get("small"),
                        "image_large": api_card.get("images", {}).get("large"),
                    }
        except Exception as e:
            logger.warning(f"API search failed for {pokemon_name}: {e}")

        return None

    async def _find_decks_with_pokemon(
        self,
        pokemon_name: str,
        card_id: Optional[int],
        format_filter
    ) -> List[Deck]:
        """Find decks that contain the specified Pokémon"""
        # Query decks that contain cards matching the Pokémon name
        query = select(Deck).options(
            selectinload(Deck.cards).selectinload(DeckCard.card)
        ).where(Deck.is_active == True)

        if format_filter:
            query = query.where(Deck.format == format_filter)

        result = await self.db.execute(query)
        all_decks = result.scalars().unique().all()

        # Filter decks that contain the Pokémon
        matching_decks = []
        name_lower = pokemon_name.lower()

        for deck in all_decks:
            for dc in deck.cards:
                if dc.card:
                    # Match by card ID or name
                    if (card_id and dc.card.id == card_id) or \
                       (name_lower in dc.card.name.lower()):
                        matching_decks.append(deck)
                        break

        return matching_decks

    async def _find_meta_archetypes(
        self,
        pokemon_name: str
    ) -> List[MetaDeck]:
        """Find meta archetypes that feature this Pokémon"""
        # Get the latest meta snapshot
        query = select(MetaSnapshot).options(
            selectinload(MetaSnapshot.meta_decks)
        ).order_by(MetaSnapshot.snapshot_date.desc()).limit(1)

        result = await self.db.execute(query)
        snapshot = result.scalar_one_or_none()

        if not snapshot:
            return []

        # Find archetypes that mention this Pokémon
        name_lower = pokemon_name.lower()
        matching_archetypes = []

        for meta_deck in snapshot.meta_decks:
            archetype_lower = meta_deck.archetype.lower()

            # Check if Pokémon name is in archetype
            if name_lower in archetype_lower:
                matching_archetypes.append(meta_deck)
                continue

            # Check core cards
            if meta_deck.core_cards:
                for core_card in meta_deck.core_cards:
                    if name_lower in str(core_card).lower():
                        matching_archetypes.append(meta_deck)
                        break

        return matching_archetypes

    async def _build_suggestions(
        self,
        pokemon_name: str,
        card_info: Dict[str, Any],
        decks: List[Deck],
        meta_archetypes: List[MetaDeck]
    ) -> List[SuggestedDeckInfo]:
        """Build deck suggestions from found data"""
        suggestions = []

        # Add suggestions from meta archetypes (highest priority)
        for meta_deck in meta_archetypes:
            reasoning = self._generate_reasoning(
                pokemon_name,
                card_info,
                meta_deck=meta_deck
            )

            suggestions.append(SuggestedDeckInfo(
                archetype=meta_deck.archetype,
                meta_rank=meta_deck.rank,
                meta_share=meta_deck.meta_share,
                win_rate=meta_deck.win_rate,
                deck_id=meta_deck.sample_deck_id,
                core_cards=meta_deck.core_cards,
                matchup_summary=self._summarize_matchups(meta_deck.matchups),
                reasoning=reasoning
            ))

        # Add suggestions from user decks (if not already covered by meta)
        covered_archetypes = {s.archetype.lower() for s in suggestions}

        for deck in decks:
            archetype = deck.archetype or self._infer_archetype(deck, pokemon_name)
            if archetype.lower() in covered_archetypes:
                continue

            reasoning = self._generate_reasoning(
                pokemon_name,
                card_info,
                deck=deck
            )

            suggestions.append(SuggestedDeckInfo(
                archetype=archetype,
                meta_rank=None,
                meta_share=None,
                win_rate=None,
                deck_id=deck.id,
                core_cards=self._extract_core_cards(deck),
                matchup_summary=None,
                reasoning=reasoning
            ))

            covered_archetypes.add(archetype.lower())

        # If no suggestions found, provide generic suggestions based on Pokémon type
        if not suggestions:
            generic_suggestion = self._generate_generic_suggestion(
                pokemon_name,
                card_info
            )
            if generic_suggestion:
                suggestions.append(generic_suggestion)

        # Sort by meta rank (meta decks first), then by meta share
        suggestions.sort(
            key=lambda x: (
                x.meta_rank is None,  # Meta decks first
                x.meta_rank or 999,   # Then by rank
                -(x.meta_share or 0)  # Then by meta share
            )
        )

        return suggestions[:5]  # Return top 5 suggestions

    def _generate_reasoning(
        self,
        pokemon_name: str,
        card_info: Dict[str, Any],
        meta_deck: Optional[MetaDeck] = None,
        deck: Optional[Deck] = None
    ) -> str:
        """Generate reasoning for why this deck is suggested"""
        reasons = []

        if meta_deck:
            reasons.append(
                f"{pokemon_name} is a core Pokémon in the {meta_deck.archetype} archetype"
            )
            if meta_deck.meta_share:
                reasons.append(
                    f"which represents {meta_deck.meta_share:.1f}% of the current meta"
                )
            if meta_deck.win_rate:
                reasons.append(
                    f"with a {meta_deck.win_rate:.1f}% win rate"
                )
            if meta_deck.rank:
                reasons.append(f"(Rank #{meta_deck.rank} in meta)")
        elif deck:
            reasons.append(
                f"{pokemon_name} is featured in the '{deck.name}' deck"
            )
            if deck.archetype:
                reasons.append(f"following the {deck.archetype} archetype strategy")

        return ". ".join(reasons) if reasons else f"{pokemon_name} can be used in this deck."

    def _summarize_matchups(
        self,
        matchups: Optional[Dict[str, float]]
    ) -> Optional[Dict[str, Any]]:
        """Summarize matchup data"""
        if not matchups:
            return None

        favorable = []
        unfavorable = []

        for archetype, win_rate in matchups.items():
            if win_rate >= 55:
                favorable.append({"archetype": archetype, "win_rate": win_rate})
            elif win_rate <= 45:
                unfavorable.append({"archetype": archetype, "win_rate": win_rate})

        return {
            "favorable": sorted(favorable, key=lambda x: -x["win_rate"])[:3],
            "unfavorable": sorted(unfavorable, key=lambda x: x["win_rate"])[:3],
        }

    def _infer_archetype(self, deck: Deck, pokemon_name: str) -> str:
        """Infer deck archetype from its contents"""
        if deck.archetype:
            return deck.archetype

        # Find main attackers
        main_pokemon = []
        for dc in deck.cards:
            if dc.card and dc.card.card_type == CardType.POKEMON:
                if dc.card.subtype and dc.card.subtype.value in ["ex", "v", "vstar", "vmax"]:
                    main_pokemon.append((dc.card.name, dc.quantity))

        if main_pokemon:
            main_pokemon.sort(key=lambda x: x[1], reverse=True)
            return main_pokemon[0][0]

        return pokemon_name

    def _extract_core_cards(self, deck: Deck) -> List[str]:
        """Extract core cards from a deck"""
        core_cards = []
        for dc in deck.cards:
            if dc.card and dc.quantity >= 3:
                core_cards.append(dc.card.name)
        return core_cards[:10]

    def _generate_generic_suggestion(
        self,
        pokemon_name: str,
        card_info: Dict[str, Any]
    ) -> Optional[SuggestedDeckInfo]:
        """Generate a generic suggestion when no specific data is found"""
        pokemon_type = card_info.get("type")
        subtype = card_info.get("subtype")

        # Suggest archetypes based on Pokémon type
        type_archetypes = {
            "fire": "Charizard ex / Fire Control",
            "water": "Chien-Pao ex / Baxcalibur",
            "lightning": "Miraidon ex / Electric",
            "psychic": "Gardevoir ex / Psychic",
            "fighting": "Ancient Box / Fighting",
            "darkness": "Roaring Moon ex / Dark",
            "metal": "Gholdengo ex / Metal",
            "grass": "Sceptile / Grass",
            "dragon": "Giratina VSTAR / Dragon",
            "colorless": "Lugia VSTAR / Colorless",
        }

        if pokemon_type:
            archetype = type_archetypes.get(pokemon_type.lower())
            if archetype:
                return SuggestedDeckInfo(
                    archetype=archetype,
                    meta_rank=None,
                    meta_share=None,
                    win_rate=None,
                    deck_id=None,
                    core_cards=None,
                    matchup_summary=None,
                    reasoning=f"{pokemon_name} is a {pokemon_type}-type Pokémon. "
                    f"Consider building around {archetype} archetype which synergizes with "
                    f"{pokemon_type}-type attackers. Check if {pokemon_name} can fit the strategy."
                )

        return None

    async def _get_ai_analysis(
        self,
        pokemon_name: str,
        card_info: Dict[str, Any],
        suggestions: List[SuggestedDeckInfo]
    ) -> Optional[str]:
        """Get AI-powered analysis for deck suggestions"""
        if not self.client:
            return None

        # Build context
        card_details = f"""
Pokémon: {card_info.get('name')}
Type: {card_info.get('type', 'Unknown')}
Subtype: {card_info.get('subtype', 'Unknown')}
HP: {card_info.get('hp', 'Unknown')}
Set: {card_info.get('set_name', 'Unknown')} ({card_info.get('set_code', '')})
"""

        if card_info.get("abilities"):
            abilities = card_info["abilities"]
            if isinstance(abilities, list):
                ability_text = "\n".join([
                    f"  - {ab.get('name', 'Ability')}: {ab.get('text', '')}"
                    for ab in abilities
                ])
                card_details += f"\nAbilities:\n{ability_text}"

        if card_info.get("attacks"):
            attacks = card_info["attacks"]
            if isinstance(attacks, list):
                attack_text = "\n".join([
                    f"  - {atk.get('name', 'Attack')}: {atk.get('damage', '')} - {atk.get('text', '')}"
                    for atk in attacks
                ])
                card_details += f"\nAttacks:\n{attack_text}"

        suggestions_text = ""
        for i, sug in enumerate(suggestions, 1):
            suggestions_text += f"""
{i}. {sug.archetype}
   - Meta Rank: {sug.meta_rank or 'N/A'}
   - Meta Share: {f'{sug.meta_share:.1f}%' if sug.meta_share else 'N/A'}
   - Win Rate: {f'{sug.win_rate:.1f}%' if sug.win_rate else 'N/A'}
"""

        prompt = f"""Analyze this Pokémon TCG card and provide insights on how to best use it in competitive play:

{card_details}

Current deck suggestions:
{suggestions_text if suggestions_text else "No specific deck archetypes found in the current meta."}

Provide a concise analysis (2-3 paragraphs) covering:
1. The card's competitive viability and strengths
2. Which deck archetype(s) would best utilize this card
3. Key synergies and partner cards to consider

Be specific and practical. If the card is not competitively viable, explain why and suggest alternatives."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            return None
