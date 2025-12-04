"""Meta Import Service - Import meta data from files"""
import json
import csv
from io import StringIO
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.models.meta import MetaSnapshot, MetaDeck

logger = structlog.get_logger()


class MetaImportService:
    """Service for importing meta data from various file formats"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def import_from_json(
        self,
        content: bytes,
        name: Optional[str] = None
    ) -> MetaSnapshot:
        """Import meta data from JSON file"""
        try:
            data = json.loads(content.decode("utf-8"))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {str(e)}")

        # Parse snapshot data
        snapshot_name = name or data.get("name", f"Import {datetime.now().strftime('%Y-%m-%d')}")

        snapshot = MetaSnapshot(
            name=snapshot_name,
            description=data.get("description"),
            snapshot_date=self._parse_date(data.get("snapshot_date") or data.get("date")) or datetime.now(),
            source="file",
            tournament_name=data.get("tournament_name") or data.get("tournament"),
            total_players=data.get("total_players") or data.get("players")
        )

        self.db.add(snapshot)
        await self.db.flush()

        # Parse deck data
        decks_data = data.get("decks", data.get("meta_decks", []))

        for i, deck_data in enumerate(decks_data):
            meta_deck = MetaDeck(
                snapshot_id=snapshot.id,
                archetype=deck_data.get("archetype") or deck_data.get("name", f"Unknown #{i+1}"),
                rank=deck_data.get("rank", i + 1),
                meta_share=self._parse_percentage(deck_data.get("meta_share") or deck_data.get("share", 0)),
                play_rate=self._parse_percentage(deck_data.get("play_rate")),
                win_rate=self._parse_percentage(deck_data.get("win_rate")),
                matchups=deck_data.get("matchups"),
                core_cards=deck_data.get("core_cards"),
                day2_conversion=self._parse_percentage(deck_data.get("day2_conversion")),
                top8_count=deck_data.get("top8_count") or deck_data.get("top8"),
                top16_count=deck_data.get("top16_count") or deck_data.get("top16")
            )
            self.db.add(meta_deck)

        await self.db.flush()
        await self.db.refresh(snapshot)

        logger.info(f"Imported meta snapshot: {snapshot.name} with {len(decks_data)} decks")
        return snapshot

    async def import_from_csv(
        self,
        content: bytes,
        name: Optional[str] = None
    ) -> MetaSnapshot:
        """
        Import meta data from CSV file.

        Expected columns:
        - rank (optional)
        - archetype or name
        - meta_share or share
        - win_rate (optional)
        - play_rate (optional)
        """
        try:
            text = content.decode("utf-8")
            reader = csv.DictReader(StringIO(text))
            rows = list(reader)
        except Exception as e:
            raise ValueError(f"Invalid CSV: {str(e)}")

        if not rows:
            raise ValueError("CSV file is empty")

        # Create snapshot
        snapshot_name = name or f"CSV Import {datetime.now().strftime('%Y-%m-%d')}"

        snapshot = MetaSnapshot(
            name=snapshot_name,
            snapshot_date=datetime.now(),
            source="file"
        )

        self.db.add(snapshot)
        await self.db.flush()

        # Parse each row
        for i, row in enumerate(rows):
            # Normalize column names
            row = {k.lower().strip(): v for k, v in row.items()}

            archetype = (
                row.get("archetype") or
                row.get("name") or
                row.get("deck") or
                f"Unknown #{i+1}"
            )

            meta_share = (
                row.get("meta_share") or
                row.get("share") or
                row.get("percentage") or
                "0"
            )

            meta_deck = MetaDeck(
                snapshot_id=snapshot.id,
                archetype=archetype.strip(),
                rank=self._parse_int(row.get("rank")) or (i + 1),
                meta_share=self._parse_percentage(meta_share),
                play_rate=self._parse_percentage(row.get("play_rate")),
                win_rate=self._parse_percentage(row.get("win_rate")),
                day2_conversion=self._parse_percentage(row.get("day2_conversion") or row.get("day2")),
                top8_count=self._parse_int(row.get("top8_count") or row.get("top8")),
                top16_count=self._parse_int(row.get("top16_count") or row.get("top16"))
            )
            self.db.add(meta_deck)

        await self.db.flush()
        await self.db.refresh(snapshot)

        logger.info(f"Imported meta snapshot from CSV: {snapshot.name} with {len(rows)} decks")
        return snapshot

    def _parse_date(self, date_value) -> Optional[datetime]:
        """Parse date from various formats"""
        if not date_value:
            return None

        if isinstance(date_value, datetime):
            return date_value

        date_str = str(date_value)

        # Try common formats
        formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ"
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return None

    def _parse_percentage(self, value) -> Optional[float]:
        """Parse percentage value"""
        if value is None:
            return None

        try:
            value_str = str(value).strip().rstrip("%")
            result = float(value_str)

            # If value > 1, assume it's already a percentage
            # Otherwise, it might be a decimal (0.45 = 45%)
            if result <= 1 and result > 0:
                result *= 100

            return result
        except (ValueError, TypeError):
            return None

    def _parse_int(self, value) -> Optional[int]:
        """Safely parse integer"""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
