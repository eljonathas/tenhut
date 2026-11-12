from __future__ import annotations

from typing import ClassVar

from tenhut.game.audio import SoundEffect
from tenhut.i18n import t
from tenhut.services.judge import JudgeRequest, Verdict

from .reaction import Reaction
from .request_outcome import RequestOutcome
from .utterance import Utterance


class DesertionOutcome(RequestOutcome):
    """A request to abandon the mission: approved, the mission ends unfinished."""

    denied_speech_key: ClassVar[str] = "speech.desertion.denied_default"

    def _approve(self, request: JudgeRequest, verdict: Verdict, now: float) -> None:
        self._session.log("desertion: APPROVED")
        self._session.end_mission(False)
        self._feedback.play(SoundEffect.BREAK)
        self._speech.say(
            Utterance(
                verdict.speech or t("speech.desertion.approved_default"), Reaction.NEUTRAL_SALUTE, self.SPEECH_SECONDS
            )
        )
        if self._session.pending_count():
            self._speech.say_next(t("speech.desertion.resume_hint"))
        self._feedback.notify(t("notify.desertion_approved.title"), t("notify.desertion_approved.body"))

    def _denial_entry(self, request: JudgeRequest) -> str:
        return "desertion: DENIED"
