from __future__ import annotations

from tenhut.controllers.feedback import Feedback
from tenhut.game.audio import SoundEffect

from .change_effect import ChangeEffect


class ClickEffect(ChangeEffect):
    """A click."""

    def __init__(self, feedback: Feedback) -> None:
        self._feedback = feedback

    def apply(self, new_value: object) -> None:
        self._feedback.play(SoundEffect.CLICK)
