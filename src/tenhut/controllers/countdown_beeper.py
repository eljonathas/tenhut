from __future__ import annotations

from tenhut.core import Clock, Session
from tenhut.game.audio import SoundEffect

from .feedback import Feedback
from .tickable import Tickable


class CountdownBeeper(Tickable):
    """Ticks once a second during the last seconds of a phase."""

    LAST_SECONDS = 5

    def __init__(self, session: Session, clock: Clock, feedback: Feedback) -> None:
        self._session = session
        self._clock = clock
        self._feedback = feedback
        self._last_second = -1

    def tick(self, dt: float) -> None:
        second = int(self._session.remaining(self._clock.now()))
        if self._session.in_mission and second != self._last_second and second < self.LAST_SECONDS:
            self._feedback.play(SoundEffect.TICK)
        self._last_second = second
