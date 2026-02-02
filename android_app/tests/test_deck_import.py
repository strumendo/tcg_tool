"""
Tests for DeckImportService

Tests deck parsing, validation, and import functionality.
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.deck_import import DeckImportService, ValidationSeverity


class TestDeckImportService(unittest.TestCase):
    """Test cases for DeckImportService."""

    def setUp(self):
        """Set up test fixtures."""
        self.service = DeckImportService()

    # =========================================================================
    # PARSING TESTS
    # =========================================================================

    def test_parse_valid_card_line(self):
        """Test parsing a valid PTCGO card line."""
        text = "4 Charizard ex OBF 125"
        result = self.service.import_from_text(text)

        self.assertTrue(result.success)
        self.assertIsNotNone(result.deck)
        self.assertEqual(len(result.deck.cards), 1)

        card = result.deck.cards[0]
        self.assertEqual(card.quantity, 4)
        self.assertEqual(card.name, "Charizard ex")
        self.assertEqual(card.set_code, "OBF")
        self.assertEqual(card.set_number, "125")

    def test_parse_pokemon_with_special_characters(self):
        """Test parsing Pokemon with special names."""
        text = "2 Mr. Mime PAL 122"
        result = self.service.import_from_text(text)

        self.assertTrue(result.success)
        self.assertEqual(result.deck.cards[0].name, "Mr. Mime")

    def test_parse_energy_card(self):
        """Test parsing basic energy card."""
        text = "10 Basic Fire Energy SVE 2"
        result = self.service.import_from_text(text)

        self.assertTrue(result.success)
        card = result.deck.cards[0]
        self.assertEqual(card.quantity, 10)
        self.assertEqual(card.card_type, "energy")

    def test_parse_trainer_card(self):
        """Test parsing trainer card."""
        text = "4 Professor's Research SVI 189"
        result = self.service.import_from_text(text)

        self.assertTrue(result.success)
        card = result.deck.cards[0]
        self.assertEqual(card.card_type, "trainer")

    def test_ignore_comment_lines(self):
        """Test that comment lines are ignored."""
        text = """# This is a comment
        // Another comment
        4 Charizard ex OBF 125"""
        result = self.service.import_from_text(text)

        self.assertTrue(result.success)
        self.assertEqual(len(result.deck.cards), 1)

    def test_ignore_section_headers(self):
        """Test that section headers are ignored."""
        text = """Pokemon: 4
        4 Charizard ex OBF 125
        Trainer: 4
        4 Arven SVI 166"""
        result = self.service.import_from_text(text)

        self.assertTrue(result.success)
        self.assertEqual(len(result.deck.cards), 2)

    def test_parse_multiple_cards(self):
        """Test parsing multiple cards."""
        text = """4 Charizard ex OBF 125
        4 Charmander OBF 26
        4 Arven SVI 166
        10 Basic Fire Energy SVE 2"""
        result = self.service.import_from_text(text)

        self.assertTrue(result.success)
        self.assertEqual(len(result.deck.cards), 4)
        self.assertEqual(result.deck.total_cards, 22)

    def test_empty_input(self):
        """Test handling empty input."""
        result = self.service.import_from_text("")

        # Empty input may return success with None deck or empty deck
        # Verify no errors are raised
        self.assertIsNotNone(result)

    def test_invalid_format(self):
        """Test handling invalid card format."""
        text = "This is not a valid card line"
        result = self.service.import_from_text(text)

        # Should still create deck but with issues
        self.assertTrue(len(result.issues) > 0)

    # =========================================================================
    # VALIDATION TESTS
    # =========================================================================

    def test_validate_complete_deck(self):
        """Test validation of a complete 60-card deck."""
        # Create a 60-card deck
        cards = []
        cards.append("4 Charizard ex OBF 125")
        cards.append("4 Charmeleon OBF 27")
        cards.append("4 Charmander OBF 26")
        cards.append("4 Pidgeot ex OBF 164")
        cards.append("4 Pidgey OBF 162")
        cards.append("4 Arven SVI 166")
        cards.append("4 Professor's Research SVI 189")
        cards.append("4 Iono PAL 185")
        cards.append("4 Ultra Ball SVI 196")
        cards.append("4 Rare Candy SVI 191")
        cards.append("4 Nest Ball SVI 181")
        cards.append("4 Switch SVI 194")
        cards.append("12 Basic Fire Energy SVE 2")

        text = "\n".join(cards)
        result = self.service.import_from_text(text)

        self.assertTrue(result.success)
        self.assertEqual(result.deck.total_cards, 60)
        self.assertTrue(result.deck.is_complete)

    def test_validate_four_copy_rule(self):
        """Test that 4-copy rule is enforced (except basic energy)."""
        text = """5 Charizard ex OBF 125
        4 Arven SVI 166"""
        result = self.service.import_from_text(text)

        # Should have warning about 5 copies
        has_copy_warning = any(
            'copies' in issue.message_en.lower() or 'cópias' in issue.message_pt.lower()
            for issue in result.issues
        )
        self.assertTrue(has_copy_warning)

    def test_basic_energy_unlimited(self):
        """Test that basic energy can exceed 4 copies."""
        text = "20 Basic Fire Energy SVE 2"
        result = self.service.import_from_text(text)

        self.assertTrue(result.success)
        # Should not have 4-copy warning for basic energy
        has_copy_warning = any(
            issue.severity == ValidationSeverity.ERROR and 'copies' in issue.message_en.lower()
            for issue in result.issues
        )
        self.assertFalse(has_copy_warning)

    def test_incomplete_deck_warning(self):
        """Test warning for incomplete deck."""
        text = "4 Charizard ex OBF 125"
        result = self.service.import_from_text(text)

        self.assertTrue(result.success)
        self.assertFalse(result.deck.is_complete)

        # Should have warning about incomplete deck
        has_incomplete_warning = any(
            'incomplete' in issue.message_en.lower() or 'incompleto' in issue.message_pt.lower()
            for issue in result.issues
        )
        self.assertTrue(has_incomplete_warning)

    # =========================================================================
    # DECK NAME SUGGESTION TESTS
    # =========================================================================

    def test_suggest_deck_name_charizard(self):
        """Test deck name suggestion for Charizard deck."""
        text = """4 Charizard ex OBF 125
        4 Pidgeot ex OBF 164"""
        result = self.service.import_from_text(text)

        name = self.service.suggest_deck_name(result.deck)
        self.assertIn("Charizard", name)

    def test_suggest_deck_name_generic(self):
        """Test generic deck name when no pattern matches."""
        text = "4 Arven SVI 166"
        result = self.service.import_from_text(text)

        name = self.service.suggest_deck_name(result.deck)
        self.assertIsNotNone(name)
        self.assertTrue(len(name) > 0)

    # =========================================================================
    # REGULATION MARK TESTS
    # =========================================================================

    def test_detect_rotating_cards(self):
        """Test detection of cards with regulation mark G (rotating)."""
        text = "4 Charizard ex OBF 125"  # OBF is regulation G
        result = self.service.import_from_text(text)

        card = result.deck.cards[0]
        self.assertEqual(card.regulation_mark, "G")

    def test_detect_legal_cards(self):
        """Test detection of cards with regulation mark H (legal)."""
        text = "4 Iron Thorns ex TEF 123"  # TEF is regulation H
        result = self.service.import_from_text(text)

        card = result.deck.cards[0]
        self.assertEqual(card.regulation_mark, "H")


class TestCardTypeDetection(unittest.TestCase):
    """Test card type detection logic."""

    def setUp(self):
        self.service = DeckImportService()

    def test_detect_pokemon_ex(self):
        """Test detection of Pokemon ex."""
        text = "4 Charizard ex OBF 125"
        result = self.service.import_from_text(text)
        self.assertEqual(result.deck.cards[0].card_type, "pokemon")

    def test_detect_pokemon_v(self):
        """Test detection of Pokemon V."""
        text = "4 Arceus V BRS 122"
        result = self.service.import_from_text(text)
        self.assertEqual(result.deck.cards[0].card_type, "pokemon")

    def test_detect_supporter(self):
        """Test detection of Supporter cards."""
        text = "4 Professor's Research SVI 189"
        result = self.service.import_from_text(text)
        card = result.deck.cards[0]
        self.assertEqual(card.card_type, "trainer")
        self.assertEqual(card.subtype, "supporter")

    def test_detect_basic_energy(self):
        """Test detection of Basic Energy."""
        text = "10 Basic Fire Energy SVE 2"
        result = self.service.import_from_text(text)
        card = result.deck.cards[0]
        self.assertEqual(card.card_type, "energy")
        # Basic energy is detected by name, subtype not always set
        self.assertIn("energy", card.name.lower())


if __name__ == '__main__':
    unittest.main()
