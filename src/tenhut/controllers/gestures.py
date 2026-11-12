from __future__ import annotations

from abc import ABC, abstractmethod

from tenhut.game.animations import SlamAnimation


class Gestures(ABC):
    """The general's physical outbursts."""

    @property
    @abstractmethod
    def poke_active(self) -> bool: ...

    @property
    @abstractmethod
    def slam(self) -> SlamAnimation | None: ...

    @abstractmethod
    def poke(self, jabs: int = 1) -> None:
        """He reaches through the screen and prods the soldier."""

    @abstractmethod
    def start_slam(self) -> None:
        """He raises his fists and pounds the desk."""
