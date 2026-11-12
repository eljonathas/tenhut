from __future__ import annotations

import pygame

from tenhut.game.geometry import Point
from tenhut.ui.painting import TextAlign, TextStyle, UiCanvas, UiPalette

from .task_marker import TaskMarker


class RemoveMarker(TaskMarker):
    """A red box with an x: clicking the task removes it."""

    def draw(self, canvas: UiCanvas, box: pygame.Rect, done: bool) -> None:
        canvas.shapes.rect(UiPalette.RED, box)
        canvas.write(
            "x", Point(box.centerx, box.centery - 1), TextStyle(canvas.fonts.small, UiPalette.CHALK, TextAlign.CENTER)
        )
