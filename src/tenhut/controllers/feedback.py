from __future__ import annotations

from abc import ABC, abstractmethod

from tenhut.game.audio import SoundEffect
from tenhut.game.painting import Palette, Rgb


class Feedback(ABC):
    """Everything that tells the soldier something besides the general's words."""

    @abstractmethod
    def play(self, effect: SoundEffect) -> None: ...

    @abstractmethod
    def notify(self, title: str, body: str, urgent: bool = False) -> None: ...

    @abstractmethod
    def show_stamp(self, message: str, color: Rgb) -> None: ...

    @abstractmethod
    def popup(self, message: str, color: Rgb = Palette.GOLD_LIGHT) -> None: ...

    @abstractmethod
    def flash(self, seconds: float) -> None:
        """Washes the screen red, fading over ``seconds``."""

    @abstractmethod
    def shake_screen(self, seconds: float) -> None: ...
