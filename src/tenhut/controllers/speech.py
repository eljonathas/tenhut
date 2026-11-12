from __future__ import annotations

from abc import ABC, abstractmethod

from .utterance import Utterance


class Speech(ABC):
    """How controllers make the general talk."""

    @abstractmethod
    def say(self, utterance: Utterance) -> None:
        """Interrupts whatever he was saying."""

    @abstractmethod
    def say_next(self, message: str) -> None:
        """Queues the line after the current one, without changing his look."""

    @abstractmethod
    def murmur(self, message: str, persist: bool = False) -> None:
        """Interrupts with a line that changes neither his look nor his attention."""

    @abstractmethod
    def keep_reacting(self, seconds: float) -> None:
        """Keeps his current look for at least ``seconds`` more."""

    @abstractmethod
    def react_for(self, seconds: float) -> None:
        """Keeps his current look for exactly ``seconds`` more."""
