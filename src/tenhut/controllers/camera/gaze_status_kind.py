from __future__ import annotations

from enum import Enum


class GazeStatusKind(Enum):
    """What the camera currently makes of the soldier, and the translation key that says it (when there is one)."""

    NONE = ("none", None)
    WATCHING = ("watching", "camera.status.watching")
    OTHER_MONITOR = ("other_monitor", "camera.status.watching_other_monitor")
    LOOKING_DOWN = ("looking_down", "camera.status.looking_down")
    LOOKING_AWAY = ("looking_away", "camera.status.looking_away")
    NO_FACE = ("no_face", "camera.status.no_face")
    FACE_VANISHED = ("face_vanished", "camera.status.looking_down")
    ERROR = ("error", None)

    label_key: str | None

    def __new__(cls, value: str, label_key: str | None) -> GazeStatusKind:
        member = object.__new__(cls)
        member._value_ = value
        member.label_key = label_key
        return member
