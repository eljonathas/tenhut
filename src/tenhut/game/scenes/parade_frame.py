from __future__ import annotations

from dataclasses import dataclass

from ..random_source import RandomSource


@dataclass(frozen=True, slots=True)
class ParadeFrame:
    """What the parade's live objects need to know about the current frame."""

    elapsed: float
    party: bool
    randomness: RandomSource
