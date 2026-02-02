"""Screens module for TCG App."""
from .import_screen import ImportScreen
from .my_decks_screen import MyDecksScreen
from .deck_editor_screen import DeckEditorScreen
from .comparison_screen import ComparisonScreen
from .news_screen import NewsScreen
from .calendar_screen import CalendarScreen

__all__ = [
    'ImportScreen',
    'MyDecksScreen',
    'DeckEditorScreen',
    'ComparisonScreen',
    'NewsScreen',
    'CalendarScreen'
]
