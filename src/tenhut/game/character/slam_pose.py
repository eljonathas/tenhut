from __future__ import annotations

from ..geometry import Point
from ..painting import Palette
from .anatomy import Anatomy
from .character_state import CharacterState
from .limb import Limb
from .painter import Painter
from .pose import Pose
from .pose_name import PoseName


class SlamPose(Pose):
    """Arms down on the desk; the fists themselves are drawn over the desk by the slam animation."""

    LEFT_FIST = Point(19, 63)
    RIGHT_FIST = Point(53, 63)

    @property
    def name(self) -> PoseName:
        return PoseName.SLAM

    def paint_arms(self, painter: Painter, state: CharacterState) -> None:
        for shoulder, fist in ((Anatomy.LEFT_SHOULDER, self.LEFT_FIST), (Anatomy.RIGHT_SHOULDER, self.RIGHT_FIST)):
            painter.limb(Palette.OLIVE, Limb(shoulder, fist))
            painter.line(Palette.OLIVE, shoulder, fist, width=7)
