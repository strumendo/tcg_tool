"""
Battles screen - Track and analyze battle history.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.clock import Clock

from app.components import (
    ColoredBox, CardBox, PrimaryButton, SecondaryButton,
    LoadingSpinner, ErrorMessage, COLORS, get_color_from_hex
)
from app.utils.responsive import scaled_font, get_padding, get_spacing
from app.services.api_client import APIClient
import threading


class BattleCard(CardBox):
    """Battle history card widget."""

    def __init__(self, battle_data, on_click=None, **kwargs):
        super().__init__(**kwargs)
        self.battle_data = battle_data
        self.orientation = 'horizontal'
        self.spacing = dp(10)
        self.size_hint_y = None
        self.height = dp(80)

        # Result indicator
        result = battle_data.get('result', 'T')  # W, L, T
        result_colors = {
            'W': COLORS['success'],
            'L': COLORS['danger'],
            'T': COLORS['text_muted']
        }
        result_labels = {
            'W': 'V',
            'L': 'D',
            'T': 'E'
        }

        result_box = ColoredBox(
            bg_color=result_colors.get(result, COLORS['text_muted']),
            size_hint_x=None,
            width=dp(50),
            radius=[dp(4)] * 4
        )

        result_label = Label(
            text=result_labels.get(result, 'E'),
            font_size=scaled_font(24),
            bold=True,
            color=get_color_from_hex(COLORS['nav_text']),
            halign='center',
            valign='middle'
        )
        result_box.add_widget(result_label)
        self.add_widget(result_box)

        # Battle info
        info_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(5)
        )

        # Opponent
        opponent_label = Label(
            text=f"vs {battle_data.get('opponent', 'Oponente')}",
            font_size=scaled_font(15),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            size_hint_y=None,
            height=dp(25),
            halign='left',
            valign='middle'
        )
        opponent_label.bind(size=lambda *x: setattr(opponent_label, 'text_size', (opponent_label.width, None)))
        info_layout.add_widget(opponent_label)

        # Date and turns
        date = battle_data.get('date', '')
        turns = battle_data.get('turns', 0)
        details_label = Label(
            text=f"{date} • {turns} turnos" if turns else date,
            font_size=scaled_font(12),
            color=get_color_from_hex(COLORS['text_secondary']),
            size_hint_y=None,
            height=dp(20),
            halign='left',
            valign='middle'
        )
        details_label.bind(size=lambda *x: setattr(details_label, 'text_size', (details_label.width, None)))
        info_layout.add_widget(details_label)

        # AI analysis indicator
        has_analysis = battle_data.get('has_analysis', False)
        if has_analysis:
            analysis_label = Label(
                text='🤖 Análise disponível',
                font_size=scaled_font(11),
                color=get_color_from_hex(COLORS['accent']),
                size_hint_y=None,
                height=dp(20),
                halign='left',
                valign='middle'
            )
            analysis_label.bind(size=lambda *x: setattr(analysis_label, 'text_size', (analysis_label.width, None)))
            info_layout.add_widget(analysis_label)

        self.add_widget(info_layout)

        # Make card clickable
        if on_click:
            self.bind(on_touch_down=lambda instance, touch: on_click(battle_data) if self.collide_point(*touch.pos) else None)


class BattlesScreen(Screen):
    """Screen for tracking battle history."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'battles'
        self.api_client = APIClient()
        self.battles_data = []

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
        Clock.schedule_once(lambda dt: self._load_battles(), 0.1)

    def _load_battles(self):
        """Load battle history from API."""
        def fetch():
            try:
                result = self.api_client.get_battles()
                Clock.schedule_once(lambda dt: self._display_battles(result), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: self._show_error(str(e)), 0)

        threading.Thread(target=fetch, daemon=True).start()

    def _display_battles(self, battles):
        """Display battle history."""
        self.content_container.clear_widgets()
        self.battles_data = battles

        # Scroll view
        scroll = ScrollView()
        content = BoxLayout(
            orientation='vertical',
            spacing=get_spacing(),
            padding=get_padding(),
            size_hint_y=None
        )
        content.bind(minimum_height=content.setter('height'))

        # Header with stats
        header = CardBox(
            orientation='vertical',
            size_hint_y=None,
            height=dp(120),
            spacing=dp(10)
        )

        title_box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40)
        )

        title = Label(
            text='Batalhas',
            font_size=scaled_font(22),
            bold=True,
            color=get_color_from_hex(COLORS['primary']),
            halign='left',
            valign='middle'
        )
        title.bind(size=lambda *x: setattr(title, 'text_size', (title.width, None)))
        title_box.add_widget(title)

        # New battle button
        new_battle_btn = PrimaryButton(
            text='+ Nova',
            size_hint_x=None,
            width=dp(100),
            height=dp(35),
            size_hint_y=None
        )
        new_battle_btn.bind(on_press=lambda x: self._new_battle())
        title_box.add_widget(new_battle_btn)

        header.add_widget(title_box)

        # Win rate stats
        if battles:
            wins = sum(1 for b in battles if b.get('result') == 'W')
            losses = sum(1 for b in battles if b.get('result') == 'L')
            total = len(battles)
            win_rate = (wins / total * 100) if total > 0 else 0

            stats_label = Label(
                text=f'Taxa de Vitória: {win_rate:.1f}% ({wins}V - {losses}D - {total - wins - losses}E)',
                font_size=scaled_font(14),
                color=get_color_from_hex(COLORS['text_secondary']),
                size_hint_y=None,
                height=dp(30),
                halign='center',
                valign='middle'
            )
            stats_label.bind(size=lambda *x: setattr(stats_label, 'text_size', (stats_label.width, None)))
            header.add_widget(stats_label)

        content.add_widget(header)

        # Battle cards
        if not battles:
            empty_label = Label(
                text='Nenhuma batalha registrada.\nRegistre suas batalhas para acompanhar seu progresso!',
                font_size=scaled_font(14),
                color=get_color_from_hex(COLORS['text_muted']),
                size_hint_y=None,
                height=dp(60),
                halign='center',
                valign='middle'
            )
            empty_label.bind(size=lambda *x: setattr(empty_label, 'text_size', (empty_label.width, None)))
            content.add_widget(empty_label)
        else:
            for battle in battles:
                battle_card = BattleCard(
                    battle_data=battle,
                    on_click=self._on_battle_click
                )
                content.add_widget(battle_card)

        scroll.add_widget(content)
        self.content_container.add_widget(scroll)

    def _show_error(self, error_msg):
        """Show error message."""
        self.content_container.clear_widgets()
        error = ErrorMessage(
            message=f'Erro ao carregar batalhas: {error_msg}',
            on_retry=self._load_battles
        )
        self.content_container.add_widget(error)

    def _on_battle_click(self, battle_data):
        """Handle battle card click."""
        # Navigate to battle detail or show analysis
        # TODO: Implement battle detail screen
        pass

    def _new_battle(self):
        """Open new battle form."""
        # TODO: Implement new battle form (simple popup or screen)
        # For now, just show a placeholder
        from kivy.uix.popup import Popup

        content = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=get_padding()
        )

        message = Label(
            text='Formulário de nova batalha\n(Em desenvolvimento)',
            font_size=scaled_font(14),
            color=get_color_from_hex(COLORS['text']),
            size_hint_y=None,
            height=dp(60),
            halign='center',
            valign='middle'
        )
        message.bind(size=lambda *x: setattr(message, 'text_size', (message.width, None)))
        content.add_widget(message)

        close_btn = SecondaryButton(text='Fechar')
        content.add_widget(close_btn)

        popup = Popup(
            title='Nova Batalha',
            content=content,
            size_hint=(0.8, None),
            height=dp(200)
        )

        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def on_enter(self):
        """Called when screen is displayed."""
        # Reload battles
        self._load_battles()
