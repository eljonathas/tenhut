from __future__ import annotations

from pygame import Rect

from ..painting import Palette
from .body_part import BodyPart
from .boots import Boots
from .character_palette import CharacterPalette
from .character_state import CharacterState
from .painter import Painter


class Legs(BodyPart):
    """Trousers with the general's red stripes, and the boots. They stay on the floor while the body breathes."""

    LEFT_TROUSER = Rect(26, 72, 9, 14)
    RIGHT_TROUSER = Rect(37, 72, 9, 14)
    LEFT_STRIPE = Rect(26, 72, 1, 13)
    RIGHT_STRIPE = Rect(45, 72, 1, 13)
    CREASE = Rect(35, 74, 2, 10)

    def __init__(self) -> None:
        self._boots = Boots()

    def paint(self, painter: Painter, state: CharacterState) -> None:
        floor = painter.grounded()
        floor.rect(Palette.OLIVE_DARK, self.LEFT_TROUSER)
        floor.rect(Palette.OLIVE_DARK, self.RIGHT_TROUSER)
        floor.rect(Palette.RED, self.LEFT_STRIPE)
        floor.rect(Palette.RED, self.RIGHT_STRIPE)
        floor.rect(CharacterPalette.CAP_DARK, self.CREASE)
        self._boots.paint(floor, state.turn)
