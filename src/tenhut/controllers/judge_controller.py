from __future__ import annotations

from pathlib import Path

from tenhut.core import Clock, RequestLog, RequestRecord, Session
from tenhut.game.audio import SoundEffect
from tenhut.game.character import Character
from tenhut.i18n import t
from tenhut.services.judge import (
    JudgeBackend,
    JudgeContext,
    JudgeFactory,
    JudgeJob,
    JudgeRequest,
    RequestKind,
)
from tenhut.ui.painting import ClockText

from .active_settings import ActiveSettings
from .enforcement import Enforcement
from .feedback import Feedback
from .judge_slot import JudgeSlot
from .navigation import Navigation
from .page_id import PageId
from .reaction import Reaction
from .request_form import RequestForm
from .request_outcome import RequestOutcome
from .speech import Speech
from .tickable import Tickable
from .utterance import Utterance


class JudgeController(Tickable):
    """Takes the soldier's requests to the judge, waits for the verdict on a thread and applies it."""

    MIN_JUSTIFICATION = 15

    def __init__(
        self,
        slot: JudgeSlot,
        factory: JudgeFactory,
        work_dir: Path,
        *,
        session: Session,
        settings: ActiveSettings,
        clock: Clock,
        log: RequestLog,
        general: Character,
        outcomes: dict[RequestKind, RequestOutcome],
        speech: Speech,
        feedback: Feedback,
        navigation: Navigation,
        enforcement: Enforcement,
    ) -> None:
        self._slot = slot
        self._factory = factory
        self._work_dir = work_dir
        self._session = session
        self._settings = settings
        self._clock = clock
        self._log = log
        self._general = general
        self._outcomes = outcomes
        self._backend = self._new_backend()
        self._speech = speech
        self._feedback = feedback
        self._navigation = navigation
        self._enforcement = enforcement

    @property
    def backend(self) -> JudgeBackend:
        return self._backend

    @property
    def slot(self) -> JudgeSlot:
        return self._slot

    def refresh_backend(self) -> None:
        self._backend = self._new_backend()

    def open_request(self) -> None:
        now = self._clock.now()
        if now < self._session.denied_until:
            wait = ClockText.format(self._session.denied_until - now)
            self._speech.say(Utterance(t("speech.request.still_denied", time=wait), Reaction.ANGRY_POINT))
            self._feedback.play(SoundEffect.DENIED)
            return
        self._navigation.open(PageId.REQUEST)
        self._speech.say(Utterance(t("speech.request.opened"), Reaction.STERN_CROSSED))

    def submit(self, form: RequestForm) -> None:
        if self._slot.active or not self._acceptable(form):
            return
        session = self._session
        context = JudgeContext(
            session.tasks,
            session.phase,
            ClockText.format(session.remaining()),
            session.cycles,
            tuple(self._settings.current.block_list.names),
            session.history,
        )
        self._backend = self._new_backend()
        job = JudgeJob(self._backend, JudgeRequest(form.kind, form.target, form.justification, context), self._clock)
        job.start()
        self._slot.occupy(job)
        self._feedback.play(SoundEffect.THINK)
        self._general.show(Reaction.THINKING_CHIN.mood, Reaction.THINKING_CHIN.pose)
        self._announce_wait()

    def tick(self, dt: float) -> None:
        job = self._slot.job
        if job is not None and not job.is_alive():
            self._finish(job)

    def _acceptable(self, form: RequestForm) -> bool:
        if form.kind is RequestKind.ACCESS and not form.target:
            self._speech.say(Utterance(t("speech.request.target_missing"), Reaction.ANGRY_POINT))
            return False
        if len(form.justification) < self.MIN_JUSTIFICATION:
            self._speech.say(Utterance(t("speech.request.justification_too_short"), Reaction.ANGRY_POINT))
            self._feedback.play(SoundEffect.DENIED)
            return False
        now = self._clock.now()
        if form.kind is RequestKind.DESERTION and now < self._session.denied_until:
            wait = ClockText.format(self._session.denied_until - now)
            self._speech.say(Utterance(t("speech.request.recently_denied", time=wait), Reaction.ANGRY_POINT))
            return False
        return True

    def _announce_wait(self) -> None:
        if self._backend.uses_ai:
            self._speech.murmur(t("speech.request.asking_command"), persist=True)
        else:
            self._speech.murmur(
                t("speech.request.no_ai_wait", n=self._settings.current.judge.local_wait_seconds), persist=True
            )

    def _finish(self, job: JudgeJob) -> None:
        self._slot.release()
        verdict, request, now = job.result, job.request, self._clock.now()
        self._log.append(
            RequestRecord(
                now,
                request.kind.value,
                request.target,
                request.justification,
                verdict.approved,
                tuple(verdict.groups),
                verdict.minutes,
                verdict.speech,
                verdict.error,
            )
        )
        self._outcomes[request.kind].resolve(request, verdict, now)
        self._session.save()
        self._navigation.open(PageId.MAIN)
        self._enforcement.enforce(force=True)

    def _new_backend(self) -> JudgeBackend:
        return self._factory.create(self._settings.current, self._work_dir)
