from __future__ import annotations

from tenhut.core import Phase, Session
from tenhut.game.audio import SoundEffect
from tenhut.game.character import Character
from tenhut.i18n import t
from tenhut.services.platform import APP_NAME

from .feedback import Feedback
from .reaction import Reaction
from .run_state import RunState
from .speech import Speech
from .utterance import Utterance
from .window_control import WindowControl


class QuitController:
    """Lets the soldier leave, except in the middle of a combat: then the window only minimises."""

    DENIED_SPEECH_SECONDS = 4

    def __init__(
        self,
        session: Session,
        run_state: RunState,
        general: Character,
        *,
        speech: Speech,
        feedback: Feedback,
        window: WindowControl,
    ) -> None:
        self._session = session
        self._run_state = run_state
        self._general = general
        self._speech = speech
        self._feedback = feedback
        self._window = window

    def request_quit(self) -> None:
        if self._session.phase is not Phase.WORK:
            self._run_state.stop()
            return
        self._feedback.play(SoundEffect.DENIED)
        self._general.shake()
        self._speech.say(Utterance(t("speech.quit.denied"), Reaction.ANGRY_POINT, self.DENIED_SPEECH_SECONDS))
        self._feedback.notify(APP_NAME, t("notify.quit_denied.body"))
        self._window.minimize()
