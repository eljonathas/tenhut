from __future__ import annotations

import pygame

from .sound_effect import SoundEffect
from .tone_synth import ToneSynth
from .volume_curve import VolumeCurve


class SoundBank:
    """The synthesized effects loaded into the mixer. Silent when disabled, muted or when no audio device exists."""

    _BIT_DEPTH = -16
    _CHANNELS = 1
    _BUFFER_SAMPLES = 512

    def __init__(
        self, enabled: bool = True, volume: int = 40, synth: ToneSynth | None = None, curve: VolumeCurve | None = None
    ) -> None:
        self._enabled = enabled
        self._volume = volume
        self._curve = curve or VolumeCurve()
        self._sounds: dict[SoundEffect, pygame.mixer.Sound] = {}
        if not self._open_mixer():
            self._enabled = False
            return
        self._load(synth or ToneSynth())
        self.set_volume(volume)

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = value

    @property
    def available(self) -> bool:
        """Whether at least one effect made it into the mixer."""
        return bool(self._sounds)

    @property
    def volume(self) -> int:
        return self._volume

    def set_volume(self, volume: int) -> None:
        """Master volume as a percentage; each effect keeps its own relative gain."""
        self._volume = max(0, min(100, int(volume)))
        master = self._curve.level(self._volume)
        for effect, sound in self._sounds.items():
            sound.set_volume(master * effect.recipe.gain)

    def play(self, effect: SoundEffect) -> None:
        if self._enabled and self._volume > 0 and effect in self._sounds:
            self._sounds[effect].play()

    def _open_mixer(self) -> bool:
        try:
            pygame.mixer.init(ToneSynth.SAMPLE_RATE, self._BIT_DEPTH, self._CHANNELS, self._BUFFER_SAMPLES)
        except pygame.error:
            return False
        return True

    def _load(self, synth: ToneSynth) -> None:
        for effect in SoundEffect:
            try:
                self._sounds[effect] = pygame.mixer.Sound(buffer=synth.synthesize(effect.recipe))
            except pygame.error:
                continue
