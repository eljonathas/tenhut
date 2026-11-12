from __future__ import annotations

from abc import ABC, abstractmethod


class Clock(ABC):
    """Source of time, injected so logic never calls the time module directly."""

    @abstractmethod
    def now(self) -> float:
        """Seconds since the epoch."""

    @abstractmethod
    def sleep(self, seconds: float) -> None: ...
