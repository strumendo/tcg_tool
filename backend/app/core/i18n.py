"""
Bilingual (English / Portuguese) internationalisation support.

Provides a ``Language`` enum, a translation dictionary with common UI strings,
and helper functions to retrieve localised text.

No framework dependencies -- pure Python only.
"""
from enum import Enum


class Language(str, Enum):
    """Supported UI languages."""
    EN = "en"
    PT = "pt"


# ---------------------------------------------------------------------------
# Translation keys
# ---------------------------------------------------------------------------
TRANSLATIONS: dict[str, dict[str, str]] = {
    # General UI
    "tier":              {"en": "Tier",              "pt": "Tier"},
    "meta_share":        {"en": "Meta Share",        "pt": "Participacao no Meta"},
    "difficulty":        {"en": "Difficulty",        "pt": "Dificuldade"},
    "strategy":          {"en": "Strategy",          "pt": "Estrategia"},
    "strengths":         {"en": "Strengths",         "pt": "Pontos Fortes"},
    "weaknesses":        {"en": "Weaknesses",        "pt": "Pontos Fracos"},
    "key_pokemon":       {"en": "Key Pokemon",       "pt": "Pokemon Chave"},
    "matchups":          {"en": "Matchups",          "pt": "Confrontos"},
    "win_rate":          {"en": "Win Rate",          "pt": "Taxa de Vitoria"},
    "favored":           {"en": "Favored",           "pt": "Favorecido"},
    "unfavored":         {"en": "Unfavored",         "pt": "Desfavorecido"},
    "even":              {"en": "Even",              "pt": "Equilibrado"},
    "deck_list":         {"en": "Deck List",         "pt": "Lista do Deck"},

    # Card types
    "pokemon":           {"en": "Pokemon",           "pt": "Pokemon"},
    "trainer":           {"en": "Trainer",           "pt": "Treinador"},
    "energy":            {"en": "Energy",            "pt": "Energia"},
    "total":             {"en": "Total",             "pt": "Total"},

    # Difficulty levels
    "beginner":          {"en": "Beginner",          "pt": "Iniciante"},
    "intermediate":      {"en": "Intermediate",      "pt": "Intermediario"},
    "advanced":          {"en": "Advanced",          "pt": "Avancado"},

    # Rotation
    "rotating":          {"en": "Rotating",          "pt": "Rotacionando"},
    "safe":              {"en": "Safe",              "pt": "Seguro"},
    "illegal":           {"en": "Illegal",           "pt": "Ilegal"},
    "rotation_impact":   {"en": "Rotation Impact",   "pt": "Impacto da Rotacao"},
    "severity":          {"en": "Severity",          "pt": "Severidade"},
    "none":              {"en": "None",              "pt": "Nenhum"},
    "low":               {"en": "Low",               "pt": "Baixo"},
    "moderate":          {"en": "Moderate",          "pt": "Moderado"},
    "high":              {"en": "High",              "pt": "Alto"},
    "critical":          {"en": "Critical",          "pt": "Critico"},

    # Deck analysis
    "deck_analysis":     {"en": "Deck Analysis",     "pt": "Analise do Deck"},
    "comparison":        {"en": "Comparison",        "pt": "Comparacao"},
    "substitution":      {"en": "Substitution",      "pt": "Substituicao"},
    "validation":        {"en": "Validation",        "pt": "Validacao"},

    # Misc
    "vs":                {"en": "vs",                "pt": "vs"},
    "notes":             {"en": "Notes",             "pt": "Observacoes"},
    "your_deck":         {"en": "Your Deck",         "pt": "Seu Deck"},
    "opponent_deck":     {"en": "Opponent Deck",     "pt": "Deck Oponente"},
}


def get_translation(key: str, lang: Language = Language.EN) -> str:
    """Return the translated string for *key* in the given language.

    Falls back to the English value, then to the raw key if not found.
    """
    lang_value = lang.value if isinstance(lang, Language) else str(lang)
    entry = TRANSLATIONS.get(key)
    if entry is None:
        return key
    return entry.get(lang_value, entry.get("en", key))


def get_localized(en: str, pt: str, lang: Language = Language.EN) -> str:
    """Return *en* or *pt* depending on the requested language."""
    if lang == Language.PT:
        return pt
    return en
