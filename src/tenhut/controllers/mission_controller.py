from __future__ import annotations

from tenhut.core import Clock, Session
from tenhut.game.audio import SoundEffect
from tenhut.game.painting import Rgb
from tenhut.i18n import t
from tenhut.ui.layout import LayoutProvider

from .active_settings import ActiveSettings
from .blocking_status import BlockingStatus
from .career_controller import CareerController
from .celebration import Celebration
from .enforcement import Enforcement
from .feedback import Feedback
from .navigation import Navigation
from .page_id import PageId
from .reaction import Reaction
from .speech import Speech
from .speech_hold import SpeechHold
from .utterance import Utterance
from .xp_award import XpAward


class MissionController:
    """The soldier's mission: building the task list, starting, resuming, completing and abandoning it."""

    DISCARD_CONFIRMATION_SECONDS = 4
    VICTORY_STAMP = Rgb(250, 214, 90)
    VICTORY_XP = 2

    def __init__(
        self,
        session: Session,
        settings: ActiveSettings,
        clock: Clock,
        *,
        navigation: Navigation,
        speech: Speech,
        feedback: Feedback,
        blocking: BlockingStatus,
        enforcement: Enforcement,
        career: CareerController,
        celebration: Celebration,
        layouts: LayoutProvider,
    ) -> None:
        self._session = session
        self._settings = settings
        self._clock = clock
        self._navigation = navigation
        self._speech = speech
        self._feedback = feedback
        self._blocking = blocking
        self._enforcement = enforcement
        self._career = career
        self._celebration = celebration
        self._layouts = layouts
        self._confirm_until = 0.0

    @property
    def confirming_discard(self) -> bool:
        return self._clock.now() < self._confirm_until

    def expire_confirmation(self) -> bool:
        """True when a pending 'discard the unfinished mission?' question just timed out."""
        if self._confirm_until and self._clock.now() >= self._confirm_until:
            self._confirm_until = 0.0
            return True
        return False

    def new_mission(self) -> None:
        self._session.keep_pending_tasks()
        self._session.save()
        self._navigation.open(PageId.MISSION)
        self._speech.say(Utterance(t("speech.mission.list_tasks"), Reaction.NEUTRAL_POINT))

    def resume_mission(self) -> None:
        if self._session.pending_count():
            self.start_mission(resume=True)

    def fresh_mission(self) -> None:
        """Starts over; with unfinished tasks it asks for a second click first."""
        pending = self._session.pending_count()
        now = self._clock.now()
        if pending and now >= self._confirm_until:
            self._confirm_until = now + self.DISCARD_CONFIRMATION_SECONDS
            self._navigation.open(PageId.MAIN)
            self._speech.say(
                Utterance(t("speech.mission.discard_confirm", n=pending), Reaction.THINKING_CHIN, SpeechHold.NORMAL)
            )
            return
        self._confirm_until = 0.0
        self._session.clear_tasks()
        self._session.save()
        self._navigation.open(PageId.MISSION)
        self._speech.say(Utterance(t("speech.mission.cleared"), Reaction.NEUTRAL_POINT))

    def add_task(self, text: str) -> bool:
        """Adds a task and says so; an empty text only gets the general to ask for one."""
        if not text:
            self._speech.say(Utterance(t("speech.mission.type_task_first"), Reaction.NEUTRAL_POINT, SpeechHold.BRIEF))
            return False
        self._session.add_task(text)
        self._session.save()
        self._feedback.play(SoundEffect.CLICK)
        if self._session.in_mission:
            self._speech.say(Utterance(t("speech.mission.task_added"), Reaction.HAPPY_THUMBS, SpeechHold.BRIEF))
        return True

    def press_task(self, index: int) -> None:
        """A click on a task of the board: ticks it during a mission, otherwise the general asks to start first."""
        if self._session.in_mission:
            self.toggle_task(index)
        else:
            self._speech.say(Utterance(t("speech.mission.start_first"), Reaction.NEUTRAL_POINT, SpeechHold.BRIEF))

    def remove_task(self, index: int) -> None:
        if self._session.in_mission:
            self._speech.say(Utterance(t("speech.mission.cannot_remove_task"), Reaction.ANGRY_POINT))
            return
        self._session.remove_task(index)
        self._session.save()

    def start_mission(self, resume: bool = False) -> None:
        session = self._session
        if not session.tasks:
            return
        session.start_mission(self._settings.current)
        session.save()
        self._feedback.play(SoundEffect.START)
        self._navigation.open(PageId.MAIN)
        warning = (
            ""
            if self._blocking.helper_installed
            else t("speech.mission.blocking_inactive_warning", hint=self._blocking.hint)
        )
        minutes = self._settings.current.timer.work_minutes
        if resume:
            message = t("speech.mission.resumed", n=session.pending_count(), warn=warning)
        else:
            message = t("speech.mission.started", n=minutes, warn=warning)
        self._speech.say(Utterance(message, Reaction.STERN_POINT, SpeechHold.NORMAL))
        self._feedback.notify(t("notify.mission_started.title"), t("notify.mission_started.body", n=minutes))
        self._enforcement.enforce(force=True)

    def skip_break(self) -> None:
        self._session.skip_break(self._settings.current)
        self._session.save()
        self._feedback.play(SoundEffect.START)
        self._navigation.open(PageId.MAIN)
        self._speech.say(Utterance(t("speech.break.skipped"), Reaction.PROUD_THUMBS))
        self._enforcement.enforce(force=True)

    def toggle_task(self, index: int) -> None:
        session = self._session
        task = session.toggle_task(index)
        if task is None:
            return
        session.save()
        self._feedback.play(SoundEffect.CLICK)
        if task.done and session.in_mission and not session.all_done():
            self._speech.say(
                Utterance(
                    t("speech.mission.task_done_remaining", n=session.pending_count()),
                    Reaction.HAPPY_THUMBS,
                    SpeechHold.SHORT,
                )
            )
        if session.in_mission and session.all_done():
            session.end_mission(True)
            session.save()
            self.victory()

    def victory(self) -> None:
        self._feedback.play(SoundEffect.VICTORY)
        self._celebration.fireworks(self._layouts.layout.vanishing_x)
        self._navigation.open(PageId.MAIN)
        self._speech.say(Utterance(t("speech.mission.victory"), Reaction.PROUD_SALUTE, SpeechHold.VICTORY))
        self._feedback.notify(t("notify.victory.title"), t("notify.victory.body"))
        self._feedback.show_stamp(t("phase.victory"), self.VICTORY_STAMP)
        self._career.award(XpAward(self.VICTORY_XP, mission=True))
        self._enforcement.enforce(force=True)
