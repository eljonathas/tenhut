from __future__ import annotations

from pygame import Rect

from ..painting import Palette
from .character_state import CharacterState
from .painter import Painter
from .pose import Pose
from .pose_name import PoseName
from .side_arm import SideArm


class PokePose(Pose):
    """The right arm reaches toward the screen; the arm itself is drawn by the poke animation, here only the shoulder."""

    SHOULDER_RIM = Rect(11, 41, 12, 12)
    SHOULDER = Rect(12, 42, 10, 10)
    SHOULDER_SHADE = Rect(14, 44, 6, 6)

    def __init__(self) -> None:
        self._arm = SideArm()

    @property
    def name(self) -> PoseName:
        return PoseName.POKE

    def paint_arms(self, painter: Painter, state: CharacterState) -> None:
        self._arm.paint(painter, left=False)
        painter.ellipse(Palette.OUTLINE, self.SHOULDER_RIM)
        painter.ellipse(Palette.OLIVE, self.SHOULDER)
        painter.ellipse(Palette.OLIVE_DARK, self.SHOULDER_SHADE)
