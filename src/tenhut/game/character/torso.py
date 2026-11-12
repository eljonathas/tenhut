from __future__ import annotations

from pygame import Rect

from ..painting import Palette
from .belt import Belt
from .body_part import BodyPart
from .character_state import CharacterState
from .epaulettes import Epaulettes
from .medals import Medals
from .painter import Painter
from .placket import Placket


class Torso(BodyPart):
    """Shoulders and jacket, with everything pinned or buttoned on it."""

    LEFT_SHOULDER = Rect(13, 39, 18, 12)
    RIGHT_SHOULDER = Rect(41, 39, 18, 12)
    CHEST = Rect(19, 43, 34, 30)
    HIPS = Rect(18, 68, 36, 7)
    RIGHT_SHADE = Rect(48, 46, 5, 28)
    LEFT_LIGHT = Rect(19, 46, 2, 26)
    POCKETS = (Rect(22, 69, 8, 1), Rect(42, 69, 8, 1))

    def __init__(self) -> None:
        self._placket = Placket()
        self._medals = Medals()
        self._belt = Belt()
        self._epaulettes = Epaulettes()

    def paint(self, painter: Painter, state: CharacterState) -> None:
        self._paint_jacket(painter)
        turn_shift = state.turn // 2
        with painter.shifted(turn_shift):
            self._placket.paint(painter)
        self._medals.paint(painter)
        self._belt.paint(painter, turn_shift)
        for pocket in self.POCKETS:
            painter.rect(Palette.OLIVE_DARK, pocket)
        self._epaulettes.paint(painter)

    def _paint_jacket(self, painter: Painter) -> None:
        for shoulder in (self.LEFT_SHOULDER, self.RIGHT_SHOULDER):
            painter.ellipse(Palette.OLIVE, shoulder)
        painter.rect(Palette.OLIVE, self.CHEST)
        painter.rect(Palette.OLIVE, self.HIPS)
        painter.rect(Palette.OLIVE_DARK, self.RIGHT_SHADE)
        painter.rect(Palette.OLIVE_LIGHT, self.LEFT_LIGHT)
