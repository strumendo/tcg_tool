"""
Deck Editor Screen - Create and edit decks

Features:
- Create new deck from scratch
- Edit existing decks
- Search cards by name
- Add/remove cards with quantity control
- Real-time deck validation
- Card preview with images
"""

import os
import sys

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.image import AsyncImage
from kivy.uix.screenmanager import Screen
from kivy.uix.spinner import Spinner
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty, NumericProperty

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.user_database import UserDatabase, UserDeck, UserCard


# Color scheme
COLORS = {
    'background': '#f5f5f5',
    'surface': '#ffffff',
    'card': '#ffffff',
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
    'info': '#2196f3',
}

# Common cards for quick add (frequently used)
COMMON_CARDS = [
    # Supporters
    {"name": "Professor's Research", "set_code": "SVI", "set_number": "189", "type": "trainer", "subtype": "supporter"},
    {"name": "Iono", "set_code": "PAL", "set_number": "185", "type": "trainer", "subtype": "supporter"},
    {"name": "Boss's Orders", "set_code": "PAL", "set_number": "172", "type": "trainer", "subtype": "supporter"},
    {"name": "Arven", "set_code": "SVI", "set_number": "166", "type": "trainer", "subtype": "supporter"},
    {"name": "Penny", "set_code": "SVI", "set_number": "183", "type": "trainer", "subtype": "supporter"},
    # Items
    {"name": "Nest Ball", "set_code": "SVI", "set_number": "181", "type": "trainer", "subtype": "item"},
    {"name": "Ultra Ball", "set_code": "SVI", "set_number": "196", "type": "trainer", "subtype": "item"},
    {"name": "Rare Candy", "set_code": "SVI", "set_number": "191", "type": "trainer", "subtype": "item"},
    {"name": "Switch", "set_code": "SVI", "set_number": "194", "type": "trainer", "subtype": "item"},
    {"name": "Super Rod", "set_code": "PAL", "set_number": "188", "type": "trainer", "subtype": "item"},
    {"name": "Night Stretcher", "set_code": "SFA", "set_number": "61", "type": "trainer", "subtype": "item"},
    {"name": "Counter Catcher", "set_code": "PAR", "set_number": "160", "type": "trainer", "subtype": "item"},
    # Energy
    {"name": "Basic Fire Energy", "set_code": "SVE", "set_number": "2", "type": "energy", "subtype": "basic"},
    {"name": "Basic Water Energy", "set_code": "SVE", "set_number": "3", "type": "energy", "subtype": "basic"},
    {"name": "Basic Grass Energy", "set_code": "SVE", "set_number": "1", "type": "energy", "subtype": "basic"},
    {"name": "Basic Lightning Energy", "set_code": "SVE", "set_number": "4", "type": "energy", "subtype": "basic"},
    {"name": "Basic Psychic Energy", "set_code": "SVE", "set_number": "5", "type": "energy", "subtype": "basic"},
    {"name": "Basic Fighting Energy", "set_code": "SVE", "set_number": "6", "type": "energy", "subtype": "basic"},
    {"name": "Basic Darkness Energy", "set_code": "SVE", "set_number": "7", "type": "energy", "subtype": "basic"},
    {"name": "Basic Metal Energy", "set_code": "SVE", "set_number": "8", "type": "energy", "subtype": "basic"},
]


class DeckEditorScreen(Screen):
    """Screen for creating and editing decks."""

    deck_id = NumericProperty(0)
    lang = StringProperty("en")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = UserDatabase()
        self.current_deck = None
        self.deck_cards = []  # Working copy of cards
        self.search_results = []
        self._search_scheduled = None
        self._build_ui()

    def _build_ui(self):
        """Build the editor screen UI."""
        main_layout = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(10))

        with main_layout.canvas.before:
            Color(*get_color_from_hex(COLORS['background']))
            self._bg_rect = Rectangle(pos=main_layout.pos, size=main_layout.size)
        main_layout.bind(pos=self._update_bg, size=self._update_bg)

        # Header
        header = self._create_header()
        main_layout.add_widget(header)

        # Deck name input
        name_area = self._create_name_area()
        main_layout.add_widget(name_area)

        # Deck stats bar
        self.stats_bar = self._create_stats_bar()
        main_layout.add_widget(self.stats_bar)

        # Main content area (split view)
        content = BoxLayout(orientation='horizontal', spacing=dp(10))

        # Left side: Deck cards
        deck_area = self._create_deck_area()
        content.add_widget(deck_area)

        # Right side: Search and add cards
        search_area = self._create_search_area()
        content.add_widget(search_area)

        main_layout.add_widget(content)

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

        self.header_title = Label(
            text='New Deck' if self.lang == 'en' else 'Novo Deck',
            font_size=sp(18),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            valign='middle'
        )
        self.header_title.bind(size=self.header_title.setter('text_size'))
        header.add_widget(self.header_title)

        return header

    def _create_name_area(self):
        """Create deck name input area."""
        container = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))

        label = Label(
            text='Name:' if self.lang == 'en' else 'Nome:',
            font_size=sp(14),
            color=get_color_from_hex(COLORS['text']),
            size_hint_x=None,
            width=dp(50)
        )
        container.add_widget(label)

        # Input with card styling
        input_box = BoxLayout(padding=dp(2))
        with input_box.canvas.before:
            Color(*get_color_from_hex(COLORS['surface']))
            self._name_bg = RoundedRectangle(
                pos=input_box.pos,
                size=input_box.size,
                radius=[dp(6)]
            )
        input_box.bind(
            pos=lambda *a: setattr(self._name_bg, 'pos', input_box.pos),
            size=lambda *a: setattr(self._name_bg, 'size', input_box.size)
        )

        self.name_input = TextInput(
            text='My Deck',
            multiline=False,
            font_size=sp(14),
            background_color=(0, 0, 0, 0),
            foreground_color=get_color_from_hex(COLORS['text']),
            padding=[dp(10), dp(8)]
        )
        input_box.add_widget(self.name_input)
        container.add_widget(input_box)

        return container

    def _create_stats_bar(self):
        """Create deck statistics bar."""
        container = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))

        with container.canvas.before:
            Color(*get_color_from_hex(COLORS['primary']))
            self._stats_bg = RoundedRectangle(
                pos=container.pos,
                size=container.size,
                radius=[dp(6)]
            )
        container.bind(
            pos=lambda *a: setattr(self._stats_bg, 'pos', container.pos),
            size=lambda *a: setattr(self._stats_bg, 'size', container.size)
        )

        self.total_label = Label(
            text='Total: 0/60',
            font_size=sp(13),
            bold=True,
            color=(1, 1, 1, 1)
        )
        container.add_widget(self.total_label)

        self.pokemon_label = Label(
            text='Pokemon: 0',
            font_size=sp(12),
            color=(1, 1, 1, 0.9)
        )
        container.add_widget(self.pokemon_label)

        self.trainer_label = Label(
            text='Trainers: 0',
            font_size=sp(12),
            color=(1, 1, 1, 0.9)
        )
        container.add_widget(self.trainer_label)

        self.energy_label = Label(
            text='Energy: 0',
            font_size=sp(12),
            color=(1, 1, 1, 0.9)
        )
        container.add_widget(self.energy_label)

        return container

    def _create_deck_area(self):
        """Create the deck cards area (left side)."""
        container = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_x=0.55)

        # Section header
        header = Label(
            text='Deck Cards' if self.lang == 'en' else 'Cartas do Deck',
            font_size=sp(14),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            size_hint_y=None,
            height=dp(25),
            halign='left',
            valign='middle'
        )
        header.bind(size=header.setter('text_size'))
        container.add_widget(header)

        # Scrollable card list
        scroll = ScrollView()
        self.deck_grid = GridLayout(
            cols=1,
            spacing=dp(6),
            size_hint_y=None,
            padding=[0, dp(4)]
        )
        self.deck_grid.bind(minimum_height=self.deck_grid.setter('height'))
        scroll.add_widget(self.deck_grid)
        container.add_widget(scroll)

        return container

    def _create_search_area(self):
        """Create the search and add cards area (right side)."""
        container = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_x=0.45)

        # Search header
        header = Label(
            text='Add Cards' if self.lang == 'en' else 'Adicionar Cartas',
            font_size=sp(14),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            size_hint_y=None,
            height=dp(25),
            halign='left',
            valign='middle'
        )
        header.bind(size=header.setter('text_size'))
        container.add_widget(header)

        # Search input
        search_box = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(6))

        input_container = BoxLayout(padding=dp(2))
        with input_container.canvas.before:
            Color(*get_color_from_hex(COLORS['surface']))
            self._search_bg = RoundedRectangle(
                pos=input_container.pos,
                size=input_container.size,
                radius=[dp(6)]
            )
        input_container.bind(
            pos=lambda *a: setattr(self._search_bg, 'pos', input_container.pos),
            size=lambda *a: setattr(self._search_bg, 'size', input_container.size)
        )

        self.search_input = TextInput(
            hint_text='Search card...' if self.lang == 'en' else 'Buscar carta...',
            multiline=False,
            font_size=sp(13),
            background_color=(0, 0, 0, 0),
            foreground_color=get_color_from_hex(COLORS['text']),
            padding=[dp(10), dp(8)]
        )
        self.search_input.bind(text=self._on_search_text)
        input_container.add_widget(self.search_input)
        search_box.add_widget(input_container)

        container.add_widget(search_box)

        # Filter by type
        filter_box = BoxLayout(size_hint_y=None, height=dp(35), spacing=dp(4))

        self.filter_all = Button(
            text='All',
            background_color=get_color_from_hex(COLORS['primary']),
            font_size=sp(11)
        )
        self.filter_all.bind(on_release=lambda x: self._set_filter('all'))

        self.filter_pokemon = Button(
            text='Pokemon',
            background_color=get_color_from_hex(COLORS['text_muted']),
            font_size=sp(11)
        )
        self.filter_pokemon.bind(on_release=lambda x: self._set_filter('pokemon'))

        self.filter_trainer = Button(
            text='Trainer',
            background_color=get_color_from_hex(COLORS['text_muted']),
            font_size=sp(11)
        )
        self.filter_trainer.bind(on_release=lambda x: self._set_filter('trainer'))

        self.filter_energy = Button(
            text='Energy',
            background_color=get_color_from_hex(COLORS['text_muted']),
            font_size=sp(11)
        )
        self.filter_energy.bind(on_release=lambda x: self._set_filter('energy'))

        filter_box.add_widget(self.filter_all)
        filter_box.add_widget(self.filter_pokemon)
        filter_box.add_widget(self.filter_trainer)
        filter_box.add_widget(self.filter_energy)

        container.add_widget(filter_box)
        self.current_filter = 'all'

        # Search results / common cards
        scroll = ScrollView()
        self.search_grid = GridLayout(
            cols=1,
            spacing=dp(6),
            size_hint_y=None,
            padding=[0, dp(4)]
        )
        self.search_grid.bind(minimum_height=self.search_grid.setter('height'))
        scroll.add_widget(self.search_grid)
        container.add_widget(scroll)

        return container

    def _create_bottom_buttons(self):
        """Create save/cancel buttons."""
        buttons = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))

        save_btn = Button(
            text='Save Deck' if self.lang == 'en' else 'Salvar Deck',
            background_color=get_color_from_hex(COLORS['success']),
            font_size=sp(14),
            bold=True
        )
        save_btn.bind(on_release=self._on_save)
        buttons.add_widget(save_btn)

        cancel_btn = Button(
            text='Cancel' if self.lang == 'en' else 'Cancelar',
            background_color=get_color_from_hex(COLORS['text_muted']),
            font_size=sp(14)
        )
        cancel_btn.bind(on_release=self._go_back)
        buttons.add_widget(cancel_btn)

        return buttons

    # =========================================================================
    # SCREEN LIFECYCLE
    # =========================================================================

    def on_enter(self):
        """Called when screen is displayed."""
        self._load_deck()
        self._show_common_cards()
        self._update_stats()

    def on_leave(self):
        """Called when leaving screen."""
        if self._search_scheduled:
            self._search_scheduled.cancel()

    def _load_deck(self):
        """Load deck if editing, or create new."""
        if self.deck_id > 0:
            self.current_deck = self.db.get_deck(self.deck_id)
            if self.current_deck:
                self.name_input.text = self.current_deck.name
                self.deck_cards = list(self.current_deck.cards)
                self.header_title.text = 'Edit Deck' if self.lang == 'en' else 'Editar Deck'
            else:
                self._init_new_deck()
        else:
            self._init_new_deck()

        self._refresh_deck_list()

    def _init_new_deck(self):
        """Initialize a new empty deck."""
        self.current_deck = UserDeck(name='My Deck')
        self.deck_cards = []
        self.name_input.text = 'My Deck'
        self.header_title.text = 'New Deck' if self.lang == 'en' else 'Novo Deck'

    # =========================================================================
    # CARD SEARCH
    # =========================================================================

    def _on_search_text(self, instance, value):
        """Handle search text changes with debounce."""
        if self._search_scheduled:
            self._search_scheduled.cancel()

        if len(value.strip()) >= 2:
            self._search_scheduled = Clock.schedule_once(
                lambda dt: self._do_search(value.strip()), 0.3
            )
        elif len(value.strip()) == 0:
            self._show_common_cards()

    def _do_search(self, query):
        """Perform card search."""
        query_lower = query.lower()
        results = []

        # Search in common cards first
        for card in COMMON_CARDS:
            if query_lower in card['name'].lower():
                if self.current_filter == 'all' or card['type'] == self.current_filter:
                    results.append(card)

        # TODO: Add API search for Pokemon cards
        # For now, just search common cards

        self.search_results = results[:20]  # Limit results
        self._show_search_results()

    def _show_common_cards(self):
        """Show common cards for quick adding."""
        self.search_grid.clear_widgets()

        # Filter by current filter
        filtered = [c for c in COMMON_CARDS
                    if self.current_filter == 'all' or c['type'] == self.current_filter]

        for card_data in filtered:
            row = self._create_search_card_row(card_data)
            self.search_grid.add_widget(row)

    def _show_search_results(self):
        """Show search results."""
        self.search_grid.clear_widgets()

        if not self.search_results:
            empty_label = Label(
                text='No cards found' if self.lang == 'en' else 'Nenhuma carta encontrada',
                font_size=sp(13),
                color=get_color_from_hex(COLORS['text_secondary']),
                size_hint_y=None,
                height=dp(40)
            )
            self.search_grid.add_widget(empty_label)
            return

        for card_data in self.search_results:
            row = self._create_search_card_row(card_data)
            self.search_grid.add_widget(row)

    def _set_filter(self, filter_type):
        """Set the card type filter."""
        self.current_filter = filter_type

        # Update button colors
        all_btns = [self.filter_all, self.filter_pokemon, self.filter_trainer, self.filter_energy]
        for btn in all_btns:
            btn.background_color = get_color_from_hex(COLORS['text_muted'])

        if filter_type == 'all':
            self.filter_all.background_color = get_color_from_hex(COLORS['primary'])
        elif filter_type == 'pokemon':
            self.filter_pokemon.background_color = get_color_from_hex(COLORS['primary'])
        elif filter_type == 'trainer':
            self.filter_trainer.background_color = get_color_from_hex(COLORS['primary'])
        elif filter_type == 'energy':
            self.filter_energy.background_color = get_color_from_hex(COLORS['primary'])

        # Refresh search results or common cards
        if self.search_input.text.strip():
            self._do_search(self.search_input.text.strip())
        else:
            self._show_common_cards()

    # =========================================================================
    # DECK MANAGEMENT
    # =========================================================================

    def _add_card(self, card_data, quantity=1):
        """Add a card to the deck."""
        # Check if card already exists
        existing = None
        for card in self.deck_cards:
            if card.name.lower() == card_data['name'].lower():
                existing = card
                break

        if existing:
            # Check 4-copy rule (except basic energy)
            is_basic_energy = 'basic' in card_data['name'].lower() and card_data['type'] == 'energy'
            if not is_basic_energy and existing.quantity >= 4:
                self._show_message(
                    'Limit Reached' if self.lang == 'en' else 'Limite Atingido',
                    'Maximum 4 copies per card' if self.lang == 'en' else 'Máximo 4 cópias por carta'
                )
                return
            existing.quantity += quantity
        else:
            # Add new card
            new_card = UserCard(
                name=card_data['name'],
                set_code=card_data['set_code'],
                set_number=card_data['set_number'],
                quantity=quantity,
                card_type=card_data['type'],
                subtype=card_data.get('subtype', ''),
                regulation_mark=self._get_regulation_mark(card_data['set_code'])
            )
            self.deck_cards.append(new_card)

        self._refresh_deck_list()
        self._update_stats()

    def _remove_card(self, card):
        """Remove a card from deck or decrease quantity."""
        if card.quantity > 1:
            card.quantity -= 1
        else:
            self.deck_cards.remove(card)

        self._refresh_deck_list()
        self._update_stats()

    def _delete_card(self, card):
        """Completely remove a card from deck."""
        self.deck_cards.remove(card)
        self._refresh_deck_list()
        self._update_stats()

    def _get_regulation_mark(self, set_code):
        """Get regulation mark for a set code."""
        marks = {
            'SVI': 'G', 'PAL': 'G', 'OBF': 'G', 'MEW': 'G', 'PAR': 'G', 'PAF': 'G',
            'TEF': 'H', 'TWM': 'H', 'SFA': 'H', 'SCR': 'H', 'SSP': 'H',
            'PRE': 'I', 'JTG': 'I', 'ASC': 'I', 'DRI': 'I',
            'SVE': 'H',
        }
        return marks.get(set_code.upper(), '?')

    # =========================================================================
    # UI REFRESH
    # =========================================================================

    def _refresh_deck_list(self):
        """Refresh the deck cards display."""
        self.deck_grid.clear_widgets()

        if not self.deck_cards:
            empty_label = Label(
                text='No cards yet\nAdd cards from the right panel' if self.lang == 'en' else
                     'Nenhuma carta ainda\nAdicione cartas pelo painel direito',
                font_size=sp(13),
                color=get_color_from_hex(COLORS['text_secondary']),
                size_hint_y=None,
                height=dp(60),
                halign='center'
            )
            self.deck_grid.add_widget(empty_label)
            return

        # Sort cards: Pokemon, Trainers, Energy
        sorted_cards = sorted(self.deck_cards, key=lambda c: (
            0 if c.card_type == 'pokemon' else 1 if c.card_type == 'trainer' else 2,
            c.name
        ))

        current_type = None
        for card in sorted_cards:
            # Add type header if changed
            if card.card_type != current_type:
                current_type = card.card_type
                header = self._create_type_header(current_type)
                self.deck_grid.add_widget(header)

            row = self._create_deck_card_row(card)
            self.deck_grid.add_widget(row)

    def _update_stats(self):
        """Update deck statistics display."""
        total = sum(c.quantity for c in self.deck_cards)
        pokemon = sum(c.quantity for c in self.deck_cards if c.card_type == 'pokemon')
        trainers = sum(c.quantity for c in self.deck_cards if c.card_type == 'trainer')
        energy = sum(c.quantity for c in self.deck_cards if c.card_type == 'energy')

        self.total_label.text = f'Total: {total}/60'
        self.pokemon_label.text = f'Pokemon: {pokemon}'
        self.trainer_label.text = f'Trainers: {trainers}'
        self.energy_label.text = f'Energy: {energy}'

        # Update color based on total
        if total == 60:
            self._stats_bg.radius = [dp(6)]
            # Green - valid
            with self.stats_bar.canvas.before:
                Color(*get_color_from_hex(COLORS['success']))
                self._stats_bg = RoundedRectangle(
                    pos=self.stats_bar.pos,
                    size=self.stats_bar.size,
                    radius=[dp(6)]
                )
        elif total > 60:
            # Red - too many
            with self.stats_bar.canvas.before:
                Color(*get_color_from_hex(COLORS['danger']))
                self._stats_bg = RoundedRectangle(
                    pos=self.stats_bar.pos,
                    size=self.stats_bar.size,
                    radius=[dp(6)]
                )

    def _create_type_header(self, card_type):
        """Create a section header for card type."""
        type_names = {
            'pokemon': 'Pokemon',
            'trainer': 'Trainers',
            'energy': 'Energy'
        }

        header = Label(
            text=type_names.get(card_type, card_type.title()),
            font_size=sp(12),
            bold=True,
            color=get_color_from_hex(COLORS['text_secondary']),
            size_hint_y=None,
            height=dp(25),
            halign='left',
            valign='bottom'
        )
        header.bind(size=header.setter('text_size'))
        return header

    def _create_deck_card_row(self, card):
        """Create a row for a deck card with quantity controls."""
        row = BoxLayout(
            size_hint_y=None,
            height=dp(40),
            spacing=dp(6),
            padding=[dp(8), dp(4)]
        )

        with row.canvas.before:
            Color(*get_color_from_hex(COLORS['surface']))
            row._bg = RoundedRectangle(pos=row.pos, size=row.size, radius=[dp(4)])
        row.bind(
            pos=lambda *a, r=row: setattr(r._bg, 'pos', r.pos),
            size=lambda *a, r=row: setattr(r._bg, 'size', r.size)
        )

        # Quantity
        qty_label = Label(
            text=str(card.quantity),
            font_size=sp(14),
            bold=True,
            color=get_color_from_hex(COLORS['primary']),
            size_hint_x=None,
            width=dp(25)
        )
        row.add_widget(qty_label)

        # Name
        name_label = Label(
            text=card.name,
            font_size=sp(12),
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            valign='middle',
            text_size=(dp(120), None)
        )
        row.add_widget(name_label)

        # Set code
        set_label = Label(
            text=f'{card.set_code}',
            font_size=sp(10),
            color=get_color_from_hex(COLORS['text_muted']),
            size_hint_x=None,
            width=dp(35)
        )
        row.add_widget(set_label)

        # Regulation mark (if rotating)
        if card.regulation_mark == 'G':
            reg_label = Label(
                text='G',
                font_size=sp(10),
                bold=True,
                color=get_color_from_hex(COLORS['warning']),
                size_hint_x=None,
                width=dp(15)
            )
            row.add_widget(reg_label)

        # Control buttons
        minus_btn = Button(
            text='-',
            size_hint_x=None,
            width=dp(30),
            background_color=get_color_from_hex(COLORS['warning']),
            font_size=sp(16)
        )
        minus_btn.bind(on_release=lambda x, c=card: self._remove_card(c))
        row.add_widget(minus_btn)

        plus_btn = Button(
            text='+',
            size_hint_x=None,
            width=dp(30),
            background_color=get_color_from_hex(COLORS['success']),
            font_size=sp(16)
        )
        plus_btn.bind(on_release=lambda x, c=card: self._add_card({
            'name': c.name,
            'set_code': c.set_code,
            'set_number': c.set_number,
            'type': c.card_type,
            'subtype': c.subtype
        }, 1))
        row.add_widget(plus_btn)

        delete_btn = Button(
            text='×',
            size_hint_x=None,
            width=dp(30),
            background_color=get_color_from_hex(COLORS['danger']),
            font_size=sp(16)
        )
        delete_btn.bind(on_release=lambda x, c=card: self._delete_card(c))
        row.add_widget(delete_btn)

        return row

    def _create_search_card_row(self, card_data):
        """Create a row for a search result card."""
        row = BoxLayout(
            size_hint_y=None,
            height=dp(40),
            spacing=dp(6),
            padding=[dp(8), dp(4)]
        )

        with row.canvas.before:
            Color(*get_color_from_hex(COLORS['surface']))
            row._bg = RoundedRectangle(pos=row.pos, size=row.size, radius=[dp(4)])
        row.bind(
            pos=lambda *a, r=row: setattr(r._bg, 'pos', r.pos),
            size=lambda *a, r=row: setattr(r._bg, 'size', r.size)
        )

        # Type indicator
        type_colors = {
            'pokemon': COLORS['secondary'],
            'trainer': COLORS['accent'],
            'energy': COLORS['success']
        }
        type_label = Label(
            text=card_data['type'][0].upper(),
            font_size=sp(11),
            bold=True,
            color=get_color_from_hex(type_colors.get(card_data['type'], COLORS['text'])),
            size_hint_x=None,
            width=dp(20)
        )
        row.add_widget(type_label)

        # Name
        name_label = Label(
            text=card_data['name'],
            font_size=sp(12),
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            valign='middle'
        )
        name_label.bind(size=name_label.setter('text_size'))
        row.add_widget(name_label)

        # Add button
        add_btn = Button(
            text='+',
            size_hint_x=None,
            width=dp(35),
            background_color=get_color_from_hex(COLORS['primary']),
            font_size=sp(16)
        )
        add_btn.bind(on_release=lambda x: self._add_card(card_data))
        row.add_widget(add_btn)

        return row

    # =========================================================================
    # ACTIONS
    # =========================================================================

    def _go_back(self, *args):
        """Navigate back, with confirmation if unsaved changes."""
        # Check for unsaved changes
        if self.deck_cards:
            self._confirm_discard()
        else:
            self._do_go_back()

    def _do_go_back(self):
        """Actually navigate back."""
        if self.manager:
            self.manager.transition.direction = 'right'
            self.manager.current = 'my_decks'

    def _confirm_discard(self):
        """Confirm discarding unsaved changes."""
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

        content.add_widget(Label(
            text='Discard unsaved changes?' if self.lang == 'en' else
                 'Descartar alterações não salvas?',
            font_size=sp(14),
            halign='center'
        ))

        buttons = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))

        discard_btn = Button(
            text='Discard' if self.lang == 'en' else 'Descartar',
            background_color=get_color_from_hex(COLORS['danger'])
        )
        keep_btn = Button(
            text='Keep Editing' if self.lang == 'en' else 'Continuar Editando',
            background_color=get_color_from_hex(COLORS['primary'])
        )

        buttons.add_widget(discard_btn)
        buttons.add_widget(keep_btn)
        content.add_widget(buttons)

        popup = Popup(
            title='Unsaved Changes' if self.lang == 'en' else 'Alterações Não Salvas',
            content=content,
            size_hint=(0.8, 0.35),
            auto_dismiss=True
        )

        discard_btn.bind(on_release=lambda x: (popup.dismiss(), self._do_go_back()))
        keep_btn.bind(on_release=popup.dismiss)
        popup.open()

    def _on_save(self, *args):
        """Save the deck."""
        total = sum(c.quantity for c in self.deck_cards)

        if total == 0:
            self._show_message(
                'Empty Deck' if self.lang == 'en' else 'Deck Vazio',
                'Add at least one card' if self.lang == 'en' else 'Adicione pelo menos uma carta'
            )
            return

        # Create or update deck
        if self.current_deck and self.current_deck.id > 0:
            deck = self.current_deck
        else:
            deck = UserDeck()

        deck.name = self.name_input.text.strip() or 'My Deck'
        deck.cards = self.deck_cards
        deck.is_complete = total == 60

        deck_id = self.db.save_deck(deck)

        # Show success and go back
        self._show_message(
            'Saved!' if self.lang == 'en' else 'Salvo!',
            f'Deck "{deck.name}" saved successfully' if self.lang == 'en' else
            f'Deck "{deck.name}" salvo com sucesso',
            on_dismiss=self._do_go_back
        )

    def _show_message(self, title, message, on_dismiss=None):
        """Show a message popup."""
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

        content.add_widget(Label(
            text=message,
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
            title=title,
            content=content,
            size_hint=(0.8, 0.35),
            auto_dismiss=True
        )

        def do_dismiss(*a):
            popup.dismiss()
            if on_dismiss:
                on_dismiss()

        close_btn.bind(on_release=do_dismiss)
        content.add_widget(close_btn)
        popup.open()

    def set_deck_id(self, deck_id):
        """Set deck ID for editing."""
        self.deck_id = deck_id
