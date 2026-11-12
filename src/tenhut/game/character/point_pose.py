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


class PointPose(Pose):
    """The right arm up, finger accusing the soldier."""

    def __init__(self) -> None:
        self._arm = SideArm()

    @property
    def name(self) -> PoseName:
        return PoseName.POINT

    def paint_arms(self, painter: Painter, state: CharacterState) -> None:
        self._arm.paint(painter, left=False)
        painter.limb(Palette.OLIVE, Limb(Anatomy.LEFT_SHOULDER, Point(8, 32)))
        painter.line(Palette.OLIVE_DARK, Point(18, 49), Point(11, 34), width=2)
        painter.line(Palette.GOLD_DARK, Point(7, 33), Point(10, 30), width=3)
        self._paint_pointing_glove(painter)

    @staticmethod
    def _paint_pointing_glove(painter: Painter) -> None:
        painter.ellipse(Palette.OUTLINE, Rect(2, 22, 10, 10))
        painter.outlined_rect(Palette.GLOVE, Rect(3, 15, 3, 9))
        painter.ellipse(Palette.GLOVE, Rect(3, 23, 8, 8))
        painter.rect(Palette.GLOVE_SHADE, Rect(7, 25, 3, 1))
        painter.rect(Palette.GLOVE_SHADE, Rect(7, 27, 3, 1))
        painter.pixel(Palette.WHITE, Point(4, 15))
        painter.rect(Palette.GLOVE_SHADE, Rect(4, 29, 6, 1))
