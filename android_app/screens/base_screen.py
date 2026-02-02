"""
Base Screen with Responsive Support

Provides a base class for screens that automatically adapts
to Samsung Galaxy Z Fold 6 screen modes.
"""

import os
import sys

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.clock import Clock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.responsive import (
    get_responsive_manager,
    ScreenMode,
    is_cover_mode,
    is_main_mode,
)


# Color scheme
COLORS = {
    'background': '#f5f5f5',
    'surface': '#ffffff',
    'primary': '#4caf50',
    'primary_dark': '#388e3c',
    'secondary': '#2196f3',
    'accent': '#ff9800',
    'text': '#212121',
    'text_secondary': '#757575',
    'text_muted': '#9e9e9e',
    'border': '#e0e0e0',
}


class ResponsiveScreen(Screen):
    """
    Base screen class with responsive layout support.

    Automatically adapts to Samsung Fold 6 screen modes:
    - Cover Screen: Compact single-column layout
    - Main Screen: Expanded multi-column layout

    Subclasses should override:
    - _build_content(): Build the main content
    - _on_mode_change(): Handle screen mode changes
    """

    lang = StringProperty("en")
    current_mode = StringProperty(ScreenMode.PHONE)
    is_cover = BooleanProperty(False)
    is_main = BooleanProperty(False)

    # Layout properties that update based on mode
    grid_cols = NumericProperty(1)
    content_padding = NumericProperty(12)
    content_spacing = NumericProperty(10)
    card_height = NumericProperty(120)
    font_scale = NumericProperty(1.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.responsive = get_responsive_manager()
        self._content_built = False
        self._bind_responsive()

    def _bind_responsive(self):
        """Bind to responsive manager changes."""
        self.responsive.bind(screen_mode=self._handle_mode_change)
        self._sync_properties()

    def _sync_properties(self):
        """Sync properties from responsive manager."""
        self.current_mode = self.responsive.screen_mode
        self.is_cover = self.responsive.is_cover_mode
        self.is_main = self.responsive.is_main_mode
        self.grid_cols = self.responsive.grid_columns
        self.content_padding = self.responsive.padding
        self.content_spacing = self.responsive.spacing
        self.card_height = self.responsive.card_height
        self.font_scale = self.responsive.font_scale

    def _handle_mode_change(self, instance, mode):
        """Handle screen mode change."""
        self._sync_properties()
        if self._content_built:
            self._on_mode_change(mode)

    def on_enter(self):
        """Called when screen is displayed."""
        if not self._content_built:
            self._build_ui()
            self._content_built = True
        self._sync_properties()

    def _build_ui(self):
        """Build the screen UI - override in subclass."""
        pass

    def _on_mode_change(self, mode):
        """Handle mode change - override in subclass to adapt layout."""
        pass

    # =========================================================================
    # HELPER METHODS FOR RESPONSIVE LAYOUTS
    # =========================================================================

    def get_scaled_font(self, base_sp: float) -> float:
        """Get font size scaled for current mode."""
        return sp(base_sp * self.font_scale)

    def create_responsive_grid(self, **kwargs) -> GridLayout:
        """Create a GridLayout that adapts columns to screen mode."""
        cols = kwargs.pop('cols', None) or self.grid_cols
        spacing = kwargs.pop('spacing', None) or self.content_spacing

        grid = GridLayout(
            cols=cols,
            spacing=spacing,
            size_hint_y=None,
            **kwargs
        )
        grid.bind(minimum_height=grid.setter('height'))
        return grid

    def create_card(self, **kwargs) -> BoxLayout:
        """Create a card container with responsive styling."""
        height = kwargs.pop('height', None) or self.card_height
        padding = kwargs.pop('padding', None) or dp(12)

        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=height,
            padding=padding,
            **kwargs
        )

        with card.canvas.before:
            Color(*get_color_from_hex(COLORS['surface']))
            card._bg = RoundedRectangle(
                pos=card.pos,
                size=card.size,
                radius=[dp(8)]
            )
        card.bind(
            pos=lambda *a, c=card: setattr(c._bg, 'pos', c.pos),
            size=lambda *a, c=card: setattr(c._bg, 'size', c.size)
        )

        return card

    def create_header(self, title: str, show_back: bool = True) -> BoxLayout:
        """Create a responsive header with optional back button."""
        header = BoxLayout(
            size_hint_y=None,
            height=dp(45) if not self.is_cover else dp(40),
            spacing=dp(10)
        )

        if show_back:
            back_btn = Button(
                text='<',
                size_hint_x=None,
                width=dp(40) if not self.is_cover else dp(35),
                background_color=get_color_from_hex(COLORS['text_muted']),
                font_size=self.get_scaled_font(20)
            )
            back_btn.bind(on_release=self._go_back)
            header.add_widget(back_btn)

        title_label = Label(
            text=title,
            font_size=self.get_scaled_font(18),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            halign='left',
            valign='middle'
        )
        title_label.bind(size=title_label.setter('text_size'))
        header.add_widget(title_label)

        return header

    def create_section_label(self, text: str) -> Label:
        """Create a section header label."""
        label = Label(
            text=text,
            font_size=self.get_scaled_font(14),
            bold=True,
            color=get_color_from_hex(COLORS['text']),
            size_hint_y=None,
            height=dp(30),
            halign='left',
            valign='bottom'
        )
        label.bind(size=label.setter('text_size'))
        return label

    def _go_back(self, *args):
        """Navigate back - override if needed."""
        if self.manager:
            self.manager.transition.direction = 'right'
            self.manager.current = 'home'

    # =========================================================================
    # LAYOUT HELPERS FOR DIFFERENT MODES
    # =========================================================================

    def should_use_side_panel(self) -> bool:
        """Check if side-by-side layout should be used."""
        return self.is_main and not self.is_cover

    def get_optimal_button_width(self) -> float:
        """Get optimal button width for current mode."""
        if self.is_cover:
            return dp(70)
        elif self.is_main:
            return dp(100)
        return dp(85)

    def get_optimal_card_columns(self) -> int:
        """Get optimal number of card columns."""
        if self.is_cover:
            return 1
        elif self.is_main:
            return 2
        return 1
