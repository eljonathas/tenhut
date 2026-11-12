from __future__ import annotations

from typing import ClassVar

from tenhut.core import Clock, Phase, Session
from tenhut.game.character import Character
from tenhut.ui.widgets.balloon import Balloon

from .distraction_tracker import DistractionTracker
from .judge_slot import JudgeSlot
from .reaction import Reaction
from .speech import Speech
from .tickable import Tickable
from .utterance import Utterance


class SpeechController(Speech, Tickable):
    """Makes the general talk and keeps his mood and pose in line with the phase while he is not reacting."""

    MIN_HOLD = 2.5
    CHARACTERS_PER_SECOND = 18
    VICTORY_POSE_SECONDS = 6
    AMBIENT: ClassVar[dict[Phase, Reaction]] = {
        Phase.WORK: Reaction.STERN_CROSSED,
        Phase.SHORT: Reaction.HAPPY_COFFEE,
        Phase.LONG: Reaction.HAPPY_COFFEE,
    }

    def __init__(
        self,
        balloon: Balloon,
        general: Character,
        session: Session,
        *,
        clock: Clock,
        judge: JudgeSlot,
        distraction: DistractionTracker,
    ) -> None:
        self._balloon = balloon
        self._general = general
        self._session = session
        self._clock = clock
        self._judge = judge
        self._distraction = distraction
        self._reaction_until = 0.0
        self._last_said_at = 0.0

    @property
    def last_said_at(self) -> float:
        return self._last_said_at

    @property
    def reacting(self) -> bool:
        return self._clock.now() < self._reaction_until

    def say(self, utterance: Utterance) -> None:
        self._balloon.say(utterance.message, persist=utterance.persist)
        self._last_said_at = self._clock.now()
        self._general.snap(alert=False)
        self._distraction.forget()
        if utterance.reaction:
            self._general.show(utterance.reaction.mood, utterance.reaction.pose)
            self.react_for(max(utterance.seconds, self._minimum_hold(utterance.message)))

    def say_next(self, message: str) -> None:
        self._balloon.say(message, interrupt=False)

    def murmur(self, message: str, persist: bool = False) -> None:
        self._balloon.say(message, persist=persist)

    def keep_reacting(self, seconds: float) -> None:
        self._reaction_until = max(self._reaction_until, self._clock.now() + seconds)

    def react_for(self, seconds: float) -> None:
        self._reaction_until = self._clock.now() + seconds

    def release_reaction(self) -> None:
        self._reaction_until = 0.0

    def tick(self, dt: float) -> None:
        """Gives the general the default look of the phase when nothing is making him react."""
        if self.reacting or self._judge.active:
            return
        reaction = self._ambient_reaction()
        self._general.show(reaction.mood, reaction.pose)

    def _ambient_reaction(self) -> Reaction:
        phase = self._session.phase
        if phase is Phase.VICTORY:
            alternate = int(self._clock.now() / self.VICTORY_POSE_SECONDS) % 2 == 0
            return Reaction.PROUD_SALUTE if alternate else Reaction.PROUD_THUMBS
        return self.AMBIENT.get(phase, Reaction.NEUTRAL_BEHIND)

    @classmethod
    def _minimum_hold(cls, message: str) -> float:
        return cls.MIN_HOLD + len(message) / cls.CHARACTERS_PER_SECOND
