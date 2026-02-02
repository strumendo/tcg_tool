"""
News Screen - Display Pokemon TCG news and events

Features:
- News feed from PokeBeach
- Upcoming tournaments
- Pull to refresh
- Open articles in browser
"""

import os
import sys
import webbrowser

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.uix.screenmanager import Screen
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.news_service import NewsService, NewsArticle, Tournament


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


class NewsScreen(Screen):
    """Screen for displaying news and events."""

    lang = StringProperty("en")
    is_loading = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.news_service = NewsService()
        self._build_ui()

    def _build_ui(self):
        """Build the news screen UI."""
        main_layout = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(10))

        with main_layout.canvas.before:
            Color(*get_color_from_hex(COLORS['background']))
            self._bg_rect = Rectangle(pos=main_layout.pos, size=main_layout.size)
        main_layout.bind(pos=self._update_bg, size=self._update_bg)

        # Header
        header = self._create_header()
        main_layout.add_widget(header)

        # Tab buttons
        tabs = self._create_tabs()
        main_layout.add_widget(tabs)

        # Content area (scrollable)
        self.scroll = ScrollView()
        self.content_grid = GridLayout(
            cols=1,
            spacing=dp(10),
            size_hint_y=None,
            padding=[0, dp(8)]
        )
        self.content_grid.bind(minimum_height=self.content_grid.setter('height'))
        self.scroll.add_widget(self.content_grid)
        main_layout.add_widget(self.scroll)

        # Refresh button
        refresh_btn = Button(
            text='Refresh' if self.lang == 'en' else 'Atualizar',
            background_color=get_color_from_hex(COLORS['primary']),
            font_size=sp(14),
            size_hint_y=None,
            height=dp(45)
        )
        refresh_btn.bind(on_release=self._on_refresh)
        main_layout.add_widget(refresh_btn)

        self.add_widget(main_layout)
        self.current_tab = 'news'

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
            text='News & Events' if self.lang == 'en' else 'Notícias & Eventos',
            font_size=sp(18),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        header.add_widget(title)

        return header

    def _create_tabs(self):
        """Create tab buttons for News/Events."""
        tabs = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))

        self.news_tab = Button(
            text='News' if self.lang == 'en' else 'Notícias',
            background_color=get_color_from_hex(COLORS['primary']),
            font_size=sp(14)
        )
        self.news_tab.bind(on_release=lambda x: self._switch_tab('news'))
        tabs.add_widget(self.news_tab)

        self.events_tab = Button(
            text='Events' if self.lang == 'en' else 'Eventos',
            background_color=get_color_from_hex(COLORS['text_muted']),
            font_size=sp(14)
        )
        self.events_tab.bind(on_release=lambda x: self._switch_tab('events'))
        tabs.add_widget(self.events_tab)

        return tabs

    # =========================================================================
    # LIFECYCLE
    # =========================================================================

    def on_enter(self):
        """Called when screen is displayed."""
        self._load_content()

    def _switch_tab(self, tab):
        """Switch between news and events tabs."""
        self.current_tab = tab

        if tab == 'news':
            self.news_tab.background_color = get_color_from_hex(COLORS['primary'])
            self.events_tab.background_color = get_color_from_hex(COLORS['text_muted'])
        else:
            self.news_tab.background_color = get_color_from_hex(COLORS['text_muted'])
            self.events_tab.background_color = get_color_from_hex(COLORS['primary'])

        self._load_content()

    def _load_content(self):
        """Load content based on current tab."""
        self.content_grid.clear_widgets()

        if self.current_tab == 'news':
            self._load_news()
        else:
            self._load_events()

    def _on_refresh(self, *args):
        """Handle refresh button click."""
        self.is_loading = True
        Clock.schedule_once(lambda dt: self._do_refresh(), 0.1)

    def _do_refresh(self):
        """Perform refresh."""
        if self.current_tab == 'news':
            self.news_service.get_news(force_refresh=True)
        else:
            self.news_service.get_events(force_refresh=True)
        self._load_content()
        self.is_loading = False

    # =========================================================================
    # NEWS
    # =========================================================================

    def _load_news(self):
        """Load and display news articles."""
        articles = self.news_service.get_news(limit=15)

        if not articles:
            self._show_empty_state(
                'No news available' if self.lang == 'en' else 'Nenhuma notícia disponível',
                'Pull to refresh' if self.lang == 'en' else 'Deslize para atualizar'
            )
            return

        for article in articles:
            card = self._create_news_card(article)
            self.content_grid.add_widget(card)

    def _create_news_card(self, article: NewsArticle):
        """Create a news article card."""
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(120),
            padding=dp(12),
            spacing=dp(8)
        )

        with card.canvas.before:
            Color(*get_color_from_hex(COLORS['surface']))
            card._bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(8)])
        card.bind(
            pos=lambda *a, c=card: setattr(c._bg, 'pos', c.pos),
            size=lambda *a, c=card: setattr(c._bg, 'size', c.size)
        )

        # Content row
        content = BoxLayout(spacing=dp(10))

        # Image (if available)
        if article.image_url:
            img = AsyncImage(
                source=article.image_url,
                size_hint_x=None,
                width=dp(80),
                allow_stretch=True,
                keep_ratio=True
            )
            content.add_widget(img)

        # Text content
        text_box = BoxLayout(orientation='vertical', spacing=dp(4))

        # Title
        title = Label(
            text=article.title[:80] + ('...' if len(article.title) > 80 else ''),
            font_size=sp(14),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            valign='top',
            text_size=(dp(200), None)
        )
        text_box.add_widget(title)

        # Summary
        if article.summary:
            summary = Label(
                text=article.summary[:100] + ('...' if len(article.summary) > 100 else ''),
                font_size=sp(11),
                color=get_color_from_hex(COLORS['text_secondary']),
                halign='left',
                valign='top',
                text_size=(dp(200), None)
            )
            text_box.add_widget(summary)

        # Source and date
        meta = Label(
            text=f'{article.source} • {self._format_date(article.published_date)}',
            font_size=sp(10),
            color=get_color_from_hex(COLORS['text_muted']),
            halign='left',
            valign='bottom'
        )
        meta.bind(size=meta.setter('text_size'))
        text_box.add_widget(meta)

        content.add_widget(text_box)
        card.add_widget(content)

        # Make card clickable
        btn = Button(
            text='Read More' if self.lang == 'en' else 'Ler Mais',
            size_hint_y=None,
            height=dp(30),
            background_color=get_color_from_hex(COLORS['secondary']),
            font_size=sp(12)
        )
        btn.bind(on_release=lambda x, url=article.url: self._open_url(url))
        card.add_widget(btn)

        return card

    # =========================================================================
    # EVENTS
    # =========================================================================

    def _load_events(self):
        """Load and display upcoming events."""
        events = self.news_service.get_events(limit=10)

        if not events:
            self._show_empty_state(
                'No events available' if self.lang == 'en' else 'Nenhum evento disponível',
                'Check back later' if self.lang == 'en' else 'Volte mais tarde'
            )
            return

        # Section: Registered events
        registered = [e for e in events if e.is_registered]
        if registered:
            header = self._create_section_header(
                'My Events' if self.lang == 'en' else 'Meus Eventos'
            )
            self.content_grid.add_widget(header)

            for event in registered:
                card = self._create_event_card(event)
                self.content_grid.add_widget(card)

        # Section: Upcoming events
        header = self._create_section_header(
            'Upcoming Events' if self.lang == 'en' else 'Próximos Eventos'
        )
        self.content_grid.add_widget(header)

        for event in events:
            card = self._create_event_card(event)
            self.content_grid.add_widget(card)

    def _create_event_card(self, event: Tournament):
        """Create an event card."""
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(110),
            padding=dp(12),
            spacing=dp(6)
        )

        # Card background color based on event type
        type_colors = {
            'Worlds': COLORS['accent'],
            'International': COLORS['secondary'],
            'Regional': COLORS['primary'],
        }
        bg_color = type_colors.get(event.event_type, COLORS['surface'])

        with card.canvas.before:
            Color(*get_color_from_hex(COLORS['surface']))
            card._bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(8)])
        card.bind(
            pos=lambda *a, c=card: setattr(c._bg, 'pos', c.pos),
            size=lambda *a, c=card: setattr(c._bg, 'size', c.size)
        )

        # Header row
        header = BoxLayout(size_hint_y=None, height=dp(25))

        # Event type badge
        type_badge = BoxLayout(size_hint_x=None, width=dp(80), padding=dp(2))
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

        # Registered indicator
        if event.is_registered:
            reg_label = Label(
                text='✓ Registered' if self.lang == 'en' else '✓ Inscrito',
                font_size=sp(10),
                color=get_color_from_hex(COLORS['success']),
                halign='right'
            )
            reg_label.bind(size=reg_label.setter('text_size'))
            header.add_widget(reg_label)
        else:
            header.add_widget(Label())  # Spacer

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
            height=dp(20)
        )
        name.bind(size=name.setter('text_size'))
        card.add_widget(name)

        # Date and location
        info = Label(
            text=f'📅 {event.date}  📍 {event.location}',
            font_size=sp(12),
            color=get_color_from_hex(COLORS['text_secondary']),
            halign='left',
            valign='middle',
            size_hint_y=None,
            height=dp(20)
        )
        info.bind(size=info.setter('text_size'))
        card.add_widget(info)

        # Action button
        btn_text = 'View Details' if self.lang == 'en' else 'Ver Detalhes'
        btn = Button(
            text=btn_text,
            size_hint_y=None,
            height=dp(30),
            background_color=get_color_from_hex(COLORS['secondary']),
            font_size=sp(12)
        )
        btn.bind(on_release=lambda x, url=event.url: self._open_url(url))
        card.add_widget(btn)

        return card

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _create_section_header(self, text):
        """Create a section header."""
        header = Label(
            text=text,
            font_size=sp(14),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            size_hint_y=None,
            height=dp(30),
            halign='left',
            valign='bottom'
        )
        header.bind(size=header.setter('text_size'))
        return header

    def _show_empty_state(self, title, subtitle):
        """Show empty state message."""
        container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(150),
            padding=dp(30)
        )

        title_label = Label(
            text=title,
            font_size=sp(16),
            bold=True,
            color=get_color_from_hex(COLORS['text_secondary']),
            halign='center'
        )
        container.add_widget(title_label)

        subtitle_label = Label(
            text=subtitle,
            font_size=sp(13),
            color=get_color_from_hex(COLORS['text_muted']),
            halign='center'
        )
        container.add_widget(subtitle_label)

        self.content_grid.add_widget(container)

    def _format_date(self, date_str):
        """Format date string for display."""
        if not date_str:
            return ""
        # Simple formatting - just return first part
        return date_str.split(',')[0] if ',' in date_str else date_str[:20]

    def _open_url(self, url):
        """Open URL in browser."""
        if url:
            try:
                webbrowser.open(url)
            except Exception:
                pass

    def _go_back(self, *args):
        """Navigate back."""
        if self.manager:
            self.manager.transition.direction = 'right'
            self.manager.current = 'home'
