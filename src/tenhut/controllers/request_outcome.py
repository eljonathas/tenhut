from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar

from tenhut.core import Session
from tenhut.game.audio import SoundEffect
from tenhut.game.painting import Rgb
from tenhut.i18n import t
from tenhut.services.judge import JudgeRequest, Verdict

from .active_settings import ActiveSettings
from .feedback import Feedback
from .gestures import Gestures
from .reaction import Reaction
from .speech import Speech
from .utterance import Utterance


class RequestOutcome(ABC):
    """What happens once the judge has ruled on one kind of request."""

    DENIED_STAMP: ClassVar[Rgb] = Rgb(240, 90, 80)
    DENIAL_FLASH: ClassVar[float] = 0.5
    SPEECH_SECONDS: ClassVar[float] = 5
    denied_speech_key: ClassVar[str]

    def __init__(
        self, session: Session, settings: ActiveSettings, speech: Speech, *, feedback: Feedback, gestures: Gestures
    ) -> None:
        self._session = session
        self._settings = settings
        self._speech = speech
        self._feedback = feedback
        self._gestures = gestures

    def resolve(self, request: JudgeRequest, verdict: Verdict, now: float) -> None:
        if verdict.approved:
            self._approve(request, verdict, now)
        else:
            self._deny(request, verdict, now)

    @abstractmethod
    def _approve(self, request: JudgeRequest, verdict: Verdict, now: float) -> None: ...

    @abstractmethod
    def _denial_entry(self, request: JudgeRequest) -> str:
        """The line written to the session history."""

    def _deny(self, request: JudgeRequest, verdict: Verdict, now: float) -> None:
        self._session.deny_until(now + self._settings.current.judge.denial_cooldown_seconds)
        self._session.log(self._denial_entry(request))
        self._feedback.show_stamp(t("stamp.denied"), self.DENIED_STAMP)
        self._feedback.flash(self.DENIAL_FLASH)
        self._feedback.play(SoundEffect.DENIED)
        self._gestures.start_slam()
        self._speech.say(
            Utterance(verdict.speech or t(self.denied_speech_key), Reaction.ANGRY_FISTS_UP, self.SPEECH_SECONDS)
        )
