"""
Import Deck Screen - Import decks from text or file

Features:
- Paste deck text from TCG Live
- Import from .txt file
- Multi-deck support
- Validation feedback
- Preview before saving
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
from kivy.uix.image import AsyncImage
from kivy.uix.screenmanager import Screen
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty, ListProperty

# Add parent to path for service imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.deck_import import DeckImportService, ImportResult, ValidationSeverity
from services.user_database import UserDatabase, UserDeck


# Color scheme (matching main app)
COLORS = {
    'background': '#f5f5f5',
    'surface': '#ffffff',
    'card': '#ffffff',
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
    'info': '#2196f3',
}


class ImportScreen(Screen):
    """Screen for importing decks."""

    current_result = ObjectProperty(None, allownone=True)
    status_text = StringProperty("")
    lang = StringProperty("en")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.import_service = DeckImportService()
        self.db = UserDatabase()
        self._build_ui()

    def _build_ui(self):
        """Build the import screen UI."""
        # Main container
        main_layout = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(16))

        with main_layout.canvas.before:
            Color(*get_color_from_hex(COLORS['background']))
            self._bg_rect = Rectangle(pos=main_layout.pos, size=main_layout.size)
        main_layout.bind(pos=self._update_bg, size=self._update_bg)

        # Header
        header = self._create_header()
        main_layout.add_widget(header)

        # Instructions
        instructions = self._create_instructions()
        main_layout.add_widget(instructions)

        # Text input area
        input_area = self._create_input_area()
        main_layout.add_widget(input_area)

        # Action buttons
        buttons = self._create_action_buttons()
        main_layout.add_widget(buttons)

        # Status/Results area
        self.status_area = self._create_status_area()
        main_layout.add_widget(self.status_area)

        # Preview area (scrollable)
        self.preview_area = self._create_preview_area()
        main_layout.add_widget(self.preview_area)

        # Bottom buttons (Save/Discard)
        self.bottom_buttons = self._create_bottom_buttons()
        main_layout.add_widget(self.bottom_buttons)
        self.bottom_buttons.opacity = 0
        self.bottom_buttons.disabled = True

        self.add_widget(main_layout)

    def _update_bg(self, *args):
        self._bg_rect.pos = args[0].pos
        self._bg_rect.size = args[0].size

    def _create_header(self):
        """Create header with title and back button."""
        header = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))

        # Back button
        back_btn = Button(
            text='<',
            size_hint_x=None,
            width=dp(40),
            background_color=get_color_from_hex(COLORS['text_muted']),
            font_size=sp(20)
        )
        back_btn.bind(on_release=self._go_back)
        header.add_widget(back_btn)

        # Title
        title = Label(
            text='Import Deck' if self.lang == 'en' else 'Importar Deck',
            font_size=sp(20),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        header.add_widget(title)

        return header

    def _create_instructions(self):
        """Create instructions label."""
        text_en = "Paste your deck from Pokemon TCG Live or select a .txt file"
        text_pt = "Cole seu deck do Pokemon TCG Live ou selecione um arquivo .txt"

        instructions = Label(
            text=text_en if self.lang == 'en' else text_pt,
            font_size=sp(14),
            color=get_color_from_hex(COLORS['text_secondary']),
            size_hint_y=None,
            height=dp(30),
            halign='left',
            valign='middle'
        )
        instructions.bind(size=instructions.setter('text_size'))
        return instructions

    def _create_input_area(self):
        """Create the text input area."""
        container = BoxLayout(orientation='vertical', size_hint_y=0.35, spacing=dp(8))

        # Text input with card styling
        input_container = BoxLayout(padding=dp(2))
        with input_container.canvas.before:
            Color(*get_color_from_hex(COLORS['surface']))
            self._input_bg = RoundedRectangle(
                pos=input_container.pos,
                size=input_container.size,
                radius=[dp(8)]
            )
        input_container.bind(
            pos=lambda *a: setattr(self._input_bg, 'pos', input_container.pos),
            size=lambda *a: setattr(self._input_bg, 'size', input_container.size)
        )

        self.text_input = TextInput(
            hint_text='Paste deck here...\n\nExample:\n4 Charizard ex OBF 125\n4 Arven SVI 166\n...',
            multiline=True,
            font_size=sp(13),
            background_color=(0, 0, 0, 0),
            foreground_color=get_color_from_hex(COLORS['text']),
            cursor_color=get_color_from_hex(COLORS['primary']),
            padding=[dp(12), dp(12)]
        )
        input_container.add_widget(self.text_input)
        container.add_widget(input_container)

        return container

    def _create_action_buttons(self):
        """Create action buttons (Import, Clear, Load File)."""
        buttons = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))

        # Import button
        import_btn = Button(
            text='Import' if self.lang == 'en' else 'Importar',
            background_color=get_color_from_hex(COLORS['primary']),
            font_size=sp(14),
            bold=True
        )
        import_btn.bind(on_release=self._on_import)
        buttons.add_widget(import_btn)

        # Load file button
        file_btn = Button(
            text='Load File' if self.lang == 'en' else 'Carregar Arquivo',
            background_color=get_color_from_hex(COLORS['secondary']),
            font_size=sp(14)
        )
        file_btn.bind(on_release=self._on_load_file)
        buttons.add_widget(file_btn)

        # Clear button
        clear_btn = Button(
            text='Clear' if self.lang == 'en' else 'Limpar',
            background_color=get_color_from_hex(COLORS['text_muted']),
            font_size=sp(14)
        )
        clear_btn.bind(on_release=self._on_clear)
        buttons.add_widget(clear_btn)

        return buttons

    def _create_status_area(self):
        """Create status message area."""
        self.status_label = Label(
            text='',
            font_size=sp(13),
            color=get_color_from_hex(COLORS['text_secondary']),
            size_hint_y=None,
            height=dp(25),
            halign='left',
            valign='middle'
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))
        return self.status_label

    def _create_preview_area(self):
        """Create scrollable preview area for imported deck."""
        scroll = ScrollView(size_hint_y=0.35)

        self.preview_grid = GridLayout(
            cols=1,
            spacing=dp(8),
            size_hint_y=None,
            padding=[0, dp(8)]
        )
        self.preview_grid.bind(minimum_height=self.preview_grid.setter('height'))

        scroll.add_widget(self.preview_grid)
        return scroll

    def _create_bottom_buttons(self):
        """Create save/discard buttons."""
        buttons = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))

        # Save button
        self.save_btn = Button(
            text='Save to My Decks' if self.lang == 'en' else 'Salvar em Meus Decks',
            background_color=get_color_from_hex(COLORS['success']),
            font_size=sp(14),
            bold=True
        )
        self.save_btn.bind(on_release=self._on_save)
        buttons.add_widget(self.save_btn)

        # Discard button
        discard_btn = Button(
            text='Discard' if self.lang == 'en' else 'Descartar',
            background_color=get_color_from_hex(COLORS['danger']),
            font_size=sp(14)
        )
        discard_btn.bind(on_release=self._on_discard)
        buttons.add_widget(discard_btn)

        return buttons

    # =========================================================================
    # EVENT HANDLERS
    # =========================================================================

    def _go_back(self, *args):
        """Navigate back."""
        if self.manager:
            self.manager.transition.direction = 'right'
            self.manager.current = 'home'

    def _on_import(self, *args):
        """Handle import button click."""
        text = self.text_input.text.strip()

        if not text:
            self._show_status("Please paste a deck first" if self.lang == 'en' else
                              "Por favor, cole um deck primeiro", 'warning')
            return

        # Import the deck
        result = self.import_service.import_from_text(text)
        self.current_result = result

        if result.deck:
            self._show_preview(result)
            self._show_bottom_buttons(True)

            if result.has_errors:
                self._show_status(
                    f"Deck has errors - review before saving" if self.lang == 'en' else
                    f"Deck tem erros - revise antes de salvar", 'danger'
                )
            elif result.has_warnings:
                self._show_status(
                    f"Deck imported with warnings ({result.deck.total_cards}/60 cards)" if self.lang == 'en' else
                    f"Deck importado com avisos ({result.deck.total_cards}/60 cartas)", 'warning'
                )
            else:
                self._show_status(
                    f"Deck imported successfully ({result.deck.total_cards}/60 cards)" if self.lang == 'en' else
                    f"Deck importado com sucesso ({result.deck.total_cards}/60 cartas)", 'success'
                )
        else:
            self._show_status(
                "Could not parse deck - check format" if self.lang == 'en' else
                "Não foi possível processar o deck - verifique o formato", 'danger'
            )

    def _on_load_file(self, *args):
        """Handle load file button click."""
        # Try to use Android file picker or Kivy file chooser
        try:
            from plyer import filechooser
            filechooser.open_file(
                on_selection=self._on_file_selected,
                filters=[("Text files", "*.txt")]
            )
        except ImportError:
            # Fallback - show popup with instructions
            self._show_file_popup()

    def _on_file_selected(self, selection):
        """Handle file selection."""
        if selection:
            file_path = selection[0]
            result = self.import_service.import_from_file(file_path)

            if result.successful > 0:
                # Use first successful deck for now
                for r in result.results:
                    if r.success and r.deck:
                        self.current_result = r
                        self._show_preview(r)
                        self._show_bottom_buttons(True)
                        self._show_status(
                            f"Loaded {result.successful} deck(s) from file" if self.lang == 'en' else
                            f"Carregados {result.successful} deck(s) do arquivo", 'success'
                        )
                        break
            else:
                self._show_status(
                    "No valid decks found in file" if self.lang == 'en' else
                    "Nenhum deck válido encontrado no arquivo", 'danger'
                )

    def _show_file_popup(self):
        """Show popup for file loading (fallback)."""
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

        content.add_widget(Label(
            text="File loading not available on this device.\nPlease copy and paste your deck text instead." if self.lang == 'en' else
                 "Carregamento de arquivo não disponível neste dispositivo.\nPor favor, copie e cole o texto do deck.",
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
            title='Info',
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=True
        )
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()

    def _on_clear(self, *args):
        """Clear all input and preview."""
        self.text_input.text = ''
        self.current_result = None
        self._clear_preview()
        self._show_bottom_buttons(False)
        self._show_status('', None)

    def _on_save(self, *args):
        """Save the imported deck."""
        if not self.current_result or not self.current_result.deck:
            return

        deck = self.current_result.deck

        # Suggest a name
        suggested_name = self.import_service.suggest_deck_name(deck)

        # Show name dialog
        self._show_name_dialog(deck, suggested_name)

    def _show_name_dialog(self, deck, suggested_name):
        """Show dialog to name the deck."""
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

        content.add_widget(Label(
            text='Enter deck name:' if self.lang == 'en' else 'Digite o nome do deck:',
            font_size=sp(14),
            size_hint_y=None,
            height=dp(30)
        ))

        name_input = TextInput(
            text=suggested_name,
            multiline=False,
            font_size=sp(16),
            size_hint_y=None,
            height=dp(45)
        )
        content.add_widget(name_input)

        # Warning if incomplete
        if not deck.is_complete:
            content.add_widget(Label(
                text=f'Warning: Deck is incomplete ({deck.total_cards}/60)' if self.lang == 'en' else
                     f'Aviso: Deck incompleto ({deck.total_cards}/60)',
                font_size=sp(12),
                color=get_color_from_hex(COLORS['warning']),
                size_hint_y=None,
                height=dp(25)
            ))

        buttons = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))

        save_btn = Button(
            text='Save' if self.lang == 'en' else 'Salvar',
            background_color=get_color_from_hex(COLORS['success'])
        )
        cancel_btn = Button(
            text='Cancel' if self.lang == 'en' else 'Cancelar',
            background_color=get_color_from_hex(COLORS['text_muted'])
        )

        buttons.add_widget(save_btn)
        buttons.add_widget(cancel_btn)
        content.add_widget(buttons)

        popup = Popup(
            title='Save Deck' if self.lang == 'en' else 'Salvar Deck',
            content=content,
            size_hint=(0.85, 0.45),
            auto_dismiss=False
        )

        def do_save(*a):
            deck.name = name_input.text or suggested_name
            deck_id = self.db.save_deck(deck)
            popup.dismiss()
            self._on_clear()
            self._show_status(
                f'Deck "{deck.name}" saved!' if self.lang == 'en' else
                f'Deck "{deck.name}" salvo!', 'success'
            )

        save_btn.bind(on_release=do_save)
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()

    def _on_discard(self, *args):
        """Discard the imported deck."""
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

        content.add_widget(Label(
            text='Are you sure you want to discard this deck?' if self.lang == 'en' else
                 'Tem certeza que deseja descartar este deck?',
            font_size=sp(14),
            halign='center'
        ))

        buttons = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))

        yes_btn = Button(
            text='Yes, Discard' if self.lang == 'en' else 'Sim, Descartar',
            background_color=get_color_from_hex(COLORS['danger'])
        )
        no_btn = Button(
            text='No, Keep' if self.lang == 'en' else 'Não, Manter',
            background_color=get_color_from_hex(COLORS['text_muted'])
        )

        buttons.add_widget(yes_btn)
        buttons.add_widget(no_btn)
        content.add_widget(buttons)

        popup = Popup(
            title='Discard Deck?' if self.lang == 'en' else 'Descartar Deck?',
            content=content,
            size_hint=(0.8, 0.35),
            auto_dismiss=True
        )

        def do_discard(*a):
            popup.dismiss()
            self._on_clear()

        yes_btn.bind(on_release=do_discard)
        no_btn.bind(on_release=popup.dismiss)
        popup.open()

    # =========================================================================
    # UI HELPERS
    # =========================================================================

    def _show_status(self, text, status_type=None):
        """Show status message."""
        self.status_label.text = text

        if status_type == 'success':
            self.status_label.color = get_color_from_hex(COLORS['success'])
        elif status_type == 'warning':
            self.status_label.color = get_color_from_hex(COLORS['warning'])
        elif status_type == 'danger':
            self.status_label.color = get_color_from_hex(COLORS['danger'])
        else:
            self.status_label.color = get_color_from_hex(COLORS['text_secondary'])

    def _show_bottom_buttons(self, show):
        """Show or hide bottom action buttons."""
        self.bottom_buttons.opacity = 1 if show else 0
        self.bottom_buttons.disabled = not show

    def _clear_preview(self):
        """Clear preview area."""
        self.preview_grid.clear_widgets()

    def _show_preview(self, result: ImportResult):
        """Show deck preview."""
        self._clear_preview()
        deck = result.deck

        # Summary card
        summary = self._create_summary_card(deck, result.issues)
        self.preview_grid.add_widget(summary)

        # Group cards by type
        pokemon = [c for c in deck.cards if c.card_type == 'pokemon']
        trainers = [c for c in deck.cards if c.card_type == 'trainer']
        energy = [c for c in deck.cards if c.card_type == 'energy']

        # Add section headers and cards
        if pokemon:
            self.preview_grid.add_widget(self._create_section_header(
                f'Pokemon ({deck.pokemon_count})'
            ))
            for card in pokemon:
                self.preview_grid.add_widget(self._create_card_row(card))

        if trainers:
            self.preview_grid.add_widget(self._create_section_header(
                f'Trainers ({deck.trainer_count})'
            ))
            for card in trainers:
                self.preview_grid.add_widget(self._create_card_row(card))

        if energy:
            self.preview_grid.add_widget(self._create_section_header(
                f'Energy ({deck.energy_count})'
            ))
            for card in energy:
                self.preview_grid.add_widget(self._create_card_row(card))

    def _create_summary_card(self, deck: UserDeck, issues):
        """Create summary card with stats and issues."""
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(120),
            padding=dp(12),
            spacing=dp(8)
        )

        with card.canvas.before:
            Color(*get_color_from_hex(COLORS['surface']))
            RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(8)])

        # Stats row
        stats = BoxLayout(size_hint_y=None, height=dp(30))
        stats.add_widget(Label(
            text=f'Total: {deck.total_cards}/60',
            font_size=sp(13),
            color=get_color_from_hex(COLORS['text']),
            bold=True
        ))
        stats.add_widget(Label(
            text=f'Pokemon: {deck.pokemon_count}',
            font_size=sp(12),
            color=get_color_from_hex(COLORS['text_secondary'])
        ))
        stats.add_widget(Label(
            text=f'Trainers: {deck.trainer_count}',
            font_size=sp(12),
            color=get_color_from_hex(COLORS['text_secondary'])
        ))
        stats.add_widget(Label(
            text=f'Energy: {deck.energy_count}',
            font_size=sp(12),
            color=get_color_from_hex(COLORS['text_secondary'])
        ))
        card.add_widget(stats)

        # Issues
        for issue in issues[:3]:  # Show max 3 issues
            color = COLORS['danger'] if issue.severity == ValidationSeverity.ERROR else \
                    COLORS['warning'] if issue.severity == ValidationSeverity.WARNING else \
                    COLORS['info']

            issue_label = Label(
                text=f'• {issue.message_en}' if self.lang == 'en' else f'• {issue.message_pt}',
                font_size=sp(11),
                color=get_color_from_hex(color),
                size_hint_y=None,
                height=dp(20),
                halign='left',
                valign='middle'
            )
            issue_label.bind(size=issue_label.setter('text_size'))
            card.add_widget(issue_label)

        return card

    def _create_section_header(self, text):
        """Create section header."""
        header = Label(
            text=text,
            font_size=sp(14),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            size_hint_y=None,
            height=dp(35),
            halign='left',
            valign='bottom',
            padding=[0, dp(10)]
        )
        header.bind(size=header.setter('text_size'))
        return header

    def _create_card_row(self, card):
        """Create a row for a card."""
        row = BoxLayout(
            size_hint_y=None,
            height=dp(35),
            spacing=dp(8),
            padding=[dp(8), 0]
        )

        with row.canvas.before:
            Color(*get_color_from_hex(COLORS['surface']))
            RoundedRectangle(pos=row.pos, size=row.size, radius=[dp(4)])

        # Quantity
        qty = Label(
            text=str(card.quantity),
            font_size=sp(14),
            bold=True,
            color=get_color_from_hex(COLORS['primary']),
            size_hint_x=None,
            width=dp(25)
        )
        row.add_widget(qty)

        # Name
        name = Label(
            text=card.name,
            font_size=sp(13),
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            valign='middle'
        )
        name.bind(size=name.setter('text_size'))
        row.add_widget(name)

        # Set code
        set_label = Label(
            text=f'{card.set_code} {card.set_number}',
            font_size=sp(11),
            color=get_color_from_hex(COLORS['text_muted']),
            size_hint_x=None,
            width=dp(70),
            halign='right',
            valign='middle'
        )
        set_label.bind(size=set_label.setter('text_size'))
        row.add_widget(set_label)

        # Rotation indicator
        if card.regulation_mark == 'G':
            rot_label = Label(
                text='G',
                font_size=sp(10),
                color=get_color_from_hex(COLORS['warning']),
                size_hint_x=None,
                width=dp(20),
                bold=True
            )
            row.add_widget(rot_label)

        return row
