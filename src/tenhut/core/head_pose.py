from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class HeadPose:
    """Head orientation in degrees."""

    yaw: float
    pitch: float

    @classmethod
    def from_json(cls, value: object) -> HeadPose | None:
        if not isinstance(value, (list, tuple)) or len(value) != 2:
            return None
        if not all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in value):
            return None
        return cls(value[0], value[1])

    def to_json(self) -> list[float]:
        return [self.yaw, self.pitch]
