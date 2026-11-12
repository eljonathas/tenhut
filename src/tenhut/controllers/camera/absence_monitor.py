from __future__ import annotations


class AbsenceMonitor:
    """Notices a soldier who walked away from the camera."""

    GRACE_SECONDS = 60

    def __init__(self) -> None:
        self._absent_since: float | None = None
        self._warned = False

    @property
    def warned(self) -> bool:
        return self._warned

    def reset(self) -> None:
        self._absent_since = None
        self._warned = False

    def observe_absent(self, now: float) -> bool:
        """True the first time the absence has lasted too long."""
        if self._absent_since is None:
            self._absent_since = now
            return False
        if now - self._absent_since > self.GRACE_SECONDS and not self._warned:
            self._warned = True
            return True
        return False
