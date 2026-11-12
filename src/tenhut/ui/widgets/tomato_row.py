from __future__ import annotations

from tenhut.game.geometry import Point
from tenhut.ui.painting import UiCanvas, UiPalette

from .cycle_progress import CycleProgress


class TomatoRow:
    """One tomato per pomodoro of the cycle that leads to the long break; the finished ones are red."""

    SPACING = 14
    HALF_SPACING = 7
    LEFT_OFFSET = 2
    BODY_CENTER = (4, 88)
    BODY_RADIUS = 4
    STEM = (3, 82, 3, 2)

    def draw(self, canvas: UiCanvas, origin: Point, progress: CycleProgress) -> None:
        """Draws the row centred on ``origin.x`` and hanging from ``origin.y``."""
        finished = progress.finished
        for index in range(progress.per_cycle):
            left = origin.x - progress.per_cycle * self.HALF_SPACING + index * self.SPACING + self.LEFT_OFFSET
            ripe = index < finished
            canvas.shapes.circle(
                UiPalette.TOMATO if ripe else UiPalette.PROGRESS_EMPTY,
                (left + self.BODY_CENTER[0], origin.y + self.BODY_CENTER[1]),
                self.BODY_RADIUS,
            )
            stem_x, stem_y, stem_w, stem_h = self.STEM
            canvas.shapes.rect(
                UiPalette.TOMATO_STEM if ripe else UiPalette.PROGRESS_EMPTY,
                (left + stem_x, origin.y + stem_y, stem_w, stem_h),
            )
