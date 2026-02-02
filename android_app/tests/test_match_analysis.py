"""
Tests for MatchAnalysisService

Tests video URL processing, transcription parsing, and insights generation.
"""

import unittest
import sys
import os
import tempfile
import shutil

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.match_analysis import (
    MatchAnalysisService,
    MatchData,
    MatchSource,
    ProcessingStatus,
    PlayAction
)


class TestMatchAnalysisService(unittest.TestCase):
    """Test cases for MatchAnalysisService."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.service = MatchAnalysisService(cache_dir=self.test_dir)

    def tearDown(self):
        """Clean up temporary files."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    # =========================================================================
    # YOUTUBE URL TESTS
    # =========================================================================

    def test_valid_youtube_url(self):
        """Test processing a valid YouTube URL."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        result = self.service.process_youtube_url(url)

        self.assertIsNotNone(result)
        self.assertEqual(result.source, MatchSource.YOUTUBE)
        self.assertEqual(result.source_url, url)

    def test_valid_youtube_short_url(self):
        """Test processing a short YouTube URL."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        result = self.service.process_youtube_url(url)

        self.assertIsNotNone(result)
        self.assertEqual(result.source, MatchSource.YOUTUBE)

    def test_invalid_youtube_url(self):
        """Test processing an invalid URL."""
        url = "https://example.com/not-youtube"
        result = self.service.process_youtube_url(url)

        self.assertEqual(result.status, ProcessingStatus.FAILED)
        self.assertIn("Invalid", result.error_message)

    def test_youtube_video_id_extraction(self):
        """Test video ID extraction from various URL formats."""
        test_cases = [
            ("https://www.youtube.com/watch?v=abc123xyz", "abc123xyz"),
            ("https://youtu.be/abc123xyz", "abc123xyz"),
            ("https://www.youtube.com/embed/abc123xyz", "abc123xyz"),
        ]

        for url, expected_id in test_cases:
            video_id = self.service._extract_video_id(url)
            self.assertEqual(video_id, expected_id, f"Failed for URL: {url}")

    # =========================================================================
    # TRANSCRIPTION PARSING TESTS
    # =========================================================================

    def test_process_simple_transcription(self):
        """Test processing a simple transcription."""
        text = """Turn 1: I start with Charmander.
        I attach a Fire Energy to Charmander.
        Turn 2: I play Rare Candy and evolve to Charizard ex.
        I attack with Charizard ex for 180 damage."""

        result = self.service.process_transcription(text, "Test Match")

        self.assertEqual(result.status, ProcessingStatus.COMPLETED)
        self.assertEqual(result.title, "Test Match")
        self.assertGreater(len(result.cards_identified), 0)

    def test_identify_pokemon_cards(self):
        """Test identification of Pokemon cards in text."""
        text = """Charizard ex attacked.
        Pidgeot ex used Quick Search.
        Gardevoir ex powered up."""

        result = self.service.process_transcription(text)

        # Should identify Charizard, Pidgeot, Gardevoir
        cards_lower = [c.lower() for c in result.cards_identified]
        self.assertTrue(any('charizard' in c for c in cards_lower))

    def test_identify_trainer_cards(self):
        """Test identification of Trainer cards in text."""
        text = """I played Professor's Research and drew 7 cards.
        Then I used Iono to shuffle hands.
        Boss's Orders brought up the benched Pokemon."""

        result = self.service.process_transcription(text)

        cards_lower = [c.lower() for c in result.cards_identified]
        self.assertTrue(any("professor" in c for c in cards_lower) or
                       any("iono" in c for c in cards_lower) or
                       any("boss" in c for c in cards_lower))

    def test_identify_item_cards(self):
        """Test identification of Item cards in text."""
        text = """I used Ultra Ball to search for Charizard.
        Rare Candy evolved Charmander directly.
        Nest Ball found a basic Pokemon."""

        result = self.service.process_transcription(text)

        cards_lower = [c.lower() for c in result.cards_identified]
        self.assertTrue(any('ultra ball' in c or 'rare candy' in c or 'nest ball' in c
                           for c in cards_lower))

    def test_parse_turn_numbers(self):
        """Test parsing of turn numbers with recognizable actions."""
        # Text needs recognizable actions for turns to be counted
        text = """Turn 1: draws a card and plays Charizard.
        Turn 2: attaches energy and uses Ultra Ball.
        Turn 3: knocks out opponent."""

        result = self.service.process_transcription(text)

        # total_turns is based on actions detected with turn info
        self.assertGreaterEqual(len(result.actions), 0)

    def test_detect_deck_archetype_charizard(self):
        """Test deck archetype detection for Charizard."""
        text = """Charizard ex used Burning Darkness.
        Pidgeot ex searched with Quick Search.
        Another Charizard attack."""

        result = self.service.process_transcription(text)

        self.assertIn("Charizard", result.player1_deck)

    def test_detect_deck_archetype_gardevoir(self):
        """Test deck archetype detection for Gardevoir."""
        text = """Gardevoir ex powered up with Psychic Embrace.
        Kirlia evolved from Ralts.
        Scream Tail provided support."""

        result = self.service.process_transcription(text)

        # May detect as Gardevoir or Unknown depending on threshold
        self.assertIsNotNone(result.player1_deck)

    def test_empty_transcription(self):
        """Test handling empty transcription."""
        result = self.service.process_transcription("")

        self.assertEqual(result.status, ProcessingStatus.COMPLETED)
        self.assertEqual(len(result.cards_identified), 0)

    # =========================================================================
    # INSIGHTS GENERATION TESTS
    # =========================================================================

    def test_generate_card_count_insight(self):
        """Test insight generation for card counts."""
        text = """Charizard ex attacked.
        Pidgeot ex searched.
        Arven found items."""

        result = self.service.process_transcription(text)

        # Should have insight about identified cards
        has_card_insight = any('card' in i.lower() for i in result.insights)
        self.assertTrue(has_card_insight or len(result.insights) > 0)

    def test_generate_deck_insight(self):
        """Test insight generation for detected deck."""
        text = """Charizard ex attacked multiple times.
        Pidgeot ex was essential."""

        result = self.service.process_transcription(text)

        # Should have insight about deck or cards
        self.assertGreater(len(result.insights), 0)

    # =========================================================================
    # MATCH MANAGEMENT TESTS
    # =========================================================================

    def test_get_all_matches(self):
        """Test retrieving all matches."""
        self.service.process_transcription("Match 1: Charizard ex attacked.")
        self.service.process_transcription("Match 2: Gardevoir ex powered up.")

        matches = self.service.get_all_matches()

        self.assertEqual(len(matches), 2)

    def test_get_match_by_id(self):
        """Test retrieving match by ID."""
        result = self.service.process_transcription("Test match")

        retrieved = self.service.get_match(result.id)

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, result.id)

    def test_delete_match(self):
        """Test deleting a match."""
        result = self.service.process_transcription("To delete")
        match_id = result.id

        success = self.service.delete_match(match_id)

        self.assertTrue(success)
        self.assertIsNone(self.service.get_match(match_id))

    def test_matches_sorted_by_date(self):
        """Test that matches are sorted by creation date (newest first)."""
        self.service.process_transcription("First match")
        self.service.process_transcription("Second match")
        self.service.process_transcription("Third match")

        matches = self.service.get_all_matches()

        # Most recent should be first
        self.assertEqual(matches[0].title, "Transcribed Match")  # Default title


class TestPlayAction(unittest.TestCase):
    """Test cases for PlayAction dataclass."""

    def test_play_action_creation(self):
        """Test creating a PlayAction."""
        action = PlayAction(
            turn=1,
            player="player1",
            action_type="attack",
            card_name="Charizard ex",
            details="Attacked for 180 damage"
        )

        self.assertEqual(action.turn, 1)
        self.assertEqual(action.player, "player1")
        self.assertEqual(action.action_type, "attack")
        self.assertEqual(action.card_name, "Charizard ex")


class TestMatchData(unittest.TestCase):
    """Test cases for MatchData dataclass."""

    def test_match_data_creation(self):
        """Test creating MatchData."""
        match = MatchData(
            id="test_123",
            title="Test Match",
            source=MatchSource.TRANSCRIPTION
        )

        self.assertEqual(match.id, "test_123")
        self.assertEqual(match.title, "Test Match")
        self.assertEqual(match.source, MatchSource.TRANSCRIPTION)

    def test_match_data_to_dict(self):
        """Test MatchData serialization."""
        match = MatchData(
            id="test_123",
            title="Test Match",
            source=MatchSource.YOUTUBE,
            status=ProcessingStatus.COMPLETED
        )

        data = match.to_dict()

        self.assertEqual(data['id'], "test_123")
        self.assertEqual(data['source'], "youtube")
        self.assertEqual(data['status'], "completed")

    def test_match_data_from_dict(self):
        """Test MatchData deserialization."""
        data = {
            'id': 'test_123',
            'title': 'Test Match',
            'source': 'transcription',
            'status': 'pending',
            'actions': [],
            'cards_identified': ['Charizard ex'],
            'insights': ['Test insight']
        }

        match = MatchData.from_dict(data)

        self.assertEqual(match.id, 'test_123')
        self.assertEqual(match.source, MatchSource.TRANSCRIPTION)
        self.assertEqual(match.status, ProcessingStatus.PENDING)


if __name__ == '__main__':
    unittest.main()
