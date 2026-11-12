from __future__ import annotations

from typing import Final


class SipCycle:
    """The coffee routine: seven seconds, the mug goes up to his mouth for a second and a half."""

    PERIOD: Final = 7.0
    SIP_START: Final = 4.5
    SIP_END: Final = 6.0

    def __init__(self) -> None:
        self._phase = 0.0

    @property
    def phase(self) -> float:
        return self._phase

    def advance(self, dt: float) -> None:
        self._phase = (self._phase + dt) % self.PERIOD

    @classmethod
    def is_sipping_at(cls, phase: float) -> bool:
        return cls.SIP_START < phase < cls.SIP_END
