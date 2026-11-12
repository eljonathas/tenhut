from __future__ import annotations

from typing import ClassVar

from tenhut.game.audio import SoundEffect
from tenhut.game.painting import Rgb
from tenhut.i18n import t
from tenhut.services.judge import JudgeRequest, Verdict
from tenhut.ui.painting import ClockText

from .reaction import Reaction
from .request_outcome import RequestOutcome
from .utterance import Utterance


class AccessOutcome(RequestOutcome):
    """A request for temporary access: approved passes are granted to the session."""

    APPROVED_STAMP: ClassVar[Rgb] = Rgb(120, 220, 120)
    LOGGED_JUSTIFICATION = 60
    denied_speech_key: ClassVar[str] = "speech.request.denied_default"

    def _approve(self, request: JudgeRequest, verdict: Verdict, now: float) -> None:
        for group in verdict.groups:
            self._session.grant(group, now + verdict.minutes * ClockText.SECONDS_PER_MINUTE)
        self._session.log(f"{self._entry(request)}: APPROVED {verdict.minutes} min {verdict.groups}")
        self._feedback.play(SoundEffect.APPROVED)
        self._feedback.show_stamp(t("stamp.approved"), self.APPROVED_STAMP)
        self._speech.say(
            Utterance(
                verdict.speech or t("speech.request.approved_default"), Reaction.HAPPY_THUMBS, self.SPEECH_SECONDS
            )
        )
        self._feedback.notify(
            t("notify.access_granted.title"),
            t("notify.access_granted.body", groups=", ".join(verdict.groups), n=verdict.minutes),
        )

    def _denial_entry(self, request: JudgeRequest) -> str:
        return f"{self._entry(request)}: DENIED"

    def _entry(self, request: JudgeRequest) -> str:
        return f"access to '{request.target}' ({request.justification[: self.LOGGED_JUSTIFICATION]})"
