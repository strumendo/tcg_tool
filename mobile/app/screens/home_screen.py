"""
Home screen - Welcome and quick actions.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.clock import Clock

from app.components import (
    ColoredBox, CardBox, PrimaryButton, LoadingSpinner,
    ErrorMessage, COLORS, get_color_from_hex
)
from app.utils.responsive import scaled_font, get_padding, get_spacing, is_cover_mode
from app.services.api_client import APIClient
import threading


class ActionCard(CardBox):
    """Quick action card widget."""

    def __init__(self, title, icon, description, on_press=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(8)
        self.size_hint_y = None
        self.height = dp(120)

        # Icon + Title
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(10)
        )

        icon_label = Label(
            text=icon,
            font_size=scaled_font(32),
            size_hint_x=None,
            width=dp(40)
        )
        header.add_widget(icon_label)

        title_label = Label(
            text=title,
            font_size=scaled_font(18),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            valign='middle'
        )
        title_label.bind(size=lambda *x: setattr(title_label, 'text_size', (title_label.width, None)))
        header.add_widget(title_label)

        self.add_widget(header)

        # Description
        desc_label = Label(
            text=description,
            font_size=scaled_font(14),
            color=get_color_from_hex(COLORS['text_secondary']),
            size_hint_y=None,
            height=dp(40),
            halign='left',
            valign='top'
        )
        desc_label.bind(size=lambda *x: setattr(desc_label, 'text_size', (desc_label.width, None)))
        self.add_widget(desc_label)

        # Make card clickable
        if on_press:
            from kivy.uix.behaviors import ButtonBehavior

            class ClickableCard(ButtonBehavior, CardBox):
                pass

            # This is a workaround - in real implementation, ActionCard should extend both
            self.bind(on_touch_down=lambda instance, touch: on_press() if self.collide_point(*touch.pos) else None)


class HomeScreen(Screen):
    """Home screen with welcome message and quick actions."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'home'
        self.api_client = APIClient()
        self.news_data = []

        # Main container
        main_layout = ColoredBox(
            orientation='vertical',
            bg_color=COLORS['background']
        )

        # Scroll view
        scroll = ScrollView()
        content = BoxLayout(
            orientation='vertical',
            spacing=get_spacing(),
            padding=get_padding(),
            size_hint_y=None
        )
        content.bind(minimum_height=content.setter('height'))

        # Welcome section
        welcome_card = CardBox(
            orientation='vertical',
            size_hint_y=None,
            height=dp(100)
        )

        welcome_title = Label(
            text='Bem-vindo ao TCG Tool',
            font_size=scaled_font(24),
            bold=True,
            color=get_color_from_hex(COLORS['primary']),
            size_hint_y=None,
            height=dp(40),
            halign='center',
            valign='middle'
        )
        welcome_title.bind(size=lambda *x: setattr(welcome_title, 'text_size', (welcome_title.width, None)))

        welcome_subtitle = Label(
            text='Analise decks, acompanhe o meta e melhore sua estratégia',
            font_size=scaled_font(14),
            color=get_color_from_hex(COLORS['text_secondary']),
            size_hint_y=None,
            height=dp(30),
            halign='center',
            valign='middle'
        )
        welcome_subtitle.bind(size=lambda *x: setattr(welcome_subtitle, 'text_size', (welcome_subtitle.width, None)))

        welcome_card.add_widget(welcome_title)
        welcome_card.add_widget(welcome_subtitle)
        content.add_widget(welcome_card)

        # Quick actions grid
        actions_label = Label(
            text='Ações Rápidas',
            font_size=scaled_font(18),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            size_hint_y=None,
            height=dp(40),
            halign='left',
            valign='middle'
        )
        actions_label.bind(size=lambda *x: setattr(actions_label, 'text_size', (actions_label.width, None)))
        content.add_widget(actions_label)

        # Determine columns based on screen mode
        cols = 1 if is_cover_mode() else 2

        self.actions_grid = GridLayout(
            cols=cols,
            spacing=get_spacing(),
            size_hint_y=None,
            row_default_height=dp(130),
            row_force_default=True
        )
        self.actions_grid.bind(minimum_height=self.actions_grid.setter('height'))

        # Action cards
        actions = [
            {
                'title': 'Ver Meta Decks',
                'icon': '📊',
                'description': 'Explore os decks do meta competitivo',
                'action': lambda: self.manager.current == 'meta' if self.manager else None
            },
            {
                'title': 'Meus Decks',
                'icon': '🎴',
                'description': 'Gerencie sua coleção de decks',
                'action': lambda: self.manager.current == 'my_decks' if self.manager else None
            },
            {
                'title': 'Importar Deck',
                'icon': '📥',
                'description': 'Importe do TCG Live ou arquivo',
                'action': lambda: self.manager.current == 'import' if self.manager else None
            },
            {
                'title': 'Chat IA',
                'icon': '💬',
                'description': 'Converse com o assistente IA',
                'action': lambda: self.manager.current == 'chat' if self.manager else None
            },
        ]

        for action in actions:
            card = ActionCard(
                title=action['title'],
                icon=action['icon'],
                description=action['description'],
                on_press=action['action']
            )
            self.actions_grid.add_widget(card)

        content.add_widget(self.actions_grid)

        # News section
        news_label = Label(
            text='Notícias Recentes',
            font_size=scaled_font(18),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            size_hint_y=None,
            height=dp(40),
            halign='left',
            valign='middle'
        )
        news_label.bind(size=lambda *x: setattr(news_label, 'text_size', (news_label.width, None)))
        content.add_widget(news_label)

        # News container (will be populated)
        self.news_container = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )
        self.news_container.add_widget(LoadingSpinner())
        content.add_widget(self.news_container)

        scroll.add_widget(content)
        main_layout.add_widget(scroll)
        self.add_widget(main_layout)

        # Load news on screen entry
        Clock.schedule_once(lambda dt: self._load_news(), 0.5)

    def _load_news(self):
        """Load recent news from API."""
        def fetch():
            try:
                # Fetch news from API
                result = self.api_client.get_news(limit=3)
                Clock.schedule_once(lambda dt: self._display_news(result), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: self._show_news_error(str(e)), 0)

        threading.Thread(target=fetch, daemon=True).start()

    def _display_news(self, news_list):
        """Display news items."""
        self.news_container.clear_widgets()

        if not news_list:
            no_news = Label(
                text='Nenhuma notícia disponível',
                font_size=scaled_font(14),
                color=get_color_from_hex(COLORS['text_muted']),
                size_hint_y=None,
                height=dp(40)
            )
            self.news_container.add_widget(no_news)
            return

        self.news_container.height = len(news_list) * dp(80) + (len(news_list) - 1) * dp(10)

        for item in news_list[:3]:  # Show max 3 items
            news_card = CardBox(
                orientation='vertical',
                size_hint_y=None,
                height=dp(80)
            )

            title = Label(
                text=item.get('title', 'Sem título'),
                font_size=scaled_font(14),
                bold=True,
                color=get_color_from_hex(COLORS['text']),
                size_hint_y=None,
                height=dp(30),
                halign='left',
                valign='middle',
                shorten=True,
                shorten_from='right'
            )
            title.bind(size=lambda *x: setattr(title, 'text_size', (title.width, None)))

            date = Label(
                text=item.get('date', ''),
                font_size=scaled_font(12),
                color=get_color_from_hex(COLORS['text_secondary']),
                size_hint_y=None,
                height=dp(20),
                halign='left',
                valign='middle'
            )
            date.bind(size=lambda *x: setattr(date, 'text_size', (date.width, None)))

            news_card.add_widget(title)
            news_card.add_widget(date)
            self.news_container.add_widget(news_card)

    def _show_news_error(self, error_msg):
        """Show error message for news loading."""
        self.news_container.clear_widgets()
        error = Label(
            text='Erro ao carregar notícias',
            font_size=scaled_font(14),
            color=get_color_from_hex(COLORS['text_muted']),
            size_hint_y=None,
            height=dp(40)
        )
        self.news_container.add_widget(error)

    def on_enter(self):
        """Called when screen is displayed."""
        # Reload news if needed
        pass
