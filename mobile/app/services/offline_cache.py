"""
Offline Cache for TCG Tool Mobile App
SQLite-based caching for offline functionality
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
from kivy.utils import platform


class OfflineCache:
    """SQLite-based offline cache for API data"""

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize offline cache

        Args:
            db_path: Path to SQLite database. If None, auto-detects based on platform
                    - Android: uses Kivy's app_storage_path
                    - Desktop: uses ./cache.db in current directory
        """
        if db_path is None:
            if platform == 'android':
                from android.storage import app_storage_path
                storage_path = app_storage_path()
                db_path = str(Path(storage_path) / 'tcg_cache.db')
            else:
                db_path = 'cache.db'

        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Meta decks cache
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cached_meta_decks (
                deck_id TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                cached_at TEXT NOT NULL
            )
        ''')

        # Cards cache
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cached_cards (
                card_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                data TEXT NOT NULL,
                cached_at TEXT NOT NULL
            )
        ''')

        # Create index on card name for faster searches
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_card_name
            ON cached_cards(name)
        ''')

        # Matchups cache
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cached_matchups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                cached_at TEXT NOT NULL
            )
        ''')

        # Cache metadata (for tracking freshness)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache_metadata (
                key TEXT PRIMARY KEY,
                last_updated TEXT NOT NULL
            )
        ''')

        conn.commit()
        conn.close()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        return sqlite3.connect(self.db_path)

    # Meta Decks
    def cache_meta_decks(self, decks: List[Dict[str, Any]]):
        """
        Cache meta decks data

        Args:
            decks: List of meta deck dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()

        try:
            for deck in decks:
                deck_id = deck.get('id') or deck.get('deck_id')
                cursor.execute(
                    'INSERT OR REPLACE INTO cached_meta_decks (deck_id, data, cached_at) VALUES (?, ?, ?)',
                    (deck_id, json.dumps(deck), now)
                )

            # Update metadata
            cursor.execute(
                'INSERT OR REPLACE INTO cache_metadata (key, last_updated) VALUES (?, ?)',
                ('meta_decks', now)
            )

            conn.commit()
        finally:
            conn.close()

    def get_cached_meta_decks(self) -> List[Dict[str, Any]]:
        """
        Retrieve cached meta decks

        Returns:
            List of cached meta deck dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT data FROM cached_meta_decks')
            rows = cursor.fetchall()

            decks = []
            for row in rows:
                decks.append(json.loads(row[0]))

            return decks
        finally:
            conn.close()

    # Cards
    def cache_cards(self, cards: List[Dict[str, Any]]):
        """
        Cache card data

        Args:
            cards: List of card dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()

        try:
            for card in cards:
                card_id = card.get('id') or card.get('card_id')
                name = card.get('name', '').lower()
                cursor.execute(
                    'INSERT OR REPLACE INTO cached_cards (card_id, name, data, cached_at) VALUES (?, ?, ?, ?)',
                    (card_id, name, json.dumps(card), now)
                )

            # Update metadata
            cursor.execute(
                'INSERT OR REPLACE INTO cache_metadata (key, last_updated) VALUES (?, ?)',
                ('cards', now)
            )

            conn.commit()
        finally:
            conn.close()

    def get_cached_cards(self, query: str = '') -> List[Dict[str, Any]]:
        """
        Retrieve cached cards, optionally filtered by name

        Args:
            query: Card name search query (case-insensitive)

        Returns:
            List of cached card dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            if query:
                query_lower = query.lower()
                cursor.execute(
                    'SELECT data FROM cached_cards WHERE name LIKE ?',
                    (f'%{query_lower}%',)
                )
            else:
                cursor.execute('SELECT data FROM cached_cards')

            rows = cursor.fetchall()

            cards = []
            for row in rows:
                cards.append(json.loads(row[0]))

            return cards
        finally:
            conn.close()

    # Matchups
    def cache_matchups(self, matchups: List[Dict[str, Any]]):
        """
        Cache matchup data

        Args:
            matchups: List of matchup dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()

        try:
            # Clear existing matchups
            cursor.execute('DELETE FROM cached_matchups')

            # Insert new matchups
            for matchup in matchups:
                cursor.execute(
                    'INSERT INTO cached_matchups (data, cached_at) VALUES (?, ?)',
                    (json.dumps(matchup), now)
                )

            # Update metadata
            cursor.execute(
                'INSERT OR REPLACE INTO cache_metadata (key, last_updated) VALUES (?, ?)',
                ('matchups', now)
            )

            conn.commit()
        finally:
            conn.close()

    def get_cached_matchups(self) -> List[Dict[str, Any]]:
        """
        Retrieve cached matchups

        Returns:
            List of cached matchup dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT data FROM cached_matchups')
            rows = cursor.fetchall()

            matchups = []
            for row in rows:
                matchups.append(json.loads(row[0]))

            return matchups
        finally:
            conn.close()

    # Cache Freshness
    def is_cache_fresh(self, key: str, max_age_hours: int = 24) -> bool:
        """
        Check if cached data is still fresh

        Args:
            key: Cache key (e.g., 'meta_decks', 'cards')
            max_age_hours: Maximum age in hours before cache is considered stale

        Returns:
            True if cache is fresh, False otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                'SELECT last_updated FROM cache_metadata WHERE key = ?',
                (key,)
            )
            row = cursor.fetchone()

            if not row:
                return False

            last_updated = datetime.fromisoformat(row[0])
            age = datetime.now() - last_updated

            return age < timedelta(hours=max_age_hours)
        finally:
            conn.close()

    def clear_cache(self, key: Optional[str] = None):
        """
        Clear cached data

        Args:
            key: Specific cache key to clear. If None, clears all caches.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            if key is None:
                # Clear all caches
                cursor.execute('DELETE FROM cached_meta_decks')
                cursor.execute('DELETE FROM cached_cards')
                cursor.execute('DELETE FROM cached_matchups')
                cursor.execute('DELETE FROM cache_metadata')
            elif key == 'meta_decks':
                cursor.execute('DELETE FROM cached_meta_decks')
                cursor.execute('DELETE FROM cache_metadata WHERE key = ?', (key,))
            elif key == 'cards':
                cursor.execute('DELETE FROM cached_cards')
                cursor.execute('DELETE FROM cache_metadata WHERE key = ?', (key,))
            elif key == 'matchups':
                cursor.execute('DELETE FROM cached_matchups')
                cursor.execute('DELETE FROM cache_metadata WHERE key = ?', (key,))

            conn.commit()
        finally:
            conn.close()

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics

        Returns:
            Dictionary with cache statistics (size, last updated, etc.)
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            stats = {}

            # Meta decks count
            cursor.execute('SELECT COUNT(*) FROM cached_meta_decks')
            stats['meta_decks_count'] = cursor.fetchone()[0]

            # Cards count
            cursor.execute('SELECT COUNT(*) FROM cached_cards')
            stats['cards_count'] = cursor.fetchone()[0]

            # Matchups count
            cursor.execute('SELECT COUNT(*) FROM cached_matchups')
            stats['matchups_count'] = cursor.fetchone()[0]

            # Last updated times
            cursor.execute('SELECT key, last_updated FROM cache_metadata')
            stats['last_updated'] = {}
            for row in cursor.fetchall():
                stats['last_updated'][row[0]] = row[1]

            return stats
        finally:
            conn.close()
