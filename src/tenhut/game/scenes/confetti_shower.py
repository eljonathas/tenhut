from __future__ import annotations

import math
from dataclasses import dataclass
from typing import ClassVar

from ..painting import Canvas, Rgb
from ..random_source import RandomSource
from .parade_frame import ParadeFrame


@dataclass(slots=True)
class _Sheet:
    x: float
    y: float
    fall_speed: float
    flutter_phase: float
    color: Rgb


class ConfettiShower:
    """Paper confetti drifting down the whole parade; more of it falls when the party is on."""

    PARTY_SHEETS: ClassVar[int] = 70
    CALM_SHEETS: ClassVar[int] = 30
    # Fixed 1/30 s per drawn frame, like the other parade objects (they advance only while the parade is on screen).
    FRAME_STEP: ClassVar[float] = 1 / 30
    FLUTTER_RATE: ClassVar[float] = 2
    FLUTTER_REACH: ClassVar[float] = 0.4
    TUMBLE_RATE: ClassVar[float] = 6
    BACK_SHADE: ClassVar[float] = 0.7
    COLORS: ClassVar[tuple[Rgb, ...]] = (
        Rgb(240, 80, 80),
        Rgb(250, 214, 90),
        Rgb(110, 180, 110),
        Rgb(110, 150, 230),
        Rgb(245, 245, 245),
    )

    def __init__(self) -> None:
        self._sheets: list[_Sheet] = []

    def draw(self, canvas: Canvas, frame: ParadeFrame) -> None:
        width, height = canvas.surface.get_size()
        wanted = self.PARTY_SHEETS if frame.party else self.CALM_SHEETS
        while len(self._sheets) < wanted:
            self._sheets.append(self._new_sheet(width, height, frame.randomness))
        for sheet in self._sheets:
            self._fall(sheet, frame, (width, height))
            if 0 <= sheet.x < width and 0 <= sheet.y < height:
                self._draw_sheet(canvas, sheet, frame.elapsed)

    @classmethod
    def _new_sheet(cls, width: int, height: int, randomness: RandomSource) -> _Sheet:
        return _Sheet(
            randomness.uniform(0, width),
            randomness.uniform(-height, 0),
            randomness.uniform(6, 14),
            randomness.uniform(0, 6),
            randomness.choice(cls.COLORS),
        )

    def _fall(self, sheet: _Sheet, frame: ParadeFrame, world: tuple[int, int]) -> None:
        sheet.y += sheet.fall_speed * self.FRAME_STEP
        sheet.x += math.sin(frame.elapsed * self.FLUTTER_RATE + sheet.flutter_phase) * self.FLUTTER_REACH
        if sheet.y > world[1]:
            sheet.x, sheet.y = frame.randomness.uniform(0, world[0]), frame.randomness.uniform(-20, 0)

    def _draw_sheet(self, canvas: Canvas, sheet: _Sheet, elapsed: float) -> None:
        face_up = int(elapsed * self.TUMBLE_RATE + sheet.flutter_phase) % 2
        color = sheet.color if face_up else sheet.color.shaded(self.BACK_SHADE)
        canvas.rect(color, (int(sheet.x), int(sheet.y), 2 if face_up else 1, 1 if face_up else 2))
