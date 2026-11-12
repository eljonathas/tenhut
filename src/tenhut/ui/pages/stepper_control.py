from __future__ import annotations

import pygame

from tenhut.controllers.settings import SettingsController
from tenhut.game.animations import Lettering
from tenhut.game.geometry import Point
from tenhut.ui.painting import TextAlign, TextStyle, UiCanvas, UiPalette

from .click_target import ClickTarget
from .row_adjustment import RowAdjustment
from .row_entry import RowEntry
from .row_frame import RowFrame
from .setting_control import SettingControl


class StepperControl(SettingControl):
    """A minus button, the value and a plus button."""

    BUTTON_WIDTH = 15
    RESERVED_WIDTH = 100
    MINUS_OFFSET = 86
    PLUS_OFFSET = 21
    VALUE_MARGIN = 4

    def __init__(self, settings: SettingsController) -> None:
        self._settings = settings

    @property
    def reserved_width(self) -> int:
        return self.RESERVED_WIDTH

    def draw(self, canvas: UiCanvas, frame: RowFrame, entry: RowEntry) -> list[ClickTarget]:
        row = entry.row
        right = frame.area.right
        minus = pygame.Rect(right - self.MINUS_OFFSET, frame.top, self.BUTTON_WIDTH, frame.control_height)
        plus = pygame.Rect(right - self.PLUS_OFFSET, frame.top, self.BUTTON_WIDTH, frame.control_height)
        for button, symbol in ((minus, "-"), (plus, "+")):
            canvas.shapes.rect(UiPalette.INK, button)
            canvas.shapes.rect(UiPalette.STEPPER, button.inflate(-2, -2))
            canvas.write(
                symbol,
                Point(button.centerx, button.centery - 1),
                TextStyle(canvas.fonts.body, UiPalette.INK, TextAlign.CENTER),
            )
        span = pygame.Rect(minus.right, minus.y, plus.x - minus.right, minus.h)
        self._draw_value(canvas, span, row.editor.shown(entry.value))
        return [
            ClickTarget(minus, RowAdjustment(self._settings, row, -1)),
            ClickTarget(plus, RowAdjustment(self._settings, row, 1)),
        ]

    def _draw_value(self, canvas: UiCanvas, span: pygame.Rect, shown: str) -> None:
        fonts = canvas.fonts
        room = span.w - self.VALUE_MARGIN
        font = fonts.body if fonts.body.size(shown)[0] <= room else fonts.small
        canvas.write(
            Lettering(font).fitted(shown, room),
            Point(span.centerx, span.centery),
            TextStyle(font, UiPalette.YELLOW, TextAlign.CENTER),
        )
