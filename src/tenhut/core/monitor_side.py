from __future__ import annotations

from enum import Enum


class MonitorSide(Enum):
    """Which side of the camera's monitor another monitor sits on."""

    LEFT = ("left", "calibration.side.left")
    RIGHT = ("right", "calibration.side.right")

    label_key: str

    def __new__(cls, value: str, label_key: str) -> MonitorSide:
        member = object.__new__(cls)
        member._value_ = value
        member.label_key = label_key
        return member
