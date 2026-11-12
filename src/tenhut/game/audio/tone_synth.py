from __future__ import annotations

import array

from .note import Note
from .sound_recipe import SoundRecipe


class ToneSynth:
    """Renders recipes to 16-bit mono PCM. Notes get a short attack and release so they do not click."""

    SAMPLE_RATE = 22050
    PEAK_FRACTION = 0.5
    ATTACK_SECONDS = 0.004
    RELEASE_SECONDS = 0.03
    _INT16_MAX = 32767

    def __init__(self) -> None:
        self._amplitude = self._INT16_MAX * self.PEAK_FRACTION
        self._attack = int(self.SAMPLE_RATE * self.ATTACK_SECONDS)
        self._release = int(self.SAMPLE_RATE * self.RELEASE_SECONDS)

    def synthesize(self, recipe: SoundRecipe) -> bytes:
        samples = array.array("h")
        for note in recipe.notes:
            samples.extend(self._render_note(recipe, note))
        return samples.tobytes()

    def _render_note(self, recipe: SoundRecipe, note: Note) -> array.array:
        length = int(self.SAMPLE_RATE * note.duration)
        if note.is_rest:
            return array.array("h", [0] * length)
        period = self.SAMPLE_RATE / note.frequency
        return array.array("h", (self._sample(recipe, index, length, period) for index in range(length)))

    def _sample(self, recipe: SoundRecipe, index: int, length: int, period: float) -> int:
        envelope = min(1.0, index / self._attack if self._attack else 1.0, (length - index) / self._release)
        phase = (index % period) / period
        return int(self._amplitude * envelope * recipe.waveform.sample(phase))
