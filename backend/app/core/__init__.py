"""
Core domain logic for the TCG Tool backend.

This package contains pure-Python modules with ZERO framework dependencies.
All data structures use ``dataclasses`` and ``enum`` from the standard library.
"""

# -- Set codes & regulation marks -------------------------------------------
from app.core.set_codes import (
    SET_CODE_MAP,
    REGULATION_MARKS,
    normalize_set_code,
    get_regulation_mark,
)

# -- Deck parser ------------------------------------------------------------
from app.core.deck_parser import (
    CardType,
    TrainerSubtype,
    ParsedCard,
    ParsedDeck,
    detect_card_type,
    detect_trainer_subtype,
    parse_line,
    parse_deck,
    parse_deck_file,
)

# -- Rotation analysis ------------------------------------------------------
from app.core.rotation import (
    Severity,
    RotationReport,
    analyze_rotation,
    get_rotation_summary,
)

# -- Type chart -------------------------------------------------------------
from app.core.type_chart import (
    TYPE_WEAKNESSES,
    TYPE_RESISTANCES,
    get_weakness,
    get_resistance,
)

# -- Matchup engine ---------------------------------------------------------
from app.core.matchup_engine import (
    DeckComparison,
    MatchupAnalysis,
    compare_decks,
    analyze_matchup,
    get_deck_energy_types,
    get_main_attackers,
    count_search_cards,
    count_draw_supporters,
)

# -- Substitution engine ----------------------------------------------------
from app.core.substitution_engine import (
    Substitution,
    KNOWN_SUBSTITUTIONS,
    calculate_type_match,
    calculate_function_match,
    calculate_archetype_match,
    calculate_match_score,
    find_substitutions_from_pool,
    generate_updated_deck,
)

# -- Deck validation --------------------------------------------------------
from app.core.deck_validation import (
    MAX_DECK_SIZE,
    MAX_COPIES,
    UNLIMITED_CARDS,
    ValidationResult,
    validate_deck,
)

# -- Internationalisation ---------------------------------------------------
from app.core.i18n import (
    Language,
    TRANSLATIONS,
    get_translation,
    get_localized,
)

__all__ = [
    # set_codes
    "SET_CODE_MAP",
    "REGULATION_MARKS",
    "normalize_set_code",
    "get_regulation_mark",
    # deck_parser
    "CardType",
    "TrainerSubtype",
    "ParsedCard",
    "ParsedDeck",
    "detect_card_type",
    "detect_trainer_subtype",
    "parse_line",
    "parse_deck",
    "parse_deck_file",
    # rotation
    "Severity",
    "RotationReport",
    "analyze_rotation",
    "get_rotation_summary",
    # type_chart
    "TYPE_WEAKNESSES",
    "TYPE_RESISTANCES",
    "get_weakness",
    "get_resistance",
    # matchup_engine
    "DeckComparison",
    "MatchupAnalysis",
    "compare_decks",
    "analyze_matchup",
    "get_deck_energy_types",
    "get_main_attackers",
    "count_search_cards",
    "count_draw_supporters",
    # substitution_engine
    "Substitution",
    "KNOWN_SUBSTITUTIONS",
    "calculate_type_match",
    "calculate_function_match",
    "calculate_archetype_match",
    "calculate_match_score",
    "find_substitutions_from_pool",
    "generate_updated_deck",
    # deck_validation
    "MAX_DECK_SIZE",
    "MAX_COPIES",
    "UNLIMITED_CARDS",
    "ValidationResult",
    "validate_deck",
    # i18n
    "Language",
    "TRANSLATIONS",
    "get_translation",
    "get_localized",
]
