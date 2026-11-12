from __future__ import annotations

from pygame import Rect

from ..geometry import Point
from ..painting import Palette
from .character_state import CharacterState
from .limb import Limb
from .painter import Painter
from .pose import Pose
from .pose_name import PoseName


class CrossedPose(Pose):
    """Arms folded over the chest."""

    FOREARM_THICKNESS = 6

    @property
    def name(self) -> PoseName:
        return PoseName.CROSSED

    def paint_arms(self, painter: Painter, state: CharacterState) -> None:
        self._paint_upper_arms(painter)
        self._paint_rear_forearm(painter)
        self._paint_front_forearm(painter)

    @staticmethod
    def _paint_upper_arms(painter: Painter) -> None:
        painter.outlined_rect(Palette.OLIVE, Rect(13, 43, 7, 15))
        painter.outlined_rect(Palette.OLIVE, Rect(52, 43, 7, 15))
        painter.rect(Palette.OLIVE_DARK, Rect(57, 45, 2, 12))

    def _paint_rear_forearm(self, painter: Painter) -> None:
        painter.limb(Palette.OLIVE_DARK, Limb(Point(55, 57), Point(27, 53), self.FOREARM_THICKNESS))
        painter.outlined_rect(Palette.GLOVE, Rect(22, 50, 5, 6))

    def _paint_front_forearm(self, painter: Painter) -> None:
        painter.limb(Palette.OLIVE, Limb(Point(17, 57), Point(46, 56), self.FOREARM_THICKNESS))
        painter.rect(Palette.OLIVE_DARK, Rect(16, 58, 30, 1))
        painter.rect(Palette.GOLD_DARK, Rect(41, 53, 2, 6))
        painter.outlined_rect(Palette.GLOVE, Rect(46, 52, 7, 7))
        painter.rect(Palette.GLOVE_SHADE, Rect(46, 58, 7, 1))
        painter.rect(Palette.GLOVE_SHADE, Rect(51, 54, 1, 3))
