from __future__ import annotations

import pygame

from tenhut.ui.painting import UiCanvas, UiPalette

from .bar_fill import BarFill


class FlatBar:
    """A thin solid progress bar."""

    def draw(self, canvas: UiCanvas, area: pygame.Rect, fill: BarFill) -> None:
        canvas.shapes.rect(UiPalette.BOARD_DARK, area)
        canvas.shapes.rect(fill.color, (area.x, area.y, int(area.w * fill.fraction), area.h))
