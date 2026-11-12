from __future__ import annotations

from pygame import Rect

from ..geometry import Point
from .character_palette import CharacterPalette
from .expression import Expression
from .mood import Mood
from .painter import Painter


class NeutralExpression(Expression):
    """Mouth a straight line, brows level; idles by wandering his eyes about."""

    RESTING_MOUTH = Rect(33, 37, 6, 1)

    @property
    def mood(self) -> Mood:
        return Mood.NEUTRAL

    def paint_brows(self, painter: Painter) -> None:
        painter.line(CharacterPalette.HAIR, Point(27, 23), Point(33, 24), width=2)
        painter.line(CharacterPalette.HAIR, Point(39, 24), Point(45, 23), width=2)

    def _paint_resting_mouth(self, painter: Painter) -> None:
        painter.rect(CharacterPalette.MOUTH, self.RESTING_MOUTH)
