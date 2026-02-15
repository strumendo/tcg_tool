"""
User Database Service - SQLite persistence for user decks and settings.

This module handles:
- User deck storage (My Decks)
- Active deck management
- Competition calendar
- User preferences
"""

import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field, asdict


# Database path - use app-specific directory on Android
def get_db_path() -> Path:
    """Get platform-appropriate database path."""
    try:
        from android.storage import app_storage_path
        return Path(app_storage_path()) / "user_data.db"
    except ImportError:
        # Desktop fallback
        return Path(__file__).parent.parent / "user_data.db"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class UserCard:
    """Represents a card in a user's deck."""
    name: str
    set_code: str
    set_number: str
    quantity: int
    card_type: str  # pokemon, trainer, energy
    name_pt: str = ""
    subtype: str = ""  # supporter, item, stadium, tool
    regulation_mark: str = ""
    image_url: str = ""


@dataclass
class UserDeck:
    """Represents a user's saved deck."""
    id: int = 0
    name: str = "My Deck"
    cards: list[UserCard] = field(default_factory=list)
    is_active: bool = False
    is_complete: bool = False
    created_at: str = ""
    updated_at: str = ""
    notes: str = ""
    archetype: str = ""  # e.g., "charizard", "gardevoir"

    @property
    def total_cards(self) -> int:
        return sum(c.quantity for c in self.cards)

    @property
    def pokemon_count(self) -> int:
        return sum(c.quantity for c in self.cards if c.card_type == "pokemon")

    @property
    def trainer_count(self) -> int:
        return sum(c.quantity for c in self.cards if c.card_type == "trainer")

    @property
    def energy_count(self) -> int:
        return sum(c.quantity for c in self.cards if c.card_type == "energy")

    def validate(self) -> tuple[bool, list[str]]:
        """Validate deck and return (is_valid, list of issues)."""
        issues = []

        # Check total cards
        total = self.total_cards
        if total != 60:
            issues.append(f"Deck has {total}/60 cards")

        # Check 4-copy rule
        card_counts = {}
        for card in self.cards:
            # Skip basic energy
            if "basic" in card.name.lower() and "energy" in card.name.lower():
                continue
            key = card.name.lower()
            card_counts[key] = card_counts.get(key, 0) + card.quantity
            if card_counts[key] > 4:
                issues.append(f"More than 4 copies of {card.name}")

        return len(issues) == 0, issues


@dataclass
class Competition:
    """Represents a competition event."""
    id: int = 0
    name: str = ""
    event_type: str = ""  # online, league_cup, league_challenge, regional, etc.
    event_format: str = "Standard"  # Standard, Expanded
    date: str = ""
    time: str = ""
    location: str = ""
    deck_id: int = 0  # Associated deck
    wins: int = 0
    losses: int = 0
    draws: int = 0
    placement: int = 0
    notes: str = ""
    rounds: str = ""  # JSON string of round details
    created_at: str = ""


# =============================================================================
# DATABASE SERVICE
# =============================================================================

class UserDatabase:
    """SQLite database service for user data."""

    def __init__(self, db_path: Path = None):
        self.db_path = db_path or get_db_path()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initialize database tables."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # User decks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_decks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                cards TEXT NOT NULL,
                is_active INTEGER DEFAULT 0,
                is_complete INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                notes TEXT DEFAULT '',
                archetype TEXT DEFAULT ''
            )
        """)

        # Competitions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS competitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_format TEXT DEFAULT 'Standard',
                date TEXT NOT NULL,
                time TEXT DEFAULT '',
                location TEXT DEFAULT '',
                deck_id INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                draws INTEGER DEFAULT 0,
                placement INTEGER DEFAULT 0,
                notes TEXT DEFAULT '',
                rounds TEXT DEFAULT '[]',
                created_at TEXT NOT NULL,
                FOREIGN KEY (deck_id) REFERENCES user_decks(id)
            )
        """)

        # User settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_decks_active ON user_decks(is_active)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_competitions_date ON competitions(date)")

        conn.commit()
        conn.close()

    # -------------------------------------------------------------------------
    # DECK OPERATIONS
    # -------------------------------------------------------------------------

    def save_deck(self, deck: UserDeck) -> int:
        """Save or update a deck. Returns deck ID."""
        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        cards_json = json.dumps([asdict(c) for c in deck.cards])
        deck.is_complete = deck.total_cards == 60

        if deck.id > 0:
            # Update existing
            cursor.execute("""
                UPDATE user_decks
                SET name = ?, cards = ?, is_complete = ?, updated_at = ?,
                    notes = ?, archetype = ?
                WHERE id = ?
            """, (deck.name, cards_json, deck.is_complete, now,
                  deck.notes, deck.archetype, deck.id))
            deck_id = deck.id
        else:
            # Insert new
            cursor.execute("""
                INSERT INTO user_decks (name, cards, is_active, is_complete,
                                        created_at, updated_at, notes, archetype)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (deck.name, cards_json, 0, deck.is_complete,
                  now, now, deck.notes, deck.archetype))
            deck_id = cursor.lastrowid

        conn.commit()
        conn.close()
        return deck_id

    def get_deck(self, deck_id: int) -> Optional[UserDeck]:
        """Get a deck by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_decks WHERE id = ?", (deck_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return self._row_to_deck(row)

    def get_all_decks(self) -> list[UserDeck]:
        """Get all user decks."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_decks ORDER BY updated_at DESC")
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_deck(row) for row in rows]

    def get_active_deck(self) -> Optional[UserDeck]:
        """Get the currently active deck."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_decks WHERE is_active = 1 LIMIT 1")
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return self._row_to_deck(row)

    def set_active_deck(self, deck_id: int) -> bool:
        """Set a deck as active (only one can be active)."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Clear previous active
        cursor.execute("UPDATE user_decks SET is_active = 0")
        # Set new active
        cursor.execute("UPDATE user_decks SET is_active = 1 WHERE id = ?", (deck_id,))

        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

    def delete_deck(self, deck_id: int) -> bool:
        """Delete a deck."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_decks WHERE id = ?", (deck_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

    def _row_to_deck(self, row: sqlite3.Row) -> UserDeck:
        """Convert database row to UserDeck object."""
        cards_data = json.loads(row['cards'])
        cards = [UserCard(**c) for c in cards_data]

        return UserDeck(
            id=row['id'],
            name=row['name'],
            cards=cards,
            is_active=bool(row['is_active']),
            is_complete=bool(row['is_complete']),
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            notes=row['notes'] or '',
            archetype=row['archetype'] or ''
        )

    # -------------------------------------------------------------------------
    # COMPETITION OPERATIONS
    # -------------------------------------------------------------------------

    def save_competition(self, comp: Competition) -> int:
        """Save or update a competition."""
        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        if comp.id > 0:
            cursor.execute("""
                UPDATE competitions
                SET name = ?, event_type = ?, event_format = ?, date = ?,
                    time = ?, location = ?, deck_id = ?, wins = ?, losses = ?,
                    draws = ?, placement = ?, notes = ?, rounds = ?
                WHERE id = ?
            """, (comp.name, comp.event_type, comp.event_format, comp.date,
                  comp.time, comp.location, comp.deck_id, comp.wins, comp.losses,
                  comp.draws, comp.placement, comp.notes, comp.rounds, comp.id))
            comp_id = comp.id
        else:
            cursor.execute("""
                INSERT INTO competitions (name, event_type, event_format, date,
                    time, location, deck_id, wins, losses, draws, placement,
                    notes, rounds, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (comp.name, comp.event_type, comp.event_format, comp.date,
                  comp.time, comp.location, comp.deck_id, comp.wins, comp.losses,
                  comp.draws, comp.placement, comp.notes, comp.rounds, now))
            comp_id = cursor.lastrowid

        conn.commit()
        conn.close()
        return comp_id

    def get_competitions(self, upcoming_only: bool = False) -> list[Competition]:
        """Get all competitions, optionally filtered to upcoming only."""
        conn = self._get_connection()
        cursor = conn.cursor()

        if upcoming_only:
            today = datetime.now().strftime("%Y-%m-%d")
            cursor.execute(
                "SELECT * FROM competitions WHERE date >= ? ORDER BY date ASC",
                (today,)
            )
        else:
            cursor.execute("SELECT * FROM competitions ORDER BY date DESC")

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_competition(row) for row in rows]

    def delete_competition(self, comp_id: int) -> bool:
        """Delete a competition."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM competitions WHERE id = ?", (comp_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

    def _row_to_competition(self, row: sqlite3.Row) -> Competition:
        """Convert database row to Competition object."""
        return Competition(
            id=row['id'],
            name=row['name'],
            event_type=row['event_type'],
            event_format=row['event_format'],
            date=row['date'],
            time=row['time'] or '',
            location=row['location'] or '',
            deck_id=row['deck_id'],
            wins=row['wins'],
            losses=row['losses'],
            draws=row['draws'],
            placement=row['placement'],
            notes=row['notes'] or '',
            rounds=row['rounds'] or '[]',
            created_at=row['created_at']
        )

    # -------------------------------------------------------------------------
    # STATISTICS
    # -------------------------------------------------------------------------

    def get_player_stats(self) -> dict:
        """Calculate player statistics."""
        comps = self.get_competitions()

        if not comps:
            return {
                'total_events': 0,
                'total_wins': 0,
                'total_losses': 0,
                'total_draws': 0,
                'win_rate': 0.0,
                'best_placement': 0,
                'most_played_deck': None
            }

        total_wins = sum(c.wins for c in comps)
        total_losses = sum(c.losses for c in comps)
        total_draws = sum(c.draws for c in comps)
        total_games = total_wins + total_losses + total_draws

        win_rate = (total_wins / total_games * 100) if total_games > 0 else 0.0

        # Best placement (lower is better, 0 means no placement recorded)
        placements = [c.placement for c in comps if c.placement > 0]
        best_placement = min(placements) if placements else 0

        # Most played deck
        deck_counts = {}
        for c in comps:
            if c.deck_id > 0:
                deck_counts[c.deck_id] = deck_counts.get(c.deck_id, 0) + 1

        most_played_deck_id = max(deck_counts, key=deck_counts.get) if deck_counts else None

        return {
            'total_events': len(comps),
            'total_wins': total_wins,
            'total_losses': total_losses,
            'total_draws': total_draws,
            'win_rate': win_rate,
            'best_placement': best_placement,
            'most_played_deck_id': most_played_deck_id
        }

    # -------------------------------------------------------------------------
    # SETTINGS
    # -------------------------------------------------------------------------

    def get_setting(self, key: str, default: str = "") -> str:
        """Get a user setting."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM user_settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        return row['value'] if row else default

    def set_setting(self, key: str, value: str):
        """Set a user setting."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO user_settings (key, value) VALUES (?, ?)
        """, (key, value))
        conn.commit()
        conn.close()
