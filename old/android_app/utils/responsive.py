"""
Responsive Layout Utilities for Samsung Galaxy Z Fold 6

This module provides utilities for detecting screen mode and adapting
layouts for foldable devices.

Samsung Galaxy Z Fold 6 Specifications:
- Cover Screen: ~6.2" diagonal, 904x2316 pixels (~25:9 aspect ratio, ~968dp width)
- Main Screen: ~7.6" diagonal, 1812x2176 pixels (~4:3 aspect ratio, ~768dp width)

Note: High DPI screens (3.4x density) require proper dp/sp scaling.
"""

from kivy.core.window import Window
from kivy.event import EventDispatcher
from kivy.properties import (
    StringProperty,
    NumericProperty,
    BooleanProperty,
    ListProperty
)
from kivy.metrics import dp, sp, Metrics
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

    Samsung Galaxy Z Fold 6:
    - Cover: 904x2316px at ~3.4x density = ~266x681dp (very tall/narrow)
    - Main: 1812x2176px at ~2.4x density = ~755x907dp (almost square)

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
    screen_width_dp = NumericProperty(0)
    screen_height_dp = NumericProperty(0)
    aspect_ratio = NumericProperty(1.0)
    density = NumericProperty(1.0)

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

    # Component sizing
    nav_height = NumericProperty(56)
    button_height = NumericProperty(48)
    list_item_height = NumericProperty(72)
    icon_size = NumericProperty(24)
    touch_target = NumericProperty(48)  # Minimum touch target size

    # Breakpoints (in dp) - adjusted for Fold 6
    COVER_MAX_WIDTH = 320      # Cover screen is ~266dp wide
    MAIN_MIN_WIDTH = 500       # Main screen is ~755dp wide
    TABLET_MIN_WIDTH = 900     # Tablet min width

    # Aspect ratio thresholds
    NARROW_RATIO = 2.0         # Cover screen is very narrow (~2.56 in dp)
    WIDE_RATIO = 1.3           # Below this is considered tablet-like

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._update_scheduled = None
        self._initialized = False

        # Try initial detection synchronously with safe defaults
        try:
            self._detect_mode()
            self._initialized = True
        except Exception:
            # If detection fails, use safe defaults
            self._set_safe_defaults()

        # Bind to window size changes (will update when window is ready)
        try:
            Window.bind(size=self._on_window_resize)
        except Exception:
            pass

    def _set_safe_defaults(self):
        """Set safe default values when window is not ready."""
        self.screen_mode = ScreenMode.PHONE
        self.screen_width = 800
        self.screen_height = 1200
        self.screen_width_dp = 400
        self.screen_height_dp = 600
        self.aspect_ratio = 1.5
        self.density = 2.0
        self.is_landscape = False
        self.is_cover_mode = False
        self.is_main_mode = False
        self.is_foldable = False
        self._update_layout_params()

    def _on_window_resize(self, instance, size):
        """Handle window resize - schedule mode detection."""
        try:
            if self._update_scheduled:
                self._update_scheduled.cancel()
            self._update_scheduled = Clock.schedule_once(
                lambda dt: self._safe_detect_mode(), 0.1
            )
        except Exception:
            pass

    def _safe_detect_mode(self):
        """Safely detect mode with error handling."""
        try:
            self._detect_mode()
            self._initialized = True
        except Exception:
            if not self._initialized:
                self._set_safe_defaults()

    def _detect_mode(self, *args):
        """Detect current screen mode based on dimensions."""
        # Safely get window dimensions (may not be available on Android startup)
        try:
            width = Window.width or 800
            height = Window.height or 600
        except Exception:
            width, height = 800, 600

        self.screen_width = width
        self.screen_height = height

        # Get density safely (may not be available immediately on Android)
        density = 1.0
        try:
            density = getattr(Window, 'density', None)
            if density is None or density <= 0:
                density = getattr(Metrics, 'density', 1.0) or 1.0
        except Exception:
            try:
                density = Metrics.density or 1.0
            except Exception:
                density = 1.0

        self.density = density

        # Calculate dimensions in dp
        width_dp = width / density
        height_dp = height / density
        self.screen_width_dp = width_dp
        self.screen_height_dp = height_dp

        # Calculate aspect ratio (height/width for portrait orientation)
        if width_dp > 0:
            self.aspect_ratio = height_dp / width_dp if height_dp > width_dp else width_dp / height_dp

        self.is_landscape = width > height

        # Determine screen mode based on dp dimensions
        # Samsung Fold 6 Cover: ~266dp x 681dp (ratio ~2.56)
        # Samsung Fold 6 Main: ~755dp x 907dp (ratio ~1.2)
        if width_dp <= self.COVER_MAX_WIDTH or self.aspect_ratio >= self.NARROW_RATIO:
            # Very narrow screen or small width - Cover mode
            self.screen_mode = ScreenMode.COVER
            self.is_cover_mode = True
            self.is_main_mode = False
            self.is_foldable = True
        elif width_dp >= self.MAIN_MIN_WIDTH and self.aspect_ratio < self.WIDE_RATIO:
            # Wide screen with tablet-like ratio - Main mode (unfolded)
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
            # Compact layout for cover screen (Fold 6 Cover: ~266dp wide)
            # Use larger sizes for touch targets on narrow screen
            self.grid_columns = 1
            self.card_height = dp(88)
            self.font_scale = 1.0  # Keep readable on narrow screen
            self.padding = dp(12)
            self.spacing = dp(8)
            self.nav_height = dp(56)
            self.button_height = dp(48)
            self.list_item_height = dp(72)
            self.icon_size = dp(24)
            self.touch_target = dp(48)

        elif self.screen_mode == ScreenMode.MAIN:
            # Expanded layout for main screen (Fold 6 Main: ~755dp wide)
            # Use larger sizes for better visibility on bigger screen
            self.grid_columns = 2
            self.card_height = dp(120)
            self.font_scale = 1.15  # Slightly larger fonts
            self.padding = dp(20)
            self.spacing = dp(16)
            self.nav_height = dp(64)
            self.button_height = dp(52)
            self.list_item_height = dp(80)
            self.icon_size = dp(28)
            self.touch_target = dp(52)

        elif self.screen_mode == ScreenMode.TABLET:
            # Large layout for tablets
            self.grid_columns = 3
            self.card_height = dp(140)
            self.font_scale = 1.25
            self.padding = dp(24)
            self.spacing = dp(20)
            self.nav_height = dp(72)
            self.button_height = dp(56)
            self.list_item_height = dp(88)
            self.icon_size = dp(32)
            self.touch_target = dp(56)

        else:
            # Standard phone layout
            self.grid_columns = 1
            self.card_height = dp(96)
            self.font_scale = 1.0
            self.padding = dp(16)
            self.spacing = dp(12)
            self.nav_height = dp(56)
            self.button_height = dp(48)
            self.list_item_height = dp(72)
            self.icon_size = dp(24)
            self.touch_target = dp(48)

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
