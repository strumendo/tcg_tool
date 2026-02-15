"""
Top navigation bar component for screen switching.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.properties import StringProperty, ObjectProperty

from app.components.base import ColoredBox, COLORS, get_color_from_hex
from app.utils.responsive import scaled_font, is_cover_mode


class NavTab(Button):
    """Individual navigation tab button."""

    is_active = False

    def __init__(self, title, icon='', **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.icon = icon
        self.background_normal = ''
        self.background_color = (1, 1, 1, 0)  # Transparent
        self.color = get_color_from_hex(COLORS['nav_text'])
        self.font_size = scaled_font(14)
        self.bold = False
        self.size_hint_x = 1

        self._update_text()

    def _update_text(self):
        """Update button text based on screen size."""
        if is_cover_mode():
            # Show icon only on cover screen
            self.text = self.icon if self.icon else self.title[:1]
        else:
            # Show full text on main screen
            self.text = f'{self.icon} {self.title}' if self.icon else self.title

    def set_active(self, active):
        """Set active state and update styling."""
        self.is_active = active
        if active:
            self.bold = True
            self.background_color = get_color_from_hex(COLORS['primary_dark'])
        else:
            self.bold = False
            self.background_color = (1, 1, 1, 0)


class TopNavBar(ColoredBox):
    """Top navigation bar with tabs for screen switching."""

    active_tab = StringProperty('home')
    on_tab_select = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = COLORS['nav_bg']
        self.orientation = 'vertical'
        self.size_hint_y = None
        self._update_height()

        # App title bar
        title_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(56),
            padding=[dp(16), 0]
        )

        from kivy.uix.label import Label
        title_label = Label(
            text='TCG Tool',
            font_size=scaled_font(20),
            bold=True,
            color=get_color_from_hex(COLORS['nav_text']),
            size_hint_x=1,
            halign='left',
            valign='middle'
        )
        title_label.bind(size=lambda *x: setattr(title_label, 'text_size', (title_label.width, None)))
        title_bar.add_widget(title_label)

        self.add_widget(title_bar)

        # Tab bar
        self.tab_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(48),
            spacing=dp(2)
        )

        # Create tabs
        self.tabs = {
            'home': NavTab('Início', '🏠'),
            'meta': NavTab('Meta', '📊'),
            'decks': NavTab('Decks', '🎴'),
            'battles': NavTab('Batalhas', '⚔️'),
            'chat': NavTab('Chat', '💬'),
        }

        for tab_id, tab in self.tabs.items():
            tab.bind(on_press=lambda btn, tid=tab_id: self._on_tab_pressed(tid))
            self.tab_bar.add_widget(tab)

        self.add_widget(self.tab_bar)

        # Set initial active tab
        self._update_active_tab()

        # Bind to window size changes for responsiveness
        from kivy.core.window import Window
        Window.bind(size=self._on_window_resize)

    def _update_height(self):
        """Update navbar height based on screen mode."""
        if is_cover_mode():
            self.height = dp(90)  # Compact for cover screen
        else:
            self.height = dp(104)  # Full height for main screen

    def _on_window_resize(self, instance, value):
        """Handle window resize to update responsive elements."""
        self._update_height()
        # Update all tab texts
        for tab in self.tabs.values():
            tab._update_text()

    def _on_tab_pressed(self, tab_id):
        """Handle tab press event."""
        self.active_tab = tab_id
        self._update_active_tab()

        # Call callback if set
        if self.on_tab_select:
            self.on_tab_select(tab_id)

    def _update_active_tab(self):
        """Update visual state of tabs."""
        for tab_id, tab in self.tabs.items():
            tab.set_active(tab_id == self.active_tab)

    def set_active_tab(self, tab_id):
        """Programmatically set active tab."""
        if tab_id in self.tabs:
            self.active_tab = tab_id
            self._update_active_tab()
