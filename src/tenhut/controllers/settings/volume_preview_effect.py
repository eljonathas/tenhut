from __future__ import annotations

from tenhut.controllers.feedback import Feedback
from tenhut.game.audio import SoundBank, SoundEffect

from .change_effect import ChangeEffect


class VolumePreviewEffect(ChangeEffect):
    """The new volume is applied at once and previewed with the longest effect."""

    def __init__(self, sounds: SoundBank, feedback: Feedback) -> None:
        self._sounds = sounds
        self._feedback = feedback

    def apply(self, new_value: object) -> None:
        self._sounds.set_volume(new_value)
        self._feedback.play(SoundEffect.VICTORY)
