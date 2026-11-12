from __future__ import annotations

from enum import Enum

from .note import Note
from .sound_recipe import SoundRecipe
from .waveform import Waveform


class SoundEffect(Enum):
    """Every effect the game can play, each carrying the recipe the synthesizer renders it from."""

    BLIP = SoundRecipe(Waveform.SQUARE, (Note(880, 0.018),), 0.25)
    CLICK = SoundRecipe(Waveform.SQUARE, (Note(440, 0.025),), 0.35)
    TICK = SoundRecipe(Waveform.SQUARE, (Note(660, 0.05),), 0.35)
    THINK = SoundRecipe(Waveform.SQUARE, (Note(330, 0.05), Note.rest(0.05), Note(392, 0.05)), 0.4)
    TOC = SoundRecipe(Waveform.SQUARE, (Note(220, 0.03), Note(150, 0.05)), 0.6)
    SLAM = SoundRecipe(Waveform.SQUARE, (Note(70, 0.05), Note(55, 0.08), Note(45, 0.12)), 0.7)
    DENIED = SoundRecipe(Waveform.SQUARE, (Note(196, 0.16), Note.rest(0.04), Note(147, 0.3)), 0.45)
    ALARM = SoundRecipe(
        Waveform.SQUARE,
        (Note(988, 0.1), Note.rest(0.06), Note(988, 0.1), Note.rest(0.06), Note(1318, 0.25)),
        0.35,
    )
    START = SoundRecipe(Waveform.TRIANGLE, (Note(523, 0.09), Note(659, 0.09), Note(784, 0.09), Note(1046, 0.2)), 0.6)
    BREAK = SoundRecipe(Waveform.TRIANGLE, (Note(784, 0.12), Note(659, 0.12), Note(523, 0.25)), 0.6)
    APPROVED = SoundRecipe(
        Waveform.TRIANGLE, (Note(659, 0.08), Note(784, 0.08), Note(988, 0.08), Note(1318, 0.2)), 0.55
    )
    VICTORY = SoundRecipe(
        Waveform.TRIANGLE,
        (
            Note(523, 0.11),
            Note(523, 0.11),
            Note(523, 0.11),
            Note(659, 0.3),
            Note(587, 0.11),
            Note(659, 0.11),
            Note(784, 0.45),
        ),
        0.5,
    )

    @property
    def recipe(self) -> SoundRecipe:
        return self.value
