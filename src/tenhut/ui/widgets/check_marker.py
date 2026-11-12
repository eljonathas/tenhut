from __future__ import annotations

import pygame

from tenhut.game.geometry import Point
from tenhut.ui.painting import UiCanvas, UiPalette

from .task_marker import TaskMarker


class CheckMarker(TaskMarker):
    """An empty box that gets a tick when the task is done."""

    TICK = ((2, 5), (4, 8), (9, 1))

    def draw(self, canvas: UiCanvas, box: pygame.Rect, done: bool) -> None:
        canvas.shapes.rect(UiPalette.CHALK, box, border=1)
        if done:
            start, corner, end = (Point(box.x + dx, box.y + dy) for dx, dy in self.TICK)
            canvas.shapes.line(UiPalette.YELLOW, start, corner, width=2)
            canvas.shapes.line(UiPalette.YELLOW, corner, end, width=2)
