"""
Background Sync Service for TCG Tool Mobile App
Handles background data synchronization with API
"""

import threading
from typing import Optional, Callable
from .api_client import APIClient
from .offline_cache import OfflineCache


class SyncService:
    """Background synchronization service for offline cache"""

    def __init__(self, api_client: APIClient, cache: OfflineCache):
        """
        Initialize sync service

        Args:
            api_client: API client instance
            cache: Offline cache instance
        """
        self.api_client = api_client
        self.cache = cache
        self.is_syncing = False
        self.on_sync_complete: Optional[Callable[[bool, str], None]] = None

    def sync_all(self) -> bool:
        """
        Synchronize all data from API to cache

        Returns:
            True if sync successful, False otherwise
        """
        if self.is_syncing:
            print("Sync already in progress")
            return False

        self.is_syncing = True
        success = True
        error_message = ""

        try:
            # Sync meta decks
            print("Syncing meta decks...")
            try:
                decks = self.api_client.get_meta_decks()
                self.cache.cache_meta_decks(decks)
                print(f"Cached {len(decks)} meta decks")
            except Exception as e:
                print(f"Failed to sync meta decks: {e}")
                error_message += f"Meta decks sync failed: {e}\n"
                success = False

            # Sync matchups
            print("Syncing matchups...")
            try:
                matchups = self.api_client.get_matchups()
                self.cache.cache_matchups(matchups)
                print(f"Cached {len(matchups)} matchups")
            except Exception as e:
                print(f"Failed to sync matchups: {e}")
                error_message += f"Matchups sync failed: {e}\n"
                success = False

            # Note: We don't sync all cards at once (too large)
            # Cards are cached on-demand as they are searched/viewed

            print("Sync completed" if success else "Sync completed with errors")

        except Exception as e:
            print(f"Sync failed: {e}")
            error_message = str(e)
            success = False

        finally:
            self.is_syncing = False

            # Trigger callback if registered
            if self.on_sync_complete:
                self.on_sync_complete(success, error_message)

        return success

    def sync_in_background(self, on_complete: Optional[Callable[[bool, str], None]] = None):
        """
        Start background sync in a separate thread

        Args:
            on_complete: Callback function called when sync completes
                        Signature: callback(success: bool, error_message: str)
        """
        if on_complete:
            self.on_sync_complete = on_complete

        def sync_thread():
            try:
                self.sync_all()
            except Exception as e:
                print(f"Background sync error: {e}")
                if self.on_sync_complete:
                    self.on_sync_complete(False, str(e))

        thread = threading.Thread(target=sync_thread, daemon=True)
        thread.start()

    def sync_meta_decks(self) -> bool:
        """
        Sync only meta decks

        Returns:
            True if sync successful, False otherwise
        """
        try:
            decks = self.api_client.get_meta_decks()
            self.cache.cache_meta_decks(decks)
            print(f"Synced {len(decks)} meta decks")
            return True
        except Exception as e:
            print(f"Failed to sync meta decks: {e}")
            return False

    def sync_matchups(self) -> bool:
        """
        Sync only matchups

        Returns:
            True if sync successful, False otherwise
        """
        try:
            matchups = self.api_client.get_matchups()
            self.cache.cache_matchups(matchups)
            print(f"Synced {len(matchups)} matchups")
            return True
        except Exception as e:
            print(f"Failed to sync matchups: {e}")
            return False

    def is_cache_fresh(self, key: str, max_age_hours: int = 24) -> bool:
        """
        Check if cached data is fresh

        Args:
            key: Cache key (e.g., 'meta_decks', 'cards')
            max_age_hours: Maximum age in hours

        Returns:
            True if cache is fresh, False otherwise
        """
        return self.cache.is_cache_fresh(key, max_age_hours)

    def get_sync_status(self) -> dict:
        """
        Get current sync status

        Returns:
            Dictionary with sync status information
        """
        return {
            'is_syncing': self.is_syncing,
            'cache_stats': self.cache.get_cache_stats(),
            'meta_decks_fresh': self.cache.is_cache_fresh('meta_decks', 24),
            'matchups_fresh': self.cache.is_cache_fresh('matchups', 24),
        }
