from __future__ import annotations

from pygame import Rect

from ..geometry import Point
from ..painting import Palette
from .anatomy import Anatomy
from .character_state import CharacterState
from .limb import Limb
from .painter import Painter
from .pose import Pose
from .pose_name import PoseName
from .side_arm import SideArm


class ThumbsPose(Pose):
    """Right fist raised at his side with the thumb up."""

    ELBOW = Point(10, 58)

    def __init__(self) -> None:
        self._arm = SideArm()

    @property
    def name(self) -> PoseName:
        return PoseName.THUMBS

    def paint_arms(self, painter: Painter, state: CharacterState) -> None:
        self._arm.paint(painter, left=False)
        painter.limb(Palette.OLIVE, Limb(Anatomy.LEFT_SHOULDER, self.ELBOW))
        painter.limb(Palette.OLIVE, Limb(self.ELBOW, Point(13, 48)))
        painter.line(Palette.OLIVE, Anatomy.LEFT_SHOULDER, self.ELBOW, width=7)
        self._paint_fist(painter)

    @staticmethod
    def _paint_fist(painter: Painter) -> None:
        fist = Rect(7, 41, 10, 7)
        painter.outlined_rect(Palette.GLOVE, fist)
        painter.outlined_rect(Palette.GLOVE, Rect(15, 34, 3, 7))
        painter.rect(Palette.GLOVE, fist)
        for row in (43, 45):
            painter.rect(Palette.GLOVE_SHADE, Rect(8, row, 6, 1))
        painter.rect(Palette.GLOVE_SHADE, Rect(7, 47, 10, 1))
