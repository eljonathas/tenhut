from __future__ import annotations

from tenhut.controllers.gestures import Gestures
from tenhut.controllers.judge_slot import JudgeSlot
from tenhut.controllers.reaction import Reaction
from tenhut.controllers.speech import Speech
from tenhut.controllers.utterance import Utterance
from tenhut.core import Phase, Session
from tenhut.i18n import t_choice
from tenhut.ui.layout import LayoutProvider
from tenhut.ui.widgets.balloon import Balloon


class PokeBackResponder:
    """A soldier who pokes the general during a combat gets poked back."""

    SPEECH_SECONDS = 3

    def __init__(
        self,
        session: Session,
        layouts: LayoutProvider,
        judge: JudgeSlot,
        *,
        gestures: Gestures,
        balloon: Balloon,
        speech: Speech,
    ) -> None:
        self._session = session
        self._layouts = layouts
        self._judge = judge
        self._gestures = gestures
        self._balloon = balloon
        self._speech = speech

    def respond(self, position: tuple[int, int]) -> bool:
        """True when the click landed on the general and he reacted."""
        provoked = (
            self._layouts.layout.general_rect.collidepoint(position)
            and self._session.phase is Phase.WORK
            and not self._judge.active
            and not self._gestures.poke_active
            and not self._balloon.typing
        )
        if provoked:
            self._speech.say(
                Utterance(t_choice("speech.work.poke_back_remarks"), Reaction.ANGRY_POINT, self.SPEECH_SECONDS)
            )
            self._gestures.poke(1)
        return provoked
