from __future__ import annotations

from pygame import Rect

from ..geometry import Point
from ..painting import Palette
from .character_palette import CharacterPalette
from .mood import Mood
from .painter import Painter
from .skin_tone import SkinTone
from .stern_expression import SternExpression


class AngryExpression(SternExpression):
    """Red face, lowered brows, bared teeth; he stops breathing calmly and shouts whenever he talks."""

    breathes = False
    always_squints = True
    shouts_when_talking = True
    brow_drop = 1

    SHOUTING_MOUTH = Rect(32, 36, 8, 4)
    TONGUE = Rect(34, 38, 4, 1)
    GRITTED_MOUTH = Rect(32, 37, 8, 2)
    GRITTED_TEETH = Rect(32, 37, 8, 1)
    VEIN = (Point(29, 22), Point(30, 21))

    def __init__(self) -> None:
        super().__init__(SkinTone.flushed())

    @property
    def mood(self) -> Mood:
        return Mood.ANGRY

    def paint_forehead(self, painter: Painter) -> None:
        for point in self.VEIN:
            painter.pixel(self.skin.shade, point)

    def _paint_talking_mouth(self, painter: Painter) -> None:
        painter.rect(CharacterPalette.MOUTH, self.SHOUTING_MOUTH)
        painter.rect(Palette.WHITE, self.TEETH)
        painter.rect(Palette.RED, self.TONGUE)

    def _paint_resting_mouth(self, painter: Painter) -> None:
        painter.rect(CharacterPalette.MOUTH, self.GRITTED_MOUTH)
        painter.rect(Palette.WHITE, self.GRITTED_TEETH)
