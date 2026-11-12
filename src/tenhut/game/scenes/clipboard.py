from __future__ import annotations

from typing import ClassVar

import pygame

from tenhut.core import Task

from ..geometry import Point
from ..painting import Canvas, Palette, Rgb


class Clipboard:
    """The mission checklist seen in perspective on the desk, redrawn each frame with the real tasks."""

    BOARD: ClassVar[Rgb] = Rgb(150, 104, 56)
    PAPER: ClassVar[Rgb] = Rgb(246, 244, 232)
    CLIP: ClassVar[Rgb] = Rgb(180, 184, 192)
    CLIP_SHINE: ClassVar[Rgb] = Rgb(220, 224, 230)
    CLIP_SPRING: ClassVar[Rgb] = Rgb(110, 114, 124)
    TITLE: ClassVar[Rgb] = Rgb(200, 40, 40)
    CHECKBOX: ClassVar[Rgb] = Rgb(60, 60, 80)
    TEXT_PENDING: ClassVar[Rgb] = Rgb(90, 90, 110)
    TEXT_DONE: ClassVar[Rgb] = Rgb(170, 170, 186)
    TICK: ClassVar[Rgb] = Rgb(40, 150, 60)
    TAPER: ClassVar[int] = 3
    MAX_ROWS: ClassVar[int] = 6
    PLACEHOLDER_ROWS: ClassVar[int] = 3
    ROW_HEIGHT: ClassVar[int] = 6
    TEXT_INDENT: ClassVar[int] = 20

    def __init__(self, area: pygame.Rect) -> None:
        self._area = area

    def draw(self, canvas: Canvas, tasks: tuple[Task, ...], offset: Point) -> None:
        area = self._area.move(offset.x, offset.y)
        self._draw_board(canvas, area)
        self._draw_clip(canvas, area)
        canvas.line(self.TITLE, (area.x + 10, area.y + 7), (area.x + 10 + min(20, area.width - 18), area.y + 7))
        self._draw_rows(canvas, area, tasks[: self.MAX_ROWS] if tasks else (Task(""),) * self.PLACEHOLDER_ROWS)

    def _draw_board(self, canvas: Canvas, area: pygame.Rect) -> None:
        x, y, width, height, taper = area.x, area.y, area.width, area.height, self.TAPER
        canvas.polygon(
            Palette.OUTLINE,
            [(x + taper - 1, y - 1), (x + width - taper + 1, y - 1), (x + width + 1, y + height), (x - 1, y + height)],
        )
        canvas.polygon(self.BOARD, [(x + taper, y), (x + width - taper, y), (x + width, y + height), (x, y + height)])
        canvas.polygon(
            self.PAPER,
            [
                (x + 4 + taper - 1, y + 4),
                (x + width - 4 - taper + 1, y + 4),
                (x + width - 3, y + height),
                (x + 3, y + height),
            ],
        )

    def _draw_clip(self, canvas: Canvas, area: pygame.Rect) -> None:
        center, y = area.x + area.width // 2, area.y
        canvas.rect(Palette.OUTLINE, (center - 8, y - 3, 16, 6))
        canvas.rect(self.CLIP, (center - 7, y - 2, 14, 4))
        canvas.rect(self.CLIP_SHINE, (center - 7, y - 2, 14, 1))
        canvas.rect(self.CLIP_SPRING, (center - 2, y - 2, 4, 2))

    def _draw_rows(self, canvas: Canvas, area: pygame.Rect, rows: tuple[Task, ...]) -> None:
        row_y = area.y + 11
        for task in rows:
            if row_y + 4 > area.y + area.height - 1:
                break
            self._draw_row(canvas, Point(area.x + 7, row_y), task)
            row_y += self.ROW_HEIGHT

    def _draw_row(self, canvas: Canvas, box: Point, task: Task) -> None:
        canvas.rect(self.CHECKBOX, (box.x, box.y, 4, 4), border=1)
        text_color = self.TEXT_DONE if task.done else self.TEXT_PENDING
        text_width = self._area.width - self.TEXT_INDENT
        canvas.line(text_color, (box.x + 7, box.y + 2), (box.x + 7 + text_width, box.y + 2))
        if task.done:
            canvas.line(self.TICK, (box.x, box.y + 2), (box.x + 1, box.y + 4))
            canvas.line(self.TICK, (box.x + 1, box.y + 4), (box.x + 5, box.y - 1))
