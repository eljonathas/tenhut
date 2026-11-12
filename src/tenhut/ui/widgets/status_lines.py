from __future__ import annotations

import pygame

from tenhut.controllers.status_line import StatusLine
from tenhut.game.animations import Lettering
from tenhut.game.geometry import Point
from tenhut.ui.painting import TextStyle, UiCanvas

from .severity_tint import SeverityTint


class StatusLines:
    """The lines at the bottom of the board, stacked upwards from its lower edge."""

    LINE_HEIGHT = 12
    BOTTOM_MARGIN = 4
    SIDE_MARGIN = 8
    FIT_MARGIN = 12

    def draw(self, canvas: UiCanvas, area: pygame.Rect, lines: list[StatusLine]) -> None:
        font = canvas.fonts.small
        y = area.bottom - self.BOTTOM_MARGIN - len(lines) * self.LINE_HEIGHT
        for line in lines:
            text = Lettering(font).fitted(line.text, area.w - self.FIT_MARGIN)
            canvas.write(text, Point(area.x + self.SIDE_MARGIN, y), TextStyle(font, SeverityTint.of(line.severity)))
            y += self.LINE_HEIGHT
