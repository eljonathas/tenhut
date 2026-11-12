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


class SalutePose(Pose):
    """Right hand to the cap; the hand is painted over the face."""

    ELBOW = Point(8, 40)
    HAND_BOARD = (Point(17, 17), Point(29, 15), Point(30, 21), Point(18, 25))
    HAND_FACE = (Point(18, 18), Point(28, 16), Point(29, 20), Point(19, 24))

    def __init__(self) -> None:
        self._arm = SideArm()

    @property
    def name(self) -> PoseName:
        return PoseName.SALUTE

    def paint_arms(self, painter: Painter, state: CharacterState) -> None:
        self._arm.paint(painter, left=False)
        painter.limb(Palette.OLIVE, Limb(Anatomy.LEFT_SHOULDER, self.ELBOW))
        painter.limb(Palette.OLIVE, Limb(self.ELBOW, Point(20, 24)))
        painter.line(Palette.OLIVE, Anatomy.LEFT_SHOULDER, self.ELBOW, width=7)
        painter.line(Palette.OLIVE_DARK, Point(10, 43), Point(6, 40), width=2)

    def paint_after_head(self, painter: Painter, state: CharacterState) -> None:
        painter.polygon(Palette.OUTLINE, self.HAND_BOARD)
        painter.polygon(Palette.GLOVE, self.HAND_FACE)
        painter.line(Palette.GLOVE_SHADE, Point(19, 23), Point(28, 19))
        painter.rect(Palette.GOLD_DARK, Rect(17, 23, 4, 3))
