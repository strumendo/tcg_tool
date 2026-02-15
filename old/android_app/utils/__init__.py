"""Utilities module for TCG App."""
from .responsive import (
    ResponsiveManager,
    ScreenMode,
    get_responsive_manager,
    is_cover_mode,
    is_main_mode,
    is_foldable,
    get_grid_columns,
    get_card_height,
    scaled_font,
    get_padding,
    get_spacing,
)

__all__ = [
    'ResponsiveManager',
    'ScreenMode',
    'get_responsive_manager',
    'is_cover_mode',
    'is_main_mode',
    'is_foldable',
    'get_grid_columns',
    'get_card_height',
    'scaled_font',
    'get_padding',
    'get_spacing',
]
