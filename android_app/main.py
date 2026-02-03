"""
TCG Meta Analyzer - Pokemon TCG App
Redesigned layout based on wireframe specifications
Features: Top navigation, Deck Builder, Meta Browser, Settings, Profile
"""
import sys
import os

# Add the script's directory to path for imports to work from any location
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# =============================================================================
# CRITICAL: Ensure Kivy metrics are initialized before ANY widgets are created
# This fixes ZeroDivisionError in sp() function on Android startup
# The Switch widget uses sp(41) in its style.kv which fails when density=0
# =============================================================================
import os
os.environ.setdefault('KIVY_METRICS_DENSITY', '1')
os.environ.setdefault('KIVY_METRICS_FONTSCALE', '1')
os.environ.setdefault('KIVY_DPI', '96')

from kivy.metrics import Metrics

def _ensure_metrics_density():
    """Ensure Metrics.density has a valid value to prevent sp() division by zero."""
    try:
        current_density = Metrics.density
        if current_density is None or current_density <= 0:
            # Force reset metrics with safe defaults
            Metrics.reset_metrics()
    except Exception:
        pass

_ensure_metrics_density()
# =============================================================================

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.switch import Switch
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, NoTransition
from kivy.uix.widget import Widget
from kivy.uix.image import AsyncImage
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex, platform
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line, Ellipse
from kivy.clock import Clock
from kivy.properties import StringProperty, ListProperty, BooleanProperty

# Only set window size on desktop (not Android)
# Samsung Galaxy Z Fold 6 screen sizes (approximate dp):
# - Cover screen: ~266dp x 681dp (very narrow)
# - Main screen: ~755dp x 907dp (tablet-like)
# Testing with main screen size by default (scaled for desktop)
if platform not in ('android', 'ios'):
    # Use main screen size for testing (better for development)
    Window.size = (755, 907)  # Main screen dp size
    # Uncomment below to test cover screen:
    # Window.size = (320, 720)  # Cover screen simulation

# Import meta database
from meta_data import (
    META_DECKS, MATCHUPS, Language,
    get_matchup, get_deck_matchups, get_all_decks,
    get_translation, get_difficulty_translation
)

# Import new screens
from screens.import_screen import ImportScreen
from screens.my_decks_screen import MyDecksScreen
from screens.deck_editor_screen import DeckEditorScreen
from screens.comparison_screen import ComparisonScreen
from screens.news_screen import NewsScreen
from screens.calendar_screen import CalendarScreen
from screens.match_analysis_screen import MatchAnalysisScreen

# Import responsive utilities for Samsung Fold 6
from utils.responsive import (
    get_responsive_manager,
    ScreenMode,
    is_cover_mode,
    is_main_mode,
    scaled_font,
    get_padding,
    get_spacing,
)

# =============================================================================
# COLOR SCHEME - Light theme based on wireframe
# =============================================================================
COLORS = {
    'background': '#f5f5f5',
    'surface': '#ffffff',
    'surface_light': '#fafafa',
    'card': '#ffffff',
    'card_hover': '#f0f0f0',
    'primary': '#4caf50',  # Green from wireframe
    'primary_dark': '#388e3c',
    'secondary': '#2196f3',  # Blue
    'secondary_light': '#64b5f6',
    'accent': '#ff9800',  # Orange
    'warning': '#ff9800',
    'danger': '#f44336',
    'success': '#4caf50',
    'text': '#212121',
    'text_secondary': '#757575',
    'text_muted': '#9e9e9e',
    'border': '#e0e0e0',
    'nav_bg': '#4caf50',  # Green navigation bar
    'nav_text': '#ffffff',
    'nav_inactive': '#81c784',
    'button_blue': '#2196f3',
    'button_green': '#4caf50',
    'button_yellow': '#ffc107',
    'divider': '#eeeeee',
    # Type colors
    'fire': '#ff9c54',
    'water': '#4d90d5',
    'lightning': '#f3d23b',
    'psychic': '#f97176',
    'fighting': '#ce4069',
    'darkness': '#5a5366',
    'metal': '#5a8ea1',
    'dragon': '#0a6dc4',
    'grass': '#5fbd58',
    'colorless': '#9099a1',
}

# Deck visual info
DECK_INFO = {
    'gholdengo': {
        'name': 'Gholdengo ex',
        'icon_url': 'https://img.pokemondb.net/sprites/scarlet-violet/normal/gholdengo.png',
        'card_url': 'https://images.pokemontcg.io/sv4/139_hires.png',
        'type': 'metal',
    },
    'dragapult': {
        'name': 'Dragapult ex',
        'icon_url': 'https://img.pokemondb.net/sprites/home/normal/dragapult.png',
        'card_url': 'https://images.pokemontcg.io/sv6/130_hires.png',
        'type': 'psychic',
    },
    'gardevoir': {
        'name': 'Gardevoir ex',
        'icon_url': 'https://img.pokemondb.net/sprites/home/normal/gardevoir.png',
        'card_url': 'https://images.pokemontcg.io/sv1/86_hires.png',
        'type': 'psychic',
    },
    'charizard': {
        'name': 'Charizard ex',
        'icon_url': 'https://img.pokemondb.net/sprites/home/normal/charizard.png',
        'card_url': 'https://images.pokemontcg.io/sv3/125_hires.png',
        'type': 'fire',
    },
    'raging_bolt': {
        'name': 'Raging Bolt ex',
        'icon_url': 'https://img.pokemondb.net/sprites/scarlet-violet/normal/raging-bolt.png',
        'card_url': 'https://images.pokemontcg.io/sv5/123_hires.png',
        'type': 'lightning',
    },
    'grimmsnarl': {
        'name': "Marnie's Grimmsnarl",
        'icon_url': 'https://img.pokemondb.net/sprites/home/normal/grimmsnarl.png',
        'card_url': 'https://images.pokemontcg.io/sv6pt5/72_hires.png',
        'type': 'darkness',
    },
    'joltik_box': {
        'name': 'Joltik Box',
        'icon_url': 'https://img.pokemondb.net/sprites/home/normal/galvantula.png',
        'card_url': 'https://images.pokemontcg.io/sv3/63_hires.png',
        'type': 'lightning',
    },
    'flareon': {
        'name': 'Flareon ex',
        'icon_url': 'https://img.pokemondb.net/sprites/home/normal/flareon.png',
        'card_url': 'https://images.pokemontcg.io/sv7/36_hires.png',
        'type': 'fire',
    },
}

def get_deck_info(deck_id):
    return DECK_INFO.get(deck_id, {})

def get_type_color(type_name):
    return COLORS.get(type_name.lower(), COLORS['secondary'])


# =============================================================================
# BASIC COMPONENTS
# =============================================================================

class ColoredBox(BoxLayout):
    """BoxLayout with background color."""

    def __init__(self, bg_color=None, radius=0, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color or COLORS['background']
        self.radius = radius
        with self.canvas.before:
            Color(*get_color_from_hex(self.bg_color))
            if radius > 0:
                self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(radius)])
            else:
                self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update, size=self._update)

    def _update(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class CardBox(BoxLayout):
    """Card-style container with shadow effect."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            # Shadow
            Color(0, 0, 0, 0.1)
            self.shadow = RoundedRectangle(
                pos=(self.x + dp(2), self.y - dp(2)),
                size=self.size,
                radius=[dp(8)]
            )
            # Card background
            Color(*get_color_from_hex(COLORS['card']))
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])
            # Border
            Color(*get_color_from_hex(COLORS['border']))
            self.border = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(8)), width=1)
        self.bind(pos=self._update, size=self._update)

    def _update(self, *args):
        self.shadow.pos = (self.x + dp(2), self.y - dp(2))
        self.shadow.size = self.size
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.border.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(8))


class PrimaryButton(Button):
    """Green primary button - responsive sizing."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = get_color_from_hex(COLORS['primary'])
        self.color = get_color_from_hex(COLORS['nav_text'])
        responsive = get_responsive_manager()
        self.font_size = sp(16 * responsive.font_scale)
        self.bold = True
        # Ensure minimum touch target
        if self.height < responsive.touch_target:
            self.height = responsive.touch_target


class SecondaryButton(Button):
    """Blue secondary button - responsive sizing."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = get_color_from_hex(COLORS['button_blue'])
        self.color = get_color_from_hex(COLORS['nav_text'])
        responsive = get_responsive_manager()
        self.font_size = sp(16 * responsive.font_scale)
        self.bold = True
        if self.height < responsive.touch_target:
            self.height = responsive.touch_target


class OutlineButton(Button):
    """Outlined button with border - responsive sizing."""

    def __init__(self, border_color=None, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = get_color_from_hex(COLORS['surface'])
        self.color = get_color_from_hex(border_color or COLORS['primary'])
        responsive = get_responsive_manager()
        self.font_size = sp(14 * responsive.font_scale)
        self.border_color = border_color or COLORS['primary']

        with self.canvas.after:
            Color(*get_color_from_hex(self.border_color))
            self.border_line = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(6)), width=dp(2))
        self.bind(pos=self._update, size=self._update)

    def _update(self, *args):
        self.border_line.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(6))


class PlaceholderCard(BoxLayout):
    """Placeholder card widget for deck builder."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*get_color_from_hex(COLORS['border']))
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(4)])
        self.bind(pos=self._update, size=self._update)

        # X mark
        self.add_widget(Label(
            text='X',
            font_size=sp(24),
            color=get_color_from_hex(COLORS['text_muted'])
        ))

    def _update(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size


# =============================================================================
# TOP NAVIGATION BAR
# =============================================================================

class TopNavBar(ColoredBox):
    """Top navigation bar with app title and tabs - responsive for Samsung Fold 6."""

    def __init__(self, **kwargs):
        super().__init__(bg_color=COLORS['nav_bg'], **kwargs)
        self.responsive = get_responsive_manager()
        self.orientation = 'vertical'
        self.size_hint_y = None
        # Use responsive nav height
        self._update_height()
        self.responsive.bind(screen_mode=self._on_mode_change)

        self._build_nav()

    def _update_height(self):
        """Update nav bar height based on screen mode."""
        # Cover mode: more compact, Main mode: larger
        if self.responsive.is_cover_mode:
            self.height = dp(110)
        elif self.responsive.is_main_mode:
            self.height = dp(130)
        else:
            self.height = dp(120)

    def _on_mode_change(self, instance, mode):
        """Rebuild nav bar when screen mode changes."""
        self._update_height()
        self.clear_widgets()
        self._build_nav()

    def _build_nav(self):
        """Build navigation bar content."""
        font_scale = self.responsive.font_scale
        is_cover = self.responsive.is_cover_mode

        # App title row
        title_height = dp(48) if not is_cover else dp(44)
        title_row = BoxLayout(size_hint_y=None, height=title_height, padding=[dp(16), dp(8)])

        title_label = Label(
            text='[b]Pokemon TCG App[/b]',
            markup=True,
            font_size=sp(20 * font_scale),
            color=get_color_from_hex(COLORS['nav_text']),
            halign='left',
            valign='middle'
        )
        title_label.bind(size=title_label.setter('text_size'))
        title_row.add_widget(title_label)

        # Quick actions indicator - hide on cover screen to save space
        if not is_cover:
            quick_box = BoxLayout(size_hint_x=None, width=dp(120))
            quick_label = Label(
                text='[size={}sp]Quick Actions\nView all your\nquick actions[/size]'.format(int(11 * font_scale)),
                markup=True,
                font_size=sp(11 * font_scale),
                color=get_color_from_hex(COLORS['nav_text']),
                halign='right',
                valign='middle'
            )
            quick_label.bind(size=quick_label.setter('text_size'))
            quick_box.add_widget(quick_label)
            title_row.add_widget(quick_box)

        self.add_widget(title_row)

        # Tab row - responsive font and spacing
        tab_height = dp(52) if not is_cover else dp(48)
        self.tab_row = BoxLayout(
            size_hint_y=None,
            height=tab_height,
            spacing=dp(4),
            padding=[dp(8), dp(4)]
        )
        self.tabs = {}

        # Show fewer tabs on cover screen
        if is_cover:
            tab_items = [
                ('Home', 'home'),
                ('Meta', 'meta'),
                ('Decks', 'my_decks'),
                ('More', 'settings'),
            ]
        else:
            tab_items = [
                ('Home', 'home'),
                ('Meta Decks', 'meta'),
                ('My Decks', 'my_decks'),
                ('Import', 'import'),
                ('Builder', 'deck_builder'),
            ]

        tab_font_size = sp(13 * font_scale) if not is_cover else sp(12)

        for text, screen_id in tab_items:
            btn = Button(
                text=text,
                font_size=tab_font_size,
                background_normal='',
                background_down='',
                background_color=(1, 1, 1, 0.2) if screen_id != 'home' else (1, 1, 1, 0.4),
                color=get_color_from_hex(COLORS['nav_text']),
                size_hint_x=1,
                size_hint_y=1
            )
            btn.screen_id = screen_id
            btn.bind(on_press=self.on_tab_press)
            self.tabs[screen_id] = btn
            self.tab_row.add_widget(btn)

        self.add_widget(self.tab_row)

    def on_tab_press(self, btn):
        app = App.get_running_app()
        if app.root:
            app.root.current = btn.screen_id
            self.update_active_tab(btn.screen_id)

    def update_active_tab(self, active_id):
        for screen_id, btn in self.tabs.items():
            if screen_id == active_id:
                btn.background_color = (1, 1, 1, 0.4)
            else:
                btn.background_color = (1, 1, 1, 0.2)


# =============================================================================
# SCREEN BASE CLASS
# =============================================================================

class BaseScreen(Screen):
    """Base screen with common navigation and responsive support."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.responsive = get_responsive_manager()
        self.main_layout = ColoredBox(orientation='vertical', bg_color=COLORS['background'])

        # Top navigation
        self.nav_bar = TopNavBar()
        self.main_layout.add_widget(self.nav_bar)

        # Content area
        self.content = BoxLayout(orientation='vertical')
        self.main_layout.add_widget(self.content)

        self.add_widget(self.main_layout)

        # Bind to screen mode changes for responsive layouts
        self.responsive.bind(screen_mode=self._on_screen_mode_change)

    def on_enter(self):
        self.nav_bar.update_active_tab(self.name)

    def _on_screen_mode_change(self, instance, mode):
        """Handle screen mode change - override in subclasses for custom behavior."""
        pass

    @property
    def is_cover_mode(self):
        """Check if in cover screen mode (narrow)."""
        return self.responsive.is_cover_mode

    @property
    def is_main_mode(self):
        """Check if in main screen mode (expanded)."""
        return self.responsive.is_main_mode

    @property
    def grid_columns(self):
        """Get recommended grid columns for current mode."""
        return self.responsive.grid_columns

    def get_scaled_font(self, base_sp):
        """Get scaled font size for current mode."""
        return sp(base_sp * self.responsive.font_scale)


# =============================================================================
# HOME SCREEN
# =============================================================================

class HomeScreen(BaseScreen):
    """Welcome home screen with main actions - responsive for Samsung Fold 6."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def _on_screen_mode_change(self, instance, mode):
        """Rebuild UI when screen mode changes."""
        self.content.clear_widgets()
        self.build_ui()

    def build_ui(self):
        # Adapt layout based on screen mode
        is_expanded = self.is_main_mode
        is_cover = self.is_cover_mode
        font_scale = self.responsive.font_scale

        # Responsive padding and sizes
        padding_h = dp(24) if is_expanded else (dp(16) if is_cover else dp(20))
        padding_v = dp(32) if is_expanded else (dp(20) if is_cover else dp(28))
        welcome_height = dp(280) if is_expanded else (dp(220) if is_cover else dp(240))

        # Welcome section
        welcome_box = ColoredBox(
            orientation='vertical',
            bg_color=COLORS['surface'],
            size_hint_y=None,
            height=welcome_height,
            padding=[padding_h, padding_v]
        )

        welcome_title = Label(
            text='[b]Welcome to Pokemon TCG App![/b]',
            markup=True,
            font_size=sp(22 * font_scale),
            color=get_color_from_hex(COLORS['text']),
            halign='center',
            valign='middle',
            size_hint_y=0.25
        )
        welcome_title.bind(size=welcome_title.setter('text_size'))
        welcome_box.add_widget(welcome_title)

        welcome_desc = Label(
            text='Explore meta decks, build your own, and stay ahead in\ncompetitive play.',
            font_size=sp(15 * font_scale),
            color=get_color_from_hex(COLORS['text_secondary']),
            halign='center',
            valign='middle',
            size_hint_y=0.20
        )
        welcome_desc.bind(size=welcome_desc.setter('text_size'))
        welcome_box.add_widget(welcome_desc)

        # Main action buttons - larger touch targets
        btn_padding = dp(24) if is_cover else dp(40)
        btn_box = BoxLayout(
            orientation='vertical',
            spacing=dp(14),
            size_hint_y=0.55,
            padding=[btn_padding, dp(12)]
        )

        btn_height = self.responsive.button_height

        meta_btn = PrimaryButton(
            text='Meta Decks',
            size_hint_y=None,
            height=btn_height
        )
        meta_btn.bind(on_press=lambda x: self.go_to('meta'))

        my_decks_btn = SecondaryButton(
            text='My Decks',
            size_hint_y=None,
            height=btn_height
        )
        my_decks_btn.bind(on_press=lambda x: self.go_to('my_decks'))

        btn_box.add_widget(meta_btn)
        btn_box.add_widget(my_decks_btn)
        welcome_box.add_widget(btn_box)

        self.content.add_widget(welcome_box)

        # Quick actions section - responsive for Fold 6
        quick_height = dp(220) if is_expanded else (dp(140) if is_cover else dp(160))
        quick_section = ColoredBox(
            orientation='vertical',
            bg_color=COLORS['surface'],
            size_hint_y=None,
            height=quick_height,
            padding=[dp(16), dp(16)],
            spacing=dp(12)
        )

        quick_title = Label(
            text='[b]Quick Actions[/b]',
            markup=True,
            font_size=sp(16 * font_scale),
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            size_hint_y=None,
            height=dp(28)
        )
        quick_title.bind(size=quick_title.setter('text_size'))
        quick_section.add_widget(quick_title)

        # Use GridLayout for better responsiveness
        quick_btn_height = dp(88) if is_expanded else (dp(72) if is_cover else dp(80))

        if is_expanded:
            # Main screen: 2x3 grid layout
            quick_btns = GridLayout(
                cols=3,
                spacing=dp(16),
                size_hint_y=None,
                height=quick_btn_height * 2 + dp(16)
            )
        elif is_cover:
            # Cover screen: vertical stack for better touch targets
            quick_btns = GridLayout(
                cols=3,
                spacing=dp(8),
                size_hint_y=None,
                height=quick_btn_height
            )
        else:
            # Phone: single row
            quick_btns = BoxLayout(spacing=dp(12), size_hint_y=None, height=quick_btn_height)

        import_btn = OutlineButton(
            text='Import\nDeck',
            border_color=COLORS['primary']
        )
        import_btn.bind(on_press=lambda x: self.go_to('import'))

        builder_btn = OutlineButton(
            text='Deck\nBuilder',
            border_color=COLORS['secondary']
        )
        builder_btn.bind(on_press=lambda x: self.go_to('deck_builder'))

        compare_btn = OutlineButton(
            text='Compare\nDecks',
            border_color=COLORS['accent']
        )
        compare_btn.bind(on_press=lambda x: self.go_to('comparison'))

        quick_btns.add_widget(import_btn)
        quick_btns.add_widget(builder_btn)
        quick_btns.add_widget(compare_btn)

        # Add extra buttons on main screen
        if is_expanded:
            news_btn = OutlineButton(
                text='News &\nEvents',
                border_color=COLORS['primary_dark']
            )
            news_btn.bind(on_press=lambda x: self.go_to('news'))

            calendar_btn = OutlineButton(
                text='Calendar',
                border_color=COLORS['secondary']
            )
            calendar_btn.bind(on_press=lambda x: self.go_to('calendar'))

            my_decks_btn2 = OutlineButton(
                text='My\nDecks',
                border_color=COLORS['success']
            )
            my_decks_btn2.bind(on_press=lambda x: self.go_to('my_decks'))

            quick_btns.add_widget(news_btn)
            quick_btns.add_widget(calendar_btn)
            quick_btns.add_widget(my_decks_btn2)

        quick_section.add_widget(quick_btns)
        self.content.add_widget(quick_section)

        # Spacer
        self.content.add_widget(Widget())

    def go_to(self, screen):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = screen


# =============================================================================
# META DECKS LIST SCREEN
# =============================================================================

class MetaDecksScreen(BaseScreen):
    """Meta decks list with search - responsive for Samsung Fold 6."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def _on_screen_mode_change(self, instance, mode):
        """Rebuild UI when screen mode changes."""
        self.content.clear_widgets()
        self.build_ui()
        self.refresh_list()

    def build_ui(self):
        font_scale = self.responsive.font_scale
        is_cover = self.is_cover_mode

        # Header - responsive height
        header_height = dp(100) if not is_cover else dp(88)
        header = ColoredBox(
            orientation='vertical',
            bg_color=COLORS['surface'],
            size_hint_y=None,
            height=header_height,
            padding=[dp(16), dp(14)]
        )

        title = Label(
            text='[b]Meta Decks List[/b]',
            markup=True,
            font_size=sp(20 * font_scale),
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            valign='middle',
            size_hint_y=0.4
        )
        title.bind(size=title.setter('text_size'))
        header.add_widget(title)

        # Search bar - larger touch target
        search_height = dp(44) if not is_cover else dp(40)
        search_box = BoxLayout(size_hint_y=None, height=search_height, spacing=dp(8))
        self.search_input = TextInput(
            hint_text='Search decks...',
            multiline=False,
            font_size=sp(16 * font_scale),
            background_color=get_color_from_hex(COLORS['surface_light']),
            foreground_color=get_color_from_hex(COLORS['text']),
            hint_text_color=get_color_from_hex(COLORS['text_muted']),
            padding=[dp(16), dp(10)]
        )
        search_box.add_widget(self.search_input)
        header.add_widget(search_box)

        self.content.add_widget(header)

        # Deck list
        scroll = ScrollView()
        self.deck_list = GridLayout(
            cols=1,
            spacing=dp(12),
            padding=[dp(16), dp(14)],
            size_hint_y=None
        )
        self.deck_list.bind(minimum_height=self.deck_list.setter('height'))
        scroll.add_widget(self.deck_list)
        self.content.add_widget(scroll)

    def on_enter(self):
        super().on_enter()
        self.refresh_list()

    def refresh_list(self):
        self.deck_list.clear_widgets()
        lang = App.get_running_app().current_language

        for i, deck in enumerate(get_all_decks()[:8], 1):
            item = self._create_deck_item(i, deck, lang)
            self.deck_list.add_widget(item)

    def _create_deck_item(self, rank, deck, lang):
        """Create a deck list item - responsive sizing."""
        font_scale = self.responsive.font_scale
        is_cover = self.is_cover_mode

        # Larger list items for better touch targets
        item_height = self.responsive.list_item_height + dp(16)

        item = CardBox(
            orientation='horizontal',
            size_hint_y=None,
            height=item_height,
            padding=[dp(14), dp(12)],
            spacing=dp(14)
        )

        # Deck info
        info = BoxLayout(orientation='vertical', spacing=dp(6))

        name_label = Label(
            text=f'[b]Deck Name {rank}[/b]',
            markup=True,
            font_size=sp(16 * font_scale),
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            valign='middle',
            size_hint_y=0.35
        )
        name_label.bind(size=name_label.setter('text_size'))

        # Subtitle shows real deck name
        sub_label = Label(
            text=f'{deck.get_name(lang)} | Tier {deck.tier} | {deck.meta_share:.1f}% meta',
            font_size=sp(13 * font_scale),
            color=get_color_from_hex(COLORS['text_secondary']),
            halign='left',
            valign='middle',
            size_hint_y=0.35
        )
        sub_label.bind(size=sub_label.setter('text_size'))

        desc_label = Label(
            text='Competitive meta deck with balanced strategy...',
            font_size=sp(12 * font_scale),
            color=get_color_from_hex(COLORS['text_muted']),
            halign='left',
            valign='middle',
            size_hint_y=0.3
        )
        desc_label.bind(size=desc_label.setter('text_size'))

        info.add_widget(name_label)
        info.add_widget(sub_label)
        info.add_widget(desc_label)
        item.add_widget(info)

        # View button - larger touch target
        btn_width = dp(72) if not is_cover else dp(64)
        btn_height = dp(44) if not is_cover else dp(40)

        view_btn = SecondaryButton(
            text='View',
            size_hint=(None, None),
            size=(btn_width, btn_height)
        )
        view_btn.deck_id = deck.id
        view_btn.bind(on_press=self.view_deck)

        btn_box = AnchorLayout(size_hint_x=None, width=btn_width + dp(12))
        btn_box.add_widget(view_btn)
        item.add_widget(btn_box)

        return item

    def view_deck(self, btn):
        app = App.get_running_app()
        app.selected_deck_id = btn.deck_id
        self.manager.current = 'details'


# =============================================================================
# DECK BUILDER SCREEN
# =============================================================================

class DeckBuilderScreen(BaseScreen):
    """Deck builder with filters and card grid - responsive for Samsung Fold 6."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def _on_screen_mode_change(self, instance, mode):
        """Rebuild UI when screen mode changes."""
        self.content.clear_widgets()
        self.build_ui()

    def build_ui(self):
        font_scale = self.responsive.font_scale
        is_cover = self.is_cover_mode

        # Header
        header_height = dp(64) if not is_cover else dp(56)
        header = ColoredBox(
            orientation='vertical',
            bg_color=COLORS['surface'],
            size_hint_y=None,
            height=header_height,
            padding=[dp(16), dp(14)]
        )

        title = Label(
            text='[b]Deck Builder[/b]',
            markup=True,
            font_size=sp(20 * font_scale),
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        header.add_widget(title)
        self.content.add_widget(header)

        # Form section - larger inputs
        form_height = dp(180) if not is_cover else dp(160)
        form_box = ColoredBox(
            orientation='vertical',
            bg_color=COLORS['surface'],
            size_hint_y=None,
            height=form_height,
            padding=[dp(16), dp(14)],
            spacing=dp(12)
        )

        # Name field - larger
        input_height = dp(44) if not is_cover else dp(40)
        name_row = BoxLayout(size_hint_y=None, height=input_height, spacing=dp(12))
        name_label = Label(
            text='Name:',
            font_size=sp(15 * font_scale),
            color=get_color_from_hex(COLORS['text']),
            size_hint_x=None,
            width=dp(60),
            halign='left',
            valign='middle'
        )
        name_label.bind(size=name_label.setter('text_size'))
        name_input = TextInput(
            hint_text='Enter deck name...',
            multiline=False,
            font_size=sp(15 * font_scale),
            background_color=get_color_from_hex(COLORS['surface_light']),
            foreground_color=get_color_from_hex(COLORS['text']),
            padding=[dp(12), dp(10)]
        )
        name_row.add_widget(name_label)
        name_row.add_widget(name_input)
        form_box.add_widget(name_row)

        # Type and Set dropdowns - larger
        filter_row = BoxLayout(size_hint_y=None, height=input_height, spacing=dp(16))

        type_spinner = Spinner(
            text='Type',
            values=['All', 'Pokemon', 'Trainer', 'Energy'],
            font_size=sp(14 * font_scale),
            background_color=get_color_from_hex(COLORS['surface_light']),
            color=get_color_from_hex(COLORS['text'])
        )

        set_spinner = Spinner(
            text='Set',
            values=['All', 'SVI', 'PAL', 'OBF', 'MEW', 'PAR', 'TEF', 'TWM'],
            font_size=sp(14 * font_scale),
            background_color=get_color_from_hex(COLORS['surface_light']),
            color=get_color_from_hex(COLORS['text'])
        )

        filter_row.add_widget(type_spinner)
        filter_row.add_widget(set_spinner)
        form_box.add_widget(filter_row)

        # Add card button - larger
        btn_height = self.responsive.button_height
        add_btn = PrimaryButton(
            text='+ Add Card',
            size_hint_y=None,
            height=btn_height
        )
        add_btn.bind(on_press=lambda x: self.go_to_search())
        form_box.add_widget(add_btn)

        self.content.add_widget(form_box)

        # Card grid
        grid_scroll = ScrollView()
        card_grid = GridLayout(
            cols=4,
            spacing=dp(8),
            padding=[dp(16), dp(12)],
            size_hint_y=None,
            row_default_height=dp(100)
        )
        card_grid.bind(minimum_height=card_grid.setter('height'))

        # Add placeholder cards (8 cards, 2 rows)
        for _ in range(8):
            placeholder = PlaceholderCard(size_hint=(1, None), height=dp(90))
            card_grid.add_widget(placeholder)

        grid_scroll.add_widget(card_grid)
        self.content.add_widget(grid_scroll)

        # Current deck section
        deck_section = ColoredBox(
            orientation='vertical',
            bg_color=COLORS['surface'],
            size_hint_y=None,
            height=dp(120),
            padding=[dp(16), dp(8)]
        )

        deck_title = Label(
            text='[b]Current Deck (0/60)[/b]',
            markup=True,
            font_size=sp(14),
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            size_hint_y=0.25
        )
        deck_title.bind(size=deck_title.setter('text_size'))
        deck_section.add_widget(deck_title)

        # Mini card icons
        mini_scroll = ScrollView(size_hint_y=0.75, do_scroll_y=False)
        mini_grid = BoxLayout(
            orientation='horizontal',
            size_hint=(None, 1),
            spacing=dp(8),
            padding=[0, dp(4)]
        )
        mini_grid.bind(minimum_width=mini_grid.setter('width'))

        for _ in range(6):
            mini_card = PlaceholderCard(size_hint=(None, None), size=(dp(50), dp(70)))
            mini_grid.add_widget(mini_card)

        mini_scroll.add_widget(mini_grid)
        deck_section.add_widget(mini_scroll)

        self.content.add_widget(deck_section)

    def go_to_search(self):
        self.manager.current = 'card_search'


# =============================================================================
# META DECK DETAILS SCREEN
# =============================================================================

class DeckDetailsScreen(BaseScreen):
    """Detailed deck view with tabs."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_tab = 'list'
        self.current_deck = None
        self.build_ui()

    def build_ui(self):
        # Header with deck name
        self.header = ColoredBox(
            orientation='vertical',
            bg_color=COLORS['surface'],
            size_hint_y=None,
            height=dp(60),
            padding=[dp(16), dp(12)]
        )

        self.title_label = Label(
            text='[b]Meta Deck Details[/b]',
            markup=True,
            font_size=sp(18),
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            size_hint_y=0.5
        )
        self.title_label.bind(size=self.title_label.setter('text_size'))
        self.header.add_widget(self.title_label)

        # Tab buttons
        tab_row = BoxLayout(size_hint_y=0.5, spacing=dp(8))

        self.list_tab = OutlineButton(
            text='Complete List',
            border_color=COLORS['primary']
        )
        self.list_tab.bind(on_press=lambda x: self.switch_tab('list'))

        self.compare_tab = OutlineButton(
            text='Compare with meta decks',
            border_color=COLORS['text_muted']
        )
        self.compare_tab.bind(on_press=lambda x: self.switch_tab('compare'))

        tab_row.add_widget(self.list_tab)
        tab_row.add_widget(self.compare_tab)
        self.header.add_widget(tab_row)

        self.content.add_widget(self.header)

        # Strategy notes section
        self.strategy_box = CardBox(
            orientation='vertical',
            size_hint_y=None,
            height=dp(100),
            padding=[dp(12), dp(8)]
        )

        strategy_title = Label(
            text='[b]Deck Notes[/b]',
            markup=True,
            font_size=sp(13),
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            size_hint_y=0.25
        )
        strategy_title.bind(size=strategy_title.setter('text_size'))

        self.strategy_text = Label(
            text='Strategy notes: This deck features an early setup with high damage board utility that specializes in Trainers and Special cards.',
            font_size=sp(11),
            color=get_color_from_hex(COLORS['text_secondary']),
            halign='left',
            valign='top',
            size_hint_y=0.75
        )
        self.strategy_text.bind(size=self.strategy_text.setter('text_size'))

        self.strategy_box.add_widget(strategy_title)
        self.strategy_box.add_widget(self.strategy_text)

        strategy_container = BoxLayout(
            size_hint_y=None,
            height=dp(110),
            padding=[dp(16), dp(8)]
        )
        strategy_container.add_widget(self.strategy_box)
        self.content.add_widget(strategy_container)

        # Card grid
        grid_scroll = ScrollView()
        self.card_grid = GridLayout(
            cols=3,
            spacing=dp(12),
            padding=[dp(16), dp(12)],
            size_hint_y=None,
            row_default_height=dp(140)
        )
        self.card_grid.bind(minimum_height=self.card_grid.setter('height'))
        grid_scroll.add_widget(self.card_grid)
        self.content.add_widget(grid_scroll)

    def on_enter(self):
        super().on_enter()
        app = App.get_running_app()
        deck_id = getattr(app, 'selected_deck_id', None)

        if deck_id and deck_id in META_DECKS:
            self.current_deck = META_DECKS[deck_id]
            self.refresh_display()

    def switch_tab(self, tab_id):
        self.current_tab = tab_id

        if tab_id == 'list':
            self.list_tab.color = get_color_from_hex(COLORS['primary'])
            self.compare_tab.color = get_color_from_hex(COLORS['text_muted'])
        else:
            self.list_tab.color = get_color_from_hex(COLORS['text_muted'])
            self.compare_tab.color = get_color_from_hex(COLORS['primary'])

        self.refresh_display()

    def refresh_display(self):
        if not self.current_deck:
            return

        deck = self.current_deck
        lang = App.get_running_app().current_language

        self.title_label.text = f'[b]{deck.get_name(lang)}[/b]'
        self.strategy_text.text = deck.get_strategy(lang)

        self.card_grid.clear_widgets()

        if self.current_tab == 'list':
            self.show_card_list()
        else:
            self.show_comparison()

    def show_card_list(self):
        """Show deck card images."""
        deck_info = get_deck_info(self.current_deck.id)

        # Add main card
        if deck_info.get('card_url'):
            card_widget = self._create_card_widget(deck_info['card_url'], self.current_deck.get_name(App.get_running_app().current_language))
            self.card_grid.add_widget(card_widget)

        # Add icon-based cards
        if deck_info.get('icon_url'):
            card_widget = self._create_card_widget(deck_info['icon_url'], 'Key Pokemon')
            self.card_grid.add_widget(card_widget)

        # Add placeholder cards
        for i in range(7):
            placeholder = self._create_placeholder_card(f'Card {i+3}')
            self.card_grid.add_widget(placeholder)

    def show_comparison(self):
        """Show matchup comparison."""
        lang = App.get_running_app().current_language
        matchups = get_deck_matchups(self.current_deck.id)

        for opp_id, win_rate, notes in matchups[:6]:
            opp_deck = META_DECKS.get(opp_id)
            if opp_deck:
                opp_info = get_deck_info(opp_id)
                card_widget = self._create_matchup_card(opp_deck.get_name(lang), win_rate, opp_info.get('icon_url', ''))
                self.card_grid.add_widget(card_widget)

    def _create_card_widget(self, image_url, label):
        """Create a card image widget."""
        box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(140))

        img = AsyncImage(
            source=image_url,
            allow_stretch=True,
            keep_ratio=True,
            size_hint_y=0.85
        )
        box.add_widget(img)

        lbl = Label(
            text=label,
            font_size=sp(10),
            color=get_color_from_hex(COLORS['text_secondary']),
            size_hint_y=0.15,
            halign='center'
        )
        box.add_widget(lbl)

        return box

    def _create_placeholder_card(self, label):
        """Create a placeholder card."""
        box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(140))

        placeholder = PlaceholderCard(size_hint_y=0.85)
        box.add_widget(placeholder)

        lbl = Label(
            text=label,
            font_size=sp(10),
            color=get_color_from_hex(COLORS['text_secondary']),
            size_hint_y=0.15,
            halign='center'
        )
        box.add_widget(lbl)

        return box

    def _create_matchup_card(self, name, win_rate, icon_url):
        """Create a matchup info card."""
        box = CardBox(orientation='vertical', size_hint_y=None, height=dp(140), padding=[dp(8), dp(4)])

        if icon_url:
            img = AsyncImage(
                source=icon_url,
                allow_stretch=True,
                keep_ratio=True,
                size_hint_y=0.6
            )
            box.add_widget(img)
        else:
            box.add_widget(Widget(size_hint_y=0.6))

        name_lbl = Label(
            text=name[:15] + '...' if len(name) > 15 else name,
            font_size=sp(10),
            color=get_color_from_hex(COLORS['text']),
            size_hint_y=0.2,
            halign='center'
        )
        box.add_widget(name_lbl)

        # Win rate with color
        rate_color = COLORS['success'] if win_rate >= 55 else (COLORS['danger'] if win_rate <= 45 else COLORS['warning'])
        rate_lbl = Label(
            text=f'{win_rate:.0f}%',
            font_size=sp(14),
            color=get_color_from_hex(rate_color),
            bold=True,
            size_hint_y=0.2,
            halign='center'
        )
        box.add_widget(rate_lbl)

        return box


# =============================================================================
# CARD SEARCH & ADD SCREEN
# =============================================================================

class CardSearchScreen(BaseScreen):
    """Card search interface."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        # Header
        header = ColoredBox(
            orientation='vertical',
            bg_color=COLORS['surface'],
            size_hint_y=None,
            height=dp(50),
            padding=[dp(16), dp(12)]
        )

        title = Label(
            text='[b]Card Search & Add[/b]',
            markup=True,
            font_size=sp(18),
            color=get_color_from_hex(COLORS['text']),
            halign='left'
        )
        title.bind(size=title.setter('text_size'))
        header.add_widget(title)
        self.content.add_widget(header)

        # Search form
        form_box = ColoredBox(
            orientation='vertical',
            bg_color=COLORS['surface'],
            size_hint_y=None,
            height=dp(160),
            padding=[dp(16), dp(12)],
            spacing=dp(12)
        )

        # Search input
        search_row = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(8))
        search_label = Label(
            text='Search:',
            font_size=sp(13),
            color=get_color_from_hex(COLORS['text']),
            size_hint_x=None,
            width=dp(60),
            halign='left'
        )
        search_label.bind(size=search_label.setter('text_size'))

        self.search_input = TextInput(
            hint_text='Search for cards...',
            multiline=False,
            font_size=sp(13),
            background_color=get_color_from_hex(COLORS['surface_light']),
            foreground_color=get_color_from_hex(COLORS['text']),
            padding=[dp(8), dp(6)]
        )
        search_row.add_widget(search_label)
        search_row.add_widget(self.search_input)
        form_box.add_widget(search_row)

        # Card type dropdown
        type_row = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(8))
        type_label = Label(
            text='AP / Card:',
            font_size=sp(13),
            color=get_color_from_hex(COLORS['text']),
            size_hint_x=None,
            width=dp(60),
            halign='left'
        )
        type_label.bind(size=type_label.setter('text_size'))

        type_spinner = Spinner(
            text='All Types',
            values=['All Types', 'Pokemon', 'Trainer', 'Energy'],
            font_size=sp(12),
            background_normal='',
            background_color=get_color_from_hex(COLORS['surface_light']),
            color=get_color_from_hex(COLORS['text'])
        )
        type_row.add_widget(type_label)
        type_row.add_widget(type_spinner)
        form_box.add_widget(type_row)

        # Set dropdown
        set_row = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(8))
        set_label = Label(
            text='All Sets:',
            font_size=sp(13),
            color=get_color_from_hex(COLORS['text']),
            size_hint_x=None,
            width=dp(60),
            halign='left'
        )
        set_label.bind(size=set_label.setter('text_size'))

        set_spinner = Spinner(
            text='All Sets',
            values=['All Sets', 'SVI', 'PAL', 'OBF', 'MEW', 'PAR', 'TEF', 'TWM', 'SFA', 'SCR'],
            font_size=sp(12),
            background_normal='',
            background_color=get_color_from_hex(COLORS['surface_light']),
            color=get_color_from_hex(COLORS['text'])
        )
        set_row.add_widget(set_label)
        set_row.add_widget(set_spinner)
        form_box.add_widget(set_row)

        self.content.add_widget(form_box)

        # Spacer
        self.content.add_widget(Widget(size_hint_y=0.3))

        # Card results - horizontal scroll
        results_label = Label(
            text='  Results:',
            font_size=sp(13),
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            size_hint_y=None,
            height=dp(30)
        )
        results_label.bind(size=results_label.setter('text_size'))
        self.content.add_widget(results_label)

        results_scroll = ScrollView(
            size_hint_y=None,
            height=dp(160),
            do_scroll_y=False
        )
        results_grid = BoxLayout(
            orientation='horizontal',
            size_hint=(None, 1),
            spacing=dp(12),
            padding=[dp(16), dp(8)]
        )
        results_grid.bind(minimum_width=results_grid.setter('width'))

        # Sample card images from meta decks
        for deck_id, info in list(DECK_INFO.items())[:6]:
            card_box = BoxLayout(
                orientation='vertical',
                size_hint=(None, 1),
                width=dp(100)
            )

            img = AsyncImage(
                source=info.get('card_url', ''),
                allow_stretch=True,
                keep_ratio=True,
                size_hint_y=0.85
            )
            card_box.add_widget(img)

            add_btn = PrimaryButton(
                text='Add',
                size_hint=(1, 0.15),
                font_size=sp(10)
            )
            card_box.add_widget(add_btn)

            results_grid.add_widget(card_box)

        results_scroll.add_widget(results_grid)
        self.content.add_widget(results_scroll)


# =============================================================================
# SAVED DECKS SCREEN
# =============================================================================

class SavedDecksScreen(BaseScreen):
    """List of user's saved decks."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        # Header
        header = ColoredBox(
            orientation='vertical',
            bg_color=COLORS['surface'],
            size_hint_y=None,
            height=dp(50),
            padding=[dp(16), dp(12)]
        )

        title = Label(
            text='[b]Saved Decks[/b]',
            markup=True,
            font_size=sp(18),
            color=get_color_from_hex(COLORS['text']),
            halign='left'
        )
        title.bind(size=title.setter('text_size'))
        header.add_widget(title)
        self.content.add_widget(header)

        # Deck list
        scroll = ScrollView()
        deck_list = GridLayout(
            cols=1,
            spacing=dp(8),
            padding=[dp(16), dp(12)],
            size_hint_y=None
        )
        deck_list.bind(minimum_height=deck_list.setter('height'))

        # Sample saved decks
        sample_decks = [
            ('My First Deck', 'A basic deck for beginners'),
            ('Fire Theme', 'Fire-type focused deck'),
            ('Water Wall', 'Defensive water deck'),
            ('Electric Storm', 'Fast lightning attacks'),
            ('Grass Growth', 'Energy acceleration deck'),
        ]

        for name, desc in sample_decks:
            item = CardBox(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(70),
                padding=[dp(12), dp(8)],
                spacing=dp(12)
            )

            info = BoxLayout(orientation='vertical')
            name_label = Label(
                text=f'[b]{name}[/b]',
                markup=True,
                font_size=sp(14),
                color=get_color_from_hex(COLORS['text']),
                halign='left',
                size_hint_y=0.5
            )
            name_label.bind(size=name_label.setter('text_size'))

            desc_label = Label(
                text=desc,
                font_size=sp(11),
                color=get_color_from_hex(COLORS['text_secondary']),
                halign='left',
                size_hint_y=0.5
            )
            desc_label.bind(size=desc_label.setter('text_size'))

            info.add_widget(name_label)
            info.add_widget(desc_label)
            item.add_widget(info)

            edit_btn = SecondaryButton(
                text='Edit',
                size_hint=(None, None),
                size=(dp(50), dp(32))
            )
            btn_box = AnchorLayout(size_hint_x=None, width=dp(60))
            btn_box.add_widget(edit_btn)
            item.add_widget(btn_box)

            deck_list.add_widget(item)

        scroll.add_widget(deck_list)
        self.content.add_widget(scroll)


# =============================================================================
# DECK COMPARISON SCREEN
# =============================================================================

class DeckComparisonScreen(BaseScreen):
    """Side-by-side deck comparison."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        # Header
        header = ColoredBox(
            orientation='vertical',
            bg_color=COLORS['surface'],
            size_hint_y=None,
            height=dp(50),
            padding=[dp(16), dp(12)]
        )

        title = Label(
            text='[b]Deck Comparison[/b]',
            markup=True,
            font_size=sp(18),
            color=get_color_from_hex(COLORS['text']),
            halign='left'
        )
        title.bind(size=title.setter('text_size'))
        header.add_widget(title)
        self.content.add_widget(header)

        # Selection row
        select_row = BoxLayout(
            size_hint_y=None,
            height=dp(60),
            padding=[dp(16), dp(8)],
            spacing=dp(8)
        )

        select_label = Label(
            text='Select Decks:',
            font_size=sp(13),
            color=get_color_from_hex(COLORS['text']),
            size_hint_x=None,
            width=dp(80),
            halign='left'
        )
        select_label.bind(size=select_label.setter('text_size'))
        select_row.add_widget(select_label)

        decks = get_all_decks()
        deck_names = ['Select...'] + [d.name_en for d in decks[:8]]

        self.deck_a_spinner = Spinner(
            text='My Favorite Deck',
            values=deck_names,
            font_size=sp(11),
            background_normal='',
            background_color=get_color_from_hex(COLORS['surface_light']),
            color=get_color_from_hex(COLORS['text'])
        )

        self.deck_b_spinner = Spinner(
            text='Meta Deck B',
            values=deck_names,
            font_size=sp(11),
            background_normal='',
            background_color=get_color_from_hex(COLORS['surface_light']),
            color=get_color_from_hex(COLORS['text'])
        )

        select_row.add_widget(self.deck_a_spinner)
        select_row.add_widget(self.deck_b_spinner)
        self.content.add_widget(select_row)

        # Comparison area
        compare_scroll = ScrollView()
        compare_box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(500),
            padding=[dp(16), dp(8)],
            spacing=dp(16)
        )

        # Deck A column
        deck_a_col = self._create_deck_column('My Favorite Deck', 'meta_deck_a')
        compare_box.add_widget(deck_a_col)

        # Deck B column
        deck_b_col = self._create_deck_column('Meta Deck B', 'meta_deck_b')
        compare_box.add_widget(deck_b_col)

        compare_scroll.add_widget(compare_box)
        self.content.add_widget(compare_scroll)

    def _create_deck_column(self, title, deck_key):
        """Create a deck column for comparison."""
        col = CardBox(
            orientation='vertical',
            padding=[dp(8), dp(8)],
            spacing=dp(8)
        )

        # Title
        title_label = Label(
            text=f'[b]{title}[/b]',
            markup=True,
            font_size=sp(13),
            color=get_color_from_hex(COLORS['text']),
            halign='center',
            size_hint_y=None,
            height=dp(30)
        )
        col.add_widget(title_label)

        # Stats
        stats = [
            ('Pokemon:', '18'),
            ('Trainer:', '30'),
            ('Energy:', '12'),
        ]

        for stat_name, stat_val in stats:
            stat_row = BoxLayout(size_hint_y=None, height=dp(24))
            name_lbl = Label(
                text=stat_name,
                font_size=sp(11),
                color=get_color_from_hex(COLORS['text_secondary']),
                halign='left',
                size_hint_x=0.6
            )
            name_lbl.bind(size=name_lbl.setter('text_size'))

            val_lbl = Label(
                text=stat_val,
                font_size=sp(11),
                color=get_color_from_hex(COLORS['text']),
                halign='right',
                size_hint_x=0.4
            )
            val_lbl.bind(size=val_lbl.setter('text_size'))

            stat_row.add_widget(name_lbl)
            stat_row.add_widget(val_lbl)
            col.add_widget(stat_row)

        # Key cards label
        key_label = Label(
            text='Key Cards:',
            font_size=sp(11),
            color=get_color_from_hex(COLORS['text_secondary']),
            halign='left',
            size_hint_y=None,
            height=dp(24)
        )
        key_label.bind(size=key_label.setter('text_size'))
        col.add_widget(key_label)

        # Card grid
        card_grid = GridLayout(
            cols=2,
            spacing=dp(4),
            size_hint_y=None,
            height=dp(200)
        )

        for _ in range(4):
            placeholder = PlaceholderCard(size_hint=(1, None), height=dp(90))
            card_grid.add_widget(placeholder)

        col.add_widget(card_grid)

        return col


# =============================================================================
# BATTLE SEQUENCE SUGGESTION SCREEN
# =============================================================================

class BattleSequenceScreen(BaseScreen):
    """Battle sequence suggestion interface."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        # Header
        header = ColoredBox(
            orientation='vertical',
            bg_color=COLORS['surface'],
            size_hint_y=None,
            height=dp(50),
            padding=[dp(16), dp(12)]
        )

        title = Label(
            text='[b]Battle Sequence Suggestion[/b]',
            markup=True,
            font_size=sp(18),
            color=get_color_from_hex(COLORS['text']),
            halign='left'
        )
        title.bind(size=title.setter('text_size'))
        header.add_widget(title)
        self.content.add_widget(header)

        # Form section
        form_box = ColoredBox(
            orientation='vertical',
            bg_color=COLORS['surface'],
            size_hint_y=None,
            height=dp(120),
            padding=[dp(16), dp(12)],
            spacing=dp(12)
        )

        # Deck selection
        deck_row = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(8))
        deck_label = Label(
            text='Select Deck:',
            font_size=sp(13),
            color=get_color_from_hex(COLORS['text']),
            size_hint_x=None,
            width=dp(80),
            halign='left'
        )
        deck_label.bind(size=deck_label.setter('text_size'))

        decks = get_all_decks()
        deck_names = ['Select your deck...'] + [d.name_en for d in decks[:8]]

        deck_spinner = Spinner(
            text='Your Favorite Deck',
            values=deck_names,
            font_size=sp(12),
            background_normal='',
            background_color=get_color_from_hex(COLORS['surface_light']),
            color=get_color_from_hex(COLORS['text'])
        )

        deck_row.add_widget(deck_label)
        deck_row.add_widget(deck_spinner)
        form_box.add_widget(deck_row)

        # Info text
        info_label = Label(
            text='Enter opponent info below (e.g. "Retaliat / PTCGL 12 Energy Based+")',
            font_size=sp(11),
            color=get_color_from_hex(COLORS['text_muted']),
            halign='left',
            size_hint_y=None,
            height=dp(24)
        )
        info_label.bind(size=info_label.setter('text_size'))
        form_box.add_widget(info_label)

        # Get suggestions button
        suggest_btn = PrimaryButton(
            text='Get Suggestions',
            size_hint_y=None,
            height=dp(40)
        )
        form_box.add_widget(suggest_btn)

        self.content.add_widget(form_box)

        # Results section
        results_box = ColoredBox(
            orientation='vertical',
            bg_color=COLORS['surface'],
            size_hint_y=None,
            height=dp(50),
            padding=[dp(16), dp(8)]
        )

        results_title = Label(
            text='[b]Suggested Play Sequence[/b]',
            markup=True,
            font_size=sp(14),
            color=get_color_from_hex(COLORS['text']),
            halign='left'
        )
        results_title.bind(size=results_title.setter('text_size'))
        results_box.add_widget(results_title)
        self.content.add_widget(results_box)

        # Sequence cards
        sequence_scroll = ScrollView()
        sequence_list = GridLayout(
            cols=1,
            spacing=dp(8),
            padding=[dp(16), dp(8)],
            size_hint_y=None
        )
        sequence_list.bind(minimum_height=sequence_list.setter('height'))

        # Sample sequence
        sequence_items = [
            ('Turn 1', 'Set up Pidgey > Evolve Basic'),
            ('Turn 2', 'Attach energy > Use supporter'),
            ('Turn 3', 'Evolve to Stage 2 > Attack'),
            ('Turn 4', 'Boss\'s Orders > KO threat'),
        ]

        for turn, action in sequence_items:
            item = CardBox(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(60),
                padding=[dp(8), dp(8)],
                spacing=dp(8)
            )

            # Card placeholder
            card_placeholder = PlaceholderCard(size_hint=(None, 1), width=dp(40))
            item.add_widget(card_placeholder)

            # Action text
            action_box = BoxLayout(orientation='vertical')
            turn_label = Label(
                text=f'[b]{turn}[/b]',
                markup=True,
                font_size=sp(12),
                color=get_color_from_hex(COLORS['text']),
                halign='left',
                size_hint_y=0.4
            )
            turn_label.bind(size=turn_label.setter('text_size'))

            action_label = Label(
                text=action,
                font_size=sp(11),
                color=get_color_from_hex(COLORS['text_secondary']),
                halign='left',
                size_hint_y=0.6
            )
            action_label.bind(size=action_label.setter('text_size'))

            action_box.add_widget(turn_label)
            action_box.add_widget(action_label)
            item.add_widget(action_box)

            sequence_list.add_widget(item)

        sequence_scroll.add_widget(sequence_list)
        self.content.add_widget(sequence_scroll)


# =============================================================================
# SETTINGS SCREEN
# =============================================================================

class SettingsScreen(BaseScreen):
    """App settings with toggles - responsive for Samsung Fold 6."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def _on_screen_mode_change(self, instance, mode):
        """Rebuild UI when screen mode changes."""
        self.content.clear_widgets()
        self.build_ui()

    def build_ui(self):
        font_scale = self.responsive.font_scale
        is_cover = self.is_cover_mode

        # Header
        header_height = dp(64) if not is_cover else dp(56)
        header = ColoredBox(
            orientation='vertical',
            bg_color=COLORS['surface'],
            size_hint_y=None,
            height=header_height,
            padding=[dp(16), dp(14)]
        )

        title = Label(
            text='[b]Settings[/b]',
            markup=True,
            font_size=sp(20 * font_scale),
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        header.add_widget(title)
        self.content.add_widget(header)

        # Settings list in scrollview
        scroll = ScrollView()
        settings_box = ColoredBox(
            orientation='vertical',
            bg_color=COLORS['surface'],
            padding=[dp(16), dp(14)],
            spacing=dp(12),
            size_hint_y=None
        )
        settings_box.bind(minimum_height=settings_box.setter('height'))

        # Toggle settings - larger touch targets
        toggle_settings = [
            ('Push Notifications', 'Receive game updates'),
            ('Dark Mode', 'Enable dark theme'),
            ('Sync Data', 'Sync across devices'),
        ]

        row_height = self.responsive.list_item_height

        for name, desc in toggle_settings:
            row = BoxLayout(
                size_hint_y=None,
                height=row_height,
                spacing=dp(12)
            )

            info = BoxLayout(orientation='vertical', size_hint_x=0.7)
            name_label = Label(
                text=name,
                font_size=sp(16 * font_scale),
                color=get_color_from_hex(COLORS['text']),
                halign='left',
                valign='middle',
                size_hint_y=0.5
            )
            name_label.bind(size=name_label.setter('text_size'))

            desc_label = Label(
                text=desc,
                font_size=sp(13 * font_scale),
                color=get_color_from_hex(COLORS['text_secondary']),
                halign='left',
                valign='middle',
                size_hint_y=0.5
            )
            desc_label.bind(size=desc_label.setter('text_size'))

            info.add_widget(name_label)
            info.add_widget(desc_label)
            row.add_widget(info)

            # Toggle switch - ensure good touch target
            switch_box = AnchorLayout(size_hint_x=0.3)
            switch = Switch(active=False)
            switch_box.add_widget(switch)
            row.add_widget(switch_box)

            settings_box.add_widget(row)

            # Divider
            divider = Widget(size_hint_y=None, height=dp(1))
            with divider.canvas:
                Color(*get_color_from_hex(COLORS['divider']))
                divider._rect = Rectangle(pos=divider.pos, size=divider.size)
            divider.bind(pos=lambda w, p: setattr(w._rect, 'pos', p) if hasattr(w, '_rect') else None)
            divider.bind(size=lambda w, s: setattr(w._rect, 'size', s) if hasattr(w, '_rect') else None)
            settings_box.add_widget(divider)

        # Language dropdown - larger
        lang_row = BoxLayout(size_hint_y=None, height=row_height, spacing=dp(12))
        lang_label = Label(
            text='Language',
            font_size=sp(16 * font_scale),
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            valign='middle',
            size_hint_x=0.5
        )
        lang_label.bind(size=lang_label.setter('text_size'))

        lang_spinner = Spinner(
            text='English',
            values=['English', 'Portuguese'],
            font_size=sp(15 * font_scale),
            background_normal='',
            background_color=get_color_from_hex(COLORS['surface_light']),
            color=get_color_from_hex(COLORS['text']),
            size_hint_x=0.5
        )
        lang_spinner.bind(text=self.on_language_change)

        lang_row.add_widget(lang_label)
        lang_row.add_widget(lang_spinner)
        settings_box.add_widget(lang_row)

        # Spacer before buttons
        settings_box.add_widget(Widget(size_hint_y=None, height=dp(20)))

        # About button - larger
        btn_height = self.responsive.button_height
        about_btn = SecondaryButton(
            text='About',
            size_hint_y=None,
            height=btn_height
        )
        settings_box.add_widget(about_btn)

        # Spacer
        settings_box.add_widget(Widget(size_hint_y=None, height=dp(12)))

        # Privacy policy
        privacy_btn = OutlineButton(
            text='Privacy Policy',
            size_hint_y=None,
            height=btn_height
        )
        settings_box.add_widget(privacy_btn)

        scroll.add_widget(settings_box)
        self.content.add_widget(scroll)

    def on_language_change(self, spinner, text):
        app = App.get_running_app()
        if text == 'English':
            app.current_language = Language.EN
        else:
            app.current_language = Language.PT


# =============================================================================
# PROFILE SCREEN
# =============================================================================

class ProfileScreen(BaseScreen):
    """User profile screen."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        # Header
        header = ColoredBox(
            orientation='vertical',
            bg_color=COLORS['surface'],
            size_hint_y=None,
            height=dp(50),
            padding=[dp(16), dp(12)]
        )

        title = Label(
            text='[b]Profile[/b]',
            markup=True,
            font_size=sp(18),
            color=get_color_from_hex(COLORS['text']),
            halign='left'
        )
        title.bind(size=title.setter('text_size'))
        header.add_widget(title)
        self.content.add_widget(header)

        # Profile info
        profile_box = ColoredBox(
            orientation='vertical',
            bg_color=COLORS['surface'],
            padding=[dp(16), dp(16)],
            spacing=dp(12)
        )

        # Avatar placeholder
        avatar_box = AnchorLayout(size_hint_y=None, height=dp(100))
        avatar = BoxLayout(size_hint=(None, None), size=(dp(80), dp(80)))
        with avatar.canvas.before:
            Color(*get_color_from_hex(COLORS['border']))
            avatar._ellipse = Ellipse(pos=avatar.pos, size=avatar.size)
        avatar.bind(pos=lambda w, p: setattr(w._ellipse, 'pos', p) if hasattr(w, '_ellipse') else None)
        avatar.bind(size=lambda w, s: setattr(w._ellipse, 'size', s) if hasattr(w, '_ellipse') else None)

        avatar_label = Label(
            text='JD',
            font_size=sp(24),
            color=get_color_from_hex(COLORS['text_muted']),
            bold=True
        )
        avatar.add_widget(avatar_label)
        avatar_box.add_widget(avatar)
        profile_box.add_widget(avatar_box)

        # User info fields
        info_fields = [
            ('Name:', 'John Doe'),
            ('Username:', 'johndoe'),
            ('Email:', 'johndoe@example.com'),
        ]

        for label_text, value in info_fields:
            row = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(8))

            label = Label(
                text=label_text,
                font_size=sp(13),
                color=get_color_from_hex(COLORS['text_secondary']),
                halign='left',
                size_hint_x=0.3
            )
            label.bind(size=label.setter('text_size'))

            value_label = Label(
                text=value,
                font_size=sp(13),
                color=get_color_from_hex(COLORS['text']),
                halign='left',
                size_hint_x=0.7
            )
            value_label.bind(size=value_label.setter('text_size'))

            row.add_widget(label)
            row.add_widget(value_label)
            profile_box.add_widget(row)

        # Stats section
        stats_label = Label(
            text='[b]Stats[/b]',
            markup=True,
            font_size=sp(14),
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            size_hint_y=None,
            height=dp(30)
        )
        stats_label.bind(size=stats_label.setter('text_size'))
        profile_box.add_widget(stats_label)

        stats_row = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(8))

        stats_items = [
            ('Decks', '5'),
            ('Matches', '42'),
            ('Win Rate', '68%'),
        ]

        for stat_name, stat_val in stats_items:
            stat_box = CardBox(
                orientation='vertical',
                padding=[dp(8), dp(4)]
            )

            val_label = Label(
                text=f'[b]{stat_val}[/b]',
                markup=True,
                font_size=sp(18),
                color=get_color_from_hex(COLORS['primary']),
                halign='center',
                size_hint_y=0.6
            )

            name_label = Label(
                text=stat_name,
                font_size=sp(10),
                color=get_color_from_hex(COLORS['text_secondary']),
                halign='center',
                size_hint_y=0.4
            )

            stat_box.add_widget(val_label)
            stat_box.add_widget(name_label)
            stats_row.add_widget(stat_box)

        profile_box.add_widget(stats_row)

        # Sign in buttons
        profile_box.add_widget(Widget(size_hint_y=0.2))  # Spacer

        google_btn = PrimaryButton(
            text='Sign in with Google',
            size_hint_y=None,
            height=dp(44)
        )
        profile_box.add_widget(google_btn)

        apple_btn = Button(
            text='Sign in with Apple',
            size_hint_y=None,
            height=dp(44),
            background_normal='',
            background_color=get_color_from_hex('#000000'),
            color=get_color_from_hex('#ffffff'),
            font_size=sp(14),
            bold=True
        )
        profile_box.add_widget(apple_btn)

        # Support link
        support_btn = OutlineButton(
            text='Support',
            size_hint_y=None,
            height=dp(36),
            border_color=COLORS['text_secondary']
        )
        profile_box.add_widget(support_btn)

        self.content.add_widget(profile_box)


# =============================================================================
# SECOND ROW NAVIGATION (Extended tabs)
# =============================================================================

class ExtendedNavBar(ColoredBox):
    """Second row of navigation tabs."""

    def __init__(self, **kwargs):
        super().__init__(bg_color=COLORS['nav_bg'], **kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(40)
        self.spacing = dp(2)
        self.padding = [dp(4), dp(4)]

        tab_items = [
            ('My Decks', 'my_decks'),
            ('Import', 'import'),
            ('Compare', 'comparison'),
            ('Settings', 'settings'),
            ('Profile', 'profile'),
        ]

        for text, screen_id in tab_items:
            btn = Button(
                text=text,
                font_size=sp(10),
                background_normal='',
                background_down='',
                background_color=(1, 1, 1, 0.2),
                color=get_color_from_hex(COLORS['nav_text']),
                size_hint_x=1
            )
            btn.screen_id = screen_id
            btn.bind(on_press=self.on_tab_press)
            self.add_widget(btn)

    def on_tab_press(self, btn):
        app = App.get_running_app()
        if app.root:
            app.root.current = btn.screen_id


# =============================================================================
# MAIN APP
# =============================================================================

class TCGMetaApp(App):
    """Pokemon TCG Meta Analyzer App."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_language = Language.EN
        self.selected_deck_id = None

    def build(self):
        self.title = 'Pokemon TCG App'

        # Set window background
        Window.clearcolor = get_color_from_hex(COLORS['background'])

        # Screen manager
        sm = ScreenManager(transition=NoTransition())

        # Add all screens
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(MetaDecksScreen(name='meta'))
        sm.add_widget(DeckBuilderScreen(name='deck_builder'))
        sm.add_widget(DeckDetailsScreen(name='details'))
        sm.add_widget(CardSearchScreen(name='card_search'))
        sm.add_widget(SavedDecksScreen(name='saved_decks'))
        sm.add_widget(DeckComparisonScreen(name='comparison'))
        sm.add_widget(BattleSequenceScreen(name='battle_sequence'))
        sm.add_widget(SettingsScreen(name='settings'))
        sm.add_widget(ProfileScreen(name='profile'))
        # New v2.0 screens
        sm.add_widget(ImportScreen(name='import'))
        sm.add_widget(MyDecksScreen(name='my_decks'))
        sm.add_widget(DeckEditorScreen(name='deck_editor'))
        sm.add_widget(ComparisonScreen(name='compare'))
        sm.add_widget(NewsScreen(name='news'))
        sm.add_widget(CalendarScreen(name='calendar'))
        sm.add_widget(MatchAnalysisScreen(name='match_analysis'))

        return sm


if __name__ == '__main__':
    TCGMetaApp().run()
