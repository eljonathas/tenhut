from __future__ import annotations

from abc import ABC, abstractmethod

from tenhut.game.painting import Canvas


class GeneralOverlay(ABC):
    """A small mark drawn around the general's sprite."""

    @abstractmethod
    def applies(self) -> bool: ...

    @abstractmethod
    def draw(self, canvas: Canvas) -> None: ...
