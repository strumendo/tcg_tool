"""
Calendar Screen - Manage competition schedule

Features:
- View upcoming tournaments
- Register/unregister for events
- Associate deck with event
- Calendar view of events
- Add to device calendar
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
from kivy.uix.spinner import Spinner
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.clock import Clock
from kivy.properties import StringProperty

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.news_service import NewsService, Tournament
from services.user_database import UserDatabase


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
}


class CalendarScreen(Screen):
    """Screen for managing competition calendar."""

    lang = StringProperty("en")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.news_service = NewsService()
        self.db = UserDatabase()
        self.filter_country = 'all'
        self._build_ui()

    def _build_ui(self):
        """Build the calendar screen UI."""
        main_layout = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(10))

        with main_layout.canvas.before:
            Color(*get_color_from_hex(COLORS['background']))
            self._bg_rect = Rectangle(pos=main_layout.pos, size=main_layout.size)
        main_layout.bind(pos=self._update_bg, size=self._update_bg)

        # Header
        header = self._create_header()
        main_layout.add_widget(header)

        # Stats bar
        self.stats_bar = self._create_stats_bar()
        main_layout.add_widget(self.stats_bar)

        # Filter row
        filter_row = self._create_filter_row()
        main_layout.add_widget(filter_row)

        # Events list (scrollable)
        self.scroll = ScrollView()
        self.events_grid = GridLayout(
            cols=1,
            spacing=dp(10),
            size_hint_y=None,
            padding=[0, dp(8)]
        )
        self.events_grid.bind(minimum_height=self.events_grid.setter('height'))
        self.scroll.add_widget(self.events_grid)
        main_layout.add_widget(self.scroll)

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
            text='Competition Calendar' if self.lang == 'en' else 'Calendário de Competições',
            font_size=sp(18),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        header.add_widget(title)

        return header

    def _create_stats_bar(self):
        """Create stats bar showing registered events count."""
        container = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))

        with container.canvas.before:
            Color(*get_color_from_hex(COLORS['primary']))
            self._stats_bg = RoundedRectangle(
                pos=container.pos,
                size=container.size,
                radius=[dp(8)]
            )
        container.bind(
            pos=lambda *a: setattr(self._stats_bg, 'pos', container.pos),
            size=lambda *a: setattr(self._stats_bg, 'size', container.size)
        )

        self.registered_label = Label(
            text='Registered: 0',
            font_size=sp(14),
            bold=True,
            color=(1, 1, 1, 1)
        )
        container.add_widget(self.registered_label)

        self.next_event_label = Label(
            text='Next: --',
            font_size=sp(12),
            color=(1, 1, 1, 0.9)
        )
        container.add_widget(self.next_event_label)

        return container

    def _create_filter_row(self):
        """Create filter row for country selection."""
        filter_row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))

        label = Label(
            text='Filter:' if self.lang == 'en' else 'Filtrar:',
            font_size=sp(13),
            color=get_color_from_hex(COLORS['text']),
            size_hint_x=None,
            width=dp(50)
        )
        filter_row.add_widget(label)

        # Country filter
        self.country_spinner = Spinner(
            text='All Countries' if self.lang == 'en' else 'Todos os Países',
            values=[
                'All Countries' if self.lang == 'en' else 'Todos os Países',
                'Brazil',
                'USA',
                'UK',
                'Japan',
                'Germany'
            ],
            background_color=get_color_from_hex(COLORS['surface']),
            font_size=sp(13)
        )
        self.country_spinner.bind(text=self._on_filter_change)
        filter_row.add_widget(self.country_spinner)

        # Show registered only
        self.registered_btn = Button(
            text='My Events' if self.lang == 'en' else 'Meus Eventos',
            background_color=get_color_from_hex(COLORS['text_muted']),
            font_size=sp(12),
            size_hint_x=None,
            width=dp(100)
        )
        self.registered_btn.bind(on_release=self._toggle_registered_filter)
        filter_row.add_widget(self.registered_btn)

        self.show_registered_only = False

        return filter_row

    # =========================================================================
    # LIFECYCLE
    # =========================================================================

    def on_enter(self):
        """Called when screen is displayed."""
        self._load_events()
        self._update_stats()

    def _on_filter_change(self, spinner, text):
        """Handle filter change."""
        if text.startswith('All'):
            self.filter_country = 'all'
        else:
            self.filter_country = text
        self._load_events()

    def _toggle_registered_filter(self, *args):
        """Toggle showing only registered events."""
        self.show_registered_only = not self.show_registered_only

        if self.show_registered_only:
            self.registered_btn.background_color = get_color_from_hex(COLORS['primary'])
        else:
            self.registered_btn.background_color = get_color_from_hex(COLORS['text_muted'])

        self._load_events()

    # =========================================================================
    # EVENTS
    # =========================================================================

    def _load_events(self):
        """Load and display events."""
        self.events_grid.clear_widgets()

        events = self.news_service.get_events(limit=20)

        # Apply filters
        if self.filter_country != 'all':
            events = [e for e in events if e.country == self.filter_country]

        if self.show_registered_only:
            events = [e for e in events if e.is_registered]

        if not events:
            self._show_empty_state()
            return

        # Group by month (simple grouping)
        for event in events:
            card = self._create_event_card(event)
            self.events_grid.add_widget(card)

    def _update_stats(self):
        """Update stats bar."""
        events = self.news_service.get_events()
        registered = [e for e in events if e.is_registered]

        self.registered_label.text = f'Registered: {len(registered)}' if self.lang == 'en' else f'Inscritos: {len(registered)}'

        if registered:
            # Sort by date and get nearest
            sorted_events = sorted(registered, key=lambda e: e.date)
            next_event = sorted_events[0]
            self.next_event_label.text = f'Next: {next_event.name[:20]}...' if len(next_event.name) > 20 else f'Next: {next_event.name}'
        else:
            self.next_event_label.text = 'Next: --' if self.lang == 'en' else 'Próximo: --'

    def _create_event_card(self, event: Tournament):
        """Create an event card with registration controls."""
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(140),
            padding=dp(12),
            spacing=dp(6)
        )

        with card.canvas.before:
            Color(*get_color_from_hex(COLORS['surface']))
            card._bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(8)])
        card.bind(
            pos=lambda *a, c=card: setattr(c._bg, 'pos', c.pos),
            size=lambda *a, c=card: setattr(c._bg, 'size', c.size)
        )

        # Header row with type and date
        header = BoxLayout(size_hint_y=None, height=dp(25), spacing=dp(8))

        # Event type badge
        type_colors = {
            'Worlds': COLORS['accent'],
            'International': COLORS['secondary'],
            'Regional': COLORS['primary'],
            'League Cup': COLORS['success'],
        }
        bg_color = type_colors.get(event.event_type, COLORS['text_muted'])

        type_badge = BoxLayout(size_hint_x=None, width=dp(90), padding=dp(2))
        with type_badge.canvas.before:
            Color(*get_color_from_hex(bg_color))
            type_badge._bg = RoundedRectangle(
                pos=type_badge.pos,
                size=type_badge.size,
                radius=[dp(4)]
            )
        type_badge.bind(
            pos=lambda *a, t=type_badge: setattr(t._bg, 'pos', t.pos),
            size=lambda *a, t=type_badge: setattr(t._bg, 'size', t.size)
        )

        type_label = Label(
            text=event.event_type,
            font_size=sp(10),
            bold=True,
            color=(1, 1, 1, 1)
        )
        type_badge.add_widget(type_label)
        header.add_widget(type_badge)

        # Date
        date_label = Label(
            text=f'📅 {event.date}',
            font_size=sp(12),
            color=get_color_from_hex(COLORS['text_secondary']),
            halign='right'
        )
        date_label.bind(size=date_label.setter('text_size'))
        header.add_widget(date_label)

        card.add_widget(header)

        # Event name
        name = Label(
            text=event.name,
            font_size=sp(14),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            valign='middle',
            size_hint_y=None,
            height=dp(22)
        )
        name.bind(size=name.setter('text_size'))
        card.add_widget(name)

        # Location
        location = Label(
            text=f'📍 {event.location}',
            font_size=sp(12),
            color=get_color_from_hex(COLORS['text_secondary']),
            halign='left',
            valign='middle',
            size_hint_y=None,
            height=dp(20)
        )
        location.bind(size=location.setter('text_size'))
        card.add_widget(location)

        # Associated deck (if registered)
        if event.is_registered and event.deck_id:
            deck = self.db.get_deck(event.deck_id)
            if deck:
                deck_label = Label(
                    text=f'🃏 Deck: {deck.name}',
                    font_size=sp(11),
                    color=get_color_from_hex(COLORS['primary']),
                    halign='left',
                    valign='middle',
                    size_hint_y=None,
                    height=dp(18)
                )
                deck_label.bind(size=deck_label.setter('text_size'))
                card.add_widget(deck_label)

        # Action buttons
        buttons = BoxLayout(size_hint_y=None, height=dp(35), spacing=dp(8))

        if event.is_registered:
            # Unregister button
            unreg_btn = Button(
                text='Unregister' if self.lang == 'en' else 'Cancelar',
                background_color=get_color_from_hex(COLORS['danger']),
                font_size=sp(12)
            )
            unreg_btn.bind(on_release=lambda x, e=event: self._unregister(e))
            buttons.add_widget(unreg_btn)

            # Change deck button
            deck_btn = Button(
                text='Set Deck' if self.lang == 'en' else 'Definir Deck',
                background_color=get_color_from_hex(COLORS['secondary']),
                font_size=sp(12)
            )
            deck_btn.bind(on_release=lambda x, e=event: self._show_deck_picker(e))
            buttons.add_widget(deck_btn)
        else:
            # Register button
            reg_btn = Button(
                text='Register' if self.lang == 'en' else 'Inscrever',
                background_color=get_color_from_hex(COLORS['success']),
                font_size=sp(12)
            )
            reg_btn.bind(on_release=lambda x, e=event: self._register(e))
            buttons.add_widget(reg_btn)

        # Add to calendar button
        cal_btn = Button(
            text='📆',
            size_hint_x=None,
            width=dp(45),
            background_color=get_color_from_hex(COLORS['accent']),
            font_size=sp(16)
        )
        cal_btn.bind(on_release=lambda x, e=event: self._add_to_calendar(e))
        buttons.add_widget(cal_btn)

        card.add_widget(buttons)

        return card

    # =========================================================================
    # ACTIONS
    # =========================================================================

    def _register(self, event: Tournament):
        """Register for an event."""
        self.news_service.register_for_event(event.id)
        self._load_events()
        self._update_stats()
        self._show_message(
            'Registered!' if self.lang == 'en' else 'Inscrito!',
            f'You registered for {event.name}' if self.lang == 'en' else f'Você se inscreveu em {event.name}'
        )

    def _unregister(self, event: Tournament):
        """Unregister from an event."""
        self.news_service.unregister_from_event(event.id)
        self._load_events()
        self._update_stats()

    def _show_deck_picker(self, event: Tournament):
        """Show deck picker popup."""
        content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))

        decks = self.db.get_all_decks()

        if not decks:
            content.add_widget(Label(
                text='No decks available' if self.lang == 'en' else 'Nenhum deck disponível',
                font_size=sp(14)
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

        scroll = ScrollView(size_hint_y=0.8)
        grid = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        popup = Popup(
            title='Select Deck' if self.lang == 'en' else 'Selecionar Deck',
            content=content,
            size_hint=(0.9, 0.6)
        )

        for deck in decks:
            btn = Button(
                text=f'{deck.name} ({deck.total_cards}/60)',
                size_hint_y=None,
                height=dp(45),
                background_color=get_color_from_hex(COLORS['secondary'])
            )
            btn.bind(on_release=lambda x, d=deck, e=event: (
                self._set_event_deck(e, d.id),
                popup.dismiss()
            ))
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

    def _set_event_deck(self, event: Tournament, deck_id: int):
        """Set deck for an event."""
        for e in self.news_service._events_cache:
            if e.id == event.id:
                e.deck_id = deck_id
                break
        self.news_service._save_cache()
        self._load_events()

    def _add_to_calendar(self, event: Tournament):
        """Add event to device calendar."""
        # On Android, this would use the calendar intent
        # For now, just show a message
        self._show_message(
            'Calendar' if self.lang == 'en' else 'Calendário',
            f'Event "{event.name}" would be added to your calendar.\n\n'
            f'Date: {event.date}\nLocation: {event.location}'
            if self.lang == 'en' else
            f'O evento "{event.name}" seria adicionado ao seu calendário.\n\n'
            f'Data: {event.date}\nLocal: {event.location}'
        )

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _show_empty_state(self):
        """Show empty state message."""
        container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(150),
            padding=dp(30)
        )

        title_label = Label(
            text='No events found' if self.lang == 'en' else 'Nenhum evento encontrado',
            font_size=sp(16),
            bold=True,
            color=get_color_from_hex(COLORS['text_secondary']),
            halign='center'
        )
        container.add_widget(title_label)

        subtitle_label = Label(
            text='Try adjusting your filters' if self.lang == 'en' else 'Tente ajustar os filtros',
            font_size=sp(13),
            color=get_color_from_hex(COLORS['text_muted']),
            halign='center'
        )
        container.add_widget(subtitle_label)

        self.events_grid.add_widget(container)

    def _show_message(self, title, message):
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
            size_hint=(0.85, 0.4)
        )
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()

    def _go_back(self, *args):
        """Navigate back."""
        if self.manager:
            self.manager.transition.direction = 'right'
            self.manager.current = 'home'
