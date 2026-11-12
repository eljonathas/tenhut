from __future__ import annotations

from dataclasses import dataclass

from ..geometry import Point
from .mood import Mood
from .pose_name import PoseName
from .sip_cycle import SipCycle


@dataclass(frozen=True, slots=True)
class CharacterState:
    """Everything the painters need to draw one frame of the general."""

    mood: Mood
    pose: PoseName
    elapsed: float
    turn: int
    look: Point
    blinking: bool
    squinting: bool
    talking: bool
    mouth_open: bool
    sip_phase: float

    @property
    def sipping(self) -> bool:
        return SipCycle.is_sipping_at(self.sip_phase)
