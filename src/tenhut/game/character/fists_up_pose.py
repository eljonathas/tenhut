from __future__ import annotations

from typing import Final

from pygame import Rect

from ..geometry import Point
from ..painting import Palette
from .anatomy import Anatomy
from .character_state import CharacterState
from .limb import Limb
from .painter import Painter
from .pose import Pose
from .pose_name import PoseName


class FistsUpPose(Pose):
    """Both fists raised, about to hit the desk."""

    FIST_COLUMNS: Final = (4, 58)

    @property
    def name(self) -> PoseName:
        return PoseName.FISTS_UP

    def paint_arms(self, painter: Painter, state: CharacterState) -> None:
        painter.limb(Palette.OLIVE, Limb(Anatomy.LEFT_SHOULDER, Point(9, 31)))
        painter.limb(Palette.OLIVE, Limb(Anatomy.RIGHT_SHOULDER, Point(63, 31)))
        for column in self.FIST_COLUMNS:
            painter.outlined_rect(Palette.GLOVE, Rect(column, 22, 10, 9))
            painter.rect(Palette.GLOVE_SHADE, Rect(column + 1, 24, 8, 1))
            painter.rect(Palette.GLOVE_SHADE, Rect(column + 1, 27, 8, 1))
