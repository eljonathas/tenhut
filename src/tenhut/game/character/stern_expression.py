from __future__ import annotations

from typing import ClassVar, Final

from ..geometry import Point
from ..random_source import RandomSource
from .character_palette import CharacterPalette
from .glance import Glance
from .mood import Mood
from .neutral_expression import NeutralExpression
from .painter import Painter


class SternExpression(NeutralExpression):
    """Frowning brows; keeps watch by scanning the room and squinting at it."""

    GUARD_COLUMNS: Final = (-1.0, -0.6, 0.0, 0.6, 1.0)
    GUARD_ROWS: Final = (0.0, 0.0, 0.5)
    SQUINT_CHANCE: Final = 0.35

    brow_drop: ClassVar[int] = 0

    @property
    def mood(self) -> Mood:
        return Mood.STERN

    def choose_glance(self, randomness: RandomSource) -> Glance:
        target = Point(randomness.choice(self.GUARD_COLUMNS), randomness.choice(self.GUARD_ROWS))
        return Glance(target, squint=randomness.random() < self.SQUINT_CHANCE)

    def paint_brows(self, painter: Painter) -> None:
        drop = self.brow_drop
        painter.line(CharacterPalette.HAIR, Point(27, 23), Point(33, 25 + drop), width=2)
        painter.line(CharacterPalette.HAIR, Point(45, 23), Point(39, 25 + drop), width=2)
        painter.line(CharacterPalette.HAIR_DARK, Point(27, 24), Point(33, 26 + drop))
        painter.line(CharacterPalette.HAIR_DARK, Point(45, 24), Point(39, 26 + drop))
