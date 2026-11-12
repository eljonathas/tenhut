from __future__ import annotations

import pygame

from tenhut.ui.painting import UiCanvas, UiPalette

from .bar_fill import BarFill


class SegmentedBar:
    """A progress bar made of blocks."""

    SEGMENTS = 24

    def draw(self, canvas: UiCanvas, area: pygame.Rect, fill: BarFill) -> None:
        canvas.shapes.rect(UiPalette.BOARD_DARK, area)
        filled = int(fill.fraction * self.SEGMENTS)
        width = area.w / self.SEGMENTS
        for index in range(self.SEGMENTS):
            shade = fill.color if index < filled else UiPalette.PROGRESS_EMPTY
            canvas.shapes.rect(shade, (area.x + int(index * width) + 1, area.y + 1, max(1, int(width) - 1), area.h - 2))
