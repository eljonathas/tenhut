from __future__ import annotations

from dataclasses import dataclass

from .note import Note
from .waveform import Waveform


@dataclass(frozen=True, slots=True)
class SoundRecipe:
    """How to synthesize an effect: its waveform, its notes and its loudness relative to the master volume."""

    waveform: Waveform
    notes: tuple[Note, ...]
    gain: float
