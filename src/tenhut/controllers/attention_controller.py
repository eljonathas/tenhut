from __future__ import annotations

import pygame

from tenhut.core import Clock, Phase, Session
from tenhut.game.audio import SoundEffect
from tenhut.game.character import Character
from tenhut.game.geometry import Point
from tenhut.game.random_source import RandomSource
from tenhut.i18n import t_choice
from tenhut.ui.layout import LayoutProvider
from tenhut.ui.widgets.balloon import Balloon

from .distraction_tracker import DistractionTracker
from .feedback import Feedback
from .judge_slot import JudgeSlot
from .navigation import Navigation
from .speech_controller import SpeechController
from .tickable import Tickable
from .utterance import Utterance


class AttentionController(Tickable):
    """Where the general looks: at the pointer, at the scenery now and then, and back at the soldier with a start."""

    POINTER_MEMORY = 2.5
    POINTER_RANGE = Point(160, 120)
    CHEST_TO_EYES = 24
    GLANCE_REMARK_CHANCE = 0.4
    FIRST_DISTRACTION = (8, 16)
    DISTRACTION_LENGTH = (2.5, 6.5)
    DISTRACTION_GAP = (12, 38)

    def __init__(
        self,
        general: Character,
        balloon: Balloon,
        session: Session,
        *,
        clock: Clock,
        layouts: LayoutProvider,
        speech: SpeechController,
        feedback: Feedback,
        navigation: Navigation,
        judge: JudgeSlot,
        tracker: DistractionTracker,
        randomness: RandomSource,
    ) -> None:
        self._general = general
        self._balloon = balloon
        self._session = session
        self._clock = clock
        self._layouts = layouts
        self._speech = speech
        self._feedback = feedback
        self._navigation = navigation
        self._judge = judge
        self._tracker = tracker
        self._randomness = randomness
        self._pointer_seen = 0.0
        self._next_distraction = clock.now() + randomness.uniform(*self.FIRST_DISTRACTION)

    def pointer_moved(self) -> None:
        """Caught looking away? He turns on the spot."""
        self._pointer_seen = self._clock.now()
        if self._general.distracted:
            self._general.snap()
            self._tracker.forget()
            self._feedback.play(SoundEffect.THINK)

    def tick(self, dt: float) -> None:
        now = self._clock.now()
        self._general.follow_pointer(self._pointer_target(now))
        self._general.talking = self._balloon.typing
        self._drift_attention(now)

    def _pointer_target(self, now: float) -> Point | None:
        if now - self._pointer_seen >= self.POINTER_MEMORY or not pygame.mouse.get_focused():
            return None
        layout = self._layouts.layout
        x, y = self._layouts.to_logical(pygame.mouse.get_pos())
        head = layout.head
        eyes_y = head.y + self.CHEST_TO_EYES * layout.general_scale
        range_x, range_y = self.POINTER_RANGE
        return Point(max(-1, min(1, (x - head.x) / range_x)), max(-1, min(1, (y - eyes_y) / range_y)))

    def _may_interrupt_quietly(self) -> bool:
        return (
            not self._balloon.visible
            and not self._judge.active
            and not self._speech.reacting
            and not self._navigation.current_id.is_calibration
            and self._session.phase is not Phase.VICTORY
        )

    def _drift_attention(self, now: float) -> None:
        idle = self._may_interrupt_quietly()
        general = self._general
        if general.distracted:
            self._tracker.notice()
        elif self._tracker.was_distracted:
            self._tracker.forget()
            general.raise_alert()
            self._remark_on_return(idle)
        elif now >= self._next_distraction and idle:
            general.distract(self._randomness.choice((-1, 1)), self._randomness.uniform(*self.DISTRACTION_LENGTH))
            self._next_distraction = now + self._randomness.uniform(*self.DISTRACTION_GAP)

    def _remark_on_return(self, idle: bool) -> None:
        if self._session.phase is Phase.WORK and self._randomness.random() < self.GLANCE_REMARK_CHANCE and idle:
            self._speech.say(Utterance(t_choice("speech.work.glance_back_remarks")))
