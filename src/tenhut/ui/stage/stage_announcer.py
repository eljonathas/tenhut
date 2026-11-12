from __future__ import annotations

from typing import ClassVar

from tenhut.controllers.feedback import Feedback
from tenhut.controllers.speech import Speech
from tenhut.core import Phase, Session, Theme
from tenhut.game.audio import SoundEffect
from tenhut.i18n import t

from .stage_listener import StageListener


class StageAnnouncer(StageListener):
    """A fanfare and a remark from the general when the story reaches a new stage."""

    SPEECH: ClassVar[dict[Theme, str]] = {
        Theme.FIELD: "speech.stage.field_reached",
        Theme.TRENCH: "speech.stage.trench_reached",
        Theme.PARADE: "speech.stage.parade_reached",
    }

    def __init__(self, session: Session, feedback: Feedback, speech: Speech) -> None:
        self._session = session
        self._feedback = feedback
        self._speech = speech

    def stage_entered(self, theme: Theme) -> None:
        self._feedback.play(SoundEffect.START)
        if theme in self.SPEECH and self._session.phase is not Phase.VICTORY:
            self._speech.say_next(t(self.SPEECH[theme]))
