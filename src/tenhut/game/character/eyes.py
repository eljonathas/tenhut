from __future__ import annotations

from typing import Final

from pygame import Rect

from ..geometry import Point
from ..painting import Palette
from .character_palette import CharacterPalette
from .character_state import CharacterState
from .expression import Expression
from .painter import Painter


class Eyes:
    """Both eyes: open with a pupil that follows the gaze, blinking, or shut in satisfaction."""

    LEFT_EYE_COLUMN: Final = 28
    RIGHT_EYE_COLUMN: Final = 39
    EYE_ROW: Final = 27
    EYE_WIDTH: Final = 5
    PUPIL_SIZE: Final = 2
    PUPIL_MAX_COLUMN: Final = 3
    LOOKING_DOWN_FROM: Final = 0.35
    LOOKING_UP_FROM: Final = -0.5
    PUPIL_CENTER_COLUMN: Final = 1.5

    def paint(self, painter: Painter, state: CharacterState, expression: Expression) -> None:
        for column in (self.LEFT_EYE_COLUMN, self.RIGHT_EYE_COLUMN):
            if expression.has_content_eyes(state):
                self._paint_content(painter, column)
            elif state.blinking:
                painter.rect(CharacterPalette.BLACK, Rect(column, self.EYE_ROW + 1, self.EYE_WIDTH, 1))
            else:
                self._paint_open(painter, column, state, expression)

    @staticmethod
    def _paint_content(painter: Painter, column: int) -> None:
        painter.pixel(CharacterPalette.BLACK, Point(column, 28))
        painter.rect(CharacterPalette.BLACK, Rect(column + 1, 27, 3, 1))
        painter.pixel(CharacterPalette.BLACK, Point(column + 4, 28))

    def _paint_open(self, painter: Painter, column: int, state: CharacterState, expression: Expression) -> None:
        white = Rect(column, self.EYE_ROW, self.EYE_WIDTH, 3)
        painter.rect(Palette.WHITE, white)
        pupil = self._pupil_position(column, state.look)
        painter.rect(CharacterPalette.BLACK, Rect(pupil, (self.PUPIL_SIZE, self.PUPIL_SIZE)))
        painter.pixel(CharacterPalette.PUPIL_GLINT, pupil)
        if state.squinting or expression.always_squints:
            painter.rect(expression.skin.shade, Rect(column, self.EYE_ROW, self.EYE_WIDTH, 1))

    def _pupil_position(self, column: int, look: Point) -> Point:
        across = max(0, min(self.PUPIL_MAX_COLUMN, round(self.PUPIL_CENTER_COLUMN + 1.5 * look.x)))
        if look.y < self.LOOKING_UP_FROM:
            row = self.EYE_ROW - 1
        else:
            row = self.EYE_ROW + (1 if look.y > self.LOOKING_DOWN_FROM else 0)
        return Point(column + across, max(self.EYE_ROW, row))
