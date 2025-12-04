"""Card Sync Service - Sync cards from Pokemon TCG API"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from pokemontcgsdk import Card as PTCGCard
from pokemontcgsdk import Set as PTCGSet
from pokemontcgsdk import RestClient

from app.models.card import Card, CardSet, CardType, CardSubtype, EnergyType
from app.core.config import settings

logger = structlog.get_logger()

# Configure the SDK with API key
RestClient.configure(settings.pokemon_tcg_api_key)


class CardSyncService:
    """Service for syncing cards from Pokemon TCG API"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def sync_all_sets(self) -> dict:
        """Sync all card sets from the API"""
        try:
            sets = PTCGSet.all()
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
            logger.error(f"Failed to sync sets: {str(e)}")
            return {"success": False, "error": str(e)}

    async def sync_set_cards(self, set_code: str) -> dict:
        """Sync all cards from a specific set"""
        try:
            cards = PTCGCard.where(q=f'set.id:{set_code}')
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
                    errors.append(f"{ptcg_card.name}: {str(e)}")
                    skipped += 1

            logger.info(f"Synced {synced} cards from set {set_code}, skipped {skipped}")
            return {
                "success": True,
                "synced": synced,
                "skipped": skipped,
                "errors": errors[:10]  # Limit errors shown
            }

        except Exception as e:
            logger.error(f"Failed to sync cards from set {set_code}: {str(e)}")
            return {"success": False, "error": str(e)}

    async def sync_standard_legal_cards(self) -> dict:
        """Sync all standard legal cards"""
        try:
            # Get standard legal regulation marks (F, G, H currently)
            cards = PTCGCard.where(q='legalities.standard:legal')
            synced = 0
            skipped = 0
            errors = []

            for ptcg_card in cards:
                try:
                    result = await self._sync_card(ptcg_card, is_standard=True)
                    if result:
                        synced += 1
                    else:
                        skipped += 1
                except Exception as e:
                    errors.append(f"{ptcg_card.name}: {str(e)}")
                    skipped += 1

            logger.info(f"Synced {synced} standard legal cards, skipped {skipped}")
            return {
                "success": True,
                "synced": synced,
                "skipped": skipped,
                "errors": errors[:10]
            }

        except Exception as e:
            logger.error(f"Failed to sync standard cards: {str(e)}")
            return {"success": False, "error": str(e)}

    async def search_cards(self, query: str, page: int = 1, page_size: int = 50) -> List[dict]:
        """Search cards from the API"""
        try:
            cards = PTCGCard.where(q=f'name:{query}*', page=page, pageSize=page_size)
            return [self._card_to_dict(card) for card in cards]
        except Exception as e:
            logger.error(f"Failed to search cards: {str(e)}")
            return []

    async def get_card_by_id(self, card_id: str) -> Optional[dict]:
        """Get a specific card by ID from the API"""
        try:
            card = PTCGCard.find(card_id)
            if card:
                return self._card_to_dict(card)
            return None
        except Exception as e:
            logger.error(f"Failed to get card {card_id}: {str(e)}")
            return None

    async def _sync_set(self, ptcg_set) -> Optional[CardSet]:
        """Sync a single set"""
        # Check if set already exists
        result = await self.db.execute(
            select(CardSet).where(CardSet.code == ptcg_set.id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing set
            existing.name = ptcg_set.name
            existing.series = ptcg_set.series
            existing.release_date = ptcg_set.releaseDate
            existing.total_cards = ptcg_set.total
            existing.logo_url = ptcg_set.images.logo if ptcg_set.images else None
            existing.symbol_url = ptcg_set.images.symbol if ptcg_set.images else None
            await self.db.flush()
            return None  # Return None to count as skipped (already exists)

        # Create new set
        card_set = CardSet(
            code=ptcg_set.id,
            name=ptcg_set.name,
            series=ptcg_set.series,
            release_date=ptcg_set.releaseDate,
            total_cards=ptcg_set.total,
            logo_url=ptcg_set.images.logo if ptcg_set.images else None,
            symbol_url=ptcg_set.images.symbol if ptcg_set.images else None,
        )
        self.db.add(card_set)
        await self.db.flush()
        logger.debug(f"Created set: {card_set.name}")
        return card_set

    async def _sync_card(self, ptcg_card, is_standard: bool = False) -> Optional[Card]:
        """Sync a single card"""
        # Check if card already exists
        result = await self.db.execute(
            select(Card).where(Card.ptcg_id == ptcg_card.id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            return None  # Already exists

        # Get or create the set
        card_set = None
        if ptcg_card.set:
            result = await self.db.execute(
                select(CardSet).where(CardSet.code == ptcg_card.set.id)
            )
            card_set = result.scalar_one_or_none()

            if not card_set:
                card_set = CardSet(
                    code=ptcg_card.set.id,
                    name=ptcg_card.set.name,
                    series=ptcg_card.set.series,
                    release_date=ptcg_card.set.releaseDate,
                    total_cards=ptcg_card.set.total,
                    logo_url=ptcg_card.set.images.logo if ptcg_card.set.images else None,
                    symbol_url=ptcg_card.set.images.symbol if ptcg_card.set.images else None,
                )
                self.db.add(card_set)
                await self.db.flush()

        # Parse card data
        card_type = self._parse_card_type(ptcg_card.supertype)
        subtype = self._parse_subtype(ptcg_card.subtypes[0] if ptcg_card.subtypes else None)
        energy_type = self._parse_energy_type(ptcg_card.types[0] if ptcg_card.types else None)

        # Determine legality
        is_standard_legal = False
        is_expanded_legal = False
        if ptcg_card.legalities:
            is_standard_legal = getattr(ptcg_card.legalities, 'standard', None) == 'Legal'
            is_expanded_legal = getattr(ptcg_card.legalities, 'expanded', None) == 'Legal'

        # Parse weaknesses and resistances
        weakness = None
        if ptcg_card.weaknesses:
            weakness = f"{ptcg_card.weaknesses[0].type} {ptcg_card.weaknesses[0].value}"

        resistance = None
        if ptcg_card.resistances:
            resistance = f"{ptcg_card.resistances[0].type} {ptcg_card.resistances[0].value}"

        # Create card
        card = Card(
            ptcg_id=ptcg_card.id,
            name=ptcg_card.name,
            card_type=card_type,
            subtype=subtype,
            set_id=card_set.id if card_set else None,
            set_number=ptcg_card.number,
            hp=self._parse_int(ptcg_card.hp),
            energy_type=energy_type,
            weakness=weakness,
            resistance=resistance,
            retreat_cost=len(ptcg_card.retreatCost) if ptcg_card.retreatCost else None,
            abilities=self._parse_abilities(ptcg_card.abilities),
            attacks=self._parse_attacks(ptcg_card.attacks),
            rules="\n".join(ptcg_card.rules) if ptcg_card.rules else None,
            image_small=ptcg_card.images.small if ptcg_card.images else None,
            image_large=ptcg_card.images.large if ptcg_card.images else None,
            rarity=ptcg_card.rarity,
            artist=ptcg_card.artist,
            regulation_mark=ptcg_card.regulationMark,
            is_standard_legal=is_standard_legal,
            is_expanded_legal=is_expanded_legal,
        )

        self.db.add(card)
        await self.db.flush()
        logger.debug(f"Synced card: {card.name}")
        return card

    def _card_to_dict(self, ptcg_card) -> dict:
        """Convert a Pokemon TCG SDK card to a dict"""
        return {
            "id": ptcg_card.id,
            "name": ptcg_card.name,
            "supertype": ptcg_card.supertype,
            "subtypes": ptcg_card.subtypes,
            "types": ptcg_card.types,
            "hp": ptcg_card.hp,
            "number": ptcg_card.number,
            "rarity": ptcg_card.rarity,
            "artist": ptcg_card.artist,
            "regulation_mark": ptcg_card.regulationMark,
            "set": {
                "id": ptcg_card.set.id,
                "name": ptcg_card.set.name,
                "series": ptcg_card.set.series,
            } if ptcg_card.set else None,
            "images": {
                "small": ptcg_card.images.small,
                "large": ptcg_card.images.large,
            } if ptcg_card.images else None,
            "attacks": self._parse_attacks(ptcg_card.attacks),
            "abilities": self._parse_abilities(ptcg_card.abilities),
            "legalities": {
                "standard": getattr(ptcg_card.legalities, 'standard', None),
                "expanded": getattr(ptcg_card.legalities, 'expanded', None),
            } if ptcg_card.legalities else None,
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

    def _parse_abilities(self, abilities) -> Optional[list]:
        """Parse abilities from API response"""
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

    def _parse_attacks(self, attacks) -> Optional[list]:
        """Parse attacks from API response"""
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

    def _parse_int(self, value) -> Optional[int]:
        """Safely parse integer"""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
