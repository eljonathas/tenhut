from __future__ import annotations

from abc import ABC, abstractmethod


class Enforcement(ABC):
    """Applies the blocking rules for the current phase."""

    @abstractmethod
    def enforce(self, force: bool = False) -> None: ...
