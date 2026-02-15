"""
My Decks Screen - List and manage saved decks

Features:
- List all saved decks
- Set active deck
- Navigate to deck details/edit
- Delete decks

Responsive for Samsung Galaxy Z Fold 6:
- Cover screen: Compact single-column layout
- Main screen: Larger touch targets and fonts
"""

import os
import sys

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.properties import StringProperty
from kivy.clock import Clock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.user_database import UserDatabase, UserDeck
from utils.responsive import get_responsive_manager


# Color scheme
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
}


class MyDecksScreen(Screen):
    """Screen displaying user's saved decks - responsive for Samsung Fold 6."""

    lang = StringProperty("en")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = UserDatabase()
        self.responsive = get_responsive_manager()
        self._build_ui()
        # Bind to screen mode changes
        self.responsive.bind(screen_mode=self._on_mode_change)

    def _on_mode_change(self, instance, mode):
        """Rebuild UI when screen mode changes."""
        self.clear_widgets()
        self._build_ui()
        if hasattr(self, '_entered') and self._entered:
            self._refresh_decks()

    def _get_font_scale(self):
        """Get current font scale factor."""
        return self.responsive.font_scale

    def _build_ui(self):
        """Build the screen UI with responsive sizing."""
        font_scale = self._get_font_scale()
        is_cover = self.responsive.is_cover_mode
        is_main = self.responsive.is_main_mode

        # Responsive padding
        padding = dp(20) if is_main else (dp(14) if is_cover else dp(16))
        main_layout = BoxLayout(orientation='vertical', padding=padding, spacing=dp(16))

        with main_layout.canvas.before:
            Color(*get_color_from_hex(COLORS['background']))
            self._bg_rect = Rectangle(pos=main_layout.pos, size=main_layout.size)
        main_layout.bind(pos=self._update_bg, size=self._update_bg)

        # Header
        header = self._create_header()
        main_layout.add_widget(header)

        # Active deck indicator
        self.active_deck_widget = self._create_active_deck_indicator()
        main_layout.add_widget(self.active_deck_widget)

        # Decks list (scrollable)
        self.scroll = ScrollView()
        self.decks_grid = GridLayout(
            cols=1,
            spacing=dp(14),
            size_hint_y=None,
            padding=[0, dp(10)]
        )
        self.decks_grid.bind(minimum_height=self.decks_grid.setter('height'))
        self.scroll.add_widget(self.decks_grid)
        main_layout.add_widget(self.scroll)

        # Bottom buttons - larger touch targets
        btn_height = self.responsive.button_height
        bottom_btns = BoxLayout(size_hint_y=None, height=btn_height, spacing=dp(12))

        # Import deck button
        import_btn = Button(
            text='+ Import' if self.lang == 'en' else '+ Importar',
            background_color=get_color_from_hex(COLORS['secondary']),
            font_size=sp(16 * font_scale),
            bold=True
        )
        import_btn.bind(on_release=self._go_to_import)
        bottom_btns.add_widget(import_btn)

        # Create new deck button
        new_btn = Button(
            text='+ New Deck' if self.lang == 'en' else '+ Novo Deck',
            background_color=get_color_from_hex(COLORS['primary']),
            font_size=sp(16 * font_scale),
            bold=True
        )
        new_btn.bind(on_release=self._go_to_new_deck)
        bottom_btns.add_widget(new_btn)

        main_layout.add_widget(bottom_btns)

        self.add_widget(main_layout)

    def _update_bg(self, *args):
        self._bg_rect.pos = args[0].pos
        self._bg_rect.size = args[0].size

    def _create_header(self):
        """Create header with title and back button - responsive sizing."""
        font_scale = self._get_font_scale()
        is_cover = self.responsive.is_cover_mode

        # Responsive header height - minimum 56dp for touch
        header_height = self.responsive.nav_height
        header = BoxLayout(size_hint_y=None, height=header_height, spacing=dp(12))

        # Back button - minimum 48dp touch target
        btn_size = self.responsive.touch_target
        back_btn = Button(
            text='<',
            size_hint_x=None,
            width=btn_size,
            background_color=get_color_from_hex(COLORS['text_muted']),
            font_size=sp(22 * font_scale)
        )
        back_btn.bind(on_release=self._go_back)
        header.add_widget(back_btn)

        # Title - responsive font
        title = Label(
            text='My Decks' if self.lang == 'en' else 'Meus Decks',
            font_size=sp(22 * font_scale),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        header.add_widget(title)

        return header

    def _create_active_deck_indicator(self):
        """Create indicator showing the active deck - responsive sizing."""
        font_scale = self._get_font_scale()

        # Larger touch target
        indicator_height = dp(56) if self.responsive.is_main_mode else dp(48)
        container = BoxLayout(
            size_hint_y=None,
            height=indicator_height,
            padding=dp(14),
            spacing=dp(10)
        )

        with container.canvas.before:
            Color(*get_color_from_hex(COLORS['primary']))
            self._active_bg = RoundedRectangle(
                pos=container.pos,
                size=container.size,
                radius=[dp(10)]
            )
        container.bind(
            pos=lambda *a: setattr(self._active_bg, 'pos', container.pos),
            size=lambda *a: setattr(self._active_bg, 'size', container.size)
        )

        icon = Label(
            text='★',
            font_size=sp(20 * font_scale),
            color=(1, 1, 1, 1),
            size_hint_x=None,
            width=dp(36)
        )
        container.add_widget(icon)

        self.active_deck_label = Label(
            text='No active deck' if self.lang == 'en' else 'Nenhum deck ativo',
            font_size=sp(16 * font_scale),
            color=(1, 1, 1, 1),
            halign='left',
            valign='middle'
        )
        self.active_deck_label.bind(size=self.active_deck_label.setter('text_size'))
        container.add_widget(self.active_deck_label)

        return container

    def on_enter(self):
        """Called when screen is displayed."""
        self._entered = True
        self._refresh_decks()

    def _refresh_decks(self):
        """Refresh the deck list."""
        self.decks_grid.clear_widgets()
        font_scale = self._get_font_scale()

        decks = self.db.get_all_decks()
        active_deck = self.db.get_active_deck()

        # Update active deck indicator
        if active_deck:
            self.active_deck_label.text = f'Active: {active_deck.name}'
        else:
            self.active_deck_label.text = 'No active deck' if self.lang == 'en' else 'Nenhum deck ativo'

        if not decks:
            empty_label = Label(
                text='No decks saved yet.\nImport your first deck!' if self.lang == 'en' else
                     'Nenhum deck salvo ainda.\nImporte seu primeiro deck!',
                font_size=sp(18 * font_scale),
                color=get_color_from_hex(COLORS['text_secondary']),
                halign='center',
                size_hint_y=None,
                height=dp(120)
            )
            self.decks_grid.add_widget(empty_label)
            return

        for deck in decks:
            card = self._create_deck_card(deck)
            self.decks_grid.add_widget(card)

    def _create_deck_card(self, deck: UserDeck):
        """Create a card widget for a deck - responsive sizing."""
        font_scale = self._get_font_scale()
        is_cover = self.responsive.is_cover_mode
        is_main = self.responsive.is_main_mode

        # Larger card for better touch targets
        card_height = dp(140) if is_main else (dp(120) if is_cover else dp(130))
        card_padding = dp(16) if is_main else dp(12)

        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=card_height,
            padding=card_padding,
            spacing=dp(10)
        )

        with card.canvas.before:
            Color(*get_color_from_hex(COLORS['surface']))
            card._bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(10)])
        card.bind(
            pos=lambda *a, c=card: setattr(c._bg, 'pos', c.pos),
            size=lambda *a, c=card: setattr(c._bg, 'size', c.size)
        )

        # Top row: Name + Active indicator
        top_row = BoxLayout(size_hint_y=None, height=dp(30))

        name_label = Label(
            text=deck.name,
            font_size=sp(18 * font_scale),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            valign='middle'
        )
        name_label.bind(size=name_label.setter('text_size'))
        top_row.add_widget(name_label)

        if deck.is_active:
            active_badge = Label(
                text='★ ACTIVE' if self.lang == 'en' else '★ ATIVO',
                font_size=sp(12 * font_scale),
                color=get_color_from_hex(COLORS['primary']),
                bold=True,
                size_hint_x=None,
                width=dp(80)
            )
            top_row.add_widget(active_badge)

        if not deck.is_complete:
            incomplete_badge = Label(
                text='INCOMPLETE' if self.lang == 'en' else 'INCOMPLETO',
                font_size=sp(11 * font_scale),
                color=get_color_from_hex(COLORS['warning']),
                size_hint_x=None,
                width=dp(90)
            )
            top_row.add_widget(incomplete_badge)

        card.add_widget(top_row)

        # Stats row
        stats_row = BoxLayout(size_hint_y=None, height=dp(24))

        stats_text = f'{deck.total_cards}/60 cards • {deck.pokemon_count} Pokemon • {deck.trainer_count} Trainers • {deck.energy_count} Energy'
        stats_label = Label(
            text=stats_text,
            font_size=sp(13 * font_scale),
            color=get_color_from_hex(COLORS['text_secondary']),
            halign='left',
            valign='middle'
        )
        stats_label.bind(size=stats_label.setter('text_size'))
        stats_row.add_widget(stats_label)

        card.add_widget(stats_row)

        # Buttons row - larger touch targets
        btn_height = dp(44) if is_main else dp(40)
        buttons_row = BoxLayout(size_hint_y=None, height=btn_height, spacing=dp(10))

        # Set Active button
        if not deck.is_active:
            active_btn = Button(
                text='Set Active' if self.lang == 'en' else 'Ativar',
                background_color=get_color_from_hex(COLORS['primary']),
                font_size=sp(14 * font_scale)
            )
            active_btn.bind(on_release=lambda x, d=deck: self._set_active(d))
            buttons_row.add_widget(active_btn)

        # Compare button (only if complete)
        if deck.is_complete:
            compare_btn = Button(
                text='Compare' if self.lang == 'en' else 'Comparar',
                background_color=get_color_from_hex(COLORS['secondary']),
                font_size=sp(14 * font_scale)
            )
            compare_btn.bind(on_release=lambda x, d=deck: self._go_to_compare(d))
            buttons_row.add_widget(compare_btn)

        # Edit button
        edit_btn = Button(
            text='Edit' if self.lang == 'en' else 'Editar',
            background_color=get_color_from_hex(COLORS['accent']),
            font_size=sp(14 * font_scale)
        )
        edit_btn.bind(on_release=lambda x, d=deck: self._go_to_edit(d))
        buttons_row.add_widget(edit_btn)

        # Delete button
        delete_btn = Button(
            text='Delete' if self.lang == 'en' else 'Excluir',
            background_color=get_color_from_hex(COLORS['danger']),
            font_size=sp(14 * font_scale)
        )
        delete_btn.bind(on_release=lambda x, d=deck: self._confirm_delete(d))
        buttons_row.add_widget(delete_btn)

        card.add_widget(buttons_row)

        return card

    # =========================================================================
    # EVENT HANDLERS
    # =========================================================================

    def _go_back(self, *args):
        """Navigate back to home."""
        if self.manager:
            self.manager.transition.direction = 'right'
            self.manager.current = 'home'

    def _go_to_import(self, *args):
        """Navigate to import screen."""
        if self.manager:
            self.manager.transition.direction = 'left'
            self.manager.current = 'import'

    def _go_to_new_deck(self, *args):
        """Navigate to deck editor for new deck."""
        if self.manager:
            editor_screen = self.manager.get_screen('deck_editor')
            editor_screen.deck_id = 0  # New deck
            self.manager.transition.direction = 'left'
            self.manager.current = 'deck_editor'

    def _set_active(self, deck: UserDeck):
        """Set a deck as active."""
        self.db.set_active_deck(deck.id)
        self._refresh_decks()

    def _go_to_compare(self, deck: UserDeck):
        """Navigate to comparison screen."""
        if self.manager:
            compare_screen = self.manager.get_screen('compare')
            compare_screen.deck_id = deck.id
            self.manager.transition.direction = 'left'
            self.manager.current = 'compare'

    def _go_to_edit(self, deck: UserDeck):
        """Navigate to edit screen."""
        if self.manager:
            editor_screen = self.manager.get_screen('deck_editor')
            editor_screen.deck_id = deck.id
            self.manager.transition.direction = 'left'
            self.manager.current = 'deck_editor'

    def _confirm_delete(self, deck: UserDeck):
        """Show delete confirmation dialog - responsive sizing."""
        font_scale = self._get_font_scale()
        btn_height = self.responsive.button_height

        content = BoxLayout(orientation='vertical', padding=dp(24), spacing=dp(18))

        content.add_widget(Label(
            text=f'Delete "{deck.name}"?' if self.lang == 'en' else f'Excluir "{deck.name}"?',
            font_size=sp(18 * font_scale),
            halign='center'
        ))

        content.add_widget(Label(
            text='This action cannot be undone.' if self.lang == 'en' else
                 'Esta ação não pode ser desfeita.',
            font_size=sp(15 * font_scale),
            color=get_color_from_hex(COLORS['text_secondary']),
            halign='center'
        ))

        buttons = BoxLayout(size_hint_y=None, height=btn_height, spacing=dp(12))

        delete_btn = Button(
            text='Delete' if self.lang == 'en' else 'Excluir',
            background_color=get_color_from_hex(COLORS['danger']),
            font_size=sp(16 * font_scale)
        )
        cancel_btn = Button(
            text='Cancel' if self.lang == 'en' else 'Cancelar',
            background_color=get_color_from_hex(COLORS['text_muted']),
            font_size=sp(16 * font_scale)
        )

        buttons.add_widget(delete_btn)
        buttons.add_widget(cancel_btn)
        content.add_widget(buttons)

        popup = Popup(
            title='Confirm Delete' if self.lang == 'en' else 'Confirmar Exclusão',
            content=content,
            size_hint=(0.85, 0.45),
            auto_dismiss=True
        )

        def do_delete(*a):
            self.db.delete_deck(deck.id)
            popup.dismiss()
            self._refresh_decks()

        delete_btn.bind(on_release=do_delete)
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()

    def _show_message(self, title, message):
        """Show a simple message popup - responsive sizing."""
        font_scale = self._get_font_scale()
        btn_height = self.responsive.button_height

        content = BoxLayout(orientation='vertical', padding=dp(24), spacing=dp(18))

        content.add_widget(Label(
            text=message,
            font_size=sp(16 * font_scale),
            halign='center'
        ))

        close_btn = Button(
            text='OK',
            size_hint_y=None,
            height=btn_height,
            background_color=get_color_from_hex(COLORS['primary']),
            font_size=sp(16 * font_scale)
        )

        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.85, 0.4),
            auto_dismiss=True
        )
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()
