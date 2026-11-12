from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar, Final

from pygame import Rect

from ..geometry import Point
from ..painting import Palette
from ..random_source import RandomSource
from .character_palette import CharacterPalette
from .character_state import CharacterState
from .glance import Glance
from .mood import Mood
from .painter import Painter
from .skin_tone import SkinTone


class Expression(ABC):
    """How one mood looks and behaves: skin tone, brows, mouth, cheeks, what the eyes do when idle."""

    NEUTRAL_GLANCE_X: Final = (-0.5, 0.5)
    NEUTRAL_GLANCE_Y: Final = (-0.2, 0.4)
    TALKING_MOUTH: Final = Rect(32, 36, 8, 3)
    TEETH: Final = Rect(33, 36, 6, 1)
    CHIN: Final = Rect(34, 39, 4, 1)

    breathes: ClassVar[bool] = True
    always_squints: ClassVar[bool] = False
    shouts_when_talking: ClassVar[bool] = False

    def __init__(self, skin: SkinTone | None = None) -> None:
        self._skin = skin or SkinTone.natural()

    @property
    @abstractmethod
    def mood(self) -> Mood: ...

    @property
    def skin(self) -> SkinTone:
        return self._skin

    def has_content_eyes(self, state: CharacterState) -> bool:
        """Eyes shut in satisfaction."""
        return False

    def choose_glance(self, randomness: RandomSource) -> Glance:
        """An idle look-around; consumes the random stream exactly as the original did."""
        target = Point(randomness.uniform(*self.NEUTRAL_GLANCE_X), randomness.uniform(*self.NEUTRAL_GLANCE_Y))
        return Glance(target, squint=False)

    def paint_cheeks(self, painter: Painter) -> None:
        return None

    @abstractmethod
    def paint_brows(self, painter: Painter) -> None: ...

    def paint_mouth(self, painter: Painter, state: CharacterState) -> None:
        if state.talking and (state.mouth_open or self.shouts_when_talking):
            self._paint_talking_mouth(painter)
        else:
            self._paint_resting_mouth(painter)
        painter.rect(self.skin.shade, self.CHIN)

    def paint_forehead(self, painter: Painter) -> None:
        """Marks drawn over the cap line."""
        return None

    def _paint_talking_mouth(self, painter: Painter) -> None:
        painter.rect(CharacterPalette.MOUTH, self.TALKING_MOUTH)
        painter.rect(Palette.WHITE, self.TEETH)

    @abstractmethod
    def _paint_resting_mouth(self, painter: Painter) -> None: ...
