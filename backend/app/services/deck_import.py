"""Deck Import Service - Import decks from text/files"""
import re
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.models.deck import Deck, DeckCard, DeckFormat
from app.models.card import Card, CardSet, CardType

logger = structlog.get_logger()


class DeckImportService:
    """Service for importing decks from various formats"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def import_from_text(
        self,
        deck_list: str,
        name: Optional[str] = None,
        format: DeckFormat = DeckFormat.STANDARD
    ) -> Deck:
        """
        Import a deck from text format.

        Supported formats:
        - PTCGO format: "4 Charizard ex SVI 125"
        - Simple format: "4x Charizard ex"
        - Limitless format with set codes
        """
        lines = deck_list.strip().split("\n")

        # Create deck
        deck = Deck(
            name=name or "Imported Deck",
            format=format,
            source="file"
        )
        self.db.add(deck)
        await self.db.flush()

        pokemon_count = 0
        trainer_count = 0
        energy_count = 0
        total_count = 0

        for line in lines:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("//"):
                continue

            # Skip section headers
            if line.lower() in ["pokemon", "pokémon", "trainer", "energy", "##pokemon", "##trainer", "##energy"]:
                continue

            parsed = self._parse_line(line)
            if not parsed:
                logger.debug(f"Could not parse line: {line}")
                continue

            quantity, card_name, set_code, set_number = parsed

            # Find the card in database
            card = await self._find_card(card_name, set_code, set_number)

            if card:
                deck_card = DeckCard(
                    deck_id=deck.id,
                    card_id=card.id,
                    quantity=quantity
                )
                self.db.add(deck_card)

                total_count += quantity
                if card.card_type == CardType.POKEMON:
                    pokemon_count += quantity
                elif card.card_type == CardType.TRAINER:
                    trainer_count += quantity
                elif card.card_type == CardType.ENERGY:
                    energy_count += quantity
            else:
                logger.warning(f"Card not found: {card_name} ({set_code} {set_number})")

        # Update deck counts
        deck.total_cards = total_count
        deck.pokemon_count = pokemon_count
        deck.trainer_count = trainer_count
        deck.energy_count = energy_count

        # Try to determine archetype from main Pokemon
        if not deck.archetype:
            deck.archetype = await self._determine_archetype(deck)

        await self.db.flush()

        # Reload deck with all relationships for proper serialization
        from sqlalchemy.orm import selectinload
        query = select(Deck).options(
            selectinload(Deck.cards).selectinload(DeckCard.card)
        ).where(Deck.id == deck.id)
        result = await self.db.execute(query)
        deck = result.scalar_one()

        logger.info(f"Imported deck: {deck.name} with {total_count} cards")
        return deck

    def _parse_line(self, line: str) -> Optional[tuple]:
        """
        Parse a deck list line.

        Returns: (quantity, card_name, set_code, set_number) or None
        """
        # Remove trailing semicolon if present
        line = line.rstrip(';').strip()

        # CSV format: "3, Charmander, PAF, 7" or "3,Charmander,PAF,7"
        csv_pattern = r"^(\d+)\s*,\s*(.+?)\s*,\s*([A-Z]{2,4})\s*,\s*(\d+)$"
        match = re.match(csv_pattern, line, re.IGNORECASE)
        if match:
            return (
                int(match.group(1)),
                match.group(2).strip(),
                match.group(3).upper(),
                match.group(4)
            )

        # PTCGO format: "4 Charizard ex SVI 125"
        # Pattern: quantity name set_code set_number
        ptcgo_pattern = r"^(\d+)\s+(.+?)\s+([A-Z]{2,4})\s+(\d+)$"
        match = re.match(ptcgo_pattern, line)
        if match:
            return (
                int(match.group(1)),
                match.group(2).strip(),
                match.group(3),
                match.group(4)
            )

        # Alternative: "4x Charizard ex SVI 125"
        alt_pattern = r"^(\d+)x?\s+(.+?)\s+([A-Z]{2,4})\s+(\d+)$"
        match = re.match(alt_pattern, line)
        if match:
            return (
                int(match.group(1)),
                match.group(2).strip(),
                match.group(3),
                match.group(4)
            )

        # Simple format without set: "4 Charizard ex" or "4x Charizard ex"
        simple_pattern = r"^(\d+)x?\s+(.+)$"
        match = re.match(simple_pattern, line)
        if match:
            return (
                int(match.group(1)),
                match.group(2).strip(),
                None,
                None
            )

        return None

    async def _find_card(
        self,
        name: str,
        set_code: Optional[str],
        set_number: Optional[str]
    ) -> Optional[Card]:
        """Find a card in the database - prioritizes set_code + set_number for language independence"""
        from sqlalchemy.orm import selectinload

        # PRIORITY 1: Search by set_code + set_number (language independent!)
        if set_code and set_number:
            # Normalize set codes (handle common variations)
            normalized_set_code = self._normalize_set_code(set_code)

            query = select(Card).options(selectinload(Card.set)).where(
                Card.set_number == set_number
            ).join(Card.set).where(CardSet.code == normalized_set_code)

            result = await self.db.execute(query)
            card = result.scalar_one_or_none()
            if card:
                logger.debug(f"Found card by set/number: {card.name} ({normalized_set_code} {set_number})")
                return card

            # Try alternative set code formats
            for alt_code in self._get_alternative_set_codes(set_code):
                query = select(Card).options(selectinload(Card.set)).where(
                    Card.set_number == set_number
                ).join(Card.set).where(CardSet.code == alt_code)

                result = await self.db.execute(query)
                card = result.scalar_one_or_none()
                if card:
                    logger.debug(f"Found card with alt set code: {card.name} ({alt_code} {set_number})")
                    return card

        # PRIORITY 2: Search by exact name
        query = select(Card).where(Card.name == name)
        result = await self.db.execute(query)
        cards = result.scalars().all()

        if cards:
            return cards[0]

        # PRIORITY 3: Try partial name match
        query = select(Card).where(Card.name.ilike(f"%{name}%"))
        result = await self.db.execute(query)
        cards = result.scalars().all()

        if cards:
            return cards[0]

        logger.warning(f"Card not found: {name} (set: {set_code}, number: {set_number})")
        return None

    def _normalize_set_code(self, set_code: str) -> str:
        """Normalize set code to Pokemon TCG API format"""
        # Common Portuguese/Brazilian set code mappings to API codes
        set_code_map = {
            # Scarlet & Violet era
            "PAF": "sv4pt5",  # Paldean Fates
            "PFL": "sv6pt5",  # Paldean Fates (alt) / Prismatic Evolutions?
            "OBF": "sv3",     # Obsidian Flames
            "MEW": "sv3pt5",  # 151 / Mew
            "SFA": "sv6",     # Shrouded Fable
            "TWM": "sv6",     # Twilight Masquerade
            "MEP": "sv3pt5",  # 151 (Portuguese?)
            "MEG": "sv1",     # Scarlet & Violet Base? (Portuguese)
            "PAR": "sv4",     # Paradox Rift
            "PAL": "sv2",     # Paldea Evolved
            "TEF": "sv5",     # Temporal Forces
            "MEE": "sve",     # Energies
            "SVI": "sv1",     # Scarlet & Violet Base
            "SVE": "sve",     # Scarlet & Violet Energies
            # Add more mappings as needed
        }
        return set_code_map.get(set_code.upper(), set_code.lower())

    def _get_alternative_set_codes(self, set_code: str) -> List[str]:
        """Get alternative set codes to try"""
        code = set_code.upper()
        alternatives = []

        # Try lowercase
        alternatives.append(code.lower())

        # Try with different formats
        if code.startswith("SV"):
            alternatives.append(code.lower())
        elif len(code) == 3:
            # Try sv prefix for newer sets
            alternatives.append(f"sv{code.lower()}")

        return alternatives

    async def _determine_archetype(self, deck: Deck) -> Optional[str]:
        """Try to determine deck archetype from main Pokemon"""
        # Get all Pokemon cards in deck
        from sqlalchemy.orm import selectinload

        query = select(DeckCard).options(
            selectinload(DeckCard.card)
        ).where(DeckCard.deck_id == deck.id)

        result = await self.db.execute(query)
        deck_cards = result.scalars().all()

        # Find the main attacker (usually a V/ex/VSTAR with highest count)
        main_pokemon = None
        for dc in deck_cards:
            if dc.card and dc.card.card_type == CardType.POKEMON:
                if dc.card.subtype and dc.card.subtype.value in ["ex", "v", "vstar", "vmax"]:
                    if not main_pokemon or dc.quantity > main_pokemon[1]:
                        main_pokemon = (dc.card.name, dc.quantity)

        if main_pokemon:
            return main_pokemon[0]

        return None
