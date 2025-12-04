"""Card Sync Service - Sync cards from Pokemon TCG API using httpx"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog
import httpx

from app.models.card import Card, CardSet, CardType, CardSubtype, EnergyType
from app.core.config import settings

logger = structlog.get_logger()

# Pokemon TCG API v2 base URL
POKEMON_TCG_API_URL = "https://api.pokemontcg.io/v2"


class CardSyncService:
    """Service for syncing cards from Pokemon TCG API"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.headers = {
            "X-Api-Key": settings.pokemon_tcg_api_key
        }

    async def _api_get(self, endpoint: str, params: dict = None) -> dict:
        """Make a GET request to the Pokemon TCG API"""
        async with httpx.AsyncClient() as client:
            url = f"{POKEMON_TCG_API_URL}/{endpoint}"
            response = await client.get(url, headers=self.headers, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()

    async def sync_all_sets(self) -> dict:
        """Sync all card sets from the API"""
        try:
            data = await self._api_get("sets")
            sets = data.get("data", [])
            synced = 0
            skipped = 0

            for ptcg_set in sets:
                result = await self._sync_set(ptcg_set)
                if result:
                    synced += 1
                else:
                    skipped += 1

            logger.info(f"Synced {synced} sets, skipped {skipped}")
            return {"success": True, "synced": synced, "skipped": skipped}

        except Exception as e:
            error_msg = repr(e)
            logger.error(f"Failed to sync sets: {error_msg}")
            return {"success": False, "error": error_msg}

    async def sync_set_cards(self, set_code: str) -> dict:
        """Sync all cards from a specific set"""
        try:
            data = await self._api_get("cards", params={"q": f"set.id:{set_code}", "pageSize": 250})
            cards = data.get("data", [])
            synced = 0
            skipped = 0
            errors = []

            for ptcg_card in cards:
                try:
                    result = await self._sync_card(ptcg_card)
                    if result:
                        synced += 1
                    else:
                        skipped += 1
                except Exception as e:
                    errors.append(f"{ptcg_card.get('name', 'Unknown')}: {repr(e)}")
                    skipped += 1

            logger.info(f"Synced {synced} cards from set {set_code}, skipped {skipped}")
            return {
                "success": True,
                "synced": synced,
                "skipped": skipped,
                "errors": errors[:10]
            }

        except Exception as e:
            error_msg = repr(e)
            logger.error(f"Failed to sync cards from set {set_code}: {error_msg}")
            return {"success": False, "error": error_msg}

    async def sync_standard_legal_cards(self) -> dict:
        """Sync all standard legal cards"""
        try:
            # Get standard legal cards (paginated)
            all_cards = []
            page = 1
            page_size = 250

            while True:
                data = await self._api_get("cards", params={
                    "q": "legalities.standard:legal",
                    "page": page,
                    "pageSize": page_size
                })
                cards = data.get("data", [])
                if not cards:
                    break
                all_cards.extend(cards)

                # Check if there are more pages
                total_count = data.get("totalCount", 0)
                if len(all_cards) >= total_count:
                    break
                page += 1

                # Safety limit
                if page > 20:
                    break

            synced = 0
            skipped = 0
            errors = []

            for ptcg_card in all_cards:
                try:
                    result = await self._sync_card(ptcg_card, is_standard=True)
                    if result:
                        synced += 1
                    else:
                        skipped += 1
                except Exception as e:
                    errors.append(f"{ptcg_card.get('name', 'Unknown')}: {repr(e)}")
                    skipped += 1

            logger.info(f"Synced {synced} standard legal cards, skipped {skipped}")
            return {
                "success": True,
                "synced": synced,
                "skipped": skipped,
                "errors": errors[:10]
            }

        except Exception as e:
            error_msg = repr(e)
            logger.error(f"Failed to sync standard cards: {error_msg}")
            return {"success": False, "error": error_msg}

    async def search_cards(self, query: str, page: int = 1, page_size: int = 50) -> List[dict]:
        """Search cards from the API"""
        try:
            data = await self._api_get("cards", params={
                "q": f"name:{query}*",
                "page": page,
                "pageSize": page_size
            })
            return [self._card_to_dict(card) for card in data.get("data", [])]
        except Exception as e:
            logger.error(f"Failed to search cards: {repr(e)}")
            return []

    async def get_card_by_id(self, card_id: str) -> Optional[dict]:
        """Get a specific card by ID from the API"""
        try:
            data = await self._api_get(f"cards/{card_id}")
            card = data.get("data")
            if card:
                return self._card_to_dict(card)
            return None
        except Exception as e:
            logger.error(f"Failed to get card {card_id}: {repr(e)}")
            return None

    async def _sync_set(self, ptcg_set: dict) -> Optional[CardSet]:
        """Sync a single set"""
        set_id = ptcg_set.get("id")

        # Check if set already exists
        result = await self.db.execute(
            select(CardSet).where(CardSet.code == set_id)
        )
        existing = result.scalar_one_or_none()

        images = ptcg_set.get("images", {})

        if existing:
            # Update existing set
            existing.name = ptcg_set.get("name")
            existing.series = ptcg_set.get("series")
            existing.release_date = ptcg_set.get("releaseDate")
            existing.total_cards = ptcg_set.get("total")
            existing.logo_url = images.get("logo") if images else None
            existing.symbol_url = images.get("symbol") if images else None
            await self.db.flush()
            return None  # Return None to count as skipped (already exists)

        # Create new set
        card_set = CardSet(
            code=set_id,
            name=ptcg_set.get("name"),
            series=ptcg_set.get("series"),
            release_date=ptcg_set.get("releaseDate"),
            total_cards=ptcg_set.get("total"),
            logo_url=images.get("logo") if images else None,
            symbol_url=images.get("symbol") if images else None,
        )
        self.db.add(card_set)
        await self.db.flush()
        logger.debug(f"Created set: {card_set.name}")
        return card_set

    async def _sync_card(self, ptcg_card: dict, is_standard: bool = False) -> Optional[Card]:
        """Sync a single card"""
        card_id = ptcg_card.get("id")

        # Check if card already exists
        result = await self.db.execute(
            select(Card).where(Card.ptcg_id == card_id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            return None  # Already exists

        # Get or create the set
        card_set = None
        ptcg_set = ptcg_card.get("set")
        if ptcg_set:
            result = await self.db.execute(
                select(CardSet).where(CardSet.code == ptcg_set.get("id"))
            )
            card_set = result.scalar_one_or_none()

            if not card_set:
                images = ptcg_set.get("images", {})
                card_set = CardSet(
                    code=ptcg_set.get("id"),
                    name=ptcg_set.get("name"),
                    series=ptcg_set.get("series"),
                    release_date=ptcg_set.get("releaseDate"),
                    total_cards=ptcg_set.get("total"),
                    logo_url=images.get("logo") if images else None,
                    symbol_url=images.get("symbol") if images else None,
                )
                self.db.add(card_set)
                await self.db.flush()

        # Parse card data
        card_type = self._parse_card_type(ptcg_card.get("supertype"))
        subtypes = ptcg_card.get("subtypes", [])
        subtype = self._parse_subtype(subtypes[0] if subtypes else None)
        types = ptcg_card.get("types", [])
        energy_type = self._parse_energy_type(types[0] if types else None)

        # Determine legality
        legalities = ptcg_card.get("legalities", {})
        is_standard_legal = legalities.get("standard") == "Legal"
        is_expanded_legal = legalities.get("expanded") == "Legal"

        # Parse weaknesses and resistances
        weakness = None
        weaknesses = ptcg_card.get("weaknesses", [])
        if weaknesses:
            weakness = f"{weaknesses[0].get('type', '')} {weaknesses[0].get('value', '')}"

        resistance = None
        resistances = ptcg_card.get("resistances", [])
        if resistances:
            resistance = f"{resistances[0].get('type', '')} {resistances[0].get('value', '')}"

        # Get images
        images = ptcg_card.get("images", {})

        # Get retreat cost
        retreat_cost = ptcg_card.get("retreatCost", [])

        # Create card
        card = Card(
            ptcg_id=card_id,
            name=ptcg_card.get("name"),
            card_type=card_type,
            subtype=subtype,
            set_id=card_set.id if card_set else None,
            set_number=ptcg_card.get("number"),
            hp=self._parse_int(ptcg_card.get("hp")),
            energy_type=energy_type,
            weakness=weakness,
            resistance=resistance,
            retreat_cost=len(retreat_cost) if retreat_cost else None,
            abilities=self._parse_abilities(ptcg_card.get("abilities")),
            attacks=self._parse_attacks(ptcg_card.get("attacks")),
            rules="\n".join(ptcg_card.get("rules", [])) if ptcg_card.get("rules") else None,
            image_small=images.get("small") if images else None,
            image_large=images.get("large") if images else None,
            rarity=ptcg_card.get("rarity"),
            artist=ptcg_card.get("artist"),
            regulation_mark=ptcg_card.get("regulationMark"),
            is_standard_legal=is_standard_legal,
            is_expanded_legal=is_expanded_legal,
        )

        self.db.add(card)
        await self.db.flush()
        logger.debug(f"Synced card: {card.name}")
        return card

    def _card_to_dict(self, ptcg_card: dict) -> dict:
        """Convert a Pokemon TCG API card to a dict"""
        ptcg_set = ptcg_card.get("set", {})
        images = ptcg_card.get("images", {})
        legalities = ptcg_card.get("legalities", {})

        return {
            "id": ptcg_card.get("id"),
            "name": ptcg_card.get("name"),
            "supertype": ptcg_card.get("supertype"),
            "subtypes": ptcg_card.get("subtypes"),
            "types": ptcg_card.get("types"),
            "hp": ptcg_card.get("hp"),
            "number": ptcg_card.get("number"),
            "rarity": ptcg_card.get("rarity"),
            "artist": ptcg_card.get("artist"),
            "regulation_mark": ptcg_card.get("regulationMark"),
            "set": {
                "id": ptcg_set.get("id"),
                "name": ptcg_set.get("name"),
                "series": ptcg_set.get("series"),
            } if ptcg_set else None,
            "images": {
                "small": images.get("small"),
                "large": images.get("large"),
            } if images else None,
            "attacks": self._parse_attacks(ptcg_card.get("attacks")),
            "abilities": self._parse_abilities(ptcg_card.get("abilities")),
            "legalities": {
                "standard": legalities.get("standard"),
                "expanded": legalities.get("expanded"),
            } if legalities else None,
        }

    def _parse_card_type(self, supertype: str) -> CardType:
        """Parse card type from supertype"""
        if not supertype:
            return CardType.POKEMON

        supertype = supertype.lower()
        if "pokemon" in supertype or "pokémon" in supertype:
            return CardType.POKEMON
        elif "trainer" in supertype:
            return CardType.TRAINER
        elif "energy" in supertype:
            return CardType.ENERGY
        return CardType.POKEMON

    def _parse_subtype(self, subtype_str: str) -> Optional[CardSubtype]:
        """Parse subtype string"""
        if not subtype_str:
            return None

        subtype_str = subtype_str.lower().replace(" ", "").replace("-", "")
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
            "pokemontool": CardSubtype.TOOL,
            "basicenergy": CardSubtype.BASIC_ENERGY,
            "specialenergy": CardSubtype.SPECIAL_ENERGY,
        }
        return subtype_map.get(subtype_str)

    def _parse_energy_type(self, energy_str: str) -> Optional[EnergyType]:
        """Parse energy type string"""
        if not energy_str:
            return None

        energy_str = energy_str.lower()
        energy_map = {
            "grass": EnergyType.GRASS,
            "fire": EnergyType.FIRE,
            "water": EnergyType.WATER,
            "lightning": EnergyType.LIGHTNING,
            "psychic": EnergyType.PSYCHIC,
            "fighting": EnergyType.FIGHTING,
            "darkness": EnergyType.DARKNESS,
            "dark": EnergyType.DARKNESS,
            "metal": EnergyType.METAL,
            "steel": EnergyType.METAL,
            "dragon": EnergyType.DRAGON,
            "colorless": EnergyType.COLORLESS,
            "normal": EnergyType.COLORLESS,
            "fairy": EnergyType.FAIRY,
        }
        return energy_map.get(energy_str)

    def _parse_abilities(self, abilities: list) -> Optional[list]:
        """Parse abilities from API response"""
        if not abilities:
            return None

        return [
            {
                "name": ab.get("name"),
                "text": ab.get("text"),
                "type": ab.get("type"),
            }
            for ab in abilities
        ]

    def _parse_attacks(self, attacks: list) -> Optional[list]:
        """Parse attacks from API response"""
        if not attacks:
            return None

        return [
            {
                "name": atk.get("name"),
                "cost": atk.get("cost"),
                "damage": atk.get("damage"),
                "text": atk.get("text"),
                "convertedEnergyCost": atk.get("convertedEnergyCost"),
            }
            for atk in attacks
        ]

    def _parse_int(self, value) -> Optional[int]:
        """Safely parse integer"""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
