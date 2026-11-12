from __future__ import annotations

from abc import ABC, abstractmethod


class ChangeEffect(ABC):
    """What the soldier hears or sees after changing one option."""

    @abstractmethod
    def apply(self, new_value: object) -> None: ...
