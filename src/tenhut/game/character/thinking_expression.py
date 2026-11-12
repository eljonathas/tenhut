from __future__ import annotations

from typing import Final

from ..geometry import Point
from ..random_source import RandomSource
from .character_palette import CharacterPalette
from .glance import Glance
from .mood import Mood
from .neutral_expression import NeutralExpression
from .painter import Painter


class ThinkingExpression(NeutralExpression):
    """One brow raised; his eyes drift up to the ceiling, left or right."""

    CEILING_COLUMNS: Final = (-0.8, 0.8)
    CEILING_ROW: Final = -1.0

    @property
    def mood(self) -> Mood:
        return Mood.THINKING

    def choose_glance(self, randomness: RandomSource) -> Glance:
        return Glance(Point(randomness.choice(self.CEILING_COLUMNS), self.CEILING_ROW), squint=False)

    def paint_brows(self, painter: Painter) -> None:
        painter.line(CharacterPalette.HAIR, Point(27, 24), Point(33, 24), width=2)
        painter.line(CharacterPalette.HAIR, Point(39, 22), Point(45, 23), width=2)
