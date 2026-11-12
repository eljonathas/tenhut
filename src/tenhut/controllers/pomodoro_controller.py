from __future__ import annotations

from tenhut.core import Clock, Phase, Session, SessionEvent
from tenhut.game.audio import SoundEffect
from tenhut.i18n import t

from .active_settings import ActiveSettings
from .career_controller import CareerController
from .feedback import Feedback
from .mission_controller import MissionController
from .navigation import Navigation
from .page_id import PageId
from .reaction import Reaction
from .speech import Speech
from .tickable import Tickable
from .utterance import Utterance
from .xp_award import XpAward


class PomodoroController(Tickable):
    """Reacts to the session clock: end of a work block, end of a break, victory."""

    BREAK_SPEECH_SECONDS = 5
    PAGES_CLOSED_BY_BREAK = (PageId.REQUEST, PageId.DESERTION)

    def __init__(
        self,
        session: Session,
        settings: ActiveSettings,
        clock: Clock,
        *,
        mission: MissionController,
        career: CareerController,
        navigation: Navigation,
        speech: Speech,
        feedback: Feedback,
    ) -> None:
        self._session = session
        self._settings = settings
        self._clock = clock
        self._mission = mission
        self._career = career
        self._navigation = navigation
        self._speech = speech
        self._feedback = feedback
        self._reactions = {
            SessionEvent.WORK_END: self._work_ended,
            SessionEvent.BREAK_END: self._break_ended,
            SessionEvent.VICTORY: self._mission.victory,
        }

    def tick(self, dt: float) -> None:
        for event in self._session.tick(self._settings.current, self._clock.now()):
            self._session.save()
            self._reactions[event]()
            self._navigation.refresh(PageId.MAIN)
        if self._mission.expire_confirmation():
            self._navigation.refresh(PageId.MAIN)

    def _work_ended(self) -> None:
        timer = self._settings.current.timer
        self._career.award(XpAward(1, pomodoro=True))
        long_break = self._session.phase is Phase.LONG
        self._feedback.play(SoundEffect.BREAK)
        if self._navigation.current_id in self.PAGES_CLOSED_BY_BREAK:
            self._navigation.open(PageId.MAIN)
        head = t("speech.break.long_head") if long_break else t("speech.break.short_head")
        minutes = timer.long_break_minutes if long_break else timer.short_break_minutes
        self._speech.say(
            Utterance(t("speech.break.started", head=head, n=minutes), Reaction.HAPPY_THUMBS, self.BREAK_SPEECH_SECONDS)
        )
        self._feedback.notify(t("notify.break_started.title"), t("notify.break_started.body"))

    def _break_ended(self) -> None:
        self._feedback.play(SoundEffect.ALARM)
        self._speech.say(Utterance(t("speech.break.ended"), Reaction.STERN_POINT, self.BREAK_SPEECH_SECONDS))
        self._feedback.notify(t("notify.break_ended.title"), t("notify.break_ended.body"), urgent=True)
