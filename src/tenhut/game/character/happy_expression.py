from __future__ import annotations

from pygame import Rect

from ..geometry import Point
from .character_palette import CharacterPalette
from .character_state import CharacterState
from .mood import Mood
from .neutral_expression import NeutralExpression
from .painter import Painter


class HappyExpression(NeutralExpression):
    """Raised brows, a smile with blushing cheeks; his eyes close in delight for three seconds out of every nine."""

    CONTENT_EYES_STEP = 3
    CONTENT_EYES_CYCLE = 3
    LEFT_CHEEK = Rect(27, 31, 2, 1)
    RIGHT_CHEEK = Rect(43, 31, 2, 1)
    SMILE = Rect(32, 37, 8, 1)
    SMILE_CORNERS = (Point(31, 36), Point(40, 36))
    LOWER_LIP = Rect(33, 38, 6, 1)

    @property
    def mood(self) -> Mood:
        return Mood.HAPPY

    def has_content_eyes(self, state: CharacterState) -> bool:
        return not state.talking and int(state.elapsed / self.CONTENT_EYES_STEP) % self.CONTENT_EYES_CYCLE == 0

    def paint_cheeks(self, painter: Painter) -> None:
        painter.rect(CharacterPalette.CHEEK, self.LEFT_CHEEK)
        painter.rect(CharacterPalette.CHEEK, self.RIGHT_CHEEK)

    def paint_brows(self, painter: Painter) -> None:
        hair = CharacterPalette.HAIR
        painter.line(hair, Point(27, 24), Point(30, 22), width=2)
        painter.line(hair, Point(30, 22), Point(33, 23), width=2)
        painter.line(hair, Point(39, 23), Point(42, 22), width=2)
        painter.line(hair, Point(42, 22), Point(45, 24), width=2)

    def _paint_resting_mouth(self, painter: Painter) -> None:
        painter.rect(CharacterPalette.MOUTH, self.SMILE)
        for corner in self.SMILE_CORNERS:
            painter.pixel(CharacterPalette.MOUTH, corner)
        painter.rect(self.skin.base, self.LOWER_LIP)
