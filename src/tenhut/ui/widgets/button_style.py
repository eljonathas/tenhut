from __future__ import annotations

from enum import Enum

from tenhut.game.painting import Rgb


class ButtonStyle(Enum):
    """The colour of a button: the lit face and the darker shade under it."""

    GREEN = (Rgb(92, 176, 92), Rgb(60, 128, 60))
    RED = (Rgb(216, 76, 64), Rgb(150, 44, 40))
    TAN = (Rgb(222, 196, 146), Rgb(170, 140, 96))
    BLUE = (Rgb(92, 140, 214), Rgb(60, 96, 160))
    YELLOW = (Rgb(246, 206, 86), Rgb(190, 150, 46))

    @property
    def face(self) -> Rgb:
        return self.value[0]

    @property
    def shade(self) -> Rgb:
        return self.value[1]
