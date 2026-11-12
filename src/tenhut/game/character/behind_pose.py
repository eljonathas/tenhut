from __future__ import annotations

from .character_state import CharacterState
from .painter import Painter
from .pose import Pose
from .pose_name import PoseName
from .side_arm import SideArm


class BehindPose(Pose):
    """Hands clasped behind his back: only the sleeves show, hanging at his sides."""

    def __init__(self) -> None:
        self._arm = SideArm()

    @property
    def name(self) -> PoseName:
        return PoseName.BEHIND

    def paint_before_torso(self, painter: Painter, state: CharacterState) -> None:
        self._arm.paint(painter, left=True)
        self._arm.paint(painter, left=False)
