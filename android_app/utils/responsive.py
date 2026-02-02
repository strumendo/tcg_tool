"""
Responsive Layout Utilities for Samsung Galaxy Z Fold 6

This module provides utilities for detecting screen mode and adapting
layouts for foldable devices.

Samsung Galaxy Z Fold 6 Specifications:
- Cover Screen: ~6.2" diagonal, 904x2316 pixels (~25:9 aspect ratio)
- Main Screen: ~7.6" diagonal, 1812x2176 pixels (~4:3 aspect ratio)
"""

from kivy.core.window import Window
from kivy.event import EventDispatcher
from kivy.properties import (
    StringProperty,
    NumericProperty,
    BooleanProperty,
    ListProperty
)
from kivy.metrics import dp, sp
from kivy.clock import Clock


class ScreenMode:
    """Screen mode constants."""
    COVER = 'cover'       # Narrow cover screen (folded)
    MAIN = 'main'         # Large main screen (unfolded)
    PHONE = 'phone'       # Regular phone screen
    TABLET = 'tablet'     # Tablet screen


class ResponsiveManager(EventDispatcher):
    """
    Manager for responsive layouts on foldable devices.

    Detects screen mode and provides layout parameters based on
    current screen dimensions.

    Usage:
        responsive = ResponsiveManager()

        # Get current mode
        if responsive.is_cover_mode:
            # Use compact layout
        else:
            # Use expanded layout

        # Bind to mode changes
        responsive.bind(screen_mode=my_callback)
    """

    # Properties
    screen_mode = StringProperty(ScreenMode.PHONE)
    screen_width = NumericProperty(0)
    screen_height = NumericProperty(0)
    aspect_ratio = NumericProperty(1.0)

    # Boolean helpers
    is_cover_mode = BooleanProperty(False)
    is_main_mode = BooleanProperty(False)
    is_foldable = BooleanProperty(False)
    is_landscape = BooleanProperty(False)

    # Layout parameters (updated based on mode)
    grid_columns = NumericProperty(1)
    card_height = NumericProperty(120)
    font_scale = NumericProperty(1.0)
    padding = NumericProperty(12)
    spacing = NumericProperty(10)

    # Breakpoints (in dp)
    COVER_MAX_WIDTH = 400      # Cover screen max width
    MAIN_MIN_WIDTH = 600       # Main screen min width
    TABLET_MIN_WIDTH = 800     # Tablet min width

    # Aspect ratio thresholds
    NARROW_RATIO = 2.5         # Cover screen is very narrow (~25:9 = 2.78)
    WIDE_RATIO = 1.5           # Below this is considered tablet-like

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._update_scheduled = None

        # Initial detection
        self._detect_mode()

        # Bind to window size changes
        Window.bind(size=self._on_window_resize)

    def _on_window_resize(self, instance, size):
        """Handle window resize - schedule mode detection."""
        if self._update_scheduled:
            self._update_scheduled.cancel()
        self._update_scheduled = Clock.schedule_once(
            lambda dt: self._detect_mode(), 0.1
        )

    def _detect_mode(self):
        """Detect current screen mode based on dimensions."""
        width = Window.width
        height = Window.height

        self.screen_width = width
        self.screen_height = height

        # Calculate aspect ratio (height/width for portrait orientation)
        if width > 0:
            self.aspect_ratio = height / width if height > width else width / height

        self.is_landscape = width > height

        # Detect foldable and specific mode
        width_dp = width / Window.density if Window.density else width

        # Determine screen mode
        if self.aspect_ratio >= self.NARROW_RATIO:
            # Very narrow screen - Cover mode
            self.screen_mode = ScreenMode.COVER
            self.is_cover_mode = True
            self.is_main_mode = False
            self.is_foldable = True
        elif width_dp >= self.MAIN_MIN_WIDTH and self.aspect_ratio < self.WIDE_RATIO:
            # Wide screen with tablet-like ratio - Main mode
            self.screen_mode = ScreenMode.MAIN
            self.is_cover_mode = False
            self.is_main_mode = True
            self.is_foldable = True
        elif width_dp >= self.TABLET_MIN_WIDTH:
            # Very wide - Tablet mode
            self.screen_mode = ScreenMode.TABLET
            self.is_cover_mode = False
            self.is_main_mode = False
            self.is_foldable = False
        else:
            # Regular phone
            self.screen_mode = ScreenMode.PHONE
            self.is_cover_mode = False
            self.is_main_mode = False
            self.is_foldable = False

        # Update layout parameters
        self._update_layout_params()

    def _update_layout_params(self):
        """Update layout parameters based on current mode."""
        if self.screen_mode == ScreenMode.COVER:
            # Compact layout for cover screen
            self.grid_columns = 1
            self.card_height = dp(100)
            self.font_scale = 0.9
            self.padding = dp(8)
            self.spacing = dp(6)

        elif self.screen_mode == ScreenMode.MAIN:
            # Expanded layout for main screen
            self.grid_columns = 2
            self.card_height = dp(140)
            self.font_scale = 1.1
            self.padding = dp(16)
            self.spacing = dp(12)

        elif self.screen_mode == ScreenMode.TABLET:
            # Large layout for tablets
            self.grid_columns = 3
            self.card_height = dp(160)
            self.font_scale = 1.2
            self.padding = dp(20)
            self.spacing = dp(16)

        else:
            # Standard phone layout
            self.grid_columns = 1
            self.card_height = dp(120)
            self.font_scale = 1.0
            self.padding = dp(12)
            self.spacing = dp(10)

    def get_scaled_font(self, base_sp: float) -> float:
        """Get scaled font size based on current mode."""
        return sp(base_sp * self.font_scale)

    def get_layout_params(self) -> dict:
        """Get all layout parameters as a dictionary."""
        return {
            'mode': self.screen_mode,
            'is_cover': self.is_cover_mode,
            'is_main': self.is_main_mode,
            'is_foldable': self.is_foldable,
            'is_landscape': self.is_landscape,
            'grid_columns': self.grid_columns,
            'card_height': self.card_height,
            'font_scale': self.font_scale,
            'padding': self.padding,
            'spacing': self.spacing,
            'screen_width': self.screen_width,
            'screen_height': self.screen_height,
        }

    def should_use_side_panel(self) -> bool:
        """Check if side panel layout should be used."""
        return self.screen_mode in (ScreenMode.MAIN, ScreenMode.TABLET)

    def get_optimal_columns(self, item_min_width: float = 150) -> int:
        """Calculate optimal number of columns based on item width."""
        available_width = self.screen_width - (self.padding * 2)
        columns = max(1, int(available_width / dp(item_min_width)))

        # Limit based on mode
        if self.screen_mode == ScreenMode.COVER:
            return min(columns, 2)
        elif self.screen_mode == ScreenMode.MAIN:
            return min(columns, 3)
        else:
            return min(columns, 4)


# Singleton instance
_responsive_manager = None


def get_responsive_manager() -> ResponsiveManager:
    """Get the singleton ResponsiveManager instance."""
    global _responsive_manager
    if _responsive_manager is None:
        _responsive_manager = ResponsiveManager()
    return _responsive_manager


# Convenience functions
def is_cover_mode() -> bool:
    """Check if currently in cover screen mode."""
    return get_responsive_manager().is_cover_mode


def is_main_mode() -> bool:
    """Check if currently in main screen mode."""
    return get_responsive_manager().is_main_mode


def is_foldable() -> bool:
    """Check if device is detected as foldable."""
    return get_responsive_manager().is_foldable


def get_grid_columns() -> int:
    """Get recommended number of grid columns."""
    return get_responsive_manager().grid_columns


def get_card_height() -> float:
    """Get recommended card height."""
    return get_responsive_manager().card_height


def scaled_font(base_sp: float) -> float:
    """Get scaled font size."""
    return get_responsive_manager().get_scaled_font(base_sp)


def get_padding() -> float:
    """Get recommended padding."""
    return get_responsive_manager().padding


def get_spacing() -> float:
    """Get recommended spacing."""
    return get_responsive_manager().spacing
