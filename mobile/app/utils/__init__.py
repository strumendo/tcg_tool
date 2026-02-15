"""
TCG Tool Mobile App - Utils Module

Exports responsive layout utilities
"""

from .responsive import (
    ScreenMode,
    ResponsiveManager,
    get_responsive_manager,
    is_cover_mode,
    is_main_mode,
    is_foldable,
    get_grid_columns,
    get_card_height,
    scaled_font,
    get_padding,
    get_spacing,
    get_screen_mode,
)

__all__ = [
    'ScreenMode',
    'ResponsiveManager',
    'get_responsive_manager',
    'is_cover_mode',
    'is_main_mode',
    'is_foldable',
    'get_grid_columns',
    'get_card_height',
    'scaled_font',
    'get_padding',
    'get_spacing',
    'get_screen_mode',
]
