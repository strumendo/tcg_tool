"""
Tests for UserDatabase

Tests deck storage, retrieval, and management.
"""

import unittest
import sys
import os
import tempfile
import shutil

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.user_database import UserDatabase, UserDeck, UserCard


class TestUserDatabase(unittest.TestCase):
    """Test cases for UserDatabase."""

    def setUp(self):
        """Set up test fixtures with temporary database."""
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_decks.db")
        self.db = UserDatabase(db_path=self.db_path)

    def tearDown(self):
        """Clean up temporary files."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_card(self, name, quantity, card_type="pokemon", set_code="OBF", set_number="1"):
        """Helper to create a UserCard with required fields."""
        return UserCard(
            name=name,
            set_code=set_code,
            set_number=set_number,
            quantity=quantity,
            card_type=card_type
        )

    # =========================================================================
    # DECK CRUD TESTS
    # =========================================================================

    def test_save_new_deck(self):
        """Test saving a new deck."""
        deck = UserDeck(name="Test Deck")
        deck.cards = [
            self._create_card("Charizard ex", 4, "pokemon", "OBF", "125"),
            self._create_card("Arven", 4, "trainer", "SVI", "166"),
        ]

        deck_id = self.db.save_deck(deck)

        self.assertIsNotNone(deck_id)
        self.assertGreater(deck_id, 0)

    def test_get_deck_by_id(self):
        """Test retrieving a deck by ID."""
        deck = UserDeck(name="Test Deck")
        deck.cards = [
            self._create_card("Charizard ex", 4, "pokemon", "OBF", "125"),
        ]
        deck_id = self.db.save_deck(deck)

        retrieved = self.db.get_deck(deck_id)

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "Test Deck")
        self.assertEqual(len(retrieved.cards), 1)
        self.assertEqual(retrieved.cards[0].name, "Charizard ex")

    def test_get_all_decks(self):
        """Test retrieving all decks."""
        # Save multiple decks
        for i in range(3):
            deck = UserDeck(name=f"Deck {i}")
            self.db.save_deck(deck)

        decks = self.db.get_all_decks()

        self.assertEqual(len(decks), 3)

    def test_update_deck(self):
        """Test updating an existing deck."""
        deck = UserDeck(name="Original Name")
        deck_id = self.db.save_deck(deck)

        # Retrieve and modify
        deck = self.db.get_deck(deck_id)
        deck.name = "Updated Name"
        deck.cards = [
            self._create_card("Pikachu", 4, "pokemon", "SVI", "1"),
        ]
        self.db.save_deck(deck)

        # Verify update
        updated = self.db.get_deck(deck_id)
        self.assertEqual(updated.name, "Updated Name")
        self.assertEqual(len(updated.cards), 1)

    def test_delete_deck(self):
        """Test deleting a deck."""
        deck = UserDeck(name="To Delete")
        deck_id = self.db.save_deck(deck)

        result = self.db.delete_deck(deck_id)

        self.assertTrue(result)
        self.assertIsNone(self.db.get_deck(deck_id))

    def test_delete_nonexistent_deck(self):
        """Test deleting a deck that doesn't exist."""
        result = self.db.delete_deck(9999)
        self.assertFalse(result)

    # =========================================================================
    # ACTIVE DECK TESTS
    # =========================================================================

    def test_set_active_deck(self):
        """Test setting a deck as active."""
        deck1 = UserDeck(name="Deck 1")
        deck2 = UserDeck(name="Deck 2")
        id1 = self.db.save_deck(deck1)
        id2 = self.db.save_deck(deck2)

        self.db.set_active_deck(id1)
        active = self.db.get_active_deck()

        self.assertIsNotNone(active)
        self.assertEqual(active.id, id1)

    def test_only_one_active_deck(self):
        """Test that only one deck can be active at a time."""
        deck1 = UserDeck(name="Deck 1")
        deck2 = UserDeck(name="Deck 2")
        id1 = self.db.save_deck(deck1)
        id2 = self.db.save_deck(deck2)

        self.db.set_active_deck(id1)
        self.db.set_active_deck(id2)

        # Deck 2 should be active, Deck 1 should not
        deck1_retrieved = self.db.get_deck(id1)
        deck2_retrieved = self.db.get_deck(id2)

        self.assertFalse(deck1_retrieved.is_active)
        self.assertTrue(deck2_retrieved.is_active)

    def test_get_active_deck_none(self):
        """Test getting active deck when none is set."""
        deck = UserDeck(name="Inactive Deck")
        self.db.save_deck(deck)

        active = self.db.get_active_deck()
        self.assertIsNone(active)

    # =========================================================================
    # DECK PROPERTIES TESTS
    # =========================================================================

    def test_deck_total_cards(self):
        """Test deck total cards calculation."""
        deck = UserDeck(name="Test")
        deck.cards = [
            self._create_card("Card 1", 4),
            self._create_card("Card 2", 3),
            self._create_card("Card 3", 10),
        ]

        self.assertEqual(deck.total_cards, 17)

    def test_deck_pokemon_count(self):
        """Test deck Pokemon count."""
        deck = UserDeck(name="Test")
        deck.cards = [
            self._create_card("Charizard", 4, "pokemon"),
            self._create_card("Pikachu", 2, "pokemon"),
            self._create_card("Arven", 4, "trainer"),
        ]

        self.assertEqual(deck.pokemon_count, 6)

    def test_deck_trainer_count(self):
        """Test deck Trainer count."""
        deck = UserDeck(name="Test")
        deck.cards = [
            self._create_card("Arven", 4, "trainer"),
            self._create_card("Iono", 4, "trainer"),
            self._create_card("Charizard", 4, "pokemon"),
        ]

        self.assertEqual(deck.trainer_count, 8)

    def test_deck_energy_count(self):
        """Test deck Energy count."""
        deck = UserDeck(name="Test")
        deck.cards = [
            self._create_card("Fire Energy", 10, "energy"),
            self._create_card("Water Energy", 5, "energy"),
            self._create_card("Charizard", 4, "pokemon"),
        ]

        self.assertEqual(deck.energy_count, 15)

    def test_deck_is_complete(self):
        """Test deck completeness via total_cards."""
        deck = UserDeck(name="Test")

        # Incomplete deck (30 cards)
        deck.cards = [self._create_card("Card", 30)]
        self.assertEqual(deck.total_cards, 30)
        self.assertNotEqual(deck.total_cards, 60)

        # Complete deck (60 cards)
        deck.cards = [self._create_card("Card", 60)]
        self.assertEqual(deck.total_cards, 60)


class TestUserCard(unittest.TestCase):
    """Test cases for UserCard dataclass."""

    def test_card_creation(self):
        """Test creating a UserCard."""
        card = UserCard(
            name="Charizard ex",
            set_code="OBF",
            set_number="125",
            quantity=4,
            card_type="pokemon",
            regulation_mark="G"
        )

        self.assertEqual(card.name, "Charizard ex")
        self.assertEqual(card.quantity, 4)
        self.assertEqual(card.set_code, "OBF")
        self.assertEqual(card.regulation_mark, "G")

    def test_card_with_defaults(self):
        """Test UserCard optional field defaults."""
        card = UserCard(
            name="Test Card",
            set_code="TST",
            set_number="1",
            quantity=1,
            card_type="pokemon"
        )

        self.assertEqual(card.name, "Test Card")
        self.assertEqual(card.subtype, "")
        self.assertEqual(card.regulation_mark, "")


if __name__ == '__main__':
    unittest.main()
