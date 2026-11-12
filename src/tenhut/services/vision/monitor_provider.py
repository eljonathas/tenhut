from __future__ import annotations

from abc import ABC, abstractmethod

from .monitor import Monitor


class MonitorProvider(ABC):
    """Asks the system for its monitors; an unavailable source gives an empty list, never an error."""

    @abstractmethod
    def list_monitors(self) -> list[Monitor]: ...
