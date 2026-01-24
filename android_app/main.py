"""
TCG Meta Analyzer - Beautiful Pokemon TCG App
Stunning visual design with card images and deck icons
Optimized for Samsung Z Fold and other foldable devices
"""
import sys
import os

# Add the script's directory to path for imports to work from any location
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, FadeTransition
from kivy.uix.widget import Widget
from kivy.uix.image import AsyncImage
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex, platform
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line, Ellipse
from kivy.graphics.texture import Texture
from kivy.clock import Clock

# Only set window size on desktop (not Android)
if platform not in ('android', 'ios'):
    Window.size = (420, 900)

# Import meta database
from meta_data import (
    META_DECKS, MATCHUPS, Language,
    get_matchup, get_deck_matchups, get_all_decks,
    get_translation, get_difficulty_translation
)

# Modern color scheme - Dark theme with vibrant accents
COLORS = {
    'background': '#0d1117',
    'surface': '#161b22',
    'surface_light': '#21262d',
    'card': '#1c2128',
    'card_hover': '#252c35',
    'primary': '#f85149',
    'primary_light': '#ff7b72',
    'secondary': '#58a6ff',
    'secondary_light': '#79c0ff',
    'accent': '#7c3aed',
    'accent_light': '#a78bfa',
    'success': '#3fb950',
    'success_light': '#56d364',
    'warning': '#d29922',
    'warning_light': '#e3b341',
    'danger': '#f85149',
    'text': '#f0f6fc',
    'text_secondary': '#8b949e',
    'text_muted': '#6e7681',
    'border': '#30363d',
    'tier1': '#3fb950',
    'tier2': '#d29922',
    'tier3': '#8b949e',
    'gold': '#ffd700',
    'silver': '#c0c0c0',
    'bronze': '#cd7f32',
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
    'fairy': '#ec8fe6',
}

# Deck data with icons, card images and type info
# Pokemon sprites from PokemonDB (https://pokemondb.net/sprites)
# Using HOME sprites for Gen 1-8 and Scarlet-Violet sprites for Gen 9
DECK_INFO = {
    'gholdengo': {
        'name': 'Gholdengo ex',
        'icon_url': 'https://img.pokemondb.net/sprites/scarlet-violet/normal/gholdengo.png',
        'card_url': 'https://images.pokemontcg.io/sv4/139_hires.png',
        'secondary_cards': [
            'https://images.pokemontcg.io/sv4/138_hires.png',  # Gimmighoul
            'https://images.pokemontcg.io/sv3pt5/148_hires.png',  # Superior Energy
        ],
        'type': 'metal',
        'type_icon': 'Metal',
    },
    'dragapult': {
        'name': 'Dragapult ex',
        'icon_url': 'https://img.pokemondb.net/sprites/home/normal/dragapult.png',
        'card_url': 'https://images.pokemontcg.io/sv6/130_hires.png',
        'secondary_cards': [
            'https://images.pokemontcg.io/sv6/129_hires.png',  # Drakloak
            'https://images.pokemontcg.io/sv6/89_hires.png',  # Dreepy
        ],
        'type': 'psychic',
        'type_icon': 'Psychic',
    },
    'gardevoir': {
        'name': 'Gardevoir ex',
        'icon_url': 'https://img.pokemondb.net/sprites/home/normal/gardevoir.png',
        'card_url': 'https://images.pokemontcg.io/sv1/86_hires.png',
        'secondary_cards': [
            'https://images.pokemontcg.io/sv1/85_hires.png',  # Kirlia
            'https://images.pokemontcg.io/sv1/245_hires.png',  # Gardevoir ex SAR
        ],
        'type': 'psychic',
        'type_icon': 'Psychic',
    },
    'charizard': {
        'name': 'Charizard ex',
        'icon_url': 'https://img.pokemondb.net/sprites/home/normal/charizard.png',
        'card_url': 'https://images.pokemontcg.io/sv3/125_hires.png',
        'secondary_cards': [
            'https://images.pokemontcg.io/sv3/124_hires.png',  # Charmeleon
            'https://images.pokemontcg.io/sv3pt5/199_hires.png',  # Pidgeot
        ],
        'type': 'fire',
        'type_icon': 'Fire',
    },
    'raging_bolt': {
        'name': 'Raging Bolt ex',
        'icon_url': 'https://img.pokemondb.net/sprites/scarlet-violet/normal/raging-bolt.png',
        'card_url': 'https://images.pokemontcg.io/sv5/123_hires.png',
        'secondary_cards': [
            'https://images.pokemontcg.io/sv5/64_hires.png',  # Ogerpon
        ],
        'type': 'lightning',
        'type_icon': 'Lightning',
    },
    'grimmsnarl': {
        'name': "Marnie's Grimmsnarl",
        'icon_url': 'https://img.pokemondb.net/sprites/home/normal/grimmsnarl.png',
        'card_url': 'https://images.pokemontcg.io/sv6pt5/72_hires.png',
        'secondary_cards': [
            'https://images.pokemontcg.io/sv6pt5/41_hires.png',  # Froslass
        ],
        'type': 'darkness',
        'type_icon': 'Darkness',
    },
    'joltik': {
        'name': 'Joltik Box',
        'icon_url': 'https://img.pokemondb.net/sprites/home/normal/galvantula.png',
        'card_url': 'https://images.pokemontcg.io/sv3/63_hires.png',
        'secondary_cards': [
            'https://images.pokemontcg.io/sv3/64_hires.png',  # Galvantula
        ],
        'type': 'lightning',
        'type_icon': 'Lightning',
    },
    'flareon': {
        'name': 'Flareon ex',
        'icon_url': 'https://img.pokemondb.net/sprites/home/normal/flareon.png',
        'card_url': 'https://images.pokemontcg.io/sv7/36_hires.png',
        'secondary_cards': [
            'https://images.pokemontcg.io/sv7/35_hires.png',  # Eevee
        ],
        'type': 'fire',
        'type_icon': 'Fire',
    },
}

def get_deck_info(deck_id):
    """Get deck visual info."""
    return DECK_INFO.get(deck_id, {})

def get_type_color(type_name):
    """Get color for a Pokemon type."""
    return COLORS.get(type_name.lower(), COLORS['secondary'])


class GradientWidget(Widget):
    """Widget with gradient background."""

    def __init__(self, colors=None, direction='vertical', **kwargs):
        super().__init__(**kwargs)
        self.gradient_colors = colors or [COLORS['background'], COLORS['surface']]
        self.direction = direction
        self.bind(pos=self._update, size=self._update)
        Clock.schedule_once(lambda dt: self._update())

    def _update(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # Create gradient effect with multiple rectangles
            num_steps = 20
            for i in range(num_steps):
                t = i / num_steps
                # Interpolate colors
                c1 = get_color_from_hex(self.gradient_colors[0])
                c2 = get_color_from_hex(self.gradient_colors[1])
                r = c1[0] + (c2[0] - c1[0]) * t
                g = c1[1] + (c2[1] - c1[1]) * t
                b = c1[2] + (c2[2] - c1[2]) * t
                Color(r, g, b, 1)

                if self.direction == 'vertical':
                    step_height = self.height / num_steps
                    Rectangle(pos=(self.x, self.y + self.height - (i + 1) * step_height),
                             size=(self.width, step_height + 1))
                else:
                    step_width = self.width / num_steps
                    Rectangle(pos=(self.x + i * step_width, self.y),
                             size=(step_width + 1, self.height))


class ColoredBoxLayout(BoxLayout):
    """BoxLayout with background color support."""

    def __init__(self, bg_color=None, radius=0, border_color=None, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color or COLORS['background']
        self.radius = radius
        self.border_color = border_color
        with self.canvas.before:
            Color(*get_color_from_hex(self.bg_color))
            if radius > 0:
                self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(radius)])
            else:
                self.rect = Rectangle(pos=self.pos, size=self.size)

            if border_color:
                Color(*get_color_from_hex(border_color))
                if radius > 0:
                    self.border = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(radius)), width=1)
                else:
                    self.border = Line(rectangle=(self.x, self.y, self.width, self.height), width=1)
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        if hasattr(self, 'border') and self.border_color:
            if self.radius > 0:
                self.border.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(self.radius))
            else:
                self.border.rectangle = (self.x, self.y, self.width, self.height)


class GlassCard(BoxLayout):
    """Modern glass-morphism style card widget."""

    def __init__(self, bg_color=None, glow_color=None, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color or COLORS['card']
        self.glow_color = glow_color
        self.padding = dp(16)
        self._draw()
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # Glow effect
            if self.glow_color:
                Color(*get_color_from_hex(self.glow_color), 0.15)
                RoundedRectangle(
                    pos=(self.x - dp(2), self.y - dp(2)),
                    size=(self.width + dp(4), self.height + dp(4)),
                    radius=[dp(16)]
                )

            # Main card background
            Color(*get_color_from_hex(self.bg_color))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])

            # Subtle border
            Color(*get_color_from_hex(COLORS['border']), 0.5)
            Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(12)), width=1)


class CardImageWidget(RelativeLayout):
    """Widget for displaying a Pokemon card with styling."""

    def __init__(self, image_url='', **kwargs):
        super().__init__(**kwargs)
        self.image_url = image_url
        self._build()

    def _build(self):
        # Card shadow
        with self.canvas.before:
            Color(0, 0, 0, 0.3)
            RoundedRectangle(
                pos=(dp(4), -dp(4)),
                size=(self.width, self.height),
                radius=[dp(8)]
            )

        # Card image
        self.card_image = AsyncImage(
            source=self.image_url,
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.add_widget(self.card_image)
        self.bind(size=self._update_shadow, pos=self._update_shadow)

    def _update_shadow(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0, 0, 0, 0.3)
            RoundedRectangle(
                pos=(self.x + dp(4), self.y - dp(4)),
                size=self.size,
                radius=[dp(8)]
            )

    def set_source(self, url):
        self.image_url = url
        self.card_image.source = url


class TypeBadge(BoxLayout):
    """Stylish type badge with icon."""

    def __init__(self, type_name='', **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint = (None, None)
        self.height = dp(28)
        self.padding = [dp(10), dp(4)]
        self.spacing = dp(4)

        type_color = get_type_color(type_name)

        with self.canvas.before:
            Color(*get_color_from_hex(type_color), 0.8)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])
        self.bind(pos=self._update, size=self._update)

        self.label = Label(
            text=type_name,
            font_size=sp(12),
            color=get_color_from_hex(COLORS['text']),
            bold=True
        )
        self.add_widget(self.label)
        self.width = len(type_name) * dp(10) + dp(24)

    def _update(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size


class TierBadge(BoxLayout):
    """Tier indicator badge."""

    def __init__(self, tier=1, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(32), dp(32))

        tier_colors = {
            1: COLORS['gold'],
            2: COLORS['silver'],
            3: COLORS['bronze']
        }
        color = tier_colors.get(tier, COLORS['text_muted'])

        with self.canvas.before:
            Color(*get_color_from_hex(COLORS['surface_light']))
            Ellipse(pos=self.pos, size=self.size)
            Color(*get_color_from_hex(color))
            Ellipse(
                pos=(self.x + dp(3), self.y + dp(3)),
                size=(self.width - dp(6), self.height - dp(6))
            )
        self.bind(pos=self._update, size=self._update)

        self.label = Label(
            text=str(tier),
            font_size=sp(14),
            color=get_color_from_hex(COLORS['background']),
            bold=True
        )
        self.add_widget(self.label)

    def _update(self, *args):
        self.canvas.before.clear()
        tier_colors = {1: COLORS['gold'], 2: COLORS['silver'], 3: COLORS['bronze']}
        color = tier_colors.get(int(self.label.text), COLORS['text_muted'])

        with self.canvas.before:
            Color(*get_color_from_hex(COLORS['surface_light']))
            Ellipse(pos=self.pos, size=self.size)
            Color(*get_color_from_hex(color))
            Ellipse(
                pos=(self.x + dp(3), self.y + dp(3)),
                size=(self.width - dp(6), self.height - dp(6))
            )


class StyledButton(Button):
    """Modern styled button with hover effects."""

    def __init__(self, bg_color=None, text_color=None, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.bg_color = bg_color or COLORS['primary']
        self.background_color = get_color_from_hex(self.bg_color)
        self.color = get_color_from_hex(text_color or COLORS['text'])
        self.font_size = sp(15)
        self.bold = True


class IconButton(Button):
    """Circular icon button."""

    def __init__(self, icon_text='', bg_color=None, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        self.text = icon_text
        self.font_size = sp(24)
        self.color = get_color_from_hex(COLORS['text'])
        self.size_hint = (None, None)
        self.size = (dp(44), dp(44))

        self.bg_color = bg_color or COLORS['surface_light']
        with self.canvas.before:
            Color(*get_color_from_hex(self.bg_color))
            self.bg_shape = Ellipse(pos=self.pos, size=self.size)
        self.bind(pos=self._update, size=self._update)

    def _update(self, *args):
        self.bg_shape.pos = self.pos
        self.bg_shape.size = self.size


class HeaderWidget(ColoredBoxLayout):
    """Beautiful header with back navigation and title."""

    def __init__(self, title, show_back=True, on_back=None, subtitle=None, **kwargs):
        super().__init__(bg_color=COLORS['surface'], **kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(70)
        self.padding = [dp(16), dp(12)]
        self.spacing = dp(12)

        if show_back:
            back_btn = IconButton(icon_text='<', bg_color=COLORS['card'])
            if on_back:
                back_btn.bind(on_press=on_back)
            self.add_widget(back_btn)

        # Title area
        title_box = BoxLayout(orientation='vertical')
        title_label = Label(
            text=f'[b]{title}[/b]',
            markup=True,
            font_size=sp(20),
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            size_hint_y=0.6 if subtitle else 1
        )
        title_label.bind(size=title_label.setter('text_size'))
        title_box.add_widget(title_label)

        if subtitle:
            sub_label = Label(
                text=subtitle,
                font_size=sp(13),
                color=get_color_from_hex(COLORS['text_secondary']),
                halign='left',
                size_hint_y=0.4
            )
            sub_label.bind(size=sub_label.setter('text_size'))
            title_box.add_widget(sub_label)

        self.add_widget(title_box)

        if show_back:
            # Spacer to balance the back button
            self.add_widget(Widget(size_hint=(None, 1), width=dp(44)))


class HomeScreen(Screen):
    """Stunning home screen with featured decks."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        # Main container
        main = ColoredBoxLayout(orientation='vertical', bg_color=COLORS['background'])

        # Hero header section
        hero = ColoredBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(220),
            bg_color=COLORS['surface'],
            padding=[dp(24), dp(20)]
        )

        # App branding
        brand_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60))

        # Logo area
        logo_label = Label(
            text='[b][color=#f85149]TCG[/color] Meta[/b]',
            markup=True,
            font_size=sp(32),
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            size_hint_x=0.7
        )
        logo_label.bind(size=logo_label.setter('text_size'))
        brand_box.add_widget(logo_label)

        hero.add_widget(brand_box)

        # Tagline
        tagline = Label(
            text='Pokemon TCG Competitive Meta Browser',
            font_size=sp(14),
            color=get_color_from_hex(COLORS['text_secondary']),
            halign='left',
            size_hint_y=None,
            height=dp(30)
        )
        tagline.bind(size=tagline.setter('text_size'))
        hero.add_widget(tagline)

        # Featured card display - horizontal scroll of top 3 decks
        featured_label = Label(
            text='[b]Featured Decks[/b]',
            markup=True,
            font_size=sp(13),
            color=get_color_from_hex(COLORS['text_muted']),
            halign='left',
            size_hint_y=None,
            height=dp(24)
        )
        featured_label.bind(size=featured_label.setter('text_size'))
        hero.add_widget(featured_label)

        # Featured deck icons
        featured_scroll = ScrollView(
            size_hint_y=None,
            height=dp(80),
            do_scroll_y=False
        )
        featured_box = BoxLayout(
            orientation='horizontal',
            size_hint=(None, 1),
            spacing=dp(12)
        )
        featured_box.bind(minimum_width=featured_box.setter('width'))

        top_decks = list(DECK_INFO.keys())[:5]
        for deck_id in top_decks:
            info = DECK_INFO[deck_id]
            deck_card = self._create_featured_card(deck_id, info)
            featured_box.add_widget(deck_card)

        featured_scroll.add_widget(featured_box)
        hero.add_widget(featured_scroll)

        main.add_widget(hero)

        # Language selector
        lang_container = ColoredBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(56),
            bg_color=COLORS['background'],
            padding=[dp(20), dp(8)],
            spacing=dp(12)
        )

        self.lang_en_btn = StyledButton(
            text='English',
            size_hint_x=0.5,
            bg_color=COLORS['primary']
        )
        self.lang_en_btn.bind(on_press=lambda x: self.set_language(Language.EN))

        self.lang_pt_btn = StyledButton(
            text='Portugues',
            size_hint_x=0.5,
            bg_color=COLORS['card']
        )
        self.lang_pt_btn.bind(on_press=lambda x: self.set_language(Language.PT))

        lang_container.add_widget(self.lang_en_btn)
        lang_container.add_widget(self.lang_pt_btn)
        main.add_widget(lang_container)

        # Menu section
        menu_scroll = ScrollView(size_hint_y=1)
        menu_container = GridLayout(
            cols=1,
            spacing=dp(16),
            padding=[dp(20), dp(16)],
            size_hint_y=None
        )
        menu_container.bind(minimum_height=menu_container.setter('height'))

        # Menu items with icons and descriptions
        menu_items = [
            ('Browse Meta Decks', 'meta', COLORS['success'], 'Explore Top 8 competitive decks with full decklists', '8 Decks'),
            ('Matchup Chart', 'matchups', COLORS['warning'], 'Compare win rates between top meta decks', '28 Matchups'),
            ('Search Pokemon', 'search', COLORS['secondary'], 'Find which decks use your favorite Pokemon', 'All Cards'),
        ]

        for title, screen, color, desc, badge in menu_items:
            card = self._create_menu_card(title, desc, color, badge, screen)
            menu_container.add_widget(card)

        menu_scroll.add_widget(menu_container)
        main.add_widget(menu_scroll)

        # Footer
        footer = ColoredBoxLayout(
            size_hint_y=None,
            height=dp(50),
            bg_color=COLORS['surface'],
            padding=[dp(20), dp(12)]
        )
        footer_text = Label(
            text='[color=#6e7681]January 2026 Meta[/color]  |  [color=#8b949e]Powered by TrainerHill Data[/color]',
            markup=True,
            font_size=sp(12),
            halign='center'
        )
        footer.add_widget(footer_text)
        main.add_widget(footer)

        self.add_widget(main)

    def _create_featured_card(self, deck_id, info):
        """Create a featured deck mini card."""
        card = GlassCard(
            size_hint=(None, 1),
            width=dp(100),
            glow_color=get_type_color(info.get('type', 'colorless'))
        )
        card.padding = dp(8)
        card.orientation = 'vertical'

        # Deck icon image
        icon_img = AsyncImage(
            source=info.get('icon_url', ''),
            allow_stretch=True,
            keep_ratio=True,
            size_hint_y=0.7
        )
        card.add_widget(icon_img)

        # Deck name (short)
        name = info.get('name', deck_id).split()[0]  # First word only
        name_label = Label(
            text=name,
            font_size=sp(11),
            color=get_color_from_hex(COLORS['text']),
            size_hint_y=0.3,
            halign='center'
        )
        card.add_widget(name_label)

        card.deck_id = deck_id
        card.bind(on_touch_down=self._on_featured_touch)

        return card

    def _on_featured_touch(self, card, touch):
        if card.collide_point(*touch.pos):
            if hasattr(card, 'deck_id'):
                app = App.get_running_app()
                app.selected_deck_id = card.deck_id
                self.manager.transition = SlideTransition(direction='left')
                self.manager.current = 'details'
                return True
        return False

    def _create_menu_card(self, title, desc, color, badge, screen):
        """Create a beautiful menu card."""
        card = GlassCard(
            orientation='vertical',
            size_hint_y=None,
            height=dp(110),
            glow_color=color
        )

        # Top row with title and badge
        top_row = BoxLayout(size_hint_y=0.4)

        title_label = Label(
            text=f'[b]{title}[/b]',
            markup=True,
            font_size=sp(18),
            color=get_color_from_hex(color),
            halign='left'
        )
        title_label.bind(size=title_label.setter('text_size'))
        top_row.add_widget(title_label)

        # Badge
        badge_box = BoxLayout(size_hint_x=None, width=dp(80))
        badge_label = Label(
            text=f'[color=#6e7681]{badge}[/color]',
            markup=True,
            font_size=sp(12),
            halign='right'
        )
        badge_label.bind(size=badge_label.setter('text_size'))
        badge_box.add_widget(badge_label)
        top_row.add_widget(badge_box)

        card.add_widget(top_row)

        # Description
        desc_label = Label(
            text=desc,
            font_size=sp(13),
            color=get_color_from_hex(COLORS['text_secondary']),
            halign='left',
            valign='top',
            size_hint_y=0.4
        )
        desc_label.bind(size=desc_label.setter('text_size'))
        card.add_widget(desc_label)

        # Action hint
        action_label = Label(
            text='Tap to explore >',
            font_size=sp(12),
            color=get_color_from_hex(COLORS['text_muted']),
            halign='left',
            size_hint_y=0.2
        )
        action_label.bind(size=action_label.setter('text_size'))
        card.add_widget(action_label)

        card.screen_name = screen
        card.bind(on_touch_down=self.on_card_touch)

        return card

    def on_card_touch(self, card, touch):
        if card.collide_point(*touch.pos):
            if hasattr(card, 'screen_name'):
                self.manager.transition = SlideTransition(direction='left')
                self.manager.current = card.screen_name
                return True
        return False

    def set_language(self, lang):
        app = App.get_running_app()
        app.current_language = lang

        if lang == Language.EN:
            self.lang_en_btn.background_color = get_color_from_hex(COLORS['primary'])
            self.lang_pt_btn.background_color = get_color_from_hex(COLORS['card'])
        else:
            self.lang_en_btn.background_color = get_color_from_hex(COLORS['card'])
            self.lang_pt_btn.background_color = get_color_from_hex(COLORS['primary'])


class MetaDecksScreen(Screen):
    """Beautiful meta decks gallery with card images."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        main = ColoredBoxLayout(orientation='vertical', bg_color=COLORS['background'])

        # Header
        header = HeaderWidget('Top 8 Meta Decks', on_back=self.go_back, subtitle='January 2026')
        main.add_widget(header)

        # Deck list
        scroll = ScrollView()
        self.deck_container = GridLayout(
            cols=1,
            spacing=dp(14),
            padding=[dp(16), dp(16)],
            size_hint_y=None
        )
        self.deck_container.bind(minimum_height=self.deck_container.setter('height'))
        scroll.add_widget(self.deck_container)
        main.add_widget(scroll)

        self.add_widget(main)

    def on_enter(self):
        self.refresh_decks()

    def refresh_decks(self):
        self.deck_container.clear_widgets()
        lang = App.get_running_app().current_language

        for i, deck in enumerate(get_all_decks()[:8], 1):
            deck_info = get_deck_info(deck.id)
            card = self._create_deck_card(i, deck, deck_info, lang)
            self.deck_container.add_widget(card)

    def _create_deck_card(self, rank, deck, deck_info, lang):
        """Create a beautiful deck card with image and stats."""
        type_color = get_type_color(deck_info.get('type', 'colorless'))

        card = GlassCard(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(130),
            glow_color=type_color
        )

        # Left: Card image thumbnail
        img_box = BoxLayout(size_hint_x=None, width=dp(85), padding=[0, dp(5)])
        card_img = AsyncImage(
            source=deck_info.get('icon_url', ''),
            allow_stretch=True,
            keep_ratio=True
        )
        img_box.add_widget(card_img)
        card.add_widget(img_box)

        # Center: Deck info
        info_box = BoxLayout(orientation='vertical', padding=[dp(10), 0], spacing=dp(4))

        # Rank and name
        name_row = BoxLayout(size_hint_y=None, height=dp(28))
        rank_label = Label(
            text=f'[b]#{rank}[/b]',
            markup=True,
            font_size=sp(18),
            color=get_color_from_hex(self._get_rank_color(rank)),
            size_hint_x=None,
            width=dp(35),
            halign='left'
        )
        rank_label.bind(size=rank_label.setter('text_size'))
        name_row.add_widget(rank_label)

        name_label = Label(
            text=f'[b]{deck.get_name(lang)}[/b]',
            markup=True,
            font_size=sp(16),
            color=get_color_from_hex(type_color),
            halign='left'
        )
        name_label.bind(size=name_label.setter('text_size'))
        name_row.add_widget(name_label)
        info_box.add_widget(name_row)

        # Type badge row
        badge_row = BoxLayout(size_hint_y=None, height=dp(32))
        type_badge = TypeBadge(deck_info.get('type_icon', 'Unknown'))
        badge_row.add_widget(type_badge)
        badge_row.add_widget(Widget())  # Spacer
        info_box.add_widget(badge_row)

        # Stats row
        stats_row = BoxLayout(size_hint_y=None, height=dp(24))
        tier_text = f'Tier {deck.tier}'
        meta_text = f'{deck.meta_share:.1f}% meta'
        stats_label = Label(
            text=f'[color=#8b949e]{tier_text}[/color]  |  [color=#58a6ff]{meta_text}[/color]',
            markup=True,
            font_size=sp(12),
            halign='left',
            size_hint_y=1
        )
        stats_label.bind(size=stats_label.setter('text_size'))
        stats_row.add_widget(stats_label)
        info_box.add_widget(stats_row)

        # Difficulty
        diff_colors = {'Beginner': COLORS['success'], 'Intermediate': COLORS['warning'], 'Advanced': COLORS['danger']}
        diff_color = diff_colors.get(deck.difficulty, COLORS['text_secondary'])
        diff_label = Label(
            text=f'[color={diff_color[1:]}]{get_difficulty_translation(deck.difficulty, lang)}[/color]',
            markup=True,
            font_size=sp(12),
            halign='left',
            size_hint_y=None,
            height=dp(20)
        )
        diff_label.bind(size=diff_label.setter('text_size'))
        info_box.add_widget(diff_label)

        card.add_widget(info_box)

        # Right: Arrow
        arrow_box = BoxLayout(size_hint_x=None, width=dp(36))
        arrow = Label(
            text='[color=#6e7681]>[/color]',
            markup=True,
            font_size=sp(28)
        )
        arrow_box.add_widget(arrow)
        card.add_widget(arrow_box)

        card.deck_id = deck.id
        card.bind(on_touch_down=self.on_deck_touch)

        return card

    def _get_rank_color(self, rank):
        if rank == 1:
            return COLORS['gold']
        elif rank == 2:
            return COLORS['silver']
        elif rank == 3:
            return COLORS['bronze']
        return COLORS['text_secondary']

    def on_deck_touch(self, card, touch):
        if card.collide_point(*touch.pos):
            if hasattr(card, 'deck_id'):
                app = App.get_running_app()
                app.selected_deck_id = card.deck_id
                self.manager.transition = SlideTransition(direction='left')
                self.manager.current = 'details'
                return True
        return False

    def go_back(self, *args):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'home'


class DeckDetailsScreen(Screen):
    """Stunning deck details with card gallery."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        main = ColoredBoxLayout(orientation='vertical', bg_color=COLORS['background'])

        # Header
        self.header = HeaderWidget('Deck Details', on_back=self.go_back)
        main.add_widget(self.header)

        # Hero section with card image and name
        self.hero_section = ColoredBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(140),
            bg_color=COLORS['surface'],
            padding=[dp(16), dp(12)],
            spacing=dp(16)
        )

        # Card image
        self.hero_image = AsyncImage(
            source='',
            allow_stretch=True,
            keep_ratio=True,
            size_hint_x=None,
            width=dp(95)
        )
        self.hero_section.add_widget(self.hero_image)

        # Deck info
        info_box = BoxLayout(orientation='vertical', spacing=dp(6))

        self.deck_name_label = Label(
            text='[b]Deck Name[/b]',
            markup=True,
            font_size=sp(22),
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            size_hint_y=0.35
        )
        self.deck_name_label.bind(size=self.deck_name_label.setter('text_size'))
        info_box.add_widget(self.deck_name_label)

        self.deck_type_label = Label(
            text='Type',
            font_size=sp(13),
            color=get_color_from_hex(COLORS['text_secondary']),
            halign='left',
            size_hint_y=0.2
        )
        self.deck_type_label.bind(size=self.deck_type_label.setter('text_size'))
        info_box.add_widget(self.deck_type_label)

        # Stats row in hero
        stats_box = BoxLayout(size_hint_y=0.25, spacing=dp(20))

        self.tier_display = Label(
            text='[b][color=#ffd700]Tier 1[/color][/b]',
            markup=True,
            font_size=sp(14),
            halign='left'
        )
        self.tier_display.bind(size=self.tier_display.setter('text_size'))
        stats_box.add_widget(self.tier_display)

        self.meta_display = Label(
            text='[color=#58a6ff]26.5%[/color]',
            markup=True,
            font_size=sp(14),
            halign='left'
        )
        self.meta_display.bind(size=self.meta_display.setter('text_size'))
        stats_box.add_widget(self.meta_display)

        info_box.add_widget(stats_box)
        info_box.add_widget(Widget(size_hint_y=0.2))  # Spacer

        self.hero_section.add_widget(info_box)
        main.add_widget(self.hero_section)

        # Tab buttons
        tab_container = ColoredBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            bg_color=COLORS['surface'],
            spacing=dp(8),
            padding=[dp(12), dp(6)]
        )

        self.tab_buttons = {}
        tabs = [('Info', 'info'), ('Cards', 'cards'), ('Gallery', 'gallery'), ('Matchups', 'matchups')]

        for text, tab_id in tabs:
            btn = StyledButton(
                text=text,
                bg_color=COLORS['primary'] if tab_id == 'info' else COLORS['card'],
                font_size=sp(13)
            )
            btn.tab_id = tab_id
            btn.bind(on_press=self.switch_tab)
            self.tab_buttons[tab_id] = btn
            tab_container.add_widget(btn)

        main.add_widget(tab_container)

        # Content area
        self.content_scroll = ScrollView()
        self.content_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=[dp(16), dp(16)]
        )
        self.content_container.bind(minimum_height=self.content_container.setter('height'))

        # Text content
        self.content_label = Label(
            text='',
            markup=True,
            font_size=sp(14),
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            valign='top',
            size_hint_y=None
        )
        self.content_label.bind(texture_size=self._update_content_size)

        # Gallery container
        self.gallery_container = GridLayout(
            cols=2,
            spacing=dp(12),
            size_hint_y=None,
            height=0
        )
        self.gallery_container.bind(minimum_height=self.gallery_container.setter('height'))

        self.content_container.add_widget(self.gallery_container)
        self.content_container.add_widget(self.content_label)
        self.content_scroll.add_widget(self.content_container)
        main.add_widget(self.content_scroll)

        self.add_widget(main)
        self.current_tab = 'info'
        self.current_deck = None

    def _update_content_size(self, *args):
        self.content_label.height = self.content_label.texture_size[1] + dp(40)
        self.content_label.text_size = (self.content_scroll.width - dp(40), None)

    def on_enter(self):
        app = App.get_running_app()
        deck_id = getattr(app, 'selected_deck_id', None)
        lang = app.current_language

        if deck_id and deck_id in META_DECKS:
            self.current_deck = META_DECKS[deck_id]
            deck = self.current_deck
            deck_info = get_deck_info(deck.id)
            type_color = get_type_color(deck_info.get('type', 'colorless'))

            # Update hero section
            self.hero_image.source = deck_info.get('icon_url', '')
            self.deck_name_label.text = f'[b]{deck.get_name(lang)}[/b]'
            self.deck_name_label.color = get_color_from_hex(type_color)
            self.deck_type_label.text = f'{deck_info.get("type_icon", "Unknown")} Type  |  {", ".join(deck.energy_types)}'

            tier_colors = {1: COLORS['gold'], 2: COLORS['silver'], 3: COLORS['bronze']}
            tier_color = tier_colors.get(deck.tier, COLORS['text_secondary'])
            self.tier_display.text = f'[b][color={tier_color[1:]}]Tier {deck.tier}[/color][/b]'
            self.meta_display.text = f'[color=#58a6ff]{deck.meta_share:.1f}% Meta[/color]'

            self.show_tab('info')

    def switch_tab(self, btn):
        self.show_tab(btn.tab_id)

    def show_tab(self, tab_id):
        self.current_tab = tab_id

        # Update button colors
        for tid, btn in self.tab_buttons.items():
            btn.background_color = get_color_from_hex(
                COLORS['primary'] if tid == tab_id else COLORS['card']
            )

        if not self.current_deck:
            return

        deck = self.current_deck
        lang = App.get_running_app().current_language

        # Hide/show gallery
        if tab_id == 'gallery':
            self.gallery_container.height = dp(500)
            self.show_gallery(deck)
            self.content_label.text = ''
        else:
            self.gallery_container.clear_widgets()
            self.gallery_container.height = 0

            if tab_id == 'info':
                self.show_info(deck, lang)
            elif tab_id == 'cards':
                self.show_cards(deck, lang)
            elif tab_id == 'matchups':
                self.show_matchups(deck, lang)

    def show_gallery(self, deck):
        """Show card gallery."""
        self.gallery_container.clear_widgets()
        deck_info = get_deck_info(deck.id)

        # Main card
        main_card_url = deck_info.get('card_url', '')
        if main_card_url:
            card_widget = self._create_gallery_card(main_card_url, 'Main Card')
            self.gallery_container.add_widget(card_widget)

        # Secondary cards
        for i, url in enumerate(deck_info.get('secondary_cards', [])):
            card_widget = self._create_gallery_card(url, f'Card {i+2}')
            self.gallery_container.add_widget(card_widget)

    def _create_gallery_card(self, url, label):
        """Create a gallery card widget."""
        card_box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(240))

        img = AsyncImage(
            source=url,
            allow_stretch=True,
            keep_ratio=True,
            size_hint_y=0.9
        )
        card_box.add_widget(img)

        lbl = Label(
            text=label,
            font_size=sp(11),
            color=get_color_from_hex(COLORS['text_secondary']),
            size_hint_y=0.1
        )
        card_box.add_widget(lbl)

        return card_box

    def show_info(self, deck, lang):
        deck_info = get_deck_info(deck.id)
        type_color = get_type_color(deck_info.get('type', 'colorless'))

        diff_colors = {'Beginner': COLORS['success'], 'Intermediate': COLORS['warning'], 'Advanced': COLORS['danger']}
        diff_color = diff_colors.get(deck.difficulty, COLORS['text'])

        strengths = '\n'.join([f"  [color={COLORS['success'][1:]}]+[/color] {s}" for s in deck.get_strengths(lang)])
        weaknesses = '\n'.join([f"  [color={COLORS['danger'][1:]}]-[/color] {w}" for w in deck.get_weaknesses(lang)])

        text = f"""[size=22sp][b][color={type_color[1:]}]{deck.get_name(lang)}[/color][/b][/size]

[color={COLORS['border'][1:]}]{'_' * 40}[/color]

[b]Overview[/b]
{deck.get_description(lang)}

[b]Strategy[/b]
{deck.get_strategy(lang)}

[color={COLORS['border'][1:]}]{'_' * 40}[/color]

[b]Key Pokemon[/b]
{', '.join(deck.key_pokemon)}

[b]Energy Types[/b]
{', '.join(deck.energy_types)}

[b]Difficulty[/b]
[color={diff_color[1:]}]{get_difficulty_translation(deck.difficulty, lang)}[/color]

[color={COLORS['border'][1:]}]{'_' * 40}[/color]

[b][color={COLORS['success'][1:]}]Strengths[/color][/b]
{strengths}

[b][color={COLORS['danger'][1:]}]Weaknesses[/color][/b]
{weaknesses}
"""
        self.content_label.text = text

    def show_cards(self, deck, lang):
        pokemon = deck.get_pokemon()
        trainers = deck.get_trainers()
        energy = deck.get_energy()

        pokemon_text = '\n'.join([f"  [color=#58a6ff]{c.quantity}x[/color] {c.get_name(lang)} [color=#6e7681]({c.set_code})[/color]" for c in pokemon])
        trainer_text = '\n'.join([f"  [color=#58a6ff]{c.quantity}x[/color] {c.get_name(lang)} [color=#6e7681]({c.set_code})[/color]" for c in trainers])
        energy_text = '\n'.join([f"  [color=#58a6ff]{c.quantity}x[/color] {c.get_name(lang)} [color=#6e7681]({c.set_code})[/color]" for c in energy])

        text = f"""[size=20sp][b]Full Deck List[/b][/size]
[color={COLORS['text_secondary'][1:]}]Total: {deck.total_cards()} cards[/color]

[color={COLORS['border'][1:]}]{'_' * 40}[/color]

[b][color={COLORS['success'][1:]}]Pokemon ({sum(c.quantity for c in pokemon)})[/color][/b]
{pokemon_text}

[color={COLORS['border'][1:]}]{'_' * 40}[/color]

[b][color={COLORS['warning'][1:]}]Trainers ({sum(c.quantity for c in trainers)})[/color][/b]
{trainer_text}

[color={COLORS['border'][1:]}]{'_' * 40}[/color]

[b][color={COLORS['secondary'][1:]}]Energy ({sum(c.quantity for c in energy)})[/color][/b]
{energy_text}
"""
        self.content_label.text = text

    def show_matchups(self, deck, lang):
        matchups = get_deck_matchups(deck.id)

        lines = [f"[size=20sp][b]Matchup Analysis[/b][/size]\n"]
        lines.append(f"[color={COLORS['border'][1:]}]{'_' * 40}[/color]\n")

        for opp_id, win_rate, notes in matchups:
            opp_deck = META_DECKS.get(opp_id)
            if opp_deck:
                opp_info = get_deck_info(opp_id)
                opp_color = get_type_color(opp_info.get('type', 'colorless'))

                if win_rate >= 55:
                    color = COLORS['success']
                    icon = '[color=#3fb950]Favorable[/color]'
                elif win_rate <= 45:
                    color = COLORS['danger']
                    icon = '[color=#f85149]Unfavorable[/color]'
                else:
                    color = COLORS['warning']
                    icon = '[color=#d29922]Even[/color]'

                matchup_obj = get_matchup(deck.id, opp_id)
                notes_text = matchup_obj.get_notes(lang) if matchup_obj else ""

                lines.append(f"\n[b]vs [color={opp_color[1:]}]{opp_deck.get_name(lang)}[/color][/b]")
                lines.append(f"[size=28sp][color={color[1:]}]{win_rate:.0f}%[/color][/size]  {icon}")
                if notes_text:
                    lines.append(f"[color={COLORS['text_secondary'][1:]}][size=12sp]{notes_text}[/size][/color]")
                lines.append("")

        self.content_label.text = '\n'.join(lines)

    def go_back(self, *args):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'meta'


class MatchupsScreen(Screen):
    """Beautiful matchup comparison screen."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        main = ColoredBoxLayout(orientation='vertical', bg_color=COLORS['background'])

        # Header
        header = HeaderWidget('Matchup Chart', on_back=self.go_back, subtitle='Compare win rates')
        main.add_widget(header)

        # Content
        content = BoxLayout(
            orientation='vertical',
            padding=[dp(20), dp(16)],
            spacing=dp(16)
        )

        # Deck selection cards
        decks = get_all_decks()[:8]
        self.deck_names = {d.name_en: d for d in decks}
        deck_list = ['-- Select Deck --'] + [d.name_en for d in decks]

        # Deck A
        deck_a_card = GlassCard(size_hint_y=None, height=dp(90), glow_color=COLORS['secondary'])
        deck_a_content = BoxLayout(orientation='vertical', spacing=dp(4))

        deck_a_label = Label(
            text='[b]Deck 1[/b]',
            markup=True,
            font_size=sp(14),
            color=get_color_from_hex(COLORS['text_secondary']),
            size_hint_y=0.35,
            halign='left'
        )
        deck_a_label.bind(size=deck_a_label.setter('text_size'))

        self.deck_a_btn = StyledButton(
            text='-- Select Deck --',
            size_hint_y=0.65,
            bg_color=COLORS['surface_light']
        )
        self.deck_a_btn.deck_list = deck_list
        self.deck_a_btn.current_idx = 0
        self.deck_a_btn.bind(on_press=self.cycle_deck_a)

        deck_a_content.add_widget(deck_a_label)
        deck_a_content.add_widget(self.deck_a_btn)
        deck_a_card.add_widget(deck_a_content)
        content.add_widget(deck_a_card)

        # VS divider
        vs_box = BoxLayout(size_hint_y=None, height=dp(50))
        vs_label = Label(
            text='[b][color=#f85149]VS[/color][/b]',
            markup=True,
            font_size=sp(28)
        )
        vs_box.add_widget(vs_label)
        content.add_widget(vs_box)

        # Deck B
        deck_b_card = GlassCard(size_hint_y=None, height=dp(90), glow_color=COLORS['warning'])
        deck_b_content = BoxLayout(orientation='vertical', spacing=dp(4))

        deck_b_label = Label(
            text='[b]Deck 2[/b]',
            markup=True,
            font_size=sp(14),
            color=get_color_from_hex(COLORS['text_secondary']),
            size_hint_y=0.35,
            halign='left'
        )
        deck_b_label.bind(size=deck_b_label.setter('text_size'))

        self.deck_b_btn = StyledButton(
            text='-- Select Deck --',
            size_hint_y=0.65,
            bg_color=COLORS['surface_light']
        )
        self.deck_b_btn.deck_list = deck_list
        self.deck_b_btn.current_idx = 0
        self.deck_b_btn.bind(on_press=self.cycle_deck_b)

        deck_b_content.add_widget(deck_b_label)
        deck_b_content.add_widget(self.deck_b_btn)
        deck_b_card.add_widget(deck_b_content)
        content.add_widget(deck_b_card)

        # Compare button
        compare_btn = StyledButton(
            text='Compare Matchup',
            size_hint_y=None,
            height=dp(54),
            bg_color=COLORS['success']
        )
        compare_btn.bind(on_press=self.compare_decks)
        content.add_widget(compare_btn)

        # Result area
        self.result_scroll = ScrollView(size_hint_y=1)
        self.result_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=[dp(8), dp(8)]
        )
        self.result_container.bind(minimum_height=self.result_container.setter('height'))

        self.result_label = Label(
            text='[color=#6e7681]Select two decks and tap Compare[/color]',
            markup=True,
            font_size=sp(14),
            halign='center',
            valign='top',
            size_hint_y=None
        )
        self.result_label.bind(texture_size=self._update_result_size)
        self.result_container.add_widget(self.result_label)
        self.result_scroll.add_widget(self.result_container)
        content.add_widget(self.result_scroll)

        main.add_widget(content)
        self.add_widget(main)

    def _update_result_size(self, *args):
        self.result_label.height = self.result_label.texture_size[1] + dp(20)
        self.result_label.text_size = (self.result_scroll.width - dp(40), None)

    def cycle_deck_a(self, btn):
        btn.current_idx = (btn.current_idx + 1) % len(btn.deck_list)
        btn.text = btn.deck_list[btn.current_idx]

    def cycle_deck_b(self, btn):
        btn.current_idx = (btn.current_idx + 1) % len(btn.deck_list)
        btn.text = btn.deck_list[btn.current_idx]

    def compare_decks(self, *args):
        lang = App.get_running_app().current_language

        name_a = self.deck_a_btn.text
        name_b = self.deck_b_btn.text

        if name_a == '-- Select Deck --' or name_b == '-- Select Deck --':
            self.result_label.text = f'[color={COLORS["danger"][1:]}]Please select both decks[/color]'
            return

        if name_a == name_b:
            self.result_label.text = f'[color={COLORS["danger"][1:]}]Please select different decks[/color]'
            return

        deck_a = self.deck_names.get(name_a)
        deck_b = self.deck_names.get(name_b)

        if not deck_a or not deck_b:
            self.result_label.text = f'[color={COLORS["danger"][1:]}]Deck not found[/color]'
            return

        matchup = get_matchup(deck_a.id, deck_b.id)
        if not matchup:
            self.result_label.text = f'[color={COLORS["warning"][1:]}]No matchup data available[/color]'
            return

        info_a = get_deck_info(deck_a.id)
        info_b = get_deck_info(deck_b.id)
        color_a = get_type_color(info_a.get('type', 'colorless'))
        color_b = get_type_color(info_b.get('type', 'colorless'))

        if matchup.win_rate_a >= 55:
            result_color_a, result_color_b = COLORS['success'], COLORS['danger']
            verdict = f'[color={color_a[1:]}]{deck_a.get_name(lang)}[/color] is favored'
        elif matchup.win_rate_a <= 45:
            result_color_a, result_color_b = COLORS['danger'], COLORS['success']
            verdict = f'[color={color_b[1:]}]{deck_b.get_name(lang)}[/color] is favored'
        else:
            result_color_a = result_color_b = COLORS['warning']
            verdict = 'Even matchup - skill dependent'

        result = f"""[size=18sp][b]Matchup Result[/b][/size]

[color={COLORS['border'][1:]}]{'_' * 35}[/color]

[b][color={color_a[1:]}]{deck_a.get_name(lang)}[/color][/b]
[size=42sp][color={result_color_a[1:]}]{matchup.win_rate_a:.0f}%[/color][/size]

[size=16sp][color=#6e7681]vs[/color][/size]

[b][color={color_b[1:]}]{deck_b.get_name(lang)}[/color][/b]
[size=42sp][color={result_color_b[1:]}]{matchup.win_rate_b:.0f}%[/color][/size]

[color={COLORS['border'][1:]}]{'_' * 35}[/color]

[b]Verdict:[/b] {verdict}

[b]Notes:[/b]
[color=#8b949e]{matchup.get_notes(lang)}[/color]
"""
        self.result_label.text = result

    def go_back(self, *args):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'home'


class SearchScreen(Screen):
    """Beautiful Pokemon search screen."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        main = ColoredBoxLayout(orientation='vertical', bg_color=COLORS['background'])

        # Header
        header = HeaderWidget('Search Pokemon', on_back=self.go_back, subtitle='Find decks by Pokemon')
        main.add_widget(header)

        # Search area
        search_card = GlassCard(
            size_hint_y=None,
            height=dp(70),
            glow_color=COLORS['secondary']
        )
        search_card.padding = [dp(12), dp(8)]

        search_box = BoxLayout(orientation='horizontal', spacing=dp(12))

        self.search_input = TextInput(
            hint_text='Enter Pokemon name...',
            multiline=False,
            size_hint_x=0.75,
            font_size=sp(16),
            background_color=get_color_from_hex(COLORS['surface_light']),
            foreground_color=get_color_from_hex(COLORS['text']),
            hint_text_color=get_color_from_hex(COLORS['text_muted']),
            cursor_color=get_color_from_hex(COLORS['primary']),
            padding=[dp(16), dp(12)]
        )

        search_btn = StyledButton(
            text='Search',
            size_hint_x=0.25,
            bg_color=COLORS['success']
        )
        search_btn.bind(on_press=self.do_search)

        search_box.add_widget(self.search_input)
        search_box.add_widget(search_btn)
        search_card.add_widget(search_box)
        main.add_widget(search_card)

        # Popular searches
        popular_box = ColoredBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(90),
            bg_color=COLORS['background'],
            padding=[dp(16), dp(8)]
        )

        popular_label = Label(
            text='[b]Popular Searches[/b]',
            markup=True,
            font_size=sp(13),
            color=get_color_from_hex(COLORS['text_muted']),
            halign='left',
            size_hint_y=0.3
        )
        popular_label.bind(size=popular_label.setter('text_size'))
        popular_box.add_widget(popular_label)

        chips_box = BoxLayout(size_hint_y=0.7, spacing=dp(8))
        popular_pokemon = ['Charizard', 'Gardevoir', 'Dragapult', 'Gholdengo']
        for name in popular_pokemon:
            chip = StyledButton(
                text=name,
                size_hint_x=None,
                width=dp(90),
                bg_color=COLORS['surface_light'],
                font_size=sp(12)
            )
            chip.search_term = name
            chip.bind(on_press=self.quick_search)
            chips_box.add_widget(chip)
        popular_box.add_widget(chips_box)
        main.add_widget(popular_box)

        # Results
        self.result_scroll = ScrollView()
        self.result_container = GridLayout(
            cols=1,
            spacing=dp(12),
            padding=[dp(16), dp(12)],
            size_hint_y=None
        )
        self.result_container.bind(minimum_height=self.result_container.setter('height'))
        self.result_scroll.add_widget(self.result_container)
        main.add_widget(self.result_scroll)

        self.add_widget(main)

    def quick_search(self, btn):
        self.search_input.text = btn.search_term
        self.do_search()

    def do_search(self, *args):
        query = self.search_input.text.strip().lower()
        if not query:
            return

        self.result_container.clear_widgets()
        lang = App.get_running_app().current_language

        found = False
        for deck in META_DECKS.values():
            match_reason = None

            # Check key pokemon
            for key_mon in deck.key_pokemon:
                if query in key_mon.lower():
                    match_reason = f"Key Pokemon: {key_mon}"
                    break

            if not match_reason:
                # Check all cards
                for card in deck.cards:
                    if card.card_type == "pokemon" and query in card.name_en.lower():
                        match_reason = f"Contains: {card.name_en}"
                        break

            if match_reason:
                found = True
                self.add_result(deck, lang, match_reason)

        if not found:
            no_result = Label(
                text=f'[color=#8b949e]No meta decks found with "[b]{query}[/b]"[/color]',
                markup=True,
                font_size=sp(14),
                size_hint_y=None,
                height=dp(60)
            )
            self.result_container.add_widget(no_result)

    def add_result(self, deck, lang, reason):
        deck_info = get_deck_info(deck.id)
        type_color = get_type_color(deck_info.get('type', 'colorless'))

        card = GlassCard(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(100),
            glow_color=type_color
        )

        # Icon
        icon_box = BoxLayout(size_hint_x=None, width=dp(70), padding=[dp(4), dp(8)])
        icon_img = AsyncImage(
            source=deck_info.get('icon_url', ''),
            allow_stretch=True,
            keep_ratio=True
        )
        icon_box.add_widget(icon_img)
        card.add_widget(icon_box)

        # Info
        info_box = BoxLayout(orientation='vertical', padding=[dp(8), 0], spacing=dp(4))

        name_label = Label(
            text=f'[b][color={type_color[1:]}]{deck.get_name(lang)}[/color][/b]',
            markup=True,
            font_size=sp(16),
            halign='left',
            size_hint_y=0.35
        )
        name_label.bind(size=name_label.setter('text_size'))

        reason_label = Label(
            text=f'[color={COLORS["success"][1:]}]{reason}[/color]',
            markup=True,
            font_size=sp(12),
            halign='left',
            size_hint_y=0.35
        )
        reason_label.bind(size=reason_label.setter('text_size'))

        stats_label = Label(
            text=f'[color=#8b949e]Tier {deck.tier} | {deck.meta_share:.1f}%[/color]',
            markup=True,
            font_size=sp(12),
            halign='left',
            size_hint_y=0.3
        )
        stats_label.bind(size=stats_label.setter('text_size'))

        info_box.add_widget(name_label)
        info_box.add_widget(reason_label)
        info_box.add_widget(stats_label)
        card.add_widget(info_box)

        # Arrow
        arrow_box = BoxLayout(size_hint_x=None, width=dp(32))
        arrow = Label(
            text='[color=#6e7681]>[/color]',
            markup=True,
            font_size=sp(28)
        )
        arrow_box.add_widget(arrow)
        card.add_widget(arrow_box)

        card.deck_id = deck.id
        card.bind(on_touch_down=self.on_result_touch)

        self.result_container.add_widget(card)

    def on_result_touch(self, card, touch):
        if card.collide_point(*touch.pos):
            if hasattr(card, 'deck_id'):
                app = App.get_running_app()
                app.selected_deck_id = card.deck_id
                self.manager.transition = SlideTransition(direction='left')
                self.manager.current = 'details'
                return True
        return False

    def go_back(self, *args):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'home'


class TCGMetaApp(App):
    """Beautiful Pokemon TCG Meta Analyzer App."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_language = Language.EN
        self.selected_deck_id = None

    def build(self):
        self.title = 'TCG Meta Analyzer'

        # Set window background color
        Window.clearcolor = get_color_from_hex(COLORS['background'])

        # Screen manager with smooth transitions
        sm = ScreenManager(transition=SlideTransition(duration=0.25))
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(MetaDecksScreen(name='meta'))
        sm.add_widget(DeckDetailsScreen(name='details'))
        sm.add_widget(MatchupsScreen(name='matchups'))
        sm.add_widget(SearchScreen(name='search'))

        # Bind to window resize for foldable devices
        Window.bind(on_resize=self.on_window_resize)

        return sm

    def on_window_resize(self, window, width, height):
        """Handle window resize for foldable phones."""
        if self.root:
            Clock.schedule_once(lambda dt: self._refresh_current_screen(), 0.1)

    def _refresh_current_screen(self):
        if self.root:
            current_screen = self.root.current_screen
            if current_screen:
                current_screen.do_layout()

    def on_start(self):
        """Called when the app starts."""
        if platform == 'android':
            try:
                from android.runnable import run_on_ui_thread
                from jnius import autoclass

                @run_on_ui_thread
                def set_window_flags():
                    PythonActivity = autoclass('org.kivy.android.PythonActivity')
                    activity = PythonActivity.mActivity
                    window = activity.getWindow()
                    if hasattr(window, 'setDecorFitsSystemWindows'):
                        window.setDecorFitsSystemWindows(False)

                set_window_flags()
            except Exception as e:
                print(f"Could not set Android window flags: {e}")


if __name__ == '__main__':
    TCGMetaApp().run()
