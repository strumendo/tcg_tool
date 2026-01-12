"""
TCG Meta Analyzer - Android App
Pokemon TCG competitive deck browser with matchup analysis
Optimized for Samsung Z Fold and other foldable devices
"""
import sys
import os

# Add the script's directory to path for imports to work from any location
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex, platform
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.clock import Clock

# Only set window size on desktop (not Android)
if platform not in ('android', 'ios'):
    Window.size = (420, 800)

# Import meta database
from meta_data import (
    META_DECKS, MATCHUPS, Language,
    get_matchup, get_deck_matchups, get_all_decks,
    get_translation, get_difficulty_translation
)

# Color scheme
COLORS = {
    'background': '#1a1a2e',
    'surface': '#16213e',
    'card': '#0f3460',
    'primary': '#e94560',
    'secondary': '#00d9ff',
    'success': '#4ecca3',
    'warning': '#ffc107',
    'danger': '#ff6b6b',
    'text': '#ffffff',
    'text_secondary': '#a0a0a0',
    'tier1': '#4ecca3',
    'tier2': '#ffc107',
    'tier3': '#a0a0a0',
}


class ColoredBoxLayout(BoxLayout):
    """BoxLayout with background color support."""

    def __init__(self, bg_color=None, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color or COLORS['background']
        with self.canvas.before:
            Color(*get_color_from_hex(self.bg_color))
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class CardWidget(BoxLayout):
    """A card-style widget with rounded corners and shadow effect."""

    def __init__(self, bg_color=None, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color or COLORS['card']
        self.padding = dp(15)
        with self.canvas.before:
            Color(*get_color_from_hex(self.bg_color))
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class StyledButton(Button):
    """Modern styled button."""

    def __init__(self, bg_color=None, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = get_color_from_hex(bg_color or COLORS['primary'])
        self.color = get_color_from_hex(COLORS['text'])
        self.font_size = sp(16)
        self.bold = True


class HeaderWidget(ColoredBoxLayout):
    """Reusable header with back button and title."""

    def __init__(self, title, show_back=True, on_back=None, **kwargs):
        super().__init__(bg_color=COLORS['surface'], **kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(60)
        self.padding = [dp(10), dp(5)]
        self.spacing = dp(10)

        if show_back:
            back_btn = StyledButton(
                text='←',
                size_hint=(None, 1),
                width=dp(50),
                bg_color=COLORS['card']
            )
            if on_back:
                back_btn.bind(on_press=on_back)
            self.add_widget(back_btn)

        title_label = Label(
            text=f'[b]{title}[/b]',
            markup=True,
            font_size=sp(20),
            color=get_color_from_hex(COLORS['text']),
            halign='center'
        )
        self.add_widget(title_label)

        if show_back:
            # Spacer to balance the back button
            self.add_widget(Widget(size_hint=(None, 1), width=dp(50)))


class HomeScreen(Screen):
    """Main home screen with menu options."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        # Main container with background
        main = ColoredBoxLayout(orientation='vertical', bg_color=COLORS['background'])

        # Header area
        header_container = ColoredBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(180),
            bg_color=COLORS['surface'],
            padding=[dp(20), dp(30)]
        )

        # App title
        title = Label(
            text='[b]TCG Meta[/b]\n[size=16sp]Analyzer[/size]',
            markup=True,
            font_size=sp(36),
            color=get_color_from_hex(COLORS['primary']),
            halign='center',
            size_hint_y=0.7
        )
        title.bind(size=title.setter('text_size'))
        header_container.add_widget(title)

        # Subtitle
        subtitle = Label(
            text='Pokemon TCG Competitive Meta Browser',
            font_size=sp(14),
            color=get_color_from_hex(COLORS['text_secondary']),
            halign='center',
            size_hint_y=0.3
        )
        header_container.add_widget(subtitle)

        main.add_widget(header_container)

        # Language selector
        lang_container = ColoredBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            bg_color=COLORS['background'],
            padding=[dp(20), dp(5)],
            spacing=dp(10)
        )

        self.lang_en_btn = StyledButton(
            text='English',
            size_hint_x=0.5,
            bg_color=COLORS['primary']
        )
        self.lang_en_btn.bind(on_press=lambda x: self.set_language(Language.EN))

        self.lang_pt_btn = StyledButton(
            text='Português',
            size_hint_x=0.5,
            bg_color=COLORS['card']
        )
        self.lang_pt_btn.bind(on_press=lambda x: self.set_language(Language.PT))

        lang_container.add_widget(self.lang_en_btn)
        lang_container.add_widget(self.lang_pt_btn)
        main.add_widget(lang_container)

        # Menu buttons container
        menu_scroll = ScrollView(size_hint_y=1)
        menu_container = GridLayout(
            cols=1,
            spacing=dp(15),
            padding=[dp(20), dp(20)],
            size_hint_y=None
        )
        menu_container.bind(minimum_height=menu_container.setter('height'))

        # Menu items
        menu_items = [
            ('🎴  Browse Meta Decks', 'meta', COLORS['success'], 'View Top 8 competitive decks'),
            ('⚔️  Matchup Chart', 'matchups', COLORS['warning'], 'Compare deck win rates'),
            ('🔍  Search Pokemon', 'search', COLORS['secondary'], 'Find decks by Pokemon'),
        ]

        for text, screen, color, desc in menu_items:
            card = CardWidget(
                orientation='vertical',
                size_hint_y=None,
                height=dp(100),
                bg_color=COLORS['card']
            )

            btn_content = BoxLayout(orientation='vertical')

            btn_title = Label(
                text=f'[b]{text}[/b]',
                markup=True,
                font_size=sp(18),
                color=get_color_from_hex(color),
                halign='left',
                size_hint_y=0.6
            )
            btn_title.bind(size=btn_title.setter('text_size'))

            btn_desc = Label(
                text=desc,
                font_size=sp(12),
                color=get_color_from_hex(COLORS['text_secondary']),
                halign='left',
                size_hint_y=0.4
            )
            btn_desc.bind(size=btn_desc.setter('text_size'))

            btn_content.add_widget(btn_title)
            btn_content.add_widget(btn_desc)
            card.add_widget(btn_content)

            # Make the card clickable
            card.screen_name = screen
            card.bind(on_touch_down=self.on_card_touch)

            menu_container.add_widget(card)

        menu_scroll.add_widget(menu_container)
        main.add_widget(menu_scroll)

        # Footer
        footer = ColoredBoxLayout(
            size_hint_y=None,
            height=dp(40),
            bg_color=COLORS['surface'],
            padding=[dp(20), dp(10)]
        )
        footer_text = Label(
            text='January 2026 Meta | v1.0',
            font_size=sp(12),
            color=get_color_from_hex(COLORS['text_secondary'])
        )
        footer.add_widget(footer_text)
        main.add_widget(footer)

        self.add_widget(main)

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

        # Update button colors
        if lang == Language.EN:
            self.lang_en_btn.background_color = get_color_from_hex(COLORS['primary'])
            self.lang_pt_btn.background_color = get_color_from_hex(COLORS['card'])
        else:
            self.lang_en_btn.background_color = get_color_from_hex(COLORS['card'])
            self.lang_pt_btn.background_color = get_color_from_hex(COLORS['primary'])


class MetaDecksScreen(Screen):
    """Screen showing top 8 meta decks."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        main = ColoredBoxLayout(orientation='vertical', bg_color=COLORS['background'])

        # Header
        header = HeaderWidget('Top 8 Meta Decks', on_back=self.go_back)
        main.add_widget(header)

        # Deck list
        scroll = ScrollView()
        self.deck_container = GridLayout(
            cols=1,
            spacing=dp(10),
            padding=[dp(15), dp(15)],
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
            tier_color = COLORS[f'tier{deck.tier}'] if deck.tier <= 3 else COLORS['tier3']

            card = CardWidget(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(90),
                bg_color=COLORS['card']
            )

            # Rank badge
            rank_box = BoxLayout(size_hint_x=None, width=dp(50))
            rank_label = Label(
                text=f'[b]#{i}[/b]',
                markup=True,
                font_size=sp(24),
                color=get_color_from_hex(tier_color)
            )
            rank_box.add_widget(rank_label)
            card.add_widget(rank_box)

            # Deck info
            info_box = BoxLayout(orientation='vertical', padding=[dp(10), 0])

            name_label = Label(
                text=f'[b]{deck.get_name(lang)}[/b]',
                markup=True,
                font_size=sp(16),
                color=get_color_from_hex(COLORS['text']),
                halign='left',
                size_hint_y=0.5
            )
            name_label.bind(size=name_label.setter('text_size'))

            diff_text = get_difficulty_translation(deck.difficulty, lang)
            stats_label = Label(
                text=f'Tier {deck.tier} • {deck.meta_share:.1f}% • {diff_text}',
                font_size=sp(12),
                color=get_color_from_hex(COLORS['text_secondary']),
                halign='left',
                size_hint_y=0.5
            )
            stats_label.bind(size=stats_label.setter('text_size'))

            info_box.add_widget(name_label)
            info_box.add_widget(stats_label)
            card.add_widget(info_box)

            # Arrow
            arrow_box = BoxLayout(size_hint_x=None, width=dp(30))
            arrow = Label(
                text='›',
                font_size=sp(30),
                color=get_color_from_hex(COLORS['text_secondary'])
            )
            arrow_box.add_widget(arrow)
            card.add_widget(arrow_box)

            card.deck_id = deck.id
            card.bind(on_touch_down=self.on_deck_touch)

            self.deck_container.add_widget(card)

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
    """Screen showing detailed deck information."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        main = ColoredBoxLayout(orientation='vertical', bg_color=COLORS['background'])

        # Header (will be updated with deck name)
        self.header = HeaderWidget('Deck Details', on_back=self.go_back)
        main.add_widget(self.header)

        # Tab buttons
        tab_container = ColoredBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            bg_color=COLORS['surface'],
            spacing=dp(5),
            padding=[dp(10), dp(5)]
        )

        self.tab_buttons = {}
        tabs = [('Info', 'info'), ('Cards', 'cards'), ('Matchups', 'matchups')]

        for text, tab_id in tabs:
            btn = StyledButton(
                text=text,
                bg_color=COLORS['primary'] if tab_id == 'info' else COLORS['card']
            )
            btn.tab_id = tab_id
            btn.bind(on_press=self.switch_tab)
            self.tab_buttons[tab_id] = btn
            tab_container.add_widget(btn)

        main.add_widget(tab_container)

        # Content area
        self.content_scroll = ScrollView()
        self.content_label = Label(
            text='',
            markup=True,
            font_size=sp(14),
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            valign='top',
            size_hint_y=None,
            padding=[dp(20), dp(20)]
        )
        self.content_label.bind(texture_size=self._update_content_size)
        self.content_scroll.add_widget(self.content_label)
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

        if deck_id and deck_id in META_DECKS:
            self.current_deck = META_DECKS[deck_id]
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

        if tab_id == 'info':
            self.show_info(deck, lang)
        elif tab_id == 'cards':
            self.show_cards(deck, lang)
        elif tab_id == 'matchups':
            self.show_matchups(deck, lang)

    def show_info(self, deck, lang):
        diff_colors = {'Beginner': COLORS['success'], 'Intermediate': COLORS['warning'], 'Advanced': COLORS['danger']}
        diff_color = diff_colors.get(deck.difficulty, COLORS['text'])

        strengths = '\n'.join([f"  [color={COLORS['success'][1:]}]✓[/color] {s}" for s in deck.get_strengths(lang)])
        weaknesses = '\n'.join([f"  [color={COLORS['danger'][1:]}]✗[/color] {w}" for w in deck.get_weaknesses(lang)])

        text = f"""[size=24sp][b]{deck.get_name(lang)}[/b][/size]

[color={COLORS['text_secondary'][1:]}]━━━━━━━━━━━━━━━━━━━━━━━━[/color]

[b]Tier:[/b] {deck.tier}
[b]Meta Share:[/b] {deck.meta_share:.1f}%
[b]Difficulty:[/b] [color={diff_color[1:]}]{get_difficulty_translation(deck.difficulty, lang)}[/color]

[color={COLORS['text_secondary'][1:]}]━━━━━━━━━━━━━━━━━━━━━━━━[/color]

[b]Description[/b]
{deck.get_description(lang)}

[b]Strategy[/b]
{deck.get_strategy(lang)}

[color={COLORS['text_secondary'][1:]}]━━━━━━━━━━━━━━━━━━━━━━━━[/color]

[b]Key Pokemon:[/b] {', '.join(deck.key_pokemon)}
[b]Energy Types:[/b] {', '.join(deck.energy_types)}

[color={COLORS['text_secondary'][1:]}]━━━━━━━━━━━━━━━━━━━━━━━━[/color]

[b]Strengths[/b]
{strengths}

[b]Weaknesses[/b]
{weaknesses}
"""
        self.content_label.text = text

    def show_cards(self, deck, lang):
        pokemon = deck.get_pokemon()
        trainers = deck.get_trainers()
        energy = deck.get_energy()

        pokemon_text = '\n'.join([f"  {c.quantity}x {c.get_name(lang)} ({c.set_code} {c.set_number})" for c in pokemon])
        trainer_text = '\n'.join([f"  {c.quantity}x {c.get_name(lang)} ({c.set_code} {c.set_number})" for c in trainers])
        energy_text = '\n'.join([f"  {c.quantity}x {c.get_name(lang)} ({c.set_code} {c.set_number})" for c in energy])

        text = f"""[size=20sp][b]Deck List[/b][/size]
[color={COLORS['text_secondary'][1:]}]Total: {deck.total_cards()} cards[/color]

[color={COLORS['text_secondary'][1:]}]━━━━━━━━━━━━━━━━━━━━━━━━[/color]

[b][color={COLORS['success'][1:]}]Pokemon ({sum(c.quantity for c in pokemon)})[/color][/b]
{pokemon_text}

[color={COLORS['text_secondary'][1:]}]━━━━━━━━━━━━━━━━━━━━━━━━[/color]

[b][color={COLORS['warning'][1:]}]Trainer ({sum(c.quantity for c in trainers)})[/color][/b]
{trainer_text}

[color={COLORS['text_secondary'][1:]}]━━━━━━━━━━━━━━━━━━━━━━━━[/color]

[b][color={COLORS['secondary'][1:]}]Energy ({sum(c.quantity for c in energy)})[/color][/b]
{energy_text}
"""
        self.content_label.text = text

    def show_matchups(self, deck, lang):
        matchups = get_deck_matchups(deck.id)

        lines = [f"[size=20sp][b]Matchups[/b][/size]\n"]
        lines.append(f"[color={COLORS['text_secondary'][1:]}]━━━━━━━━━━━━━━━━━━━━━━━━[/color]\n")

        for opp_id, win_rate, notes in matchups:
            opp_deck = META_DECKS.get(opp_id)
            if opp_deck:
                if win_rate >= 55:
                    color = COLORS['success']
                    icon = '▲'
                elif win_rate <= 45:
                    color = COLORS['danger']
                    icon = '▼'
                else:
                    color = COLORS['warning']
                    icon = '●'

                matchup_obj = get_matchup(deck.id, opp_id)
                notes_text = matchup_obj.get_notes(lang) if matchup_obj else ""

                lines.append(f"\n[b]vs {opp_deck.get_name(lang)}[/b]")
                lines.append(f"[color={color[1:]}]{icon} {win_rate:.0f}%[/color]")
                if notes_text:
                    lines.append(f"[color={COLORS['text_secondary'][1:]}][size=12sp]{notes_text}[/size][/color]")
                lines.append("")

        self.content_label.text = '\n'.join(lines)

    def go_back(self, *args):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'meta'


class MatchupsScreen(Screen):
    """Screen for comparing two decks."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        main = ColoredBoxLayout(orientation='vertical', bg_color=COLORS['background'])

        # Header
        header = HeaderWidget('Matchup Chart', on_back=self.go_back)
        main.add_widget(header)

        # Content
        content = BoxLayout(
            orientation='vertical',
            padding=[dp(20), dp(20)],
            spacing=dp(15)
        )

        # Instructions
        instr = Label(
            text='Select two decks to compare their matchup:',
            font_size=sp(14),
            color=get_color_from_hex(COLORS['text_secondary']),
            size_hint_y=None,
            height=dp(30)
        )
        content.add_widget(instr)

        # Deck selection
        decks = get_all_decks()[:8]
        self.deck_names = {d.name_en: d for d in decks}
        deck_list = ['-- Select Deck --'] + [d.name_en for d in decks]

        # Deck A selector
        deck_a_box = CardWidget(size_hint_y=None, height=dp(70), bg_color=COLORS['card'])
        deck_a_content = BoxLayout(orientation='vertical')
        deck_a_label = Label(
            text='Deck 1:',
            font_size=sp(12),
            color=get_color_from_hex(COLORS['text_secondary']),
            size_hint_y=0.3,
            halign='left'
        )
        deck_a_label.bind(size=deck_a_label.setter('text_size'))

        self.deck_a_btn = StyledButton(
            text='-- Select Deck --',
            size_hint_y=0.7,
            bg_color=COLORS['surface']
        )
        self.deck_a_btn.deck_list = deck_list
        self.deck_a_btn.current_idx = 0
        self.deck_a_btn.bind(on_press=self.cycle_deck_a)

        deck_a_content.add_widget(deck_a_label)
        deck_a_content.add_widget(self.deck_a_btn)
        deck_a_box.add_widget(deck_a_content)
        content.add_widget(deck_a_box)

        # VS label
        vs_label = Label(
            text='[b]VS[/b]',
            markup=True,
            font_size=sp(24),
            color=get_color_from_hex(COLORS['primary']),
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(vs_label)

        # Deck B selector
        deck_b_box = CardWidget(size_hint_y=None, height=dp(70), bg_color=COLORS['card'])
        deck_b_content = BoxLayout(orientation='vertical')
        deck_b_label = Label(
            text='Deck 2:',
            font_size=sp(12),
            color=get_color_from_hex(COLORS['text_secondary']),
            size_hint_y=0.3,
            halign='left'
        )
        deck_b_label.bind(size=deck_b_label.setter('text_size'))

        self.deck_b_btn = StyledButton(
            text='-- Select Deck --',
            size_hint_y=0.7,
            bg_color=COLORS['surface']
        )
        self.deck_b_btn.deck_list = deck_list
        self.deck_b_btn.current_idx = 0
        self.deck_b_btn.bind(on_press=self.cycle_deck_b)

        deck_b_content.add_widget(deck_b_label)
        deck_b_content.add_widget(self.deck_b_btn)
        deck_b_box.add_widget(deck_b_content)
        content.add_widget(deck_b_box)

        # Compare button
        compare_btn = StyledButton(
            text='Compare Matchup',
            size_hint_y=None,
            height=dp(50),
            bg_color=COLORS['success']
        )
        compare_btn.bind(on_press=self.compare_decks)
        content.add_widget(compare_btn)

        # Result area
        self.result_scroll = ScrollView(size_hint_y=1)
        self.result_label = Label(
            text='',
            markup=True,
            font_size=sp(14),
            color=get_color_from_hex(COLORS['text']),
            halign='center',
            valign='top',
            size_hint_y=None
        )
        self.result_label.bind(texture_size=self._update_result_size)
        self.result_scroll.add_widget(self.result_label)
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

        if matchup.win_rate_a >= 55:
            color_a, color_b = COLORS['success'], COLORS['danger']
            winner = deck_a.get_name(lang)
        elif matchup.win_rate_a <= 45:
            color_a, color_b = COLORS['danger'], COLORS['success']
            winner = deck_b.get_name(lang)
        else:
            color_a = color_b = COLORS['warning']
            winner = "Even matchup"

        result = f"""[size=20sp][b]Matchup Result[/b][/size]

[color={COLORS['text_secondary'][1:]}]━━━━━━━━━━━━━━━━━━━━[/color]

[b]{deck_a.get_name(lang)}[/b]
[size=36sp][color={color_a[1:]}]{matchup.win_rate_a:.0f}%[/color][/size]

[size=16sp]vs[/size]

[b]{deck_b.get_name(lang)}[/b]
[size=36sp][color={color_b[1:]}]{matchup.win_rate_b:.0f}%[/color][/size]

[color={COLORS['text_secondary'][1:]}]━━━━━━━━━━━━━━━━━━━━[/color]

[b]Notes:[/b]
{matchup.get_notes(lang)}
"""
        self.result_label.text = result

    def go_back(self, *args):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'home'


class SearchScreen(Screen):
    """Screen for searching Pokemon in meta decks."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        main = ColoredBoxLayout(orientation='vertical', bg_color=COLORS['background'])

        # Header
        header = HeaderWidget('Search Pokemon', on_back=self.go_back)
        main.add_widget(header)

        # Search area
        search_box = ColoredBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            bg_color=COLORS['surface'],
            padding=[dp(15), dp(10)],
            spacing=dp(10)
        )

        self.search_input = TextInput(
            hint_text='Enter Pokemon name...',
            multiline=False,
            size_hint_x=0.7,
            font_size=sp(16),
            background_color=get_color_from_hex(COLORS['card']),
            foreground_color=get_color_from_hex(COLORS['text']),
            hint_text_color=get_color_from_hex(COLORS['text_secondary']),
            cursor_color=get_color_from_hex(COLORS['primary']),
            padding=[dp(15), dp(12)]
        )

        search_btn = StyledButton(
            text='🔍',
            size_hint_x=0.3,
            bg_color=COLORS['success']
        )
        search_btn.bind(on_press=self.do_search)

        search_box.add_widget(self.search_input)
        search_box.add_widget(search_btn)
        main.add_widget(search_box)

        # Results
        self.result_scroll = ScrollView()
        self.result_container = GridLayout(
            cols=1,
            spacing=dp(10),
            padding=[dp(15), dp(15)],
            size_hint_y=None
        )
        self.result_container.bind(minimum_height=self.result_container.setter('height'))
        self.result_scroll.add_widget(self.result_container)
        main.add_widget(self.result_scroll)

        self.add_widget(main)

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
                text=f'No meta decks found with "[b]{query}[/b]"',
                markup=True,
                font_size=sp(14),
                color=get_color_from_hex(COLORS['text_secondary']),
                size_hint_y=None,
                height=dp(60)
            )
            self.result_container.add_widget(no_result)

    def add_result(self, deck, lang, reason):
        card = CardWidget(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(90),
            bg_color=COLORS['card']
        )

        # Info
        info_box = BoxLayout(orientation='vertical', padding=[dp(5), 0])

        name_label = Label(
            text=f'[b]{deck.get_name(lang)}[/b]',
            markup=True,
            font_size=sp(16),
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            size_hint_y=0.4
        )
        name_label.bind(size=name_label.setter('text_size'))

        reason_label = Label(
            text=f'[color={COLORS["success"][1:]}]{reason}[/color]',
            markup=True,
            font_size=sp(12),
            halign='left',
            size_hint_y=0.3
        )
        reason_label.bind(size=reason_label.setter('text_size'))

        stats_label = Label(
            text=f'Tier {deck.tier} • {deck.meta_share:.1f}%',
            font_size=sp(12),
            color=get_color_from_hex(COLORS['text_secondary']),
            halign='left',
            size_hint_y=0.3
        )
        stats_label.bind(size=stats_label.setter('text_size'))

        info_box.add_widget(name_label)
        info_box.add_widget(reason_label)
        info_box.add_widget(stats_label)
        card.add_widget(info_box)

        # Arrow
        arrow_box = BoxLayout(size_hint_x=None, width=dp(30))
        arrow = Label(
            text='›',
            font_size=sp(30),
            color=get_color_from_hex(COLORS['text_secondary'])
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
    """Main application class."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_language = Language.EN
        self.selected_deck_id = None

    def build(self):
        self.title = 'TCG Meta Analyzer'

        # Set window background color
        Window.clearcolor = get_color_from_hex(COLORS['background'])

        # Screen manager with slide transitions
        sm = ScreenManager(transition=SlideTransition())
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
            # Schedule a layout refresh
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
