"""
Match Analysis Screen - AI-powered match video and transcription analysis

Features:
- Input YouTube URLs for processing
- Paste match transcriptions
- View identified cards and play sequences
- Get AI-generated insights
- History of analyzed matches
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
from kivy.uix.screenmanager import Screen
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.clock import Clock
from kivy.properties import StringProperty

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.match_analysis import (
    MatchAnalysisService,
    MatchData,
    MatchSource,
    ProcessingStatus
)


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
    'ai_purple': '#9c27b0',
}


class MatchAnalysisScreen(Screen):
    """Screen for AI-powered match analysis."""

    lang = StringProperty("en")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.analysis_service = MatchAnalysisService()
        self.current_tab = 'youtube'
        self._build_ui()

    def _build_ui(self):
        """Build the analysis screen UI."""
        main_layout = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(10))

        with main_layout.canvas.before:
            Color(*get_color_from_hex(COLORS['background']))
            self._bg_rect = Rectangle(pos=main_layout.pos, size=main_layout.size)
        main_layout.bind(pos=self._update_bg, size=self._update_bg)

        # Header
        header = self._create_header()
        main_layout.add_widget(header)

        # AI Badge
        ai_badge = self._create_ai_badge()
        main_layout.add_widget(ai_badge)

        # Tab buttons
        tabs = self._create_tabs()
        main_layout.add_widget(tabs)

        # Input area (changes based on tab)
        self.input_area = BoxLayout(orientation='vertical', size_hint_y=0.4)
        main_layout.add_widget(self.input_area)

        # Results/History section
        results_label = Label(
            text='Analysis Results' if self.lang == 'en' else 'Resultados da Análise',
            font_size=sp(14),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            size_hint_y=None,
            height=dp(30),
            halign='left',
            valign='middle'
        )
        results_label.bind(size=results_label.setter('text_size'))
        main_layout.add_widget(results_label)

        # Results scroll
        scroll = ScrollView(size_hint_y=0.4)
        self.results_grid = GridLayout(
            cols=1,
            spacing=dp(8),
            size_hint_y=None,
            padding=[0, dp(4)]
        )
        self.results_grid.bind(minimum_height=self.results_grid.setter('height'))
        scroll.add_widget(self.results_grid)
        main_layout.add_widget(scroll)

        self.add_widget(main_layout)

        # Initialize with YouTube tab
        self._show_youtube_input()

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
            text='Match Analysis' if self.lang == 'en' else 'Análise de Partidas',
            font_size=sp(18),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        header.add_widget(title)

        return header

    def _create_ai_badge(self):
        """Create AI feature badge."""
        badge = BoxLayout(size_hint_y=None, height=dp(35), padding=[dp(8), dp(4)])

        with badge.canvas.before:
            Color(*get_color_from_hex(COLORS['ai_purple']))
            badge._bg = RoundedRectangle(pos=badge.pos, size=badge.size, radius=[dp(6)])
        badge.bind(
            pos=lambda *a: setattr(badge._bg, 'pos', badge.pos),
            size=lambda *a: setattr(badge._bg, 'size', badge.size)
        )

        text = '🤖 AI-Powered Analysis' if self.lang == 'en' else '🤖 Análise com IA'
        label = Label(
            text=text,
            font_size=sp(12),
            bold=True,
            color=(1, 1, 1, 1)
        )
        badge.add_widget(label)

        return badge

    def _create_tabs(self):
        """Create tab buttons."""
        tabs = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))

        self.youtube_tab = Button(
            text='YouTube',
            background_color=get_color_from_hex(COLORS['primary']),
            font_size=sp(13)
        )
        self.youtube_tab.bind(on_release=lambda x: self._switch_tab('youtube'))
        tabs.add_widget(self.youtube_tab)

        self.transcription_tab = Button(
            text='Transcription' if self.lang == 'en' else 'Transcrição',
            background_color=get_color_from_hex(COLORS['text_muted']),
            font_size=sp(13)
        )
        self.transcription_tab.bind(on_release=lambda x: self._switch_tab('transcription'))
        tabs.add_widget(self.transcription_tab)

        self.history_tab = Button(
            text='History' if self.lang == 'en' else 'Histórico',
            background_color=get_color_from_hex(COLORS['text_muted']),
            font_size=sp(13)
        )
        self.history_tab.bind(on_release=lambda x: self._switch_tab('history'))
        tabs.add_widget(self.history_tab)

        return tabs

    # =========================================================================
    # TAB SWITCHING
    # =========================================================================

    def _switch_tab(self, tab):
        """Switch between tabs."""
        self.current_tab = tab

        # Update tab button colors
        self.youtube_tab.background_color = get_color_from_hex(
            COLORS['primary'] if tab == 'youtube' else COLORS['text_muted']
        )
        self.transcription_tab.background_color = get_color_from_hex(
            COLORS['primary'] if tab == 'transcription' else COLORS['text_muted']
        )
        self.history_tab.background_color = get_color_from_hex(
            COLORS['primary'] if tab == 'history' else COLORS['text_muted']
        )

        # Update input area
        self.input_area.clear_widgets()
        if tab == 'youtube':
            self._show_youtube_input()
        elif tab == 'transcription':
            self._show_transcription_input()
        else:
            self._show_history()

    def _show_youtube_input(self):
        """Show YouTube URL input."""
        container = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(8))

        # Instructions
        instructions = Label(
            text='Paste a YouTube URL of a Pokemon TCG match:' if self.lang == 'en' else
                 'Cole a URL de um vídeo de partida Pokemon TCG:',
            font_size=sp(13),
            color=get_color_from_hex(COLORS['text_secondary']),
            size_hint_y=None,
            height=dp(25),
            halign='left'
        )
        instructions.bind(size=instructions.setter('text_size'))
        container.add_widget(instructions)

        # URL input
        input_box = BoxLayout(padding=dp(2), size_hint_y=None, height=dp(45))
        with input_box.canvas.before:
            Color(*get_color_from_hex(COLORS['surface']))
            input_box._bg = RoundedRectangle(pos=input_box.pos, size=input_box.size, radius=[dp(6)])
        input_box.bind(
            pos=lambda *a: setattr(input_box._bg, 'pos', input_box.pos),
            size=lambda *a: setattr(input_box._bg, 'size', input_box.size)
        )

        self.url_input = TextInput(
            hint_text='https://youtube.com/watch?v=...',
            multiline=False,
            font_size=sp(13),
            background_color=(0, 0, 0, 0),
            foreground_color=get_color_from_hex(COLORS['text']),
            padding=[dp(10), dp(10)]
        )
        input_box.add_widget(self.url_input)
        container.add_widget(input_box)

        # Process button
        process_btn = Button(
            text='Analyze Video' if self.lang == 'en' else 'Analisar Vídeo',
            background_color=get_color_from_hex(COLORS['secondary']),
            font_size=sp(14),
            bold=True,
            size_hint_y=None,
            height=dp(45)
        )
        process_btn.bind(on_release=self._process_youtube)
        container.add_widget(process_btn)

        # Tips
        tips = Label(
            text='💡 Tip: Works best with TCG Live streams and tournament VODs' if self.lang == 'en' else
                 '💡 Dica: Funciona melhor com streams do TCG Live e VODs de torneios',
            font_size=sp(11),
            color=get_color_from_hex(COLORS['text_muted']),
            size_hint_y=None,
            height=dp(25),
            halign='center'
        )
        container.add_widget(tips)

        container.add_widget(BoxLayout())  # Spacer

        self.input_area.add_widget(container)

    def _show_transcription_input(self):
        """Show transcription text input."""
        container = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(8))

        # Instructions
        instructions = Label(
            text='Paste a match transcription or play-by-play:' if self.lang == 'en' else
                 'Cole uma transcrição ou resumo da partida:',
            font_size=sp(13),
            color=get_color_from_hex(COLORS['text_secondary']),
            size_hint_y=None,
            height=dp(25),
            halign='left'
        )
        instructions.bind(size=instructions.setter('text_size'))
        container.add_widget(instructions)

        # Text input
        input_box = BoxLayout(padding=dp(2))
        with input_box.canvas.before:
            Color(*get_color_from_hex(COLORS['surface']))
            input_box._bg = RoundedRectangle(pos=input_box.pos, size=input_box.size, radius=[dp(6)])
        input_box.bind(
            pos=lambda *a: setattr(input_box._bg, 'pos', input_box.pos),
            size=lambda *a: setattr(input_box._bg, 'size', input_box.size)
        )

        self.transcription_input = TextInput(
            hint_text='Turn 1: I start with Charmander, attach Fire Energy...\nTurn 2: Play Rare Candy, evolve to Charizard ex...',
            multiline=True,
            font_size=sp(12),
            background_color=(0, 0, 0, 0),
            foreground_color=get_color_from_hex(COLORS['text']),
            padding=[dp(10), dp(10)]
        )
        input_box.add_widget(self.transcription_input)
        container.add_widget(input_box)

        # Process button
        process_btn = Button(
            text='Analyze Transcription' if self.lang == 'en' else 'Analisar Transcrição',
            background_color=get_color_from_hex(COLORS['ai_purple']),
            font_size=sp(14),
            bold=True,
            size_hint_y=None,
            height=dp(45)
        )
        process_btn.bind(on_release=self._process_transcription)
        container.add_widget(process_btn)

        self.input_area.add_widget(container)

    def _show_history(self):
        """Show analysis history."""
        container = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(8))

        matches = self.analysis_service.get_all_matches()

        if not matches:
            empty = Label(
                text='No analyzed matches yet.\nStart by processing a video or transcription!' if self.lang == 'en' else
                     'Nenhuma partida analisada ainda.\nComece processando um vídeo ou transcrição!',
                font_size=sp(13),
                color=get_color_from_hex(COLORS['text_secondary']),
                halign='center'
            )
            container.add_widget(empty)
        else:
            scroll = ScrollView()
            grid = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
            grid.bind(minimum_height=grid.setter('height'))

            for match in matches[:10]:  # Show last 10
                card = self._create_match_history_card(match)
                grid.add_widget(card)

            scroll.add_widget(grid)
            container.add_widget(scroll)

        self.input_area.add_widget(container)

    # =========================================================================
    # PROCESSING
    # =========================================================================

    def on_enter(self):
        """Called when screen is displayed."""
        self._refresh_results()

    def _process_youtube(self, *args):
        """Process YouTube URL."""
        url = self.url_input.text.strip()
        if not url:
            self._show_message(
                'Error' if self.lang == 'en' else 'Erro',
                'Please enter a YouTube URL' if self.lang == 'en' else 'Por favor, insira uma URL do YouTube'
            )
            return

        # Process the URL
        match = self.analysis_service.process_youtube_url(url)

        if match.status == ProcessingStatus.FAILED:
            self._show_message(
                'Error' if self.lang == 'en' else 'Erro',
                match.error_message
            )
        else:
            self._show_match_result(match)
            self.url_input.text = ''
            self._refresh_results()

    def _process_transcription(self, *args):
        """Process transcription text."""
        text = self.transcription_input.text.strip()
        if not text:
            self._show_message(
                'Error' if self.lang == 'en' else 'Erro',
                'Please enter a transcription' if self.lang == 'en' else 'Por favor, insira uma transcrição'
            )
            return

        # Process the transcription
        match = self.analysis_service.process_transcription(text)
        self._show_match_result(match)
        self.transcription_input.text = ''
        self._refresh_results()

    def _refresh_results(self):
        """Refresh results display."""
        self.results_grid.clear_widgets()

        matches = self.analysis_service.get_all_matches()[:5]  # Last 5

        if not matches:
            empty = Label(
                text='No results yet' if self.lang == 'en' else 'Sem resultados ainda',
                font_size=sp(13),
                color=get_color_from_hex(COLORS['text_muted']),
                size_hint_y=None,
                height=dp(40)
            )
            self.results_grid.add_widget(empty)
            return

        for match in matches:
            card = self._create_result_card(match)
            self.results_grid.add_widget(card)

    # =========================================================================
    # UI COMPONENTS
    # =========================================================================

    def _create_result_card(self, match: MatchData):
        """Create a result card for a processed match."""
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(100),
            padding=dp(10),
            spacing=dp(4)
        )

        with card.canvas.before:
            Color(*get_color_from_hex(COLORS['surface']))
            card._bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(6)])
        card.bind(
            pos=lambda *a, c=card: setattr(c._bg, 'pos', c.pos),
            size=lambda *a, c=card: setattr(c._bg, 'size', c.size)
        )

        # Header row
        header = BoxLayout(size_hint_y=None, height=dp(25))

        # Source badge
        source_colors = {
            MatchSource.YOUTUBE: COLORS['danger'],
            MatchSource.TRANSCRIPTION: COLORS['ai_purple'],
            MatchSource.VIDEO_FILE: COLORS['secondary'],
        }
        source_text = match.source.value.title()

        source_badge = Label(
            text=source_text,
            font_size=sp(10),
            bold=True,
            color=get_color_from_hex(source_colors.get(match.source, COLORS['text_muted'])),
            size_hint_x=None,
            width=dp(80)
        )
        header.add_widget(source_badge)

        # Title
        title = Label(
            text=match.title[:30] + ('...' if len(match.title) > 30 else ''),
            font_size=sp(13),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            halign='left'
        )
        title.bind(size=title.setter('text_size'))
        header.add_widget(title)

        card.add_widget(header)

        # Deck detection
        if match.player1_deck and match.player1_deck != "Unknown":
            deck_label = Label(
                text=f'🃏 Deck: {match.player1_deck}',
                font_size=sp(11),
                color=get_color_from_hex(COLORS['primary']),
                size_hint_y=None,
                height=dp(20),
                halign='left'
            )
            deck_label.bind(size=deck_label.setter('text_size'))
            card.add_widget(deck_label)

        # Insights preview
        if match.insights:
            insight_text = match.insights[0][:50] + ('...' if len(match.insights[0]) > 50 else '')
            insight_label = Label(
                text=f'💡 {insight_text}',
                font_size=sp(11),
                color=get_color_from_hex(COLORS['text_secondary']),
                size_hint_y=None,
                height=dp(20),
                halign='left'
            )
            insight_label.bind(size=insight_label.setter('text_size'))
            card.add_widget(insight_label)

        # Cards count
        if match.cards_identified:
            cards_label = Label(
                text=f'🎴 {len(match.cards_identified)} cards identified',
                font_size=sp(10),
                color=get_color_from_hex(COLORS['text_muted']),
                size_hint_y=None,
                height=dp(18),
                halign='left'
            )
            cards_label.bind(size=cards_label.setter('text_size'))
            card.add_widget(cards_label)

        return card

    def _create_match_history_card(self, match: MatchData):
        """Create a history card for a match."""
        card = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            padding=dp(10),
            spacing=dp(8)
        )

        with card.canvas.before:
            Color(*get_color_from_hex(COLORS['surface']))
            card._bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(6)])
        card.bind(
            pos=lambda *a, c=card: setattr(c._bg, 'pos', c.pos),
            size=lambda *a, c=card: setattr(c._bg, 'size', c.size)
        )

        # Info
        info = BoxLayout(orientation='vertical', spacing=dp(2))

        title = Label(
            text=match.title[:25] + ('...' if len(match.title) > 25 else ''),
            font_size=sp(13),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            halign='left'
        )
        title.bind(size=title.setter('text_size'))
        info.add_widget(title)

        meta = Label(
            text=f'{match.source.value} • {len(match.cards_identified)} cards',
            font_size=sp(10),
            color=get_color_from_hex(COLORS['text_muted']),
            halign='left'
        )
        meta.bind(size=meta.setter('text_size'))
        info.add_widget(meta)

        card.add_widget(info)

        # View button
        view_btn = Button(
            text='View',
            size_hint_x=None,
            width=dp(60),
            background_color=get_color_from_hex(COLORS['secondary']),
            font_size=sp(12)
        )
        view_btn.bind(on_release=lambda x, m=match: self._show_match_result(m))
        card.add_widget(view_btn)

        # Delete button
        del_btn = Button(
            text='×',
            size_hint_x=None,
            width=dp(40),
            background_color=get_color_from_hex(COLORS['danger']),
            font_size=sp(16)
        )
        del_btn.bind(on_release=lambda x, m=match: self._delete_match(m))
        card.add_widget(del_btn)

        return card

    def _show_match_result(self, match: MatchData):
        """Show detailed match result popup."""
        content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))

        # Title
        content.add_widget(Label(
            text=match.title,
            font_size=sp(16),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            size_hint_y=None,
            height=dp(30)
        ))

        # Scroll content
        scroll = ScrollView(size_hint_y=0.7)
        details = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
        details.bind(minimum_height=details.setter('height'))

        # Deck
        if match.player1_deck:
            details.add_widget(Label(
                text=f'🃏 Detected Deck: {match.player1_deck}',
                font_size=sp(13),
                color=get_color_from_hex(COLORS['primary']),
                size_hint_y=None,
                height=dp(25)
            ))

        # Cards identified
        if match.cards_identified:
            details.add_widget(Label(
                text=f'🎴 Cards Identified ({len(match.cards_identified)}):',
                font_size=sp(12),
                bold=True,
                color=get_color_from_hex(COLORS['text']),
                size_hint_y=None,
                height=dp(25)
            ))
            cards_text = ', '.join(match.cards_identified[:15])
            if len(match.cards_identified) > 15:
                cards_text += f' (+{len(match.cards_identified) - 15} more)'
            details.add_widget(Label(
                text=cards_text,
                font_size=sp(11),
                color=get_color_from_hex(COLORS['text_secondary']),
                size_hint_y=None,
                height=dp(40),
                text_size=(dp(280), None)
            ))

        # Insights
        if match.insights:
            details.add_widget(Label(
                text='💡 Insights:',
                font_size=sp(12),
                bold=True,
                color=get_color_from_hex(COLORS['text']),
                size_hint_y=None,
                height=dp(25)
            ))
            for insight in match.insights:
                details.add_widget(Label(
                    text=f'• {insight}',
                    font_size=sp(11),
                    color=get_color_from_hex(COLORS['text_secondary']),
                    size_hint_y=None,
                    height=dp(22)
                ))

        scroll.add_widget(details)
        content.add_widget(scroll)

        # Close button
        close_btn = Button(
            text='Close' if self.lang == 'en' else 'Fechar',
            size_hint_y=None,
            height=dp(45),
            background_color=get_color_from_hex(COLORS['primary'])
        )

        popup = Popup(
            title='Match Analysis' if self.lang == 'en' else 'Análise da Partida',
            content=content,
            size_hint=(0.9, 0.8)
        )
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()

    def _delete_match(self, match: MatchData):
        """Delete a match from history."""
        self.analysis_service.delete_match(match.id)
        self._switch_tab('history')
        self._refresh_results()

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
            size_hint=(0.8, 0.35)
        )
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()

    def _go_back(self, *args):
        """Navigate back."""
        if self.manager:
            self.manager.transition.direction = 'right'
            self.manager.current = 'home'
