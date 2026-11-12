from __future__ import annotations

from abc import ABC, abstractmethod

from .character_state import CharacterState
from .painter import Painter
from .pose_name import PoseName


class Pose(ABC):
    """What the arms (and the props in his hands) look like. Painted in three layers around the torso and head."""

    @property
    @abstractmethod
    def name(self) -> PoseName: ...

    def paint_before_torso(self, painter: Painter, state: CharacterState) -> None:
        """Arms hanging behind the jacket."""
        return None

    def paint_arms(self, painter: Painter, state: CharacterState) -> None:
        """Arms in front of the jacket."""
        return None

    def paint_after_head(self, painter: Painter, state: CharacterState) -> None:
        """Hands and props that cross the face."""
        return None
