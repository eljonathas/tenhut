from __future__ import annotations

from pygame import Rect

from ..geometry import Point
from ..painting import Palette
from .character_state import CharacterState
from .limb import Limb
from .mug import Mug
from .painter import Painter
from .pose import Pose
from .pose_name import PoseName
from .side_arm import SideArm


class CoffeePose(Pose):
    """Holds a mug at his side, and every seven seconds lifts it to his mouth for a sip."""

    SHOULDER = Point(55, 46)
    RESTING_MUG = Point(41, 46)
    SIPPING_MUG = Point(34, 36)

    def __init__(self) -> None:
        self._arm = SideArm()
        self._mug = Mug()

    @property
    def name(self) -> PoseName:
        return PoseName.COFFEE

    def paint_arms(self, painter: Painter, state: CharacterState) -> None:
        self._arm.paint(painter, left=True)
        if state.sipping:
            self._paint_raised_arm(painter)
        else:
            self._paint_resting_arm(painter)
            self._mug.paint(painter, self.RESTING_MUG, state.elapsed)

    def paint_after_head(self, painter: Painter, state: CharacterState) -> None:
        if state.sipping:
            self._mug.paint(painter, self.SIPPING_MUG, state.elapsed)

    def _paint_raised_arm(self, painter: Painter) -> None:
        elbow = Point(60, 56)
        painter.limb(Palette.OLIVE, Limb(self.SHOULDER, elbow))
        painter.limb(Palette.OLIVE, Limb(elbow, Point(44, 42)))
        painter.line(Palette.OLIVE, self.SHOULDER, elbow, width=7)

    def _paint_resting_arm(self, painter: Painter) -> None:
        elbow = Point(58, 60)
        painter.limb(Palette.OLIVE, Limb(self.SHOULDER, elbow))
        painter.limb(Palette.OLIVE, Limb(elbow, Point(48, 54)))
        painter.line(Palette.OLIVE, self.SHOULDER, elbow, width=7)
        painter.rect(Palette.GOLD_DARK, Rect(54, 56, 2, 5))
