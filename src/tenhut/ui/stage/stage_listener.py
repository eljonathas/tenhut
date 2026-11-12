from __future__ import annotations

from abc import ABC, abstractmethod

from tenhut.core import Theme


class StageListener(ABC):
    """Told when the story moves on to a new stage."""

    @abstractmethod
    def stage_entered(self, theme: Theme) -> None: ...
