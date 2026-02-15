"""
API Client for TCG Tool Backend
Handles all HTTP communication with the FastAPI backend
"""

import httpx
from typing import Optional, List, Dict, Any
from kivy.utils import platform


class APIClient:
    """Client for interacting with TCG Tool FastAPI backend"""

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize API client

        Args:
            base_url: Base URL for API. If None, auto-detects based on platform
                     - Android emulator: http://10.0.2.2:8000/api/v1
                     - Desktop/Other: http://localhost:8000/api/v1
        """
        if base_url is None:
            if platform == 'android':
                # Android emulator uses 10.0.2.2 to access host machine
                base_url = 'http://10.0.2.2:8000/api/v1'
            else:
                # Desktop and other platforms use localhost
                base_url = 'http://localhost:8000/api/v1'

        self.base_url = base_url.rstrip('/')
        self.timeout = 15.0  # 15 second timeout

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform GET request

        Args:
            endpoint: API endpoint (will be appended to base_url)
            params: Query parameters

        Returns:
            JSON response as dictionary

        Raises:
            httpx.HTTPError: On network or HTTP errors
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            print(f"API request failed: {e}")
            raise

    def _post(self, endpoint: str, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform POST request

        Args:
            endpoint: API endpoint (will be appended to base_url)
            json: JSON body

        Returns:
            JSON response as dictionary

        Raises:
            httpx.HTTPError: On network or HTTP errors
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, json=json)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            print(f"API request failed: {e}")
            raise

    def _delete(self, endpoint: str) -> None:
        """
        Perform DELETE request

        Args:
            endpoint: API endpoint (will be appended to base_url)

        Raises:
            httpx.HTTPError: On network or HTTP errors
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.delete(url)
                response.raise_for_status()
        except httpx.HTTPError as e:
            print(f"API request failed: {e}")
            raise

    # Meta Decks
    def get_meta_decks(self) -> List[Dict[str, Any]]:
        """
        Get list of meta decks

        Returns:
            List of meta deck dictionaries
        """
        return self._get('meta/decks')

    def get_meta_deck(self, deck_id: str) -> Dict[str, Any]:
        """
        Get specific meta deck by ID

        Args:
            deck_id: Deck identifier

        Returns:
            Meta deck dictionary with full details
        """
        return self._get(f'meta/decks/{deck_id}')

    def get_matchups(self) -> List[Dict[str, Any]]:
        """
        Get matchup data for meta decks

        Returns:
            List of matchup dictionaries
        """
        return self._get('meta/matchups')

    def get_tiers(self) -> List[Dict[str, Any]]:
        """
        Get tier list

        Returns:
            List of tier dictionaries
        """
        return self._get('meta/tiers')

    # Cards
    def search_cards(
        self,
        name: Optional[str] = None,
        card_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search for cards

        Args:
            name: Card name to search for
            card_type: Filter by card type (pokemon, trainer, energy)
            limit: Maximum number of results

        Returns:
            List of card dictionaries
        """
        params = {'limit': limit}
        if name:
            params['name'] = name
        if card_type:
            params['type'] = card_type

        return self._get('cards/search', params=params)

    def get_card(self, card_id: int) -> Dict[str, Any]:
        """
        Get specific card by ID

        Args:
            card_id: Card identifier

        Returns:
            Card dictionary with full details
        """
        return self._get(f'cards/{card_id}')

    # User Decks
    def get_user_decks(self) -> List[Dict[str, Any]]:
        """
        Get user's personal decks

        Returns:
            List of user deck dictionaries
        """
        return self._get('decks')

    def import_deck(self, deck_text: str, name: str) -> Dict[str, Any]:
        """
        Import a deck from text format

        Args:
            deck_text: Deck list in PTCGO/TCG Live format
            name: Name for the deck

        Returns:
            Created deck dictionary
        """
        return self._post('decks/import', json={'text': deck_text, 'name': name})

    def get_deck(self, deck_id: int) -> Dict[str, Any]:
        """
        Get specific user deck by ID

        Args:
            deck_id: Deck identifier

        Returns:
            Deck dictionary with full details
        """
        return self._get(f'decks/{deck_id}')

    def delete_deck(self, deck_id: int) -> None:
        """
        Delete a user deck

        Args:
            deck_id: Deck identifier
        """
        self._delete(f'decks/{deck_id}')

    # Battles
    def get_battles(self) -> List[Dict[str, Any]]:
        """
        Get user's battle history

        Returns:
            List of battle dictionaries
        """
        return self._get('battles')

    def create_battle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new battle record

        Args:
            data: Battle data (deck_id, opponent_deck, result, etc.)

        Returns:
            Created battle dictionary
        """
        return self._post('battles', json=data)

    def analyze_battle(self, battle_id: int) -> Dict[str, Any]:
        """
        Get AI analysis for a battle

        Args:
            battle_id: Battle identifier

        Returns:
            Analysis dictionary with insights
        """
        return self._get(f'battles/{battle_id}/analyze')

    # Chat
    def chat_message(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        deck_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Send a chat message to AI assistant

        Args:
            message: User's message
            history: Conversation history
            deck_id: Optional deck context

        Returns:
            Response dictionary with AI reply
        """
        payload = {'message': message}
        if history:
            payload['history'] = history
        if deck_id:
            payload['deck_id'] = deck_id

        return self._post('chat', json=payload)

    # Tournaments & News
    def get_tournaments(self) -> List[Dict[str, Any]]:
        """
        Get upcoming tournaments

        Returns:
            List of tournament dictionaries
        """
        return self._get('tournaments')

    def get_news(self) -> List[Dict[str, Any]]:
        """
        Get latest Pokemon TCG news

        Returns:
            List of news article dictionaries
        """
        return self._get('news')
