from __future__ import annotations

from typing import ClassVar

from tenhut.core import Clock, Phase, Session
from tenhut.game.random_source import RandomSource
from tenhut.i18n import t_choice
from tenhut.ui.widgets.balloon import Balloon

from .chatter_rule import ChatterRule
from .gestures import Gestures
from .judge_slot import JudgeSlot
from .navigation import Navigation
from .page_id import PageId
from .speech_controller import SpeechController
from .tickable import Tickable
from .utterance import Utterance


class ChatterController(Tickable):
    """Makes the general comment now and then while the soldier does nothing."""

    FIRST_REMARK_DELAY = 6
    SILENCE_AFTER_SPEECH = 15
    DEFAULT_WAIT = 120
    RULES: ClassVar[dict[Phase, ChatterRule]] = {
        Phase.WORK: ChatterRule("speech.work.idle_remarks", 120, 260),
        Phase.SHORT: ChatterRule("speech.break.idle_remarks", 90, 180),
        Phase.LONG: ChatterRule("speech.break.idle_remarks", 90, 180),
        Phase.IDLE: ChatterRule("speech.idle.prompt_remarks", 60, 120),
    }

    def __init__(
        self,
        session: Session,
        clock: Clock,
        speech: SpeechController,
        *,
        navigation: Navigation,
        judge: JudgeSlot,
        gestures: Gestures,
        randomness: RandomSource,
        balloon: Balloon,
    ) -> None:
        self._session = session
        self._clock = clock
        self._speech = speech
        self._navigation = navigation
        self._judge = judge
        self._gestures = gestures
        self._randomness = randomness
        self._balloon = balloon
        self._next_remark = clock.now() + self.FIRST_REMARK_DELAY

    def tick(self, dt: float) -> None:
        now = self._clock.now()
        if not self._may_speak(now):
            return
        rule = self.RULES.get(self._session.phase)
        if rule is None:
            self._next_remark = now + self.DEFAULT_WAIT
            return
        self._speech.say(Utterance(t_choice(rule.key)))
        self._next_remark = now + self._randomness.uniform(rule.min_seconds, rule.max_seconds)

    def _may_speak(self, now: float) -> bool:
        return not (
            now < self._next_remark
            or self._balloon.visible
            or self._navigation.current_id is not PageId.MAIN
            or self._judge.active
            or now - self._speech.last_said_at < self.SILENCE_AFTER_SPEECH
            or self._gestures.poke_active
        )
