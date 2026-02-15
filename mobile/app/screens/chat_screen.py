"""
Chat screen - AI assistant chat interface.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.clock import Clock

from app.components import (
    ColoredBox, CardBox, PrimaryButton, OutlineButton,
    LoadingSpinner, COLORS, get_color_from_hex
)
from app.utils.responsive import scaled_font, get_padding, get_spacing, is_cover_mode
from app.services.api_client import APIClient
import threading


class MessageBubble(BoxLayout):
    """Chat message bubble widget."""

    def __init__(self, message, is_user=False, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.spacing = dp(5)
        self.padding = [dp(10), dp(5)]

        # Determine alignment
        if is_user:
            # User message on right
            self.add_widget(BoxLayout(size_hint_x=0.2))  # Spacer
            bubble = self._create_bubble(message, COLORS['secondary'], COLORS['nav_text'])
            self.add_widget(bubble)
        else:
            # AI message on left
            bubble = self._create_bubble(message, COLORS['surface'], COLORS['text'])
            self.add_widget(bubble)
            self.add_widget(BoxLayout(size_hint_x=0.2))  # Spacer

        # Calculate height based on content
        self.height = self._calculate_height(message)

    def _create_bubble(self, text, bg_color, text_color):
        """Create message bubble."""
        bubble = CardBox(
            bg_color=bg_color,
            size_hint_x=0.8
        )

        message_label = Label(
            text=text,
            font_size=scaled_font(14),
            color=get_color_from_hex(text_color),
            markup=True,
            halign='left',
            valign='top',
            padding=[dp(10), dp(10)]
        )
        message_label.bind(
            size=lambda *x: setattr(message_label, 'text_size', (message_label.width - dp(20), None))
        )
        bubble.add_widget(message_label)

        return bubble

    def _calculate_height(self, text):
        """Estimate height based on text length."""
        # Rough estimate: 20dp per line, assuming ~40 chars per line
        lines = max(1, len(text) // 40 + text.count('\n'))
        return min(dp(30) + lines * dp(25), dp(300))  # Cap at 300dp


class ChatScreen(Screen):
    """Screen for AI chat interface."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'chat'
        self.api_client = APIClient()
        self.messages = []

        # Main container
        main_layout = ColoredBox(
            orientation='vertical',
            bg_color=COLORS['background']
        )

        # Messages scroll area
        self.scroll = ScrollView()
        self.messages_container = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=get_padding(),
            size_hint_y=None
        )
        self.messages_container.bind(minimum_height=self.messages_container.setter('height'))
        self.scroll.add_widget(self.messages_container)

        main_layout.add_widget(self.scroll)

        # Quick suggestions (initially visible)
        self.suggestions_box = BoxLayout(
            orientation='vertical',
            spacing=dp(8),
            padding=get_padding(),
            size_hint_y=None,
            height=dp(200)
        )

        sugg_title = Label(
            text='Sugestões:',
            font_size=scaled_font(14),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            size_hint_y=None,
            height=dp(30),
            halign='left',
            valign='middle'
        )
        sugg_title.bind(size=lambda *x: setattr(sugg_title, 'text_size', (sugg_title.width, None)))
        self.suggestions_box.add_widget(sugg_title)

        suggestions = [
            'Analise meu deck',
            'Melhor estratégia contra Charizard',
            'Substituições para cartas em rotação'
        ]

        for suggestion in suggestions:
            btn = OutlineButton(
                text=suggestion,
                outline_color=COLORS['primary'],
                height=dp(40)
            )
            btn.bind(on_press=lambda x, s=suggestion: self._send_message(s))
            self.suggestions_box.add_widget(btn)

        main_layout.add_widget(self.suggestions_box)

        # Input area
        input_area = ColoredBox(
            orientation='horizontal',
            bg_color=COLORS['surface'],
            size_hint_y=None,
            height=dp(70),
            spacing=dp(10),
            padding=get_padding()
        )

        self.text_input = TextInput(
            hint_text='Digite sua mensagem...',
            font_size=scaled_font(14),
            multiline=False,
            size_hint_y=None,
            height=dp(45)
        )
        self.text_input.bind(on_text_validate=lambda x: self._send_message())
        input_area.add_widget(self.text_input)

        send_btn = PrimaryButton(
            text='Enviar',
            size_hint_x=None,
            width=dp(100),
            height=dp(45),
            size_hint_y=None
        )
        send_btn.bind(on_press=lambda x: self._send_message())
        input_area.add_widget(send_btn)

        main_layout.add_widget(input_area)
        self.add_widget(main_layout)

        # Add welcome message
        self._add_ai_message('Olá! Sou seu assistente de TCG. Como posso ajudar você hoje?')

    def _send_message(self, text=None):
        """Send message to AI."""
        message = text if text else self.text_input.text.strip()

        if not message:
            return

        # Clear input
        self.text_input.text = ''

        # Hide suggestions after first message
        if self.suggestions_box.parent:
            self.suggestions_box.parent.remove_widget(self.suggestions_box)

        # Add user message
        self._add_user_message(message)

        # Show loading indicator
        loading = LoadingSpinner()
        self.messages_container.add_widget(loading)
        self._scroll_to_bottom()

        # Call API
        def fetch():
            try:
                result = self.api_client.send_chat_message(message)
                Clock.schedule_once(lambda dt: self._receive_response(result, loading), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: self._receive_error(str(e), loading), 0)

        threading.Thread(target=fetch, daemon=True).start()

    def _add_user_message(self, text):
        """Add user message to chat."""
        bubble = MessageBubble(message=text, is_user=True)
        self.messages_container.add_widget(bubble)
        self.messages.append({'role': 'user', 'content': text})
        self._scroll_to_bottom()

    def _add_ai_message(self, text):
        """Add AI message to chat."""
        bubble = MessageBubble(message=text, is_user=False)
        self.messages_container.add_widget(bubble)
        self.messages.append({'role': 'assistant', 'content': text})
        self._scroll_to_bottom()

    def _receive_response(self, response, loading_widget):
        """Handle AI response."""
        # Remove loading indicator
        if loading_widget in self.messages_container.children:
            self.messages_container.remove_widget(loading_widget)

        # Add AI response
        ai_message = response.get('message', 'Desculpe, não consegui processar sua mensagem.')
        self._add_ai_message(ai_message)

    def _receive_error(self, error_msg, loading_widget):
        """Handle error response."""
        # Remove loading indicator
        if loading_widget in self.messages_container.children:
            self.messages_container.remove_widget(loading_widget)

        # Add error message
        self._add_ai_message(f'Desculpe, ocorreu um erro: {error_msg}')

    def _scroll_to_bottom(self):
        """Scroll to bottom of messages."""
        Clock.schedule_once(lambda dt: setattr(self.scroll, 'scroll_y', 0), 0.1)

    def on_enter(self):
        """Called when screen is displayed."""
        # Focus on input
        self.text_input.focus = True
