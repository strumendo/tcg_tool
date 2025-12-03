"""Card Import Service - Import cards from files"""
import json
import csv
from io import StringIO
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.models.card import Card, CardSet, CardType, CardSubtype, EnergyType

logger = structlog.get_logger()


class CardImportService:
    """Service for importing cards from various file formats"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def import_from_json(self, content: bytes) -> dict:
        """Import cards from JSON file"""
        try:
            data = json.loads(content.decode("utf-8"))
        except json.JSONDecodeError as e:
            return {"success": False, "error": f"Invalid JSON: {str(e)}"}

        imported = 0
        skipped = 0
        errors = []

        # Handle both single card and list of cards
        cards_data = data if isinstance(data, list) else data.get("cards", [data])

        for card_data in cards_data:
            try:
                result = await self._import_card(card_data)
                if result:
                    imported += 1
                else:
                    skipped += 1
            except Exception as e:
                errors.append(f"Failed to import {card_data.get('name', 'unknown')}: {str(e)}")
                skipped += 1

        return {
            "success": True,
            "imported": imported,
            "skipped": skipped,
            "errors": errors
        }

    async def import_from_csv(self, content: bytes) -> dict:
        """Import cards from CSV file"""
        try:
            text = content.decode("utf-8")
            reader = csv.DictReader(StringIO(text))
        except Exception as e:
            return {"success": False, "error": f"Invalid CSV: {str(e)}"}

        imported = 0
        skipped = 0
        errors = []

        for row in reader:
            try:
                result = await self._import_card(row)
                if result:
                    imported += 1
                else:
                    skipped += 1
            except Exception as e:
                errors.append(f"Failed to import {row.get('name', 'unknown')}: {str(e)}")
                skipped += 1

        return {
            "success": True,
            "imported": imported,
            "skipped": skipped,
            "errors": errors
        }

    async def _import_card(self, card_data: dict) -> Optional[Card]:
        """Import a single card"""
        # Check if card already exists
        limitless_id = card_data.get("limitless_id") or card_data.get("id")
        if limitless_id:
            existing = await self.db.execute(
                select(Card).where(Card.limitless_id == limitless_id)
            )
            if existing.scalar_one_or_none():
                logger.debug(f"Card already exists: {limitless_id}")
                return None

        # Get or create card set
        set_code = card_data.get("set_code") or card_data.get("set", {}).get("code")
        card_set = None
        if set_code:
            card_set = await self._get_or_create_set(set_code, card_data)

        # Parse card type
        card_type_str = card_data.get("card_type") or card_data.get("supertype", "").lower()
        card_type = self._parse_card_type(card_type_str)

        # Parse subtype
        subtype_str = card_data.get("subtype") or card_data.get("subtypes", [""])[0] if isinstance(
            card_data.get("subtypes"), list) else card_data.get("subtypes")
        subtype = self._parse_subtype(subtype_str)

        # Parse energy type
        energy_type_str = card_data.get("energy_type") or card_data.get("types", [""])[0] if isinstance(
            card_data.get("types"), list) else card_data.get("types")
        energy_type = self._parse_energy_type(energy_type_str)

        # Create card
        card = Card(
            limitless_id=limitless_id,
            ptcgo_code=card_data.get("ptcgo_code"),
            name=card_data.get("name", "Unknown"),
            card_type=card_type,
            subtype=subtype,
            set_id=card_set.id if card_set else None,
            set_number=card_data.get("set_number") or card_data.get("number"),
            hp=self._parse_int(card_data.get("hp")),
            energy_type=energy_type,
            weakness=card_data.get("weakness"),
            resistance=card_data.get("resistance"),
            retreat_cost=self._parse_int(card_data.get("retreat_cost") or card_data.get("convertedRetreatCost")),
            abilities=card_data.get("abilities"),
            attacks=card_data.get("attacks"),
            rules=card_data.get("rules") if isinstance(card_data.get("rules"), str) else (
                "\n".join(card_data.get("rules", [])) if card_data.get("rules") else None),
            image_small=card_data.get("image_small") or card_data.get("images", {}).get("small"),
            image_large=card_data.get("image_large") or card_data.get("images", {}).get("large"),
            rarity=card_data.get("rarity"),
            artist=card_data.get("artist"),
            regulation_mark=card_data.get("regulation_mark") or card_data.get("regulationMark"),
            is_standard_legal=card_data.get("is_standard_legal", True),
            is_expanded_legal=card_data.get("is_expanded_legal", True),
        )

        self.db.add(card)
        await self.db.flush()
        logger.info(f"Imported card: {card.name}")
        return card

    async def _get_or_create_set(self, set_code: str, card_data: dict) -> CardSet:
        """Get or create a card set"""
        result = await self.db.execute(
            select(CardSet).where(CardSet.code == set_code)
        )
        card_set = result.scalar_one_or_none()

        if not card_set:
            set_data = card_data.get("set", {})
            card_set = CardSet(
                code=set_code,
                name=set_data.get("name", set_code),
                series=set_data.get("series"),
                release_date=set_data.get("releaseDate"),
                total_cards=self._parse_int(set_data.get("total")),
                logo_url=set_data.get("images", {}).get("logo"),
                symbol_url=set_data.get("images", {}).get("symbol"),
            )
            self.db.add(card_set)
            await self.db.flush()
            logger.info(f"Created set: {card_set.name}")

        return card_set

    def _parse_card_type(self, type_str: str) -> CardType:
        """Parse card type string"""
        if not type_str:
            return CardType.POKEMON

        type_str = type_str.lower()
        if "pokemon" in type_str or "pokémon" in type_str:
            return CardType.POKEMON
        elif "trainer" in type_str:
            return CardType.TRAINER
        elif "energy" in type_str:
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

    def _parse_int(self, value) -> Optional[int]:
        """Safely parse integer"""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
