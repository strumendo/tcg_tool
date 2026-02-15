"""
Deck Detail screen - Shows complete deck information.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.metrics import dp
from kivy.clock import Clock

from app.components import (
    ColoredBox, CardBox, SecondaryButton, LoadingSpinner,
    COLORS, get_color_from_hex
)
from app.utils.responsive import scaled_font, get_padding, get_spacing, is_cover_mode
from app.services.api_client import APIClient
import threading


class CardItem(BoxLayout):
    """Individual card display widget."""

    def __init__(self, card_data, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.spacing = dp(10)
        self.size_hint_y = None
        self.height = dp(60)

        # Card image (small)
        if card_data.get('image_url'):
            img = AsyncImage(
                source=card_data['image_url'],
                size_hint_x=None,
                width=dp(40)
            )
            self.add_widget(img)

        # Card info
        info = BoxLayout(orientation='vertical', spacing=dp(2))

        # Card name and count
        name_text = f"{card_data.get('count', 1)}x {card_data.get('name', 'Card')}"
        name_label = Label(
            text=name_text,
            font_size=scaled_font(14),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            size_hint_y=None,
            height=dp(25),
            halign='left',
            valign='middle'
        )
        name_label.bind(size=lambda *x: setattr(name_label, 'text_size', (name_label.width, None)))
        info.add_widget(name_label)

        # Set info
        set_info = card_data.get('set', '')
        if set_info:
            set_label = Label(
                text=set_info,
                font_size=scaled_font(12),
                color=get_color_from_hex(COLORS['text_secondary']),
                size_hint_y=None,
                height=dp(20),
                halign='left',
                valign='middle'
            )
            set_label.bind(size=lambda *x: setattr(set_label, 'text_size', (set_label.width, None)))
            info.add_widget(set_label)

        self.add_widget(info)


class DeckDetailScreen(Screen):
    """Screen showing full deck details."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'deck_detail'
        self.api_client = APIClient()
        self.current_deck = None

        # Main container
        self.main_layout = ColoredBox(
            orientation='vertical',
            bg_color=COLORS['background']
        )

        self.add_widget(self.main_layout)

    def load_deck(self, deck_data):
        """Load and display deck details."""
        self.current_deck = deck_data
        self.main_layout.clear_widgets()

        # Loading state
        self.main_layout.add_widget(LoadingSpinner())

        # Fetch full deck details from API
        def fetch():
            try:
                deck_id = deck_data.get('id')
                result = self.api_client.get_deck_detail(deck_id)
                Clock.schedule_once(lambda dt: self._display_deck(result), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: self._show_error(str(e)), 0)

        threading.Thread(target=fetch, daemon=True).start()

    def _display_deck(self, deck_data):
        """Display full deck information."""
        self.main_layout.clear_widgets()

        # Scroll view
        scroll = ScrollView()
        content = BoxLayout(
            orientation='vertical',
            spacing=get_spacing(),
            padding=get_padding(),
            size_hint_y=None
        )
        content.bind(minimum_height=content.setter('height'))

        # Header section
        header = CardBox(
            orientation='vertical',
            size_hint_y=None,
            height=dp(150)
        )

        # Deck name
        name_label = Label(
            text=deck_data.get('name', 'Deck'),
            font_size=scaled_font(22),
            bold=True,
            color=get_color_from_hex(COLORS['primary']),
            size_hint_y=None,
            height=dp(40),
            halign='center',
            valign='middle'
        )
        name_label.bind(size=lambda *x: setattr(name_label, 'text_size', (name_label.width, None)))
        header.add_widget(name_label)

        # Stats
        tier = deck_data.get('tier', 'N/A')
        meta_share = deck_data.get('meta_share', 0)
        stats_label = Label(
            text=f'{tier} • {meta_share}% do meta',
            font_size=scaled_font(14),
            color=get_color_from_hex(COLORS['text_secondary']),
            size_hint_y=None,
            height=dp(30),
            halign='center',
            valign='middle'
        )
        stats_label.bind(size=lambda *x: setattr(stats_label, 'text_size', (stats_label.width, None)))
        header.add_widget(stats_label)

        # Description
        desc = deck_data.get('description', '')
        if desc:
            desc_label = Label(
                text=desc,
                font_size=scaled_font(13),
                color=get_color_from_hex(COLORS['text']),
                size_hint_y=None,
                height=dp(60),
                halign='center',
                valign='middle'
            )
            desc_label.bind(size=lambda *x: setattr(desc_label, 'text_size', (desc_label.width, None)))
            header.add_widget(desc_label)

        content.add_widget(header)

        # Card lists (tabbed or sections)
        cards = deck_data.get('cards', {})
        pokemon_cards = cards.get('pokemon', [])
        trainer_cards = cards.get('trainers', [])
        energy_cards = cards.get('energy', [])

        # Pokemon section
        if pokemon_cards:
            self._add_card_section(content, 'Pokémon', pokemon_cards)

        # Trainers section
        if trainer_cards:
            self._add_card_section(content, 'Treinadores', trainer_cards)

        # Energy section
        if energy_cards:
            self._add_card_section(content, 'Energias', energy_cards)

        # Matchups section
        matchups = deck_data.get('matchups', [])
        if matchups:
            content.add_widget(self._create_matchups_section(matchups))

        # Strengths/Weaknesses
        strengths = deck_data.get('strengths', [])
        weaknesses = deck_data.get('weaknesses', [])
        if strengths or weaknesses:
            content.add_widget(self._create_strengths_weaknesses_section(strengths, weaknesses))

        # Back button
        back_btn = SecondaryButton(
            text='← Voltar',
            size_hint_x=None,
            width=dp(150),
            pos_hint={'center_x': 0.5}
        )
        back_btn.bind(on_press=lambda x: self._go_back())
        content.add_widget(back_btn)

        scroll.add_widget(content)
        self.main_layout.add_widget(scroll)

    def _add_card_section(self, parent, title, cards):
        """Add a card list section."""
        # Section title
        title_label = Label(
            text=title,
            font_size=scaled_font(18),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            size_hint_y=None,
            height=dp(40),
            halign='left',
            valign='middle'
        )
        title_label.bind(size=lambda *x: setattr(title_label, 'text_size', (title_label.width, None)))
        parent.add_widget(title_label)

        # Cards container
        cards_box = CardBox(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(5)
        )
        cards_box.height = len(cards) * dp(65) + (len(cards) - 1) * dp(5) + get_padding()[0] * 2

        for card in cards:
            card_item = CardItem(card_data=card)
            cards_box.add_widget(card_item)

        parent.add_widget(cards_box)

    def _create_matchups_section(self, matchups):
        """Create matchups section."""
        section = CardBox(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(5)
        )

        # Title
        title = Label(
            text='Matchups',
            font_size=scaled_font(18),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            size_hint_y=None,
            height=dp(40),
            halign='left',
            valign='middle'
        )
        title.bind(size=lambda *x: setattr(title, 'text_size', (title.width, None)))
        section.add_widget(title)

        # Matchup items
        for matchup in matchups:
            matchup_box = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(40),
                spacing=dp(10)
            )

            opponent = Label(
                text=matchup.get('opponent', ''),
                font_size=scaled_font(14),
                color=get_color_from_hex(COLORS['text']),
                halign='left',
                valign='middle'
            )
            opponent.bind(size=lambda *x: setattr(opponent, 'text_size', (opponent.width, None)))
            matchup_box.add_widget(opponent)

            win_rate = matchup.get('win_rate', 50)
            wr_color = COLORS['success'] if win_rate >= 55 else COLORS['danger'] if win_rate <= 45 else COLORS['secondary']
            win_rate_label = Label(
                text=f'{win_rate}%',
                font_size=scaled_font(14),
                bold=True,
                color=get_color_from_hex(wr_color),
                size_hint_x=None,
                width=dp(60),
                halign='right',
                valign='middle'
            )
            win_rate_label.bind(size=lambda *x: setattr(win_rate_label, 'text_size', (win_rate_label.width, None)))
            matchup_box.add_widget(win_rate_label)

            section.add_widget(matchup_box)

        section.height = dp(40) + len(matchups) * dp(45) + get_padding()[0] * 2
        return section

    def _create_strengths_weaknesses_section(self, strengths, weaknesses):
        """Create strengths and weaknesses section."""
        section = CardBox(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(10)
        )

        total_height = dp(20)

        if strengths:
            str_label = Label(
                text='✅ Pontos Fortes',
                font_size=scaled_font(16),
                bold=True,
                color=get_color_from_hex(COLORS['success']),
                size_hint_y=None,
                height=dp(30),
                halign='left',
                valign='middle'
            )
            str_label.bind(size=lambda *x: setattr(str_label, 'text_size', (str_label.width, None)))
            section.add_widget(str_label)
            total_height += dp(30)

            for strength in strengths:
                s_label = Label(
                    text=f'• {strength}',
                    font_size=scaled_font(13),
                    color=get_color_from_hex(COLORS['text']),
                    size_hint_y=None,
                    height=dp(25),
                    halign='left',
                    valign='middle'
                )
                s_label.bind(size=lambda *x: setattr(s_label, 'text_size', (s_label.width, None)))
                section.add_widget(s_label)
                total_height += dp(25)

        if weaknesses:
            weak_label = Label(
                text='⚠️ Pontos Fracos',
                font_size=scaled_font(16),
                bold=True,
                color=get_color_from_hex(COLORS['danger']),
                size_hint_y=None,
                height=dp(30),
                halign='left',
                valign='middle'
            )
            weak_label.bind(size=lambda *x: setattr(weak_label, 'text_size', (weak_label.width, None)))
            section.add_widget(weak_label)
            total_height += dp(30)

            for weakness in weaknesses:
                w_label = Label(
                    text=f'• {weakness}',
                    font_size=scaled_font(13),
                    color=get_color_from_hex(COLORS['text']),
                    size_hint_y=None,
                    height=dp(25),
                    halign='left',
                    valign='middle'
                )
                w_label.bind(size=lambda *x: setattr(w_label, 'text_size', (w_label.width, None)))
                section.add_widget(w_label)
                total_height += dp(25)

        section.height = total_height + get_padding()[0] * 2
        return section

    def _show_error(self, error_msg):
        """Show error message."""
        self.main_layout.clear_widgets()
        from app.components import ErrorMessage
        error = ErrorMessage(
            message=f'Erro ao carregar deck: {error_msg}',
            on_retry=lambda: self.load_deck(self.current_deck) if self.current_deck else None
        )
        self.main_layout.add_widget(error)

    def _go_back(self):
        """Navigate back to previous screen."""
        if self.manager:
            self.manager.current = 'meta'
