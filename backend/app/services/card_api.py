"""Dual Card API Service - TCGdex (Primary) + Pokemon TCG API (Fallback)

TCGdex provides multilingual support, TCG Live/Pocket integration.
Pokemon TCG API provides complete English data and prices as fallback.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from tcgdex import TCGdex, Language
from pokemontcgsdk import Card as PTCGCard, Set as PTCGSet, RestClient

from app.models.card import Card, CardSet, CardType, CardSubtype, EnergyType
from app.core.config import settings

logger = structlog.get_logger()

# Configure Pokemon TCG SDK
RestClient.configure(settings.pokemon_tcg_api_key)

# Language mapping for TCGdex
LANGUAGE_MAP = {
    "en": Language.EN,
    "fr": Language.FR,
    "de": Language.DE,
    "es": Language.ES,
    "it": Language.IT,
    "pt": Language.PT,
    "ja": Language.JA,
    "zh-tw": Language.ZH_TW,
    "id": Language.ID,
    "th": Language.TH,
}


class DualCardApiService:
    """Dual API service using TCGdex (primary) and Pokemon TCG API (fallback)"""

    def __init__(self, db: AsyncSession, language: str = None):
        self.db = db
        self.language = language or settings.default_language
        self._tcgdex = None

    @property
    def tcgdex(self) -> TCGdex:
        """Lazy-load TCGdex client with current language"""
        if self._tcgdex is None:
            lang = LANGUAGE_MAP.get(self.language, Language.EN)
            self._tcgdex = TCGdex(lang)
        return self._tcgdex

    def set_language(self, language: str):
        """Change the language for subsequent requests"""
        if language in LANGUAGE_MAP:
            self.language = language
            self._tcgdex = None  # Reset to recreate with new language

    # =====================
    # Card Search Methods
    # =====================

    async def search_cards(
        self,
        query: str,
        page: int = 1,
        page_size: int = 50,
        use_fallback: bool = True
    ) -> Dict[str, Any]:
        """Search cards with TCGdex primary, Pokemon TCG API fallback"""
        try:
            # Try TCGdex first (async)
            cards = await self.tcgdex.card.list()

            # Filter by name (TCGdex returns all, we filter)
            query_lower = query.lower()
            filtered = [
                c for c in cards
                if query_lower in (c.name or "").lower()
            ]

            # Paginate
            start = (page - 1) * page_size
            end = start + page_size
            page_cards = filtered[start:end]

            if page_cards:
                return {
                    "source": "tcgdex",
                    "language": self.language,
                    "cards": [self._tcgdex_card_to_dict(c) for c in page_cards],
                    "total": len(filtered),
                    "page": page,
                    "page_size": page_size,
                }
        except Exception as e:
            logger.warning(f"TCGdex search failed: {e}")

        # Fallback to Pokemon TCG API
        if use_fallback:
            try:
                ptcg_cards = PTCGCard.where(q=f'name:{query}*', page=page, pageSize=page_size)
                return {
                    "source": "pokemon_tcg_api",
                    "language": "en",
                    "cards": [self._ptcg_card_to_dict(c) for c in ptcg_cards],
                    "total": len(ptcg_cards),
                    "page": page,
                    "page_size": page_size,
                }
            except Exception as e:
                logger.error(f"Pokemon TCG API fallback failed: {e}")

        return {"source": "none", "cards": [], "total": 0, "page": page, "page_size": page_size}

    async def get_card(self, card_id: str, use_fallback: bool = True) -> Optional[Dict[str, Any]]:
        """Get a specific card by ID"""
        try:
            # Try TCGdex first
            card = await self.tcgdex.card.get(card_id)
            if card:
                return {
                    "source": "tcgdex",
                    "language": self.language,
                    "card": self._tcgdex_card_to_dict(card),
                }
        except Exception as e:
            logger.warning(f"TCGdex get card failed: {e}")

        # Fallback
        if use_fallback:
            try:
                card = PTCGCard.find(card_id)
                if card:
                    return {
                        "source": "pokemon_tcg_api",
                        "language": "en",
                        "card": self._ptcg_card_to_dict(card),
                    }
            except Exception as e:
                logger.error(f"Pokemon TCG API fallback failed: {e}")

        return None

    # =====================
    # Set Methods
    # =====================

    async def get_sets(self, use_fallback: bool = True) -> Dict[str, Any]:
        """Get all card sets"""
        try:
            sets = await self.tcgdex.set.list()
            if sets:
                return {
                    "source": "tcgdex",
                    "language": self.language,
                    "sets": [self._tcgdex_set_to_dict(s) for s in sets],
                }
        except Exception as e:
            logger.warning(f"TCGdex get sets failed: {e}")

        if use_fallback:
            try:
                sets = PTCGSet.all()
                return {
                    "source": "pokemon_tcg_api",
                    "language": "en",
                    "sets": [self._ptcg_set_to_dict(s) for s in sets],
                }
            except Exception as e:
                logger.error(f"Pokemon TCG API fallback failed: {e}")

        return {"source": "none", "sets": []}

    async def get_set(self, set_id: str, use_fallback: bool = True) -> Optional[Dict[str, Any]]:
        """Get a specific set by ID"""
        try:
            set_data = await self.tcgdex.set.get(set_id)
            if set_data:
                return {
                    "source": "tcgdex",
                    "language": self.language,
                    "set": self._tcgdex_set_to_dict(set_data),
                }
        except Exception as e:
            logger.warning(f"TCGdex get set failed: {e}")

        if use_fallback:
            try:
                set_data = PTCGSet.find(set_id)
                if set_data:
                    return {
                        "source": "pokemon_tcg_api",
                        "language": "en",
                        "set": self._ptcg_set_to_dict(set_data),
                    }
            except Exception as e:
                logger.error(f"Pokemon TCG API fallback failed: {e}")

        return None

    async def get_set_cards(
        self,
        set_id: str,
        page: int = 1,
        page_size: int = 100,
        use_fallback: bool = True
    ) -> Dict[str, Any]:
        """Get all cards from a specific set"""
        try:
            # TCGdex: Get set with cards
            set_data = await self.tcgdex.set.get(set_id)
            if set_data and hasattr(set_data, 'cards') and set_data.cards:
                cards = set_data.cards
                start = (page - 1) * page_size
                end = start + page_size
                page_cards = cards[start:end]

                return {
                    "source": "tcgdex",
                    "language": self.language,
                    "set_id": set_id,
                    "cards": [self._tcgdex_card_to_dict(c) for c in page_cards],
                    "total": len(cards),
                    "page": page,
                    "page_size": page_size,
                }
        except Exception as e:
            logger.warning(f"TCGdex get set cards failed: {e}")

        if use_fallback:
            try:
                cards = PTCGCard.where(q=f'set.id:{set_id}', page=page, pageSize=page_size)
                return {
                    "source": "pokemon_tcg_api",
                    "language": "en",
                    "set_id": set_id,
                    "cards": [self._ptcg_card_to_dict(c) for c in cards],
                    "total": len(cards),
                    "page": page,
                    "page_size": page_size,
                }
            except Exception as e:
                logger.error(f"Pokemon TCG API fallback failed: {e}")

        return {"source": "none", "set_id": set_id, "cards": [], "total": 0, "page": page, "page_size": page_size}

    # =====================
    # Sync to Database
    # =====================

    async def sync_card_to_db(self, card_data: Dict[str, Any]) -> Optional[Card]:
        """Sync a card from API response to database"""
        card_id = card_data.get("id")
        if not card_id:
            return None

        # Check if exists
        result = await self.db.execute(
            select(Card).where(Card.ptcg_id == card_id)
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing

        # Get or create set
        card_set = None
        set_data = card_data.get("set")
        if set_data:
            result = await self.db.execute(
                select(CardSet).where(CardSet.code == set_data.get("id"))
            )
            card_set = result.scalar_one_or_none()

            if not card_set:
                card_set = CardSet(
                    code=set_data.get("id"),
                    name=set_data.get("name"),
                    series=set_data.get("series"),
                    logo_url=set_data.get("logo_url"),
                    symbol_url=set_data.get("symbol_url"),
                )
                self.db.add(card_set)
                await self.db.flush()

        # Parse types
        card_type = self._parse_card_type(card_data.get("supertype"))
        subtype = self._parse_subtype(card_data.get("subtypes", []))
        energy_type = self._parse_energy_type(card_data.get("types", []))

        # Create card
        card = Card(
            ptcg_id=card_id,
            name=card_data.get("name"),
            card_type=card_type,
            subtype=subtype,
            set_id=card_set.id if card_set else None,
            set_number=card_data.get("number"),
            hp=self._parse_int(card_data.get("hp")),
            energy_type=energy_type,
            abilities=card_data.get("abilities"),
            attacks=card_data.get("attacks"),
            image_small=card_data.get("images", {}).get("small"),
            image_large=card_data.get("images", {}).get("large"),
            rarity=card_data.get("rarity"),
            artist=card_data.get("artist"),
            regulation_mark=card_data.get("regulation_mark"),
            is_standard_legal=card_data.get("legalities", {}).get("standard") == "Legal",
            is_expanded_legal=card_data.get("legalities", {}).get("expanded") == "Legal",
        )

        self.db.add(card)
        await self.db.flush()
        return card

    # =====================
    # Conversion Helpers
    # =====================

    def _tcgdex_card_to_dict(self, card) -> Dict[str, Any]:
        """Convert TCGdex card to standard dict format"""
        images = {}
        if hasattr(card, 'image'):
            images["small"] = card.image
            images["large"] = card.image

        return {
            "id": card.id if hasattr(card, 'id') else None,
            "name": card.name if hasattr(card, 'name') else None,
            "supertype": card.category if hasattr(card, 'category') else None,
            "subtypes": [card.stage] if hasattr(card, 'stage') and card.stage else [],
            "types": [card.types[0]] if hasattr(card, 'types') and card.types else [],
            "hp": card.hp if hasattr(card, 'hp') else None,
            "number": card.localId if hasattr(card, 'localId') else None,
            "rarity": card.rarity if hasattr(card, 'rarity') else None,
            "artist": card.illustrator if hasattr(card, 'illustrator') else None,
            "regulation_mark": card.regulationMark if hasattr(card, 'regulationMark') else None,
            "set": {
                "id": card.set.id if hasattr(card, 'set') and card.set else None,
                "name": card.set.name if hasattr(card, 'set') and card.set else None,
            } if hasattr(card, 'set') and card.set else None,
            "images": images,
            "attacks": self._parse_tcgdex_attacks(card.attacks if hasattr(card, 'attacks') else None),
            "abilities": self._parse_tcgdex_abilities(card.abilities if hasattr(card, 'abilities') else None),
            "legalities": {
                "standard": "Legal" if hasattr(card, 'legal') and card.legal and card.legal.standard else None,
                "expanded": "Legal" if hasattr(card, 'legal') and card.legal and card.legal.expanded else None,
            } if hasattr(card, 'legal') and card.legal else {},
        }

    def _ptcg_card_to_dict(self, card) -> Dict[str, Any]:
        """Convert Pokemon TCG API card to standard dict format"""
        return {
            "id": card.id,
            "name": card.name,
            "supertype": card.supertype,
            "subtypes": card.subtypes or [],
            "types": card.types or [],
            "hp": card.hp,
            "number": card.number,
            "rarity": card.rarity,
            "artist": card.artist,
            "regulation_mark": card.regulationMark,
            "set": {
                "id": card.set.id,
                "name": card.set.name,
                "series": card.set.series,
                "logo_url": card.set.images.logo if card.set.images else None,
                "symbol_url": card.set.images.symbol if card.set.images else None,
            } if card.set else None,
            "images": {
                "small": card.images.small if card.images else None,
                "large": card.images.large if card.images else None,
            } if card.images else {},
            "attacks": self._parse_ptcg_attacks(card.attacks),
            "abilities": self._parse_ptcg_abilities(card.abilities),
            "legalities": {
                "standard": getattr(card.legalities, 'standard', None),
                "expanded": getattr(card.legalities, 'expanded', None),
            } if card.legalities else {},
        }

    def _tcgdex_set_to_dict(self, set_data) -> Dict[str, Any]:
        """Convert TCGdex set to standard dict format"""
        return {
            "id": set_data.id if hasattr(set_data, 'id') else None,
            "name": set_data.name if hasattr(set_data, 'name') else None,
            "series": set_data.serie.name if hasattr(set_data, 'serie') and set_data.serie else None,
            "release_date": set_data.releaseDate if hasattr(set_data, 'releaseDate') else None,
            "total_cards": set_data.cardCount.total if hasattr(set_data, 'cardCount') and set_data.cardCount else None,
            "logo_url": set_data.logo if hasattr(set_data, 'logo') else None,
            "symbol_url": set_data.symbol if hasattr(set_data, 'symbol') else None,
        }

    def _ptcg_set_to_dict(self, set_data) -> Dict[str, Any]:
        """Convert Pokemon TCG API set to standard dict format"""
        return {
            "id": set_data.id,
            "name": set_data.name,
            "series": set_data.series,
            "release_date": set_data.releaseDate,
            "total_cards": set_data.total,
            "logo_url": set_data.images.logo if set_data.images else None,
            "symbol_url": set_data.images.symbol if set_data.images else None,
        }

    def _parse_tcgdex_attacks(self, attacks) -> Optional[List[Dict]]:
        """Parse TCGdex attacks"""
        if not attacks:
            return None
        return [
            {
                "name": atk.name if hasattr(atk, 'name') else None,
                "cost": atk.cost if hasattr(atk, 'cost') else [],
                "damage": atk.damage if hasattr(atk, 'damage') else None,
                "text": atk.effect if hasattr(atk, 'effect') else None,
            }
            for atk in attacks
        ]

    def _parse_tcgdex_abilities(self, abilities) -> Optional[List[Dict]]:
        """Parse TCGdex abilities"""
        if not abilities:
            return None
        return [
            {
                "name": ab.name if hasattr(ab, 'name') else None,
                "text": ab.effect if hasattr(ab, 'effect') else None,
                "type": ab.type if hasattr(ab, 'type') else None,
            }
            for ab in abilities
        ]

    def _parse_ptcg_attacks(self, attacks) -> Optional[List[Dict]]:
        """Parse Pokemon TCG API attacks"""
        if not attacks:
            return None
        return [
            {
                "name": atk.name,
                "cost": atk.cost,
                "damage": atk.damage,
                "text": atk.text,
                "convertedEnergyCost": atk.convertedEnergyCost,
            }
            for atk in attacks
        ]

    def _parse_ptcg_abilities(self, abilities) -> Optional[List[Dict]]:
        """Parse Pokemon TCG API abilities"""
        if not abilities:
            return None
        return [
            {
                "name": ab.name,
                "text": ab.text,
                "type": ab.type,
            }
            for ab in abilities
        ]

    def _parse_card_type(self, supertype: str) -> CardType:
        """Parse card type from supertype"""
        if not supertype:
            return CardType.POKEMON
        supertype_lower = supertype.lower()
        if "pokemon" in supertype_lower or "pokémon" in supertype_lower:
            return CardType.POKEMON
        elif "trainer" in supertype_lower:
            return CardType.TRAINER
        elif "energy" in supertype_lower:
            return CardType.ENERGY
        return CardType.POKEMON

    def _parse_subtype(self, subtypes: List[str]) -> Optional[CardSubtype]:
        """Parse subtype from list"""
        if not subtypes:
            return None
        subtype_str = subtypes[0].lower().replace(" ", "").replace("-", "")
        subtype_map = {
            "basic": CardSubtype.BASIC,
            "stage1": CardSubtype.STAGE1,
            "stage2": CardSubtype.STAGE2,
            "vstar": CardSubtype.VSTAR,
            "vmax": CardSubtype.VMAX,
            "v": CardSubtype.V,
            "ex": CardSubtype.EX,
            "gx": CardSubtype.GX,
            "radiant": CardSubtype.RADIANT,
            "item": CardSubtype.ITEM,
            "supporter": CardSubtype.SUPPORTER,
            "stadium": CardSubtype.STADIUM,
            "tool": CardSubtype.TOOL,
        }
        return subtype_map.get(subtype_str)

    def _parse_energy_type(self, types: List[str]) -> Optional[EnergyType]:
        """Parse energy type from list"""
        if not types:
            return None
        energy_str = types[0].lower()
        energy_map = {
            "grass": EnergyType.GRASS,
            "fire": EnergyType.FIRE,
            "water": EnergyType.WATER,
            "lightning": EnergyType.LIGHTNING,
            "psychic": EnergyType.PSYCHIC,
            "fighting": EnergyType.FIGHTING,
            "darkness": EnergyType.DARKNESS,
            "metal": EnergyType.METAL,
            "dragon": EnergyType.DRAGON,
            "colorless": EnergyType.COLORLESS,
            "fairy": EnergyType.FAIRY,
        }
        return energy_map.get(energy_str)

    def _parse_int(self, value) -> Optional[int]:
        """Safely parse integer"""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
