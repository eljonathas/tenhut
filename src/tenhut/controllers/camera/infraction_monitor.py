from __future__ import annotations


class InfractionMonitor:
    """Times a bad posture: a warning after a short while, a punishment once the tolerance is used up."""

    WARNING_AFTER = 2.0
    SCOLD_INTERVAL = 15

    def __init__(self) -> None:
        self._bad_since: float | None = None
        self._warned = False
        self._next_scold = 0.0

    @property
    def warned(self) -> bool:
        return self._warned

    def clear(self) -> None:
        self._bad_since = None
        self._warned = False

    def keeps_going(self, now: float) -> bool:
        """False on the first bad moment, which only starts the clock."""
        if self._bad_since is None:
            self._bad_since = now
            return False
        return True

    def warning_due(self, now: float, tolerance: float) -> bool:
        if self._warned or now - self._elapsed_start() < min(self.WARNING_AFTER, tolerance / 2):
            return False
        self._warned = True
        return True

    def punishment_due(self, now: float, tolerance: float) -> bool:
        if now - self._elapsed_start() < tolerance or now < self._next_scold:
            return False
        self._next_scold = now + self.SCOLD_INTERVAL
        self.clear()
        return True

    def _elapsed_start(self) -> float:
        assert self._bad_since is not None
        return self._bad_since
