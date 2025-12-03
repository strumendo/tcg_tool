"""Match Import Service - Import matches from OCR/text"""
import re
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.models.match import Match, MatchAction, MatchResult, ActionType

logger = structlog.get_logger()


class MatchImportService:
    """Service for importing matches from screenshots or text"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def import_from_screenshot(
        self,
        image_data: bytes,
        deck_id: Optional[int] = None
    ) -> Match:
        """Import match data from a Pokemon TCG Live screenshot using OCR"""
        import pytesseract
        from PIL import Image
        from io import BytesIO

        try:
            # Load image
            image = Image.open(BytesIO(image_data))

            # Perform OCR
            text = pytesseract.image_to_string(image)

            logger.info(f"OCR extracted text: {text[:200]}...")

            # Parse the extracted text
            return await self._parse_match_text(text, deck_id, "ocr")

        except Exception as e:
            logger.error(f"Failed to process screenshot: {str(e)}")
            raise

    async def import_from_text(
        self,
        text_data: str,
        deck_id: Optional[int] = None
    ) -> Match:
        """Import match data from text"""
        return await self._parse_match_text(text_data, deck_id, "text")

    async def _parse_match_text(
        self,
        text: str,
        deck_id: Optional[int],
        source: str
    ) -> Match:
        """Parse match data from text (OCR or manual input)"""
        lines = text.strip().split("\n")

        # Initialize match data
        result = None
        opponent_archetype = None
        player_prizes = 0
        opponent_prizes = 0
        went_first = None
        actions = []
        current_turn = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Try to detect result
            if "victory" in line.lower() or "you won" in line.lower() or "win" in line.lower():
                result = MatchResult.WIN
            elif "defeat" in line.lower() or "you lost" in line.lower() or "loss" in line.lower():
                result = MatchResult.LOSS
            elif "draw" in line.lower() or "tie" in line.lower():
                result = MatchResult.DRAW
            elif "concede" in line.lower():
                result = MatchResult.CONCEDE

            # Try to detect prize counts
            prize_match = re.search(r"prizes?[:\s]+(\d+)\s*[-/]\s*(\d+)", line, re.IGNORECASE)
            if prize_match:
                player_prizes = int(prize_match.group(1))
                opponent_prizes = int(prize_match.group(2))

            # Try to detect opponent deck
            opponent_match = re.search(r"opponent[:\s]+(.+?)(?:\s|$)", line, re.IGNORECASE)
            if opponent_match:
                opponent_archetype = opponent_match.group(1).strip()

            # Try to detect who went first
            if "went first" in line.lower():
                if "you" in line.lower() or "player" in line.lower():
                    went_first = True
                else:
                    went_first = False

            # Try to detect turn markers
            turn_match = re.search(r"turn\s+(\d+)", line, re.IGNORECASE)
            if turn_match:
                current_turn = int(turn_match.group(1))

            # Try to parse action lines
            action = self._parse_action_line(line, current_turn, len(actions))
            if action:
                actions.append(action)

        # Create the match
        match = Match(
            deck_id=deck_id,
            opponent_deck_archetype=opponent_archetype,
            result=result,
            player_prizes_taken=player_prizes,
            opponent_prizes_taken=opponent_prizes,
            total_turns=current_turn if current_turn > 0 else None,
            went_first=went_first,
            match_date=datetime.now(),
            import_source=source,
            raw_data=text
        )

        self.db.add(match)
        await self.db.flush()

        # Add actions
        for action_data in actions:
            action = MatchAction(
                match_id=match.id,
                **action_data
            )
            self.db.add(action)

        await self.db.flush()
        await self.db.refresh(match)

        logger.info(f"Imported match: {result} vs {opponent_archetype}")
        return match

    def _parse_action_line(
        self,
        line: str,
        current_turn: int,
        action_order: int
    ) -> Optional[dict]:
        """Try to parse an action from a line of text"""
        line_lower = line.lower()

        # Common action patterns
        action_patterns = [
            (r"played?\s+(.+?)(?:\s+from|\s*$)", ActionType.PLAY_POKEMON),
            (r"evolved?\s+(.+?)\s+into\s+(.+)", ActionType.EVOLVE),
            (r"attached?\s+(.+?)\s+to\s+(.+)", ActionType.ATTACH_ENERGY),
            (r"used?\s+(.+?)(?:'s)?\s+(.+)", ActionType.ABILITY),
            (r"attacked?\s+(?:with\s+)?(.+)", ActionType.ATTACK),
            (r"knocked\s+out\s+(.+)", ActionType.KNOCK_OUT),
            (r"retreat(?:ed)?\s+(.+)", ActionType.RETREAT),
            (r"drew?\s+(.+)", ActionType.DRAW),
            (r"took?\s+(\d+)\s+prize", ActionType.PRIZE_TAKE),
        ]

        for pattern, action_type in action_patterns:
            match = re.search(pattern, line_lower)
            if match:
                return {
                    "turn_number": current_turn,
                    "action_order": action_order,
                    "is_player_action": True,  # Assume player action by default
                    "action_type": action_type,
                    "card_name": match.group(1).strip() if match.groups() else None,
                    "target_card": match.group(2).strip() if len(match.groups()) > 1 else None,
                    "description": line
                }

        return None
