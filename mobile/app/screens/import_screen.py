"""
Import Deck screen - Import decks from PTCGO/TCG Live format.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from kivy.clock import Clock

from app.components import (
    ColoredBox, CardBox, PrimaryButton, SecondaryButton,
    LoadingSpinner, COLORS, get_color_from_hex
)
from app.utils.responsive import scaled_font, get_padding, get_spacing
from app.services.api_client import APIClient
import threading


class ImportScreen(Screen):
    """Screen for importing decks from text format."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'import'
        self.api_client = APIClient()

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

        # Title
        title = Label(
            text='Importar Deck',
            font_size=scaled_font(24),
            bold=True,
            color=get_color_from_hex(COLORS['primary']),
            size_hint_y=None,
            height=dp(50),
            halign='center',
            valign='middle'
        )
        title.bind(size=lambda *x: setattr(title, 'text_size', (title.width, None)))
        content.add_widget(title)

        # Instructions card
        instructions = CardBox(
            orientation='vertical',
            size_hint_y=None,
            height=dp(150)
        )

        inst_title = Label(
            text='Como importar:',
            font_size=scaled_font(16),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            size_hint_y=None,
            height=dp(30),
            halign='left',
            valign='middle'
        )
        inst_title.bind(size=lambda *x: setattr(inst_title, 'text_size', (inst_title.width, None)))
        instructions.add_widget(inst_title)

        inst_text = Label(
            text='1. Abra TCG Live ou PTCGO\n'
                 '2. Exporte seu deck (copie)\n'
                 '3. Cole o texto abaixo\n'
                 '4. Dê um nome ao deck\n'
                 '5. Clique em "Importar"',
            font_size=scaled_font(13),
            color=get_color_from_hex(COLORS['text_secondary']),
            size_hint_y=None,
            height=dp(100),
            halign='left',
            valign='top'
        )
        inst_text.bind(size=lambda *x: setattr(inst_text, 'text_size', (inst_text.width, None)))
        instructions.add_widget(inst_text)

        content.add_widget(instructions)

        # Deck name input
        name_label = Label(
            text='Nome do Deck:',
            font_size=scaled_font(14),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            size_hint_y=None,
            height=dp(30),
            halign='left',
            valign='middle'
        )
        name_label.bind(size=lambda *x: setattr(name_label, 'text_size', (name_label.width, None)))
        content.add_widget(name_label)

        self.name_input = TextInput(
            hint_text='Ex: Charizard ex / Pidgeot ex',
            font_size=scaled_font(14),
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            padding=[dp(10), dp(15)]
        )
        content.add_widget(self.name_input)

        # Deck text input
        deck_label = Label(
            text='Cole o deck aqui:',
            font_size=scaled_font(14),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            size_hint_y=None,
            height=dp(30),
            halign='left',
            valign='middle'
        )
        deck_label.bind(size=lambda *x: setattr(deck_label, 'text_size', (deck_label.width, None)))
        content.add_widget(deck_label)

        self.deck_input = TextInput(
            hint_text='Pokémon: 15\n2 Charizard ex OBF 125\n...',
            font_size=scaled_font(12),
            multiline=True,
            size_hint_y=None,
            height=dp(300),
            padding=[dp(10), dp(10)]
        )
        content.add_widget(self.deck_input)

        # Format example
        example_label = Label(
            text='Formato esperado: "2 Charizard ex OBF 125"',
            font_size=scaled_font(11),
            color=get_color_from_hex(COLORS['text_muted']),
            italic=True,
            size_hint_y=None,
            height=dp(25),
            halign='center',
            valign='middle'
        )
        example_label.bind(size=lambda *x: setattr(example_label, 'text_size', (example_label.width, None)))
        content.add_widget(example_label)

        # Error/success message container
        self.message_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(0)
        )
        content.add_widget(self.message_container)

        # Buttons
        buttons = BoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(60)
        )

        cancel_btn = SecondaryButton(text='Cancelar')
        cancel_btn.bind(on_press=lambda x: self._go_back())
        buttons.add_widget(cancel_btn)

        self.import_btn = PrimaryButton(text='Importar')
        self.import_btn.bind(on_press=lambda x: self._import_deck())
        buttons.add_widget(self.import_btn)

        content.add_widget(buttons)

        scroll.add_widget(content)
        main_layout.add_widget(scroll)
        self.add_widget(main_layout)

    def _import_deck(self):
        """Import deck via API."""
        deck_name = self.name_input.text.strip()
        deck_text = self.deck_input.text.strip()

        # Validation
        if not deck_name:
            self._show_message('Por favor, dê um nome ao deck', 'error')
            return

        if not deck_text:
            self._show_message('Por favor, cole o deck', 'error')
            return

        # Show loading
        self.import_btn.disabled = True
        self.import_btn.text = 'Importando...'
        self._clear_message()

        def import_deck():
            try:
                result = self.api_client.import_deck(
                    name=deck_name,
                    deck_text=deck_text
                )
                Clock.schedule_once(lambda dt: self._import_success(result), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: self._import_error(str(e)), 0)

        threading.Thread(target=import_deck, daemon=True).start()

    def _import_success(self, result):
        """Handle successful import."""
        self.import_btn.disabled = False
        self.import_btn.text = 'Importar'

        # Show success message
        self._show_message('✅ Deck importado com sucesso!', 'success')

        # Clear inputs
        self.name_input.text = ''
        self.deck_input.text = ''

        # Navigate to my decks after delay
        Clock.schedule_once(lambda dt: self._go_to_my_decks(), 1.5)

    def _import_error(self, error_msg):
        """Handle import error."""
        self.import_btn.disabled = False
        self.import_btn.text = 'Importar'

        # Show error message
        self._show_message(f'❌ Erro: {error_msg}', 'error')

    def _show_message(self, text, msg_type='info'):
        """Show message to user."""
        self._clear_message()

        color = COLORS['success'] if msg_type == 'success' else COLORS['danger'] if msg_type == 'error' else COLORS['secondary']

        msg_label = Label(
            text=text,
            font_size=scaled_font(14),
            color=get_color_from_hex(color),
            size_hint_y=None,
            height=dp(40),
            halign='center',
            valign='middle'
        )
        msg_label.bind(size=lambda *x: setattr(msg_label, 'text_size', (msg_label.width, None)))

        self.message_container.clear_widgets()
        self.message_container.add_widget(msg_label)
        self.message_container.height = dp(50)

    def _clear_message(self):
        """Clear message container."""
        self.message_container.clear_widgets()
        self.message_container.height = dp(0)

    def _go_back(self):
        """Navigate back."""
        if self.manager:
            self.manager.current = 'my_decks'

    def _go_to_my_decks(self):
        """Navigate to my decks screen."""
        if self.manager:
            self.manager.current = 'my_decks'

    def on_enter(self):
        """Called when screen is displayed."""
        # Clear any previous messages
        self._clear_message()
