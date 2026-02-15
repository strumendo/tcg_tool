"""
Match Analysis Service - Process videos and transcriptions for insights

Features:
- YouTube URL processing
- Match transcription parsing
- Card identification from text
- Play sequence extraction
- Basic insights generation
"""

import re
import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional
from enum import Enum
from urllib.request import urlopen, Request
from urllib.error import URLError


class MatchSource(Enum):
    """Source type for match data."""
    YOUTUBE = "youtube"
    VIDEO_FILE = "video_file"
    TRANSCRIPTION = "transcription"
    MANUAL = "manual"


class ProcessingStatus(Enum):
    """Processing status for match data."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PlayAction:
    """Represents a single play action in a match."""
    turn: int = 0
    player: str = ""  # "player1" or "player2"
    action_type: str = ""  # "draw", "play_pokemon", "attach_energy", "attack", etc.
    card_name: str = ""
    details: str = ""
    timestamp: str = ""


@dataclass
class MatchData:
    """Represents processed match data."""
    id: str = ""
    title: str = ""
    source: MatchSource = MatchSource.MANUAL
    source_url: str = ""
    player1_deck: str = ""
    player2_deck: str = ""
    winner: str = ""
    total_turns: int = 0
    actions: list[PlayAction] = field(default_factory=list)
    cards_identified: list[str] = field(default_factory=list)
    insights: list[str] = field(default_factory=list)
    status: ProcessingStatus = ProcessingStatus.PENDING
    created_at: str = ""
    processed_at: str = ""
    error_message: str = ""

    def to_dict(self):
        data = asdict(self)
        data['source'] = self.source.value
        data['status'] = self.status.value
        return data

    @staticmethod
    def from_dict(data: dict) -> 'MatchData':
        data['source'] = MatchSource(data.get('source', 'manual'))
        data['status'] = ProcessingStatus(data.get('status', 'pending'))
        data['actions'] = [PlayAction(**a) for a in data.get('actions', [])]
        return MatchData(**data)


# Common Pokemon TCG card patterns for identification
CARD_PATTERNS = [
    # Pokemon ex
    r'\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\s+ex\b',
    # Pokemon V/VMAX/VSTAR
    r'\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\s+(V|VMAX|VSTAR)\b',
    # Regular Pokemon
    r'\b(Charizard|Pikachu|Gardevoir|Dragapult|Lugia|Arceus|Giratina|Comfey|Mew|Pidgeot|Bibarel|Lumineon)\b',
    # Supporters
    r'\b(Professor\'s Research|Iono|Boss\'s Orders|Arven|Penny|Irida|Colress|Judge|Cynthia)\b',
    # Items
    r'\b(Ultra Ball|Nest Ball|Rare Candy|Switch|Super Rod|Night Stretcher|Counter Catcher|Battle VIP Pass)\b',
    # Stadiums
    r'\b(Artazon|Temple of Sinnoh|Path to the Peak|Collapsed Stadium|Beach Court)\b',
    # Energy
    r'\b(Double Turbo Energy|Jet Energy|Reversal Energy|Gift Energy|Basic .+ Energy)\b',
]

# Action patterns for transcription parsing
ACTION_PATTERNS = {
    'draw': [r'draw(?:s|ing)?\s+(?:a\s+)?card', r'drew\s+(?:a\s+)?card'],
    'play_pokemon': [r'play(?:s|ed)?\s+(?:down\s+)?([A-Z][a-z]+)', r'bench(?:es|ed)?\s+([A-Z][a-z]+)'],
    'attach_energy': [r'attach(?:es|ed)?\s+(?:an?\s+)?energy', r'attach(?:es|ed)?\s+(.+)\s+energy'],
    'attack': [r'attack(?:s|ed)?\s+(?:with\s+)?(.+)', r'use(?:s|d)?\s+(.+)\s+for\s+\d+'],
    'retreat': [r'retreat(?:s|ed)?', r'switch(?:es|ed)?'],
    'supporter': [r'play(?:s|ed)?\s+(Professor|Iono|Boss|Arven|Penny)', r'use(?:s|d)?\s+(.+)\s+supporter'],
    'item': [r'use(?:s|d)?\s+(?:an?\s+)?(Ultra Ball|Nest Ball|Rare Candy)', r'play(?:s|ed)?\s+(.+)\s+item'],
    'knock_out': [r'knock(?:s|ed)?\s+out', r'KO(?:\'s|ed)?'],
    'prize': [r'take(?:s)?\s+(?:a\s+)?prize', r'drew\s+prize'],
}


class MatchAnalysisService:
    """Service for analyzing Pokemon TCG matches."""

    CACHE_FILE = "matches_cache.json"

    def __init__(self, cache_dir: str = None):
        """Initialize match analysis service."""
        self.cache_dir = cache_dir or os.path.dirname(os.path.abspath(__file__))
        self.cache_path = os.path.join(self.cache_dir, self.CACHE_FILE)
        self._matches: list[MatchData] = []
        self._load_cache()

    def _load_cache(self):
        """Load cached matches from file."""
        try:
            if os.path.exists(self.cache_path):
                with open(self.cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._matches = [MatchData.from_dict(m) for m in data.get('matches', [])]
        except (json.JSONDecodeError, IOError):
            pass

    def _save_cache(self):
        """Save matches to cache file."""
        try:
            data = {
                'matches': [m.to_dict() for m in self._matches]
            }
            with open(self.cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError:
            pass

    def _generate_id(self) -> str:
        """Generate unique match ID."""
        return f"match_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(self._matches)}"

    # =========================================================================
    # YOUTUBE PROCESSING
    # =========================================================================

    def process_youtube_url(self, url: str) -> MatchData:
        """
        Process a YouTube URL for match analysis.

        Args:
            url: YouTube video URL

        Returns:
            MatchData with extracted information
        """
        match = MatchData(
            id=self._generate_id(),
            source=MatchSource.YOUTUBE,
            source_url=url,
            status=ProcessingStatus.PROCESSING,
            created_at=datetime.now().isoformat()
        )

        # Validate YouTube URL
        if not self._is_valid_youtube_url(url):
            match.status = ProcessingStatus.FAILED
            match.error_message = "Invalid YouTube URL"
            return match

        # Extract video ID and fetch metadata
        video_id = self._extract_video_id(url)
        if video_id:
            metadata = self._fetch_youtube_metadata(video_id)
            if metadata:
                match.title = metadata.get('title', 'Unknown Video')

        # Note: Full video processing would require yt-dlp and ffmpeg
        # For now, we mark it for manual review
        match.status = ProcessingStatus.PENDING
        match.insights.append("Video queued for processing")
        match.insights.append("Tip: Add transcription manually for faster analysis")

        self._matches.append(match)
        self._save_cache()
        return match

    def _is_valid_youtube_url(self, url: str) -> bool:
        """Check if URL is a valid YouTube URL."""
        patterns = [
            r'youtube\.com/watch\?v=[\w-]+',
            r'youtu\.be/[\w-]+',
            r'youtube\.com/embed/[\w-]+',
        ]
        return any(re.search(p, url) for p in patterns)

    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL."""
        patterns = [
            r'youtube\.com/watch\?v=([\w-]+)',
            r'youtu\.be/([\w-]+)',
            r'youtube\.com/embed/([\w-]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def _fetch_youtube_metadata(self, video_id: str) -> Optional[dict]:
        """Fetch YouTube video metadata (title, thumbnail)."""
        # Note: Full metadata requires YouTube Data API
        # Using oembed as a simple alternative
        try:
            oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
            req = Request(oembed_url, headers={'User-Agent': 'TCG Tool/1.0'})
            with urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode('utf-8'))
        except (URLError, json.JSONDecodeError):
            return None

    # =========================================================================
    # TRANSCRIPTION PROCESSING
    # =========================================================================

    def process_transcription(self, text: str, title: str = "") -> MatchData:
        """
        Process a match transcription for analysis.

        Args:
            text: Transcription text
            title: Optional title for the match

        Returns:
            MatchData with extracted information
        """
        match = MatchData(
            id=self._generate_id(),
            source=MatchSource.TRANSCRIPTION,
            title=title or "Transcribed Match",
            status=ProcessingStatus.PROCESSING,
            created_at=datetime.now().isoformat()
        )

        # Identify cards mentioned
        cards = self._identify_cards(text)
        match.cards_identified = list(set(cards))

        # Parse play sequence
        actions = self._parse_play_sequence(text)
        match.actions = actions
        match.total_turns = max((a.turn for a in actions), default=0)

        # Detect decks
        match.player1_deck = self._detect_deck_archetype(cards)

        # Generate insights
        insights = self._generate_insights(match)
        match.insights = insights

        match.status = ProcessingStatus.COMPLETED
        match.processed_at = datetime.now().isoformat()

        self._matches.append(match)
        self._save_cache()
        return match

    def _identify_cards(self, text: str) -> list[str]:
        """Identify Pokemon TCG cards mentioned in text."""
        cards = []
        for pattern in CARD_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for m in matches:
                if isinstance(m, tuple):
                    cards.append(' '.join(m).strip())
                else:
                    cards.append(m.strip())
        return cards

    def _parse_play_sequence(self, text: str) -> list[PlayAction]:
        """Parse play sequence from transcription."""
        actions = []
        lines = text.split('\n')
        current_turn = 0
        current_player = "player1"

        for line in lines:
            line = line.strip().lower()
            if not line:
                continue

            # Detect turn changes
            turn_match = re.search(r'turn\s+(\d+)', line)
            if turn_match:
                current_turn = int(turn_match.group(1))

            # Detect player changes
            if 'opponent' in line or 'player 2' in line:
                current_player = "player2"
            elif 'my turn' in line or 'player 1' in line or 'i ' in line[:3]:
                current_player = "player1"

            # Detect actions
            for action_type, patterns in ACTION_PATTERNS.items():
                for pattern in patterns:
                    match = re.search(pattern, line)
                    if match:
                        card_name = match.group(1) if match.lastindex else ""
                        action = PlayAction(
                            turn=current_turn,
                            player=current_player,
                            action_type=action_type,
                            card_name=card_name.title() if card_name else "",
                            details=line[:100]
                        )
                        actions.append(action)
                        break

        return actions

    def _detect_deck_archetype(self, cards: list[str]) -> str:
        """Detect deck archetype based on cards identified."""
        archetypes = {
            'Charizard ex': ['charizard', 'pidgeot'],
            'Dragapult ex': ['dragapult', 'giratina'],
            'Gardevoir ex': ['gardevoir', 'kirlia'],
            'Lugia VSTAR': ['lugia', 'archeops'],
            'Regidrago VSTAR': ['regidrago', 'ogerpon'],
            'Gholdengo ex': ['gholdengo', 'gimmighoul'],
            'Roaring Moon ex': ['roaring moon', 'flutter mane'],
            'Lost Zone': ['comfey', 'cramorant', 'sableye'],
        }

        cards_lower = [c.lower() for c in cards]

        for archetype, keywords in archetypes.items():
            matches = sum(1 for kw in keywords if any(kw in c for c in cards_lower))
            if matches >= len(keywords) // 2 + 1:
                return archetype

        return "Unknown"

    def _generate_insights(self, match: MatchData) -> list[str]:
        """Generate insights from match data."""
        insights = []

        # Card count insights
        if match.cards_identified:
            insights.append(f"Identified {len(match.cards_identified)} unique cards")

        # Deck detection
        if match.player1_deck and match.player1_deck != "Unknown":
            insights.append(f"Detected deck archetype: {match.player1_deck}")

        # Turn analysis
        if match.total_turns > 0:
            insights.append(f"Match lasted {match.total_turns} turns")

        # Action analysis
        if match.actions:
            attack_count = sum(1 for a in match.actions if a.action_type == 'attack')
            ko_count = sum(1 for a in match.actions if a.action_type == 'knock_out')
            supporter_count = sum(1 for a in match.actions if a.action_type == 'supporter')

            if attack_count:
                insights.append(f"Total attacks: {attack_count}")
            if ko_count:
                insights.append(f"Knockouts recorded: {ko_count}")
            if supporter_count:
                insights.append(f"Supporters played: {supporter_count}")

        # Suggestions
        if not insights:
            insights.append("Add more detail to the transcription for better analysis")

        return insights

    # =========================================================================
    # MATCH MANAGEMENT
    # =========================================================================

    def get_all_matches(self) -> list[MatchData]:
        """Get all processed matches."""
        return sorted(self._matches, key=lambda m: m.created_at, reverse=True)

    def get_match(self, match_id: str) -> Optional[MatchData]:
        """Get a specific match by ID."""
        for match in self._matches:
            if match.id == match_id:
                return match
        return None

    def delete_match(self, match_id: str) -> bool:
        """Delete a match."""
        for i, match in enumerate(self._matches):
            if match.id == match_id:
                self._matches.pop(i)
                self._save_cache()
                return True
        return False

    def get_recent_insights(self, limit: int = 5) -> list[str]:
        """Get recent insights from all matches."""
        all_insights = []
        for match in self._matches[:limit]:
            for insight in match.insights[:2]:
                all_insights.append(f"{match.title[:20]}: {insight}")
        return all_insights[:limit]
