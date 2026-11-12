from __future__ import annotations

import time

from .clock import Clock


class SystemClock(Clock):
    """The real clock."""

    def now(self) -> float:
        return time.time()

    def sleep(self, seconds: float) -> None:
        time.sleep(seconds)
