from __future__ import annotations

from collections.abc import Iterable

from .behind_pose import BehindPose
from .chin_pose import ChinPose
from .coffee_pose import CoffeePose
from .crossed_pose import CrossedPose
from .fists_up_pose import FistsUpPose
from .point_pose import PointPose
from .poke_pose import PokePose
from .pose import Pose
from .pose_name import PoseName
from .salute_pose import SalutePose
from .slam_pose import SlamPose
from .thumbs_pose import ThumbsPose


class PoseCatalog:
    """One pose per name."""

    def __init__(self, poses: Iterable[Pose]) -> None:
        self._by_name = {pose.name: pose for pose in poses}
        missing = set(PoseName) - set(self._by_name)
        if missing:
            raise ValueError(f"no pose for {sorted(name.value for name in missing)}")

    @classmethod
    def standard(cls) -> PoseCatalog:
        return cls(
            [
                BehindPose(),
                CrossedPose(),
                PointPose(),
                SalutePose(),
                CoffeePose(),
                ChinPose(),
                ThumbsPose(),
                FistsUpPose(),
                SlamPose(),
                PokePose(),
            ]
        )

    def for_name(self, name: PoseName) -> Pose:
        return self._by_name[name]
