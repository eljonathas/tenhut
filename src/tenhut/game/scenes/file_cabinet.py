from __future__ import annotations

from typing import ClassVar

from ..painting import Canvas, Palette, Rgb


class FileCabinet:
    """A steel filing cabinet with three drawers, standing on the floor against the back wall."""

    STEEL: ClassVar[Rgb] = Rgb(120, 128, 112)
    DRAWER: ClassVar[Rgb] = Rgb(96, 104, 90)
    HANDLE: ClassVar[Rgb] = Rgb(210, 210, 200)
    DRAWERS: ClassVar[int] = 3
    WIDTH: ClassVar[int] = 14

    def __init__(self, left: int, floor_y: int, height: int) -> None:
        self._left = left
        self._floor_y = floor_y
        self._height = height

    def draw(self, canvas: Canvas) -> None:
        left, top, height = self._left, self._floor_y - self._height, self._height
        canvas.rect(Palette.OUTLINE, (left - 1, top - 1, self.WIDTH + 2, height + 1))
        canvas.rect(self.STEEL, (left, top, self.WIDTH, height))
        slot = height // self.DRAWERS
        for drawer in range(self.DRAWERS):
            y = top + 2 + drawer * slot
            canvas.rect(self.DRAWER, (left + 1, y, 12, slot - 2), border=1)
            canvas.rect(self.HANDLE, (left + 5, y + 2, 4, 1))
