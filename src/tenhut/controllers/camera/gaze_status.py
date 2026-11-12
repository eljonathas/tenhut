from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from tenhut.i18n import t
from tenhut.services.vision import GazeState

from .gaze_status_kind import GazeStatusKind


@dataclass(frozen=True, slots=True)
class GazeStatus:
    """The camera's current reading of the soldier, ready to show."""

    kind: GazeStatusKind
    message: str = ""

    KINDS: ClassVar[dict[GazeState, GazeStatusKind]] = {
        GazeState.OK: GazeStatusKind.WATCHING,
        GazeState.SIDE_ALLOWED: GazeStatusKind.OTHER_MONITOR,
        GazeState.DOWN: GazeStatusKind.LOOKING_DOWN,
        GazeState.SIDE: GazeStatusKind.LOOKING_AWAY,
    }

    @classmethod
    def of(cls, state: GazeState) -> GazeStatus:
        return cls(cls.KINDS[state])

    @classmethod
    def none(cls) -> GazeStatus:
        return cls(GazeStatusKind.NONE)

    @classmethod
    def no_face(cls) -> GazeStatus:
        return cls(GazeStatusKind.NO_FACE)

    @classmethod
    def face_vanished(cls) -> GazeStatus:
        return cls(GazeStatusKind.FACE_VANISHED)

    @classmethod
    def error(cls, message: str) -> GazeStatus:
        return cls(GazeStatusKind.ERROR, message)

    @property
    def present(self) -> bool:
        return self.kind is not GazeStatusKind.NONE

    @property
    def is_alert(self) -> bool:
        return self.kind in (GazeStatusKind.LOOKING_DOWN, GazeStatusKind.LOOKING_AWAY)

    @property
    def text(self) -> str:
        key = self.kind.label_key
        return t(key) if key else self.message
