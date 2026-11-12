from __future__ import annotations

from abc import ABC, abstractmethod

from .character_state import CharacterState
from .painter import Painter


class BodyPart(ABC):
    """A piece of the general that paints itself."""

    @abstractmethod
    def paint(self, painter: Painter, state: CharacterState) -> None: ...
