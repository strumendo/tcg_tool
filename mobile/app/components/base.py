"""
Base UI components for the TCG Tool mobile app.
Provides reusable styled widgets with responsive sizing.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.metrics import dp, sp
from kivy.properties import StringProperty, NumericProperty, ListProperty

from app.utils.responsive import get_responsive_manager, scaled_font, get_padding

# Color scheme
COLORS = {
    'background': '#f5f5f5', 'surface': '#ffffff', 'card': '#ffffff',
    'primary': '#4caf50', 'primary_dark': '#388e3c', 'secondary': '#2196f3',
    'accent': '#ff9800', 'danger': '#f44336', 'success': '#4caf50',
    'text': '#212121', 'text_secondary': '#757575', 'text_muted': '#9e9e9e',
    'border': '#e0e0e0', 'nav_bg': '#4caf50', 'nav_text': '#ffffff',
    'divider': '#eeeeee',
    'fire': '#ff9c54', 'water': '#4d90d5', 'lightning': '#f3d23b',
    'psychic': '#f97176', 'fighting': '#ce4069', 'darkness': '#5a5366',
    'metal': '#5a8ea1', 'grass': '#5fbd58', 'colorless': '#9099a1',
}


def get_color_from_hex(hex_color):
    """Convert hex color to Kivy RGBA format."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        r, g, b = tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
        return (r, g, b, 1)
    return (1, 1, 1, 1)


class ColoredBox(BoxLayout):
    """BoxLayout with background color and optional rounded corners."""

    bg_color = StringProperty('#ffffff')
    radius = ListProperty([0, 0, 0, 0])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._update_canvas, size=self._update_canvas, bg_color=self._update_canvas)
        self._update_canvas()

    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*get_color_from_hex(self.bg_color))
            RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)


class CardBox(BoxLayout):
    """Card-style container with shadow effect and border."""

    bg_color = StringProperty(COLORS['card'])
    border_color = StringProperty(COLORS['border'])
    radius = NumericProperty(dp(8))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.padding = get_padding()
        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self._update_canvas()

    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # Background
            Color(*get_color_from_hex(self.bg_color))
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[self.radius] * 4
            )
            # Border
            Color(*get_color_from_hex(self.border_color))
            Line(
                rounded_rectangle=(
                    self.x, self.y,
                    self.width, self.height,
                    self.radius
                ),
                width=dp(1)
            )


class PrimaryButton(Button):
    """Primary green button with responsive font sizing."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = get_color_from_hex(COLORS['primary'])
        self.color = get_color_from_hex(COLORS['nav_text'])
        self.font_size = scaled_font(16)
        self.size_hint_y = None
        self.height = dp(48)
        self.bold = True

        # Update background on state
        self.bind(state=self._update_background)

    def _update_background(self, instance, value):
        if value == 'down':
            self.background_color = get_color_from_hex(COLORS['primary_dark'])
        else:
            self.background_color = get_color_from_hex(COLORS['primary'])


class SecondaryButton(Button):
    """Secondary blue button with responsive font sizing."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = get_color_from_hex(COLORS['secondary'])
        self.color = get_color_from_hex(COLORS['nav_text'])
        self.font_size = scaled_font(16)
        self.size_hint_y = None
        self.height = dp(48)
        self.bold = True

        self.bind(state=self._update_background)

    def _update_background(self, instance, value):
        if value == 'down':
            self.background_color = get_color_from_hex('#1976d2')  # Darker blue
        else:
            self.background_color = get_color_from_hex(COLORS['secondary'])


class OutlineButton(Button):
    """Outlined button with border and transparent background."""

    outline_color = StringProperty(COLORS['primary'])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (1, 1, 1, 0)
        self.color = get_color_from_hex(self.outline_color)
        self.font_size = scaled_font(16)
        self.size_hint_y = None
        self.height = dp(48)
        self.bold = True

        self.bind(pos=self._update_canvas, size=self._update_canvas, outline_color=self._update_canvas)
        self._update_canvas()

    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*get_color_from_hex(self.outline_color))
            Line(
                rounded_rectangle=(
                    self.x, self.y,
                    self.width, self.height,
                    dp(4)
                ),
                width=dp(2)
            )
        self.color = get_color_from_hex(self.outline_color)


class LoadingSpinner(BoxLayout):
    """Simple loading indicator widget."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(10)
        self.padding = get_padding()

        # Spinner label with animation dots
        self.label = Label(
            text='Carregando...',
            font_size=scaled_font(16),
            color=get_color_from_hex(COLORS['text_secondary']),
            size_hint_y=None,
            height=dp(40)
        )
        self.add_widget(self.label)

        # Simple animation
        from kivy.clock import Clock
        self._dot_count = 0
        Clock.schedule_interval(self._animate, 0.5)

    def _animate(self, dt):
        self._dot_count = (self._dot_count + 1) % 4
        self.label.text = 'Carregando' + '.' * self._dot_count


class ErrorMessage(BoxLayout):
    """Error display widget with retry button."""

    message = StringProperty('Erro ao carregar dados')

    def __init__(self, on_retry=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(15)
        self.padding = get_padding()
        self.on_retry_callback = on_retry

        # Error icon/text
        error_label = Label(
            text=f'⚠️ {self.message}',
            font_size=scaled_font(14),
            color=get_color_from_hex(COLORS['danger']),
            size_hint_y=None,
            height=dp(60),
            halign='center',
            valign='middle',
            text_size=(None, None)
        )
        error_label.bind(size=lambda *x: setattr(error_label, 'text_size', (error_label.width, None)))
        self.add_widget(error_label)

        # Retry button
        if on_retry:
            retry_btn = SecondaryButton(
                text='Tentar Novamente',
                size_hint_x=None,
                width=dp(200),
                pos_hint={'center_x': 0.5}
            )
            retry_btn.bind(on_press=self._on_retry)
            self.add_widget(retry_btn)

        self.bind(message=self._update_message)

    def _update_message(self, instance, value):
        if len(self.children) > 0:
            self.children[-1].text = f'⚠️ {value}'

    def _on_retry(self, instance):
        if self.on_retry_callback:
            self.on_retry_callback()
