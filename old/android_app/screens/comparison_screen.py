"""
Deck Comparison Screen - Compare user deck against META

Features:
- Compare your deck against META archetypes
- Show matchup win rates
- Highlight card differences
- Rotation impact comparison
- Suggestions for improvements
"""

import os
import sys

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.properties import ObjectProperty, StringProperty, NumericProperty

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.user_database import UserDatabase, UserDeck
from meta_data import META_DECKS, get_matchup, get_deck_matchups, Language


# Color scheme
COLORS = {
    'background': '#f5f5f5',
    'surface': '#ffffff',
    'primary': '#4caf50',
    'primary_dark': '#388e3c',
    'secondary': '#2196f3',
    'accent': '#ff9800',
    'warning': '#ff9800',
    'danger': '#f44336',
    'success': '#4caf50',
    'text': '#212121',
    'text_secondary': '#757575',
    'text_muted': '#9e9e9e',
    'border': '#e0e0e0',
    'favorable': '#4caf50',
    'neutral': '#ff9800',
    'unfavorable': '#f44336',
}

# Archetype detection keywords
ARCHETYPE_KEYWORDS = {
    'charizard': ['charizard', 'pidgeot'],
    'dragapult': ['dragapult', 'giratina'],
    'regidrago': ['regidrago', 'ogerpon'],
    'gardevoir': ['gardevoir', 'kirlia', 'scream tail'],
    'gholdengo': ['gholdengo', 'gimmighoul'],
    'lugia': ['lugia', 'archeops'],
    'roaring_moon': ['roaring moon', 'flutter mane'],
    'terapagos': ['terapagos', 'dusknoir'],
}


class ComparisonScreen(Screen):
    """Screen for comparing user deck against META."""

    deck_id = NumericProperty(0)
    lang = StringProperty("en")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = UserDatabase()
        self.current_deck = None
        self.detected_archetype = None
        self._build_ui()

    def _build_ui(self):
        """Build the comparison screen UI."""
        main_layout = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(10))

        with main_layout.canvas.before:
            Color(*get_color_from_hex(COLORS['background']))
            self._bg_rect = Rectangle(pos=main_layout.pos, size=main_layout.size)
        main_layout.bind(pos=self._update_bg, size=self._update_bg)

        # Header
        header = self._create_header()
        main_layout.add_widget(header)

        # Deck info card
        self.deck_info = self._create_deck_info()
        main_layout.add_widget(self.deck_info)

        # Archetype detection
        self.archetype_section = self._create_archetype_section()
        main_layout.add_widget(self.archetype_section)

        # Matchups section
        matchup_label = Label(
            text='META Matchups' if self.lang == 'en' else 'Matchups META',
            font_size=sp(16),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            size_hint_y=None,
            height=dp(30),
            halign='left',
            valign='middle'
        )
        matchup_label.bind(size=matchup_label.setter('text_size'))
        main_layout.add_widget(matchup_label)

        # Matchups scroll
        scroll = ScrollView()
        self.matchups_grid = GridLayout(
            cols=1,
            spacing=dp(8),
            size_hint_y=None,
            padding=[0, dp(4)]
        )
        self.matchups_grid.bind(minimum_height=self.matchups_grid.setter('height'))
        scroll.add_widget(self.matchups_grid)
        main_layout.add_widget(scroll)

        # Bottom buttons
        bottom_buttons = self._create_bottom_buttons()
        main_layout.add_widget(bottom_buttons)

        self.add_widget(main_layout)

    def _update_bg(self, *args):
        self._bg_rect.pos = args[0].pos
        self._bg_rect.size = args[0].size

    def _create_header(self):
        """Create header with title and back button."""
        header = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))

        back_btn = Button(
            text='<',
            size_hint_x=None,
            width=dp(40),
            background_color=get_color_from_hex(COLORS['text_muted']),
            font_size=sp(20)
        )
        back_btn.bind(on_release=self._go_back)
        header.add_widget(back_btn)

        title = Label(
            text='Deck Comparison' if self.lang == 'en' else 'Comparar Deck',
            font_size=sp(18),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        header.add_widget(title)

        return header

    def _create_deck_info(self):
        """Create deck info card."""
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(80),
            padding=dp(12),
            spacing=dp(8)
        )

        with card.canvas.before:
            Color(*get_color_from_hex(COLORS['surface']))
            self._deck_bg = RoundedRectangle(
                pos=card.pos,
                size=card.size,
                radius=[dp(8)]
            )
        card.bind(
            pos=lambda *a: setattr(self._deck_bg, 'pos', card.pos),
            size=lambda *a: setattr(self._deck_bg, 'size', card.size)
        )

        self.deck_name_label = Label(
            text='Select a deck',
            font_size=sp(16),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            valign='middle'
        )
        self.deck_name_label.bind(size=self.deck_name_label.setter('text_size'))
        card.add_widget(self.deck_name_label)

        self.deck_stats_label = Label(
            text='',
            font_size=sp(12),
            color=get_color_from_hex(COLORS['text_secondary']),
            halign='left',
            valign='middle'
        )
        self.deck_stats_label.bind(size=self.deck_stats_label.setter('text_size'))
        card.add_widget(self.deck_stats_label)

        return card

    def _create_archetype_section(self):
        """Create archetype detection section."""
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(60),
            padding=dp(12),
            spacing=dp(6)
        )

        with card.canvas.before:
            Color(*get_color_from_hex(COLORS['primary']))
            self._arch_bg = RoundedRectangle(
                pos=card.pos,
                size=card.size,
                radius=[dp(8)]
            )
        card.bind(
            pos=lambda *a: setattr(self._arch_bg, 'pos', card.pos),
            size=lambda *a: setattr(self._arch_bg, 'size', card.size)
        )

        self.archetype_label = Label(
            text='Detected Archetype: Unknown' if self.lang == 'en' else 'Arquétipo Detectado: Desconhecido',
            font_size=sp(14),
            bold=True,
            color=(1, 1, 1, 1)
        )
        card.add_widget(self.archetype_label)

        self.archetype_detail = Label(
            text='Import a deck to detect archetype',
            font_size=sp(11),
            color=(1, 1, 1, 0.8)
        )
        card.add_widget(self.archetype_detail)

        return card

    def _create_bottom_buttons(self):
        """Create bottom action buttons."""
        buttons = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))

        select_btn = Button(
            text='Select Deck' if self.lang == 'en' else 'Selecionar Deck',
            background_color=get_color_from_hex(COLORS['secondary']),
            font_size=sp(14)
        )
        select_btn.bind(on_release=self._show_deck_selector)
        buttons.add_widget(select_btn)

        back_btn = Button(
            text='Back' if self.lang == 'en' else 'Voltar',
            background_color=get_color_from_hex(COLORS['text_muted']),
            font_size=sp(14)
        )
        back_btn.bind(on_release=self._go_back)
        buttons.add_widget(back_btn)

        return buttons

    # =========================================================================
    # LIFECYCLE
    # =========================================================================

    def on_enter(self):
        """Called when screen is displayed."""
        if self.deck_id > 0:
            self._load_deck(self.deck_id)
        else:
            # Check for active deck
            active = self.db.get_active_deck()
            if active:
                self._load_deck(active.id)
            else:
                self._show_no_deck()

    def _load_deck(self, deck_id):
        """Load a deck for comparison."""
        deck = self.db.get_deck(deck_id)
        if deck:
            self.current_deck = deck
            self.deck_id = deck_id
            self._update_deck_display()
            self._detect_archetype()
            self._show_matchups()

    def _show_no_deck(self):
        """Show state when no deck is selected."""
        self.deck_name_label.text = 'No deck selected' if self.lang == 'en' else 'Nenhum deck selecionado'
        self.deck_stats_label.text = 'Select a deck to compare against META' if self.lang == 'en' else 'Selecione um deck para comparar com META'
        self.archetype_label.text = 'Detected Archetype: None' if self.lang == 'en' else 'Arquétipo Detectado: Nenhum'
        self.archetype_detail.text = ''
        self.matchups_grid.clear_widgets()

    def _update_deck_display(self):
        """Update the deck info display."""
        if not self.current_deck:
            return

        self.deck_name_label.text = self.current_deck.name

        total = self.current_deck.total_cards
        pokemon = self.current_deck.pokemon_count
        trainers = self.current_deck.trainer_count
        energy = self.current_deck.energy_count

        self.deck_stats_label.text = f'{total}/60 cards • {pokemon} Pokemon • {trainers} Trainers • {energy} Energy'

    # =========================================================================
    # ARCHETYPE DETECTION
    # =========================================================================

    def _detect_archetype(self):
        """Detect deck archetype based on cards."""
        if not self.current_deck:
            return

        card_names = [c.name.lower() for c in self.current_deck.cards]
        all_text = ' '.join(card_names)

        detected = None
        best_score = 0

        for archetype, keywords in ARCHETYPE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in all_text)
            if score > best_score:
                best_score = score
                detected = archetype

        self.detected_archetype = detected

        if detected:
            # Get archetype display name from META_DECKS
            if detected in META_DECKS:
                meta_deck = META_DECKS[detected]
                archetype_name = meta_deck.get('name', detected.title())
            else:
                archetype_name = detected.replace('_', ' ').title()

            self.archetype_label.text = f'Detected: {archetype_name}' if self.lang == 'en' else f'Detectado: {archetype_name}'
            self.archetype_detail.text = f'Matched {best_score} key cards' if self.lang == 'en' else f'{best_score} cartas-chave identificadas'
        else:
            self.archetype_label.text = 'Archetype: Custom/Unknown' if self.lang == 'en' else 'Arquétipo: Personalizado/Desconhecido'
            self.archetype_detail.text = 'No known archetype detected' if self.lang == 'en' else 'Nenhum arquétipo conhecido detectado'

    # =========================================================================
    # MATCHUPS
    # =========================================================================

    def _show_matchups(self):
        """Show matchups against all META decks."""
        self.matchups_grid.clear_widgets()

        if not self.detected_archetype:
            # Show general info
            info_label = Label(
                text='Archetype not detected. Showing all META decks.' if self.lang == 'en' else
                     'Arquétipo não detectado. Mostrando todos os decks META.',
                font_size=sp(12),
                color=get_color_from_hex(COLORS['text_secondary']),
                size_hint_y=None,
                height=dp(30)
            )
            self.matchups_grid.add_widget(info_label)

            # Show all META decks without matchup data
            for deck_key, deck_data in META_DECKS.items():
                row = self._create_meta_deck_row(deck_key, deck_data, None)
                self.matchups_grid.add_widget(row)
            return

        # Get matchups for detected archetype
        matchups = get_deck_matchups(self.detected_archetype)

        if matchups:
            # Sort by win rate
            sorted_matchups = sorted(matchups.items(), key=lambda x: x[1], reverse=True)

            for opponent, win_rate in sorted_matchups:
                if opponent in META_DECKS:
                    row = self._create_matchup_row(opponent, META_DECKS[opponent], win_rate)
                    self.matchups_grid.add_widget(row)
        else:
            # No matchup data, show all decks
            for deck_key, deck_data in META_DECKS.items():
                row = self._create_meta_deck_row(deck_key, deck_data, None)
                self.matchups_grid.add_widget(row)

    def _create_matchup_row(self, deck_key, deck_data, win_rate):
        """Create a matchup row with win rate."""
        row = BoxLayout(
            size_hint_y=None,
            height=dp(55),
            padding=dp(10),
            spacing=dp(8)
        )

        with row.canvas.before:
            Color(*get_color_from_hex(COLORS['surface']))
            row._bg = RoundedRectangle(pos=row.pos, size=row.size, radius=[dp(6)])
        row.bind(
            pos=lambda *a, r=row: setattr(r._bg, 'pos', r.pos),
            size=lambda *a, r=row: setattr(r._bg, 'size', r.size)
        )

        # Info section
        info = BoxLayout(orientation='vertical', spacing=dp(2))

        name = Label(
            text=deck_data.get('name', deck_key.title()),
            font_size=sp(14),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            valign='middle'
        )
        name.bind(size=name.setter('text_size'))
        info.add_widget(name)

        # Matchup indicator text
        if win_rate >= 55:
            indicator = 'Favorable' if self.lang == 'en' else 'Favorável'
            ind_color = COLORS['favorable']
        elif win_rate <= 45:
            indicator = 'Unfavorable' if self.lang == 'en' else 'Desfavorável'
            ind_color = COLORS['unfavorable']
        else:
            indicator = 'Even' if self.lang == 'en' else 'Equilibrado'
            ind_color = COLORS['neutral']

        matchup_text = Label(
            text=indicator,
            font_size=sp(11),
            color=get_color_from_hex(ind_color),
            halign='left',
            valign='middle'
        )
        matchup_text.bind(size=matchup_text.setter('text_size'))
        info.add_widget(matchup_text)

        row.add_widget(info)

        # Win rate badge
        rate_color = ind_color
        rate_box = BoxLayout(
            size_hint_x=None,
            width=dp(60),
            padding=dp(4)
        )

        with rate_box.canvas.before:
            Color(*get_color_from_hex(rate_color))
            rate_box._bg = RoundedRectangle(
                pos=rate_box.pos,
                size=rate_box.size,
                radius=[dp(4)]
            )
        rate_box.bind(
            pos=lambda *a, r=rate_box: setattr(r._bg, 'pos', r.pos),
            size=lambda *a, r=rate_box: setattr(r._bg, 'size', r.size)
        )

        rate_label = Label(
            text=f'{win_rate}%',
            font_size=sp(14),
            bold=True,
            color=(1, 1, 1, 1)
        )
        rate_box.add_widget(rate_label)
        row.add_widget(rate_box)

        return row

    def _create_meta_deck_row(self, deck_key, deck_data, win_rate):
        """Create a META deck row without specific matchup."""
        row = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            padding=dp(10),
            spacing=dp(8)
        )

        with row.canvas.before:
            Color(*get_color_from_hex(COLORS['surface']))
            row._bg = RoundedRectangle(pos=row.pos, size=row.size, radius=[dp(6)])
        row.bind(
            pos=lambda *a, r=row: setattr(r._bg, 'pos', r.pos),
            size=lambda *a, r=row: setattr(r._bg, 'size', r.size)
        )

        name = Label(
            text=deck_data.get('name', deck_key.title()),
            font_size=sp(14),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            valign='middle'
        )
        name.bind(size=name.setter('text_size'))
        row.add_widget(name)

        # Difficulty badge
        difficulty = deck_data.get('difficulty', 'medium')
        diff_colors = {
            'easy': COLORS['success'],
            'medium': COLORS['warning'],
            'hard': COLORS['danger']
        }

        diff_label = Label(
            text=difficulty.upper(),
            font_size=sp(10),
            color=get_color_from_hex(diff_colors.get(difficulty, COLORS['text_muted'])),
            size_hint_x=None,
            width=dp(60)
        )
        row.add_widget(diff_label)

        return row

    # =========================================================================
    # DECK SELECTION
    # =========================================================================

    def _show_deck_selector(self, *args):
        """Show popup to select a deck."""
        content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))

        decks = self.db.get_all_decks()

        if not decks:
            content.add_widget(Label(
                text='No decks available.\nImport or create a deck first.' if self.lang == 'en' else
                     'Nenhum deck disponível.\nImporte ou crie um deck primeiro.',
                font_size=sp(14),
                halign='center'
            ))

            close_btn = Button(
                text='OK',
                size_hint_y=None,
                height=dp(40),
                background_color=get_color_from_hex(COLORS['primary'])
            )
            popup = Popup(
                title='Select Deck' if self.lang == 'en' else 'Selecionar Deck',
                content=content,
                size_hint=(0.85, 0.4)
            )
            close_btn.bind(on_release=popup.dismiss)
            content.add_widget(close_btn)
            popup.open()
            return

        # Scrollable deck list
        scroll = ScrollView(size_hint_y=0.8)
        grid = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        popup = Popup(
            title='Select Deck' if self.lang == 'en' else 'Selecionar Deck',
            content=content,
            size_hint=(0.9, 0.7)
        )

        for deck in decks:
            btn = Button(
                text=f'{deck.name} ({deck.total_cards}/60)',
                size_hint_y=None,
                height=dp(45),
                background_color=get_color_from_hex(COLORS['secondary'] if deck.is_complete else COLORS['accent'])
            )
            btn.bind(on_release=lambda x, d=deck: (popup.dismiss(), self._load_deck(d.id)))
            grid.add_widget(btn)

        scroll.add_widget(grid)
        content.add_widget(scroll)

        cancel_btn = Button(
            text='Cancel' if self.lang == 'en' else 'Cancelar',
            size_hint_y=None,
            height=dp(40),
            background_color=get_color_from_hex(COLORS['text_muted'])
        )
        cancel_btn.bind(on_release=popup.dismiss)
        content.add_widget(cancel_btn)

        popup.open()

    # =========================================================================
    # NAVIGATION
    # =========================================================================

    def _go_back(self, *args):
        """Navigate back."""
        if self.manager:
            self.manager.transition.direction = 'right'
            self.manager.current = 'my_decks'

    def set_deck_id(self, deck_id):
        """Set deck ID for comparison."""
        self.deck_id = deck_id
