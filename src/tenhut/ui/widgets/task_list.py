from __future__ import annotations

from collections.abc import Callable

import pygame

from tenhut.core import Session, Task
from tenhut.game.animations import Lettering
from tenhut.game.geometry import Point
from tenhut.i18n import t
from tenhut.ui.painting import TextAlign, TextStyle, UiCanvas, UiPalette

from .task_area import TaskArea
from .task_marker import TaskMarker
from .task_row import TaskRow
from .task_scroll import TaskScroll


class TaskList:
    """The mission's tasks, one per line, scrollable; clicking a line hands its index to ``on_press``."""

    ROW_HEIGHT = 15
    HIT_HEIGHT = 14
    BOX_SIZE = 10
    LABEL_INDENT = 15
    LABEL_MARGIN = 16
    MIN_LABEL = 3
    COUNTER_LIFT = 13

    def __init__(
        self, session: Session, marker: TaskMarker, scroll: TaskScroll, *, on_press: Callable[[int], None]
    ) -> None:
        self._session = session
        self._marker = marker
        self._scroll = scroll
        self._on_press = on_press
        self._rows: list[TaskRow] = []

    def draw(self, canvas: UiCanvas, area: TaskArea) -> None:
        fonts = canvas.fonts
        tasks = self._session.tasks
        origin, width, max_rows = area.origin, area.width, area.rows
        self._rows = []
        offset = self._scroll.clamp(len(tasks), max_rows)
        if not tasks:
            canvas.write(t("board.tasks.empty"), origin, TextStyle(fonts.small, UiPalette.CHALK_DIM))
            return
        for position, task in enumerate(tasks[offset : offset + max_rows]):
            row = pygame.Rect(origin.x, origin.y + position * self.ROW_HEIGHT, width, self.HIT_HEIGHT)
            self._marker.draw(canvas, pygame.Rect(row.x, row.y + 1, self.BOX_SIZE, self.BOX_SIZE), task.done)
            self._draw_label(canvas, task, row)
            self._rows.append(TaskRow(row, position + offset))
        if len(tasks) > max_rows:
            counter = f"▲▼ {offset + 1}-{min(len(tasks), offset + max_rows)}/{len(tasks)}"
            canvas.write(
                counter,
                Point(origin.x + width, origin.y - self.COUNTER_LIFT),
                TextStyle(fonts.small, UiPalette.CHALK_DIM, TextAlign.RIGHT),
            )

    def click(self, position: tuple[int, int]) -> bool:
        """Presses the task under ``position``; False when there is none."""
        for row in self._rows:
            if row.rect.collidepoint(position):
                self._on_press(row.index)
                return True
        return False

    def _draw_label(self, canvas: UiCanvas, task: Task, row: pygame.Rect) -> None:
        font = canvas.fonts.body
        label = task.text
        while font.size(label)[0] > row.w - self.LABEL_MARGIN and len(label) > self.MIN_LABEL:
            label = label[:-2]
        if label != task.text:
            label = label[:-1] + Lettering.ELLIPSIS
        color = UiPalette.CHALK_DIM if task.done else UiPalette.CHALK
        written = canvas.write(label, Point(row.x + self.LABEL_INDENT, row.y), TextStyle(font, color))
        if task.done:
            canvas.shapes.line(
                UiPalette.CHALK_DIM, (written.x, written.centery + 1), (written.right, written.centery + 1)
            )
