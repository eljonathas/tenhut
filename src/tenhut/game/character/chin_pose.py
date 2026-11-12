from __future__ import annotations

from pygame import Rect

from ..geometry import Point
from ..painting import Palette
from .character_state import CharacterState
from .limb import Limb
from .painter import Painter
from .pose import Pose
from .pose_name import PoseName


class ChinPose(Pose):
    """Thinking: one arm across the belly supports the other, whose hand rests on his chin."""

    @property
    def name(self) -> PoseName:
        return PoseName.CHIN

    def paint_arms(self, painter: Painter, state: CharacterState) -> None:
        painter.outlined_rect(Palette.OLIVE, Rect(13, 43, 7, 14))
        painter.outlined_rect(Palette.OLIVE, Rect(52, 43, 7, 16))
        painter.outlined_rect(Palette.OLIVE, Rect(18, 57, 36, 6))
        painter.rect(Palette.OLIVE_DARK, Rect(18, 62, 36, 1))
        painter.outlined_rect(Palette.GLOVE, Rect(49, 57, 5, 6))
        painter.limb(Palette.OLIVE, Limb(Point(19, 56), Point(31, 45)))

    def paint_after_head(self, painter: Painter, state: CharacterState) -> None:
        painter.ellipse(Palette.OUTLINE, Rect(28, 38, 11, 9))
        painter.ellipse(Palette.GLOVE, Rect(29, 39, 9, 7))
        painter.rect(Palette.GLOVE, Rect(31, 38, 6, 2))
        painter.pixel(Palette.GLOVE_SHADE, Point(33, 44))
