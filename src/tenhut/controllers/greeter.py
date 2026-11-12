from __future__ import annotations

from typing import ClassVar

from tenhut.core import Phase, Session
from tenhut.i18n import t

from .greeting import Greeting
from .reaction import Reaction
from .speech import Speech
from .utterance import Utterance


class Greeter:
    """The general's first words when the app opens, according to where the mission was left."""

    BY_PHASE: ClassVar[dict[Phase, Greeting]] = {
        Phase.WORK: Greeting("speech.greeting.resume_work", Reaction.STERN_POINT),
        Phase.SHORT: Greeting("speech.greeting.still_on_break", Reaction.HAPPY_COFFEE),
        Phase.LONG: Greeting("speech.greeting.still_on_break", Reaction.HAPPY_COFFEE),
        Phase.VICTORY: Greeting("speech.greeting.mission_done", Reaction.PROUD_SALUTE),
    }
    FIRST_TIME = Greeting("speech.greeting.first_time", Reaction.NEUTRAL_SALUTE)

    def __init__(self, session: Session, speech: Speech) -> None:
        self._session = session
        self._speech = speech

    def greet(self) -> None:
        phase, pending = self._session.phase, self._session.pending_count()
        greeting = self.BY_PHASE.get(phase)
        if greeting is not None:
            utterance = Utterance(t(greeting.key), greeting.reaction)
        elif pending:
            utterance = Utterance(t("speech.greeting.unfinished_mission", n=pending), Reaction.NEUTRAL_POINT)
        else:
            utterance = Utterance(t(self.FIRST_TIME.key), self.FIRST_TIME.reaction)
        self._speech.say(utterance)
