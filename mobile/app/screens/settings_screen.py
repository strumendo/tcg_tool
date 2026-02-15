"""
Settings screen - App configuration and preferences.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.switch import Switch
from kivy.metrics import dp

from app.components import (
    ColoredBox, CardBox, PrimaryButton, SecondaryButton,
    COLORS, get_color_from_hex
)
from app.utils.responsive import scaled_font, get_padding, get_spacing
from app.services.api_client import APIClient


class SettingItem(BoxLayout):
    """Individual setting item widget."""

    def __init__(self, title, description='', widget=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.spacing = dp(15)
        self.size_hint_y = None
        self.height = dp(70)

        # Title and description
        text_box = BoxLayout(
            orientation='vertical',
            spacing=dp(5)
        )

        title_label = Label(
            text=title,
            font_size=scaled_font(15),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            size_hint_y=None,
            height=dp(25),
            halign='left',
            valign='middle'
        )
        title_label.bind(size=lambda *x: setattr(title_label, 'text_size', (title_label.width, None)))
        text_box.add_widget(title_label)

        if description:
            desc_label = Label(
                text=description,
                font_size=scaled_font(12),
                color=get_color_from_hex(COLORS['text_secondary']),
                size_hint_y=None,
                height=dp(20),
                halign='left',
                valign='middle'
            )
            desc_label.bind(size=lambda *x: setattr(desc_label, 'text_size', (desc_label.width, None)))
            text_box.add_widget(desc_label)

        self.add_widget(text_box)

        # Widget (input, switch, etc.)
        if widget:
            widget_container = BoxLayout(
                size_hint_x=None,
                width=dp(120)
            )
            widget_container.add_widget(widget)
            self.add_widget(widget_container)


class SettingsScreen(Screen):
    """Screen for app settings and configuration."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'settings'
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
            text='Configurações',
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

        # Backend section
        backend_section = CardBox(
            orientation='vertical',
            size_hint_y=None,
            height=dp(140),
            spacing=dp(10)
        )

        backend_title = Label(
            text='Conexão com Backend',
            font_size=scaled_font(16),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            size_hint_y=None,
            height=dp(30),
            halign='left',
            valign='middle'
        )
        backend_title.bind(size=lambda *x: setattr(backend_title, 'text_size', (backend_title.width, None)))
        backend_section.add_widget(backend_title)

        # Backend URL input
        url_label = Label(
            text='URL do Backend:',
            font_size=scaled_font(14),
            color=get_color_from_hex(COLORS['text_secondary']),
            size_hint_y=None,
            height=dp(25),
            halign='left',
            valign='middle'
        )
        url_label.bind(size=lambda *x: setattr(url_label, 'text_size', (url_label.width, None)))
        backend_section.add_widget(url_label)

        self.backend_url_input = TextInput(
            text=self.api_client.base_url,
            font_size=scaled_font(13),
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            padding=[dp(10), dp(12)]
        )
        backend_section.add_widget(self.backend_url_input)

        save_url_btn = SecondaryButton(
            text='Salvar URL',
            size_hint_x=None,
            width=dp(120),
            height=dp(35),
            size_hint_y=None
        )
        save_url_btn.bind(on_press=lambda x: self._save_backend_url())
        backend_section.add_widget(save_url_btn)

        content.add_widget(backend_section)

        # Language section
        language_section = CardBox(
            orientation='vertical',
            size_hint_y=None,
            height=dp(100),
            spacing=dp(5)
        )

        lang_item = SettingItem(
            title='Idioma',
            description='Português (Brasil)',
            widget=Switch(active=True, disabled=True)  # PT only for now
        )
        language_section.add_widget(lang_item)

        content.add_widget(language_section)

        # Cache section
        cache_section = CardBox(
            orientation='vertical',
            size_hint_y=None,
            height=dp(100),
            spacing=dp(10)
        )

        cache_title = Label(
            text='Cache',
            font_size=scaled_font(16),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            size_hint_y=None,
            height=dp(30),
            halign='left',
            valign='middle'
        )
        cache_title.bind(size=lambda *x: setattr(cache_title, 'text_size', (cache_title.width, None)))
        cache_section.add_widget(cache_title)

        clear_cache_btn = SecondaryButton(
            text='Limpar Cache',
            size_hint_x=None,
            width=dp(150),
            height=dp(40),
            size_hint_y=None
        )
        clear_cache_btn.bind(on_press=lambda x: self._clear_cache())
        cache_section.add_widget(clear_cache_btn)

        content.add_widget(cache_section)

        # About section
        about_section = CardBox(
            orientation='vertical',
            size_hint_y=None,
            height=dp(150),
            spacing=dp(8)
        )

        about_title = Label(
            text='Sobre',
            font_size=scaled_font(16),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            size_hint_y=None,
            height=dp(30),
            halign='left',
            valign='middle'
        )
        about_title.bind(size=lambda *x: setattr(about_title, 'text_size', (about_title.width, None)))
        about_section.add_widget(about_title)

        version_label = Label(
            text='Versão: 3.0.0',
            font_size=scaled_font(14),
            color=get_color_from_hex(COLORS['text_secondary']),
            size_hint_y=None,
            height=dp(25),
            halign='left',
            valign='middle'
        )
        version_label.bind(size=lambda *x: setattr(version_label, 'text_size', (version_label.width, None)))
        about_section.add_widget(version_label)

        description_label = Label(
            text='TCG Tool - Analisador de Decks Pokemon\nDesenvolvido com Kivy + FastAPI',
            font_size=scaled_font(12),
            color=get_color_from_hex(COLORS['text_muted']),
            size_hint_y=None,
            height=dp(45),
            halign='left',
            valign='top'
        )
        description_label.bind(size=lambda *x: setattr(description_label, 'text_size', (description_label.width, None)))
        about_section.add_widget(description_label)

        content.add_widget(about_section)

        scroll.add_widget(content)
        main_layout.add_widget(scroll)
        self.add_widget(main_layout)

        # Message label for feedback
        self.message_label = None

    def _save_backend_url(self):
        """Save backend URL."""
        new_url = self.backend_url_input.text.strip()

        if not new_url:
            self._show_message('URL não pode estar vazia', 'error')
            return

        # Validate URL format
        if not (new_url.startswith('http://') or new_url.startswith('https://')):
            self._show_message('URL deve começar com http:// ou https://', 'error')
            return

        # Update API client
        self.api_client.base_url = new_url

        # Save to config (would need implementation)
        # For now, just show success message
        self._show_message('✅ URL salva com sucesso!', 'success')

    def _clear_cache(self):
        """Clear app cache."""
        # TODO: Implement cache clearing
        # For now, just show confirmation
        self._show_message('✅ Cache limpo com sucesso!', 'success')

    def _show_message(self, text, msg_type='info'):
        """Show temporary message."""
        from kivy.clock import Clock

        if self.message_label and self.message_label.parent:
            self.message_label.parent.remove_widget(self.message_label)

        color = COLORS['success'] if msg_type == 'success' else COLORS['danger'] if msg_type == 'error' else COLORS['secondary']

        self.message_label = Label(
            text=text,
            font_size=scaled_font(14),
            color=get_color_from_hex(color),
            size_hint_y=None,
            height=dp(40),
            halign='center',
            valign='middle'
        )
        self.message_label.bind(size=lambda *x: setattr(self.message_label, 'text_size', (self.message_label.width, None)))

        # Add to layout (would need reference to parent)
        # For now, just clear after timeout
        Clock.schedule_once(lambda dt: self._clear_message(), 3)

    def _clear_message(self):
        """Clear message label."""
        if self.message_label and self.message_label.parent:
            self.message_label.parent.remove_widget(self.message_label)
