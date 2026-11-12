from __future__ import annotations

from abc import ABC, abstractmethod


class Celebration(ABC):
    """Fireworks for good news."""

    @abstractmethod
    def fireworks(self, center_x: float | None = None) -> None: ...
