from __future__ import annotations

from dataclasses import dataclass, field

from .head_pose import HeadPose
from .monitor_side import MonitorSide


@dataclass(frozen=True, slots=True)
class CameraCalibration:
    """Head poses recorded looking at the main screen, down, and at each side monitor."""

    base: HeadPose
    down: HeadPose
    sides: dict[MonitorSide, HeadPose] = field(default_factory=dict)
    down_face_vanishes: bool = False

    @classmethod
    def from_dict(cls, data: object) -> CameraCalibration | None:
        if not isinstance(data, dict):
            return None
        base, down = HeadPose.from_json(data.get("base")), HeadPose.from_json(data.get("down"))
        if base is None or down is None:
            return None
        return cls(base, down, cls._sides_from(data.get("sides")), data.get("down_face_vanishes") is True)

    @staticmethod
    def _sides_from(raw: object) -> dict[MonitorSide, HeadPose]:
        sides: dict[MonitorSide, HeadPose] = {}
        for name, pose in raw.items() if isinstance(raw, dict) else ():
            parsed = HeadPose.from_json(pose)
            if parsed is not None and name in {s.value for s in MonitorSide}:
                sides[MonitorSide(name)] = parsed
        return sides

    def to_dict(self) -> dict[str, object]:
        out: dict[str, object] = {
            "base": self.base.to_json(),
            "down": self.down.to_json(),
            "sides": {side.value: pose.to_json() for side, pose in self.sides.items()},
        }
        if self.down_face_vanishes:
            out["down_face_vanishes"] = True
        return out
