"""
TCG Tool - Mobile App Entry Point
Kivy-based Pokemon TCG deck analyzer with FastAPI backend integration
"""

import os
os.environ['KIVY_METRICS_DENSITY'] = '1'

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import platform

from app.services.api_client import APIClient
from app.services.offline_cache import OfflineCache
from app.services.sync_service import SyncService
from app.utils.responsive import ScreenMode, get_screen_mode

# Color palette
COLORS = {
    'primary': '#1E3A8A',      # Dark blue
    'secondary': '#3B82F6',    # Medium blue
    'accent': '#60A5FA',       # Light blue
    'background': '#F3F4F6',   # Light gray
    'surface': '#FFFFFF',      # White
    'error': '#DC2626',        # Red
    'success': '#16A34A',      # Green
    'text': '#1F2937',         # Dark gray
    'text_light': '#6B7280',   # Medium gray
    'border': '#D1D5DB',       # Light border
    'pokemon_red': '#FF0000',
    'pokemon_blue': '#0075BE',
    'pokemon_yellow': '#FFCB05',
}


def get_color_from_hex(hex_color):
    """Convert hex color to Kivy RGBA format"""
    hex_color = hex_color.lstrip('#')
    return [int(hex_color[i:i+2], 16)/255 for i in (0, 2, 4)] + [1]


class TopNavBar(BoxLayout):
    """Top navigation bar with tabs"""

    def __init__(self, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(56)
        self.screen_manager = screen_manager

        # Navigation tabs
        self.tabs = [
            ('Home', 'home'),
            ('Meta', 'meta_decks'),
            ('Decks', 'my_decks'),
            ('Batalhas', 'battles'),
            ('Chat', 'chat'),
        ]

        self.buttons = {}
        for label, screen_name in self.tabs:
            btn = Button(
                text=label,
                size_hint_x=1,
                background_normal='',
                background_color=get_color_from_hex(COLORS['primary']),
                color=get_color_from_hex(COLORS['surface']),
            )
            btn.bind(on_press=lambda x, s=screen_name: self.navigate_to(s))
            self.add_widget(btn)
            self.buttons[screen_name] = btn

    def navigate_to(self, screen_name):
        """Navigate to a screen and update button states"""
        self.screen_manager.current = screen_name

        # Update button colors
        for btn_screen, btn in self.buttons.items():
            if btn_screen == screen_name:
                btn.background_color = get_color_from_hex(COLORS['accent'])
            else:
                btn.background_color = get_color_from_hex(COLORS['primary'])


class HomeScreen(Screen):
    """Home screen with quick actions"""

    def __init__(self, api_client, **kwargs):
        super().__init__(**kwargs)
        self.api_client = api_client

        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

        # Title
        title = Label(
            text='TCG Tool',
            font_size=dp(32),
            size_hint_y=None,
            height=dp(60),
            color=get_color_from_hex(COLORS['primary']),
            bold=True,
        )
        layout.add_widget(title)

        # Quick action buttons
        actions = [
            ('Browse Meta Decks', 'meta_decks'),
            ('My Decks', 'my_decks'),
            ('Import Deck', 'deck_import'),
            ('Search Cards', 'card_search'),
            ('Battles', 'battles'),
            ('Chat Assistant', 'chat'),
        ]

        for label, screen_name in actions:
            btn = Button(
                text=label,
                size_hint_y=None,
                height=dp(50),
                background_normal='',
                background_color=get_color_from_hex(COLORS['secondary']),
                color=get_color_from_hex(COLORS['surface']),
            )
            btn.bind(on_press=lambda x, s=screen_name: setattr(self.manager, 'current', s))
            layout.add_widget(btn)

        self.add_widget(layout)


class MetaDecksScreen(Screen):
    """Meta decks list screen"""

    def __init__(self, api_client, **kwargs):
        super().__init__(**kwargs)
        self.api_client = api_client

        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        # Title
        title = Label(
            text='Meta Decks',
            font_size=dp(24),
            size_hint_y=None,
            height=dp(40),
            color=get_color_from_hex(COLORS['primary']),
            bold=True,
        )
        layout.add_widget(title)

        # Placeholder - will be populated from API
        self.decks_container = BoxLayout(orientation='vertical', spacing=dp(5))
        layout.add_widget(self.decks_container)

        self.add_widget(layout)

    def on_enter(self):
        """Load decks when screen is entered"""
        self.load_decks()

    def load_decks(self):
        """Load meta decks from API"""
        self.decks_container.clear_widgets()

        try:
            decks = self.api_client.get_meta_decks()

            for deck in decks:
                btn = Button(
                    text=f"{deck['name']} (Tier {deck.get('tier', 'N/A')})",
                    size_hint_y=None,
                    height=dp(60),
                    background_normal='',
                    background_color=get_color_from_hex(COLORS['surface']),
                    color=get_color_from_hex(COLORS['text']),
                )
                btn.bind(on_press=lambda x, d=deck: self.view_deck(d))
                self.decks_container.add_widget(btn)
        except Exception as e:
            error_label = Label(
                text=f'Error loading decks: {str(e)}',
                color=get_color_from_hex(COLORS['error']),
            )
            self.decks_container.add_widget(error_label)

    def view_deck(self, deck):
        """Navigate to deck detail screen"""
        detail_screen = self.manager.get_screen('deck_detail')
        detail_screen.load_deck(deck)
        self.manager.current = 'deck_detail'


class DeckDetailScreen(Screen):
    """Deck detail screen"""

    def __init__(self, api_client, **kwargs):
        super().__init__(**kwargs)
        self.api_client = api_client
        self.current_deck = None

        self.layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        self.add_widget(self.layout)

    def load_deck(self, deck):
        """Load and display deck details"""
        self.current_deck = deck
        self.layout.clear_widgets()

        # Back button
        back_btn = Button(
            text='< Back',
            size_hint_y=None,
            height=dp(40),
            background_normal='',
            background_color=get_color_from_hex(COLORS['secondary']),
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'meta_decks'))
        self.layout.add_widget(back_btn)

        # Deck name
        name_label = Label(
            text=deck.get('name', 'Unknown Deck'),
            font_size=dp(24),
            size_hint_y=None,
            height=dp(40),
            color=get_color_from_hex(COLORS['primary']),
            bold=True,
        )
        self.layout.add_widget(name_label)

        # Deck info
        info_text = f"Archetype: {deck.get('archetype', 'N/A')}\n"
        info_text += f"Tier: {deck.get('tier', 'N/A')}\n"
        info_text += f"Win Rate: {deck.get('win_rate', 'N/A')}%"

        info_label = Label(
            text=info_text,
            size_hint_y=None,
            height=dp(80),
            color=get_color_from_hex(COLORS['text']),
        )
        self.layout.add_widget(info_label)


class CardSearchScreen(Screen):
    """Card search screen"""

    def __init__(self, api_client, **kwargs):
        super().__init__(**kwargs)
        self.api_client = api_client

        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        title = Label(
            text='Search Cards',
            font_size=dp(24),
            size_hint_y=None,
            height=dp(40),
            color=get_color_from_hex(COLORS['primary']),
            bold=True,
        )
        layout.add_widget(title)

        # Placeholder
        placeholder = Label(text='Card search coming soon...')
        layout.add_widget(placeholder)

        self.add_widget(layout)


class MyDecksScreen(Screen):
    """User's personal decks screen"""

    def __init__(self, api_client, **kwargs):
        super().__init__(**kwargs)
        self.api_client = api_client

        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        title = Label(
            text='My Decks',
            font_size=dp(24),
            size_hint_y=None,
            height=dp(40),
            color=get_color_from_hex(COLORS['primary']),
            bold=True,
        )
        layout.add_widget(title)

        # Placeholder
        placeholder = Label(text='Your decks will appear here...')
        layout.add_widget(placeholder)

        self.add_widget(layout)


class DeckImportScreen(Screen):
    """Deck import screen"""

    def __init__(self, api_client, **kwargs):
        super().__init__(**kwargs)
        self.api_client = api_client

        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        title = Label(
            text='Import Deck',
            font_size=dp(24),
            size_hint_y=None,
            height=dp(40),
            color=get_color_from_hex(COLORS['primary']),
            bold=True,
        )
        layout.add_widget(title)

        # Placeholder
        placeholder = Label(text='Deck import coming soon...')
        layout.add_widget(placeholder)

        self.add_widget(layout)


class BattlesScreen(Screen):
    """Battles tracking screen"""

    def __init__(self, api_client, **kwargs):
        super().__init__(**kwargs)
        self.api_client = api_client

        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        title = Label(
            text='Battles',
            font_size=dp(24),
            size_hint_y=None,
            height=dp(40),
            color=get_color_from_hex(COLORS['primary']),
            bold=True,
        )
        layout.add_widget(title)

        # Placeholder
        placeholder = Label(text='Battle tracking coming soon...')
        layout.add_widget(placeholder)

        self.add_widget(layout)


class ChatScreen(Screen):
    """AI chat assistant screen"""

    def __init__(self, api_client, **kwargs):
        super().__init__(**kwargs)
        self.api_client = api_client

        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        title = Label(
            text='Chat Assistant',
            font_size=dp(24),
            size_hint_y=None,
            height=dp(40),
            color=get_color_from_hex(COLORS['primary']),
            bold=True,
        )
        layout.add_widget(title)

        # Placeholder
        placeholder = Label(text='AI chat assistant coming soon...')
        layout.add_widget(placeholder)

        self.add_widget(layout)


class SettingsScreen(Screen):
    """Settings screen"""

    def __init__(self, api_client, **kwargs):
        super().__init__(**kwargs)
        self.api_client = api_client

        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        title = Label(
            text='Settings',
            font_size=dp(24),
            size_hint_y=None,
            height=dp(40),
            color=get_color_from_hex(COLORS['primary']),
            bold=True,
        )
        layout.add_widget(title)

        # Placeholder
        placeholder = Label(text='Settings coming soon...')
        layout.add_widget(placeholder)

        self.add_widget(layout)


class TCGToolApp(App):
    """Main application class"""

    def build(self):
        # Initialize services
        self.api_client = APIClient()
        self.offline_cache = OfflineCache()
        self.sync_service = SyncService(self.api_client, self.offline_cache)

        # Start background sync
        self.sync_service.sync_in_background()

        # Set window size for desktop testing (Samsung Galaxy Z Fold 6 main screen)
        if platform not in ('android', 'ios'):
            Window.size = (755, 907)

        # Main layout
        main_layout = BoxLayout(orientation='vertical')

        # Screen manager
        sm = ScreenManager()

        # Add screens
        sm.add_widget(HomeScreen(name='home', api_client=self.api_client))
        sm.add_widget(MetaDecksScreen(name='meta_decks', api_client=self.api_client))
        sm.add_widget(DeckDetailScreen(name='deck_detail', api_client=self.api_client))
        sm.add_widget(CardSearchScreen(name='card_search', api_client=self.api_client))
        sm.add_widget(MyDecksScreen(name='my_decks', api_client=self.api_client))
        sm.add_widget(DeckImportScreen(name='deck_import', api_client=self.api_client))
        sm.add_widget(BattlesScreen(name='battles', api_client=self.api_client))
        sm.add_widget(ChatScreen(name='chat', api_client=self.api_client))
        sm.add_widget(SettingsScreen(name='settings', api_client=self.api_client))

        # Add navigation bar
        nav_bar = TopNavBar(sm)
        main_layout.add_widget(nav_bar)

        # Add screen manager
        main_layout.add_widget(sm)

        return main_layout

    def on_stop(self):
        """Cleanup on app exit"""
        pass


if __name__ == '__main__':
    TCGToolApp().run()
