"""
My Decks screen - Manage user's personal deck collection.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.clock import Clock

from app.components import (
    ColoredBox, CardBox, PrimaryButton, SecondaryButton,
    LoadingSpinner, ErrorMessage, COLORS, get_color_from_hex
)
from app.utils.responsive import scaled_font, get_padding, get_spacing
from app.services.api_client import APIClient
import threading


class UserDeckCard(CardBox):
    """User deck card widget."""

    def __init__(self, deck_data, on_click=None, on_delete=None, **kwargs):
        super().__init__(**kwargs)
        self.deck_data = deck_data
        self.orientation = 'horizontal'
        self.spacing = dp(10)
        self.size_hint_y = None
        self.height = dp(90)

        # Deck info
        info_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(5)
        )

        # Deck name
        name_label = Label(
            text=deck_data.get('name', 'Deck sem nome'),
            font_size=scaled_font(16),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            size_hint_y=None,
            height=dp(30),
            halign='left',
            valign='middle'
        )
        name_label.bind(size=lambda *x: setattr(name_label, 'text_size', (name_label.width, None)))
        info_layout.add_widget(name_label)

        # Archetype and card count
        archetype = deck_data.get('archetype', 'Desconhecido')
        card_count = deck_data.get('card_count', 0)
        details_label = Label(
            text=f'{archetype} • {card_count} cartas',
            font_size=scaled_font(13),
            color=get_color_from_hex(COLORS['text_secondary']),
            size_hint_y=None,
            height=dp(25),
            halign='left',
            valign='middle'
        )
        details_label.bind(size=lambda *x: setattr(details_label, 'text_size', (details_label.width, None)))
        info_layout.add_widget(details_label)

        # Validity badge
        is_valid = deck_data.get('is_valid', True)
        validity_text = '✅ Válido' if is_valid else '⚠️ Inválido'
        validity_color = COLORS['success'] if is_valid else COLORS['danger']
        validity_label = Label(
            text=validity_text,
            font_size=scaled_font(12),
            color=get_color_from_hex(validity_color),
            size_hint_y=None,
            height=dp(20),
            halign='left',
            valign='middle'
        )
        validity_label.bind(size=lambda *x: setattr(validity_label, 'text_size', (validity_label.width, None)))
        info_layout.add_widget(validity_label)

        self.add_widget(info_layout)

        # Delete button
        if on_delete:
            delete_btn = SecondaryButton(
                text='🗑️',
                size_hint_x=None,
                width=dp(50),
                background_color=get_color_from_hex(COLORS['danger'])
            )
            delete_btn.bind(on_press=lambda x: on_delete(deck_data))
            self.add_widget(delete_btn)

        # Make card clickable
        if on_click:
            self.bind(on_touch_down=lambda instance, touch: on_click(deck_data) if self.collide_point(*touch.pos) and not delete_btn.collide_point(*touch.pos) else None)


class MyDecksScreen(Screen):
    """Screen for managing user's personal decks."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'my_decks'
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
        Clock.schedule_once(lambda dt: self._load_decks(), 0.1)

    def _load_decks(self):
        """Load user decks from API."""
        def fetch():
            try:
                result = self.api_client.get_user_decks()
                Clock.schedule_once(lambda dt: self._display_decks(result), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: self._show_error(str(e)), 0)

        threading.Thread(target=fetch, daemon=True).start()

    def _display_decks(self, decks):
        """Display user decks."""
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

        # Header
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )

        title = Label(
            text='Meus Decks',
            font_size=scaled_font(22),
            bold=True,
            color=get_color_from_hex(COLORS['primary']),
            halign='left',
            valign='middle'
        )
        title.bind(size=lambda *x: setattr(title, 'text_size', (title.width, None)))
        header.add_widget(title)

        # Add deck button
        add_btn = PrimaryButton(
            text='+ Importar',
            size_hint_x=None,
            width=dp(130),
            height=dp(40),
            size_hint_y=None
        )
        add_btn.bind(on_press=lambda x: self._go_to_import())
        header.add_widget(add_btn)

        content.add_widget(header)

        # Deck cards
        if not decks:
            empty_label = Label(
                text='Você ainda não tem decks.\nImporte um deck para começar!',
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
            for deck in decks:
                deck_card = UserDeckCard(
                    deck_data=deck,
                    on_click=self._on_deck_click,
                    on_delete=self._on_deck_delete
                )
                content.add_widget(deck_card)

        scroll.add_widget(content)
        self.content_container.add_widget(scroll)

    def _show_error(self, error_msg):
        """Show error message."""
        self.content_container.clear_widgets()
        error = ErrorMessage(
            message=f'Erro ao carregar decks: {error_msg}',
            on_retry=self._load_decks
        )
        self.content_container.add_widget(error)

    def _on_deck_click(self, deck_data):
        """Handle deck card click."""
        # Navigate to deck detail screen
        if self.manager:
            # TODO: Create user deck detail screen
            pass

    def _on_deck_delete(self, deck_data):
        """Handle deck deletion with confirmation."""
        # Create confirmation popup
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=get_padding()
        )

        message = Label(
            text=f'Deseja excluir o deck "{deck_data.get("name", "Deck")}"?',
            font_size=scaled_font(14),
            color=get_color_from_hex(COLORS['text']),
            size_hint_y=None,
            height=dp(60),
            halign='center',
            valign='middle'
        )
        message.bind(size=lambda *x: setattr(message, 'text_size', (message.width, None)))
        content.add_widget(message)

        buttons = BoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )

        cancel_btn = SecondaryButton(text='Cancelar')
        confirm_btn = PrimaryButton(
            text='Excluir',
            background_color=get_color_from_hex(COLORS['danger'])
        )

        buttons.add_widget(cancel_btn)
        buttons.add_widget(confirm_btn)
        content.add_widget(buttons)

        popup = Popup(
            title='Confirmar Exclusão',
            content=content,
            size_hint=(0.8, None),
            height=dp(200)
        )

        cancel_btn.bind(on_press=popup.dismiss)
        confirm_btn.bind(on_press=lambda x: self._delete_deck(deck_data, popup))

        popup.open()

    def _delete_deck(self, deck_data, popup):
        """Delete deck via API."""
        popup.dismiss()

        def delete():
            try:
                deck_id = deck_data.get('id')
                self.api_client.delete_deck(deck_id)
                Clock.schedule_once(lambda dt: self._load_decks(), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: self._show_error(str(e)), 0)

        threading.Thread(target=delete, daemon=True).start()

    def _go_to_import(self):
        """Navigate to import screen."""
        if self.manager:
            self.manager.current = 'import'

    def on_enter(self):
        """Called when screen is displayed."""
        # Reload decks
        self._load_decks()
