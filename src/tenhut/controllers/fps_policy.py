from __future__ import annotations

from .run_state import RunState


class FpsPolicy:
    """Keeps the app light: full speed with focus, slower without it, almost stopped when minimised."""

    FOCUSED = 30
    UNFOCUSED = 12
    HIDDEN = 2

    @classmethod
    def frames_per_second(cls, state: RunState) -> int:
        if state.hidden:
            return cls.HIDDEN
        return cls.FOCUSED if state.focused else cls.UNFOCUSED
