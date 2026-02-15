"""
Meta Decks screen - Browse competitive meta decks.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.metrics import dp
from kivy.clock import Clock

from app.components import (
    ColoredBox, CardBox, LoadingSpinner, ErrorMessage,
    COLORS, get_color_from_hex
)
from app.utils.responsive import scaled_font, get_padding, get_spacing
from app.services.api_client import APIClient
import threading


class DeckCard(CardBox):
    """Meta deck card widget."""

    def __init__(self, deck_data, on_click=None, **kwargs):
        super().__init__(**kwargs)
        self.deck_data = deck_data
        self.orientation = 'horizontal'
        self.spacing = dp(10)
        self.size_hint_y = None
        self.height = dp(100)

        # Deck icon/image
        icon_container = BoxLayout(
            size_hint_x=None,
            width=dp(80)
        )

        # Use pokemon sprite as icon if available
        icon_url = deck_data.get('icon_url', '')
        if icon_url:
            icon = AsyncImage(
                source=icon_url,
                size_hint=(None, None),
                size=(dp(60), dp(60)),
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )
            icon_container.add_widget(icon)
        else:
            # Fallback emoji
            icon_label = Label(
                text='🎴',
                font_size=scaled_font(48),
                size_hint=(None, None),
                size=(dp(60), dp(60)),
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )
            icon_container.add_widget(icon_label)

        self.add_widget(icon_container)

        # Deck info
        info_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(5)
        )

        # Deck name
        name_label = Label(
            text=deck_data.get('name', 'Deck'),
            font_size=scaled_font(16),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            size_hint_y=None,
            height=dp(25),
            halign='left',
            valign='middle'
        )
        name_label.bind(size=lambda *x: setattr(name_label, 'text_size', (name_label.width, None)))
        info_layout.add_widget(name_label)

        # Tier and meta share
        tier = deck_data.get('tier', 'N/A')
        meta_share = deck_data.get('meta_share', 0)

        tier_color = COLORS['success'] if tier == 'Tier 1' else COLORS['secondary'] if tier == 'Tier 2' else COLORS['text_muted']

        stats_label = Label(
            text=f'{tier} • {meta_share}% do meta',
            font_size=scaled_font(12),
            color=get_color_from_hex(tier_color),
            size_hint_y=None,
            height=dp(20),
            halign='left',
            valign='middle'
        )
        stats_label.bind(size=lambda *x: setattr(stats_label, 'text_size', (stats_label.width, None)))
        info_layout.add_widget(stats_label)

        # Energy types
        types = deck_data.get('types', [])
        if types:
            types_text = ' '.join([self._get_type_emoji(t) for t in types])
            types_label = Label(
                text=types_text,
                font_size=scaled_font(20),
                size_hint_y=None,
                height=dp(25),
                halign='left',
                valign='middle'
            )
            types_label.bind(size=lambda *x: setattr(types_label, 'text_size', (types_label.width, None)))
            info_layout.add_widget(types_label)

        self.add_widget(info_layout)

        # Make card clickable
        if on_click:
            self.bind(on_touch_down=lambda instance, touch: on_click(deck_data) if self.collide_point(*touch.pos) else None)

    def _get_type_emoji(self, type_name):
        """Get emoji for energy type."""
        type_map = {
            'Fire': '🔥',
            'Water': '💧',
            'Lightning': '⚡',
            'Psychic': '🔮',
            'Fighting': '👊',
            'Darkness': '🌙',
            'Metal': '⚙️',
            'Grass': '🍃',
            'Colorless': '⭐',
        }
        return type_map.get(type_name, '⭐')


class MetaDecksScreen(Screen):
    """Screen for browsing meta decks."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'meta'
        self.api_client = APIClient()
        self.decks_data = []

        # Main container
        main_layout = ColoredBox(
            orientation='vertical',
            bg_color=COLORS['background']
        )

        # Content container
        self.content_container = BoxLayout(
            orientation='vertical'
        )

        # Loading state
        self.content_container.add_widget(LoadingSpinner())

        main_layout.add_widget(self.content_container)
        self.add_widget(main_layout)

        # Load data on screen creation
        Clock.schedule_once(lambda dt: self._load_meta_decks(), 0.1)

    def _load_meta_decks(self):
        """Load meta decks from API."""
        def fetch():
            try:
                result = self.api_client.get_meta_decks()
                Clock.schedule_once(lambda dt: self._display_decks(result), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: self._show_error(str(e)), 0)

        threading.Thread(target=fetch, daemon=True).start()

    def _display_decks(self, decks):
        """Display meta decks grouped by tier."""
        self.content_container.clear_widgets()
        self.decks_data = decks

        # Scroll view
        scroll = ScrollView()
        content = BoxLayout(
            orientation='vertical',
            spacing=get_spacing(),
            padding=get_padding(),
            size_hint_y=None
        )
        content.bind(minimum_height=content.setter('height'))

        # Group decks by tier
        tiers = {}
        for deck in decks:
            tier = deck.get('tier', 'Tier 3')
            if tier not in tiers:
                tiers[tier] = []
            tiers[tier].append(deck)

        # Display by tier
        for tier in ['Tier 1', 'Tier 2', 'Tier 3']:
            if tier in tiers:
                # Tier header
                tier_label = Label(
                    text=tier,
                    font_size=scaled_font(20),
                    bold=True,
                    color=get_color_from_hex(COLORS['primary']),
                    size_hint_y=None,
                    height=dp(40),
                    halign='left',
                    valign='middle'
                )
                tier_label.bind(size=lambda *x: setattr(tier_label, 'text_size', (tier_label.width, None)))
                content.add_widget(tier_label)

                # Deck cards
                for deck in tiers[tier]:
                    deck_card = DeckCard(
                        deck_data=deck,
                        on_click=self._on_deck_click
                    )
                    content.add_widget(deck_card)

        scroll.add_widget(content)
        self.content_container.add_widget(scroll)

    def _show_error(self, error_msg):
        """Show error message."""
        self.content_container.clear_widgets()
        error = ErrorMessage(
            message=f'Erro ao carregar meta decks: {error_msg}',
            on_retry=self._load_meta_decks
        )
        self.content_container.add_widget(error)

    def _on_deck_click(self, deck_data):
        """Handle deck card click."""
        # Navigate to deck detail screen
        if self.manager:
            deck_detail = self.manager.get_screen('deck_detail')
            deck_detail.load_deck(deck_data)
            self.manager.current = 'deck_detail'

    def on_enter(self):
        """Called when screen is displayed."""
        # Reload if data is stale (optional)
        pass
